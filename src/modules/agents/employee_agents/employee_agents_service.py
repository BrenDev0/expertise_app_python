from src.modules.agents.employee_agents.employee_agents_repository import EmployeeAgentRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.modules.agents.employee_agents.employee_agent_models import EmployeeAgent, EmployeeAgentCreate, EmployeeAgentDelete
from sqlalchemy.orm import Session
from  src.modules.agents.agents_models import Agent
from typing import List
from uuid import UUID

class EmployeeAgentService:
    __MODULE = "employee_agents.service"
    def __init__(self, repository: EmployeeAgentRepository):
        self.__repository = repository

    @service_error_handler(f"{__MODULE}.create_many")
    def create_many(self, db: Session, data: EmployeeAgentCreate, employee_id: UUID) -> List[EmployeeAgent]:
        return self.__repository.create_many(db=db, employee_id=employee_id, agent_ids=data.agent_ids)
    
    @service_error_handler(f"{__MODULE}.collection")
    def collection(self, db: Session, employee_id: UUID) -> List[Agent]:
        return self.__repository.get_agents_by_employee(db=db, employee_id=employee_id)

    @service_error_handler(f"{__MODULE}.remove_many")
    def remove_many(self, db: Session, data: EmployeeAgentDelete, employee_id: UUID):
        self.__repository.delete_by_employee_and_agents(db, employee_id, data.agent_ids)
