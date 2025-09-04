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

    company_id = token_payload.get("company_id")
    if company_id:
        company_resource = middleware_service.http_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Invalid credentials",
            status_code=403
        )

        request.state.company_id = company_id

   
    return user, company_resource
    
