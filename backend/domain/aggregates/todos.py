from domain.base import DomainBaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import field_serializer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import UsersWithTodos

class Todos(DomainBaseModel):
    __tablename__ = 'todos'
    id: int = Column(Integer, primary_key=True)
    description: str = Column(String)
    completed: bool = Column(Boolean)
    user_id: int = Column(Integer, ForeignKey('users.id'))
    user: 'UsersWithTodos' = relationship('UsersWithTodos', back_populates='todos')

    def complete(self):
        self.completed = True

## --- Create DTO --- ##
class CreateTodoDTO(DomainBaseModel):
    description: str
    completed: bool = False

## --- Read DTO --- ##
class ReadTodoDTO(DomainBaseModel):
    id: int

    # We serialize the id into a string for the frontend
    # frontend can send this to backend as int/string
    @field_serializer("id")
    def serialize_id(self, v: int) -> str:
        return str(v)

    version: int

    description: str
    completed: bool

## --- Update DTO --- ##
class UpdateTodoDTO(DomainBaseModel):
    version: int

    description: str | None = None
    completed: bool | None = None

## --- Delete DTO --- ##
class DeleteTodoDTO(DomainBaseModel):
    id: int
    version: int

## --- Complete DTO --- ##
class CompleteTodoDTO(DomainBaseModel):
    id: int
    version: int