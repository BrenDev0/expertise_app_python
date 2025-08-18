from src.core.repository.base_repository import BaseRepository
from src.modules.agents.employee_agents.employee_agent_models import EmployeeAgent
from src.modules.agents.agents_models import Agent
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from typing import List

class EmployeeAgentRepository(BaseRepository):
    def __init__(self):
        super().__init__(EmployeeAgent)

    def delete_by_employee_and_agents(self, db: Session, employee_id: UUID, agent_ids: List[UUID]):
       
        db.query(EmployeeAgent).filter(
            EmployeeAgent.employee_id == employee_id,
            EmployeeAgent.agent_id.in_(agent_ids)
        ).delete(synchronize_session=False)
        db.commit()

    def get_agents_by_employee(self, db: Session, employee_id: UUID) -> List[Agent]:
        stmt = (
            select(Agent)
            .join(EmployeeAgent, Agent.agent_id == EmployeeAgent.agent_id)
            .where(EmployeeAgent.employee_id == employee_id)
        )
        return db.execute(stmt).scalars().all()