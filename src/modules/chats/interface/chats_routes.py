from fastapi import APIRouter, Depends, Body, Request, UploadFile, File
from typing import List
from uuid import UUID

from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.interface.middleware.middleware_service import security
from src.core.interface.middleware.hmac_verification import verify_hmac
from src.core.interface.middleware.auth_middleware import auth_middleware

from src.modules.chats.interface.chats_controller import ChatsController
from src.modules.chats.domain.chats_models import ChatPublic, ChatUpdate, ChatCreate
from src.modules.chats.interface.chats_dependencies import get_chats_controller


router = APIRouter(
    prefix="/chats",
    dependencies=[Depends(security), Depends(verify_hmac)],
    tags=["Chats (Deprecated)"],
    deprecated=True
)

@router.post("/secure/create", status_code=201, response_model=ChatPublic)
def secure_create(
    req: Request,
    data: ChatCreate = Body(...),
    _: None = Depends(auth_middleware),
    controller: ChatsController = Depends(get_chats_controller)
):
    """
    ## Chat create request

    This endpoint creates a chat in the database.
    The id returned is needed for all requests to the llm.
    """
    return controller.create_request(req=req, data=data)

@router.post("/secure/context/{chat_id}", status_code=201, response_model=CommonHttpResponse)
async def secure_add_chat_context(
    chat_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    file: UploadFile = File(...),
    controller: ChatsController = Depends(get_chats_controller)
): 
    """
    ## Add context to chat

    This endpoint will add a tempory source of context for the agent that will last one request
    """
    return await controller.add_context(
        chat_id=chat_id,
        req=req,
        file=file
    )

@router.get("/secure/collection", status_code=200, response_model=List[ChatPublic])
def secure_collection( 
    req: Request,
    _: None = Depends(auth_middleware),
    controller: ChatsController = Depends(get_chats_controller)
):
    """
    ## Chat collection request

    This endpoint returns a list of chats by the user id in the auth token.
    """
    return controller.collection_request(req=req)


@router.patch("/secure/{chat_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    chat_id: UUID,
    req: Request,
    data: ChatUpdate,
    _: None = Depends(auth_middleware),
    controller: ChatsController = Depends(get_chats_controller)
): 
    """
    ## Update request

    This endpont updates the title of the chat provided in the params
    """
    return controller.update_request(
        req=req,
        data=data,
        chat_id=chat_id
    )

@router.delete("/secure/{chat_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    chat_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    controller: ChatsController = Depends(get_chats_controller)
):
    """
    ## Delete request 

    This endpoint deletes a chat by id.
    """
    return controller.delete_request(
        chat_id=chat_id,
        req=req
    )

@router.delete("/secure/context/{chat_id}/{filename}", status_code=200, response_model=CommonHttpResponse)
def secure_remove_chat_context(
    chat_id: UUID,
    filename: str,
    req: Request,
    _: None = Depends(auth_middleware),
    controller: ChatsController = Depends(get_chats_controller)
):
    """
    ## Remove context from chat

    This endpoint will remove the file noted in the params from the vecotr base
    """
    return controller.remove_context(
        req=req,
        chat_id=chat_id,
        filename=filename
    )
    