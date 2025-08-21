from src.core.dependencies.container import Container
from src.core.logs.logger import Logger
from src.core.repository.base_repository import BaseRepository
from src.modules.chats.messages.messages_service import MessagesService
from src.modules.chats.messages.messages_models import Message
from src.modules.chats.messages.messages_controller import MessagesController
from src.core.services.http_service import HttpService

def configure_messages_dependencies(http_service: HttpService):
    repository = BaseRepository(Message)
    service = MessagesService(repository=repository)
    controller = MessagesController(http_service=http_service, messages_service=service)
    Container.register("messages_service", service)
    Container.register("messages_controller", controller) 