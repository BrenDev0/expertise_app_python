from fastapi import Request, Depends, APIRouter, Body
from src.core.database.session import Session, get_db_session
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.modules.employees.employees_models import EmployeePublic, EmployeeCreate, EmployeeUpdate
from src.modules.employees.employee_controller import EmployeesController
from src.core.dependencies.container import Container
from src.core.middleware.verification_middleware import verification_middleware
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.middleware_service import security
from uuid import UUID
from typing import List

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
    dependencies=[Depends(security)]
)

def get_controller():
    controller = Container.resolve("employees_controller")
    return controller

@router.post("/verified/create", status_code=201, response_model=ResponseWithToken)
def verified_create(
    req: Request,
    data: EmployeeCreate,
    _: None = Depends(verification_middleware),
    db: Session = Depends(get_db_session),
    controller: EmployeesController = Depends(get_controller)
): 
    """
    ## Create request

    This endpoint creates an employee in the database.
    The token givin in the invitation acception link must be used in this request.
    Will recieve a new token in the response.
    """
    return controller.create_request(
        req=req,
        data=data,
        db=db
    )

@router.get("/secure/resource/{employee_id}", status_code=200, response_model=EmployeePublic)
def secure_resource(
    employee_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: EmployeesController = Depends(get_controller)
): 
    """
    ## Resource request

    This enpoint will get an employee by id.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.resource_request(
        employee_id=employee_id,
        req=req,
        db=db
    )

@router.get("/secure/collection/{company_id}", status_code=200, response_model=List[EmployeePublic])
def secure_collection(
    company_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: EmployeesController = Depends(get_controller)
): 
    """
    ## Collection request

    This endpoint will get all employees of a company.
    Only admin level users, and manager level employees have access to this endpoint. 
    """
    return controller.collection_request(
        company_id=company_id,
        req=req,
        db=db
    )

@router.put("/secure/{employee_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    employee_id: UUID,
    req: Request,
    data: EmployeeUpdate = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: EmployeesController = Depends(get_controller)
):
    """
    ## Update request

    This enpoint updates an employee role by id.
    Only admin level users, and manager level employees have access to this endpoint.
    """
    return controller.update_request(
        employee_id=employee_id,
        req=req,
        data=data,
        db=db
    )

@router.delete("/secure/{employee_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    employee_id: UUID,
    req: Request, 
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: EmployeesController = Depends(get_controller)
): 
    """
    ## Delete request

    This endpoint deletes an employee by id.
    Only admin level users, and manager level employees have access to this endpoint.
    """
    return controller.delete_request(
        employee_id=employee_id,
        req=req,
        db=db
    )