from typing import List
from uuid import UUID

from src.core.domain.repositories.data_repository import DataRepository
from src.modules.agents.domain.entities import Agent
from src.core.utils.decorators.service_error_handler import service_error_handler


class AgentsService:
    __MODULE = "agents.service"
    def __init__(self, respository: DataRepository):
        self.__repository = respository

    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, key: str, value: UUID | str) -> Agent | None:
        return self.__repository.get_one(
            key=key,
            value=value
        )
    
    @service_error_handler(f"{__MODULE}.read")
    def read(self, ) -> List[Agent]:
        return self.__repository.get_all()