import pathlib

import pytest


@pytest.fixture(scope="module")
def session():
    from infrastructure.databases.sqlite import Sqlite

    sqlite = Sqlite(
        f"sqlite:///{pathlib.Path(__file__).parent.parent.parent.parent}/dev_todo_db.sqlite"
    )
    with sqlite.session() as session:
        yield session
