from abc  import ABC, abstractmethod
from uuid import UUID

class FileRepository(ABC):
    @abstractmethod
    async def upload(
        self, 
        file_bytes: bytes,
        filename: str,
        company_id: UUID,
        user_id: UUID
    ) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def delete_user_data(self, user_id: UUID) -> None:
        raise NotImplementedError


    @abstractmethod
    def delete_company_data(self, user_id: UUID, company_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_document_data(self, 
        user_id: UUID,
        company_id: UUID,
        filename: str
       
    ) -> None:
        raise NotImplementedError
