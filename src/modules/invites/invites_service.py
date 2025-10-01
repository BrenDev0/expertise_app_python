from src.core.repository.base_repository import BaseRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.core.services.data_handling_service import DataHandlingService
from src.modules.invites.invites_models import Invite, InviteCreate, InviteUpdate
from src.modules.users.users_models import UserCreate
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

class InvitesService:
    __MODULE = "invites.service"
    def __init__(self, repository: BaseRepository, data_handler: DataHandlingService):
        self.__repository = repository
        self.__data_handler = data_handler

    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, db: Session, data: InviteCreate, company_id: UUID) -> Invite:
        encrypted_email = self.__data_handler.encryption_service.encrypt(data.email)
        encrypted_name = self.__data_handler.encryption_service.encrypt(data.name)
        encrypted_phone = self.__data_handler.encryption_service.encrypt(data.phone)
        
        invite = Invite(
            company_id=company_id,
            name=encrypted_name,
            email=encrypted_email,
            phone=encrypted_phone,
            position=data.position
        )

        return self.__repository.create(db=db, data=invite)
    
  
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, invite_id: UUID) -> Invite | None:
        return self.__repository.get_one(db=db, key="invite_id", value=invite_id)
    

    @service_error_handler(module=f"{__MODULE}.collection")
    def collection(self, db: Session, company_id: UUID) -> List[Invite]:
        return self.__repository.get_many(db=db, key="company_id", value=company_id)
    

    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, invite_id: UUID, changes: InviteUpdate) -> Invite:
        return self.__repository.update(
            db=db, key="invite_id", 
            value=invite_id, 
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, db: Session, invite_id: UUID) -> Invite | None:
        return self.__repository.delete(db=db, key="invite_id", value=invite_id)
    
    @service_error_handler(module=f"{__MODULE}.extract_user_data_from_invite")
    def extract_user_data_from_invite(self, data: Invite, password: str) -> UserCreate:
        return  UserCreate(
            name=self.__data_handler.encryption_service.decrypt(data.name),
            phone=self.__data_handler.encryption_service.decrypt(data.phone),
            email=self.__data_handler.encryption_service.decrypt(data.email),
            password=password,
            code=1 # placeholder. not needed for backend logic, too lazy to make another model
        )