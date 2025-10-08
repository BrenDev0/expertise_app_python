import uuid
from fastapi import HTTPException, Request
from typing import Any, Union
from src.modules.companies.domain.enitities import Company
from sqlalchemy.orm import Session
from uuid import UUID


class RequestValidationService:
    @classmethod
    def validate_uuid(cls, uuid_str: str):
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid id")

    @classmethod  
    def verify_resource(
        cls,
        result: Any,
        not_found_message: str = "Resource not found" ,
        status_code: int = 404,
        throw_http_error: bool = True
    ):
        if result is None and throw_http_error:
            raise HTTPException(status_code=status_code, detail=not_found_message)

    
    @classmethod
    def verifiy_ownership(cls, id: Union[str, UUID], resource_id: Union[str, UUID]):
        if str(id) != str(resource_id):
            raise HTTPException(status_code=403, detail="Forbidden")
