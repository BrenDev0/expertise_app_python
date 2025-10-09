import uuid 
from sqlalchemy import Column, String, DateTime, func, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from pandas import DataFrame

from src.modules.documents.domain.entities import TenantTable
from src.modules.documents.domain.tenant_tables_repository import TenentTablesRepository
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base

class SqlAlchemyTenantTable(Base):
    __tablename__ = "tenant_tables"

    tenant_table_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False)
    table_name = Column(String, nullable=False)
    create_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class SqlAlchemyTennentTableRepsoitory(SqlAlchemyDataRepository[TenantTable, SqlAlchemyTenantTable], TenentTablesRepository):
    def __init__(self):
        super().__init__(SqlAlchemyTenantTable)

    def _to_entity(self, model: SqlAlchemyTenantTable) -> TenantTable:
        return TenantTable(
            tenant_table_id=model.tenant_table_id,
            company_id=model.company_id,
            table_name=model.table_name,
            create_at=model.create_at
        )
    
    def _to_model(self, entity: TenantTable) -> SqlAlchemyTenantTable:
        data = entity.model_dump(exclude={'tenant_table_id ', 'created_at'} if not entity.tenant_table_id else set())
        return SqlAlchemyTenantTable(**data)
    
    def create_table(self, table_name: str, df: DataFrame):
        with self._get_session as db:
            df.to_sql(
                name=table_name, 
                con=db.get_bind(),
                index=False,
                if_exists="replace",
                schema="public"
            )
    
    def delete_table(self, table: TenantTable):
        with self._get_session as db:
            db.execute(text(f'DROP TABLE IF EXISTS "{table.table_name}"'))
            db.commit()