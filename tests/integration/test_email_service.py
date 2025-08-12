from dotenv import load_dotenv
load_dotenv()
import pytest
from unittest.mock import Mock
from src.core.services.email_service import EmailService
from src.core.services.webtoken_service import WebTokenService

@pytest.fixture
def email_service():
    return EmailService()


@pytest.fixture
def mock_webtoken_service():
    mock = Mock(spec=WebTokenService)
    mock.generate_token.return_value = "mocked_token"
    return mock

def test_send_verification_email(email_service, mock_webtoken_service):
    email = "brendan.soullens@gmail.com"
    type_ = "NEW"

    token = email_service.handle_request(email=email, type_=type_, webtoken_service=mock_webtoken_service)

    assert token == "mocked_token"
    mock_webtoken_service.generate_token.assert_called_once()

