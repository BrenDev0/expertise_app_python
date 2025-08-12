from sqlalchemy.orm import Session
from  src.modules.users.users_models import User, UserCreate
from src.core.repository.base_repository import BaseRepository
from src.core.services.data_handling_service import DataHandlingService
from src.core.logs.logger import Logger
from src.core.decorators.service_error_handler import service_error_handler
from uuid import UUID
from typing import Dict, Any

class UsersService:
    __MODULE = "users.service"

    def __init__(self, respository: BaseRepository, data_hanlder: DataHandlingService, logger: Logger):
        self.__repository = respository
        self.__data_handler = data_hanlder
        self._logger = logger

    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, db: Session, user: UserCreate, ) -> User:
        hashed_email = self.__data_handler.hashing_service.hash_for_search(data=user.email)
        hashed_password = self.__data_handler.hashing_service.hash_password(password=user.password)

        new_user = User(
            **user.model_dump(by_alias=False, exclude="code"),
            email_hash = hashed_email
        )

        new_user.password = hashed_password

        return self.__repository.create(db=db, data=new_user)
    

    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, key: str,  value: UUID | str) -> User:
        return self.__repository.get_one(db=db, key=key, value=value)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, user_id: UUID, changes: Dict[str, Any]) -> User:
        return self.__repository.update(db=db, key="agent_id", value=user_id, changes=changes.model_dump(by_alias=False, exclude_unset=True))
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, db: Session, user_id: UUID) -> User:
        return self.__repository.delete(db=db, key="user_id", value=user_id)