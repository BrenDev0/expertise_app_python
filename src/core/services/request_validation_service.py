import uuid
from fastapi import HTTPException
from typing import List, Dict, Any
from src.core.dependencies.container import Container
from src.modules.companies.companies_models import Company
from sqlalchemy.orm import Session
from uuid import UUID
from src.modules.users.users_models import User
from src.modules.employees.employees_models import Employee
from src.modules.employees.employees_service import EmployeesService

class RequestValidationService:
    @staticmethod
    def validate_uuid(uuid_str: str):
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid id")

    @staticmethod   
    def verify_resource(
        service_key: str,
        params: Dict[str, Any],
        not_found_message: str = "Resource not found" ,
        status_code: int = 404
    ):
        service = Container.resolve(service_key)

        result = service.resource(**params)

        if result is None:
            raise HTTPException(status_code=status_code, detail=not_found_message)
        
        return result
    
    @staticmethod
    def validate_action_authorization(id: UUID | str | int, resource_id: UUID | str | int):
        if id != resource_id:
            raise HTTPException(status_code=403, detail="Forbidden")
    
       
    def verify_company_user_relation(
        self,
        db: Session,
        user: User,
        company_id: UUID
    ) -> None:
        if user.is_admin:
            company_resource: Company = self.verify_resource(
                service_key="companies_service",
                params={
                    "db": db,
                    "company_id": company_id
                },
                not_found_message="Company not found"
            )

            self.validate_action_authorization(user.user_id, company_resource.user_id)
            return 
        
        employees_service: EmployeesService = Container.resolve(employees_service)
        manager: Employee = employees_service.resource_by_user_and_company(
            db=db,
            company_id=company_id,
            user_id=user.user_id
        )

        if not manager or manager.position != "manager":
            raise HTTPException(status_code=403, detail="Forbidden")