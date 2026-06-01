from typing import Self

from sqlmodel import Field, SQLModel

from domain.base import snowflake_generator


## --- Create DTO --- ##
class CreateTaskDTO(SQLModel):
    name: str
    description: str | None = None
    completed: bool = False


## --- Read DTO --- ##
class ReadTaskDTO(SQLModel):
    id: int
    version: int

    name: str
    description: str | None = None
    completed: bool


## --- Update DTO --- ##
class UpdateTaskDTO(SQLModel):
    version: int

    name: str | None = None
    description: str | None = None
    completed: bool | None = None


## --- Delete DTO --- ##
class DeleteTaskDTO(SQLModel):
    id: int
    version: int


## --- Complete DTO --- ##
class CompleteTaskDTO(SQLModel):
    id: int
    version: int


## --- Domain Model --- ##
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(
        default_factory=snowflake_generator.generate_next_id, primary_key=True
    )
    version: int = Field(default=0)

    name: str
    description: str | None = None
    completed: bool = False

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
