from sqlalchemy.orm import Session
from  src.modules.users.users_models import User, UserCreate, UserUpdate
from src.core.repository.base_repository import BaseRepository
from src.core.services.data_handling_service import DataHandlingService
from src.core.decorators.service_error_handler import service_error_handler
from uuid import UUID

class UsersService:
    __MODULE = "users.service"

    def __init__(self, respository: BaseRepository, data_hanlder: DataHandlingService):
        self.__repository = respository
        self.__data_handler = data_hanlder

    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, db: Session, data: UserCreate, is_admin: bool = False) -> User:
        hashed_email = self.__data_handler.hashing_service.hash_for_search(data=data.email)
        hashed_password = self.__data_handler.hashing_service.hash_password(password=data.password)
        
        encrypted_email = self.__data_handler.encryption_service.encrypt(data.email)
        encrypted_name = self.__data_handler.encryption_service.encrypt(data.name)
        encrypted_phone = self.__data_handler.encryption_service.encrypt(data.phone)
        
        new_user = User(
            name=encrypted_name,
            email=encrypted_email,
            phone=encrypted_phone,
            email_hash=hashed_email,
            password=hashed_password
        )

        if is_admin:
            new_user.is_admin = True

        return self.__repository.create(db=db, data=new_user)
    
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, key: str,  value: UUID | str) -> User:
        return self.__repository.get_one(db=db, key=key, value=value)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, user_id: UUID, changes: UserUpdate) -> User:
        data = changes.model_dump(exclude={"old_password"}, by_alias=False, exclude_unset=True)
        if changes.password:
            hashed_password = self.__data_handler.hashing_service.hash_password(changes.password)
            data["password"] = hashed_password

        if changes.name:
            encrypted_name = self.__data_handler.encryption_service.encrypt(changes.name)
            data["name"] = encrypted_name

        if changes.phone:
            encrypted_phone = self.__data_handler.encryption_service.encrypt(changes.phone)
            data["phone"] = encrypted_phone
            
        return self.__repository.update(db=db, key="user_id", value=user_id, changes=data)
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, db: Session, user_id: UUID) -> User:
        return self.__repository.delete(db=db, key="user_id", value=user_id)