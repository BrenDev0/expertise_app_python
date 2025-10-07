from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService

from src.modules.chats.messages.messages_repository import MessagesRepository
from src.modules.chats.messages.messages_service import MessagesService
from src.modules.chats.messages.messages_controller import MessagesController


def configure_messages_dependencies(http_service: HttpService):
    repository = MessagesRepository()
    service = MessagesService(repository=repository)
    controller = MessagesController(http_service=http_service, messages_service=service)
    Container.register("messages_service", service)
    Container.register("messages_controller", controller) 