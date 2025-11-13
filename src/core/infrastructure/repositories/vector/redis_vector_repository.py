# src/core/infrastructure/repositories/vector/redis_vector_repository.py
import json
import numpy as np
from redis import Redis
from typing import Dict, List, Any
from uuid import uuid4
import os
import logging
logger = logging.getLogger(__name__)

from src.core.domain.repositories.vector_respository import VectorRepository

def get_redis_client() -> Redis:
    return Redis.from_url(url=os.getenv("REDIS_URL"))

class RedisVectorRepository(VectorRepository):
    def __init__(self, client: Redis):
        super().__init__()
        self.__client = client

    def store_embeddings(
        self, 
        embeddings: List[List[float]], 
        chunks: List[Any], 
        namespace: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Simple storage without RediSearch - just for chat context"""
        try:
            stored_count = 0
            
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                # Create simple key for chat context
                chunk_id = chunk.chunk_id or str(uuid4())
                doc_key = f"chat_context:{namespace}:{chunk_id}"
                
                # Store as JSON with embedding
                doc_data = {
                    "content": chunk.content,
                    "embedding": embedding,  # Store as list, not bytes
                    "chat_id": str(kwargs.get("chat_id", "")),
                    "filename": kwargs.get("filename", ""),
                    "chunk_index": i,
                    "chunk_id": chunk_id,
                    "metadata": getattr(chunk, 'metadata', {})
                }
                
                # Store as JSON string with 2-minute TTL
                self.__client.setex(
                    doc_key, 
                    120,  # 2 minutes TTL
                    json.dumps(doc_data)
                )
                stored_count += 1
            
            return {
                "status": "success",
                "chunks_processed": stored_count,
                "namespace": namespace
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to store embeddings: {str(e)}"
            }

    def delete_embeddings(self, namespace: str, **filters) -> Dict[str, Any]:
        """Delete embeddings by chat_id or other filters"""
        try:
            pattern = f"chat_context:{namespace}:*"
            keys = self.__client.keys(pattern)
            
            deleted_count = 0
            for key in keys:
                try:
                    data_json = self.__client.get(key)
                    if data_json:
                        data = json.loads(data_json)
                        
                        # Check if matches filters
                        should_delete = True
                        for filter_key, filter_value in filters.items():
                            if data.get(filter_key) != filter_value:
                                should_delete = False
                                break
                        
                        if should_delete:
                            self.__client.delete(key)
                            deleted_count += 1
                            
                except Exception as e:
                    logger.error(f"Error processing key {key}: {e}")
                    continue
            
            return {
                "status": "success",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Delete failed: {str(e)}"
            }

    def delete_namespace(self, namespace: str) -> Dict[str, Any]:
        """Delete all embeddings in a namespace"""
        try:
            pattern = f"chat_context:{namespace}:*"
            keys = self.__client.keys(pattern)
            
            if keys:
                self.__client.delete(*keys)
            
            return {
                "status": "success",
                "message": f"Deleted {len(keys)} embeddings from namespace {namespace}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete namespace: {str(e)}"
            }

    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all user chat contexts"""
        try:
            pattern = f"chat_context:*{user_id}*"
            keys = self.__client.keys(pattern)
            
            if keys:
                self.__client.delete(*keys)
            
            return {
                "status": "success",
                "deleted_count": len(keys)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete user data: {str(e)}"
            }

    def get_collection_info(self, namespace: str) -> Dict[str, Any]:
        """Get info about stored embeddings"""
        try:
            pattern = f"chat_context:{namespace}:*"
            keys = self.__client.keys(pattern)
            
            return {
                "status": "success",
                "info": {
                    "total_documents": len(keys),
                    "namespace": namespace
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }