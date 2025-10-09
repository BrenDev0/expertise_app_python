from typing import Dict, Any, Union
from src.modules.users.domain.models import UserUpdate, VerifiedUserUpdate
from src.core.services.encryption_service import EncryptionService
from src.core.services.hashing_service import HashingService

class UpdateUserUseCase:
    def __init__(
        self, 
        encryption_service: EncryptionService,
        hashing_service: HashingService
    ):
        self.__encryption_service = encryption_service
        self.__hashing_service = hashing_service

    def execute(self, changes: Union[UserUpdate, VerifiedUserUpdate]) -> Dict[str, Any]:
        """
        Business rule: Update user data with proper encryption and hashing
        """
        data = changes.model_dump(exclude={"old_password", "code"}, by_alias=False, exclude_unset=True)

        fields_to_encrypt = ["name", "email", "phone"]
        for key in fields_to_encrypt:
            value = getattr(changes, key, None)
            if value not in (None, ""):
                data[key] = self.__encryption_service.encrypt(value)

        # Hash email for search if email is being updated
        if changes.email:
            email_hash = self.__hashing_service.hash_for_search(changes.email)
            data["email_hash"] = email_hash
        
        if getattr(changes, "password", None):
            hashed_password = self.__hashing_service.hash_password(changes.password)
            data["password"] = hashed_password
            
        return data