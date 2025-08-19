from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Text, ForeignKey
from src.core.database.database_models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, List, Dict
from pydantic.alias_generators import to_camel

class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=True)

class ChatConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel 
    )


class ChatCreate(ChatConfig):
    title: str

class ChatUpdate(ChatCreate):
    pass

class ChatPublic(ChatCreate):
    chat_id: uuid.UUID
    user_id: uuid.UUID
    agent_id: uuid.UUID
   
class ChatCreateResponse(ChatConfig):
    chat_id: uuid.UUID


