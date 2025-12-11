from fastapi import APIRouter, Depends, Request, Body, BackgroundTasks
from typing import List
from uuid import UUID

from src.core.interface.middleware.auth_middleware import auth_middleware
from src.core.interface.middleware.hmac_verification import verify_hmac
from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.interface.middleware.middleware_service import security

from src.modules.chats.interface.messages_controller import MessagesController
from src.modules.chats.domain.messages_models import MessagePublic, MessageCreate
from src.modules.chats.interface.chats_dependencies import get_chats_service
from src.modules.chats.interface.messages_dependencies import get_messages_controller
from src.modules.state.interface.state_dependencies import get_state_service
from src.modules.state.application.state_service import StateService

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    tags=["Messages (Depricated)"],
    deprecated=True, 
    dependencies=[Depends(verify_hmac)]
)

@router.post("/internal/{chat_id}", status_code=201, response_model=CommonHttpResponse)
async def internal_create(
    chat_id: UUID,
    bakcground_tasks: BackgroundTasks,
    data: MessageCreate = Body(...),
    _: None = Depends(verify_hmac), # server to server verification
    state_service: StateService = Depends(get_state_service),
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## HMAC protected  for internal use only 
    """
    return await controller.create_request(
        background_tasks=bakcground_tasks,
        chat_id=chat_id, 
        data=data, 
        state_service=state_service
    )


@router.get("/secure/collection/{chat_id}", status_code=200, response_model=List[MessagePublic], dependencies=[Depends(security)])
def secure_collection( 
    chat_id: UUID,
    req: Request,
    _=Depends(auth_middleware), 
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## Messages collection  request

    This endpoint returns a list of messages associated with the chat id passed in the params
    """
    return controller.collection_request(
        req=req,  
        chat_id=chat_id
    )

@router.get("/secure/search", status_code=200, response_model=List[MessagePublic], dependencies=[Depends(security)])
def secure_serch(
    query: str,
    req: Request,
    _: None = Depends(auth_middleware),
    controller: MessagesController = Depends(get_messages_controller)
):
    """
    ## Search request

    This endpoint will query the database for all users messages containing the string in the query
    """

    return controller.search_request(
        req=req,
        query=query
    )