from fastapi import Request, Depends, HTTPException

from src.core.interface.middleware.middleware_service import MiddlewareService

from src.modules.companies.domain.enitities import Company
from src.modules.companies.application.companies_service import CompaniesService
from src.core.services.webtoken_service import WebTokenService
from src.modules.users.application.users_service import UsersService

from src.modules.companies.interface.companies_dependencies import get_companies_service
from src.core.dependencies.services import get_middleware_service, get_web_token_service
from src.modules.users.interface.users_dependencies import get_users_service



async def auth_middleware(
    request: Request, 
    middleware_service: MiddlewareService = Depends(get_middleware_service),
    web_token_service: WebTokenService = Depends(get_web_token_service),
    companies_service: CompaniesService = Depends(get_companies_service),
    user_service: UsersService = Depends(get_users_service)
):
    token_payload = middleware_service.get_auth_bearer(
        request=request,
        web_token_service=web_token_service
    )

    user_id = token_payload.get("user_id", None)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invlalid token")
    
    user = user_service.resource(
        key="user_id",
        value=user_id
    )

    request.state.user = user
    
    company_id = token_payload.get("company_id", None)
    if company_id:
        company_resource: Company = companies_service.resource(
            key="company_id",
            value=company_id
        )

        if company_resource:
            request.state.company_id = company_resource.company_id

    return user
    
