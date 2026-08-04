from contextlib import contextmanager

from pydantic import ValidationInfo, field_validator
from sqlmodel import Session, create_engine

from infrastructure.config import DatabaseSettings
from infrastructure.databases.base import Database


class PostgreConfig(DatabaseSettings):
    DB_URL: str

    @field_validator("DB_URL", mode="before")
    def db_url(cls, v, values: ValidationInfo):
        username = values.data.get("DB_USER", "Nope")
        password = values.data.get("DB_PASS", "Nope")
        db_name = values.data.get("DB_NAME", "Nope")
        db_port = values.data.get("DB_PORT", 123)
        db_protocol = values.data.get("DB_PTCL", "Nope")
        db_host = values.data.get("DB_HOST", "Nope")
        return f"{db_protocol}://{username}:{password}@{db_host}:{db_port}/{db_name}"


postgres_db_config = PostgreConfig()


class PostgreSQL(Database):
    def __init__(self, db_url: str | None = None):
        url = db_url or postgres_db_config.DB_URL
        self._engine = create_engine(f"{url}", echo=True)

    @contextmanager
    def session(self):
        with Session(self._engine) as session:
            yield session
            session.flush()
            session.commit()


postgres_db = PostgreSQL()
