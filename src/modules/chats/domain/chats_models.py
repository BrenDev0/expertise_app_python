from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, ForeignKey
import uuid
from sqlalchemy.dialects.postgresql import UUID
from pydantic.alias_generators import to_camel


class ChatConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class ChatCreate(ChatConfig):
    title: str

class ChatUpdate(ChatConfig):
    title: str

class ChatPublic(ChatCreate):
    chat_id: uuid.UUID
    user_id: uuid.UUID
    
   
class ChatCreateResponse(ChatConfig):
    chat_id: uuid.UUID


