import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str
    server_host: str
    server_port: int

    model_config = SettingsConfigDict()

@lru_cache
def get_settings():
    return Settings()
