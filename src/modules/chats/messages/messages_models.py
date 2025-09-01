from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from src.core.database.database_models import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from  datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    sender = Column(UUID(as_uuid=True), nullable=False) # can be user_id or agent_id depending on message_type 
    text = Column(Text, nullable=False)
    message_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MessageConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class MessageCreate(MessageConfig):
    chat_id: uuid.UUID
    sender: uuid.UUID
    message_type: str
    text: str

class MessagePublic(MessageCreate):
    message_id: uuid.UUID
    created_at: datetime

    
