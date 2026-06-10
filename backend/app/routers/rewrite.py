"""Rewrite router stub."""
from fastapi import APIRouter

from app.services.storage_service import StorageService

router = APIRouter()


@router.post("/")
async def start_rewrite() -> dict:
    """Stub: Kick off an async resume rewrite task."""
    return {"message": "rewrite.start_rewrite — not implemented"}


@router.get("/{task_id}")
async def get_rewrite_status(task_id: str) -> dict:
    """Stub: Poll the status / result of a rewrite task."""
    return {"message": f"rewrite.get_rewrite_status({task_id}) — not implemented"}


@router.post("/{task_id}/accept")
async def accept_rewrite(task_id: str) -> dict:
    """Stub: Accept and persist the rewritten resume."""
    return {"message": f"rewrite.accept_rewrite({task_id}) — not implemented"}


@router.get("/{task_id}/download")
async def get_rewrite_download_url(task_id: str, fmt: str = "docx") -> dict:
    """
    Stub: Return a short-lived signed URL for downloading the rewritten resume.

    Storage path: users/{uid}/resumes/{resume_id}/rewrite_{rewrite_id}.{fmt}
    Uses StorageService.get_signed_url() (expires_in=900s by default).
    """
    # TODO:
    # storage = StorageService(supabase_client)
    # path = f"users/{uid}/resumes/{resume_id}/rewrite_{rewrite_id}.{fmt}"
    # signed_url = storage.get_signed_url(path)
    return {"message": f"rewrite.get_rewrite_download_url({task_id}, {fmt}) — not implemented"}
