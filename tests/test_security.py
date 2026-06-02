import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
import os

client = TestClient(app)

def test_tasks_endpoint_requires_api_key_when_enabled():
    """Verify that /tasks is protected when REQUIRE_API_KEY is true"""
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret123"}):
        # No key
        response = client.get("/tasks")
        assert response.status_code == 403

        # Wrong key
        response = client.get("/tasks", headers={"X-API-Key": "wrong"})
        assert response.status_code == 403

        # Correct key
        response = client.get("/tasks", headers={"X-API-Key": "secret123"})
        assert response.status_code == 200

def test_create_task_endpoint_requires_api_key_when_enabled():
    """Verify that /task/create is protected when REQUIRE_API_KEY is true"""
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret123"}):
        task_data = {"title": "Test", "description": "Test"}

        # No key
        response = client.post("/task/create", json=task_data)
        assert response.status_code == 403

        # Correct key
        response = client.post("/task/create", json=task_data, headers={"X-API-Key": "secret123"})
        assert response.status_code == 200

def test_execute_endpoint_requires_api_key_when_enabled():
    """Verify that /execute is protected when REQUIRE_API_KEY is true"""
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret123"}):
        # No key
        response = client.post("/execute?task_id=123")
        assert response.status_code == 403

        # Correct key
        response = client.post("/execute?task_id=123", headers={"X-API-Key": "secret123"})
        assert response.status_code == 200

def test_error_information_not_leaked():
    """Verify that error responses DO NOT leak internal exception details"""
    # Force an exception by monkeypatching logger.info
    # Note: we need to patch logger.info inside the create_task function context
    # In main.py, it's logger.info(f"Creating task: {task.title}")
    with patch("main.logger.info", side_effect=Exception("Sensitive DB Error")):
        response = client.post("/task/create", json={"title": "test", "description": "test"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert "Sensitive DB Error" not in response.json()["detail"]
