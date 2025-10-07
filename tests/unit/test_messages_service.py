import pytest

from unittest.mock import Mock, AsyncMock, patch
import uuid

from src.modules.chats.messages.messages_service import MessagesService
from src.modules.chats.messages.messages_models import Message, MessageCreate

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def messages_service(mock_repository):
    return MessagesService(repository=mock_repository)

message_id = uuid.uuid4()
chat_id = uuid.uuid4()

def test_create(mock_db, mock_repository, messages_service):
    message_create = MessageCreate(chat_id=chat_id, sender="human", text="Hello")
    mock_message = Mock(spec=Message)
    mock_repository.create.return_value = mock_message

    result = messages_service.create(
        db=mock_db,
        message=message_create
    )

    assert result == mock_message
    mock_repository.create.assert_called_once()
    data_passed = mock_repository.create.call_args[1]["data"]
    assert data_passed.chat_id == chat_id
    assert data_passed.sender == "human"
    assert data_passed.text == "Hello"

def test_resource(mock_db, mock_repository, messages_service):
    mock_message = Mock(spec=Message)
    mock_repository.get_one.return_value = mock_message

    result = messages_service.resource(
        db=mock_db,
        message_id=message_id
    )

    assert result == mock_message
    mock_repository.get_one.assert_called_once_with(
        db=mock_db,
        key="chat_id",
        value=message_id
    )

def test_collection(mock_db, mock_repository, messages_service):
    mock_message1 = Mock(spec=Message)
    mock_message2 = Mock(spec=Message)
    mock_message1.created_at = 2
    mock_message2.created_at = 1
    mock_repository.get_many.return_value = [mock_message1, mock_message2]

    result = messages_service.collection(
        db=mock_db,
        key="chat_id",
        value=chat_id
    )

    assert result == [mock_message1, mock_message2] or result == [mock_message2, mock_message1]
    mock_repository.get_many.assert_called_once_with(
        db=mock_db,
        key="chat_id",
        value=chat_id
    )

def test_delete(mock_db, mock_repository, messages_service):
    mock_message = Mock(spec=Message)
    mock_repository.delete.return_value = mock_message

    result = messages_service.delete(
        db=mock_db,
        message_id=message_id
    )

    assert result == mock_message
    mock_repository.delete.assert_called_once_with(
        db=mock_db,
        key="message_id",
        value=message_id
    )


@pytest.mark.asyncio
@patch("src.modules.chats.messages.messages_service.Container.resolve")
async def test_handle_messages(mock_resolve, mock_db, mock_repository, messages_service):
    # Setup
    chat_id = uuid.uuid4()
    human_message = "Hi"
    ai_message = "Hello!"
    redis_service = AsyncMock()
    mock_resolve.return_value = redis_service
    redis_service.get_agent_state_key.return_value = "agent_state:{}".format(chat_id)
    redis_service.get_session.return_value = {"chat_history": []}

    # Patch create to avoid DB side effects
    messages_service.create = Mock()

    await messages_service.handle_messages(
        db=mock_db,
        chat_id=chat_id,
        human_message=human_message,
        ai_message=ai_message,
        num_of_messages=2
    )

    assert messages_service.create.call_count == 2
    redis_service.set_session.assert_awaited_once()
    redis_service.get_session.assert_awaited_once()