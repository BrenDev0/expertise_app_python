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
agent_id_1 = "95e222ef-c637-42d3-a81e-955beeeb0ba2"
agent_id_2 = "99b5792d-c38a-4e49-9207-a3fa547905ae"  

def test_secure_create():
    with TestClient(app) as client:
        payload = {
            "title": "Test Chat",
            "agents": [agent_id_1, agent_id_2]  
        }
        res = client.post(
            f"/chats/secure/create",
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
        print(res.json(), ":::::::::COLLECTION")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
       
        if res.json():
            chat = res.json()[0]
            assert "chatId" in chat
            assert "userId" in chat
            assert "agents" in chat  
            assert isinstance(chat["agents"], list)
            assert "title" in chat

def test_secure_update():
    with TestClient(app) as client:
      
        payload = {"title": "Chat to Update", "agents": [agent_id_1]}
        create_res = client.post(
            f"/chats/secure/create",
            headers=auth_header,
            json=payload
        )
        assert create_res.status_code == 201
        chat_id = create_res.json()["chatId"]

    
        update_payload = {"title": "Updated Title"}
        update_res = client.patch(
            f"/chats/secure/{chat_id}",
            headers=auth_header,
            json=update_payload
        )
        assert update_res.status_code == 200
        assert update_res.json()["detail"] == "Chat updated"

def test_secure_delete():
    with TestClient(app) as client:
       
        payload = {"title": "Chat to Delete", "agents": [agent_id_1]}
        create_res = client.post(
            f"/chats/secure/create",
            headers=auth_header,
            json=payload
        )
        assert create_res.status_code == 201
        chat_id = create_res.json()["chatId"]

        delete_res = client.delete(
            f"/chats/secure/{chat_id}",
            headers=auth_header,
        )
        assert delete_res.status_code == 200
        assert delete_res.json()["detail"] == "Chat deleted"