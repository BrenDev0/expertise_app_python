from fastapi import Depends

from src.modules.agents.application.agents_service import AgentsService
from src.modules.agents.interface.agents_controller import AgentsController
from src.core.domain.repositories.data_repository import DataRepository

from src.modules.agents.application.agent_access_service import AgentAccessService

from src.modules.agents.infrastructure.sqlalchemy_agents_repository import SqlAlchemyAgentsRepsoitory
from src.modules.agents.infrastructure.sqlalchemy_agent_access_repository import SqlAlchemyAgentAccessRepository

from src.modules.agents.domain.agent_access_repository import AgentAccessRepository
from src.modules.agents.domain.entities import Agent



def get_agents_repository() -> DataRepository:
    return SqlAlchemyAgentsRepsoitory(Agent)

def get_access_repository() -> AgentAccessRepository:
    return SqlAlchemyAgentAccessRepository()

def get_agents_service(
    repository: DataRepository = Depends(get_agents_repository)
) -> AgentsService:
    return AgentsService(
        respository=repository
    )

def get_access_service(
    repository: AgentAccessRepository = Depends(get_access_repository)
) -> AgentAccessService:
    return AgentAccessService(
        repository=repository
    )

def get_agents_controller(
    service: AgentsService =Depends(get_agents_service),
    access_service: AgentAccessService = Depends(get_access_service)
) -> AgentsController:
    return AgentsController(
        agents_service=service,
        agent_access_service=access_service
    )