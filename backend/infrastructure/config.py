from pydantic import ValidationInfo, field_validator
from pydantic_config.main import SettingsModel


class DatabaseSettings(SettingsModel):
    DB_HOST: str = "localhost"
    DB_USERNAME: str = "Nope"
    DB_PASSWORD: str = "Nope"
    DB_PORT: int = 5432
    DB_NAME: str = "Nope"
    DB_PROTOCOL: str = "Nope"

    # DB_URL: str
    # @field_validator("DB_URL", mode="before")
    # def db_url(cls, v, values: ValidationInfo):
    #     username = values.data.get("DB_USERNAME", "Nope")
    #     password = values.data.get("DB_PASSWORD", "Nope")
    #     db_name = values.data.get("DB_NAME", "Nope")
    #     db_port = values.data.get("DB_PORT", 123)
    #     db_protocol = values.data.get("DB_PROTOCOL", "Nope")
    #     db_host = values.data.get("DB_HOST", "Nope")
    #     return f"{db_protocol}://{username}:{password}@{db_host}:{db_port}/{db_name}"
