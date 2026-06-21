"""
Parse task — processes uploaded resume files asynchronously.
Routed to the 'parse' queue.
"""

import os
import tempfile
from datetime import datetime, timezone

from app.db import supabase_client
from app.services import parse_service
from workers.celery_app import app


@app.task(bind=True, max_retries=3, default_retry_delay=30, queue="parse", name="workers.tasks.parse.parse_resume")
def parse_resume(self, resume_id: str, file_path: str, source_format: str) -> dict:
    """
    Parse an uploaded resume file (PDF or DOCX) and store the
    StructuredResume result in Supabase.

    Args:
        resume_id: UUID of the resume record in Supabase.
        file_path: Path in Supabase Storage (will download to temp file)
        source_format: 'pdf' or 'docx'

    Returns:
        dict with 'status' and 'resume_id'.
    """
    try:
        # Update status to processing
        supabase_client.table("resumes").update({
            "parse_status": "processing"
        }).eq("id", resume_id).execute()
        
        # Download file from Supabase Storage to temp file
        from app.services.storage_service import StorageService
        storage = StorageService(supabase_client)
        
        # Get signed URL and download
        file_bytes = supabase_client.storage.from_("kalibr-files").download(file_path)
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{source_format}") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Parse based on format
            if source_format == "docx":
                fingerprint = parse_service.parse_docx(tmp_path)
            else:  # pdf
                fingerprint = parse_service.parse_pdf(tmp_path)
            
            # Extract structured data
            raw_text = fingerprint.raw_full_text
            structured = parse_service.extract_structured(raw_text)
            
            # Generate embedding
            embedding = parse_service.generate_embedding(raw_text)
            
            # Update resume record
            supabase_client.table("resumes").update({
                "structured": structured.model_dump(mode="json"),
                "fingerprint": fingerprint.model_dump(mode="json"),
                "embedding": embedding,
                "parse_status": "done",
                "parse_error": None
            }).eq("id", resume_id).execute()
            
            return {"status": "done", "resume_id": resume_id}
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        # Update status to failed
        supabase_client.table("resumes").update({
            "parse_status": "failed",
            "parse_error": str(e)
        }).eq("id", resume_id).execute()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {"status": "failed", "resume_id": resume_id, "error": str(e)}
