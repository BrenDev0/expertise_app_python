from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.domain.enitities import Company
from src.modules.documents.application.documents_service import DocumentsService
from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService

from src.modules.users.domain.entities import User

class DeleteUserDocuments():
    def __init__(
        self,
        companies_service: CompaniesService,
        vector_repository: VectorRepository,
        file_repository: FileRepository,
        documents_service: DocumentsService,
        tenent_data_service: TenantDataService
    ):
        self.__companies_service = companies_service
        self.__vector_respository = vector_repository
        self.__file_repository = file_repository
        self.__documents_service = documents_service,
        self.__tenant_data_service = tenent_data_service

    def execute(
        self,
        user: User,
        company: Company
    ):

        ## delete bucket and vector base data 
        users_companies = self.__companies_service.collection(user_id=user.user_id)

        self.__file_repository.delete_user_data(user_id=user.user_id)

        self.__vector_respository.delete_user_data(user_id=user.user_id)

        for company in users_companies:
            self.__tenant_data_service.delete_companies_tables(
                company_id=company.company_id
            )

            self.__documents_service.delete(
                key="company_id",
                value=company.company_id
            )

        ## delete companies and employee accounts
        companies = self.__companies_service.collection(user_id=user.user_id)

        if len(companies) != 0:
            for company in companies:
                self.__companies_service.delete(company_id=company.company_id)