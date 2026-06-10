"""Auto-apply router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/settings")
async def get_auto_apply_settings() -> dict:
    """Stub: Return user's auto-apply configuration."""
    return {"message": "auto_apply.get_auto_apply_settings — not implemented"}


@router.put("/settings")
async def update_auto_apply_settings() -> dict:
    """Stub: Update user's auto-apply configuration."""
    return {"message": "auto_apply.update_auto_apply_settings — not implemented"}


@router.post("/trigger")
async def trigger_auto_apply() -> dict:
    """Stub: Manually trigger the auto-apply task."""
    return {"message": "auto_apply.trigger_auto_apply — not implemented"}
