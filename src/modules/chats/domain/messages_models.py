from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
import uuid
from  datetime import datetime
from typing import Union, Dict, List, Any, Optional




class MessageConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel,
        extra="forbid"
    )

class MessageCreate(MessageConfig):
    sender: uuid.UUID
    message_type: str
    text: Optional[Union[str, List[Any]]] = None
    json_data: Optional[Any] = None


class MessagePublic(MessageCreate):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    created_at: datetime
    
