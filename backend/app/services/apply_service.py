"""
Apply service stub.
Uses Playwright to automate form-filling and submission on job boards.
Credential access goes through encryption_service for secure storage.
"""


async def apply_to_job(job_id: str, user_id: str) -> dict:
    """
    Stub: Automatically apply to a job using stored credentials.
    Opens the job application page with Playwright and fills the form.
    Returns a status dict with the application result.
    """
    raise NotImplementedError("apply_service.apply_to_job is not implemented yet.")


async def check_application_status(application_id: str) -> dict:
    """Stub: Poll or scrape the status of a submitted application."""
    raise NotImplementedError("apply_service.check_application_status is not implemented yet.")
