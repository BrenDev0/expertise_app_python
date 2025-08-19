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

    def create_many(self, db: Session, employee_id: UUID, agent_ids: List[UUID]):
        existing = db.query(EmployeeAgent.agent_id).filter(
            EmployeeAgent.employee_id == employee_id,
            EmployeeAgent.agent_id.in_(agent_ids)
        ).all()
        existing_ids = {row[0] for row in existing}

    
        new_agent_ids = [aid for aid in agent_ids if aid not in existing_ids]

        new_links = [
            EmployeeAgent(agent_id=aid, employee_id=employee_id)
            for aid in new_agent_ids
        ]
        db.add_all(new_links)
        db.commit()
        return new_links

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