from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.core.repository.base_repository import BaseRepository
from src.core.decorators.service_error_handler import service_error_handler
from src.core.dependencies.container import Container

from src.modules.users.users_service import UsersService
from src.modules.employees.employees_service import EmployeesService
from src.modules.companies.companies_models import Company, CompanyCreate, CompanyUpdate



class CompaniesService:
    __MODULE = "companies.service"
    def __init__(self, respository: BaseRepository):
        self.__repository = respository
    
    @service_error_handler(module=__MODULE)
    def create(self, db: Session, data: CompanyCreate, user_id: UUID) -> Company: 
        new_company = Company(
            **data.model_dump(by_alias=False),
            user_id=user_id
        )

        return self.__repository.create(db=db, data=new_company)
    
    @service_error_handler(module=__MODULE)
    def resource(self, db: Session, company_id: UUID) -> Company | None:
        return self.__repository.get_one(db=db, key="company_id", value=company_id)
    

    @service_error_handler(module=__MODULE)
    def collection(self, db: Session, user_id: UUID) -> List[Company]:
        return self.__repository.get_many(db=db, key="user_id", value=user_id)
    
    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, db: Session, company_id: UUID, changes: CompanyUpdate) -> Company:
        return self.__repository.update(
            db=db,
            key="company_id",
            value=company_id,
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )
    
    @service_error_handler(module=__MODULE)
    def delete(self, db: Session, company_id: UUID) -> Company:
        ## delete users accounts of the employees
        self.delete_employee_data(db=db, company_id=company_id)
        return self.__repository.delete(db=db, key="company_id", value=company_id)
    
    @service_error_handler(module=__MODULE)
    def delete_employee_data(self, db: Session, company_id: UUID):
        employees_service: EmployeesService = Container.resolve("employees_service")

        employees = employees_service.collection(db=db, company_id=company_id)
        employee_account_ids = [employee.user_id for employee in employees] 

        if len(employee_account_ids) != 0:
            users_service: UsersService = Container.resolve("users_service")
            users_service.bulk_delete(db=db, ids=employee_account_ids)