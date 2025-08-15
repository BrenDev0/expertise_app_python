from src.core.services.http_service import HttpService
from src.modules.employees.employees_models import Employee, EmployeeCreate, EmployeeUpdate, EmplyeePublic
from src.modules.employees.employees_service import EmployeesService
from src.modules.users.users_service import UsersService
from src.core.models.http_responses import CommonHttpResponse
from src.modules.invites.invites_service import InvitesService
from src.modules.users.users_models import User, UserCreate
from src.modules.companies.companies_models import Company
from src.modules.invites.invites_models import Invite
from fastapi  import Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

class EmployeesController:
    def __init__(self, 
        http_service: HttpService, 
        employees_service: EmployeesService, 
        users_service: UsersService,
        invites_service: InvitesService
    ):
        self.__http_service = http_service
        self.__employees_service = employees_service
        self.__users_service = users_service
        self.__invites_service = invites_service

    def create_request(
        self,
        req: Request,
        data: EmployeeCreate,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user
        invite_id = req.state.verification_code

        invitation_resource: Invite = self.__http_service.request_validation_service.verify_resource(
            service_key="invites_service",
            params={
                "db": db,
                "invite_id": invite_id
            },
            not_found_message="Expired",
            status_code=403
        )

        user_data = self.__invites_service.extract_user_data_from_invite(data=invitation_resource, password=data.password)

        new_user = self.__users_service.create(db=db, data=user_data)

        self.__employees_service.create(
            db=db, 
            user_id=new_user.user_id, 
            company_id=invitation_resource.company_id, 
            position=invitation_resource.position
        )

        return CommonHttpResponse
    

    def resource_request(
        self,
        employee_id: UUID,
        req: Request,
        db: Session
    ) -> EmplyeePublic:
        user: User = req.state.user

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "employee_id": employee_id
            },
            not_found_message="Employee not found"
        )

        if user.is_admin:
            self.__http_service.request_validation_service.verify_company_user_relation(db=db, user_id=user.user_id, company_id=employee_resource.company_id)
        else: 
           self.__verify_manager_company_relation(db=db, company_id=employee_resource.company_id, user_id=user.user_id)
        
        return self.__to_public(employee_resource)


    def __verify_manager_company_relation(
        self,
        db: Session,
        company_id: UUID,
        user_id: UUID
    ):

        manager = self.__employees_service.resource_by_user_and_company(
            db=db,
            company_id=company_id,
            user_id=user_id
        )

        if not manager:
            raise HTTPException(status_code=403, detail="Forbidden")
    
    
    def __to_public(data: Employee) -> EmplyeePublic:
        return EmplyeePublic.model_validate(data, from_attributes=True)

        


    








        

        