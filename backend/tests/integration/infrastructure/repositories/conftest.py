from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def project_root(request) -> Path:
    """Returns the absolute Path to the uv project root directory."""
    return request.config.rootpath


@pytest.fixture(scope="module")
def session(project_root: Path):
    from infrastructure.databases.sqlite import Sqlite

    sqlite = Sqlite(f"sqlite:///{project_root}/dev_todo_db.sqlite")
    with sqlite.session() as session:
        yield session
