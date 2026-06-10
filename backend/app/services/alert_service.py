"""
Alert service stub.
Sends email notifications to users via Resend when new matching jobs are found.
"""


async def send_job_alert(user_id: str, job_ids: list[str]) -> None:
    """
    Stub: Send a job-alert email to the user listing the new matching jobs.
    Uses the Resend SDK and the RESEND_API_KEY from settings.
    """
    raise NotImplementedError("alert_service.send_job_alert is not implemented yet.")


async def send_follow_up_reminder(user_id: str, application_id: str) -> None:
    """Stub: Send a follow-up reminder email for an application past its follow-up date."""
    raise NotImplementedError("alert_service.send_follow_up_reminder is not implemented yet.")
