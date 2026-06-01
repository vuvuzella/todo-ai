from pydantic import ValidationInfo, field_validator

from infrastructure.config import DatabaseSettings
from infrastructure.databases.base import Database


class PostgreConfig(DatabaseSettings):
    DB_URL: str

    @field_validator("DB_URL", mode="before")
    def db_url(cls, v, values: ValidationInfo):
        username = values.data.get("DB_USERNAME", "Nope")
        password = values.data.get("DB_PASSWORD", "Nope")
        db_name = values.data.get("DB_NAME", "Nope")
        db_port = values.data.get("DB_PORT", 123)
        db_protocol = values.data.get("DB_PROTOCOL", "Nope")
        db_host = values.data.get("DB_HOST", "Nope")
        return f"{db_protocol}://{username}:{password}@{db_host}:{db_port}/{db_name}"


class PostgreSQL(Database):
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        # Code to establish a connection to the PostgreSQL database
        pass

    def disconnect(self):
        # Code to close the connection to the PostgreSQL database
        pass

    def execute_query(self, query):
        # Code to execute a SQL query on the PostgreSQL database
        pass
