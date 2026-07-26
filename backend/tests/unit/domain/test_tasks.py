from typing import Callable

import pytest

from domain.aggregates import Users
from domain.aggregates import CompleteTaskDTO, Tasks, UpdateTaskDTO


@pytest.fixture
def task_factory():
    def _create_task():
        user = Users(username="testy")
        return Tasks(
            user_id=user.id,
            user=user,
            name="Test Task",
            description="This is a test task.")

    return _create_task


def test_create_task(task_factory: Callable[[], Tasks]):
    task_1 = task_factory()
    task_2 = task_factory()
    assert task_1.id is not None
    assert task_1.name == "Test Task"
    assert task_1.description == "This is a test task."
    assert not task_1.completed

    assert task_1.id != task_2.id  # Ensure unique IDs are generated for each task


def test_update_task(task_factory: Callable[[], Tasks]):
    task = task_factory()
    original_version = task.version

    update_dto = UpdateTaskDTO(
        version=original_version,
        name="Updated Task",
        description="This is an updated test task.",
        completed=True,
    )

    updated_task = task.update_from_dto(update_dto)

    assert updated_task.name == "Updated Task"
    assert updated_task.description == "This is an updated test task."
    assert updated_task.completed
    assert updated_task.version == original_version + 1


def test_complete_task(task_factory: Callable[[], Tasks]):
    task = task_factory()
    original_version = task.version

    complete_dto = CompleteTaskDTO(id=task.id, version=original_version)

    completed_task = task.complete(complete_dto)

    assert completed_task.completed
    assert completed_task.version == original_version + 1
