from .tasks import CompleteTaskDTO, CreateTaskDTO, ReadTaskDTO, Tasks, UpdateTaskDTO
from .users import CreateUserDTO, ReadUserDTO, Users

Users.model_rebuild()
Tasks.model_rebuild()
ReadUserDTO.model_rebuild()
