from fastapi import APIRouter, Depends, Body, Request
from typing import List
from src.core.middleware.auth_middleware import auth_middleware


from src.modules.chats.interface.chats_controller import ChatsController
from src.modules.chats.domain.chats_models import ChatPublic,  ChatUpdate, ChatCreate
from src.core.domain.models.http_responses import CommonHttpResponse
from src.core.middleware.middleware_service import security
from src.core.middleware.hmac_verification import verify_hmac
from uuid import UUID
from src.modules.chats.interface.chats_dependencies import get_chats_controller


router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    dependencies=[Depends(security), Depends(verify_hmac)] 
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
    