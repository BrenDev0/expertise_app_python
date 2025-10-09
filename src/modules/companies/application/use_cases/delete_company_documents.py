from uuid import UUID

from src.modules.companies.domain.enitities import Company
from src.modules.documents.application.documents_service import DocumentsService
from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService

from src.modules.users.domain.entities import User


class DeleteCompanyDocuments():
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
        user: User,
        company_id: UUID
    ):
        self.__tenant_data_service.delete_companies_tables(
            company_id=company_id
        )

        self.__file_repository.delete_company_data(
            user_id=user.user_id,
            company_id=company_id
        )

        self.__vector_respository.delete_company_data(
            user_id=user.user_id,
            company_id=company_id
        )

        self.__documents_service.delete(
            key="company_id",
            value=company_id
        )