from pydantic import BaseModel
from typing import List
from src.modules.chats.messages.messages_models import Message
from uuid import UUID

class ChatState(BaseModel):
    input: str
    chat_id: UUID
    chat_history: List[Message]
    user_id: UUID
    agent_id: UUID