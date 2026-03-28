import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Catalog Service", version="1.0.0")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:9000")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Category(BaseModel):
    id: str
    name: str
    description: str


class MenuItem(BaseModel):
    id: str
    vendor_id: str
    vendor_name: str
    category_id: str
    name: str
    description: str
    price: float
    available: bool


class CreateMenuItemRequest(BaseModel):
    vendor_id: str
    vendor_name: str
    category_id: str
    name: str
    description: str
    price: float
    available: bool = True


# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------
CATEGORIES: dict[str, Category] = {
    "cat-1": Category(id="cat-1", name="Pizza", description="Wood-fired and classic pizzas"),
    "cat-2": Category(id="cat-2", name="Sushi", description="Fresh sushi rolls and sashimi"),
    "cat-3": Category(id="cat-3", name="Burgers", description="Gourmet and classic burgers"),
}

_ITEM_COUNTER = 0


def _next_item_id() -> str:
    global _ITEM_COUNTER
    _ITEM_COUNTER += 1
    return f"item-{_ITEM_COUNTER}"


MENU_ITEMS: dict[str, MenuItem] = {}


def _seed_menu() -> None:
    items = [
        # Vendor user-2 (Bob Smith) -- Pizza & Burgers
        ("user-2", "Bob Smith", "cat-1", "Margherita Pizza", "Classic tomato, mozzarella, basil", 12.99),
        ("user-2", "Bob Smith", "cat-1", "Pepperoni Pizza", "Loaded with pepperoni and cheese", 14.99),
        ("user-2", "Bob Smith", "cat-3", "Classic Cheeseburger", "Beef patty with cheddar and pickles", 10.49),
        ("user-2", "Bob Smith", "cat-3", "BBQ Bacon Burger", "Smoky BBQ sauce, crispy bacon, onion rings", 13.99),
        # Vendor user-4 (Dave Lee) -- Sushi & Pizza
        ("user-4", "Dave Lee", "cat-2", "Salmon Nigiri", "Fresh Atlantic salmon over sushi rice", 8.99),
        ("user-4", "Dave Lee", "cat-2", "Dragon Roll", "Eel, cucumber, avocado, tobiko", 15.49),
        ("user-4", "Dave Lee", "cat-2", "Spicy Tuna Roll", "Tuna, spicy mayo, tempura flakes", 13.49),
        ("user-4", "Dave Lee", "cat-1", "Truffle Mushroom Pizza", "Wild mushrooms, truffle oil, fontina", 17.99),
    ]
    for vendor_id, vendor_name, cat_id, name, desc, price in items:
        iid = _next_item_id()
        MENU_ITEMS[iid] = MenuItem(
            id=iid,
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            category_id=cat_id,
            name=name,
            description=desc,
            price=price,
            available=True,
        )


_seed_menu()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _validate_vendor(vendor_id: str) -> None:
    """Call auth-service to confirm vendor_id belongs to a vendor."""
    url = f"{AUTH_SERVICE_URL}/api/v1/users/{vendor_id}/validate"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=5.0)
            resp.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(status_code=502, detail="Auth service unavailable")

    data = resp.json()
    if not data.get("valid"):
        raise HTTPException(status_code=404, detail="Vendor not found")
    if data.get("role") != "vendor":
        raise HTTPException(status_code=403, detail="User is not a vendor")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "healthy", "service": "catalog-service"}


@app.get("/api/v1/categories", response_model=list[Category])
def list_categories():
    return list(CATEGORIES.values())


@app.get("/api/v1/menu/search", response_model=list[MenuItem])
def search_menu(q: str = Query(..., min_length=1)):
    query = q.lower()
    return [
        item
        for item in MENU_ITEMS.values()
        if query in item.name.lower() or query in item.description.lower()
    ]


@app.get("/api/v1/menu", response_model=list[MenuItem])
def list_menu(
    category_id: Optional[str] = Query(None),
    vendor_id: Optional[str] = Query(None),
    available: Optional[bool] = Query(None),
):
    items = list(MENU_ITEMS.values())
    if category_id is not None:
        items = [i for i in items if i.category_id == category_id]
    if vendor_id is not None:
        items = [i for i in items if i.vendor_id == vendor_id]
    if available is not None:
        items = [i for i in items if i.available == available]
    return items


@app.get("/api/v1/menu/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: str):
    item = MENU_ITEMS.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@app.post("/api/v1/menu", response_model=MenuItem, status_code=201)
async def create_menu_item(body: CreateMenuItemRequest):
    await _validate_vendor(body.vendor_id)

    if body.category_id not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category_id")

    iid = _next_item_id()
    item = MenuItem(
        id=iid,
        vendor_id=body.vendor_id,
        vendor_name=body.vendor_name,
        category_id=body.category_id,
        name=body.name,
        description=body.description,
        price=body.price,
        available=body.available,
    )
    MENU_ITEMS[iid] = item
    return item


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9001)
