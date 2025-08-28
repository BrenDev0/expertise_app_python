from src.core.database.database_models import Base
from sqlalchemy import Column, String, UUID, ForeignKey, UniqueConstraint
import uuid

class Participant(Base):
    __tablename__ = "participants"

    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.agent_id", ondelete="CASCADE"), nullable=False)
    UniqueConstraint("chat_id", "agent_id", name="uix_chat_agent")