from fastapi import UploadFile
import io
import pandas as pd
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from src.core.decorators.service_error_handler import service_error_handler
import os
import uuid
from typing import Dict, Any
import PyPDF2

class EmbeddingService:
    __MODULE = "embeddings.service"
    
    def __init__(self, client: QdrantClient):
        self.__client = client
        
        self.__embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.__text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    @service_error_handler(__MODULE)
    def get_collection_name(self, user_id: str, company_id: str) -> str:
        return f"user_{user_id}_company_{company_id}"
    
    @service_error_handler(__MODULE)
    def ensure_collection_exists(self, user_id: str, company_id: str) -> None:
        collection_name = self.get_collection_name(user_id, company_id)
        
        try:
            self.__client.get_collection(collection_name)
        except Exception:
            self.__client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )

            self.__client.create_payload_index(collection_name=collection_name, field_name="filename", field_schema="keyword")
            self.__client.create_payload_index(collection_name=collection_name, field_name="user_id", field_schema="keyword")
            self.__client.create_payload_index(collection_name=collection_name, field_name="agent_id", field_schema="keyword")

    @service_error_handler(__MODULE)
    async def add_document(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        company_id: str
    ) -> Dict[str, Any]:
        self.ensure_collection_exists(user_id, company_id)
        collection_name = self.get_collection_name(user_id, company_id)

        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            documents = [Document(page_content=text)]
        elif filename.endswith('.txt'):
            text = file_bytes.decode("utf-8")
            documents = [Document(page_content=text)]
        elif filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
            documents = [
                Document(page_content=row.to_json(), metadata={"row_index": idx})
                for idx, row in df.iterrows()
            ]
        else:
            raise ValueError(f"Unsupported file type: {filename}")

        chunks = self.__text_splitter.split_documents(documents)
        texts = [chunk.page_content for chunk in chunks]
        embeddings = await self.__embedding_model.aembed_documents(texts)

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append({
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "text": chunk.page_content,
                    "filename": filename,
                    "user_id": user_id,
                    "company_id": company_id
                }
            })

        batch_size = 50
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.__client.upsert(collection_name=collection_name, points=batch)

        return {
            "status": "success",
            "chunks_processed": len(points),
            "collection": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_document_data(self, user_id: str, company_id: str, filename: str) -> Dict[str, Any]:
        """Delete all embeddings for a specific document"""
        collection_name = self.get_collection_name(user_id, company_id)
        
        points_filter = Filter(
            must=[
                FieldCondition(key="filename", match=MatchValue(value=filename)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="company_id", match=MatchValue(value=company_id))
            ]
        )
        
        result = self.__client.delete(
            collection_name=collection_name,
            points_selector=points_filter
        )
        
        return {
            "status": "success",
            "operation": "delete_document",
            "filename": filename,
            "collection": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_company_data(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """Delete entire collection for a company (all documents)"""
        collection_name = self.get_collection_name(user_id, company_id)
        
        self.__client.delete_collection(collection_name)
        return {
            "status": "success",
            "operation": "delete_company",
            "collection_deleted": collection_name
        }

    @service_error_handler(__MODULE)
    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all collections for a user (across all companies)"""
        collections = self.__client.get_collections()
        user_prefix = f"user_{user_id}_company_"
        deleted_collections = []
        
        for collection in collections.collections:
            if collection.name.startswith(user_prefix):
                self.__client.delete_collection(collection.name)
                deleted_collections.append(collection.name)
        
        return {
            "status": "success",
            "operation": "delete_user",
            "collections_deleted": deleted_collections,
            "count": len(deleted_collections)
        }