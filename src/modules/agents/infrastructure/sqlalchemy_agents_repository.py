import uuid 
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.modules.agents.domain.entities import Agent

from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base


class SqlAlchemyAgent(Base):
    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    agent_name = Column(String, nullable=False)
    agent_username = Column(String, nullable=False)
    description = Column(String, nullable=True)
    profile_pic = Column(String, nullable=True)



class SqlAlchemyAgentsRepsoitory(SqlAlchemyDataRepository[Agent, SqlAlchemyAgent]):
    def __init__(self):
        super().__init__(SqlAlchemyAgent)
        
    def _to_entity(self, model: SqlAlchemyAgent) -> Agent:
        return Agent(
            agent_id=model.agent_id,
            agent_name=model.agent_name,
            agent_username=model.agent_username,
            description=model.description,
            profile_pic=model.profile_pic
        )
    
    def _to_model(self, entity: Agent) -> SqlAlchemyAgent:
        data = entity.model_dump(exclude={'agent_id'} if not entity.agent_id else set())
        return SqlAlchemyAgent(**data)