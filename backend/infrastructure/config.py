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


infra_settings = InfraSettings()
