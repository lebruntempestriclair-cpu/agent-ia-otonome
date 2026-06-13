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
        task_data = {"title": "Test", "description": "Test", "gdpr_consent": True}
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
    
    def test_create_task_with_oauth(self):
        """Test creating a new task using OAuth token"""
        headers = {"Authorization": "Bearer simulated-oauth-token-123"}
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": 1,
            "gdpr_consent": True
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data

    def test_create_task_no_gdpr_fails(self):
        """Test creating task without GDPR consent fails"""
        headers = {"X-API-Key": "test_secret_key"}
        task_data = {
            "title": "Test Task",
            "description": "No consent",
            "gdpr_consent": False
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 400
        assert "GDPR consent is required" in response.json()["detail"]

    def test_create_dubbing_task(self):
        """Test creating a task with dubbing-specific fields"""
        headers = {"X-API-Key": "test_secret_key"}
        task_data = {
            "title": "Dubbing Project",
            "description": "Translate to French",
            "file_url": "http://example.com/video.mp4",
            "source_language": "en",
            "target_language": "fr",
            "voice_id": "female-1",
            "gdpr_consent": True
        }
        response = client.post("/task/create", json=task_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["task_id"].startswith("task_")
    
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
        # Create a task first
        task_data = {"title": "Retrieval Test", "description": "Test", "gdpr_consent": True}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        response = client.get(f"/task/{task_id}", headers=headers)
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

class TestUploads:
    """Tests for chunked media uploads"""

    def test_chunked_upload_flow(self):
        headers = {"Authorization": "Bearer simulated-oauth-token-123"}

        # 1. Upload chunk
        chunk_data = {"file_id": "vid_123", "chunk_index": 0, "chunk_data": "SGVsbG8="}
        res = client.post("/upload/chunk", json=chunk_data, headers=headers)
        assert res.status_code == 200
        assert res.json()["success"] is True

        # 2. Finalize
        res = client.post("/upload/finalize?file_id=vid_123&total_chunks=1", headers=headers)
        assert res.status_code == 200
        assert "file_url" in res.json()

class TestDubbingPipeline:
    """Tests for the dubbing pipeline and progress tracking"""

    def test_task_lifecycle_and_progress(self):
        """Test the full lifecycle from creation to execution and progress tracking"""
        headers = {"X-API-Key": "test_secret_key"}

        # 1. Create Task
        task_data = {"title": "Lifecycle Test", "description": "Testing progress", "gdpr_consent": True}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        # 2. Check initial progress
        prog_res = client.get(f"/task/{task_id}/progress", headers=headers)
        assert prog_res.status_code == 200
        assert prog_res.json()["progress"] == 0
        assert prog_res.json()["metrics"]["wer"] is None

        # 3. Execute Task (Note: In TestClient, BackgroundTasks run synchronously)
        exec_res = client.post(f"/execute?task_id={task_id}", headers=headers)
        assert exec_res.status_code == 200
        assert exec_res.json()["success"] is True

        # 4. Check final status and metrics
        final_res = client.get(f"/task/{task_id}/progress", headers=headers)
        data = final_res.json()
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["metrics"]["wer"] == 0.05
        assert data["metrics"]["mos"] == 4.2
        assert data["metrics"]["latency_ms"] == 1200

    def test_execute_nonexistent_task(self):
        """Test executing a task that doesn't exist"""
        headers = {"X-API-Key": "test_secret_key"}
        response = client.post("/execute?task_id=nonexistent", headers=headers)
        assert response.status_code == 404

class TestTaskExecution:
    """Tests for task execution"""
    
    def test_execute_task(self):
        """Test executing a task"""
        headers = {"X-API-Key": "test_secret_key"}
        # First create the task since we are now using tasks_db
        task_data = {"title": "Execution Test", "description": "Test", "gdpr_consent": True}
        create_res = client.post("/task/create", json=task_data, headers=headers)
        task_id = create_res.json()["task_id"]

        response = client.post(f"/execute?task_id={task_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
