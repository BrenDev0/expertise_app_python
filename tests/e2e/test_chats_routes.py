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

# Replace with valid IDs from your test DB
agent_id = "95e222ef-c637-42d3-a81e-955beeeb0ba2"

def test_secure_create():
    with TestClient(app) as client:
        payload = {
            "title": "Test Chat"
        }
        res = client.post(
            f"/chats/secure/create/{agent_id}",
            headers=auth_header,
            json=payload
        )
        assert res.status_code == 201
        data = res.json()
        assert "chatId" in data
        assert isinstance(data["chatId"], str)

def test_secure_collection():
    with TestClient(app) as client:
        res = client.get(
            "/chats/secure/collection",
            headers=auth_header
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        if res.json():
            chat = res.json()[0]
            assert "chatId" in chat
            assert "userId" in chat
            assert "agentId" in chat
            assert "title" in chat

def test_secure_update():
    with TestClient(app) as client:
        # First, create a chat to update
        payload = {"title": "Chat to Update"}
        create_res = client.post(
            f"/chats/secure/create/{agent_id}",
            headers=auth_header,
            json=payload
        )
        assert create_res.status_code == 201
        chat_id = create_res.json()["chatId"]

        # Now, update the chat
        update_payload = {"title": "Updated Title"}
        update_res = client.put(
            f"/chats/secure/update/{chat_id}",
            headers=auth_header,
            json=update_payload
        )
        assert update_res.status_code == 200
        assert update_res.json()["detail"] == "Chat updated"