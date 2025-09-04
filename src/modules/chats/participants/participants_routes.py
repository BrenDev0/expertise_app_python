from fastapi import Request, Depends, APIRouter, Body
from sqlalchemy.orm import Session
from src.core.database.session import get_db_session
from src.modules.chats.participants.participants_controller import ParticipantsController
from src.modules.chats.participants.participants_models import InviteToChat, RemoveFromChat
from src.core.models.http_responses import CommonHttpResponse
from src.core.middleware.middleware_service import security
from src.core.middleware.auth_middleware import auth_middleware
from src.core.dependencies.container import Container
from uuid import UUID
from src.core.middleware.hmac_verification import verify_hmac

router = APIRouter(
    prefix="/chat-participants",
    tags=["Chat Participants"],
    dependencies=[Depends(security), Depends(verify_hmac)]
)

def get_controller() -> ParticipantsController:
    controller = Container.resolve("participants_controller")
    return controller

@router.post("/secure/{chat_id}", status_code=201, response_model=CommonHttpResponse)
def secure_invite(
    chat_id: UUID,
    req: Request,
    data: InviteToChat = Body(...),
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: ParticipantsController = Depends(get_controller)
) ->  CommonHttpResponse:
    """
    ## Add agents to chat

    This endpoint accepts an array of agent ids to add to a chat
    """
    return controller.add_to_chat(chat_id=chat_id, req=req, data=data, db=db)


@router.delete("/secure/{chat_id}", status_code=200, response_model=CommonHttpResponse)
def secure_remove(
    chat_id: UUID,
    req: Request,
    data: RemoveFromChat,
    _: None = Depends(auth_middleware),
    db: Session = Depends(get_db_session),
    controller: ParticipantsController = Depends(get_controller)
):
    """
    ## Remove agents from chat

    This endpoint accepts an array of agent ids to be removed from a chat
    """
    return controller.remove_from_chat(
        chat_id=chat_id,
        req=req,
        data=data,
        db=db
    )