from fastapi import APIRouter, Request, Depends, Body
from uuid import UUID
from typing import List

from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.middleware.middleware_service import security
from src.core.middleware.permissions import is_owner, token_is_company_stamped
from src.core.middleware.hmac_verification import verify_hmac

from src.modules.invites.interface.invites_controller import InvitesController
from src.modules.invites.domain.invites_models import InviteCreate, InvitePublic, InviteUpdate
from src.modules.invites.interface.invites_dependencies import get_invites_controller


router = APIRouter(
    prefix="/invites",
    tags=["Invites"],
    dependencies=[
        Depends(security), 
        Depends(verify_hmac), 
        Depends(is_owner), 
        Depends(token_is_company_stamped)
    ]
)


@router.post("/secure", status_code=201, response_model=CommonHttpResponse)
def secure_create(
    req: Request,
    data: InviteCreate = Body(...),
    controller: InvitesController = Depends(get_invites_controller)
):
    """
    ## Create request

    This endpoint will send an account invite email.
    The email sent will have a link with the token attached as a parameter, token is needed for next step.
    Only admin level users have access to this endpoint. 
    """
    return controller.create_request(
        req=req,
        data=data
    )

@router.get("/secure/resource/{invite_id}", status_code=200, response_model=InvitePublic)
def secure_resource(
    invite_id: UUID,
    req: Request,
    controller: InvitesController = Depends(get_invites_controller)
): 
    """
    ## Resource request

    This endpoints gets an invite by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.resource_request(
        invite_id=invite_id,
        req=req,
    )

@router.get("/secure/collection", status_code=200, response_model=List[InvitePublic])
def secure_collection(
    req: Request,
    controller: InvitesController = Depends(get_invites_controller)
): 
    """
    ## Collection request

    This endpoint returns all unexpired invites sent by a company.
    Only admin level users have access to this endpoint. 
    """
    return controller.collection_request(
        req=req
    )

@router.patch("/secure/{invite_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    invite_id: UUID,
    req: Request,
    data: InviteUpdate = Body(...),
    controller: InvitesController = Depends(get_invites_controller)
):
    """
    ## Update request

    This endpoint updates invitation data by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.update_request(
        invite_id=invite_id,
        req=req,
        data=data
    )


@router.delete("/secure/{invite_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    invite_id: UUID,
    req: Request,
    controller: InvitesController = Depends(get_invites_controller)
):
    """
    ## Delete request

    This endpoint deletes an invite by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.delete_request(
        invite_id=invite_id,
        req=req
    )