from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from  typing import List

from src.core.models.http_responses import CommonHttpResponse
from src.core.services.http_service import HttpService
from src.modules.agents.agents_models import Agent, AgentPublic
from src.modules.users.users_models import User
from src.modules.agents.agents_service import AgentsService
from src.modules.agents.agent_access.agent_access_models import AgentAccessCreate, AgentAccessDelete, AgentAccess
from src.modules.agents.agent_access.agent_access_service import AgentAccessService
from src.modules.employees.employees_models import Employee




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
    ) -> List[AgentPublic]:
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)
        
        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "key": "employee_id",
                "value": employee_id
            },
            not_found_message="Employee not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

        valid_agents = []
        for agent_id in data.agent_ids:
            agent_resource: Agent = self.__agents_service.resource(db=db, agent_id=agent_id)
            if agent_resource:
                valid_agents.append(agent_resource)
        
        if len(valid_agents) == 0:
            raise HTTPException(status_code=400, detail="No valid agents in request")

        updated_access = self.__agent_access_service.upsert(
            db=db, 
            agent_ids=[agent.agent_id for agent in valid_agents], 
            user_id=employee_resource.user_id
        )
        
        return [
            self.__to_public(access.agent) for access in updated_access
        ]
       

    def agent_acccess_collection_request(
        self,
        employee_id: UUID,
        req: Request,
        db: Session
    ):
        company_id= self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)
        
        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "key": "employee_id",
                "value": employee_id
            },
            not_found_message="Employee not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

        collection = self.__agent_access_service.collection(db=db, user_id=employee_resource.user_id)

        return [self.__to_public(agent) for agent in collection]
        
    
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
        req: Request,
        db: Session
    ) -> List[AgentPublic]:
        user: User = req.state.user
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req, db=db)

        if user.is_admin:
            data = self.__agents_service.read(db=db)

            return [self.__to_public(agent) for agent in data]

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "key": "user_id", 
                "value": user.user_id
            },
            not_found_message="Employee not found"
        )

        if employee_resource.is_manager:
            data = self.__agents_service.read(db=db)

            return [self.__to_public(agent) for agent in data]

        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

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