from fastapi import Depends
from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService
from src.core.dependencies.services import get_encryption_service, get_hashing_service

from src.modules.users.interface.users_controller import UsersController 
from src.modules.users.application.users_service import UsersService
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.application.use_cases.update_user import UpdateUserUseCase
from src.modules.users.domain.users_repository import UsersRepository
from src.modules.users.infrastructure.sqlalchemy_user_repository import SqlAlchemyUsersRepository


def get_http_service() -> HttpService:
    return Container.resolve("http_service")

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

def get_users_controller(
    http_service: HttpService = Depends(get_http_service),
    users_service: UsersService = Depends(get_users_service)
):
    return UsersController(
        http_service=http_service,
        users_service=users_service
    )
