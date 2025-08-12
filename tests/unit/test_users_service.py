import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.core.repository.base_repository import BaseRepository
from src.core.logs.logger import Logger
from src.modules.users.users_service import UsersService
from src.modules.users.users_models import UserCreate, User



@pytest.fixture
def mock_repository():
    return Mock(spec=BaseRepository)

@pytest.fixture
def mock_logger():
    return Mock(spec=Logger)

@pytest.fixture
def users_service(mock_repository, mock_logger):
    return UsersService(
        respository=mock_repository,
        logger=mock_logger
    )

@pytest.fixture
def mock_db():
    return Mock()

def test_create_user(mock_db, users_service, mock_repository):
    user_data = UserCreate(
        name="testing",
        phone="1234567890",
        email="testing@gmail.com",
        password="abc123",
        code=123456
    )

    hashed_email = "hashed_email"
    hashed_password = "hashed_email"

    mock_user = Mock(spec=User)

    mock_repository.create.return_value = mock_user

    result = users_service.create(
        db=mock_db, 
        user=user_data, 
        hashed_email=hashed_email, 
        hashed_password=hashed_password
    )

    assert result == mock_user
    mock_repository.create.assert_called_once()
    created_user = mock_repository.create.call_args[1]['data']
    assert created_user.email_hash == hashed_email
    assert created_user.password  == hashed_password
    assert created_user.name == user_data.name


def test_resource(mock_db, users_service, mock_repository):
    mock_user = Mock(spec=User)
    mock_repository.get_one.return_value = mock_user

    result = users_service.resource(db=mock_db, key="user_id", value="uuid")

    assert result == mock_user
    mock_repository.get_one.assert_called_once()
    mock_repository.get_one.assert_called_once_with(db=mock_db, key="user_id", value="uuid")


def test_delete(mock_db, users_service, mock_repository):
    mock_user = Mock(spec=User)

    mock_repository.delete.return_value = mock_user

    result = users_service.delete(db=mock_db, user_id="uuid")

    
    assert result == mock_user
    mock_repository.delete.assert_called_once()
    mock_repository.delete.assert_called_once_with(db=mock_db, key="user_id", value="uuid")