from fastapi import APIRouter, Depends, Body, Request
from src.modules.users.users_controller import UsersController
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.modules.users.users_models import UserCreate, UserPublic, UserLogin, VerifyEmail, UserUpdate, VerifiedUserUpdate
from src.core.database.session import get_db_session
from sqlalchemy.orm import Session
from src.core.dependencies.container import Container
from src.core.middleware.middleware_service import security
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.verification_middleware import verification_middleware
from src.core.middleware.hmac_verification import verify_hmac



router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=([Depends(verify_hmac)])
)

def get_controller() -> UsersController:
    controller = Container.resolve("users_controller")
    return controller

@router.post("/verify-email", status_code=200, response_model=ResponseWithToken)
def verify_email(
    req: Request,
    data: VerifyEmail = Body(...),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Verify email request

    This endpoint sends a verification email to the email send in the request body.
    The token recieved in the response is needed to create a user.
    """

    return controller.verify_email(
        req=req,
        data=data,
        db=db,
    )

@router.post("/secure/verify-email", status_code=200, response_model=ResponseWithToken)
def secure_verify_email(
    req: Request,
    data: VerifyEmail = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Verify email for Update email request

    This endpoint will send a verification code to the email.
    Auth headers required for request.
    """
    return controller.verify_email(
        req=req,
        data=data,
        db=db,
        is_update=True
    )

@router.post("/verified/create", status_code=201, response_model=ResponseWithToken, dependencies=[Depends(security)])
def verifies_create(
    req: Request,
    _: None = Depends(verification_middleware),
    data: UserCreate = Body(...),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Create Request

    This endpoint creates a user in the databae.
    A verifcation code from the users email and a verification token are needed to make a request.
    Will return a valid webtoken with duration of 7 days.
    """
    return controller.create_request(
        req=req, 
        db=db, 
        data=data,
    )


@router.get("/secure/resource", status_code=200, response_model=UserPublic, dependencies=[Depends(security)])
def secure_resource(
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Resource request

    This endpoint gets the current user.
    """
    return controller.resource_request(
        req=req,
        db=db
    )

@router.patch("/secure/update", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    req: Request,
    data: UserUpdate,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Update request 

    This endpoint will update a users profile info.
    If updating password, previous password must be provided.
    """
    return controller.update_request(
        req=req,
        data=data,
        db=db
    )

@router.patch("/verified/update", status_code=200, response_model=CommonHttpResponse)
def verified_update(
    req: Request,
    data: VerifiedUserUpdate = Body(...),
    _: None = Depends(verification_middleware),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Verified update request

    This enpoint is for all updates that require a verification code.
    """
    return controller.verified_update_request(
        req=req,
        data=data,
        db=db
    )

@router.delete("/secure/delete", status_code=200, response_model=CommonHttpResponse, dependencies=[Depends(security)])
def secure_delete(
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Delete request 

    This endpoint deletes the current user from the database
    """
    
    return controller.delete_request(
        req=req,
        db=db
    )

@router.post("/login", status_code=200, response_model=ResponseWithToken)
def login(
    db: Session = Depends(get_db_session),
    data: UserLogin = Body(...),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Login request

    This endpoint retruns a valid webtoken needed for all requests to secure routes.
    """
    return controller.login(
        db=db, 
        data=data
    )


@router.post("/account-recovery", status_code=200, response_model=CommonHttpResponse)
def account_recovery(
    req: Request,
    data: VerifyEmail = Body(...),
    db: Session = Depends(get_db_session),
    controller: UsersController = Depends(get_controller)
):
    """
    ## Acount recovery request

    This endpoint will send a link to the users email to change password.
    This link will have a parameter 'token', this token is needed for the verified update request.
    """
    return controller.account_recovery_request(
        req=req,
        data=data,
        db=db
    )