from fastapi import APIRouter, Depends, Request, Security, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from applications.datastar_todo_app.auth import (
    Auth0Session,
    get_app_session,
    get_user_from_session,
    require_session_or_redirect,
)
from domain.aggregates.tasks import CreateTaskDTO, Tasks
from domain.aggregates.users import ReadUserDTO, Users
from infrastructure.repositories.base import YieldRepository
from infrastructure.repositories.tasks import TaskRepository
from infrastructure.repositories.users import UserRepository

# All in one python file for this small feature

##-- Templates ---------------------------------------#

templates = Jinja2Templates("applications/datastar_todo_app/web/templates")

tasks_router = APIRouter(
    prefix="/tasks", dependencies=[Security(require_session_or_redirect, scopes=[])]
)
##-- Pages ---------------------------------------#

page_routes = APIRouter()


@page_routes.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_tasks_page(
    request: Request,
    session: Auth0Session = Depends(get_app_session),
    user_repo: UserRepository = Depends(YieldRepository(UserRepository)),
):
    if session.token_set is not None:
        user = await user_repo.get_user_by_auth0_id(session.token_set.auth0_id)
        user_read = ReadUserDTO.model_validate(user)
    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={"user": user_read.model_dump(exclude_unset=True)},
    )


@page_routes.post("/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: CreateTaskDTO):
    # return templates.TemplateResponse(request=request, name="main.html", context={})
    ...


##-- Fragments ---------------------------------------#
fragment_routes = APIRouter(prefix="/fragments")


@fragment_routes.post("/create", response_class=HTMLResponse)
async def create_a_task(
    request: Request,
    payload: CreateTaskDTO,
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
):
    new_task = Tasks.model_validate(payload)
    new_task = await task_repo.create_task(new_task)

    html = templates.get_template("partials/task_item.html").render(task=new_task)

    def generate():
        yield "event: datastar-patch-elements\n"
        yield "data: selector #tasks-container\n"
        yield "data: mode append\n"
        for line in html.split("\n"):
            yield f"data: elements {line}\n"
        yield "\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@fragment_routes.get("/list", status_code=status.HTTP_200_OK)
async def get_tasks_list_fragment(
    request: Request,
    user: Users = Depends(get_user_from_session),
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
):

    tasks = await task_repo.get_task_by_user_id(user.id)

    html = templates.get_template("partials/task_list.html").render(tasks=tasks)

    def generate():
        yield "event: datastar-patch-elements\n"
        for line in html.split("\n"):
            yield f"data: elements {line}\n"

        yield "\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@fragment_routes.get("/{task_id}", response_class=HTMLResponse)
async def get_a_task(task_id: int, payload: CreateTaskDTO): ...


@fragment_routes.patch("/{task_id}", response_class=HTMLResponse)
async def update_a_task(task_id: int, payload: CreateTaskDTO): ...


@fragment_routes.delete("/{task_id}", response_class=HTMLResponse)
async def delete_a_task(
    task_id: int, task_repo: TaskRepository = Depends(YieldRepository(TaskRepository))
):
    await task_repo.delete_task(task_id)

    def generate():
        yield "event: datastar-patch-elements\n"
        yield f"data: selector #task-{task_id}\n"
        yield "data: mode remove\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


##-- Include Routers ---------------------------------------#
tasks_router.include_router(page_routes)
tasks_router.include_router(fragment_routes)
