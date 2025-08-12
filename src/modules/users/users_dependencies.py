from src.core.services.http_service import HttpService
from src.core.services.data_handling_service import DataHandlingService
from src.core.logs.logger import Logger
from src.core.repository.base_repository import BaseRepository
from src.modules.users.users_controller import UsersController 
from src.modules.users.users_service import UsersService
from src.modules.users.users_models import User
from src.core.dependencies.container import Container

def configure_users_dependencies(logger: Logger, http_service: HttpService, data_handling_service: DataHandlingService):
    repository = BaseRepository(User)
    service = UsersService(
        respository=repository,
        data_hanlder=data_handling_service,
        logger=logger
    )

    controller = UsersController(
        http_service=http_service,
        users_service=service
    )

    Container.register("users_service", service)
    Container.register("users_controller", controller)

