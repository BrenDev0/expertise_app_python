# middleware/auth_middleware.py
from fastapi import Request, Depends
from src.core.dependencies.container import Container
from src.core.middleware.middleware_service import MiddlewareService
from   src.core.database.session import get_db_session
from sqlalchemy.orm import Session


async def auth_middleware(request: Request, db: Session = Depends(get_db_session)):
    middleware_service: MiddlewareService = Container.resolve("middleware_service")
    user, token_payload = middleware_service.auth(request=request, db=db)

    request.state.user = user
   
    return user
    
