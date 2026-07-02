"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Create a client that uses the API key in headers by default if we want to test authenticated
# But here we want to test unauthenticated first.

# We need to ensure settings are patched BEFORE app is loaded.
# Since main.py creates settings = Settings() at module level.

with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    # Force reload of main to pick up new env vars if it was already imported,
    # but in a fresh pytest run it should be fine.
    import main
    import importlib
    importlib.reload(main)
    from main import app
    client = TestClient(app)

class TestSecurity:
    """Tests for security features"""

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/task/create", "post"),
            ("/tasks", "get"),
            ("/dub", "post"),
            ("/user/data", "delete")
        ]
        for url, method in endpoints:
            func = getattr(client, method)
            if method == "post" and url == "/dub":
                response = func(url, data={"target_lang": "en", "gdpr_consent": "true"})
            elif method == "post":
                response = func(url, json={"title": "Test", "description": "Test"})
            else:
                response = func(url)
            assert response.status_code == 403, f"Endpoint {url} with method {method} should return 403"
            assert response.json() == {"detail": "Could not validate credentials"}

    def test_authenticated_access(self):
        """Test that sensitive endpoints allow access with valid API key"""
        headers = {"X-API-Key": "test_secret_key"}

        # Test task creation
        task_data = {"title": "Test", "description": "Test"}
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 200

        # Test list tasks
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

    def test_health_check_remains_public(self):
        """Health check should not require API key"""
        response = client.get("/health")
        assert response.status_code == 200

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200 and correct structure"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

class TestTaskCreation:
    """Tests for task creation"""
    
    def test_create_task(self):
        """Test creating a new task"""
        headers = {"X-API-Key": "test_secret_key"}
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": 1
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
    
    def test_create_task_missing_required_field(self):
        """Test creating task with missing required field"""
        headers = {"X-API-Key": "test_secret_key"}
        task_data = {
            "description": "Missing title"
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 422  # Validation error

class TestTaskRetrieval:
    """Tests for task retrieval"""
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
