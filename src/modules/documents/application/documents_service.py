from  uuid import UUID
from  typing import List, Any


from src.core.services.encryption_service import EncryptionService
from src.core.utils.decorators.service_error_handler import service_error_handler
from src.core.domain.repositories.data_repository import DataRepository

from src.modules.documents.domain.entities import Document

class DocumentsService:
    __MODULE = "documents.service"
    def __init__(
        self, 
        respository: DataRepository ,
        encryption_service: EncryptionService
    ):
        self.__repository = respository
        self.__encryption_service = encryption_service

    @service_error_handler(module=__MODULE)
    def create(
        self, 
        company_id: UUID, 
        filename: str, 
        file_type: str, 
        url: str
    ) -> Document:
        document = Document(
            company_id=company_id,
            filename=filename,
            file_type=file_type,
            url=self.__encryption_service.encrypt(url)
        )

        return self.__repository.create(data=document)
    
    @service_error_handler(module=__MODULE)
    def resource(self, key: str, value: UUID | str) -> Document:
        return self.__repository.get_one(key=key, value=value)
    
    @service_error_handler(module=__MODULE)
    def collection(self, company_id: UUID) -> List[Document]:
        return self.__repository.get_many(key="company_id", value=company_id)
    
    @service_error_handler(module=__MODULE)
    def delete(self, key: str, value: Any) -> Document | List[Document] | None:
        return self.__repository.delete(key=key, value=value)
    