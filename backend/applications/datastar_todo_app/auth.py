from auth0_fastapi.auth import AuthClient
from auth0_fastapi.config import Auth0Config
from fastapi import HTTPException, Request, Response, status

from applications.datastar_todo_app.config import datastar_config

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
