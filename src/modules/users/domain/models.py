from pydantic import BaseModel, EmailStr, ConfigDict
from  pydantic.alias_generators import to_camel
from uuid import UUID
from datetime import datetime
from typing import Optional

class UsersConfig(BaseModel):
      model_config = ConfigDict(
        populate_by_name=True,
        str_min_length=1,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class UserPublic(UsersConfig):
    user_id: UUID
    name: str
    phone: str
    email: EmailStr
    is_admin: bool
    created_at: datetime 
    last_login: datetime

class UserUpdate(UsersConfig):
    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    old_password: Optional[str] = None

class InternalUserUpdate(BaseModel):
    last_login: datetime

class VerifiedUserUpdate(UsersConfig):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    code: int

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
