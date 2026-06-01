from pydantic import BaseModel, ConfigDict
from pydantic_config.main import SettingsModel
from snowflake_id_toolkit import TwitterSnowflakeIDGenerator


class DomainSettings(SettingsModel):
    NODE_ID: int = 1


domain_settings = DomainSettings()

snowflake_generator = TwitterSnowflakeIDGenerator(node_id=domain_settings.NODE_ID)


class DomainBaseConfigDict(ConfigDict): ...


class DomainBaseModel(BaseModel):
    model_config = DomainBaseConfigDict()
