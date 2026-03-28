from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Auth Service", version="1.0.0")


class Role(str, Enum):
    customer = "customer"
    vendor = "vendor"
    admin = "admin"


class User(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    created_at: datetime


class CreateUserRequest(BaseModel):
    email: str
    name: str
    role: Role


class ValidateResponse(BaseModel):
    valid: bool
    role: str


# ---------------------------------------------------------------------------
# In-memory store with 5 seed users
# ---------------------------------------------------------------------------
USERS: dict[str, User] = {}


def _seed_users() -> None:
    seed_data = [
        ("user-1", "alice@example.com", "Alice Johnson", Role.customer),
        ("user-2", "bob@example.com", "Bob Smith", Role.vendor),
        ("user-3", "carol@example.com", "Carol White", Role.customer),
        ("user-4", "dave@example.com", "Dave Lee", Role.vendor),
        ("user-5", "eve@example.com", "Eve Martinez", Role.admin),
    ]
    now = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    for uid, email, name, role in seed_data:
        USERS[uid] = User(id=uid, email=email, name=name, role=role, created_at=now)


_seed_users()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "healthy", "service": "auth-service"}


@app.get("/api/v1/users", response_model=list[User])
def list_users(role: Optional[Role] = Query(None)):
    users = list(USERS.values())
    if role is not None:
        users = [u for u in users if u.role == role]
    return users


@app.get("/api/v1/users/{user_id}", response_model=User)
def get_user(user_id: str):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/v1/users", response_model=User, status_code=201)
def create_user(body: CreateUserRequest):
    user_id = f"user-{uuid4().hex[:8]}"
    user = User(
        id=user_id,
        email=body.email,
        name=body.name,
        role=body.role,
        created_at=datetime.now(timezone.utc),
    )
    USERS[user_id] = user
    return user


@app.get("/api/v1/users/{user_id}/validate", response_model=ValidateResponse)
def validate_user(user_id: str):
    user = USERS.get(user_id)
    if user is None:
        return ValidateResponse(valid=False, role="")
    return ValidateResponse(valid=True, role=user.role)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
