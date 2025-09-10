from src.core.services.http_service import HttpService
from src.modules.users.users_models import User
from src.modules.companies.companies_service import CompaniesService
from src.modules.companies.companies_models import Company, CompanyCreate, CompanyPublic, CompanyUpdate
from src.core.models.http_responses import CommonHttpResponse, ResponseWithToken
from fastapi import Request
from sqlalchemy.orm import Session
from uuid import UUID
from src.core.dependencies.container import Container
from src.modules.documents.s3_service import S3Service
from src.modules.documents.embeddings_service import EmbeddingService

class CompaniesController:
    def __init__(self, http_service: HttpService, companies_service: CompaniesService):
        self.__https_service = http_service
        self.__companies_service = companies_service

    def create_request(
        self,
        req: Request,
        db: Session,
        data: CompanyCreate
    ) -> CompanyPublic: 
        user: User = req.state.user

        new_company = self.__companies_service.create(db=db, data=data, user_id=user.user_id)

        return self.__to_public(new_company)
    
    def resource_request(
        self,
        company_id: UUID,
        req: Request,
        db: Session
    ) -> CompanyPublic:
        user: User = req.state.user

        company_resource: Company = self.__https_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__https_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        return self.__to_public(company_resource)


    def collection_request(
        self,
        req: Request,
        db: Session,
    ):
        user: User = req.state.user

        data = self.__companies_service.collection(db=db, user_id=user.user_id)

        return [
            self.__to_public(company) for company in data
        ]
    

    def update_request(
        self,
        company_id: UUID,
        req: Request,
        db: Session,
        data: CompanyUpdate
    ) -> CommonHttpResponse:
        user: User = req.state.user

        company_resource: Company = self.__https_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__https_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        self.__companies_service.update(db=db, company_id=company_id, changes=data)

        return CommonHttpResponse(
            detail="Company updated"
        )
    
    def delete_request(
        self,
        company_id: UUID,
        req: Request,
        db: Session
    ) -> CommonHttpResponse:
        user: User = req.state.user

        company_resource: Company = self.__https_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__https_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        self.__companies_service.delete(db=db, company_id=company_id)


        ## delete bucket and vector base data 
        s3_service: S3Service = Container.resolve("s3_service")
        embeddings_service: EmbeddingService = Container.resolve("embeddings_service")
        s3_service.delete_company_data(user_id=user.user_id, company_id=company_resource.company_id)
        embeddings_service.delete_company_data(user_id=user.user_id, company_id=company_resource.company_id)

        return CommonHttpResponse(
            detail="Company deleted"
        )
    

    def login(
        self,
        company_id: UUID,
        req: Request,
        db: Session
    ) -> ResponseWithToken:
        user: User = req.state.user

        company_resource: Company = self.__https_service.request_validation_service.verify_resource(
            service_key="companies_service",
            params={
                "db": db,
                "company_id": company_id
            },
            not_found_message="Company not found"
        )

        self.__https_service.request_validation_service.validate_action_authorization(user.user_id, company_resource.user_id)

        token_payload = {
            "user_id": str(user.user_id),
            "company_id": str(company_resource.company_id)
        }

        token = self.__https_service.webtoken_service.generate_token(token_payload, "7d")

        return ResponseWithToken(
            detail="Login successful",
            token=token
        )


    @staticmethod
    def __to_public(data: Company) -> CompanyPublic:
        return CompanyPublic.model_validate(data, from_attributes=True)

        