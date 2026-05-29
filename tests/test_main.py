"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

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

class TestAuthentication:
    """Tests for API Key authentication"""

    def test_unauthorized_access(self):
        """Test access with missing API key when required"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret"}):
            response = client.get("/tasks")
            assert response.status_code == 401
            assert response.json()["detail"] == "Unauthorized"

    def test_invalid_api_key(self):
        """Test access with invalid API key when required"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret"}):
            response = client.get("/tasks", headers={"X-API-Key": "wrong"})
            assert response.status_code == 401
            assert response.json()["detail"] == "Unauthorized"

    def test_authorized_access(self):
        """Test access with valid API key when required"""
        with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret"}):
            response = client.get("/tasks", headers={"X-API-Key": "secret"})
            assert response.status_code == 200

class TestErrorHandling:
    """Tests for secure error handling"""

    def test_internal_server_error_leakage(self):
        """Test that 500 errors don't leak exception details"""
        # We'll mock create_task to raise an exception
        with patch("main.logger.info", side_effect=Exception("Database connection failed!")):
            task_data = {
                "title": "Test Task",
                "description": "This is a test task"
            }
            response = client.post("/task/create", json=task_data)
            assert response.status_code == 500
            assert response.json()["detail"] == "Internal server error"
            assert "Database connection failed!" not in str(response.json())

class TestTaskCreation:
    """Tests for task creation"""
    
    def test_create_task(self):
        """Test creating a new task"""
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
        task_data = {
            "description": "Missing title"
        }
        response = client.post("/task/create", json=task_data)
        assert response.status_code == 422  # Validation error

class TestTaskRetrieval:
    """Tests for task retrieval"""
    
    def test_get_task(self):
        """Test retrieving a task"""
        response = client.get("/task/task_123")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        response = client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

class TestTaskExecution:
    """Tests for task execution"""
    
    def test_execute_task(self):
        """Test executing a task"""
        response = client.post("/execute?task_id=task_123")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
