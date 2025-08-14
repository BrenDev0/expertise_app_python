from src.modules.employees.employees_repository import EmployeesRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.modules.employees.employees_models import Employee, EmployeeCreate, EmployeeUpdate
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List


class EmployeesService:
    def __init__(self, repository: EmployeesRepository):
        self.__repository = repository

    def create(self, db: Session, data: EmployeeCreate, user_id: UUID, company_id: UUID) -> Employee:
        employee = Employee(
            **data.model_dump(by_alias=False),
            user_id=user_id,
            company_id=company_id
        )

        return self.__repository.create(db=db, data=employee)
    

    def resource_by_user_and_company(self, db: Session, company_id: UUID, user_id: UUID) -> Employee | None:
        return self.__repository.get_by_user_and_company(db=db, user_id=user_id, company_id=company_id)
    
    def resource(self, db: Session, employee_id: UUID) -> Employee | None:
        return self.__repository.get_one(db=db, key="employee_id", value=employee_id)
    
    def collection(self, db: Session, company_id: UUID) -> List[Employee]:
        return self.__repository.get_many(db=db, key="company_id", value=company_id)
    
    def update(self, db: Session, employee_id: UUID, changes: EmployeeUpdate) -> Employee:
        return self.__repository.update(
            db=db, key="employee_id", 
            value=employee_id, 
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    def delete(self, db: Session, employee_id: UUID) -> Employee:
        return self.__repository.delete(db=db, key="employee_id", value=employee_id)