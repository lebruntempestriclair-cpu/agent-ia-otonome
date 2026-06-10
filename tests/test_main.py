"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Mock settings before importing app to test authentication
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    from main import app, Settings
    client = TestClient(app)

class TestSecurity:
    """Tests for security features"""

    def test_timing_attack_protection(self):
        """Test that secrets.compare_digest is used for API key validation"""
        with patch("secrets.compare_digest", side_effect=lambda a, b: a == b) as mock_compare:
            headers = {"X-API-Key": "test_secret_key"}
            response = client.get("/tasks", headers=headers)
            assert response.status_code == 200
            mock_compare.assert_called()

    def test_cors_wildcard_credentials(self):
        """Test that CORS does not allow credentials with wildcard origin"""
        response = client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            }
        )
        assert response.status_code == 200
        # If allow_credentials is False, Access-Control-Allow-Credentials should not be 'true'
        assert response.headers.get("Access-Control-Allow-Credentials") != "true"

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/task/create", "post"),
            ("/task/task_123", "get"),
            ("/tasks", "get"),
            ("/execute?task_id=task_123", "post")
        ]
        for url, method in endpoints:
            func = getattr(client, method)
            response = func(url)
            assert response.status_code == 403
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
        assert data["status"] == "pending"
    
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
    
    def test_get_task(self):
        """Test retrieving a task"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/task/task_123", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

class TestTaskExecution:
    """Tests for task execution"""
    
    def test_execute_task(self):
        """Test executing a task"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.post("/execute?task_id=task_123", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
