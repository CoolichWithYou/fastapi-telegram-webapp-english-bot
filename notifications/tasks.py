import asyncio

import requests
from aiogram import Bot
from celery import group
from celery_app import celery_app
from requests.exceptions import RequestException
from settings import get_settings

settings = get_settings()

bot = Bot(token=settings.TOKEN)

TELEGRAM_API_URL = settings.get_telegram_bot_api()

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
)
def send_reminder_message(self, chat_id):
    payload = {
        "chat_id": chat_id,
        "text": "Our algorithms tell us that you might want to learn words! :) 🌱"
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def send_reminders(self):
    try:
        users = get_inactive_users()
        tasks = [send_reminder_message.s(u['chat_id']) for u in users]

        for i in range(0, len(tasks), settings.CHUNK_SIZE):
            group(tasks[i:i + settings.CHUNK_SIZE]).apply_async()

    except RequestException as exc:
        raise self.retry(exc=exc)


def get_inactive_users():
    response = requests.get(
        f'http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/api/inactive_users',
        timeout=10
    )
    response.raise_for_status()
    return response.json()
