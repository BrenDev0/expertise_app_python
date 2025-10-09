from  fastapi import Request, HTTPException

from src.core.domain.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.dependencies.container import Container
from src.core.services.email_service import EmailService
from src.core.services.encryption_service import EncryptionService
from src.core.services.webtoken_service import WebTokenService
from src.core.services.hashing_service import HashingService
from src.core.services.request_validation_service import RequestValidationService
from src.core.domain.models.errors import IncorrectPassword

from src.modules.users.application.users_service import UsersService
from src.modules.users.domain.entities import User
from src.modules.users.domain.models import UserPublic,UserCreate, UserLogin, VerifyEmail, UserLogin, UserUpdate, VerifiedUserUpdate
from src.modules.users.application.use_cases.delete_user_documents import DeleteUserDocuments
from src.modules.employees.application.employees_service import EmployeesService


class UsersController:
    def __init__(
        self, 
        users_service: UsersService,
        delete_user_documents: DeleteUserDocuments,
        encryption_service: EncryptionService,
        hashing_service: HashingService,
        web_token_service: WebTokenService
    ):
        self.__delete_user_documents = delete_user_documents
        self.__users_service = users_service
        self.__encryption_service = encryption_service
        self.__hashing_service = hashing_service
        self.__web_token_service = web_token_service

    def verify_email(
        self,
        req: Request,
        data: VerifyEmail,
        is_update: bool = False
    ) -> ResponseWithToken:
        token_payload = {}

        if is_update:
            user:User = getattr(req.state, "user", None)

            if not user:
                raise HTTPException(status_code=403, detail="forbidden")
            
            token_payload["user_id"] = str(user.user_id)

        hashed_email = self.__hashing_service.hash_for_search(data.email)
        email_type = "NEW" if not is_update else "UPDATE"
        user_exists = self.__users_service.resource(key="email_hash", value=hashed_email)

        if user_exists:
            raise HTTPException(status_code=400, detail="Email in use")
        
        email_service: EmailService = Container.resolve("email_service")

        verification_code = email_service.handle_request(email=data.email, type_=email_type)

        token_payload["verification_code"] = verification_code

        token = self.__web_token_service.generate_token(token_payload, "15m")

       
        return ResponseWithToken(
            detail="Email sent",
            token=token
        ) 
    
    def account_recovery_request(
        self,
        req: Request,
        data: VerifyEmail,
    ) -> ResponseWithToken:
        email_hash = self.__hashing_service.hash_for_search(data.email)

        user_exists = self.__users_service.resource(
            key="email_hash",
            value=email_hash
        )

        RequestValidationService.verify_resource(
            result=user_exists,
            not_found_message="User profile not found"
        )

        email_service: EmailService = Container.resolve("email_service")
        verification_code = email_service.handle_request(email=data.email, type_="RECOVERY")

        token = self.__web_token_service.generate_token({
            "verification_code": verification_code,
            "user_id": str(user_exists.user_id)
        }, "15m")

        return ResponseWithToken(
            detail="Email sent",
            token=token
        ) 

    def create_request(
        self,
        req: Request,
        data: UserCreate
    ) -> ResponseWithToken:
        verification_code = req.state.verification_code

        RequestValidationService.verifiy_ownership(verification_code, data.code)

        new_user = self.__users_service.create(data=data, is_admin=True)

        token = self.__web_token_service.generate_token({
            "user_id": str(new_user.user_id)
        }, "7d")

        return ResponseWithToken(
            detail="User created",
            token=token
        )


    def resource_request(
        self, 
        req: Request
    ) -> UserPublic:
        user: User = req.state.user
        
        data = self.__to_public(data=user)

        return data


    def verified_update_request(
        self,
        req: Request,
        data: VerifiedUserUpdate
    ) -> CommonHttpResponse:
        verification_code = req.state.verification_code
        user: User = getattr(req.state, "user", None)

        if not user or data.code != verification_code: 
            raise HTTPException(status_code=403, detail="Unauthorized")

        requested_same_password = self.__hashing_service.compare_password(data.password, user.password, throw_error=False)
        if requested_same_password:
            raise HTTPException(status_code=400, detail="New password must not match current password")
        
        self.__users_service.update(user_id=user.user_id, changes=data)

        return CommonHttpResponse(
            detail="User profile updated"
        )

    def update_request(
        self,
        req: Request,
        data: UserUpdate,
    ) -> CommonHttpResponse:
        user: User = req.state.user

        if data.password:
            if not data.old_password:
                raise HTTPException(status_code=400, detail="Previous password required to update password")
            
            try:
                self.__hashing_service.compare_password(data.old_password, user.password)
                
            except IncorrectPassword as e:
                raise HTTPException(status_code=401, detail=str(e))

            requested_same_password = self.__hashing_service.compare_password(data.password, user.password, throw_error=False)
            if requested_same_password:
                raise HTTPException(status_code=400, detail="New password must not match current password")
        
        
        self.__users_service.update(user_id=user.user_id, changes=data)

        return CommonHttpResponse(
            detail="User profile updated"
        )

    def delete_request(
        self,
        req: Request
    ) -> CommonHttpResponse:
        user: User = req.state.user
        
        if user.is_admin:
            self.__delete_user_documents.execute()


        self.__users_service.delete(user_id=user.user_id) 

        return CommonHttpResponse(
            detail="User deleted"
        )

    def login(
        self,
        data: UserLogin,
        employees_service: EmployeesService
    ) -> ResponseWithToken:
        hashed_email = self.__hashing_service.hash_for_search(data=data.email)

        user = self.__users_service.resource(
            key="email_hash",
            value=hashed_email
        )

        RequestValidationService.verify_resource(
            result=user,
            not_found_message="Incorrect email or password"
        )

        try:
            self.__hashing_service.compare_password(
                password=data.password, 
                hashed_password=user.password,
                detail="Incorrect email or password"
            )
        except IncorrectPassword as e:
            raise HTTPException(status_code=401, detail=str(e))

        token_payload = {
            "user_id": str(user.user_id)
        }

        if not user.is_admin:
            employee_resource = employees_service.resource(
                key="user_id",
                value=user.user_id
            )

            RequestValidationService.verify_resource(
                result=employee_resource,
                not_found_message="Employee profile not found"
            )

            token_payload["company_id"] = str(employee_resource.company_id)

        token = self.__web_token_service.generate_token(token_payload, "7d")

        response = ResponseWithToken(
            detail="Login Successful",
            token=token
        )

        if not user.is_admin:
            response.company_id = str(employee_resource.company_id)
        
        return  response


    def __to_public(self, data: User) ->  UserPublic:
        data.user_id = str(data.user_id)
        data.name = self.__encryption_service.decrypt(data.name)
        data.email = self.__encryption_service.decrypt(data.email)
        data.phone = self.__encryption_service.decrypt(data.phone)

        user = UserPublic.model_validate(data, from_attributes=True)
        return user