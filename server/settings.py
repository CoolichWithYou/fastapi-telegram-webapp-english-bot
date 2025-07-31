from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    def get_connection(self):
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.DB_HOST
        port = self.DB_PORT
        db = self.POSTGRES_DB
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    model_config = SettingsConfigDict()


@lru_cache
def get_settings():
    return Settings()
