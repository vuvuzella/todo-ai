import uvicorn
from domain.aggregates.tasks import (
    CompleteTaskDTO,
    CreateTaskDTO,
    ReadTaskDTO,
    Tasks,
    UpdateTaskDTO,
)
from fastapi import Depends, FastAPI, status
from infrastructure.repositories.base import YieldRepository
from infrastructure.repositories.tasks import TaskRepository

app = FastAPI()


@app.get("/tasks", response_model=list[ReadTaskDTO], status_code=status.HTTP_200_OK)
def get_tasts(
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


def start():
    uvicorn.run(app=app, host="0.0.0.0", port=8000, reload=True)
