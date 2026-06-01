import pathlib

from sqlalchemy.sql import text


def test_sqlite_connection():
    from infrastructure.databases.sqlite import Sqlite

    sqlite = Sqlite(
        f"sqlite:///{pathlib.Path(__file__).parent.parent.parent.parent}/dev_todo_db.sqlite"
    )
    with sqlite.session() as session:
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
