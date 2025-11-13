from uuid import UUID
import logging
logger = logging.getLogger(__name__)

from src.core.domain.repositories.vector_respository import VectorRepository
from src.core.domain.services.embedding_service import EmbeddingService

class ChatContextService():
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_repository: VectorRepository
    ):
        self.__embedding_service = embedding_service
        self.__vector_repository = vector_repository
        self.__name_space = "expertise_user_context_"

    async def add_context(
        self,
        file_bytes: bytes,
        filename: str,
        chat_id: UUID
    ):
        embedding_result = await self.__embedding_service.embed_document(
                file_bytes=file_bytes,
                filename=filename,
                chat_id=str(chat_id)
            )

        namespace = f"{self.__name_space}{chat_id}"
        
        result = self.__vector_repository.store_embeddings(
            embeddings=embedding_result.embeddings,
            chunks=embedding_result.chunks,
            namespace=namespace,
            # Additional metadata
            filename=filename
        )
        
        logger.info(f"Stored {len(embedding_result.chunks)} chunks in Qdrant")
        logger.info(f"Result: {result}")

    
    def remove_context(
        self,
        chat_id: UUID,
        filename
    ):
        
        namespace = f"{self.__name_space}{chat_id}"
        results = self.__vector_repository.delete_embeddings(
            namespace=namespace,
            filename=filename
        )
        logger.debug(results)

    
    