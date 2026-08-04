import uvicorn
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from domain.aggregates import (
    CompleteTaskDTO,
    CreateTaskDTO,
    CreateUserDTO,
    ReadTaskDTO,
    ReadUserDTO,
    Tasks,
    UpdateTaskDTO,
    Users,
)
from infrastructure.repositories.base import YieldRepository
from infrastructure.repositories.tasks import TaskRepository
from infrastructure.repositories.users import UserRepository

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tasks", response_model=list[ReadTaskDTO], status_code=status.HTTP_200_OK)
def get_tasks(
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
) -> list[Tasks]:
    return task_repo.get_all_tasks()


@app.get("/tasks/{task_id}", response_model=ReadTaskDTO, status_code=status.HTTP_200_OK)
def get_task_by_id(
    task_id: int, task_repo: TaskRepository = Depends(YieldRepository(TaskRepository))
) -> Tasks | None:
    return task_repo.get_task_by_id(task_id)


@app.post("/tasks", response_model=ReadTaskDTO, status_code=status.HTTP_201_CREATED)
def create_task(
    task: CreateTaskDTO,
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
) -> Tasks:
    return task_repo.create_task(Tasks.from_create_dto(task))


@app.patch(
    "/tasks/{task_id}", response_model=ReadTaskDTO, status_code=status.HTTP_200_OK
)
def update_task(
    task_id: int,
    payload: UpdateTaskDTO,
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
):
    task = task_repo.get_task_by_id(task_id)
    if task is None:
        return
    task = task.update_from_dto(payload)
    return task


@app.delete("/tasks/{task_id}", response_model=None, status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
):
    task_repo.delete_task(task_id)


@app.patch(
    "/tasks/{task_id}/complete",
    response_model=ReadTaskDTO,
    status_code=status.HTTP_200_OK,
)
def complete_task(
    task_id: int,
    payload: CompleteTaskDTO,
    task_repo: TaskRepository = Depends(YieldRepository(TaskRepository)),
):
    task = task_repo.get_task_by_id(task_id)
    if task is None:
        raise Exception("Task Not found")
    task = task.complete(dto=payload)
    task_repo.update_task(task)
    return task


@app.post("/users", response_model=ReadUserDTO, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserDTO,
    user_repo: UserRepository = Depends(YieldRepository(UserRepository)),
):
    user = Users.model_validate(payload)
    user = user_repo.create_user(user)
    return user


@app.get("/users", response_model=list[ReadUserDTO], status_code=status.HTTP_200_OK)
def get_all_user(
    user_repo: UserRepository = Depends(YieldRepository(UserRepository)),
):
    return user_repo.get_all_users()


def start():
    uvicorn.run(
        "applications.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["applications", "domain", "infrastructure"],
    )
