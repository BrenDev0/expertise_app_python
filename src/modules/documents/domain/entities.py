from  pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

from src.modules.companies.domain.enitities import Company

class Document(BaseModel):
    document_id: Optional[UUID]
    company_id: UUID
    filename: str
    file_type: str
    url: str
    uploaded_at: Optional[datetime]
    company: Optional[Company]


class TenantTable(BaseModel):
    tenant_table_id: Optional[UUID]
    company_id: UUID
    document_id: UUID
    table_name: str
    create_at: Optional[datetime]