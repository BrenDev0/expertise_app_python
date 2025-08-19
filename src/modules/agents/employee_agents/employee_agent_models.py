from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, Boolean, DateTime, func, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime


class EmployeeAgent(Base):
    __tablename__ = "employee_agents"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.employee_id", ondelete="CASCADE"), primary_key=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("agent_id", "employee_id", name="uq_agent_employee"),
    )

class EmployeeAgentConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )

class EmployeeAgentCreate(EmployeeAgentConfig):
    agent_ids: List[uuid.UUID]

class EmployeeAgentDelete(EmployeeAgentCreate):
    pass