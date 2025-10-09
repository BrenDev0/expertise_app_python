from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class Invite(BaseModel):
    invite_id: Optional[UUID] = None
    company_id: UUID
    email: str
    name: str
    phone: str
    position: Optional[str] = None
    is_manager: bool = False
    created_at: Optional[datetime] = None