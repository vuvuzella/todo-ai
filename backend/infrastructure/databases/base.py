from abc import ABC, abstractmethod

from pydantic_config.main import SettingsModel


class DatabaseSettings(SettingsModel):
    DB_HOST: str = "localhost"
    DB_USERNAME: str = "Nill"
    DB_PASSWORD: str = "Nill"
    DB_PORT: int = 123
    DB_NAME: str = "Nill"
    DB_PROTOCOL: str = "Nill"

    DB_URL: str = "Nill"

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


# make generic
