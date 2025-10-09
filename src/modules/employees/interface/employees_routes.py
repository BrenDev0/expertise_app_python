from fastapi import Request, Depends, APIRouter, Body
from uuid import UUID
from typing import List

from src.core.middleware.verification_middleware import verification_middleware
from src.core.middleware.middleware_service import security
from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.middleware.hmac_verification import verify_hmac
from src.core.middleware.permissions import is_manager
from src.core.middleware.hmac_verification import verify_hmac
from src.core.middleware.permissions import is_manager
from src.core.middleware.permissions import token_is_company_stamped

from src.modules.employees.domain.employees_models import EmployeePublic, EmployeeCreate, EmployeeUpdate
from src.modules.employees.interface.employee_controller import EmployeesController
from src.modules.employees.interface.employees_dependencies import get_employees_controller


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(security), Depends(verify_hmac)]
)

@router.post("/verified/create", status_code=201, response_model=ResponseWithToken)
def verified_create(
    req: Request,
    data: EmployeeCreate,
    _: None = Depends(verification_middleware),
    controller: EmployeesController = Depends(get_employees_controller)
): 
    """
    ## Create request

    This endpoint creates an employee in the database.
    The token givin in the invitation acception link must be used in this request.
    Will recieve a new token in the response.
    """
    return controller.create_request(
        req=req,
        data=data
    )

@router.get("/secure/resource", status_code=200, response_model=EmployeePublic)
def secure_resource(
    req: Request,
    _: None = Depends(token_is_company_stamped),
    controller: EmployeesController = Depends(get_employees_controller)
): 
    """
    ## Resource request

    This enpoint will get an employee by id.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.resource_request(
        req=req,
    )

@router.get("/secure/collection", status_code=200, response_model=List[EmployeePublic])
def secure_collection(
    req: Request,
    _: None = Depends(is_manager),
    company = Depends(token_is_company_stamped),
    controller: EmployeesController = Depends(get_employees_controller)
): 
    """
    ## Collection request

    This endpoint will get all employees of a company.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.collection_request(
        req=req
    )

@router.patch("/secure/{employee_id}", status_code=200, response_model=EmployeePublic)
def secure_update(
    employee_id: UUID,
    req: Request,
    data: EmployeeUpdate = Body(...),
    _: None = Depends(is_manager),
    company = Depends(token_is_company_stamped),
    controller: EmployeesController = Depends(get_employees_controller)
):
    """
    ## Update request

    This enpoint updates an employee role by id.
    Only admin level users, and manager level employees have access to this endpoint.
    """
    return controller.update_request(
        employee_id=employee_id,
        req=req,
        data=data
    )

@router.delete("/secure/{employee_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    employee_id: UUID,
    req: Request, 
    _: None = Depends(is_manager),
    company = Depends(token_is_company_stamped),
    controller: EmployeesController = Depends(get_employees_controller)
): 
    """
    ## Delete request

    This endpoint deletes an employee by id.
    Only admin level users, and manager level employees have access to this endpoint.
    """
    return controller.delete_request(
        employee_id=employee_id,
        req=req,
    )