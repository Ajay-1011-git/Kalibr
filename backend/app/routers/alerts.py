"""Alerts router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_alerts() -> dict:
    """Stub: List all job alerts for the current user."""
    return {"message": "alerts.list_alerts — not implemented"}


@router.post("/")
async def create_alert() -> dict:
    """Stub: Create a new job alert."""
    return {"message": "alerts.create_alert — not implemented"}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str) -> dict:
    """Stub: Delete a job alert."""
    return {"message": f"alerts.delete_alert({alert_id}) — not implemented"}
