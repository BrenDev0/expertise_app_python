from src.core.repository.base_repository import BaseRepository
from src.modules.agents.agent_access.agent_access_models import AgentAccess
from src.modules.agents.agents_models import Agent
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from typing import List

class AgentAcessRepository(BaseRepository):
    def __init__(self):
        super().__init__(AgentAccess)

    def create_many(self, db: Session, user_id: UUID, agent_ids: List[UUID]):
        existing = db.query(AgentAccess.agent_id).filter(
            AgentAccess.user_id == user_id,
            AgentAccess.agent_id.in_(agent_ids)
        ).all()
        existing_ids = {row[0] for row in existing}

    
        new_agent_ids = [aid for aid in agent_ids if aid not in existing_ids]

        new_links = [
            AgentAccess(agent_id=aid, user_id=user_id)
            for aid in new_agent_ids
        ]
        db.add_all(new_links)
        db.commit()
        return new_links
    
    def get_access_resource(self, db: Session, user_id: UUID, agent_id: UUID) -> AgentAccess | None:
        stmt = select(self.model).where(
            (self.model.user_id == user_id) &
            (self.model.agent_id == agent_id)
        )
        return db.execute(stmt).scalar_one_or_none()

    def delete_by_user_and_agents(self, db: Session, user_id: UUID, agent_ids: List[UUID]):
        db.query(AgentAccess).filter(
            AgentAccess.user_id == user_id,
            AgentAccess.agent_id.in_(agent_ids)
        ).delete(synchronize_session=False)
        db.commit()

    def get_agents_by_user(self, db: Session, user_id: UUID) -> List[Agent]:
        stmt = (
            select(Agent)
            .join(AgentAccess, Agent.agent_id == AgentAccess.agent_id)
            .where(AgentAccess.user_id == user_id)
        )
        return db.execute(stmt).scalars().all()