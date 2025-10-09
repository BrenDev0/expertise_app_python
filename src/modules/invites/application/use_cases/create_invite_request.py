from src.core.services.webtoken_service import WebTokenService
from src.core.services.hashing_service import HashingService
from src.core.domain.models.errors import EmailAlreadyInUseError

from src.modules.users.domain.entities import User
from src.modules.companies.domain.enitities import Company
from src.modules.users.application.users_service import UsersService
from src.core.services.email_service import EmailService
from src.modules.invites.application.invites_service import InvitesService
from src.modules.invites.domain.invites_models import InviteCreate
from src.modules.invites.domain.entities import Invite

class CreateInviteRequest():
    def __init__(
        self,
        hashing_service: HashingService,
        web_token_service: WebTokenService,
        users_service: UsersService,
        invites_service: InvitesService,
        email_service: EmailService
    ):
        self.__hashing_service = hashing_service
        self.__web_token_service = web_token_service
        self.__users_service = users_service
        self.__invites_service = invites_service
        self.__email_service = email_service

    def exectute(
        self,
        data: InviteCreate,
        user: User,
        company: Company
    ) -> str :
        hashed_email = self.__hashing_service.hash_for_search(data=data.email)
        
        email_in_use = self.__users_service.resource(key="email_hash", value=hashed_email)
        if email_in_use:
            raise EmailAlreadyInUseError(data.email)

        invite: Invite = self.__invites_service.create(data=data, company_id=company.company_id)

        token = self.__web_token_service.generate_token({
            "verification_code": str(invite.invite_id) 
        }, "24h")

        print(token)

        # self.__email_service.handle_request(
        #     email=data.email,
        #     type_="INVITE", 
        #     custom_code=token
        # )

        return token