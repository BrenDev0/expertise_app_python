from uuid import UUID
from typing import List

from src.core.services.encryption_service import EncryptionService
from src.core.domain.repositories.data_repository import DataRepository
from src.core.utils.decorators.service_error_handler import service_error_handler
from src.modules.invites.domain.invites_models import InviteCreate, InviteUpdate
from src.modules.invites.domain.entities import Invite
from src.modules.users.domain.models import UserCreate


class InvitesService:
    __MODULE = "invites.service"
    def __init__(self, 
        repository: DataRepository, 
        encryption_service: EncryptionService
    ):
        self.__repository = repository
        self.__encryption_service = encryption_service

    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, data: InviteCreate, company_id: UUID) -> Invite:
        encrypted_email = self.__encryption_service.encrypt(data.email)
        encrypted_name = self.__encryption_service.encrypt(data.name)
        encrypted_phone = self.__encryption_service.encrypt(data.phone)
        
        invite = Invite(
            company_id=company_id,
            name=encrypted_name,
            email=encrypted_email,
            phone=encrypted_phone,
            position=data.position
        )

        return self.__repository.create(data=invite)
    
  
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, invite_id: UUID) -> Invite | None:
        return self.__repository.get_one(key="invite_id", value=invite_id)
    

    @service_error_handler(module=f"{__MODULE}.collection")
    def collection(self, company_id: UUID) -> List[Invite]:
        return self.__repository.get_many(key="company_id", value=company_id)
    

    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, invite_id: UUID, changes: InviteUpdate) -> Invite:
        return self.__repository.update(
            key="invite_id", 
            value=invite_id, 
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, invite_id: UUID) -> Invite | None:
        return self.__repository.delete(key="invite_id", value=invite_id)
    
    @service_error_handler(module=f"{__MODULE}.extract_user_data_from_invite")
    def extract_user_data_from_invite(self, data: Invite, password: str) -> UserCreate:
        return  UserCreate(
            name=self.__encryption_service.decrypt(data.name),
            phone=self.__encryption_service.decrypt(data.phone),
            email=self.__encryption_service.decrypt(data.email),
            password=password,
            code=1 # placeholder. not needed for backend logic, too lazy to make another model
        )