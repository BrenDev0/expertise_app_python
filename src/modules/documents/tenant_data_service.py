from sqlalchemy.orm import Session
import pandas as pd
import io
from uuid import UUID
from src.core.repository.base_repository import BaseRepository
from src.modules.documents.documents_models import TenantTable
from src.core.decorators.service_error_handler import service_error_handler
import os 
import chardet

class TenantDataService:
    """
    Handles the conversion of spreadsheet docs to sql  tables.
    """
    __MODULE = "tenant_data.service"
    def __init__(self, repository: BaseRepository):
        self.__repository = repository


    @service_error_handler(module=__MODULE)
    def create_table_from_file(
        self,
        db: Session,
        company_id: UUID,
        document_id: UUID,
        filename: str,
        file_bytes: bytes
    ):
        
        encoding = chardet.detect(file_bytes)

        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding["encoding"])
        elif filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file type")
        
        table_name = f"{document_id}_{os.path.splitext(filename)[0]}"
        
        ## Create a table in th db from the df
        df.to_sql(
            name=table_name, 
            con=db.get_bind(),
            index=False,
            if_exists="replace",
            schema="public"
        )

        ## Create a reference in tenant_tables
        tenant_table = TenantTable(
            company_id=company_id,
            document_id=document_id,
            table_name=table_name
        )

        self.__repository.create(db=db, data=tenant_table)

    @service_error_handler(module=__MODULE)
    def resource(
        self,
        db: Session,
        document_id: UUID,
    ) -> TenantTable | None:
        return self.__repository.get_one(
            db=db,
            key="document_id",
            value=document_id
        )

    def delete_document_table(
        self,
        db: Session,
        document_id: UUID
    ):
        table: TenantTable = self.resource(
            db=db,
            document_id=document_id
        )

        if table:
            db.execute(f'DROP TABLE IF EXISTS "{table.table_name}"')
            db.commit()

            return self.__repository.delete(
                db=db,
                key="tenant_table_id",
                value=table.tenant_table_id
            )
            
        
