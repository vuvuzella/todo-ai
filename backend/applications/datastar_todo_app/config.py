from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class DatastarAppSettings(BaseSettings):
    AUTH0_DOMAIN: str = "Nope"
    AUTH0_CLIENT_ID: str = "Nope"
    AUTH0_CLIENT_SECRET: str = "Nope"
    AUTH0AUTH0_AUDIENCE: HttpUrl = HttpUrl("https://nope.nope.nope")
    SESSION_SECRET: str = "Nope"
    API_BASE_URL: HttpUrl = HttpUrl("http://localhost:8001")
    COOKIE_SECURE: bool = False


datastar_config = DatastarAppSettings()
