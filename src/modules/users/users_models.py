from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime
from src.core.models.http_responses import CommonHttpResponse


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    email_hash = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class UsersConfig(BaseModel):
      model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid" 
    )

class UserPublic(UsersConfig):
    user_id: uuid.UUID
    name: str
    phone: str
    email: EmailStr
    is_admin: bool
    created_at: datetime 

  

class UserCreate(UsersConfig):
    name: str
    phone: str
    email: EmailStr
    password: str
    code: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VerifyEmail(BaseModel):
    email: EmailStr




