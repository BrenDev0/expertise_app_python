from src.core.services.http_service import HttpService
from src.modules.employees.employees_models import Employee, EmployeeCreate, EmployeeUpdate, EmployeePublic, EmployeeUser
from src.modules.employees.employees_service import EmployeesService
from src.modules.users.users_service import UsersService
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
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
    ) -> ResponseWithToken:
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
        self.__invites_service.delete(db=db, invite_id=invitation_resource.invite_id)

        new_user = self.__users_service.create(db=db, data=user_data)

        self.__employees_service.create(
            db=db, 
            user_id=new_user.user_id, 
            company_id=invitation_resource.company_id, 
            position=invitation_resource.position,
            is_manager=invitation_resource.is_manager
        )

        token_payload = {
            "user_id": str(new_user.user_id), 
            "company_id": str(invitation_resource.company_id)
        }

        token = self.__http_service.webtoken_service.generate_token(token_payload, "7d")

        return ResponseWithToken(
            detail="Employee created",
            token=token,
            company_id=str(invitation_resource.company_id)
        )
    

    def resource_request(
        self,
        employee_id: UUID,
        req: Request,
        db: Session
    ) -> EmployeePublic:
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service", # employee_service.resource accepts key value parameters
            params={
                "db": db,
                "key": "employee_id",
                "value": employee_id
            },
            not_found_message="Employee not found"
        )

        
        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

        
        return self.__to_public(employee_resource)


    def collection_request(
        self,
        req: Request,
        db: Session,
    ) -> List[EmployeePublic]:
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        company_resource: Company = self.__http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        data = self.__employees_service.collection(db=db, company_id=company_resource.company_id)

        return [
            self.__to_public(employee) for employee in data
        ]
    
    def update_request(
        self,
        employee_id: UUID,
        req: Request,
        data: EmployeeUpdate,
        db: Session
    ) -> CommonHttpResponse:
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "key": "employee_id",
                "value": employee_id
            },
            not_found_message="Employee not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

        self.__employees_service.update(db=db, employee_id=employee_resource.employee_id, changes=data)

        return CommonHttpResponse(
            detail="Employee updated"
        ) 
    


    def delete_request(
        self, 
        employee_id: UUID,
        req: Request,
        db: Session
    ):
        company_id = self.__http_service.request_validation_service.verify_company_in_request_state(req=req)

        employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "key": "employee_id",
                "value": employee_id
            },
            not_found_message="Employee not found"
        )

        self.__http_service.request_validation_service.validate_action_authorization(company_id, employee_resource.company_id)

       
        self.__users_service.delete(db=db, user_id=employee_resource.user_id)  ## will delete employee by Cascade

        return CommonHttpResponse(
            detail="Employee deleted"
        )

    def __to_public(self, data: Employee) -> EmployeePublic:
        user_public = EmployeeUser(
            user_id=str(data.user.user_id),
            name=self.__http_service.encryption_service.decrypt(data.user.name),
            email=self.__http_service.encryption_service.decrypt(data.user.email),
            phone=self.__http_service.encryption_service.decrypt(data.user.phone)
        )

        employee_public = EmployeePublic(
            employee_id=data.employee_id,
            company_id=data.company_id,
            position=data.position,
            is_manager=data.is_manager,
            user=user_public
        )
    
        return employee_public

        


    








        

        