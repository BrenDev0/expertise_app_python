from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime


class Company(Base):
    __tablename__ = "companies"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String, nullable=False)
    company_location = Column(String, nullable=False)
    company_subscription = Column(String, nullable=False, default="Free")
    s3_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CompanyConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid" 
    )

class CompanyCreate(CompanyConfig):
    company_name: str
    company_location: str
    company_subscription: Optional[str] = "Free"

class CompanyUpdate(CompanyConfig):
    company_id: uuid.UUID
    company_name: Optional[str] = None
    company_location: Optional[str] = None
    company_subscription: Optional[str] = None

class CompanyPublic(CompanyCreate):
    company_id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID

