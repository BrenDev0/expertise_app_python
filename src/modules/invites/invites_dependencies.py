from fastapi import Depends

from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.modules.invites.invites_controller import InvitesController
from src.modules.invites.invites_service import InvitesService
from src.modules.invites.invites_models import Invite
from src.core.repository.base_repository import BaseRepository
from src.core.services.data_handling_service import DataHandlingService
from src.core.services.email_service import EmailService

def configure_invites_dependencies(http_service: HttpService, data_handler: DataHandlingService, email_service: EmailService):
    respository = BaseRepository(Invite)

    service = InvitesService(
        repository=respository,
        data_handler=data_handler
    )
    controller = InvitesController(
        http_service=http_service,
        invites_service=service,
        email_service=email_service
    )

    Container.register("invites_service", service)
    Container.register("invites_controller", controller)


def get_data_handler() -> DataHandlingService:
    return Container.resolve("data_handler")

def get_invites_repository() -> BaseRepository:
    return BaseRepository(Invite)

def get_invites_service(
    repository: BaseRepository = Depends(get_invites_repository),
    data_hanlder: DataHandlingService = Depends(get_data_handler)
) -> InvitesService:
    return InvitesService(
        repository=repository,
        data_handler=data_hanlder
    )