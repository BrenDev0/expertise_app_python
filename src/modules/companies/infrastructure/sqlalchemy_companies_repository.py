import uuid 
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.modules.companies.domain.enitities import Company
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base


class SqlAlchemyCompany(Base):
    __tablename__ = "companies"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String, nullable=False)
    company_location = Column(String, nullable=False)
    company_subscription = Column(String, nullable=False, default="Free")
    s3_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SqlAlchemyCompaniesRepsoitory(SqlAlchemyDataRepository[Company, SqlAlchemyCompany]):
    def __init__(self):
        super().__init__(SqlAlchemyCompany)

    def _to_entity(self, model: SqlAlchemyCompany) -> Company:
        return Company(
            company_id=model.company_id,
            user_id=model.user_id,
            company_name=model.company_name,
            company_location=model.company_location,
            company_subscription=model.company_subscription,
            s3_path=model.s3_path,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: Company) -> SqlAlchemyCompany:
        data = entity.model_dump(exclude={'company_id', 'created_at'} if not entity.company_id else set())
        return SqlAlchemyCompany(**data)