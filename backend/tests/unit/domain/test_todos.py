from typing import Callable

import pytest

from domain.aggregates.todos import Todos


@pytest.fixture
def todo_factory():
    def _create_todo():
        return Todos(id=1, description="Buy groceries", completed=False, user_id=1)

    return _create_todo


def test_todo_creation(todo_factory: Callable[[], Todos]):
    todo = todo_factory()
    assert todo.id == 1
    assert todo.description == "Buy groceries"
    assert todo.completed == False


def test_todo_with_user_id(todo_factory: Callable[[], Todos]):
    todo = todo_factory()
    assert todo.user_id == 1


def test_complete(todo_factory: Callable[[], Todos]):
    todo = todo_factory()
    assert not todo.completed  # Initially, completed should be False
    todo.complete()
    assert todo.completed  # After calling complete, completed should be True
