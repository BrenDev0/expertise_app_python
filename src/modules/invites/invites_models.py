from src.core.database.database_models import Base
from pydantic import BaseModel, ConfigDict,EmailStr
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Optional
from  datetime import datetime


class Invite(Base):
    __tablename__ = "invites"

    invite_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"))
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    position = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class InviteConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class InviteCreate(InviteConfig):
    email: EmailStr
    name: str
    phone: str
    position: str

class InviteUpdate(InviteConfig):
    company_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class InvitePublic(InviteCreate):
    company_id: uuid.UUID
    invite_id: uuid.UUID
    created_at: datetime
