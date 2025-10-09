from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService

from src.modules.users.domain.entities import User
from src.modules.users.domain.models import UserCreate

class CreateUserUseCase:
    def __init__(
        self,
        encryption_service: EncryptionService,
        hashing_service: HashingService
    ):
        self.__encryption_service = encryption_service
        self.__hashing_service = hashing_service

    def execute(self, data: UserCreate, is_admin: bool = False) -> User:
        hashed_email = self.__hashing_service.hash_for_search(data=data.email)
        
        hashed_password = self.__hashing_service.hash_password(password=data.password)
        
    
        encrypted_email = self.__encryption_service.encrypt(data.email)
        encrypted_name = self.__encryption_service.encrypt(data.name)
        encrypted_phone = self.__encryption_service.encrypt(data.phone)
        
    
        return User(
            name=encrypted_name,
            email=encrypted_email,
            phone=encrypted_phone,
            email_hash=hashed_email,
            password=hashed_password,
            is_admin=is_admin
        )
            