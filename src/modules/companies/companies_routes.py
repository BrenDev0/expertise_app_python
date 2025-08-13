from fastapi import APIRouter, Request, Body, HTTPException, Depends
from src.core.dependencies.container import Container
from src.modules.companies.companies_controller import CompaniesController
from src.modules.companies.companies_models import CompanyPublic, CompanyCreate, CompanyUpdate
from src.core.models.http_responses import CommonHttpResponse
from src.core.database.session import get_db_session
from sqlalchemy.orm import Session
from src.modules.users.users_models import User
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.middleware_service import security
from uuid import UUID
from typing import List


def is_owner(req: Request, _: None = Depends(auth_middleware)):
    user: User = req.state.user

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(security), Depends(is_owner)]
)

def get_controller() -> CompaniesController:
    controller = Container.resolve("companies_controller")
    return controller

@router.post("/secure/create", status_code=201, response_model=CommonHttpResponse)
def secure_create(
    req: Request,
    data: CompanyCreate = Body(...),
    db: Session = Depends(get_db_session),
    controller: CompaniesController = Depends(get_controller)
):
    """
    ## Create request

    This enpoint will create a company in the database.
    Only admin level users have access to this endpoint.
    """
    return controller.create_request(
        req=req,
        db=db,
        data=data
    )

@router.get("/secure/resource/{company_id}", status_code=200, response_model=CompanyPublic)
def secure_resource(
    company_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: CompaniesController = Depends(get_controller)
):
    """
    ## Resource request

    This endpoint gets a company from the db by id.
    Only admin level users have access to this endpoint.
    """
    return controller.resource_request(
        company_id=company_id,
        req=req,
        db=db
    )


@router.get("/secure/collection", status_code=200, response_model=List[CompanyPublic])
def secure_collection(
    req: Request,
    db: Session = Depends(get_db_session),
    controller: CompaniesController = Depends(get_controller)
):
    """
    ## Collection request

    This endpoint gets all companies related to the current user.
    Only admin level users have access to this endpoint.
    """
    return controller.collection_request(
        req=req,
        db=db
    )

@router.put("/secure/{company_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    company_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: CompaniesController = Depends(get_controller)
):
    """
    ## Update request

    This endpoint updates a company by id.
    Only admin level users have access to this endpoint.
    """
    return controller.update_request(
        company_id=company_id,
        req=req,
        db=db
    )

@router.delete("/secure/{company_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    company_id: UUID,
    req: Request,
    db: Session = Depends(get_db_session),
    controller: CompaniesController = Depends(get_controller)
):
    """
    ## Delete request

    This endpoint deletes a company by id.
    Only admin level users have access to this endpoint.
    """
    return controller.delete_request(
        company_id=company_id,
        req=req,
        db=db
    )