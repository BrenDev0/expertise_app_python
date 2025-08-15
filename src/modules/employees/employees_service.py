from src.modules.employees.employees_repository import EmployeesRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.modules.employees.employees_models import Employee, EmployeeCreate, EmployeeUpdate
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List


class EmployeesService:
    __MODULE = "employees.service"
    def __init__(self, repository: EmployeesRepository):
        self.__repository = repository


    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, db: Session, user_id: UUID, company_id: UUID, position: str) -> Employee:
        employee = Employee(
            user_id=user_id,
            company_id=company_id,
            postiion=position
        )

        return self.__repository.create(db=db, data=employee)
     
    @service_error_handler(module=f"{__MODULE}.resource_by_user_and_company")
    def resource_by_user_and_company(self, db: Session, company_id: UUID, user_id: UUID) -> Employee | None:
        return self.__repository.get_by_user_and_company(db=db, user_id=user_id, company_id=company_id)
    
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, db: Session, employee_id: UUID) -> Employee | None:
        return self.__repository.get_one(db=db, key="employee_id", value=employee_id)
    

    @service_error_handler(module=f"{__MODULE}.collection")
    def collection(self, db: Session, company_id: UUID) -> List[Employee]:
        return self.__repository.get_many(db=db, key="company_id", value=company_id)
    

    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, employee_id: UUID, changes: EmployeeUpdate) -> Employee:
        return self.__repository.update(
            db=db, key="employee_id", 
            value=employee_id, 
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=f"{__MODULE}.delete")
    def delete(self, db: Session, employee_id: UUID) -> Employee:
        return self.__repository.delete(db=db, key="employee_id", value=employee_id)