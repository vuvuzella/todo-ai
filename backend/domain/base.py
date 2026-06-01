from pydantic import BaseModel, ConfigDict


class DomainBaseConfigDict(ConfigDict): ...


class DomainBaseModel(BaseModel):
    model_config = DomainBaseConfigDict()
