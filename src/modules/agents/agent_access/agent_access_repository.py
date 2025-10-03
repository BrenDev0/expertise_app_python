from src.core.repository.base_repository import BaseRepository
from src.modules.agents.agent_access.agent_access_models import AgentAccess
from src.modules.agents.agents_models import Agent
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from typing import List

class AgentAccessRepository(BaseRepository):
    def __init__(self):
        super().__init__(AgentAccess)

    def upsert_many(
        self, 
        db: Session,
        user_id: UUID,
        agent_ids: List[UUID]
    ) -> List[AgentAccess]:
        if not agent_ids:
            db.query(AgentAccess).filter(AgentAccess.user_id == user_id).delete(synchronize_session=False)
            db.commit()
            return []
        
        current_access = db.query(AgentAccess).filter(AgentAccess.user_id == user_id).all()
        current_agent_ids = {access.agent_id for access in current_access}

        requested_agent_ids = set(agent_ids)

        to_add = requested_agent_ids - current_agent_ids
        to_delete = current_agent_ids - requested_agent_ids

        if to_delete:
            db.query(AgentAccess).filter(
                AgentAccess.user_id == user_id,
                AgentAccess.agent_id.in_(to_delete)
            ).delete(synchronize_session=False)

        if to_add:
            new_access = [
                AgentAccess(agent_id=id, user_id=user_id)
                for id in to_add
            ]
            db.add_all(new_access)

        db.commit()

        return db.query(AgentAccess).filter(AgentAccess.user_id == user_id).all()

    
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

    def get_agents_by_user(self, db: Session, user_id: UUID) -> List[AgentAccess]:
        stmt = (
            select(AgentAccess).where(AgentAccess.user_id == user_id)
        )
        return db.execute(stmt).scalars().all()
