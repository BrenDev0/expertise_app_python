from fastapi import HTTPException, Depends, Request
from src.modules.users.users_models import User
from src.core.middleware.auth_middleware import auth_middleware
from src.core.dependencies.container import Container
from src.core.services.http_service import HttpService
from src.modules.employees.employees_models import Employee
from src.core.database.session import get_db_session
from sqlalchemy.orm import Session

def is_owner(req: Request, _: None = Depends(auth_middleware)):
    user: User = req.state.user

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")


def is_manager(
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session)
):
    user: User = req.state.user

    if user.is_admin:
        return 
    
    else:
        http_service: HttpService = Container.resolve("http_service")

        employee_resource: Employee = http_service.request_validation_service.verify_resource(
            service_key="employees_service",
            params={
                "db": db,
                "key": "user_id",
                "value": user.user_id
            },
            not_found_message="forbidden",
            status_code=403
        )

        if not employee_resource.is_manager:
            raise HTTPException(status_code=403, detail="Forbidden")