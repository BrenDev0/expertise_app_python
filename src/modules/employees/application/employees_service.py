from uuid import UUID
from typing import List

from src.core.domain.repositories.data_repository import DataRepository
from src.core.utils.decorators.service_error_handler import service_error_handler
from src.modules.employees.domain.employees_models import EmployeeUpdate
from src.modules.employees.domain.entities import Employee



class EmployeesService:
    __MODULE = "employees.service"
    def __init__(self, repository: DataRepository):
        self.__repository = repository


    @service_error_handler(module=f"{__MODULE}.create")
    def create(self, user_id: UUID, company_id: UUID, position: str, is_manager: bool = False) -> Employee:
        employee = Employee(
            user_id=user_id,
            company_id=company_id,
            position=position,
            is_manager=is_manager
        )

        return self.__repository.create(data=employee)
     
    @service_error_handler(module=f"{__MODULE}.resource")
    def resource(self, key: str, value: UUID) -> Employee | None:
        return self.__repository.get_one(key=key, value=value)
    

    @service_error_handler(module=f"{__MODULE}.collection")
    def collection(self, company_id: UUID) -> List[Employee]:
        return self.__repository.get_many(key="company_id", value=company_id)
    

    @service_error_handler(module=f"{__MODULE}.update")
    def update(self, employee_id: UUID, changes: EmployeeUpdate) -> Employee:
        return self.__repository.update(
            key="employee_id", 
            value=employee_id, 
            changes=changes.model_dump(by_alias=False, exclude_unset=True)
        )