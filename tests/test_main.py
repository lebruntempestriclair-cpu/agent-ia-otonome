"""
Unit tests for the Agent IA Autonome application
"""

import pytest
from fastapi.testclient import TestClient
from main import app, get_api_key

client = TestClient(app)

# Test key for authentication
TEST_API_KEY = "test-key-123"

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
    
    def setup_method(self):
        # Override get_api_key to simulate authentication
        app.dependency_overrides[get_api_key] = lambda x_api_key="test-key-123": x_api_key

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_create_task(self):
        """Test creating a new task"""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": 1
        }
        response = client.post(
            "/task/create",
            json=task_data,
            headers={"X-API-Key": TEST_API_KEY}
        )
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
        response = client.post(
            "/task/create",
            json=task_data,
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 422  # Validation error

class TestTaskRetrieval:
    """Tests for task retrieval"""
    
    def setup_method(self):
        app.dependency_overrides[get_api_key] = lambda x_api_key="test-key-123": x_api_key

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_get_task(self):
        """Test retrieving a task"""
        response = client.get(
            "/task/task_123",
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        response = client.get(
            "/tasks",
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

class TestTaskExecution:
    """Tests for task execution"""
    
    def setup_method(self):
        app.dependency_overrides[get_api_key] = lambda x_api_key="test-key-123": x_api_key

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_execute_task(self):
        """Test executing a task"""
        response = client.post(
            "/execute?task_id=task_123",
            headers={"X-API-Key": TEST_API_KEY}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

class TestSecurity:
    """Tests for security features"""

    def test_unauthorized_access(self):
        """Test access without API key when required"""
        # We need to make sure require_api_key is True for this test
        from main import settings
        original_require_api_key = settings.require_api_key
        original_api_key = settings.api_key
        settings.require_api_key = True
        settings.api_key = "secret-key"

        try:
            response = client.get("/tasks")
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid or missing API Key"
        finally:
            settings.require_api_key = original_require_api_key
            settings.api_key = original_api_key

    def test_invalid_api_key(self):
        """Test access with invalid API key"""
        from main import settings
        original_require_api_key = settings.require_api_key
        original_api_key = settings.api_key
        settings.require_api_key = True
        settings.api_key = "secret-key"

        try:
            response = client.get("/tasks", headers={"X-API-Key": "wrong-key"})
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid or missing API Key"
        finally:
            settings.require_api_key = original_require_api_key
            settings.api_key = original_api_key

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
