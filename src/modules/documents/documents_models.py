from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.core.database.database_models import Base 
import uuid
from  datetime import datetime

class Document(Base):
    __tablename__ = "documents"


    document_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    company = relationship("Company")


class TenantTable(Base):
    __tablename__ = "tenant_tables"

    tenant_table_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False)
    table_name = Column(String, nullable=False)
    create_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class DocumentConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra='forbid'
    )

class DocumentPublic(DocumentConfig):
    document_id: uuid.UUID
    company_id: uuid.UUID
    filename: str
    url: str
    uploaded_at: datetime
