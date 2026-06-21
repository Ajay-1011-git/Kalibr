"""
Resumes router — authenticated resume upload and management.

All endpoints require a valid Firebase Bearer token via `get_current_user`.
"""

import uuid
from datetime import datetime, timezone

from celery import Celery
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import settings
from app.db import supabase_client
from app.middleware.auth import get_current_user
from app.services.storage_service import StorageService

# Initialize Celery client for sending tasks
celery_app = Celery(
    "kalibr",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

router = APIRouter()

# ── Constants ─────────────────────────────────────────────────────────────────

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ── Response models ───────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    resume_id: str
    task_id: str


class ResumeListItem(BaseModel):
    id: str
    display_name: str
    source_format: str
    parse_status: str
    created_at: str
    skills_count: int | None = None


class ResumeDetail(BaseModel):
    resume_id: str
    structured: dict | None = None
    fingerprint: dict | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _get_user_id(firebase_uid: str) -> str:
    """Get Supabase user_id from firebase_uid."""
    result = (
        supabase_client.table("users")
        .select("id")
        .eq("firebase_uid", firebase_uid)
        .maybe_single()
        .execute()
    )
    if not result or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User not found"}},
        )
    return result.data["id"]


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_resume(
    file: UploadFile = File(...),
    display_name: str = Form(...),
    current_user: dict = Depends(get_current_user),
) -> UploadResponse:
    """
    Upload and parse a resume file.
    
    - Validates file type (PDF or DOCX) and size (≤5MB)
    - Uploads to Supabase Storage: users/{firebase_uid}/resumes/{uuid}/original.{ext}
    - Creates resume record with parse_status='pending'
    - Enqueues Celery parse task
    - Returns 202 with resume_id and task_id
    """
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"error": {"code": "FILE_TYPE_INVALID", "message": "File must be PDF or DOCX"}},
        )
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Validate size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": "File size must be ≤5MB"}},
        )
    
    # Determine format and extension
    if file.content_type == "application/pdf":
        source_format = "pdf"
        ext = "pdf"
    else:
        source_format = "docx"
        ext = "docx"
    
    # Get user_id
    firebase_uid = current_user["uid"]
    user_id = _get_user_id(firebase_uid)
    
    # Generate resume ID
    resume_id = str(uuid.uuid4())
    
    # Upload to Supabase Storage
    storage_path = f"users/{firebase_uid}/resumes/{resume_id}/original.{ext}"
    storage = StorageService(supabase_client)
    storage.upload(storage_path, file_bytes, file.content_type)
    
    # Create resume record
    supabase_client.table("resumes").insert({
        "id": resume_id,
        "user_id": user_id,
        "display_name": display_name,
        "source_format": source_format,
        "storage_path": storage_path,
        "parse_status": "pending"
    }).execute()
    
    # Enqueue parse task
    task = celery_app.send_task(
        "workers.tasks.parse.parse_resume",
        args=[resume_id, storage_path, source_format],
        queue="parse"
    )
    
    return UploadResponse(resume_id=resume_id, task_id=task.id)


@router.get("/upload/{task_id}/status")
async def get_upload_status(
    task_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    SSE endpoint for polling task status.
    
    Streams events every 2 seconds until task is done or failed.
    """
    import asyncio
    from celery.result import AsyncResult
    
    async def event_generator():
        while True:
            result = AsyncResult(task_id)
            
            if result.state == "PENDING":
                yield f"data: {{'status': 'pending'}}\n\n"
            elif result.state == "PROCESSING":
                yield f"data: {{'status': 'processing'}}\n\n"
            elif result.state == "SUCCESS":
                info = result.info or {}
                resume_id = info.get("resume_id", "")
                yield f"data: {{'status': 'done', 'resume_id': '{resume_id}'}}\n\n"
                break
            elif result.state == "FAILURE":
                error = str(result.info) if result.info else "Unknown error"
                yield f"data: {{'status': 'failed', 'error': '{error}'}}\n\n"
                break
            else:
                yield f"data: {{'status': '{result.state.lower()}'}}\n\n"
            
            await asyncio.sleep(2)
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/", response_model=list[ResumeListItem])
async def list_resumes(
    current_user: dict = Depends(get_current_user),
) -> list[ResumeListItem]:
    """
    List all resumes for the current user.
    
    Returns only non-deleted resumes with skills_count if parsed.
    """
    user_id = _get_user_id(current_user["uid"])
    
    result = (
        supabase_client.table("resumes")
        .select("id, display_name, source_format, parse_status, created_at, structured")
        .eq("user_id", user_id)
        .is_("deleted_at", "null")
        .order("created_at", desc=True)
        .execute()
    )
    
    resumes = []
    for row in result.data or []:
        skills_count = None
        if row["parse_status"] == "done" and row.get("structured"):
            skills = row["structured"].get("skills", [])
            skills_count = len(skills) if skills else 0
        
        resumes.append(ResumeListItem(
            id=row["id"],
            display_name=row["display_name"],
            source_format=row["source_format"],
            parse_status=row["parse_status"],
            created_at=row["created_at"],
            skills_count=skills_count
        ))
    
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetail)
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
) -> ResumeDetail:
    """
    Get a specific resume by ID.
    
    Returns structured data and fingerprint if parsing is done.
    """
    user_id = _get_user_id(current_user["uid"])
    
    result = (
        supabase_client.table("resumes")
        .select("id, user_id, structured, fingerprint")
        .eq("id", resume_id)
        .is_("deleted_at", "null")
        .maybe_single()
        .execute()
    )
    
    if not result or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}},
        )
    
    # Check ownership
    if result.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}},
        )
    
    return ResumeDetail(
        resume_id=result.data["id"],
        structured=result.data.get("structured"),
        fingerprint=result.data.get("fingerprint")
    )


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Soft-delete a resume by ID.
    
    Sets deleted_at timestamp (file retained in storage for 30 days).
    """
    user_id = _get_user_id(current_user["uid"])
    
    # Verify ownership
    result = (
        supabase_client.table("resumes")
        .select("user_id")
        .eq("id", resume_id)
        .is_("deleted_at", "null")
        .maybe_single()
        .execute()
    )
    
    if not result or not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}},
        )
    
    if result.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "RESUME_NOT_FOUND", "message": "Resume not found"}},
        )
    
    # Soft delete
    supabase_client.table("resumes").update({
        "deleted_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", resume_id).execute()
    
    return None
