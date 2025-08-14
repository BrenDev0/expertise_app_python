from src.core.database.database_models import Base
from  sqlalchemy import String, Column, ForeignKey, UUID, UniqueConstraint
import uuid
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id =  Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="Cascade"), nullable=False)
    company_id =  Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="Cascade"), nullable=False)
    position = Column(String, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
    )

class EmployeeConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class EmployeeCreate(EmployeeConfig):
    position: str

class EmplyeePublic(EmployeeCreate):
    user_id: uuid.UUID
    company_id: uuid.UUID

class EmployeeUpdate(EmployeeConfig):
    position: Optional[str] = None