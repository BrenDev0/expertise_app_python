from fastapi import Depends

from src.core.domain.repositories.data_repository import DataRepository
from src.modules.employees.infrastructure.sqlalchemy_employees_repository import SqlAlchemyEmployeesRepository
from src.modules.employees.application.employees_service import EmployeesService
from src.modules.employees.interface.employee_controller import EmployeesController
from src.modules.invites.application.invites_service import InvitesService
from src.modules.users.application.users_service import UsersService
from src.core.services.encryption_service import EncryptionService

from src.modules.users.interface.users_dependencies import get_users_service
from src.modules.invites.interface.invites_dependencies import get_invites_service
from src.core.dependencies.services import get_encryption_service


def get_employees_repository() -> DataRepository:
    return SqlAlchemyEmployeesRepository()

def get_employees_service(
    repository: DataRepository = Depends(get_employees_repository)
) -> EmployeesService:
    return EmployeesService(
        repository=repository
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