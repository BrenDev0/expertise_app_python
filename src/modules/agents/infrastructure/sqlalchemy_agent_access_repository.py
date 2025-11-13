from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
import uuid 
from typing import List, Optional

from src.modules.agents.domain.entities import AgentAccess, Agent
from src.modules.agents.domain.agent_access_repository import AgentAccessRepository

from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base


class SqlAlchemyAgentAccess(Base):
    __tablename__ = "agent_access"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)

    agent = relationship("SqlAlchemyAgent")

    __table_args__ = (
        UniqueConstraint("agent_id", "user_id", name="uq_agent_user"),
    )


class SqlAlchemyAgentAccessRepository(SqlAlchemyDataRepository[AgentAccess, SqlAlchemyAgentAccess], AgentAccessRepository):
    def __init__(self):
        super().__init__(SqlAlchemyAgentAccess)

    def _to_entity(self, model: SqlAlchemyAgentAccess) -> AgentAccess:
        return AgentAccess(
           user_id=model.user_id,
           agent_id=model.agent_id,
           agent=self._agent_to_entity(model.agent) if model.agent else None
        )
    
    def _agent_to_entity(self, agent_model) -> Optional[Agent]:
        if not agent_model:
            return None
        return Agent(
            agent_id=agent_model.agent_id,
            agent_name=agent_model.agent_name,
            agent_username=agent_model.agent_username,
            description=getattr(agent_model, 'description', None),
            profile_pic=agent_model.profile_pic
        )
    
    def _to_model(self, entity: AgentAccess) -> SqlAlchemyAgentAccess:
        data = entity.model_dump(exclude={'agent'})
        return SqlAlchemyAgentAccess(**data)

    def upsert_many(
        self,
        user_id: UUID,
        agent_ids: List[UUID]
    ) -> List[AgentAccess]:
        with self._get_session() as db:
            if not agent_ids:
                db.query(SqlAlchemyAgentAccess).filter(SqlAlchemyAgentAccess.user_id == user_id).delete(synchronize_session=False)
                db.commit()
                return []
            
            current_access = db.query(SqlAlchemyAgentAccess).filter(SqlAlchemyAgentAccess.user_id == user_id).all()
            current_agent_ids = {access.agent_id for access in current_access}

            requested_agent_ids = set(agent_ids)

            to_add = requested_agent_ids - current_agent_ids
            to_delete = current_agent_ids - requested_agent_ids

            if to_delete:
                db.query(SqlAlchemyAgentAccess).filter(
                    SqlAlchemyAgentAccess.user_id == user_id,
                    SqlAlchemyAgentAccess.agent_id.in_(to_delete)
                ).delete(synchronize_session=False)

            if to_add:
                new_access = [
                    SqlAlchemyAgentAccess(agent_id=id, user_id=user_id)
                    for id in to_add
                ]
                db.add_all(new_access)

            db.commit()

            updated_access = db.query(SqlAlchemyAgentAccess).filter(SqlAlchemyAgentAccess.user_id == user_id).all()
            return [self._to_entity(access) for access in updated_access]    

    
    def get_access_resource(self, user_id: UUID, agent_id: UUID) -> AgentAccess | None:
        stmt = select(SqlAlchemyAgentAccess).where(
            (SqlAlchemyAgentAccess.user_id == user_id) &
            (SqlAlchemyAgentAccess.agent_id == agent_id)
        )

        with self._get_session() as db:
            result = db.execute(stmt).scalar_one_or_none()
            return self._to_entity(result) if result else None

    def delete_by_user_and_agents(self, user_id: UUID, agent_ids: List[UUID]):
        with self._get_session() as db:
            db.query(SqlAlchemyAgentAccess).filter(
                SqlAlchemyAgentAccess.user_id == user_id,
                SqlAlchemyAgentAccess.agent_id.in_(agent_ids)
            ).delete(synchronize_session=False)
            db.commit()

    def get_agents_by_user(self, user_id: UUID) -> List[AgentAccess]:
        stmt = (
            select(SqlAlchemyAgentAccess).where(SqlAlchemyAgentAccess.user_id == user_id)
        )

        with self._get_session() as db:
            result = db.execute(stmt).scalars().all()
            return [self._to_entity(access) for access in result]
