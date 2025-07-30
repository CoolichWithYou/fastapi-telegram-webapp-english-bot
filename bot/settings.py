import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: str
    SERVER_HOST: str
    SERVER_PORT: int

    model_config = SettingsConfigDict()

@lru_cache
def get_settings():
    return Settings()
