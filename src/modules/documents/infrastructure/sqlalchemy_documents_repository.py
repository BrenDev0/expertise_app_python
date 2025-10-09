import uuid 
from typing import Optional
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.modules.documents.domain.entities import Document
from src.modules.companies.domain.enitities import Company
from  src.modules.companies.infrastructure.sqlalchemy_companies_repository import SqlAlchemyCompany
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base



class SqlAlchemyDocument(Base):
    __tablename__ = "documents"


    document_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    company = relationship("SqlAlchemyCompany")


class SqlAlchemyDocumentsRepsoitory(SqlAlchemyDataRepository[Document, SqlAlchemyDocument]):
    def __init__(self):
        super().__init__(SqlAlchemyDocument)

    def _to_entity(self, model: SqlAlchemyDocument) -> Document:
        return Document(
            document_id=model.document_id,
            company_id=model.company_id,
            filename=model.filename,
            file_type=model.file_type,
            url=model.url,
            uploaded_at=model.uploaded_at,
            company=self._company_to_entity(model.company)
        )
    
    def _company_to_entity(self, company_model: SqlAlchemyCompany) -> Optional[Company]:
        if not company_model:
            return None
        return Company(
            company_id=company_model.company_id,
            user_id=company_model.user_id,
            company_name=company_model.company_name,
            company_location=company_model.company_location,
            company_subscription=company_model.company_subscription,
            s3_path=company_model.s3_path,
            created_at=company_model.created_at
        )
    
    
    def _to_model(self, entity: Document) -> SqlAlchemyDocument:
        data = entity.model_dump(exclude={'document_id', 'uploaded_at', 'company'} if not entity.document_id else set())
        return SqlAlchemyDocument(**data)