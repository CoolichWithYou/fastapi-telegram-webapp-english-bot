import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("ENV", "dev")


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    server_host: str
    server_port: int

    token: str

    chunk_size: int

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    model_config = SettingsConfigDict()

    def get_rabbit_connection(self):
        user = self.RABBITMQ_DEFAULT_USER
        password = self.RABBITMQ_DEFAULT_PASS
        return f'amqp://{user}:{password}@rabbitmq:5672//'


@lru_cache
def get_settings():
    return Settings()
