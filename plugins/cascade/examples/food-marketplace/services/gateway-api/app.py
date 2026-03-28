from fastapi import FastAPI, HTTPException

import httpx

app = FastAPI(title="Gateway API", version="1.0.0")

# ---------------------------------------------------------------------------
# Upstream service base URLs
# ---------------------------------------------------------------------------
AUTH_URL = "http://localhost:9000"
CATALOG_URL = "http://localhost:9001"
ORDER_URL = "http://localhost:9002"
NOTIFICATION_URL = "http://localhost:9003"

TIMEOUT = httpx.Timeout(5.0, connect=3.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _get(url: str) -> dict | list | None:
    """Perform a GET request; return parsed JSON or None on failure."""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


async def _service_health(name: str, base_url: str) -> dict:
    data = await _get(f"{base_url}/health")
    if data and data.get("status") == "healthy":
        return {"service": name, "status": "healthy"}
    return {"service": name, "status": "unhealthy"}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    checks = [
        _service_health("auth-service", AUTH_URL),
        _service_health("catalog-service", CATALOG_URL),
        _service_health("order-service", ORDER_URL),
        _service_health("notification-service", NOTIFICATION_URL),
    ]
    import asyncio

    results = await asyncio.gather(*checks)
    all_healthy = all(r["status"] == "healthy" for r in results)
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "gateway-api",
        "upstreams": results,
    }


@app.get("/api/v1/dashboard")
async def dashboard():
    """Aggregate high-level platform statistics from all services."""
    import asyncio

    users_task = _get(f"{AUTH_URL}/api/v1/users")
    items_task = _get(f"{CATALOG_URL}/api/v1/items")
    orders_task = _get(f"{ORDER_URL}/api/v1/orders")
    notifs_task = _get(f"{NOTIFICATION_URL}/api/v1/notifications")

    users, items, orders, notifs = await asyncio.gather(
        users_task, items_task, orders_task, notifs_task
    )

    user_count = len(users) if isinstance(users, list) else 0
    item_count = len(items) if isinstance(items, list) else 0

    order_count = 0
    total_revenue = 0.0
    if isinstance(orders, list):
        order_count = len(orders)
        total_revenue = sum(float(o.get("total", 0)) for o in orders)

    unread_count = 0
    if isinstance(notifs, list):
        unread_count = sum(1 for n in notifs if not n.get("read", True))

    return {
        "user_count": user_count,
        "menu_item_count": item_count,
        "order_count": order_count,
        "total_revenue": round(total_revenue, 2),
        "unread_notifications": unread_count,
    }


@app.get("/api/v1/vendor/{vendor_id}/summary")
async def vendor_summary(vendor_id: str):
    """Return vendor info, their menu items, and orders for those items."""
    import asyncio

    vendor_task = _get(f"{AUTH_URL}/api/v1/users/{vendor_id}")
    items_task = _get(f"{CATALOG_URL}/api/v1/items?vendor_id={vendor_id}")
    orders_task = _get(f"{ORDER_URL}/api/v1/orders?vendor_id={vendor_id}")

    vendor, items, orders = await asyncio.gather(
        vendor_task, items_task, orders_task
    )

    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return {
        "vendor": vendor,
        "menu_items": items if isinstance(items, list) else [],
        "orders": orders if isinstance(orders, list) else [],
    }


@app.get("/api/v1/customer/{customer_id}/profile")
async def customer_profile(customer_id: str):
    """Return customer info, their orders, and their notifications."""
    import asyncio

    customer_task = _get(f"{AUTH_URL}/api/v1/users/{customer_id}")
    orders_task = _get(f"{ORDER_URL}/api/v1/orders?customer_id={customer_id}")
    notifs_task = _get(
        f"{NOTIFICATION_URL}/api/v1/notifications?user_id={customer_id}"
    )

    customer, orders, notifs = await asyncio.gather(
        customer_task, orders_task, notifs_task
    )

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer": customer,
        "orders": orders if isinstance(orders, list) else [],
        "notifications": notifs if isinstance(notifs, list) else [],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9004)
