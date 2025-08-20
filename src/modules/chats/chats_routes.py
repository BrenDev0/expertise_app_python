from fastapi import APIRouter, BackgroundTasks, Depends, Body, Request
from src.core.dependencies.container import Container
from typing import List, Dict
from src.core.middleware.auth_middleware import auth_middleware
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.modules.chats.chats_controller import ChatsController
from src.modules.chats.chats_models import ChatPublic, ChatCreateResponse, ChatUpdate, ChatCreate
from src.core.models.http_responses import CommonHttpResponse
from src.core.middleware.middleware_service import security
from uuid import UUID


router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
    dependencies=[Depends(security)] 
)

def get_controller() -> ChatsController:
    return Container.resolve("chats_controller")

@router.post("/secure/create/{agent_id}", status_code=201, response_model=ChatCreateResponse)
def secure_create(
    agent_id: UUID,
    request: Request,
    data: ChatCreate = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: ChatsController = Depends(get_controller)
):
    """
    ## Chat create request

    This endpoint creates a chat in the database.
    The id returned is needed for all requests to the llm.
    """
    return controller.create_request(agent_id=agent_id, request=request, data=data, db=db)

@router.get("/secure/collection", status_code=200, response_model=List[ChatPublic])
def secure_collection( 
    request: Request,
    _: None = Depends(auth_middleware), 
    db: Session = Depends(get_db_session),
    controller: ChatsController = Depends(get_controller)
):
    """
    ## Chat collection request

    This endpoint returns a list of chats by the user id in the auth token.
    """
    return controller.collection_request(request=request, db=db)


@router.put("/secure/{chat_id}", status_code=200, response_model=CommonHttpResponse)
def secure_update(
    chat_id: UUID,
    data: ChatUpdate,
    request: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: ChatsController = Depends(get_controller)
): 
    """
    ## Update request

    This endpont updates the title of the chat provided in the params
    """
    return controller.update_request(
        request=request,
        db=db,
        data=data,
        chat_id=chat_id
    )

@router.delete("/secure/{chat_id}", status_code=200, response_model=CommonHttpResponse)
def secure_delete(
    chat_id: UUID,
    req: Request,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: ChatsController = Depends(get_controller)
):
    """
    ## Delete request 

    This endpoint deletes a chat by id.
    """
    return controller.delete_request(
        chat_id=chat_id,
        req=req,
        db=db
    )
    