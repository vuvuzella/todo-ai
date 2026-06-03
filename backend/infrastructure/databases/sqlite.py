from contextlib import contextmanager

from pydantic import ValidationInfo, field_validator
from sqlmodel import Session, create_engine

from infrastructure.databases.base import Database, DatabaseSettings


class SqliteConfig(DatabaseSettings):
    DB_URL: str

    @field_validator("DB_URL", mode="before")
    def db_url(cls, v, values: ValidationInfo):
        db_name = values.data.get("DB_NAME", "Nope")
        return f"sqlite:///{db_name}"


sqlite_config = SqliteConfig()  # ty:ignore[missing-argument]


class Sqlite(Database):
    """
    A long running instance of the sqlite database.
    """

    def __init__(self, db_url: str | None = None):
        url = db_url or sqlite_config.DB_URL
        self._engine = create_engine(f"{url}", echo=True)

    @contextmanager
    def session(self):
        with Session(self._engine) as session:
            yield session
            session.flush()
            session.commit()


sqlite_db = Sqlite()  # ty:ignore[missing-argument]
