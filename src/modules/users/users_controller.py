from  fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from src.core.services.http_service import HttpService
from src.modules.users.users_service import UsersService
from src.modules.users.users_models import UserPublic, User, UserCreate, UserLogin, VerifyEmail, UserLogin
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.dependencies.container import Container
from src.core.services.email_service import EmailService


class UsersController:
    def __init__(self, http_service: HttpService, users_service: UsersService):
        self.__http_service = http_service
        self.__users_service = users_service

    def verify_email(
        self,
        db: Session,
        data: VerifyEmail
    ) -> ResponseWithToken:
        hashed_email = self.__http_service.hashing_service.hash_for_search(data.email)

        user_exists = self.__users_service.resource(db=db, key="email_hash", value=hashed_email)

        if user_exists:
            raise HTTPException(status_code=400, detail="Email in use")
        
        email_service: EmailService = Container.resolve("email_service")
        token = email_service.handle_request(email=data.email, type_="NEW", webtoken_service=self.__http_service.webtoken_service)

        return ResponseWithToken(
            detail="Email sent",
            token=token
        )

    def create_request(
        self,
        req: Request,
        db: Session,
        data: UserCreate
    ) -> CommonHttpResponse:
        verification_code = req.state.verification_code

        self.__http_service.request_validation_service.validate_action_authorization(verification_code, data.code)

        self.__users_service.create(db=db, user=data)

        return CommonHttpResponse(
            detail="User created"
        )


    def resource_request(
        self, 
        req: Request,
        db: Session
    ) -> UserPublic:
        data = self.__to_public(data=req.state.user)

        return data


    def delete_request(
        self,
        req: Request,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user

        self.__users_service.delete(db=db, user_id=user.user_id) 

    def login(
        self,
        db: Session,
        data: UserLogin
    ) -> ResponseWithToken:
        hashed_email = self.__http_service.hashing_service.hash_for_search(data=data.email)

        user: User = self.__http_service.request_validation_service.verify_resource(
            service_key="users_service",
            params={"db": db, "key": "email_hash", "value": hashed_email},
            not_found_message="Incorrect email or password",
            status_code=400
        )

        self.__http_service.hashing_service.compare_password(
            password=data.password, 
            hashed_password=user.password,
            status_code=400,
            detail="Incorrect email or password"
        )

        token = self.__http_service.webtoken_service.generate_token({
            "user_id": user.user_id
        }, "7d")

        return ResponseWithToken(
            detail="Login Successful",
            token=token
        )


    def __to_public(self, data: User) ->  UserPublic:
        user = UserPublic.model_validate(data, from_attributes=True)

        user.user_id = str(data.user_id)
        user.name = self.__http_service.encryption_service.decrypt(data.name)
        user.email = self.__http_service.encryption_service.decrypt(data.email)
        user.phone = self.__http_service.encryption_service.decrypt(data.phone)

        return user