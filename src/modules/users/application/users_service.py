from uuid import UUID
from typing import List, Union

from src.modules.users.domain.entities import User
from src.modules.users.domain.models import UserCreate, UserUpdate, VerifiedUserUpdate, InternalUserUpdate
from src.modules.users.domain.users_repository import UsersRepository
from src.modules.users.application.use_cases.create_user import CreateUserUseCase
from src.modules.users.application.use_cases.update_user import UpdateUserUseCase

from src.core.utils.decorators.service_error_handler import service_error_handler


class UsersService:
    __MODULE = "users.service"

    def __init__(
        self, 
        respository: UsersRepository, 
        create_user_use_case: CreateUserUseCase,
        update_user_use_case: UpdateUserUseCase
    ):
        self.__repository = respository
        self.__create_user_use_case = create_user_use_case
        self.__update_user_use_case = update_user_use_case

    @service_error_handler(module=__MODULE)
    def create(self, data: UserCreate, is_admin: bool = False) -> User:
        new_user = self.__create_user_use_case.execute(data=data, is_admin=is_admin)
        return self.__repository.create(data=new_user)
    
    @service_error_handler(module=__MODULE)
    def resource(self, key: str,  value: UUID | str) -> User | None:
        return self.__repository.get_one(key=key, value=value)
    
    @service_error_handler(module=__MODULE)
    def update(self, user_id: UUID, changes: Union[UserUpdate, VerifiedUserUpdate, InternalUserUpdate]) -> User:
        processed_changes = self.__update_user_use_case.execute(changes=changes)
        return self.__repository.update(key="user_id", value=user_id, changes=processed_changes)
    
    @service_error_handler(module=__MODULE)
    def delete(self, user_id: UUID) -> User | None:
        return self.__repository.delete(key="user_id", value=user_id)
    
    
    @service_error_handler(module=__MODULE)
    def bulk_delete(
        self,
        ids: List[UUID]
    ) -> List[User]:
        return self.__repository.bulk_delete(
            ids=ids
        )