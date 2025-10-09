from typing import List
from uuid import UUID
from fastapi import Request

from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.services.encryption_service import EncryptionService
from src.core.services.webtoken_service import WebTokenService

from src.modules.employees.domain.employees_models import EmployeeCreate, EmployeeUpdate, EmployeePublic, EmployeeUser
from src.modules.employees.domain.entities import Employee
from src.modules.employees.application.employees_service import EmployeesService
from src.modules.users.application.users_service import UsersService
from src.modules.invites.application.invites_service import InvitesService
from src.modules.users.domain.entities import User
from src.modules.companies.domain.enitities import Company
from src.modules.invites.domain.entities import Invite

from src.core.services.request_validation_service import RequestValidationService

class EmployeesController:
    def __init__(self, 
        encryption_service: EncryptionService, 
        employees_service: EmployeesService, 
        users_service: UsersService,
        invites_service: InvitesService
    ):
        self.__encryption_service = encryption_service
        self.__employees_service = employees_service
        self.__users_service = users_service
        self.__invites_service = invites_service

    def create_request(
        self,
        req: Request,
        data: EmployeeCreate,
        web_token_service: WebTokenService
    ) -> ResponseWithToken:
        invite_id = req.state.verification_code

        invitation_resource: Invite = self.__invites_service.resource(
            invite_id=invite_id
        )

        RequestValidationService.verify_resource(
            result=invitation_resource,
            not_found_message="Invite not found"
        )

        user_data = self.__invites_service.extract_user_data_from_invite(data=invitation_resource, password=data.password)
        self.__invites_service.delete(invite_id=invitation_resource.invite_id)

        new_user = self.__users_service.create(data=user_data)

        self.__employees_service.create(
            user_id=new_user.user_id, 
            company_id=invitation_resource.company_id, 
            position=invitation_resource.position,
            is_manager=invitation_resource.is_manager
        )

        token_payload = {
            "user_id": str(new_user.user_id), 
            "company_id": str(invitation_resource.company_id)
        }

        token = web_token_service.generate_token(token_payload, "7d")

        return ResponseWithToken(
            detail="Employee created",
            token=token,
            company_id=str(invitation_resource.company_id)
        )
    

    def resource_request(
        self,
        req: Request,
    ) -> EmployeePublic:
        user: User = req.state.user
        company: Company = req.state.company

        employee_resource: Employee = self.__employees_service.resource(
            key="user_id",
            value=user.user_id
        )
        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

        
        return self.__to_public(employee_resource)


    def collection_request(
        self,
        req: Request,
    ) -> List[EmployeePublic]:
        company: Company = req.state.company

        data = self.__employees_service.collection(company_id=company.company_id)

        return [
            self.__to_public(employee) for employee in data
        ]
    
    def update_request(
        self,
        employee_id: UUID,
        req: Request,
        data: EmployeeUpdate,
    ) -> EmployeePublic:
        company: Company = self.__http_service.request_validation_service.verify_company_in_request_state(req=req,)

        employee_resource: Employee = self.__employees_service.resource(
            key="employee_id",
            value=employee_id
        )

        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

        updated_emplooyee = self.__employees_service.update(employee_id=employee_resource.employee_id, changes=data)

        return self.__to_public(updated_emplooyee)
    


    def delete_request(
        self, 
        employee_id: UUID,
        req: Request
    ):
        company: Company = req.state.company

        employee_resource: Employee = self.__employees_service.resource(
            key="employee_id",
            value=employee_id
        )

        RequestValidationService.verify_resource(
            result=employee_resource,
            not_found_message="Employee not found"
        )

        RequestValidationService.verifiy_ownership(company.company_id, employee_resource.company_id)

       
        self.__users_service.delete(user_id=employee_resource.user_id)  ## will delete employee by Cascade

        return CommonHttpResponse(
            detail="Employee deleted"
        )

    def __to_public(self, data: Employee) -> EmployeePublic:
        user_public = EmployeeUser(
            user_id=str(data.user.user_id),
            name=self.__encryption_service.decrypt(data.user.name),
            email=self.__encryption_service.decrypt(data.user.email),
            phone=self.__encryption_service.decrypt(data.user.phone)
        )

        employee_public = EmployeePublic(
            employee_id=data.employee_id,
            company_id=data.company_id,
            position=data.position,
            is_manager=data.is_manager,
            user=user_public
        )
    
        return employee_public

        


    








        

        