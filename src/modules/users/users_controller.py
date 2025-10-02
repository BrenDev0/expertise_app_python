from  fastapi import Request, HTTPException
from sqlalchemy.orm import Session

from src.core.services.http_service import HttpService
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from src.core.dependencies.container import Container
from src.core.services.email_service import EmailService

from src.modules.users.users_service import UsersService
from src.modules.users.users_models import UserPublic, User, UserCreate, UserLogin, VerifyEmail, UserLogin, UserUpdate, VerifiedUserUpdate
from src.modules.employees.employees_models import Employee
from src.modules.documents.document_manager import DocumentManager
from src.modules.companies.companies_service import CompaniesService


class UsersController:
    def __init__(self, http_service: HttpService, users_service: UsersService):
        self.__http_service = http_service
        self.__users_service = users_service

    def verify_email(
        self,
        req: Request,
        data: VerifyEmail,
        db: Session,
        is_update: bool = False
    ) -> ResponseWithToken:
        token_payload = {}

        if is_update:
            user:User = getattr(req.state, "user", None)

            if not user:
                raise HTTPException(status_code=403, detail="forbidden")
            
            token_payload["user_id"] = str(user.user_id)

        hashed_email = self.__http_service.hashing_service.hash_for_search(data.email)
        email_type = "NEW" if not is_update else "UPDATE"
        user_exists = self.__users_service.resource(db=db, key="email_hash", value=hashed_email)

        if user_exists:
            raise HTTPException(status_code=400, detail="Email in use")
        
        email_service: EmailService = Container.resolve("email_service")

        verification_code = email_service.handle_request(email=data.email, type_=email_type)

        token_payload["verification_code"] = verification_code

        token = self.__http_service.webtoken_service.generate_token(token_payload, "15m")

       
        return ResponseWithToken(
            detail="Email sent",
            token=token
        ) 
    
    def account_recovery_request(
        self,
        req: Request,
        data: VerifyEmail,
        db: Session
    ) -> ResponseWithToken:
        email_hash = self.__http_service.hashing_service.hash_for_search(data.email)

        user_exists: User =  self.__http_service.request_validation_service.verify_resource(
            service_key="users_service",
            params={
                "db": db,
                "key": "email_hash",
                "value": email_hash
            },
            not_found_message="User profile not found"
        )

        email_service: EmailService = Container.resolve("email_service")
        verification_code = email_service.handle_request(email=data.email, type_="RECOVERY")

        token = self.__http_service.webtoken_service.generate_token({
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
        db: Session,
        data: UserCreate
    ) -> ResponseWithToken:
        verification_code = req.state.verification_code

        self.__http_service.request_validation_service.validate_action_authorization(verification_code, data.code)

        new_user = self.__users_service.create(db=db, data=data, is_admin=True)

        token = self.__http_service.webtoken_service.generate_token({
            "user_id": str(new_user.user_id)
        }, "7d")

        return ResponseWithToken(
            detail="User created",
            token=token
        )


    def resource_request(
        self, 
        req: Request,
        db: Session
    ) -> UserPublic:
        user: User = req.state.user
        data = self.__to_public(data=user)

        return data


    def verified_update_request(
        self,
        req: Request,
        data: VerifiedUserUpdate,
        db: Session
    ) -> CommonHttpResponse:
        verification_code = req.state.verification_code
        user: User = getattr(req.state, "user", None)

        if not user or data.code != verification_code: 
            raise HTTPException(status_code=403, detail="Unauthorized")

        requested_same_password = self.__http_service.hashing_service.compare_password(data.password, user.password, throw_error=False)
        if requested_same_password:
            raise HTTPException(status_code=400, detail="New password must not match current password")
        
        self.__users_service.update(db=db, user_id=user.user_id, changes=data)

        return CommonHttpResponse(
            detail="User profile updated"
        )

    def update_request(
        self,
        req: Request,
        data: UserUpdate,
        db: Session,
    ) -> CommonHttpResponse:
        user: User = req.state.user

        if data.password:
            if not data.old_password:
                raise HTTPException(status_code=400, detail="Previous password required to update password")
            
            self.__http_service.hashing_service.compare_password(data.old_password, user.password)

            requested_same_password = self.__http_service.hashing_service.compare_password(data.password, user.password, throw_error=False)
            if requested_same_password:
                raise HTTPException(status_code=400, detail="New password must not match current password")
        
        
        self.__users_service.update(db=db, user_id=user.user_id, changes=data)

        return CommonHttpResponse(
            detail="User profile updated"
        )

    def delete_request(
        self,
        req: Request,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user
        
        if user.is_admin:
            ## delete bucket and vector base data 
            document_manager: DocumentManager = Container.resolve("document_manager")
            document_manager.user_level_deletion(user_id=user.user_id, db=db)

            ## delete companies and employee accounts
            companies_service: CompaniesService = Container.resolve("companies_service")
            companies = companies_service.collection(db=db, user_id=user.user_id)

            if len(companies) != 0:
                for company in companies:
                    companies_service.delete(db=db, company_id=company.company_id)


        self.__users_service.delete(db=db, user_id=user.user_id) 

        return CommonHttpResponse(
            detail="User deleted"
        )

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

        token_payload = {
            "user_id": str(user.user_id)
        }

        if not user.is_admin:
            employee_resource: Employee = self.__http_service.request_validation_service.verify_resource(
                service_key="employees_service",
                params={
                    "db": db,
                    "key": "user_id",
                    "value": user.user_id
                },
                not_found_message="Employee profile not found"
            )

            token_payload["company_id"] = str(employee_resource.company_id)

        token = self.__http_service.webtoken_service.generate_token(token_payload, "7d")

        response = ResponseWithToken(
            detail="Login Successful",
            token=token
        )

        if not user.is_admin:
            response.company_id = str(employee_resource.company_id)
        
        return  response


    def __to_public(self, data: User) ->  UserPublic:
        data.user_id = str(data.user_id)
        data.name = self.__http_service.encryption_service.decrypt(data.name)
        data.email = self.__http_service.encryption_service.decrypt(data.email)
        data.phone = self.__http_service.encryption_service.decrypt(data.phone)

        user = UserPublic.model_validate(data, from_attributes=True)
        return user