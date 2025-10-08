import uuid 
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.modules.agents.domain.entities import Agent
from src.core.infrastructure.repositories.data.sqlalchemy.entities import Base
from src.core.infrastructure.repositories.data.sqlalchemy.sqlalchemy_data_repository import SqlAlchemyDataRepository


class SqlAlchemyAgent(Base):
    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    agent_name = Column(String, nullable=False)
    agent_username = Column(String, nullable=False)
    profile_pic = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)



class SqlAlchemyAgentsRepsoitory(SqlAlchemyDataRepository[Agent, SqlAlchemyAgent]):
    def __init__(self):
        super().__init__(SqlAlchemyAgent)
        
    def _to_entity(self, model: SqlAlchemyAgent) -> Agent:
        return Agent(
            agent_id=model.agent_id,
            agent_name=model.agent_name,
            profile_pic=model.profile_pic,
            endpoint=model.endpoint
        )
    
    def _to_model(self, entity: Agent) -> SqlAlchemyAgent:
        data = entity.model_dump(exclude={'agent_id'} if not entity.agent_id else set())
        return SqlAlchemyAgent(**data)