"""
Auto-apply task — automates job application submission using Playwright.
Routed to the 'apply' queue.

Screenshots of completed applications are stored in Supabase Storage via
StorageService at:  users/{firebase_uid}/screenshots/{queue_id}.png
"""

from workers.celery_app import app


@app.task(bind=True, queue="apply", name="workers.tasks.auto_apply.sweep_auto_apply")
def sweep_auto_apply(self) -> dict:
    """
    Stub: Beat-triggered sweep that identifies users with auto-apply enabled,
    finds new matching jobs, and submits applications on their behalf.

    Returns:
        dict with 'applications_submitted' count.
    """
    raise NotImplementedError("tasks.auto_apply.sweep_auto_apply is not implemented yet.")


@app.task(bind=True, queue="apply", name="workers.tasks.auto_apply.apply_single_job")
def apply_single_job(self, user_id: str, job_id: str, resume_id: str) -> dict:
    """
    Stub: Apply to a single job for a specific user.

    On completion, captures a screenshot of the confirmation page and uploads
    it to Supabase Storage using StorageService:
        path = f"users/{user_id}/screenshots/{self.request.id}.png"
        StorageService(supabase_client).upload(path, png_bytes, "image/png")

    Returns:
        dict with 'status' and 'application_id'.
    """
    raise NotImplementedError("tasks.auto_apply.apply_single_job is not implemented yet.")
