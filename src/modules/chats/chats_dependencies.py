from fastapi import Depends

from src.core.dependencies.container import Container
from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_controller import ChatsController
from src.modules.chats.chats_models import Chat
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService

from src.modules.chats.messages.messages_dependencies import configure_messages_dependencies

def configure_chats_dependencies(http_service: HttpService) -> None:

    ## configure sub modules
    configure_messages_dependencies(http_service=http_service)


    repository = BaseRepository(Chat)
    service = ChatsService(repository=repository)
    controller = ChatsController(chats_service=service)

    Container.register("chats_service", service)
    Container.register("chats_controller", controller)

def get_chats_repository() -> BaseRepository:
    return BaseRepository(Chat)

def get_chats_service(
    repository: BaseRepository = Depends(get_chats_repository)
) -> ChatsService:
    return ChatsService(
        repository=repository
    )

def get_chats_controller(
    service: ChatsService = Depends(get_chats_service)
) -> ChatsController:
    return ChatsController(
        chats_service=service
    )