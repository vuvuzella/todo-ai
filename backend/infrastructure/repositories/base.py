from fastapi import Depends
from sqlmodel import Session

from infrastructure.config import DBType, infra_settings
from infrastructure.databases.sqlite import sqlite_db


class Repository:
    def __init__(self, session: Session):
        self.session = session


class YieldSession:
    def __call__(self):
        match infra_settings.DB_TYPE:
            case DBType.SQLITE:
                with sqlite_db.session() as session:
                    yield session
                    session
            case _:
                raise Exception(f"Unknown database setting: {infra_settings.DB_TYPE}")


class YieldRepository:
    def __init__(self, repo_type: type[Repository]):
        self._repo_type = repo_type

    # TODO make this switchable with other databases
    def __call__(self, session: Session = Depends(YieldSession())):
        yield self._repo_type(session)
