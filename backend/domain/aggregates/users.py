from typing import TYPE_CHECKING

from sqlmodel import BigInteger, Field, Relationship

from domain.aggregates.base import SQLModelBase
from domain.base import DomainBaseModel, generate_js_safe_sf_id

if TYPE_CHECKING:
    from domain.aggregates.tasks import Tasks


## --- DTO Models --- ##
class ReadUserDTO(DomainBaseModel):
    id: int
    version: int
    username: str

    tasks: list["Tasks"]


class CreateUserDTO(DomainBaseModel):
    username: str


## --- Domain Model --- ##


class Users(SQLModelBase, table=True):
    __tablename__ = "users"
    id: int = Field(
        default_factory=generate_js_safe_sf_id,
        sa_type=BigInteger,
        primary_key=True,
        sa_column_kwargs={"autoincrement": False},
    )

    version: int = Field(default=0)
    username: str
    auth0_id: str | None = None
    tasks: list["Tasks"] = Relationship(back_populates="user")
