from uuid import UUID

from src.modules.documents.application.documents_service import DocumentsService
from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService


class DeleteDocument():
    def __init__(
        self,
        vector_repository: VectorRepository,
        file_repository: FileRepository,
        documents_service: DocumentsService,
        tenent_data_service: TenantDataService
    ):
        self.__vector_respository = vector_repository
        self.__file_repository = file_repository
        self.__documents_service = documents_service,
        self.__tenant_data_service = tenent_data_service

    def execute(
        self,
        document_id: UUID,
        company_id: UUID,
        user_id: UUID,
        filename: str,
    ):
        
        self.__file_repository.delete_document_data(
            user_id=user_id, 
            company_id=company_id, 
            filename=filename
        )
        
        if filename.endswith((".xlsx", ".xls", ".xlsm", ".xlsb", ".csv")):
            self.__tenant_data_service.delete_document_table(
                document_id=document_id
            )
        else:
            self.__vector_respository.delete_document_data(
                user_id=str(user_id),
                company_id=str(company_id),
                filename=filename
            )

        self.__documents_service.delete(
            key="document_id",
            value=document_id
        )