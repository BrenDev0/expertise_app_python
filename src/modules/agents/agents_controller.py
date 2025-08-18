from src.core.services.http_service import HttpService
from src.modules.agents.agents_models import Agent, AgentPublic
from src.modules.users.users_models import User
from src.modules.agents.agents_service import AgentsService
from src.modules.agents.employee_agents.employee_agent_models import EmployeeAgentCreate
from src.modules.agents.employee_agents.employee_agents_service import EmployeeAgentService
from src.modules.employees.employees_models import Employee
from src.modules.users.users_models import User
from src.core.models.http_responses import CommonHttpResponse
from fastapi import Request
from sqlalchemy.orm import Session
from uuid import UUID

class AgentsController:
    def __init__(self, http_service: HttpService, agents_service: AgentsService, employee_agents_service: EmployeeAgentService):
        self.__http_service = http_service
        self.__agents_service = agents_service
        self.__employee_agents_service = employee_agents_service

    def add_access(
        self,
        employee_id: UUID,
        data: EmployeeAgentCreate,
        req: Request,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user
        
        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "employee_id": employee_id
            },
            not_found_message="Employee not found"
        )

        self.__http_service.request_validation_service.verify_company_user_relation(db=db, user=user, company_id=employee_resource.company_id)

        self.__employee_agents_service.create_many(db=db, data=EmployeeAgentCreate)

        return CommonHttpResponse(
            detail="Agent access added to employee"
        )
    
    def resource_request(
        self,
        agent_id: UUID,
        req: Request,
        db: Session
    ) -> AgentPublic:
        agent_resource = self.__http_service.request_validation_service.verify_resource(
            service_key="agents_service",
            params={
                "db": db,
                "agent_id": agent_id
            },
            not_found_message="Agent not found"
        )

        return self.__to_public(data=agent_resource)
    
    def collection_request(
        self,
        employee_id: UUID,
        req: Request,
        db: Session
    ):
        user = req.state.user

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employee_service",
            params={
                "db": db,
                "employee_id": employee_id
            },
            not_found_message="Employee not found"
        )

        data = self.__employee_agents_service.collection(db=db, employee_id=employee_resource.employee_id)

        return [
            self.__to_public(data=agent) for agent in data
        ]
    
    def read_request(
        self,
        db: Session
    ):
        data = self.__agents_service.read(db=db)

        return [
            self.__to_public(agent) for agent in data
        ]

    @staticmethod
    def __to_public(data: Agent) -> AgentPublic:
        return AgentPublic.model_validate(data, from_attributes=True)