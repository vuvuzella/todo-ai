from backend.domain.base import snowflake_generator
from sqlmodel import Relationship, Field, SQLModel
from typing import TYPE_CHECKING
from domain.base import DomainBaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    # from domain.aggregates.todos import Todos
    from domain.aggregates.tasks import Tasks
class Users(SQLModel, table=True):
    __tablename__ = 'users'
    id: int = Field(
        default_factory=snowflake_generator.generate_next_id,
        primary_key=True)
    username: str
    tasks: list['Tasks'] = Relationship(back_populates="user")