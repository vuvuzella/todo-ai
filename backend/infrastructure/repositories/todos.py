from domain.aggregates.todos import Todos
from domain.aggregates.users import UsersWithTodos
from backend.infrastructure.databases.base import BaseRepository

class TodoRepository(BaseRepository):
    def get_by_user_id(self, user_id: int) -> List[Todos]:
        # Implement logic to fetch todos by user_id
        pass

    def add(self, todo: Todos) -> None:
        # Implement logic to add a new todo
        pass

    def update(self, todo: Todos) -> None:
        # Implement logic to update an existing todo
        pass

    def delete(self, todo_id: int) -> None:
        # Implement logic to delete a todo
        pass

    def get_todos_by_user_id(self, user_id: int) -> List[Todos]:
        # Implement logic to fetch todos by user_id
        pass