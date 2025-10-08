from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.core.domain.repositories.data_repository import DataRepository
from src.core.utils.decorators.service_error_handler import service_error_handler
from src.core.dependencies.container import Container

from src.modules.users.application.users_service import UsersService
from src.modules.employees.employees_service import EmployeesService
from src.modules.companies.domain.companies_models import CompanyCreate, CompanyUpdate
from src.modules.companies.domain.enitities import Company


class CompaniesService:
    __MODULE = "companies.service"
    def __init__(self, respository: DataRepository):
        self.__repository = respository
    
    @service_error_handler(module=__MODULE)
    def create(self, db: Session, data: CompanyCreate, user_id: UUID) -> Company: 
        new_company = Company(
            **data.model_dump(by_alias=False),
            user_id=user_id
        )

        return self.__repository.create(db=db, data=new_company)
    
    @service_error_handler(module=__MODULE)
    def resource(self, key: str, value: UUID | str) -> Company | None:
        return self.__repository.get_one(key="company_id", value=value)
    

    @service_error_handler(module=__MODULE)
    def collection(self, user_id: UUID) -> List[Company]:
        return self.__repository.get_many(key="user_id", value=user_id)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, company_id: UUID, changes: CompanyUpdate) -> Company:
        return self.__repository.update(
            key="company_id",
            value=company_id,
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=__MODULE)
    def delete(self, db: Session, company_id: UUID) -> Company:
        ## delete users accounts of the employees
        self.delete_employee_data(db=db, company_id=company_id)
        return self.__repository.delete(key="company_id", value=company_id)
    
    @service_error_handler(module=__MODULE)
    def delete_employee_data(self, db: Session, company_id: UUID):
        employees_service: EmployeesService = Container.resolve("employees_service")

        employees = employees_service.collection(db=db, company_id=company_id)
        employee_account_ids = [employee.user_id for employee in employees] 

        if len(employee_account_ids) != 0:
            users_service: UsersService = Container.resolve("users_service")
            users_service.bulk_delete(db=db, ids=employee_account_ids)