from src.core.repository.base_repository import BaseRepository
from sqlalchemy.orm import Session
from src.modules.documents.documents_models import Document
from  uuid import UUID
from src.core.services.data_handling_service import DataHandlingService
from  typing import List, Any
from src.core.decorators.service_error_handler import service_error_handler
from fastapi import UploadFile

class DocumentsService:
    __MODULE = "documents.service"
    def __init__(self, respository: BaseRepository, data_hander: DataHandlingService):
        self.__repository = respository
        self.__data_handler = data_hander

    @service_error_handler(module=__MODULE)
    def create(
        self, 
        db: Session, 
        company_id: UUID, 
        filename: str, 
        file_type: str, 
        url: str
    ) -> Document:
        document = Document(
            company_id=company_id,
            filename=filename,
            file_type=file_type,
            url=self.__data_handler.encryption_service.encrypt(url)
        )

        return self.__repository.create(db=db, data=document)
    
    @service_error_handler(module=__MODULE)
    def resource(self, db: Session, document_id: UUID) -> Document:
        return self.__repository.get_one(db=db, key="document_id", value=document_id)
    
    @service_error_handler(module=__MODULE)
    def collection(self, db: Session, company_id: UUID) -> List[Document]:
        return self.__repository.get_many(db=db, key="company_id", value=company_id)
    
    @service_error_handler(module=__MODULE)
    def delete(self, db: Session, key: str, value: Any) -> Document | List[Document] | None:
        return self.__repository.delete(db=db, key=key, value=value)
    