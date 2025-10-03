from src.modules.agents.agent_access.agent_access_repository import AgentAccessRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.modules.agents.agent_access.agent_access_models import AgentAccess, AgentAccessCreate, AgentAccessDelete
from sqlalchemy.orm import Session
from  src.modules.agents.agents_models import Agent
from typing import List
from uuid import UUID

class AgentAccessService:
    __MODULE = "agent_access.service"
    def __init__(self, repository: AgentAccessRepository):
        self.__repository = repository

    @service_error_handler(f"{__MODULE}.create_many")
    def upsert(self, db: Session, agent_ids: List[UUID], user_id: UUID) -> List[AgentAccess]:
        return self.__repository.upsert_many(db=db, user_id=user_id, agent_ids=agent_ids)
    
    @service_error_handler(f"{__MODULE}.resource")
    def resource(self, db: Session, user_id: UUID, agent_id: UUID) -> AgentAccess | None:
        return self.__repository.get_access_resource(db=db, user_id=user_id, agent_id=agent_id)

    @service_error_handler(f"{__MODULE}.collection")
    def collection(self, db: Session, user_id: UUID) -> List[AgentAccess]:
        return self.__repository.get_agents_by_user(db=db, user_id=user_id)

    @service_error_handler(f"{__MODULE}.remove_many")
    def remove_many(self, db: Session, data: AgentAccessDelete, user_id: UUID):
        self.__repository.delete_by_user_and_agents(db=db, user_id=user_id, agent_ids=data.agent_ids)
