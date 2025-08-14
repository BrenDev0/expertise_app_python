import pytest
from unittest.mock import Mock, patch
import uuid

with patch("src.core.decorators.service_error_handler.service_error_handler", lambda *a, **kw: (lambda f: f)):

    from src.modules.invites.invites_service import InvitesService
    from src.modules.invites.invites_models import Invite, InviteCreate, InviteUpdate

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_data_handler():
    # Mock the encryption_service used inside data_handler
    mock_encryption_service = Mock()
    mock_encryption_service.encrypt.side_effect = lambda x: f"enc_{x}"
    mock_data_handler = Mock()
    mock_data_handler.encryption_service = mock_encryption_service
    return mock_data_handler

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def invites_service(mock_repository, mock_data_handler):
    return InvitesService(
        repository=mock_repository,
        data_handler=mock_data_handler
    )

invite_id = uuid.uuid4()
company_id = uuid.uuid4()

def test_create(mock_repository, mock_data_handler, mock_db, invites_service):
    invite_data = InviteCreate(
        name="John Doe",
        email="john@example.com",
        phone="1234567890",
        position="manager"
    )

    mock_invite = Mock(spec=Invite)
    mock_repository.create.return_value = mock_invite

    result = invites_service.create(
        db=mock_db,
        data=invite_data,
        company_id=company_id
    )

    assert result == mock_invite
    mock_repository.create.assert_called_once()

    data_passed = mock_repository.create.call_args[1]["data"]
    assert data_passed.company_id == company_id
    assert data_passed.name == "enc_John Doe"
    assert data_passed.email == "enc_john@example.com"
    assert data_passed.phone == "enc_1234567890"
    assert data_passed.position == invite_data.position

def test_resource(mock_db, mock_repository, invites_service):
    mock_invite = Mock(spec=Invite)
    mock_repository.get_one.return_value = mock_invite

    result = invites_service.resource(
        db=mock_db,
        invite_id=invite_id
    )

    assert result == mock_invite
    mock_repository.get_one.assert_called_once()

    args_passed = mock_repository.get_one.call_args[1]
    assert args_passed["key"] == "invite_id"
    assert args_passed["value"] == invite_id

def test_collection(mock_db, mock_repository, invites_service):
    mock_invite_1 = Mock(spec=Invite)
    mock_invite_2 = Mock(spec=Invite)
    mock_collection = [mock_invite_1, mock_invite_2]

    mock_repository.get_many.return_value = mock_collection

    result = invites_service.collection(
        db=mock_db,
        company_id=company_id
    )

    assert result == mock_collection
    mock_repository.get_many.assert_called_once()

    args_passed = mock_repository.get_many.call_args[1]
    assert args_passed["key"] == "company_id"
    assert args_passed["value"] == company_id

def test_update(mock_db, mock_repository, invites_service):
    changes = InviteUpdate(
        position="director"
    )

    mock_invite = Mock(spec=Invite)
    mock_repository.update.return_value = mock_invite

    result = invites_service.update(
        db=mock_db,
        invite_id=invite_id,
        changes=changes
    )

    assert result == mock_invite
    mock_repository.update.assert_called_once()

    args_passed = mock_repository.update.call_args[1]
    assert args_passed["key"] == "employee_id"
    assert args_passed["value"] == invite_id
    assert args_passed["changes"]["position"] == changes.position

def test_delete(mock_db, mock_repository, invites_service):
    mock_invite = Mock(spec=Invite)
    mock_repository.delete.return_value = mock_invite

    result = invites_service.delete(
        db=mock_db,
        invite_id=invite_id
    )

    assert result == mock_invite
    mock_repository.delete.assert_called_once()

    args_passed = mock_repository.delete.call_args[1]
    assert args_passed["key"] == "invite_id"
    assert args_passed["value"] == invite_id