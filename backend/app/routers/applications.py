"""Applications router stub."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_applications() -> dict:
    """Stub: List all job applications for the current user."""
    return {"message": "applications.list_applications — not implemented"}


@router.post("/")
async def create_application() -> dict:
    """Stub: Create a new job application record."""
    return {"message": "applications.create_application — not implemented"}


@router.patch("/{application_id}")
async def update_application(application_id: str) -> dict:
    """Stub: Update application status or notes."""
    return {"message": f"applications.update_application({application_id}) — not implemented"}


@router.delete("/{application_id}")
async def delete_application(application_id: str) -> dict:
    """Stub: Delete an application record."""
    return {"message": f"applications.delete_application({application_id}) — not implemented"}
