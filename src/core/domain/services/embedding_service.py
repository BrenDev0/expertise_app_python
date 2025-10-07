from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict, List, Any


class DocumentChunk(BaseModel):
    content: str
    metadata: Dict[str, Any]
    chunk_id: str


class EmbeddingResult(BaseModel):
    chunks: List[DocumentChunk]
    embeddings: List[List[float]]
    total_tokens: int

class EmbeddingService(ABC):
    @abstractmethod
    async def embed_document(
        self,
        file_bytes: bytes,
        filename: str,
        **kwargs
    ) -> EmbeddingResult:
        raise NotImplementedError
    
    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        raise NotImplementedError
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        raise NotImplementedError