from src.core.services.http_service import HttpService
from src.modules.employees.employees_models import Employee, EmployeeCreate, EmployeeUpdate, EmplyeePublic
from src.modules.employees.employees_service import EmployeesService
from src.modules.users.users_service import UsersService
from src.modules.users.users_models import User
from src.modules.companies.companies_models import Company
from fastapi  import Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

class EmployeesController:
    def __init__(self, http_service: HttpService, employees_service: EmployeesService):
        self.__http_service = http_service
        self.__employees_service = employees_service

    def create_request(
        self,
        company_id: UUID,
        req: Request,
        data: EmployeeCreate,
        db: Session
    ):
        user: User = req.state.user

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        