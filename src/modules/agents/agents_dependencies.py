from src.core.dependencies.container import Container
from src.modules.agents.agents_service import AgentsService
from src.modules.agents.agents_controller import AgentsController
from src.modules.agents.employee_agents.employee_agents_repository import EmployeeAgentRepository
from src.core.repository.base_repository import BaseRepository
from src.modules.agents.employee_agents.employee_agents_service import EmployeeAgentService
from src.core.services.http_service import HttpService
from src.modules.agents.agents_models import Agent

def configure_agents_dependencies(http_service: HttpService):
    base_repo = BaseRepository(Agent)
    e_a_repo = EmployeeAgentRepository()
    agents_service = AgentsService(
        respository=base_repo
    )
    e_a_service = EmployeeAgentService(
        repository=e_a_repo
    )

    controller = AgentsController(
        http_service=http_service,
        agents_service=agents_service,
        employee_agents_service=e_a_service
    )

    Container.register("agents_service", agents_service)
    Container.register("agents_controller", controller)