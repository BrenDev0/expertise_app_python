from fastapi import Depends

from src.core.dependencies.container import Container
from src.modules.agents.agents_service import AgentsService
from src.modules.agents.agents_controller import AgentsController
from src.modules.agents.agent_access.agent_access_repository import AgentAccessRepository
from src.core.repository.base_repository import BaseRepository
from src.modules.agents.agent_access.agent_access_service import AgentAccessService
from src.core.services.http_service import HttpService
from src.modules.agents.agents_models import Agent

def configure_agents_dependencies(http_service: HttpService):
    base_repo = BaseRepository(Agent)
    a_a_repo = AgentAccessRepository()
    agents_service = AgentsService(
        respository=base_repo
    )
    a_a_service = AgentAccessService(
        repository=a_a_repo
    )

    controller = AgentsController(
        agents_service=agents_service,
        agent_access_service=a_a_service
    )

    Container.register("agents_service", agents_service)
    Container.register("agents_controller", controller)
    Container.register("agent_access_service", a_a_service)

def get_agents_repository() -> BaseRepository:
    return BaseRepository(Agent)

def get_access_repository() -> AgentAccessRepository:
    return AgentAccessRepository()

def get_agents_service(
    repository: BaseRepository = Depends(get_agents_repository)
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