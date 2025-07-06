from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from schema import User
from settings import get_settings

settings = get_settings()
engine = create_engine(f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
