from abc import abstractmethod
from uuid import UUID
from pandas import DataFrame

from src.modules.documents.domain.entities import TenantTable
from src.core.domain.repositories.data_repository import DataRepository

class TenentTablesRepository(DataRepository[TenantTable]):
    @abstractmethod
    def create_table(self, table_name: str, df: DataFrame):
        raise NotImplementedError
    
    @abstractmethod
    def delete_table(
        self,
        table: TenantTable
    ) -> TenantTable:
        raise NotImplementedError
        
            