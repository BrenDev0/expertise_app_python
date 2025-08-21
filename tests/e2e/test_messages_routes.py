from dotenv import load_dotenv
load_dotenv()

import os
import uuid
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

token = os.getenv("TEST_TOKEN")
auth_header = {
    "Authorization": f"Bearer {token}"
}

# Replace with a valid chat_id from your test DB
chat_id = "38412dee-d190-4e37-9818-c5cfb880b6fd"

def test_secure_collection():
    with TestClient(app) as client:
        res = client.get(
            f"/messages/secure/collection/{chat_id}",
            headers=auth_header
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        if res.json():
            message = res.json()[0]
            assert "messageId" in message
            assert "chatId" in message
            assert "sender" in message
            assert "text" in message
            assert "createdAt" in message