from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.modules.chats.participants.participants_service import ParticipantsService
from src.modules.chats.participants.participants_controller import ParticipantsController
from src.modules.chats.participants.participants_repository import ParticipantsRepository



def configure_participants_dependencies(http_service: HttpService):
    repository = ParticipantsRepository()
    service = ParticipantsService(
        repository=repository
    )
    controller = ParticipantsController(
        http_service=http_service,
        participants_service=service
    )

    Container.register("participants_service", service)
    Container.register("participant_controller", controller)