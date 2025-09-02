from pydantic import BaseModel
from typing import List
from src.modules.chats.messages.messages_models import MessagePublic
from uuid import UUID

class WorkerState(BaseModel):
    input: str
    chat_id: UUID
    chat_history: List[MessagePublic]
    user_id: UUID
    agent_id: UUID