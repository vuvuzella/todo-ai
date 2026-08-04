from enum import StrEnum

from pydantic_config.main import SettingsModel


class DBType(StrEnum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"

    @classmethod
    def _missing_(cls, value):
        normalised = value.lower() if isinstance(value, str) else str(value).lower()
        for m in cls:
            if m.lower() == normalised:
                return m
        return None


class InfraSettings(SettingsModel):
    DB_TYPE: DBType = DBType.SQLITE


from pydantic import model_validator
from pydantic_config.main import SettingsModel


class DatabaseSettings(SettingsModel):
    DB_PTCL: str = "Nope"
    DB_NAME: str = "Nope"
    DB_HOST: str = "Nope"
    DB_PORT: int = 123
    DB_USER: str = "Nope"
    DB_PASS: str = "Nope"

    DB_URL: str = "Nope"

    @model_validator(mode="before")
    def create_db_url(cls, values: any):
        if isinstance(values, dict):
            db_ptcl = values.get("DB_PTCL", "Nope")
            db_name = values.get("DB_NAME", "Nope")
            db_host = values.get("DB_HOST", "Nope")
            db_port = values.get("DB_PORT", 123)
            db_user = values.get("DB_USER", "Nope")
            db_pass = values.get("DB_PASS", "Nope")

            db_url = values.get("DB_URL", None)

            if db_url is None:
                # db_url = f"{db_ptcl}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?sslmode=allow"
                db_url = (
                    f"{db_ptcl}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
                )
                values["DB_URL"] = db_url

        return values


database_settings = DatabaseSettings()

infra_settings = InfraSettings()
