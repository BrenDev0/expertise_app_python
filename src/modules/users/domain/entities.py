from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class User(BaseModel):
    user_id: Optional[UUID] = None
    name: str
    phone: str
    email: str
    email_hash: str
    password: str
    is_admin: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None