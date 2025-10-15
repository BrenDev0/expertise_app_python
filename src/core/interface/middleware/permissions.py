from fastapi import HTTPException, Depends, Request
from src.modules.users.domain.entities import User
from src.core.interface.middleware.auth_middleware import auth_middleware

from src.modules.employees.domain.entities import Employee
from sqlalchemy.orm import Session

from src.core.interface.request_validation_service import RequestValidationService
from src.modules.companies.domain.enitities import Company
from src.modules.companies.application.companies_service import CompaniesService
from src.modules.employees.application.employees_service import EmployeesService

from src.modules.companies.interface.companies_dependencies import get_companies_service
from src.modules.employees.interface.employees_dependencies import get_employees_service

def is_owner(req: Request, _: None = Depends(auth_middleware)):
    user: User = req.state.user

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")


def is_manager(
    req: Request,
    _: None = Depends(auth_middleware),
    employees_service: EmployeesService = Depends(get_employees_service)
):
    user: User = req.state.user

    if user.is_admin:
        return 
    
    else:
        employee_resource: Employee = employees_service.resource(
            key="user_id",
            value=user.user_id
        )

        if not employee_resource.is_manager:
            raise HTTPException(status_code=403, detail="Forbidden")
        

def token_is_company_stamped(
    req: Request,
    _: None = Depends(auth_middleware),
    companies_service: CompaniesService = Depends(get_companies_service)
):
    company_id = getattr(req.state, "company_id", None)

    if not company_id:
        raise HTTPException(status_code=403, detail="Invalid credential")
    else:
        company_resource: Company = companies_service.resource(
            key="company_id",
            value=company_id
        )

        RequestValidationService.verify_resource(
            result=company_resource,
            status_code=404,
            not_found_message="Company not found"
        )

    req.state.company = company_resource