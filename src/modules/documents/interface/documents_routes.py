from fastapi import APIRouter, UploadFile, Request, File,  Depends, BackgroundTasks
from uuid import UUID
from typing import List

from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.interface.middleware.permissions import is_owner, token_is_company_stamped
from src.core.interface.middleware.middleware_service import security
from src.core.interface.middleware.hmac_verification import verify_hmac

from src.modules.documents.domain.documents_models import DocumentPublic
from src.modules.documents.interface.documents_controller import DocumentsController
from src.modules.documents.interface.documents_dependencies import get_documents_controller
from src.modules.documents.application.use_cases.upload_document import UploadDocument
from src.modules.documents.interface.documents_dependencies import get_upload_document_use_case



router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(security), Depends(verify_hmac)]
)

@router.post("/secure/upload", status_code=201, response_model=CommonHttpResponse)
async def secure_upload(
    background_tasks: BackgroundTasks,
    req: Request,
    file: UploadFile = File(...),
    _: None = Depends(is_owner),
    company = Depends(token_is_company_stamped),
    upload_document_use_case: UploadDocument = Depends(get_upload_document_use_case),
    controller: DocumentsController = Depends(get_documents_controller)
):
    """
    ## Upload request

    This endpoint will uplad a document to the s3 bucket.
    Only admin level users have access to this endpoint. 
    """
    return await controller.upload_request(
        background_tasks=background_tasks,
        req=req,
        file=file,
        upload_document=upload_document_use_case
    )


@router.get("/secure/collection", status_code=200, response_model=List[DocumentPublic])
def secure_collection(
    req: Request,
    _: None = Depends(is_owner),
    company = Depends(token_is_company_stamped),
    controller: DocumentsController = Depends(get_documents_controller)
):
    """
    ## Collection request

    This endpoint gets all documents uploaded by a company.
    Only admin level users have access to this endpoint. 
    """
    return controller.collection_request(req=req)

@router.delete("/secure/{document_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    document_id: UUID,
    req: Request,
    _: None = Depends(is_owner),
    company = Depends(token_is_company_stamped),
    controller: DocumentsController = Depends(get_documents_controller)
):
    """
    ## Delete request

    This endpoint will delete an uploaded document.
    Only admin level users have access to this endpoint.

    """
    return controller.delete_request(document_id=document_id, req=req)

