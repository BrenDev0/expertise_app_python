from fastapi import Depends

from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.modules.employees.employees_repository import EmployeesRepository
from src.modules.employees.employees_models import Employee
from src.modules.employees.employees_service import EmployeesService
from src.modules.employees.employee_controller import EmployeesController
from src.modules.invites.invites_service import InvitesService
from src.modules.users.application.users_service import UsersService
from src.core.services.encryption_service import EncryptionService

from src.modules.users.users_dependencies import get_users_service
from src.modules.invites.invites_dependencies import get_invites_service
from src.core.dependencies.services import get_encryption_service

def configure_employee_dependencies(http_service: HttpService):
    repository = EmployeesRepository()
    service = EmployeesService(
        repository=repository
    )

    user_service: UsersService = Container.resolve("users_service")
    invites_service: InvitesService = Container.resolve("invites_service")
   
    controller = EmployeesController(
        employees_service=service,
        users_service=user_service,
        invites_service=invites_service
    )

    Container.register("employees_service", service)
    Container.register("employees_controller", controller)

def get_employees_repository() -> EmployeesRepository:
    return EmployeesRepository()

def get_employees_service(
    repository: EmployeesRepository = Depends(get_employees_repository)
) -> EmployeesService:
    return EmployeesService(

    )

def get_employees_controller(
    employees_service: EmployeesService = Depends(get_employees_service),
    users_service: UsersService = Depends(get_users_service),
    invites_service: InvitesService = Depends(get_invites_service),
    encryption_service: EncryptionService = Depends(get_encryption_service)
) -> EmployeesController:
    return EmployeesController(
        employees_service=employees_service,
        users_service=users_service,
        invites_service=invites_service,
        encryption_service=encryption_service
    )