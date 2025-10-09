from fastapi import Depends

from src.modules.documents.application.documents_service import DocumentsService

from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.core.domain.repositories.data_repository import DataRepository


from src.modules.documents.application.tenant_data_service import TenantDataService
from src.modules.documents.interface.documents_dependencies import get_documents_service, get_file_repository, get_vector_repository, get_tenant_data_service

from src.modules.employees.interface.employees_dependencies import get_employees_service
from src.modules.companies.interface.companies_controller import CompaniesController
from src.modules.companies.infrastructure.sqlalchemy_companies_repository import SqlAlchemyCompaniesRepsoitory
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.application.use_cases.delete_company_documents import DeleteCompanyDocuments
from src.modules.companies.application.use_cases.delete_employees_accounts import DeleteEmployeeAccounts

def get_companies_repository() -> DataRepository:
    return SqlAlchemyCompaniesRepsoitory()

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

def get_delete_employee_accounts_use_case(
    employees_service= Depends(get_employees_service)
) -> DeleteEmployeeAccounts:
    from src.modules.users.interface.users_dependencies import get_users_service
    from src.modules.users.application.users_service import UsersService

    users_service: UsersService = get_users_service()
    return DeleteEmployeeAccounts(
        employees_service=employees_service,
        users_service=users_service
    )

def get_companies_service(
    repository: DataRepository = Depends(get_companies_repository),
    delete_company_documents: DeleteCompanyDocuments = Depends(get_delete_company_documents_use_case),
    delete_employee_accounts: DeleteEmployeeAccounts = Depends(get_delete_employee_accounts_use_case)
) -> CompaniesService:
    return CompaniesService(
        respository=repository,
        delete_company_documents=delete_company_documents,
        delete_employee_accounts=delete_employee_accounts
    )

def get_companies_controller(
    companies_service: CompaniesService = Depends(get_companies_service)
) -> CompaniesController:
    return CompaniesController(
        companies_service=companies_service
    )