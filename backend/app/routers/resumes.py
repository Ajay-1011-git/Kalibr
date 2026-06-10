"""Resumes router stub."""
from fastapi import APIRouter

from app.services.storage_service import StorageService

router = APIRouter()


@router.get("/")
async def list_resumes() -> dict:
    """Stub: List all resumes for the current user."""
    return {"message": "resumes.list_resumes — not implemented"}


@router.post("/upload")
async def upload_resume() -> dict:
    """
    Stub: Upload and parse a resume file.

    Storage path: users/{firebase_uid}/resumes/{resume_id}/original.{ext}
    Uses StorageService.upload() to write the file to the kalibr-files bucket.
    """
    # TODO: receive UploadFile, parse it, then:
    # storage = StorageService(supabase_client)
    # path = f"users/{uid}/resumes/{resume_id}/original.{ext}"
    # storage.upload(path, file_bytes, content_type)
    return {"message": "resumes.upload_resume — not implemented"}


@router.get("/{resume_id}")
async def get_resume(resume_id: str) -> dict:
    """Stub: Get a specific resume by ID."""
    return {"message": f"resumes.get_resume({resume_id}) — not implemented"}


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str) -> dict:
    """
    Stub: Delete a resume by ID.

    Removes the resume record from Supabase DB and deletes all associated
    objects from the kalibr-files bucket via StorageService.delete().
    """
    # TODO:
    # storage = StorageService(supabase_client)
    # storage.delete(f"users/{uid}/resumes/{resume_id}/original.{ext}")
    return {"message": f"resumes.delete_resume({resume_id}) — not implemented"}
