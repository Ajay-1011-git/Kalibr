"""
Parse task — processes uploaded resume files asynchronously.
Routed to the 'parse' queue.
"""

from workers.celery_app import app


@app.task(bind=True, queue="parse", name="workers.tasks.parse.parse_resume")
def parse_resume(self, resume_id: str, user_id: str, file_path: str) -> dict:
    """
    Stub: Parse an uploaded resume file (PDF or DOCX) and store the
    StructuredResume result in Supabase.

    Args:
        resume_id: UUID of the resume record in Supabase.
        user_id: Firebase UID of the owning user.
        file_path: Path to the uploaded file in Firebase Storage.

    Returns:
        dict with 'status' and 'resume_id'.
    """
    raise NotImplementedError("tasks.parse.parse_resume is not implemented yet.")
