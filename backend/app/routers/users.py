"""Users router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_me() -> dict:
    """Stub: Return current user profile."""
    return {"message": "users.get_me — not implemented"}


@router.patch("/me")
async def update_me() -> dict:
    """Stub: Update current user profile."""
    return {"message": "users.update_me — not implemented"}
