from fastapi import APIRouter, Depends, Request, Body
from src.core.dependencies.container import Container
from typing import List
from src.core.middleware.auth_middleware import auth_middleware
from src.core.middleware.hmac_verification import verify_hmac
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.modules.chats.messages.messages_controller import MessagesController
from src.core.middleware.middleware_service import security
from src.modules.chats.messages.messages_models import MessagePublic, MessageCreate
from uuid import UUID
from src.core.domain.models.http_responses import CommonHttpResponse
from src.modules.chats.chats_dependencies import get_chats_service
from src.modules.chats.messages.messages_dependencies import get_messages_controller
from src.modules.chats.chats_service import ChatsService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)

@router.post("/internal/{chat_id}", status_code=201, response_model=CommonHttpResponse)
async def internal_create(
    chat_id: UUID,
    data: MessageCreate = Body(...),
    _: None = Depends(verify_hmac), # server to server verification
    chats_service: ChatsService = Depends(get_chats_service),
    db: Session = Depends(get_db_session),
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## HMAC protected  for internal use only 
    """
    return await controller.create_request(
        chat_id=chat_id, 
        data=data, db=db,
        chats_service=chats_service
    )


@router.get("/secure/collection/{chat_id}", status_code=200, response_model=List[MessagePublic], dependencies=[Depends(security)])
def secure_collection( 
    chat_id: UUID,
    req: Request,
    _=Depends(auth_middleware), 
    chats_service: ChatsService = Depends(get_chats_service),
    db: Session = Depends(get_db_session),
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## Messages collection  request

    This endpoint returns a list of messages associated with the chat id passed in the params
    """
    return controller.collection_request(
        req=req, 
        db=db, 
        chat_id=chat_id,
        chats_service=chats_service
    )

@router.get("/secure/search", status_code=200, response_model=List[MessagePublic], dependencies=[Depends(security)])
def secure_serch(
    query: str,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## Search request

    This endpoint will query the database for all users messages containing the string in the query
    """

    return controller.search_request(
        req=req,
        query=query,
        db=db
    )