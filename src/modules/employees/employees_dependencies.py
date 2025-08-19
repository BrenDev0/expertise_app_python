from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.modules.employees.employees_repository import EmployeesRepository
from src.modules.employees.employees_models import Employee
from src.modules.employees.employees_service import EmployeesService
from src.modules.employees.employee_controller import EmployeesController
from src.modules.invites.invites_service import InvitesService
from src.modules.users.users_service import UsersService

def configure_employee_dependencies(http_service: HttpService):
    repository = EmployeesRepository()
    service = EmployeesService(
        repository=repository
    )

    user_service: UsersService = Container.resolve("users_service")
    invites_service: InvitesService = Container.resolve("invites_service")
   
    controller = EmployeesController(
        http_service=http_service,
        employees_service=service,
        users_service=user_service,
        invites_service=invites_service
    )

    Container.register("employees_service", service)
    Container.register("employees_controller", controller)