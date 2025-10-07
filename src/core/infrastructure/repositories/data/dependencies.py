from core.dependencies.container import Container

from src.modules.users.domain.users_repository import UsersRepository
from src.modules.users.infrastructure.sqlalchemy_user_repository import SqlAlchemyUserRepository


def get_users_repository() -> UsersRepository:
    return SqlAlchemyUserRepository()