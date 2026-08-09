from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    AUTH0_DOMAIN: str = "Nope"
    AUTH0_CLIENT_ID: str = "Nope"
    AUTH0_CLIENT_SECRET: str = "Nope"
    AUTH0_AUDIENCE: str = "Nope"


api_settings = APISettings()
