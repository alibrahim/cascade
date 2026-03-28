from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import httpx
import uvicorn

app = FastAPI(title="Notification Service", version="1.0.0")

AUTH_SERVICE_URL = "http://localhost:9000"
ORDER_SERVICE_URL = "http://localhost:9002"


class Notification(BaseModel):
    id: str
    user_id: str
    type: str  # order_confirmed | order_delivered | order_cancelled | welcome
    message: str
    channel: str  # email | sms
    sent_at: str
    read: bool


class SendNotificationRequest(BaseModel):
    user_id: str
    type: str
    order_id: Optional[str] = None


NOTIFICATIONS: dict[str, Notification] = {
    "notif-001": Notification(
        id="notif-001",
        user_id="user-002",
        type="order_confirmed",
        message="Your order order-001 has been confirmed!",
        channel="email",
        sent_at="2026-03-25T10:31:00Z",
        read=True,
    ),
    "notif-002": Notification(
        id="notif-002",
        user_id="user-002",
        type="order_delivered",
        message="Your order order-001 has been delivered. Enjoy your meal!",
        channel="email",
        sent_at="2026-03-25T11:45:00Z",
        read=True,
    ),
    "notif-003": Notification(
        id="notif-003",
        user_id="user-003",
        type="order_confirmed",
        message="Your order order-002 has been confirmed!",
        channel="sms",
        sent_at="2026-03-26T08:16:00Z",
        read=False,
    ),
    "notif-004": Notification(
        id="notif-004",
        user_id="user-001",
        type="welcome",
        message="Welcome to the Food Marketplace, Alice Williams! We're glad to have you.",
        channel="email",
        sent_at="2026-03-24T09:00:00Z",
        read=True,
    ),
    "notif-005": Notification(
        id="notif-005",
        user_id="user-002",
        type="order_confirmed",
        message="Your order order-003 has been confirmed!",
        channel="email",
        sent_at="2026-03-26T12:01:00Z",
        read=False,
    ),
}

VALID_TYPES = {"order_confirmed", "order_delivered", "order_cancelled", "welcome"}
VALID_CHANNELS = {"email", "sms"}

MESSAGE_TEMPLATES = {
    "order_confirmed": "Hi {name}, your order {order_id} has been confirmed!",
    "order_delivered": "Hi {name}, your order {order_id} has been delivered. Enjoy your meal!",
    "order_cancelled": "Hi {name}, your order {order_id} has been cancelled.",
    "welcome": "Welcome to the Food Marketplace, {name}! We're glad to have you.",
}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.get("/api/v1/notifications/unread-count")
async def unread_count(user_id: str = Query(...)):
    count = sum(
        1 for n in NOTIFICATIONS.values() if n.user_id == user_id and not n.read
    )
    return {"count": count}


@app.get("/api/v1/notifications")
async def list_notifications(
    user_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    read: Optional[bool] = Query(None),
):
    results = list(NOTIFICATIONS.values())
    if user_id:
        results = [n for n in results if n.user_id == user_id]
    if type:
        results = [n for n in results if n.type == type]
    if read is not None:
        results = [n for n in results if n.read == read]
    return results


@app.get("/api/v1/notifications/{notification_id}")
async def get_notification(notification_id: str):
    notif = NOTIFICATIONS.get(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@app.post("/api/v1/notifications/send", status_code=201)
async def send_notification(request: SendNotificationRequest):
    if request.type not in VALID_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {', '.join(VALID_TYPES)}",
        )

    async with httpx.AsyncClient() as client:
        # Fetch user from auth-service
        try:
            resp = await client.get(f"{AUTH_SERVICE_URL}/api/v1/users/{request.user_id}")
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid user ID")
            user = resp.json()
            user_name = user.get("name", "Customer")
            channel = "sms" if user.get("phone") else "email"
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        # Fetch order from order-service if order-related notification
        order_id = request.order_id or ""
        if request.type != "welcome":
            if not request.order_id:
                raise HTTPException(
                    status_code=400,
                    detail="order_id is required for order-related notifications",
                )
            try:
                resp = await client.get(
                    f"{ORDER_SERVICE_URL}/api/v1/orders/{request.order_id}"
                )
                if resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Invalid order ID")
                order_id = request.order_id
            except httpx.RequestError:
                raise HTTPException(status_code=503, detail="Order service unavailable")

    message = MESSAGE_TEMPLATES[request.type].format(name=user_name, order_id=order_id)
    notif_id = f"notif-{len(NOTIFICATIONS) + 1:03d}"

    notification = Notification(
        id=notif_id,
        user_id=request.user_id,
        type=request.type,
        message=message,
        channel=channel,
        sent_at=datetime.utcnow().isoformat() + "Z",
        read=False,
    )
    NOTIFICATIONS[notif_id] = notification
    return notification


@app.patch("/api/v1/notifications/{notification_id}/read")
async def mark_as_read(notification_id: str):
    notif = NOTIFICATIONS.get(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read = True
    return notif


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)
