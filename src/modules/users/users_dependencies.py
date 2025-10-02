from src.core.services.http_service import HttpService
from src.core.services.data_handling_service import DataHandlingService
from src.core.dependencies.container import Container

from src.modules.users.users_controller import UsersController 
from src.modules.users.users_service import UsersService
from src.modules.users.users_models import User
from src.modules.users.users_repository import UsersRepository


def configure_users_dependencies(http_service: HttpService, data_handling_service: DataHandlingService):
    repository = UsersRepository()
    service = UsersService(
        respository=repository,
        data_hanlder=data_handling_service
    )

    controller = UsersController(
        http_service=http_service,
        users_service=service
    )

    Container.register("users_service", service)
    Container.register("users_controller", controller)

