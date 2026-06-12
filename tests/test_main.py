"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
import secrets
import time
from unittest.mock import patch
from fastapi.testclient import TestClient

# Mock settings before importing app to test authentication
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key", "CORS_ORIGINS": "http://localhost:3000,https://app.example.com"}):
    from main import app, settings
    client = TestClient(app)

class TestSecurity:
    """Tests for security features"""

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/task/create", "post"),
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

    def test_timing_attack_protection(self):
        """Verify that secrets.compare_digest is used for API key validation"""
        with patch("secrets.compare_digest", side_effect=secrets.compare_digest) as mock_compare:
            headers = {"X-API-Key": "test_secret_key"}
            client.get("/tasks", headers=headers)
            assert mock_compare.called

    def test_secure_fail_missing_key(self):
        """System should return 500 if REQUIRE_API_KEY is True but API_KEY is default or missing"""
        with patch("main.settings.API_KEY", "default_secret_key"):
            headers = {"X-API-Key": "any"}
            response = client.get("/tasks", headers=headers)
            assert response.status_code == 500

    def test_health_check_remains_public(self):
        """Health check should not require API key"""
        response = client.get("/health")
        assert response.status_code == 200

class TestCORS:
    """Tests for CORS configuration"""

    def test_cors_origins(self):
        """Test that allowed origins are correctly handled"""
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

        response = client.options("/health", headers={
            "Origin": "https://malicious.com",
            "Access-Control-Request-Method": "GET"
        })
        assert "access-control-allow-origin" not in response.headers

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

class TestTaskWorkflow:
    """Tests for the full task workflow including dubbing fields"""
    
    def test_task_lifecycle(self):
        """Test creating, retrieving, and executing a task with new fields"""
        headers = {"X-API-Key": "test_secret_key"}

        # 1. Create task
        task_data = {
            "title": "Dubbing Video",
            "description": "Translate French to English",
            "source_language": "fr",
            "target_language": "en",
            "voice_id": "alloy",
            "file_url": "https://storage.example.com/video.mp4"
        }
        create_resp = client.post("/task/create", json=task_data, headers=headers)
        assert create_resp.status_code == 200
        task_id = create_resp.json()["task_id"]

        # 2. Get task and verify fields
        get_resp = client.get(f"/task/{task_id}", headers=headers)
        assert get_resp.status_code == 200
        task_info = get_resp.json()
        assert task_info["id"] == task_id
        assert task_info["source_language"] == "fr"
        assert task_info["target_language"] == "en"
        assert task_info["progress"] == 0

        # 3. Execute task (async)
        exec_resp = client.post(f"/execute?task_id={task_id}", headers=headers)
        assert exec_resp.status_code == 200
        assert exec_resp.json()["status"] == "processing"

        # 4. Wait for background task to complete (or simulate it if needed, but TestClient runs it synchronously unless configured otherwise)
        # By default FastAPI BackgroundTasks run after the response is sent.
        # In TestClient, they are executed immediately before the response is returned.

        final_resp = client.get(f"/task/{task_id}", headers=headers)
        assert final_resp.json()["status"] == "completed"
        assert final_resp.json()["progress"] == 100

    def test_get_nonexistent_task(self):
        """Test retrieving a task that doesn't exist"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/task/nonexistent", headers=headers)
        assert response.status_code == 404

    def test_execute_nonexistent_task(self):
        """Test executing a task that doesn't exist"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.post("/execute?task_id=nonexistent", headers=headers)
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
