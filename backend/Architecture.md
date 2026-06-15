# Architecture Reference: FastAPI + Datastar + DDD

## 1. Architectural Decisions

### Frontend: Datastar over HTMX

Datastar was chosen over HTMX because it unifies both backend-driven reactivity (HTMX's strength) and frontend reactivity (Alpine.js's strength) into a single ~14KB library. This eliminates the need to coordinate two separate libraries and provides a first-class Server-Sent Events (SSE) model that aligns naturally with FastAPI's async capabilities.

The key trade-off accepted: Datastar is younger than HTMX, so its community and ecosystem are smaller. The docs are good but learning resources are fewer.

### Deployment: Two separate instances

The application is split into two independently deployed FastAPI services:

- **Frontend instance** — serves Jinja2-rendered HTML pages and static files. Has no domain logic. Its only job is to deliver HTML to the browser with Datastar attributes baked in.
- **API instance** — owns all domain logic, SSE fragment endpoints, and command endpoints. This is where everything meaningful happens.

A reverse proxy (Caddy locally, Caddy or nginx in production) sits in front of both and presents a single domain to the browser, routing `/*` to the frontend and `/api/*` to the API.

### Communication: Browser calls the API directly

When a user interacts with the page, Datastar attributes in the HTML send requests directly from the browser to the API instance through the reverse proxy. The frontend instance is not in that data path at runtime. It only delivers the initial HTML page.

This means the frontend instance is intentionally thin — it has no need for the shared domain package beyond basic configuration.

### Domain architecture: Domain-Driven Design (DDD)

The API instance is organised into three layers housed in a `shared/` internal Python package:

- **Domain layer** — pure Python, zero framework imports. Entities, value objects, repository Protocol interfaces, domain events.
- **Application layer** — use cases (commands and queries) that orchestrate the domain. Depends only on the domain layer.
- **Infrastructure layer** — concrete implementations of repository interfaces using SQLAlchemy. Also holds external service integrations.

Both instances install `shared/` as a local package dependency. In practice the frontend instance barely uses it, but the boundary is there for the cases where it needs to (e.g. rendering initial state on page load using a query use case directly).

### Environment configuration: file-based switching

A `.env.development` and `.env.production` file in each service control environment-specific values. The most important is `API_BASE_URL`, which determines whether Datastar attributes in templates point to `http://localhost:8001` (local dev, two ports with CORS) or `/api` (production, resolved by the reverse proxy).

---

## 2. Folder Structure

```
my_app/
│
├── docker-compose.yml                  # local dev: frontend + api + proxy + db
├── Caddyfile                           # local reverse proxy config
│
├── shared/                             # internal Python package, installed by both services
│   ├── pyproject.toml
│   └── src/
│       └── shared/
│           ├── domain/
│           │   ├── user/
│           │   │   ├── entity.py       # User aggregate root
│           │   │   ├── value_objects.py # Email, UserId
│           │   │   ├── repository.py   # Protocol interface
│           │   │   └── events.py       # UserCreated, etc.
│           │   └── order/
│           │       ├── entity.py
│           │       ├── value_objects.py
│           │       ├── repository.py
│           │       └── events.py
│           ├── application/
│           │   ├── commands/
│           │   │   ├── create_user.py  # CreateUserCommand + CreateUserUseCase
│           │   │   └── place_order.py
│           │   └── queries/
│           │       ├── get_user.py
│           │       └── list_orders.py
│           └── infrastructure/
│               ├── persistence/
│               │   ├── database.py     # SQLAlchemy engine + async session factory
│               │   ├── user_repository.py
│               │   └── order_repository.py
│               └── external/
│                   └── email_service.py
│
├── frontend/                           # deployed as its own container/process
│   ├── pyproject.toml                  # depends on `shared`
│   ├── .env.development
│   ├── .env.production
│   ├── main.py                         # FastAPI() app entry point
│   └── app/
│       ├── config.py                   # loads env vars via pydantic-settings
│       ├── dependencies.py             # Depends() factories (minimal)
│       └── routes/
│           └── pages.py                # GET routes returning Jinja2 templates
│   ├── templates/
│   │   ├── base.html                   # includes datastar.js script tag
│   │   ├── index.html
│   │   └── components/                 # reusable Jinja2 partials
│   │       └── user_card.html
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── datastar.js             # self-hosted Datastar bundle
│
└── api/                                # deployed as its own container/process
    ├── pyproject.toml                  # depends on `shared`
    ├── .env.development
    ├── .env.production
    ├── main.py                         # FastAPI() app entry point
    └── app/
        ├── config.py
        ├── dependencies.py             # full Depends() chain: session → repo → use case
        └── routes/
            ├── fragments.py            # GET /sse/* — Datastar SSE endpoints
            └── commands.py             # POST /cmd/* — domain command endpoints
```

---

## 3. Functional Blocks

### Reverse Proxy

The only publicly exposed component. Receives all browser traffic on a single domain and port, then routes it to the correct internal service based on the URL path prefix. It also handles TLS termination in production (HTTPS at the edge, plain HTTP internally).

In local development: Caddy running in Docker Compose.
In production: Caddy or nginx on a VPS, or a managed load balancer (AWS ALB, GCP Load Balancer) in cloud deployments.

### Frontend Instance

A thin FastAPI application. Its routes render Jinja2 templates and return full HTML pages. The templates contain Datastar `data-on` and `data-signals` attributes that point to the API instance's endpoints. It serves `datastar.js` and CSS as static files.

It reads `API_BASE_URL` from its environment config and injects it into every template context so Datastar attributes resolve correctly in both development and production.

```python
# frontend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8001"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# frontend/app/routes/pages.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/users")
async def users_page(request: Request):
    return templates.TemplateResponse("users.html", {
        "request": request,
        "api_url": settings.api_base_url,
    })
```

```html
<!-- templates/users.html -->
<div id="user-list"
     data-on:load="@get('{{ api_url }}/sse/users')">
</div>
<button data-on:click="@post('{{ api_url }}/cmd/users/create')">
  Create user
</button>
```

### API Instance

The substantive service. It has three responsibilities:

1. **SSE fragment endpoints** (`/sse/*`) — long-lived GET connections. Datastar opens these from the browser and receives a stream of `text/event-stream` events that patch the DOM or update signals.
2. **Command endpoints** (`/cmd/*`) — short-lived POST/PUT/DELETE requests triggered by user actions. These run a use case and may return SSE events that update the UI.
3. **Wiring** — the `dependencies.py` file constructs the full dependency chain (DB session → repository → use case) using FastAPI's `Depends()` system.

```python
# api/app/routes/fragments.py
from fastapi import APIRouter, Depends
from datastar_py.fastapi import DatastarResponse
from datastar_py import ServerSentEventGenerator as SSE
from app.dependencies import get_list_orders_query
from shared.application.queries.list_orders import ListOrdersUseCase

router = APIRouter()

@router.get("/sse/orders", response_class=DatastarResponse)
async def orders_fragment(
    query: ListOrdersUseCase = Depends(get_list_orders_query),
):
    async def stream():
        orders = await query.execute()
        html = render_orders_partial(orders)   # a helper that builds HTML string
        yield SSE.patch_elements(html)
    return stream()
```

```python
# api/app/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.infrastructure.persistence.database import get_session
from shared.infrastructure.persistence.order_repository import SQLOrderRepository
from shared.application.queries.list_orders import ListOrdersUseCase

def get_order_repo(
    session: AsyncSession = Depends(get_session),
) -> SQLOrderRepository:
    return SQLOrderRepository(session)

def get_list_orders_query(
    repo: SQLOrderRepository = Depends(get_order_repo),
) -> ListOrdersUseCase:
    return ListOrdersUseCase(repo)
```

### Shared Package

An internal Python package installed into both services at build time. It is not a running service — it is code. It contains the three DDD layers:

- **Domain** — pure Python dataclasses, `Protocol` repository interfaces, value objects. No imports from FastAPI, SQLAlchemy, or any framework.
- **Application** — use case classes. Each takes repository interfaces in `__init__` and has a single `execute()` method. Knows nothing about HTTP.
- **Infrastructure** — SQLAlchemy models and repository implementations, async session factory, external service clients.

The dependency direction is strict: `infrastructure → application → domain`. The domain imports nothing from the outer layers.

### Database

PostgreSQL in production, SQLite acceptable for development. Accessed exclusively through the infrastructure layer's repository implementations. The domain layer defines what it needs via `Protocol` interfaces; infrastructure delivers it.

---

## 4. Request Flow

### Page load (browser → frontend)

```
1. Browser requests GET /users
2. Reverse proxy matches /* → routes to frontend instance
3. Frontend route handler reads API_BASE_URL from config
4. Jinja2 renders users.html with api_url injected
5. Browser receives full HTML page
6. Datastar script initialises, reads data-* attributes
7. data-on:load fires → browser opens SSE connection to /api/sse/users
```

### SSE data fetch (browser → API)

```
1. Browser sends GET /api/sse/users
2. Reverse proxy matches /api/* → routes to API instance
3. FastAPI resolves Depends() chain: session → repo → use case
4. Use case calls repository, repository queries DB
5. Handler yields SSE.patch_elements(...) events
6. Datastar receives events, patches DOM
7. Connection stays open for further events
```

### Command (user action → API)

```
1. User clicks button with data-on:click="@post('/api/cmd/users/create')"
2. Datastar sends POST /api/cmd/users/create with current signals as JSON body
3. Reverse proxy routes to API instance
4. FastAPI resolves Depends() chain
5. Use case validates input, writes to DB
6. Handler returns SSE event confirming the change
7. Datastar patches the relevant DOM element
```

---

## 5. Environment Configuration

Each service has two env files. Pydantic-settings loads the correct one based on the `ENV` variable or the default `.env` filename.

```
# frontend/.env.development
API_BASE_URL=http://localhost:8001
ENVIRONMENT=development

# frontend/.env.production
API_BASE_URL=/api
ENVIRONMENT=production
```

```
# api/.env.development
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/myapp
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:8000"]

# api/.env.production
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/myapp
ENVIRONMENT=production
CORS_ORIGINS=["https://myapp.com"]
```

In production `API_BASE_URL=/api` works because the reverse proxy resolves `/api/*` to the API instance transparently. The browser never needs to know the API's actual host or port.

---

## 6. Local Development Setup

Run both services on different ports. The API enables CORS for the frontend's origin.

```yaml
# docker-compose.yml
services:
  proxy:
    image: caddy:latest
    ports:
      - "8000:80"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile

  frontend:
    build: ./frontend
    environment:
      - ENV=development
    volumes:
      - ./frontend:/app     # hot reload

  api:
    build: ./api
    environment:
      - ENV=development
    volumes:
      - ./api:/app
      - ./shared:/shared

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
```

```
# Caddyfile (local)
:80 {
    handle /api/* {
        reverse_proxy api:8000
    }
    handle {
        reverse_proxy frontend:8000
    }
}
```

Alternatively, without Docker, run two terminals:

```bash
# terminal 1 — API on port 8001
cd api && uvicorn main:app --port 8001 --reload

# terminal 2 — frontend on port 8000
cd frontend && uvicorn main:app --port 8000 --reload
```

With this setup, add CORS middleware to the API and set `API_BASE_URL=http://localhost:8001` in `frontend/.env.development`.

---

## 7. Production Deployment

### Minimum viable infrastructure

```
Internet
   │  HTTPS :443
   ▼
[ VPS or cloud VM ]
   ├── Caddy (TLS termination + reverse proxy)
   ├── Frontend container  (uvicorn, internal port)
   ├── API container       (uvicorn, internal port)
   └── PostgreSQL          (internal, not exposed)
```

Caddy handles automatic TLS certificates via Let's Encrypt — no manual certificate management needed.

```
# Caddyfile (production)
myapp.com {
    handle /api/* {
        reverse_proxy api:8000
    }
    handle {
        reverse_proxy frontend:8000
    }
}
```

### Scaling considerations

Because the two services are independent:

- The frontend scales horizontally with a simple load balancer — it is stateless.
- The API scales horizontally if the DB connection pool is configured correctly and sessions are not stored in process memory.
- The DB is the single stateful component. Start with a managed Postgres service (Railway, Supabase, AWS RDS) rather than self-hosting it.

---

## 8. Resources

### Datastar

- Official docs and guide: https://data-star.dev/guide/getting_started
- The Tao of Datastar (design philosophy): https://data-star.dev/guide/the_tao_of_datastar
- datastar-py SDK (PyPI): https://pypi.org/project/datastar-py/
- datastar-py deep reference: https://deepwiki.com/starfederation/datastar-python
- Community resources list: https://alvarolm.github.io/datastar-resources/
- Talk Python episode on Datastar: https://talkpython.fm/episodes/show/537/datastar-modern-web-dev-simplified

### FastAPI

- Official tutorial: https://fastapi.tiangolo.com/tutorial/
- Dependency injection: https://fastapi.tiangolo.com/tutorial/dependencies/
- SSE in FastAPI: https://fastapi.tiangolo.com/tutorial/server-sent-events/
- Bigger applications with routers: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Async SQL with SQLAlchemy: https://fastapi.tiangolo.com/tutorial/sql-databases/

### Domain-Driven Design

- *Domain-Driven Design* by Eric Evans (the original book)
- *Implementing Domain-Driven Design* by Vaughn Vernon (more practical)
- Architecture Patterns with Python (free online): https://www.cosmicpython.com/
- The cosmic python book maps DDD concepts directly onto a Python/FastAPI-style project and is the closest written resource to this architecture.

### Jinja2

- Official docs: https://jinja.palletsprojects.com/en/stable/
- FastAPI + Jinja2 templates: https://fastapi.tiangolo.com/advanced/templates/

### Reverse Proxy

- Caddy getting started: https://caddyserver.com/docs/getting-started
- Caddy reverse proxy docs: https://caddyserver.com/docs/quick-starts/reverse-proxy
- nginx beginner's guide: https://nginx.org/en/docs/beginners_guide.html

### Docker and Docker Compose

- Docker getting started: https://docs.docker.com/get-started/
- Docker Compose overview: https://docs.docker.com/compose/
- FastAPI in containers: https://fastapi.tiangolo.com/deployment/docker/

### SQLAlchemy (async)

- Async SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic migrations: https://alembic.sqlalchemy.org/en/latest/tutorial.html

### pydantic-settings (env file loading)

- Official docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
