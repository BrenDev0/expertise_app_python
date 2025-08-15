from fastapi import HTTPException, Depends, Request
from src.modules.users.users_models import User
from src.core.middleware.auth_middleware import auth_middleware

def is_owner(req: Request, _: None = Depends(auth_middleware)):
    user: User = req.state.user

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")