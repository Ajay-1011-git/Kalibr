"""
Alerts task — dispatches job-alert emails to subscribed users.
Routed to the 'alerts' queue.
"""

from workers.celery_app import app


@app.task(bind=True, queue="alerts", name="workers.tasks.alerts.dispatch_alerts")
def dispatch_alerts(self) -> dict:
    """
    Stub: Beat-triggered task that queries new jobs matching each user's alert
    criteria and sends an email digest via Resend.

    Returns:
        dict with 'alerts_sent' count.
    """
    raise NotImplementedError("tasks.alerts.dispatch_alerts is not implemented yet.")


@app.task(bind=True, queue="alerts", name="workers.tasks.alerts.send_single_alert")
def send_single_alert(self, user_id: str, job_ids: list) -> dict:
    """
    Stub: Send a single job-alert email to a specific user.

    Returns:
        dict with 'status' and 'email_id'.
    """
    raise NotImplementedError("tasks.alerts.send_single_alert is not implemented yet.")
