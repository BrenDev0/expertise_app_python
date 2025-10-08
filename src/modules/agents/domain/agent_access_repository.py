from  abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.core.domain.repositories.data_repository import DataRepository
from src.modules.agents.domain.entities import AgentAccess, Agent


class AgentAccessRepository(DataRepository[AgentAccess]):
    @abstractmethod
    def upsert_many(
        self, 
        user_id: UUID,
        agent_ids: List[UUID]
    ) -> List[AgentAccess]:
        raise NotImplementedError

    
    @abstractmethod
    def get_access_resource(self, user_id: UUID, agent_id: UUID) -> AgentAccess | None:
        raise NotImplementedError
    
    @abstractmethod
    def delete_by_user_and_agents(self, user_id: UUID, agent_ids: List[UUID]):
        raise NotImplementedError

    @abstractmethod
    def get_agents_by_user(self, user_id: UUID) -> List[AgentAccess]:
        raise NotImplementedError
    
    @abstractmethod
    def _agent_to_entity(self, agent_model) -> Optional[Agent]:
        raise NotImplementedError
