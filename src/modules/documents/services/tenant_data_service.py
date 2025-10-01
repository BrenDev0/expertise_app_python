from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import io
from uuid import UUID
from src.core.repository.base_repository import BaseRepository
from src.modules.documents.documents_models import TenantTable
from src.core.decorators.service_error_handler import service_error_handler
import os 
import chardet
from typing import List

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
        
        table_name = str(document_id).replace('-', "")[:16]
        
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
    

    @service_error_handler(module=__MODULE)
    def collection(
        self,
        db: Session,
        comapny_id: UUID,
    ) -> List[TenantTable]:
        return self.__repository.get_many(
            db=db,
            key="company_id",
            value=comapny_id
        )

    @service_error_handler(module=__MODULE)
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
            self.__handle_delete(
                db=db,
                table=table
            )
            
        
    @service_error_handler(module=__MODULE)
    def delete_companies_tables(
        self,
        db: Session,
        company_id: UUID
    ) ->  List[TenantTable]:
        tables = self.collection(
            db=db,
            comapny_id=company_id
        )
        print(tables)

        if len(tables) != 0:
            for table in tables:
                self.__handle_delete(
                    db=db,
                    table=table
                )

    @service_error_handler(module=__MODULE)
    def __handle_delete(
        self,
        db: Session,
        table: TenantTable
    ) -> TenantTable:
        print(table)
        
        db.execute(text(f'DROP TABLE IF EXISTS "{table.table_name}"'))
        db.commit()

        return self.__repository.delete(
            db=db,
            key="tenant_table_id",
            value=table.tenant_table_id
        )
        
            
        
