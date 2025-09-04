from fastapi import APIRouter, Request, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from src.modules.invites.invites_controller import InvitesController
from src.modules.invites.invites_models import InviteCreate, InvitePublic, InviteUpdate
from src.modules.users.users_models import User
from src.core.dependencies.container import Container
from src.core.models.http_responses import CommonHttpResponse
from src.core.database.session import get_db_session
from src.core.middleware.middleware_service import security
from src.core.middleware.permissions import is_owner
from uuid import UUID
from typing import List


router = APIRouter(
    prefix="/invites",
    tags=["Invites"],
    dependencies=[Depends(security), Depends(is_owner)]
)



def get_controller() -> InvitesController:
    controller = Container.resolve("invites_controller")
    return controller


@router.post("/secure", status_code=201, response_model=CommonHttpResponse)
def secure_create(
    req: Request,
    data: InviteCreate = Body(...),
    db: Session = Depends(get_db_session),
    controller: InvitesController = Depends(get_controller)
):
    """
    ## Create request

    This endpoint will send an account invite email.
    Only admin level users have access to this endpoint. 
    """
    return controller.create_request(
        req=req,
        data=data,
        db=db
    )

@router.get("/secure/resource/{invite_id}", status_code=200, response_model=InvitePublic)
def secure_resource(
    invite_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: InvitesController = Depends(get_controller)
): 
    """
    ## Resource request

    This endpoints gets an invite by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.resource_request(
        invite_id=invite_id,
        req=req,
        db=db
    )

@router.get("/secure/collection/{company_id}", status_code=200, response_model=List[InvitePublic])
def secure_collection(
    company_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: InvitesController = Depends(get_controller)
): 
    """
    ## Collection request

    This endpoint returns all unexpired invites sent by a company.
    Only admin level users have access to this endpoint. 
    """
    return controller.collection_request(
        company_id=company_id,
        req=req,
        db=db
    )

@router.patch("/secure/{invite_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    invite_id: UUID,
    req: Request,
    data: InviteUpdate = Body(...),
    db: Session = Depends(get_db_session),
    controller: InvitesController = Depends(get_controller)
):
    """
    ## Update request

    This endpoint updates invitation data by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.update_request(
        invite_id=invite_id,
        req=req,
        data=data,
        db=db
    )


@router.delete("/secure/{invite_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    invite_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: InvitesController = Depends(get_controller)
):
    """
    ## Delete request

    This endpoint deletes an invite by id.
    Only admin level users have access to this endpoint. 
    """
    return controller.delete_request(
        invite_id=invite_id,
        req=req,
        db=db
    )