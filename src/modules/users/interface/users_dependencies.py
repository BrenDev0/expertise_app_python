from fastapi import Depends

from src.modules.documents.application.documents_service import DocumentsService

from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.repositories.file_repository import FileRepository
from src.modules.documents.application.tenant_data_service import TenantDataService

from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.dependencies.services import get_encryption_service, get_hashing_service

from src.modules.users.application.users_service import UsersService
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.application.use_cases.update_user import UpdateUserUseCase

from src.modules.users.interface.users_controller import UsersController 
from src.modules.users.domain.users_repository import UsersRepository
from src.modules.users.infrastructure.sqlalchemy_user_repository import SqlAlchemyUsersRepository
from src.modules.users.application.use_cases.delete_user_documents import DeleteUserDocuments
from src.modules.documents.interface.documents_dependencies import get_documents_service, get_file_repository, get_vector_repository, get_tenant_data_service
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.companies.interface.companies_dependencies import get_companies_service



def get_users_repository() -> UsersRepository:
    return SqlAlchemyUsersRepository()

def get_create_user_use_case(
    encrytpion_service: EncryptionService = Depends(get_encryption_service),
    hashing_service: HashingService = Depends(get_hashing_service)
) -> CreateUserUseCase:
    return CreateUserUseCase(
        encryption_service=encrytpion_service,
        hashing_service=hashing_service
    )

def get_update_user_use_case(
    encrytpion_service: EncryptionService = Depends(get_encryption_service),
    hashing_service: HashingService = Depends(get_hashing_service)
) -> UpdateUserUseCase:
    return UpdateUserUseCase(
        encryption_service=encrytpion_service,
        hashing_service=hashing_service
    )

def get_users_service(
    repository: UsersRepository = Depends(get_users_repository),
    create_user_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    update_user_use_case: UpdateUserUseCase = Depends(get_update_user_use_case)
)-> UsersService:
    return UsersService(
        respository=repository,
        create_user_use_case=create_user_use_case,
        update_user_use_case=update_user_use_case
    )

def get_delete_user_documents_use_case(
    file_repository: FileRepository = Depends(get_file_repository),
    vector_repository: VectorRepository = Depends(get_vector_repository),
    tenant_data_service: TenantDataService = Depends(get_tenant_data_service),
    documents_service: DocumentsService = Depends(get_documents_service),
    companies_service: CompaniesService = Depends(get_companies_service)
) -> DeleteUserDocuments:
    return DeleteUserDocuments(
        vector_repository=vector_repository,
        file_repository=file_repository,
        documents_service=documents_service,
        tenent_data_service=tenant_data_service,
        companies_service=companies_service
    )

def get_users_controller(
    users_service: UsersService = Depends(get_users_service),
    delete_user_documents: DeleteUserDocuments = Depends(get_delete_user_documents_use_case)
):
    return UsersController(
        users_service=users_service,
        delete_user_documents=delete_user_documents
    )
