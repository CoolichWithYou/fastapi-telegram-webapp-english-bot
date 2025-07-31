from celery import Celery
from settings import Settings

settings = Settings()
celery_app = Celery(
    "my_project",
    broker=settings.get_rabbit_connection(),
    backend="redis://redis:6379/0"
)

import tasks

celery_app.conf.task_routes = {
    'send_reminder_message': {'queue': 'messages'},
    'send_reminders': {'queue': 'main'},
}
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
