from __future__ import annotations
from typing import TYPE_CHECKING
from domain.base import DomainBaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from domain.aggregates.todos import Todos
    from domain.aggregates.tasks import Tasks

class UsersWithTodos(DomainBaseModel):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, unique=True)
    todos: list['Todos'] = relationship('Todos', back_populates='user')

class UsersWithTasks(DomainBaseModel):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String, unique=True)
    tasks: list['Tasks'] = relationship('Task')