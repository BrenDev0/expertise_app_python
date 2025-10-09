from fastapi import Depends

from src.core.services.encryption_service import EncryptionService
from src.core.services.email_service import EmailService
from src.core.domain.repositories.data_repository import DataRepository
from src.core.services.webtoken_service import WebTokenService
from src.core.services.hashing_service import HashingService
from src.core.dependencies.services import get_encryption_service, get_email_service, get_web_token_service, get_hashing_service

from src.modules.users.application.users_service import UsersService
from src.modules.users.interface.users_dependencies import get_users_service
from src.modules.invites.infrastructure.sqlalchemy_invites_repository import SqlAlchemyInvitesRepository
from src.modules.invites.interface.invites_controller import InvitesController
from src.modules.invites.application.invites_service import InvitesService
from src.modules.invites.domain.entities import Invite
from src.modules.invites.application.use_cases.create_invite_request import CreateInviteRequest




def get_invites_repository() -> DataRepository:
    return SqlAlchemyInvitesRepository()

def get_invites_service(
    repository: DataRepository = Depends(get_invites_repository),
    encryption_service = Depends(get_encryption_service)
) -> InvitesService:
    return InvitesService(
        repository=repository,
        encryption_service=encryption_service
    )

def get_create_invite_request_use_case(
    hashing_service: HashingService = Depends(get_hashing_service),
    web_token_service: WebTokenService = Depends(get_web_token_service),
    users_service: UsersService = Depends(get_users_service),
    email_service: EmailService = Depends(get_email_service),
    invites_service: InvitesService = Depends(get_invites_service)
) -> CreateInviteRequest:
    return CreateInviteRequest(
        hashing_service=hashing_service,
        web_token_service=web_token_service,
        users_service=users_service,
        email_service=email_service,
        invites_service=invites_service
    )

def get_invites_controller(
    invites_service: InvitesService = Depends(get_invites_service),
    encryption_service: EncodingWarning = Depends(get_encryption_service),
    create_initation_request: CreateInviteRequest = Depends(get_create_invite_request_use_case)
) ->InvitesController:
    return InvitesController(
        invites_service=invites_service,
        encryption_service=encryption_service,
        create_Invite_request=create_initation_request
    )