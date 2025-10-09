from uuid import UUID

from src.modules.employees.application.employees_service import EmployeesService
from src.modules.users.application.users_service import UsersService

class DeleteEmployeeAccounts():
    def __init__(
        self,
        employees_service: EmployeesService,
        users_service: UsersService
    ):
        self.__employees_service = employees_service
        self.__users_service = users_service

    def execute(
        self,
        company_id: UUID
    ):
        employees = self.__employees_service.collection(company_id=company_id)
        employee_account_ids = [employee.user_id for employee in employees] 

        if len(employee_account_ids) != 0:
            self.__users_service.bulk_delete(ids=employee_account_ids)