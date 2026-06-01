from abc import ABC, abstractmethod

from pydantic_config.main import SettingsModel


class DatabaseSettings(SettingsModel):
    DB_HOST: str = "localhost"
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_NAME: str
    DB_PROTOCOL: str

    DB_URL: str

    # @field_validator("DB_URL", mode="before")
    # def db_url(cls, v, values: ValidationInfo):
    #     username = values.data.get("DB_USERNAME", "Nope")
    #     password = values.data.get("DB_PASSWORD", "Nope")
    #     db_name = values.data.get("DB_NAME", "Nope")
    #     db_port = values.data.get("DB_PORT", 123)
    #     db_protocol = values.data.get("DB_PROTOCOL", "Nope")
    #     db_host = values.data.get("DB_HOST", "Nope")
    #     return f"{db_protocol}://{username}:{password}@{db_host}:{db_port}/{db_name}"


class Database(ABC):
    @abstractmethod
    def session(self):
        # Implement session management logic here
        pass

    # def __init__(self, connection_string: str):
    #     self.connection_string = connection_string
    #     self.connection = None

    # @abstractmethod
    # def connect(self):
    #     # Implement connection logic here
    #     pass

    # @abstractmethod
    # def disconnect(self):
    #     # Implement disconnection logic here
    #     pass

    # @abstractmethod
    # def execute_query(self, query):
    #     # Implement query execution logic here
    #     pass


# make generic
class YieldDatabase:
    def __init__(self, db_type: type[Database]):
        self._db_type = db_type

    def __call__(self, *args, **kwargs):
        db_instance = self._db_type(*args, **kwargs)
        with db_instance as db:
            yield db
