import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV = os.getenv("ENV", "dev")

class Settings(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_host: str

    db_port: int

    model_config = SettingsConfigDict()

@lru_cache
def get_settings():
    return Settings()
