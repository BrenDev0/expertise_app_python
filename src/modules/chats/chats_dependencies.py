from src.core.dependencies.container import Container
from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_controller import ChatsController
from src.modules.chats.chats_models import Chat
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService

from src.modules.chats.messages.messages_dependencies import configure_messages_dependencies
from src.modules.chats.participants.participants_dependencias import configure_participants_dependencies


def configure_chats_dependencies(http_service: HttpService) -> None:

    ## configure sub modules
    configure_participants_dependencies(http_service=http_service)
    configure_messages_dependencies(http_service=http_service)


    repository = BaseRepository(Chat)
    service = ChatsService(repository=repository)
    participants_service = Container.resolve("participants_service")
    controller = ChatsController(http_service=http_service, chats_service=service, participants_service=participants_service)

    Container.register("chats_service", service)
    Container.register("chats_controller", controller)