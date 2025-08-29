from src.core.database.database_models import Base
from sqlalchemy import Column, UUID, ForeignKey, UniqueConstraint, Table
import uuid
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import List

class Participant(Base):
    __tablename__ = "participants"

    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False, primary_key=True)
    UniqueConstraint("chat_id", "agent_id", name="uix_chat_agent")


class ParticipantsConfig(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        serialize_by_alias=True,
        alias_generator=to_camel
    )


class InviteToChat(ParticipantsConfig):
    agents: List[uuid.UUID]

class  RemoveFromChat(InviteToChat):
    pass