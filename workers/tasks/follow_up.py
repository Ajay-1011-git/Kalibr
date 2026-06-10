"""
Follow-up task — sends follow-up reminders for pending job applications.
Routed to the 'alerts' queue.
"""

from workers.celery_app import app


@app.task(bind=True, queue="alerts", name="workers.tasks.follow_up.send_follow_up_reminders")
def send_follow_up_reminders(self) -> dict:
    """
    Stub: Beat-triggered daily task that identifies applications past their
    follow-up date and sends reminder emails via Resend.

    Returns:
        dict with 'reminders_sent' count.
    """
    raise NotImplementedError("tasks.follow_up.send_follow_up_reminders is not implemented yet.")


@app.task(bind=True, queue="alerts", name="workers.tasks.follow_up.send_single_reminder")
def send_single_reminder(self, user_id: str, application_id: str) -> dict:
    """
    Stub: Send a follow-up reminder for a single application.

    Returns:
        dict with 'status' and 'email_id'.
    """
    raise NotImplementedError("tasks.follow_up.send_single_reminder is not implemented yet.")
