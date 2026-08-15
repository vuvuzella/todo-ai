from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from domain.aggregates.tasks import CreateTaskDTO, Tasks

# All in one python file for this small feature

##-- Templates ---------------------------------------#

templates = Jinja2Templates("applications/datastar_todo_app/web/templates")

tasks_router = APIRouter(prefix="/tasks")
##-- Pages ---------------------------------------#

page_routes = APIRouter()


@page_routes.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def get_tasks_page(request: Request):
    return templates.TemplateResponse(request=request, name="tasks.html", context={})


@page_routes.post("/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: CreateTaskDTO):
    # return templates.TemplateResponse(request=request, name="main.html", context={})
    ...


##-- Fragments ---------------------------------------#
fragment_routes = APIRouter(prefix="/fragments")


@fragment_routes.post("/create", response_class=HTMLResponse)
async def create_a_task(payload: CreateTaskDTO): ...


@fragment_routes.get("/list", status_code=status.HTTP_200_OK)
async def get_tasks_list_fragment(request: Request):
    tasks = [
        Tasks.model_validate(
            CreateTaskDTO(name="task1", description="task1 description", user_id=123)
        ),
        Tasks.model_validate(
            CreateTaskDTO(name="task2", description="task2 description", user_id=123)
        ),
        Tasks.model_validate(
            CreateTaskDTO(name="task3", description="task3 description", user_id=123)
        ),
    ]
    # html = templates.get_template("partials/task_list.html").render(tasks=tasks)
    # html = " ".join(html.split())

    # async def event_stream():
    #     yield f"event: datastar-patch-elements\ndata: elements {html}\n\n"

    # return StreamingResponse(
    #     event_stream(),
    #     media_type="text/event-stream",
    #     headers={"Cache-Control": "no-cache"},
    # )

    return templates.TemplateResponse(
        request=request, name="partials/task_list.html", context={"tasks": tasks}
    )


@fragment_routes.get("/{task_id}", response_class=HTMLResponse)
async def get_a_task(task_id: int, payload: CreateTaskDTO): ...


@fragment_routes.patch("/{task_id}", response_class=HTMLResponse)
async def update_a_task(task_id: int, payload: CreateTaskDTO): ...


@fragment_routes.delete("/{task_id}", response_class=HTMLResponse)
async def delete_a_task(task_id: int, payload: CreateTaskDTO): ...


##-- Include Routers ---------------------------------------#
tasks_router.include_router(page_routes)
tasks_router.include_router(fragment_routes)
