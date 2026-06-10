"""
Rewrite task — runs AI resume rewriting asynchronously.
Routed to the 'rewrite' queue.

Output files are stored in Supabase Storage via StorageService at:
  users/{firebase_uid}/resumes/{resume_id}/rewrite_{rewrite_id}.docx
  users/{firebase_uid}/resumes/{resume_id}/rewrite_{rewrite_id}.pdf
"""

from workers.celery_app import app


@app.task(bind=True, queue="rewrite", name="workers.tasks.rewrite.rewrite_resume")
def rewrite_resume(self, task_id: str, resume_id: str, job_id: str, user_id: str) -> dict:
    """
    Stub: Generate a tailored resume rewrite using NVIDIA NIM and store the
    RewriteResult in Supabase DB. Then export DOCX and PDF and upload both
    to Supabase Storage using StorageService:

        storage = StorageService(supabase_client)
        docx_path = f"users/{user_id}/resumes/{resume_id}/rewrite_{task_id}.docx"
        pdf_path  = f"users/{user_id}/resumes/{resume_id}/rewrite_{task_id}.pdf"
        storage.upload(docx_path, docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        storage.upload(pdf_path,  pdf_bytes,  "application/pdf")

    Updates task status for polling via the /rewrite/{task_id} endpoint.

    Args:
        task_id: UUID used to poll task progress from the frontend.
        resume_id: UUID of the source StructuredResume.
        job_id: UUID of the target NormalisedJob.
        user_id: Firebase UID of the owning user.

    Returns:
        dict with 'status' and 'rewrite_result_id'.
    """
    raise NotImplementedError("tasks.rewrite.rewrite_resume is not implemented yet.")
