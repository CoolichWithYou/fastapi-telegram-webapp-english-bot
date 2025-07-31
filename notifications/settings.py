import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    SERVER_HOST: str
    SERVER_PORT: int

    TOKEN: str

    CHUNK_SIZE: int

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    model_config = SettingsConfigDict()

    def get_rabbit_connection(self):
        user = self.RABBITMQ_DEFAULT_USER
        password = self.RABBITMQ_DEFAULT_PASS
        return f'amqp://{user}:{password}@rabbitmq:5672//'

    def get_telegram_bot_api(self):
        return f'https://api.telegram.org/bot{self.TOKEN}/sendMessage'


@lru_cache
def get_settings():
    return Settings()
