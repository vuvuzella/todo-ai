from sqlmodel import SQLModel


class SQLModelBase(SQLModel):
    class Config: ...
