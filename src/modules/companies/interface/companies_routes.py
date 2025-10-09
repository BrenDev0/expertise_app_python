from fastapi import APIRouter, Request, Body, Depends
from uuid import UUID
from typing import List

from src.core.dependencies.services import get_web_token_service
from src.core.services.webtoken_service import WebTokenService
from src.core.interface.middleware.hmac_verification import verify_hmac
from src.core.interface.middleware.permissions import token_is_company_stamped
from src.core.interface.middleware.permissions import is_owner
from src.core.interface.middleware.middleware_service import security
from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken

from src.modules.companies.interface.companies_controller import CompaniesController
from src.modules.companies.domain.companies_models import CompanyPublic, CompanyCreate, CompanyUpdate
from src.modules.companies.interface.companies_dependencies import get_companies_controller

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    dependencies=[Depends(security), Depends(verify_hmac)] # applied to all routes
)


@router.post("/secure/create", status_code=201, response_model=CompanyPublic)
def secure_create(
    req: Request,
    data: CompanyCreate = Body(...),
    _: None = Depends(is_owner),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Create request

    This enpoint will create a company in the database.
    Only admin level users have access to this endpoint.
    """
    return controller.create_request(
        req=req,
        data=data
    )

@router.get("/secure/login/{company_id}", status_code=200, response_model=ResponseWithToken)
def secure_login(
    company_id: UUID,
    req: Request,
    _: None = Depends(is_owner),
    web_token_service: WebTokenService = Depends(get_web_token_service),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Exchange login token for company marked token

    This endpoint is used by admin users to receive a company specific token used for company specific business, 
    such as agent interactions, employee managment, ect..
    Due to admin users alternative dashboad after login the token must be exchanged using this endpoint before any editorial actions can be made.

    """
    return controller.login(
        company_id=company_id,
        req=req,
        web_token_service=web_token_service
    )

@router.get("/secure/resource", status_code=200, response_model=CompanyPublic)
def secure_resource(
    req: Request,
    _: None = Depends(token_is_company_stamped),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Resource request

    This endpoint gets the company that the user is currently working in.
    """
    return controller.resource_request(
        req=req
    )


@router.get("/secure/collection", status_code=200, response_model=List[CompanyPublic])
def secure_collection(
    req: Request,
    _: None = Depends(is_owner),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Collection request

    This endpoint gets all companies related to the current user.
    Only admin level users have access to this endpoint.
    """
    return controller.collection_request(
        req=req
    )

@router.patch("/secure", status_code=200, response_model=CompanyPublic)
def secure_update(
    req: Request,
    data: CompanyUpdate = Body(...),
    _: None = Depends(is_owner),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Update request

    This endpoint updates a company by id.
    Only admin level users have access to this endpoint.
    """
    return controller.update_request(
        req=req,
        data=data
    )

@router.delete("/secure/{company_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    company_id: UUID,
    req: Request,
    _: None = Depends(is_owner),
    controller: CompaniesController = Depends(get_companies_controller)
):
    """
    ## Delete request

    This endpoint deletes a company by id.
    Only admin level users have access to this endpoint.
    """
    return controller.delete_request(
        company_id=company_id,
        req=req
    )