import asyncio

import uvicorn
from auth0_fastapi.auth import AuthClient
from auth0_fastapi.config import Auth0Config
from auth0_fastapi.server.routes import register_auth_routes, router
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.config = auth0_config
app.state.auth_client = auth_client

app.add_middleware(SessionMiddleware, secret_key=datastar_config.AUTH0_CLIENT_SECRET)

app.mount(
    "/static",
    StaticFiles(directory="applications/datastar_todo_app/static"),
    name="static",
)
templates = Jinja2Templates(directory="applications/datastar_todo_app/templates")


@app.get("/", response_class=HTMLResponse)
async def get_main_route_check(request: Request, response: Response):
    store_options = {"request": request, "response": response}
    session = await auth_client.client.get_session(store_options)
    if session is not None:
        return RedirectResponse("/home")
    else:
        return RedirectResponse("/auth/login")


@app.get("/home", response_class=HTMLResponse)
async def get_home(
    request: Request, session: dict = Depends(auth_client.require_session)
):
    token_sets = session.get("token_sets")
    token = token_sets[0].get("access_token", None) if token_sets is not None else None
    # auth0_id
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "api_url": datastar_config.API_ENDPOINT,
            "access_token": token,
        },
    )


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


register_auth_routes(router, auth0_config)
app.include_router(router)


async def start():
    uvicorn.run("applications.datastar_todo_app.app:start", host="0.0.0.0", port=8001)


if __name__ == "__main__":
    asyncio.run(start())
