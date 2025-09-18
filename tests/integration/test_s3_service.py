from dotenv import load_dotenv
load_dotenv()
import os
import pytest
from src.core.dependencies.configure_container import configure_container
from src.core.dependencies.container import Container
from src.modules.documents.s3_service import S3Service


def test_delete_company_data():
    configure_container()
    s3_service: S3Service = Container.resolve("s3_service")

    user_id = os.getenv("TEST_USER_ID")
    company_id = os.getenv("TEST_COMPANY_ID")

    result = s3_service.delete_company_data(
        user_id=user_id,
        company_id=company_id
    )

    assert result == "Company data deleted"
