from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from pydantic.alias_generators import to_camel

class CommonHttpResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid" 
    )
    detail: str

class ResponseWithToken(CommonHttpResponse):
    token: str
    company_id: Optional[UUID] = None