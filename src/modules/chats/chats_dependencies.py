from src.core.dependencies.container import Container
from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_controller import ChatsController
from src.modules.chats.chats_models import Chat
from src.core.repository.base_repository import BaseRepository
from src.core.services.http_service import HttpService
from src.modules.chats.participants.participants_service import ParticipantsService
from src.modules.chats.participants.participants_models import Participant


def configure_chats_dependencies(http_service: HttpService) -> None:
    repository = BaseRepository(Chat)
    service = ChatsService(repository=repository)
    participants_service = ParticipantsService(
        repository=BaseRepository(Participant)
    )
    controller = ChatsController(http_service=http_service, chats_service=service, participants_service=participants_service)

    Container.register("chats_service", service)
    Container.register("chats_controller", controller)