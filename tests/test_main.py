"""
Unit tests for the Multilingual Voice Dubbing Platform
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app, settings
client = TestClient(app)

class TestSecurity:
    """Tests for security features"""

    def setup_method(self):
        settings.REQUIRE_API_KEY = True
        settings.API_KEY = "test_secret_key"

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/task/create", "post", {"title": "T", "source_language": "fr", "target_language": "en"}),
            ("/task/task_123", "get", None),
            ("/tasks", "get", None),
            ("/execute?task_id=task_123", "post", None)
        ]
        for url, method, data in endpoints:
            func = getattr(client, method)
            if data:
                response = func(url, json=data)
            else:
                response = func(url)
            assert response.status_code == 403
            assert response.json() == {"detail": "Could not validate credentials"}

    def test_health_check_remains_public(self):
        """Health check should not require API key"""
        response = client.get("/health")
        assert response.status_code == 200

class TestDubbingTask:
    """Tests for dubbing task creation and management"""

    def setup_method(self):
        settings.REQUIRE_API_KEY = True
        settings.API_KEY = "test_secret_key"
    
    def test_create_dubbing_task(self):
        """Test creating a new dubbing task"""
        headers = {"X-API-Key": "test_secret_key"}
        task_data = {
            "title": "Documentaire Nature",
            "source_language": "fr",
            "target_language": "en",
            "voice_style": "narrator"
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data
        assert data["status"] == "pending"

    def test_get_task(self):
        """Test retrieving a task"""
        headers = {"X-API-Key": "test_secret_key"}
        # Create a task first
        task_data = {"title": "T1", "source_language": "fr", "target_language": "en"}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        response = client.get(f"/task/{task_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "T1"

    def test_list_tasks(self):
        """Test listing all tasks"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.get("/tasks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data

    def test_execute_task(self):
        """Test starting the pipeline for a task"""
        headers = {"X-API-Key": "test_secret_key"}
        # Create a task
        task_data = {"title": "T_Exec", "source_language": "fr", "target_language": "en"}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        response = client.post(f"/execute?task_id={task_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify status changed
        get_res = client.get(f"/task/{task_id}", headers=headers)
        assert get_res.json()["status"] == "processing"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
