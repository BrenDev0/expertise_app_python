from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class Company(BaseModel):
    company_id: Optional[UUID] = None
    user_id: UUID
    company_name: str
    company_location: str
    company_subscription: str = "Free"
    s3_path: Optional[str] = None
    created_at: Optional[datetime] = None