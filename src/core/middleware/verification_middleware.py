# middleware/auth_middleware.py
from fastapi import Request, Depends, HTTPException

from src.core.services.webtoken_service import WebTokenService
from src.core.middleware.middleware_service import MiddlewareService
from src.modules.users.application.users_service import UsersService
from src.core.services.request_validation_service import RequestValidationService

from src.modules.users.interface.users_dependencies import get_users_service
from src.core.dependencies.services import get_middleware_service, get_web_token_service



def verification_middleware(
    request: Request, 
    middleware_service: MiddlewareService = Depends(get_middleware_service),
    web_token_service: WebTokenService = Depends(get_web_token_service),
    users_service: UsersService = Depends(get_users_service)
):
    
    token_payload = middleware_service.get_auth_bearer(
        request=request,
        web_token_service=web_token_service
    )

    verification_code = token_payload.get("verification_code")

    if verification_code is None:
        raise HTTPException(status_code=403, detail="Unauthorized")

    request.state.verification_code = verification_code
    
    user_id = token_payload.get("user_id", None)
    if user_id:
        user = users_service.resource(
            key="user_id",
            value=user_id
        )

        RequestValidationService.verify_resource(
            result=user,
            not_found_message="Forbidden",
            status_code=403
        )

        request.state.user = user

    return verification_code
  
        