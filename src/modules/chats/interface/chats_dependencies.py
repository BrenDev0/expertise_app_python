from fastapi import Depends

from src.core.domain.repositories.data_repository import DataRepository
from src.modules.chats.infrastructure.sqlalchemy_chats_repository import SqlAchemyChatsRepsitory
from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.services.embedding_service import EmbeddingService
from src.core.infrastructure.repositories.vector.redis_vector_repository import RedisVectorRepository, get_redis_client

from src.modules.chats.application.chats_service import ChatsService
from src.modules.chats.application.chat_context_service import ChatContextService
from src.modules.chats.interface.chats_controller import ChatsController
from src.modules.documents.interface.documents_dependencies import get_embedding_service


def get_context_vector_repository(
    client = Depends(get_redis_client)
) -> VectorRepository:
    return RedisVectorRepository(client=client)

def get_chats_repository() -> DataRepository:
    return SqlAchemyChatsRepsitory()

def get_chats_service(
    repository: DataRepository = Depends(get_chats_repository)
) -> ChatsService:
    return ChatsService(
        repository=repository
    )

def get_chat_context_service(
    verctor_repository: VectorRepository = Depends(get_context_vector_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> ChatContextService:
    return ChatContextService(
        embedding_service=embedding_service,
        vector_repository=verctor_repository
    )

def get_chats_controller(
    service: ChatsService = Depends(get_chats_service),
    chat_context_service: ChatContextService = Depends(get_chat_context_service)
) -> ChatsController:
    return ChatsController(
        chats_service=service,
        chat_context_service=chat_context_service
    )