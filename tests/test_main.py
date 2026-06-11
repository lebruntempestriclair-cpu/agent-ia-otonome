"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

# Mock settings before importing app
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    from main import app, tasks_db, DB_FILE
    client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    """Clear DB before and after each test"""
    tasks_db.clear()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    yield
    tasks_db.clear()
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

class TestSecurityAndAuth:
    """Tests for hybrid security (API Key + OAuth2)"""

    def test_unauthenticated_access(self):
        response = client.get("/tasks")
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_api_key_access(self):
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

    def test_oauth_access(self):
        # 1. Login to get token
        login_res = client.post("/auth/login")
        token = login_res.json()["access_token"]

        # 2. Use token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

    def test_auth_me(self):
        login_res = client.post("/auth/login")
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "user@example.com"

class TestTaskPersistence:
    """Tests for the simulated persistence layer"""

    def test_persistence_across_requests(self):
        headers = {"X-API-Key": "test_secret_key"}

        # 1. Create task
        task_data = {"title": "Persist Test", "description": "...", "gdpr_consent": True}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        # 2. Check if file exists
        assert os.path.exists(DB_FILE)
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            assert task_id in data
            assert data[task_id]["title"] == "Persist Test"

class TestDubbingWorkflow:
    """Tests for the storage-enabled dubbing workflow"""

    def test_full_workflow_with_storage(self):
        headers = {"X-API-Key": "test_secret_key"}

        # 1. Create task
        task_data = {"title": "Storage Test", "description": "...", "gdpr_consent": True}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        # 2. Upload chunk (with body)
        chunk_data = b"fake-video-chunk"
        upload_res = client.post(
            f"/upload/chunk?chunk_index=0&total_chunks=1&task_id={task_id}",
            content=chunk_data,
            headers=headers
        )
        assert upload_res.status_code == 200
        assert upload_res.json()["is_complete"] is True

        # 3. Verify file_url is set
        status_res = client.get(f"/task/{task_id}", headers=headers)
        assert "https://storage.cloud.com" in status_res.json()["file_url"]

        # 4. Execute
        exec_res = client.post(f"/execute?task_id={task_id}", headers=headers)
        assert exec_res.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
