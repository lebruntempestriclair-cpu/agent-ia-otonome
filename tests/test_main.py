"""
Unit tests for the Agent IA Autonome application
"""

import pytest
from fastapi.testclient import TestClient
from main import app, settings

client = TestClient(app)

# Test API Key
TEST_API_KEY = "test_api_key"

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
        settings.require_api_key = False
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": 1
        }
        response = client.post("/task/create", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
        assert data["status"] == "pending"
    
    def test_create_task_missing_required_field(self):
        """Test creating task with missing required field"""
        settings.require_api_key = False
        task_data = {
            "description": "Missing title"
        }
        response = client.post("/task/create", json=task_data)
        assert response.status_code == 422  # Validation error

class TestAuthentication:
    """Tests for API Key authentication"""

    def test_unauthorized_access(self):
        """Test access without API Key when required"""
        settings.require_api_key = True
        settings.api_key = TEST_API_KEY

        response = client.get("/tasks")
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_authorized_access(self):
        """Test access with correct API Key when required"""
        settings.require_api_key = True
        settings.api_key = TEST_API_KEY

        headers = {"X-API-Key": TEST_API_KEY}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

class TestTaskRetrieval:
    """Tests for task retrieval"""
    
    def test_get_task(self):
        """Test retrieving a task"""
        settings.require_api_key = False
        response = client.get("/task/task_123")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        settings.require_api_key = False
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

class TestTaskExecution:
    """Tests for task execution"""
    
    def test_execute_task(self):
        """Test executing a task"""
        settings.require_api_key = False
        response = client.post("/execute?task_id=task_123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
