import random

import pytest
from sqlmodel import Session, delete, insert, select

from domain.tasks import Task
from infrastructure.repositories.tasks import TaskRepository


@pytest.fixture(scope="function")
def new_task():
    return Task(
        id=random.randint(1, 1000), name="New Task", description="New Description"
    )


@pytest.fixture(scope="function")
def add_tasks(session: Session, new_task: Task):
    try:
        session.exec(
            insert(Task).values(
                id=new_task.id, name=new_task.name, description=new_task.description
            )
        )
        session.commit()
        yield new_task
    except Exception as e:
        ...
    finally:
        session.exec(delete(Task).where(Task.id == new_task.id))  # ty:ignore[invalid-argument-type]
        session.commit()


@pytest.fixture(scope="function")
def remove_new_task(session: Session, new_task: Task):
    yield
    session.exec(delete(Task).where(Task.id == new_task.id))  # ty:ignore[invalid-argument-type]
    session.commit()


def test_get_tasks(session: Session):
    repo = TaskRepository(session)
    tasks = repo.get_all_tasks()
    assert isinstance(tasks, list)


def test_get_task_by_id(add_tasks, session: Session):
    repo = TaskRepository(session)
    task = repo.get_task_by_id(add_tasks.id)
    assert task is not None
    assert task.id == add_tasks.id


def test_create_task(session: Session, new_task: Task, remove_new_task):
    repo = TaskRepository(session)
    repo.create_task(new_task)
    created_task = session.exec(select(Task).where(Task.name == new_task.name)).first()
    assert created_task is not None
    assert created_task.id == new_task.id
    assert created_task.name == new_task.name


def test_update_task(session: Session, add_tasks: Task):
    repo = TaskRepository(session)
    add_tasks.name = "This is a new name"
    add_tasks.description = "This is a new description"
    add_tasks = repo.update_task(add_tasks)

    updated_task = session.exec(select(Task).where(Task.id == add_tasks.id)).first()

    assert updated_task is not None
    assert updated_task.id == add_tasks.id
    assert updated_task.name == add_tasks.name
    assert updated_task.description == add_tasks.description

    new_task = Task(id=updated_task.id, name="nonlive", description="New Description")
    new_task = repo.update_task(new_task)
    assert new_task.id == updated_task.id


def test_delete_task(session: Session, add_tasks: Task):
    repo = TaskRepository(session)
    repo.delete_task(add_tasks.id)

    deleted_task = session.exec(select(Task).where(Task.id == add_tasks.id)).first()
    assert deleted_task is None
