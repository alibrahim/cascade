from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import httpx
import uvicorn

app = FastAPI(title="Order Service", version="1.0.0")

AUTH_SERVICE_URL = "http://localhost:9000"
CATALOG_SERVICE_URL = "http://localhost:9001"


class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int


class OrderItem(BaseModel):
    menu_item_id: str
    quantity: int
    unit_price: float
    subtotal: float


class Order(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    items: list[OrderItem]
    total: float
    status: str  # pending | confirmed | preparing | delivered | cancelled
    created_at: str


class CreateOrderRequest(BaseModel):
    customer_id: str
    items: list[OrderItemCreate]


class UpdateStatusRequest(BaseModel):
    status: str


ORDERS: dict[str, Order] = {
    "order-001": Order(
        id="order-001",
        customer_id="user-002",
        customer_name="Jane Smith",
        items=[
            OrderItem(menu_item_id="item-001", quantity=2, unit_price=12.99, subtotal=25.98),
            OrderItem(menu_item_id="item-003", quantity=1, unit_price=8.50, subtotal=8.50),
        ],
        total=34.48,
        status="delivered",
        created_at="2026-03-25T10:30:00Z",
    ),
    "order-002": Order(
        id="order-002",
        customer_id="user-003",
        customer_name="Bob Johnson",
        items=[
            OrderItem(menu_item_id="item-002", quantity=1, unit_price=15.99, subtotal=15.99),
        ],
        total=15.99,
        status="preparing",
        created_at="2026-03-26T08:15:00Z",
    ),
    "order-003": Order(
        id="order-003",
        customer_id="user-002",
        customer_name="Jane Smith",
        items=[
            OrderItem(menu_item_id="item-001", quantity=1, unit_price=12.99, subtotal=12.99),
            OrderItem(menu_item_id="item-002", quantity=2, unit_price=15.99, subtotal=31.98),
        ],
        total=44.97,
        status="pending",
        created_at="2026-03-26T12:00:00Z",
    ),
}

VALID_STATUSES = {"pending", "confirmed", "preparing", "delivered", "cancelled"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order-service"}


@app.get("/api/v1/orders/stats")
async def order_stats():
    orders = list(ORDERS.values())
    total_revenue = sum(o.total for o in orders)
    orders_by_status: dict[str, int] = {}
    for o in orders:
        orders_by_status[o.status] = orders_by_status.get(o.status, 0) + 1
    return {
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "orders_by_status": orders_by_status,
    }


@app.get("/api/v1/orders")
async def list_orders(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    results = list(ORDERS.values())
    if customer_id:
        results = [o for o in results if o.customer_id == customer_id]
    if status:
        results = [o for o in results if o.status == status]
    return results


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/api/v1/orders", status_code=201)
async def create_order(request: CreateOrderRequest):
    # Validate customer via auth-service
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AUTH_SERVICE_URL}/api/v1/users/{request.customer_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid customer ID")
            customer = resp.json()
            customer_name = customer.get("name", "Unknown")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        # Validate menu items and get prices via catalog-service
        order_items: list[OrderItem] = []
        for item in request.items:
            try:
                resp = await client.get(f"{CATALOG_SERVICE_URL}/api/v1/menu/{item.menu_item_id}")
                if resp.status_code != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Menu item {item.menu_item_id} not found",
                    )
                menu_item = resp.json()
                unit_price = menu_item["price"]
                subtotal = round(unit_price * item.quantity, 2)
                order_items.append(
                    OrderItem(
                        menu_item_id=item.menu_item_id,
                        quantity=item.quantity,
                        unit_price=unit_price,
                        subtotal=subtotal,
                    )
                )
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Catalog service unavailable")

    total = round(sum(i.subtotal for i in order_items), 2)
    order_id = f"order-{len(ORDERS) + 1:03d}"

    order = Order(
        id=order_id,
        customer_id=request.customer_id,
        customer_name=customer_name,
        items=order_items,
        total=total,
        status="pending",
        created_at=datetime.utcnow().isoformat() + "Z",
    )
    ORDERS[order_id] = order
    return order


@app.patch("/api/v1/orders/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateStatusRequest):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if request.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}",
        )
    order.status = request.status
    return order


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9002)
