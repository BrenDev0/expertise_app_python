from dotenv import load_dotenv
load_dotenv()

import os
import uuid
from fastapi.testclient import TestClient
from src.server import app
import json

client = TestClient(app)

token = os.getenv("TEST_TOKEN")
auth_header = {
    "Authorization": f"Bearer {token}"
}

# Replace these with valid IDs from your test DB
employee_id = "672cfdca-23bf-43f4-b725-cf2c2a8f0f31"
agent_id = "95e222ef-c637-42d3-a81e-955beeeb0ba2"

def test_secure_read():
    with TestClient(app) as client:
        res = client.get(
            "/agents/secure/read",
            headers=auth_header
        )
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        if res.json():
            agent = res.json()[0]
            assert "agentId" in agent
            assert "agentName" in agent
            assert "agentUsername" in agent
            assert "profilePic" in agent
            assert "endpoint" in agent

def test_secure_resource_success():
    with TestClient(app) as client:
        res = client.get(
            f"/agents/secure/resource/{agent_id}",
            headers=auth_header
        )
        assert res.status_code == 200
        agent = res.json()
        assert agent["agentId"] == agent_id
        assert "agentName" in agent
        assert "agentUsername" in agent

def test_secure_resource_not_found():
    with TestClient(app) as client:
        res = client.get(
            f"/agents/secure/resource/{uuid.uuid4()}",
            headers=auth_header
        )
        assert res.status_code == 404
        assert res.json()["detail"] == "Agent not found"

def test_secure_add_access():
    with TestClient(app) as client:
        payload = {
            "agentIds": [agent_id]
        }
        res = client.post(
            f"/agents/secure/access/{employee_id}",
            headers=auth_header,
            json=payload
        )
        assert res.status_code == 201
        assert "Agent access added" in res.json()["detail"]

def test_secure_collection():
    with TestClient(app) as client:
        res = client.get(
            f"/agents/secure/collection/{employee_id}",
            headers=auth_header
        )
      
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        
        if res.json():
            agent = res.json()[0]
            assert "agentId" in agent
            assert "agentName" in agent

def test_secure_remove_access():
    with TestClient(app) as client:
        payload = {
            "agentIds": [agent_id]
        }
        res = client.request(
            "DELETE",
            f"/agents/secure/access/{employee_id}",
            headers={**auth_header, "Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        assert res.status_code == 200
        assert res.json()["detail"] == "Agent access removed from employee" 