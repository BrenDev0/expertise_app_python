from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
import uuid
from  datetime import datetime


class CompanyConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        str_min_length=1,
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

