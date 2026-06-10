"""Auth router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login() -> dict:
    """Stub: Exchange Firebase ID token for session."""
    return {"message": "auth.login — not implemented"}


@router.post("/logout")
async def logout() -> dict:
    """Stub: Invalidate session."""
    return {"message": "auth.logout — not implemented"}
