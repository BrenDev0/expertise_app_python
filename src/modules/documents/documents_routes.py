from  fastapi import APIRouter, UploadFile, Request, File,  Depends
from src.modules.documents.s3_service import S3Service
from src.modules.documents.documents_controller import DocumentsController
from src.core.models.http_responses import CommonHttpResponse
from uuid import UUID
from src.core.middleware.permissions import is_owner
from src.core.middleware.middleware_service import security
from src.core.dependencies.container import Container
from src.core.database.session import get_db_session
from sqlalchemy.orm import Session
from src.modules.documents.documents_models import DocumentPublic
from typing import List


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    dependencies=[Depends(security)]
)

def get_controller() -> DocumentsController:
    controller =  Container.resolve("documents_controller")
    return controller

@router.post("/secure/upload", status_code=201, response_model=CommonHttpResponse)
def secure_upload(
    req: Request,
    file: UploadFile = File(...),
    _: None = Depends(is_owner),
    db: Session = Depends(get_db_session),
    controller: DocumentsController = Depends(get_controller)
):
    """
    ## Upload request

    This endpoint will uplad a document to the s3 bucket.
    Only admin level users have access to this endpoint. 
    """
    return controller.upload_request(
        req=req,
        db=db,
        file=file
    )

@router.get("/secure/collection", status_code=200, response_model=List[DocumentPublic])
def secure_collection(
    req: Request,
    _: None = Depends(is_owner),
    db: Session = Depends(get_db_session),
    controller: DocumentsController = Depends(get_controller)
):
    """
    ## Collection request

    This endpoint gets all documents uploaded by a company.
    Only admin level users have access to this endpoint. 
    """
    return controller.collection_request(req=req, db=db)

@router.delete("/secure/{document_id}", status_code=200, response_model=CommonHttpResponse)
async def secure_delete(
    document_id: UUID,
    req: Request,
    _: None = Depends(is_owner),
    db: Session = Depends(get_db_session),
    controller: DocumentsController = Depends(get_controller)
):
    """
    ## Delete request

    This endpoint will delete an uploaded document.
    Only admin level users have access to this endpoint.

    """
    return await controller.delete_request(document_id=document_id, req=req, db=db)