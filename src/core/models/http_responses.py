from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CommonHttpResponse(BaseModel):
    detail: str

class ResponseWithToken(CommonHttpResponse):
    token: str
    company_id: Optional[UUID] = None