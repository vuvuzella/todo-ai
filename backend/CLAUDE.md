# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI backend for a full-stack todo app (React frontend lives in `../frontend`, monorepo). Architecture is influenced by the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template). Python 3.13, managed with `uv`, package manager commands wrapped via `just`.

## Commands

All commands run from `backend/`.

- **Sync dependencies**: `just sync` (or `uv sync`)
- **Add a dependency**: `just add <package>` / dev dependency: `just add-dev <package>`
- **Run the API**: `uv run api` (entrypoint `applications.api.app:start`, runs uvicorn on `0.0.0.0:8000` with `reload=True`)
- **Run tests**: `just test` defaults to unit tests; `just test integration` for integration tests. Under the hood: `uv run pytest ./tests/{unit,integration} -vvsrP`
- **Run a single test**: bypass the justfile and call pytest directly, e.g. `uv run pytest tests/unit/domain/test_tasks.py::test_complete_task -vvsrP`
- **Build**: `just build` (`uv build`)

Note: `tumult` (providing `pydantic_config`, used for all `*Settings` classes) is pulled from a private AWS CodeArtifact index. If `uv sync` fails on auth, `just login` / `just token` generate the CodeArtifact token (requires AWS SSO profile `vuvuzella`).

Type checking is configured via `basedpyright` in `pyproject.toml`, scoped to `applications/api` only.

## Architecture

The backend follows a layered/clean-architecture style split into three packages, each independently packaged in `pyproject.toml` (`[tool.hatch.build.targets.wheel] packages = ["applications", "domain", "infrastructure"]`):

### `domain/` — business logic and models
- `domain/aggregates/<name>.py` defines an aggregate as a `SQLModel` table (e.g. `Task` in `tasks.py`) plus its DTOs: `Create*DTO`, `Read*DTO`, `Update*DTO`, `Delete*DTO`, `Complete*DTO` — one DTO per use case/intent rather than a single shared schema.
- Mutating behavior lives on the aggregate itself as methods that take a DTO (e.g. `Task.update_from_dto`, `Task.complete`), not in the API layer or repository. These methods enforce **optimistic concurrency**: every mutation DTO carries a `version`, checked via `_check_version` against the row's current `version` before applying changes, then `_increment_version` bumps it. Any new mutation should follow this same DTO-in/aggregate-method pattern.
- IDs are Twitter-snowflake IDs generated client-side via `domain/base.py`'s `snowflake_generator.generate_next_id` (set as the model's `default_factory`), not DB auto-increment. `ReadTaskDTO` serializes `id` to a string in JSON output (`field_serializer`) since snowflake ints can exceed JS safe-integer range on the frontend.
- `domain/aggregates/users.py` and `lists_todos.py` are stubs/placeholders for future aggregates — only `tasks.py` is wired up end-to-end.

### `infrastructure/` — persistence
- `infrastructure/config.py` holds `InfraSettings` with `DB_TYPE` (`sqlite`/`postgres`), which selects the active database backend at runtime.
- `infrastructure/databases/` defines a `Database` ABC (`base.py`) with concrete `Sqlite` and `PostgreSQL` (currently a stub — only sqlite is implemented). `sqlite_db` is a module-level long-running singleton; `Sqlite.session()` is a contextmanager that yields a `Session` and auto-flushes/commits on exit.
- `infrastructure/repositories/` wraps DB access: `Repository` is a thin base holding a `Session`; `TaskRepository` implements CRUD for `Task` (`get_all_tasks`, `get_task_by_id`, `create_task`, `update_task`, `delete_task`). Repositories persist explicitly (`session.add`/`merge` + `session.commit()`) — domain aggregate methods only mutate in-memory state, so an API handler must call the repository's persistence method to actually save changes.
- `YieldSession`/`YieldRepository` (in `infrastructure/repositories/base.py`) are FastAPI dependency-injection helpers used as `Depends(YieldRepository(TaskRepository))`, switching on `infra_settings.DB_TYPE` to produce a per-request session/repository pair.

### `applications/api/` — HTTP layer
- `app.py` is the single FastAPI app and route module. Handlers are intentionally thin: parse path/body into a domain DTO → call the aggregate method to mutate → call the repository method to persist → return, with `response_model` set to the relevant `Read*DTO`.
- Route handlers depend on a repository via `Depends(YieldRepository(TaskRepository))`, never construct sessions/repositories directly.

### `tests/`
- `tests/unit/` — pure domain logic tests, no DB (e.g. `test_tasks.py` exercises aggregate methods + DTOs directly via a `task_factory` fixture).
- `tests/integration/` — hits a real database. The `session` fixture (`tests/integration/infrastructure/repositories/conftest.py`) opens a `Sqlite` session against `dev_todo_db.sqlite` at the project root; tests insert/clean up their own rows via fixtures (e.g. `add_tasks`, `remove_new_task`) rather than relying on a shared seeded DB.

## Database

Dev DB is a local SQLite file (`dev_todo_db.sqlite`, gitignored). `docker-compose.yaml` provisions a Postgres 14.6 container (`fastapi_todo_app_db`, port `7653`) for when the Postgres backend is implemented — it's currently a stub in `infrastructure/databases/postgresql.py`.
