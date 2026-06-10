"""
Celery application — initialises the Kalibr task queue and beat schedule.
"""

from celery import Celery
from kombu import Exchange, Queue

from app.config import settings

app = Celery(
    "kalibr",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.tasks.parse",
        "workers.tasks.rewrite",
        "workers.tasks.auto_apply",
        "workers.tasks.alerts",
        "workers.tasks.follow_up",
    ],
)

# ── Serialisation ─────────────────────────────────────────────────────────────
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# ── Queues ────────────────────────────────────────────────────────────────────
default_exchange = Exchange("default", type="direct")

app.conf.task_queues = (
    Queue("default", default_exchange, routing_key="default"),
    Queue("parse", Exchange("parse", type="direct"), routing_key="parse"),
    Queue("rewrite", Exchange("rewrite", type="direct"), routing_key="rewrite"),
    Queue("apply", Exchange("apply", type="direct"), routing_key="apply"),
    Queue("alerts", Exchange("alerts", type="direct"), routing_key="alerts"),
)
app.conf.task_default_queue = "default"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "default"

# ── Beat Schedule ─────────────────────────────────────────────────────────────
app.conf.beat_schedule = {
    # Run job alerts every hour
    "dispatch-alerts-hourly": {
        "task": "workers.tasks.alerts.dispatch_alerts",
        "schedule": 3600.0,
        "options": {"queue": "alerts"},
    },
    # Auto-apply sweep every 30 minutes
    "auto-apply-sweep": {
        "task": "workers.tasks.auto_apply.sweep_auto_apply",
        "schedule": 1800.0,
        "options": {"queue": "apply"},
    },
    # Follow-up reminder daily at 09:00 UTC
    "follow-up-reminders-daily": {
        "task": "workers.tasks.follow_up.send_follow_up_reminders",
        "schedule": 86400.0,
        "options": {"queue": "alerts"},
    },
}
