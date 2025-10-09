from pydantic import BaseModel, ConfigDict,EmailStr
from pydantic.alias_generators import to_camel

import uuid
from typing import Optional
from  datetime import datetime





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
    position: Optional[str] = None
    is_manager: bool = False

class InviteUpdate(InviteConfig):
    company_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    is_manager: Optional[bool] = None

class InvitePublic(InviteCreate):
    company_id: uuid.UUID
    invite_id: uuid.UUID
    created_at: datetime
