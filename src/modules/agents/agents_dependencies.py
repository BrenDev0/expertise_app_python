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
        http_service=http_service,
        agents_service=agents_service,
        agent_access_service=a_a_service
    )

    Container.register("agents_service", agents_service)
    Container.register("agents_controller", controller)
    Container.register("agent_access_service", a_a_service)