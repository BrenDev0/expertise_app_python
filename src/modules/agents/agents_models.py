from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, Boolean, DateTime, func, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime

class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    agent_name = Column(String, nullable=False)
    agent_username = Column(String, nullable=False)
    profile_pic = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)


class AgentConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class AgentPublic(AgentConfig):
    agent_id: uuid.UUID
    agent_name: str
    agent_username: str
    profile_pic: str
    endpoint: str