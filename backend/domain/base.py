# import datetime


from pydantic import BaseModel, ConfigDict
from pydantic_config.main import SettingsModel
from snowflakekit import SnowflakeConfig, SnowflakeGenerator

# from snowflake_id_toolkit import TwitterSnowflakeIDGenerator


class DomainSettings(SettingsModel):
    NODE_ID: int = 1


domain_settings = DomainSettings()

# snowflake_generator = TwitterSnowflakeIDGenerator(
#     node_id=domain_settings.NODE_ID,
#     epoch=int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
# )

sf_config = SnowflakeConfig(
    epoch=1609459200000,
    node_id=1,
    worker_id=2,
    time_bits=39,
    node_bits=5,
    worker_bits=5,
    total_bits=53,
)

snowflake_generator = SnowflakeGenerator(config=sf_config)


async def generate_js_safe_sf_id():
    # return snowflake_generator.generate_next_id()
    return snowflake_generator.generate()


class DomainBaseConfigDict(ConfigDict): ...


class DomainBaseModel(BaseModel):
    model_config = DomainBaseConfigDict()
