from src.core.services.http_service import HttpService
from src.core.services.email_service import EmailService
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.modules.invites.invites_service import InvitesService
from src.core.dependencies.container import Container
from src.modules.users.users_service import UsersService
from src.modules.invites.invites_models import Invite, InviteCreate, InviteUpdate, InvitePublic
from src.modules.users.users_models import User
from src.modules.companies.companies_models import Company
from typing import List
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

class InvitesController:
    def __init__(self, http_service: HttpService, invites_service: InvitesService, email_service: EmailService):
        self.__http_service = http_service
        self.__invites_service = invites_service
        self.__email_service = email_service

    
    def create_request(
        self,
        req: Request,
        data: InviteCreate,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user
        company_id  = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        hashed_email = self.__http_service.hashing_service.hash_for_search(data=data.email)
        
        user_service: UsersService = Container.resolve("users_service")

        email_in_use = user_service.resource(db=db, key="email_hash", value=hashed_email)
        if email_in_use:
            raise HTTPException(status_code=400, detail="Email in use")

        invite = self.__invites_service.create(db=db, data=data, company_id=company_id)

        self.__email_service.handle_request(
            email=data.email,
            type_="INVITE", 
            webtoken_service=self.__http_service.webtoken_service,
            invitation_id=invite.invite_id
        )

        return CommonHttpResponse(
            detail="Invitaion sent"
        )
    
    def resource_request(
        self,
        invite_id: UUID,
        req: Request,
        db: Session
    ) -> InvitePublic:
        user: User = req.state.user
        company_id  = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        invite_resource: Invite = self.__http_service.request_validation_service.verify_resource(
            service_key="invites_service",
            params={
                "db": db,
                "invite_id": invite_id
            },
            not_found_message="Invite not found",
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, invite_resource.company_id)

        return self.__to_public(invite_resource)
    
    def collection_request(
        self,
        req: Request,
        db: Session
    ) -> List[InvitePublic]:
        user: User = req.state.user
        company_id  = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        data = self.__invites_service.collection(db=db, company_id=company_id)

        return [
            self.__to_public(invite) for invite in data
        ]
    

    def update_request(
        self,
        invite_id: UUID,
        req: Request,
        data: InviteUpdate,
        db: Session
    ) -> CommonHttpResponse: 
        user: User = req.state.user
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        invite_resource: Invite = self.__http_service.request_validation_service.verify_resource(
            service_key="invites_service",
            params={
                "db": db,
                "invite_id": invite_id
            },
            not_found_message="Invite not found",
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, invite_resource.company_id)

        self.__invites_service.update(db=db, invite_id=invite_id, changes=data)

        return CommonHttpResponse(
            detail="Invite updated"
        )
    
    def delete_request(
        self,
        invite_id: UUID,
        req: Request,
        db: Session
    ) -> CommonHttpResponse: 
        user: User = req.state.user
        company_id  = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        invite_resource: Invite = self.__http_service.request_validation_service.verify_resource(
            service_key="invites_service",
            params={
                "db": db,
                "invite_id": invite_id
            },
            not_found_message="Invite not found",
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, invite_resource.company_id)
        
        self.__invites_service.delete(db=db, invite_id=invite_id)

        return CommonHttpResponse(
            detail="Invite Deleted"
        )
        
    
    def __to_public(self,data: Invite) -> InvitePublic:
        data.invite_id = str(data.invite_id)
        data.name = self.__http_service.encryption_service.decrypt(data.name)
        data.email = self.__http_service.encryption_service.decrypt(data.email)
        data.phone = self.__http_service.encryption_service.decrypt(data.phone)

        invite = InvitePublic.model_validate(data, from_attributes=True)
        return invite