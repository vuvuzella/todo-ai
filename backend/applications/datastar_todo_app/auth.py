from auth0_fastapi.auth import AuthClient
from auth0_fastapi.config import Auth0Config
from fastapi import HTTPException, Request, Response, status
from jwt import PyJWKClient, decode
from pydantic import BaseModel, Field, model_validator

from applications.datastar_todo_app.config import datastar_config

jwks_client = PyJWKClient(
    f"https://{datastar_config.AUTH0_DOMAIN}/.well-known/jwks.json"
)


class DecodedToken(BaseModel):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    azp: str


class TokenSet(BaseModel):
    audience: str | None = None
    access_token: str
    scope: str | None = None
    expires_at: int

    decoded_access_token: DecodedToken

    @property
    def auth0_id(self) -> str:
        if self.decoded_access_token is not None:
            return self.decoded_access_token.sub

    @model_validator(mode="before")
    def decode_token(cls, data):
        if isinstance(data, dict):
            access_token = data.get("access_token", None)
            if access_token is not None:
                payload = decode(
                    access_token,
                    jwks_client.get_signing_key_from_jwt(access_token),
                    algorithms=["RS256"],
                    audience=datastar_config.AUTH0_AUDIENCE.unicode_host(),
                    issuer=f"https://{datastar_config.AUTH0_DOMAIN}/",
                )
                data["decoded_access_token"] = DecodedToken.model_validate(payload)
        return data


class Auth0Session(BaseModel):
    user: str | None = None
    id_token: str | None = None
    refresh_token: str | None = None
    domain: str | None = None
    connection_token_strs: list = Field(default_factory=list)

    token_set: TokenSet | None

    @model_validator(mode="before")
    def get_token_set(cls, data):
        if isinstance(data, dict):
            token_sets = data.get("token_sets", [])
            app_token_set = [
                t
                for t in token_sets
                if t["audience"] == datastar_config.AUTH0_AUDIENCE.host
            ]
            data["token_set"] = app_token_set[0] if len(app_token_set) > 0 else None

        return data


auth0_config = Auth0Config(
    domain=datastar_config.AUTH0_DOMAIN,
    audience=datastar_config.AUTH0_AUDIENCE.unicode_host(),
    client_id=datastar_config.AUTH0_CLIENT_ID,
    client_secret=datastar_config.AUTH0_CLIENT_SECRET,
    app_base_url=datastar_config.API_BASE_URL,
    secret=datastar_config.SESSION_SECRET,
)  # ty:ignore[missing-argument]

auth_client = AuthClient(auth0_config)


async def require_session_or_redirect(request: Request, response: Response):
    try:
        return await auth_client.require_session(request, response)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/auth/login"},
            )
        raise


async def get_app_session(request: Request, response: Response):
    session = await require_session_or_redirect(request, response)
    return Auth0Session.model_validate(session)
