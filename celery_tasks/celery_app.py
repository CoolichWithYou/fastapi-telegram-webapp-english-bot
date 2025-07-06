from celery import Celery

celery_app = Celery(
    "celery_app",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

import tasks

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "send-daily-reminders": {
        "task": "tasks.send_reminders",
        "schedule": 86400.0,
        "options": {
            "expires": 3600
        }
    }
}
