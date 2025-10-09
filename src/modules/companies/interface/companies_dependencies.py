from fastapi import Depends

from src.modules.documents.application.documents_service import DocumentsService

from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService

from src.modules.documents.interface.documents_dependencies import get_documents_service, get_file_repository, get_vector_repository, get_tenant_data_service
from src.core.domain.repositories.data_repository import DataRepository
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository

from src.modules.companies.interface.companies_controller import CompaniesController
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.application.use_cases.delete_company_documents import DeleteCompanyDocuments

def get_companies_repository() -> DataRepository:
    return SqlAlchemyDataRepository()

def get_companies_service(
    repository: DataRepository = Depends(get_companies_repository)
) -> CompaniesService:
    return CompaniesService(
        respository=repository
    )

def get_delete_company_documents_use_case(
    file_repository: FileRepository = Depends(get_file_repository),
    vector_repository: VectorRepository = Depends(get_vector_repository),
    tenant_data_service: TenantDataService = Depends(get_tenant_data_service),
    documents_service: DocumentsService = Depends(get_documents_service),
) -> DeleteCompanyDocuments:
    return DeleteCompanyDocuments(
        vector_repository=vector_repository,
        file_repository=file_repository,
        documents_service=documents_service,
        tenent_data_service=tenant_data_service
    )

def get_companies_controller(
    companies_service: CompaniesService = Depends(get_companies_service),
    delete_company_documents: DeleteCompanyDocuments = Depends(DeleteCompanyDocuments)
) -> CompaniesController:
    return CompaniesController(
        companies_service=companies_service,
        delete_company_documents=delete_company_documents
    )