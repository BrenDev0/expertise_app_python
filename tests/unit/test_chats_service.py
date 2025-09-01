import pytest
from unittest.mock import Mock
import uuid

from src.modules.chats.chats_service import ChatsService
from src.modules.chats.chats_models import Chat, ChatCreate, ChatUpdate
from src.modules.chats.participants.participants_models import Participant  
from src.modules.agents.agents_models import Agent  

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def chats_service(mock_repository):
    return ChatsService(repository=mock_repository)

chat_id = uuid.uuid4()
user_id = uuid.uuid4()

def test_create(mock_db, mock_repository, chats_service):
    title = "Test Chat"
    mock_chat = Mock(spec=Chat)
    mock_repository.create.return_value = mock_chat

    result = chats_service.create(
        db=mock_db,
        title=title,
        user_id=user_id
    )

    assert result == mock_chat
    mock_repository.create.assert_called_once()
    # Check that create was called with a Chat instance
    call_args = mock_repository.create.call_args
    assert call_args[1]['db'] == mock_db
    created_chat = call_args[1]['data']
    assert created_chat.user_id == user_id
    assert created_chat.title == title

def test_resource(mock_db, mock_repository, chats_service):
    mock_chat = Mock(spec=Chat)
    mock_repository.get_one.return_value = mock_chat

    result = chats_service.resource(
        db=mock_db,
        chat_id=chat_id
    )

    assert result == mock_chat
    mock_repository.get_one.assert_called_once_with(
        db=mock_db,
        key="chat_id",
        value=chat_id
    )

def test_collection(mock_db, mock_repository, chats_service):
    mock_chat1 = Mock(spec=Chat)
    mock_chat2 = Mock(spec=Chat)
    mock_repository.get_many.return_value = [mock_chat1, mock_chat2]

    result = chats_service.collection(
        db=mock_db,
        user_id=user_id
    )

    assert result == [mock_chat1, mock_chat2]
    mock_repository.get_many.assert_called_once_with(
        db=mock_db,
        key="user_id",
        value=user_id
    )

def test_update(mock_db, mock_repository, chats_service):
    changes = ChatUpdate(title="Updated Title")
    mock_chat = Mock(spec=Chat)
    mock_repository.update.return_value = mock_chat

    result = chats_service.update(
        db=mock_db,
        chat_id=chat_id,
        changes=changes
    )

    assert result == mock_chat
    mock_repository.update.assert_called_once_with(
        db=mock_db,
        key="chat_id",
        value=chat_id,
        changes=changes.model_dump(exclude_unset=True)
    )

def test_delete(mock_db, mock_repository, chats_service):
    mock_chat = Mock(spec=Chat)
    mock_repository.delete.return_value = mock_chat

    result = chats_service.delete(
        db=mock_db,
        chat_id=chat_id
    )

    assert result == mock_chat
    mock_repository.delete.assert_called_once_with(
        db=mock_db,
        key="chat_id",
        value=chat_id
    )