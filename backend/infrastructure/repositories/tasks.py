from sqlalchemy import Delete
from sqlmodel import select

from domain.aggregates.tasks import Tasks
from infrastructure.repositories.base import Repository


class TaskRepository(Repository):
    def get_all_tasks(self) -> list[Tasks]:
        tasks = self.session.exec(select(Tasks)).all()
        return list(tasks)

    def get_task_by_id(
        self, task_id: int, raise_not_found: bool = True
    ) -> Tasks | None:
        # Code to retrieve a specific task by its ID from the database
        task = self.session.exec(select(Tasks).where(Tasks.id == task_id)).first()
        if task is None and raise_not_found:
            raise Exception(f"Task id {task_id} not found")
        return task

    def create_task(self, new_task: Tasks) -> Tasks:
        result = self.session.scalar(select(Tasks.id).where(Tasks.id == new_task.id))
        if result is not None:
            raise Exception(f"Task id {new_task.id} already exists")

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)
        return new_task

    def update_task(self, task: Tasks) -> Tasks:
        result = self.session.scalar(select(Tasks.id).where(Tasks.id == task.id))
        if result is None:
            raise Exception(f"Task id {task.id} not found")

        self.session.merge(task)
        self.session.commit()
        return task

    def delete_task(self, task_id: int):
        # Code to delete a task from the database
        self.session.exec(Delete(Tasks).where(Tasks.id == task_id))  # ty:ignore[invalid-argument-type]:wa
        self.session.commit()
