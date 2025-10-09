from typing import List
from fastapi import Request, HTTPException
from uuid import UUID

from src.core.domain.models.errors import EmailAlreadyInUseError
from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.services.encryption_service import EncryptionService

from src.modules.invites.application.invites_service import InvitesService
from src.modules.invites.domain.invites_models import InviteCreate, InviteUpdate, InvitePublic
from src.modules.invites.domain.entities import Invite
from src.modules.invites.application.use_cases.create_invite_request import CreateInviteRequest
from src.modules.users.domain.entities import User
from src.modules.companies.domain.enitities import Company


from src.core.services.request_validation_service import RequestValidationService

class InvitesController:
    def __init__(
        self, 
        invites_service: InvitesService, 
        encryption_service: EncryptionService,
        create_Invite_request: CreateInviteRequest
    ):
        self.__invites_service = invites_service
        self.__encryption_service = encryption_service
        self.__create_Invite_request = create_Invite_request

    
    def create_request(
        self,
        req: Request,
        data: InviteCreate,
    ) -> CommonHttpResponse:
        user: User = req.state.user
        company: Company  = req.state.company

        try:
            token = self.__create_Invite_request.exectute(
                data=data,
                user=user,
                company=company,
            )
        
        except EmailAlreadyInUseError as e:
            raise HTTPException(status_code=401, detail=str(e))
 
        # self.__email_service.handle_request(
        #     email=data.email,
        #     type_="INVITE", 
        #     custom_code=token
        # )

        return CommonHttpResponse(
            detail=token
        )
    
    def resource_request(
        self,
        invite_id: UUID,
        req: Request,
    ) -> InvitePublic:
        user: User = req.state.user
        company: Company = req.state.company

        invite_resource = self.__invites_service.resource(
            invite_id=invite_id
        )

        RequestValidationService.verify_resource(
            result=invite_resource,
            not_found_message="Invite not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, invite_resource.company_id)

        return self.__to_public(invite_resource)
    
    def collection_request(
        self,
        req: Request,
    ) -> List[InvitePublic]:
        user: User = req.state.user
        company: Company  = req.state.company

        data = self.__invites_service.collection(company_id=company.company_id)

        return [
            self.__to_public(invite) for invite in data
        ]
    

    def update_request(
        self,
        invite_id: UUID,
        req: Request,
        data: InviteUpdate,
    ) -> CommonHttpResponse: 
        user: User = req.state.user
        company: Company = req.state.company

        invite_resource = self.__invites_service.resource(
            invite_id=invite_id
        )

        RequestValidationService.verify_resource(
            result=invite_resource,
            not_found_message="Invite not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, invite_resource.company_id)

        self.__invites_service.update(invite_id=invite_id, changes=data)

        return CommonHttpResponse(
            detail="Invite updated"
        )
    
    def delete_request(
        self,
        invite_id: UUID,
        req: Request,
    ) -> CommonHttpResponse: 
        user: User = req.state.user
        company: Company  = req.state.company

        invite_resource = self.__invites_service.resource(
            invite_id=invite_id
        )

        RequestValidationService.verify_resource(
            result=invite_resource,
            not_found_message="Invite not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, invite_resource.company_id)
        
        self.__invites_service.delete(invite_id=invite_id)

        return CommonHttpResponse(
            detail="Invite Deleted"
        )
        
    
    def __to_public(self,data: Invite) -> InvitePublic:
        data.invite_id = str(data.invite_id)
        data.name = self.__encryption_service.decrypt(data.name)
        data.email = self.__encryption_service.decrypt(data.email)
        data.phone = self.__encryption_service.decrypt(data.phone)

        invite = InvitePublic.model_validate(data, from_attributes=True)
        return invite