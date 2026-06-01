from domain.base import DomainBaseModel


class Users(DomainBaseModel):
    id: int
    first_name: str
    last_name: str | None
