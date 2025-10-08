from typing import List
from uuid import UUID

from src.modules.agents.domain.agent_access_repository import AgentAccessRepository
from src.modules.agents.domain.entities import AgentAccess

from src.core.utils.decorators.service_error_handler import service_error_handler



class AgentAccessService:
    __MODULE = "agent_access.service"
    def __init__(self, repository: AgentAccessRepository):
        self.__repository = repository

    @service_error_handler(f"{__MODULE}.create_many")
    def upsert(self, agent_ids: List[UUID], user_id: UUID) -> List[AgentAccess]:
        return self.__repository.upsert_many(user_id=user_id, agent_ids=agent_ids)
    
    @service_error_handler(f"{__MODULE}.resource")
    def resource(self, user_id: UUID, agent_id: UUID) -> AgentAccess | None:
        return self.__repository.get_access_resource(user_id=user_id, agent_id=agent_id)

    @service_error_handler(f"{__MODULE}.collection")
    def collection(self, user_id: UUID) -> List[AgentAccess]:
        return self.__repository.get_agents_by_user(user_id=user_id)

    