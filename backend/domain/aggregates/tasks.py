from typing import Self, TYPE_CHECKING

from pydantic import field_serializer
from sqlmodel import Field, Column, Integer, ForeignKey, Relationship, SQLModel

from domain.base import snowflake_generator, DomainBaseModel
from domain.aggregates.users import Users

if TYPE_CHECKING:
    from .users import Users

## --- Create DTO --- ##
class CreateTaskDTO(DomainBaseModel):
    name: str
    description: str | None = None
    completed: bool = False


## --- Read DTO --- ##
class ReadTaskDTO(DomainBaseModel):
    id: int

    # We serialize the id into a string for the frontend
    # frontend can send this to backend as int/string
    @field_serializer("id")
    def serialize_id(self, v: int) -> str:
        return str(v)

    version: int

    name: str
    description: str | None = None
    completed: bool


## --- Update DTO --- ##
class UpdateTaskDTO(DomainBaseModel):
    version: int

    name: str | None = None
    description: str | None = None
    completed: bool | None = None


## --- Delete DTO --- ##
class DeleteTaskDTO(DomainBaseModel):
    id: int
    version: int


## --- Complete DTO --- ##
class CompleteTaskDTO(DomainBaseModel):
    id: int
    version: int


## --- Domain Model --- ##
class Tasks(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(
        default_factory=snowflake_generator.generate_next_id,
        primary_key=True,
    )

    version: int = Field(default=0)

    name: str
    description: str | None = None
    completed: bool = False

    user_id: int = Field(..., foreign_key="users.id")
    user: Users = Relationship(back_populates="tasks")

    def _check_version(self, version: int) -> bool:
        if self.version != version:
            raise ValueError("Version mismatch")
        return True

    def _increment_version(self) -> Self:
        self.version += 1
        return self

    @classmethod
    def from_create_dto(cls, dto: CreateTaskDTO) -> Self:
        return cls(
            name=dto.name,
            description=dto.description,
            completed=dto.completed,
        )

    def update_from_dto(self, dto: UpdateTaskDTO) -> Self:

        self._check_version(dto.version)

        if dto.name is not None:
            self.name = dto.name
        if dto.description is not None:
            self.description = dto.description
        if dto.completed is not None:
            self.completed = dto.completed

        self._increment_version()
        return self

    def complete(self, dto: CompleteTaskDTO) -> Self:
        self._check_version(dto.version)
        self.completed = True
        self._increment_version()
        return self
