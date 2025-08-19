from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, Boolean, DateTime, func, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime


class AgentAccess(Base):
    __tablename__ = "agent_access"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("agent_id", "user_id", name="uq_agent_user"),
    )

class AgentAccessConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )

class AgentAccessCreate(AgentAccessConfig):
    agent_ids: List[uuid.UUID]

class AgentAccessDelete(AgentAccessCreate):
    pass