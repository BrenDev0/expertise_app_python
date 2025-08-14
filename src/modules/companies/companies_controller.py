from src.core.services.http_service import HttpService
from src.modules.users.users_models import User
from src.modules.companies.companies_service import CompaniesService
from src.modules.companies.companies_models import Company, CompanyCreate, CompanyPublic, CompanyUpdate
from src.core.models.http_responses import CommonHttpResponse
from fastapi import Request
from sqlalchemy.orm import Session
from uuid import UUID

class CompaniesController:
    def __init__(self, http_service: HttpService, companies_service: CompaniesService):
        self.__https_service = http_service
        self.__companies_service = companies_service

    def create_request(
        self,
        req: Request,
        db: Session,
        data: CompanyCreate
    ): 
        user: User = req.state.user

        self.__companies_service.create(db=db, data=data, user_id=user.user_id)

        return CommonHttpResponse(
            detail="Company created"
        )
    
    def resource_request(
        self,
        company_id: UUID,
        req: Request,
        db: Session
    ):
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
    ):
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
    ):
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

        return CommonHttpResponse(
            detail="Company deleted"
        )

    @staticmethod
    def __to_public(data: Company) -> CompanyPublic:
        return CompanyPublic.model_validate(data, from_attributes=True)

        