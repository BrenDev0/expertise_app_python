from fastapi import Request
from uuid import UUID
from  typing import List


from src.modules.agents.domain.models import AgentPublic
from src.modules.agents.domain.entities import Agent
from src.modules.users.domain.entities import User
from src.modules.agents.application.agents_service import AgentsService
from src.modules.agents.domain.models import AgentAccessCreate
from src.modules.agents.application.agent_access_service import AgentAccessService
from src.modules.employees.domain.entities import Employee
from src.modules.companies.domain.enitities import Company
from src.core.interface.request_validation_service import RequestValidationService
from src.modules.employees.application.employees_service import EmployeesService

class AgentsController:
    def __init__(
        self, 
        agents_service: AgentsService, 
        agent_access_service: AgentAccessService,
        employees_service: EmployeesService
    ):
        self.__agents_service = agents_service
        self.__agent_access_service = agent_access_service
        self.__employees_service = employees_service

    def add_access(
        self,
        employee_id: UUID,
        req: Request,
        data: AgentAccessCreate
    ) -> List[AgentPublic]:
        company: Company = req.state.company
        
        employee_resource = self.__employees_service.resource(
            key="employee_id",
            value=employee_id
        )

        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

        valid_agents = []
        for agent_id in data.agent_ids:
            agent_resource: Agent = self.__agents_service.resource(key="agent_id", value=agent_id)
            if agent_resource:
                valid_agents.append(agent_resource)

        updated_access = self.__agent_access_service.upsert(
            agent_ids=[agent.agent_id for agent in valid_agents], 
            user_id=employee_resource.user_id
        )
        
        return [
            self.__to_public(access.agent) for access in updated_access
        ]
       

    def agent_acccess_collection_request(
        self,
        employee_id: UUID,
        req: Request
    ):
        company: Company = req.state.company
        
        employee_resource = self.__employees_service.resource(
            key="employee_id",
            value=employee_id
        )

        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

        collection = self.__agent_access_service.collection(user_id=employee_resource.user_id)

        return [self.__to_public(access.agent) for access in collection]
        
    
    def resource_request(
        self,
        agent_id: UUID,
        req: Request
    ) -> AgentPublic:
        agent_resource = self.__agents_service.resource(
            key="agent_id",
            value=agent_id
        )

        RequestValidationService.verify_resource(
            result=agent_resource,
            not_found_message="Agent not found"
        )

        return self.__to_public(data=agent_resource)
    
    def collection_request(
        self,
        req: Request
    ) -> List[AgentPublic]:
        user: User = req.state.user
        company: Company = req.state.company

        if user.is_admin:
            data = self.__agents_service.read()

            return [self.__to_public(agent) for agent in data]

        employee_resource: Employee = self.__employees_service.resource(
            key="user_id",
            value=user.user_id
        )

        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        if employee_resource.is_manager:
            data = self.__agents_service.read()

            return [self.__to_public(agent) for agent in data]

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

        data = self.__agent_access_service.collection(user_id=employee_resource.user_id)

        return [
            self.__to_public(data=agent) for agent in data
        ]
    
    def read_request(
        self
    ):
        data = self.__agents_service.read()

        return [
            self.__to_public(agent) for agent in data
        ]

    @staticmethod
    def __to_public(data: Agent) -> AgentPublic:
        return AgentPublic.model_validate(data, from_attributes=True)