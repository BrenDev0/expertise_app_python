import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from src.modules.invites.domain.entities import Invite
from src.core.infrastructure.repositories.data.sqlalchemy_data_repository import SqlAlchemyDataRepository, Base

class SqlAlchemyInvite(Base):
    __tablename__ = "invites"

    invite_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4, unique=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.company_id", ondelete="CASCADE"))
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    position = Column(String, nullable=True)
    is_manager = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SqlAlchemyInvitesRepository(SqlAlchemyDataRepository[Invite, SqlAlchemyInvite]):
    def __init__(self):
        super().__init__(SqlAlchemyInvite)

    def _to_entity(self, model: SqlAlchemyInvite) -> Invite:
        return Invite(
            invite_id=model.invite_id,
            company_id=model.company_id,
            email=model.email,
            name=model.name,
            phone=model.phone,
            position=model.position,
            is_manager=model.is_manager,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: Invite) -> SqlAlchemyInvite:
        data = entity.model_dump(exclude={'invite_id', 'created_at'} if not entity.invite_id else set())
        return SqlAlchemyInvite(**data)