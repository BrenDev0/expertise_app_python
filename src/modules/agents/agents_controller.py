from src.core.services.http_service import HttpService
from src.modules.agents.agents_models import Agent, AgentPublic
from src.modules.users.users_models import User
from src.modules.agents.agents_service import AgentsService
from src.modules.agents.agent_access.agent_access_models import AgentAccessCreate, AgentAccessDelete
from src.modules.agents.agent_access.agent_access_service import AgentAccessService
from src.modules.employees.employees_models import Employee
from src.core.models.http_responses import CommonHttpResponse
from fastapi import Request
from sqlalchemy.orm import Session
from uuid import UUID
from  typing import List


class AgentsController:
    def __init__(self, http_service: HttpService, agents_service: AgentsService, agent_access_service: AgentAccessService):
        self.__http_service = http_service
        self.__agents_service = agents_service
        self.__agent_access_service = agent_access_service

    def add_access(
        self,
        employee_id: UUID,
        data: AgentAccessCreate,
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

        self.__agent_access_service.create_many(db=db, data=data, user_id=employee_resource.user_id)

        return CommonHttpResponse(
            detail="Agent access added to employee"
        )
    
    def remove_access(
        self,
        employee_id: UUID,
        data: AgentAccessDelete,
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

        self.__agent_access_service.remove_many(db=db, data=data, user_id=employee_resource.user_id)

        return CommonHttpResponse(
            detail="Agent access removed from employee"
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
    ) -> List[AgentPublic]:
        user = req.state.user

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "employee_id": employee_id
            },
            not_found_message="Employee not found"
        )

        data = self.__agent_access_service.collection(db=db, user_id=employee_resource.user_id)

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