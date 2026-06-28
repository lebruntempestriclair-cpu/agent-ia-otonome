"""
Unit and Integration tests for the Agent IA Autonome application
"""

import pytest
import os
import io
import shutil
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock environmental variables and force security setting for testing
os.environ["REQUIRE_API_KEY"] = "true"
os.environ["API_KEY"] = "test_secret_key"
os.environ["DEPLOYMENT_ENV"] = "development"

from main import app, settings, Settings

# Force settings to require API key for testing
settings.REQUIRE_API_KEY = True
settings.API_KEY = "test_secret_key"

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    """Clean up uploads directory before and after tests"""
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)

class TestSecurity:
    """Tests for security features"""

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/task/task_123", "get"),
            ("/tasks", "get"),
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

    def test_mock_oauth_success(self):
        """Test mock OAuth2 verification with valid token"""
        headers = {
            "X-API-Key": "test_secret_key",
            "Authorization": "Bearer valid_token"
        }
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200

    def test_mock_oauth_failure(self):
        """Test mock OAuth2 verification with invalid token"""
        headers = {
            "X-API-Key": "test_secret_key",
            "Authorization": "Bearer invalid_token"
        }
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid authentication credentials"}

class TestDubbingEndpoint:
    """Tests for the /dub endpoint"""

    def test_dub_success(self):
        """Test successful dubbing job initiation"""
        headers = {"X-API-Key": "test_secret_key"}
        file_content = b"fake video content"
        files = {"file": ("test.mp4", io.BytesIO(file_content), "video/mp4")}
        data = {
            "target_lang": "fr",
            "voice_id": "female_1",
            "gdpr_consent": "true"
        }

        # Patch background tasks to avoid real execution
        with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
            response = client.post("/dub", headers=headers, data=data, files=files)

            assert response.status_code == 200
            json_response = response.json()
            assert json_response["success"] is True
            assert "job_id" in json_response
            assert json_response["status"] == "processing"
            mock_add_task.assert_called_once()

    def test_dub_missing_consent(self):
        """Test dubbing job fails without GDPR consent"""
        headers = {"X-API-Key": "test_secret_key"}
        files = {"file": ("test.mp4", b"content", "video/mp4")}
        data = {"target_lang": "fr", "gdpr_consent": "false"}

        response = client.post("/dub", headers=headers, data=data, files=files)
        assert response.status_code == 400
        assert "GDPR consent is mandatory" in response.json()["detail"]

    def test_dub_invalid_extension(self):
        """Test dubbing job fails with unsupported extension"""
        headers = {"X-API-Key": "test_secret_key"}
        files = {"file": ("test.exe", b"content", "application/octet-stream")}
        data = {"target_lang": "fr", "gdpr_consent": "true"}

        response = client.post("/dub", headers=headers, data=data, files=files)
        assert response.status_code == 400
        assert "Unsupported file extension" in response.json()["detail"]

    def test_dub_file_too_large(self):
        """Test dubbing job fails when file exceeds limit"""
        headers = {"X-API-Key": "test_secret_key"}
        # Mocking settings to have a very small limit for testing
        with patch.object(settings, "MAX_UPLOAD_SIZE", 10):
            files = {"file": ("test.mp4", b"too long content", "video/mp4")}
            data = {"target_lang": "fr", "gdpr_consent": "true"}

            response = client.post("/dub", headers=headers, data=data, files=files)
            assert response.status_code == 413
            assert "File too large" in response.json()["detail"]

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200 and correct structure"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["environment"] == "development"

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

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
