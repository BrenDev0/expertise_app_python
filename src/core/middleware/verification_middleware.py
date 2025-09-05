# middleware/auth_middleware.py
from fastapi import Request, Depends
from src.core.dependencies.container import Container
from src.core.middleware.middleware_service import MiddlewareService
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session


def verification_middleware(request: Request, db: Session = Depends(get_db_session)):
    middleware_service: MiddlewareService = Container.resolve("middleware_service")
    verification_code, token_payload = middleware_service.verify(request)

    request.state.verification_code = verification_code
    
    user_id = token_payload.get("user_id")
    if user_id:
        user = middleware_service.authorize_user(db=db, token_payload=token_payload)

        request.state.user = user

    return verification_code
  
        