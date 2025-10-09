import pandas as pd
import io
import chardet
from typing import List
from uuid import UUID

from src.modules.documents.domain.tenant_tables_repository import TenentTablesRepository
from src.modules.documents.domain.entities import TenantTable
from src.core.utils.decorators.service_error_handler import service_error_handler


class TenantDataService:
    """
    Handles the conversion of spreadsheet docs to sql  tables.
    """
    __MODULE = "tenant_data.service"
    def __init__(self, repository: TenentTablesRepository):
        self.__repository = repository


    @service_error_handler(module=__MODULE)
    def create_table_from_file(
        self,
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
        self.__repository.create_table(table_name=table_name, df=df)

        ## Create a reference in tenant_tables
        tenant_table = TenantTable(
            company_id=company_id,
            document_id=document_id,
            table_name=table_name
        )

        self.__repository.create(data=tenant_table)

    @service_error_handler(module=__MODULE)
    def resource(
        self,
        document_id: UUID,
    ) -> TenantTable | None:
        return self.__repository.get_one(
            key="document_id",
            value=document_id
        )
    

    @service_error_handler(module=__MODULE)
    def collection(
        self,
        comapny_id: UUID,
    ) -> List[TenantTable]:
        return self.__repository.get_many(
            key="company_id",
            value=comapny_id
        )

    @service_error_handler(module=__MODULE)
    def delete_document_table(
        self,
        document_id: UUID
    ):
        table: TenantTable = self.resource(
            document_id=document_id
        )

        if table:
            self.__repository.delete_table(table=table)
            
        
    @service_error_handler(module=__MODULE)
    def delete_companies_tables(
        self,
        company_id: UUID
    ) ->  List[TenantTable]:
        tables = self.collection(
            comapny_id=company_id
        )
        for table in tables:
            print(table.table_name)

        if len(tables) != 0:
            for table in tables:
                self.__repository.delete_table(table)