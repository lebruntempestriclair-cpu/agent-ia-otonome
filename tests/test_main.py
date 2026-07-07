"""
Unit tests for the Agent IA Autonome application
"""

import pytest
import os
import json
import shutil
import asyncio
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app, settings

@pytest.fixture(scope="module", autouse=True)
def setup_test_env():
    """Setup and teardown for test environment"""
    # Patch settings for testing
    settings.REQUIRE_API_KEY = True
    settings.API_KEY = "test_secret_key"
    settings.DEPLOYMENT_ENV = "testing"

    # Ensure upload dir exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(settings.DB_PATH, "w") as f:
        json.dump({}, f)

    yield

    # Cleanup
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)

class TestSecurity:
    """Tests for security features"""

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        with TestClient(app) as client:
            # For POST /task/create, we provide a valid body to avoid 422
            task_data = {"title": "Test", "description": "Test"}

            endpoints = [
                ("/task/create", "post", {"json": task_data}),
                ("/task/task_123", "get", {}),
                ("/tasks", "get", {}),
                ("/execute?task_id=task_123", "post", {}),
                ("/upload/chunk", "post", {"data": {"upload_id": "invalid"}})
            ]
            for url, method, kwargs in endpoints:
                func = getattr(client, method)
                response = func(url, **kwargs)
                assert response.status_code == 403, f"Failed for {method.upper()} {url}"
                assert response.json() == {"detail": "Could not validate credentials"}

    def test_authenticated_access(self):
        """Test that sensitive endpoints allow access with valid API key"""
        with TestClient(app) as client:
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
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200 and correct structure"""
        with TestClient(app) as client:
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
        with TestClient(app) as client:
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
        with TestClient(app) as client:
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
        with TestClient(app) as client:
            headers = {"X-API-Key": "test_secret_key"}
            response = client.get("/task/task_123", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert "status" in data
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        with TestClient(app) as client:
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
        with TestClient(app) as client:
            headers = {"X-API-Key": "test_secret_key"}
            response = client.post("/execute?task_id=task_123", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data

class TestChunkedUpload:
    """Tests for chunked upload functionality"""

    def test_chunk_upload_flow(self):
        """Test the full flow of chunked upload and assembly"""
        import uuid
        with TestClient(app) as client:
            headers = {"X-API-Key": "test_secret_key"}
            upload_id = str(uuid.uuid4())
            filename = "test_video.mp4"
            total_chunks = 2

            # Upload chunk 1 (out of order)
            response = client.post(
                "/upload/chunk",
                data={
                    "upload_id": upload_id,
                    "chunk_index": 1,
                    "total_chunks": total_chunks,
                    "filename": filename
                },
                files={"file": ("chunk1", b"world")},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == "chunk_received"

            # Upload chunk 0
            response = client.post(
                "/upload/chunk",
                data={
                    "upload_id": upload_id,
                    "chunk_index": 0,
                    "total_chunks": total_chunks,
                    "filename": filename
                },
                files={"file": ("chunk0", b"hello ")},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert "file_path" in data

            # Verify assembled file content
            file_path = data["file_path"]
            with open(file_path, "rb") as f:
                content = f.read()
                assert content == b"hello world"

    @pytest.mark.asyncio
    async def test_concurrent_chunk_upload(self):
        """Test concurrent chunk uploads to verify locking mechanism"""
        import uuid
        from httpx import AsyncClient

        headers = {"X-API-Key": "test_secret_key"}
        upload_id = str(uuid.uuid4())
        filename = "concurrent.txt"
        total_chunks = 10

        async def upload(i):
            async with AsyncClient(app=app, base_url="http://testserver") as c:
                return await c.post(
                    "/upload/chunk",
                    data={
                        "upload_id": upload_id,
                        "chunk_index": i,
                        "total_chunks": total_chunks,
                        "filename": filename
                    },
                    files={"file": (f"chunk{i}", f"part{i}".encode())},
                    headers=headers
                )

        # Use asyncio.gather to run them concurrently in the event loop
        tasks = [upload(i) for i in range(total_chunks)]
        results = await asyncio.gather(*tasks)

        # At least one response should be "completed"
        # Others will be "chunk_received"
        statuses = [r.json()["status"] for r in results]
        assert "completed" in statuses
        assert statuses.count("chunk_received") == total_chunks - 1

        # Verify assembly
        for r in results:
            if r.json()["status"] == "completed":
                file_path = r.json()["file_path"]
                with open(file_path, "rb") as f:
                    content = f.read()
                    # Parts should be in order regardless of upload order
                    expected = "".join([f"part{i}" for i in range(total_chunks)]).encode()
                    assert content == expected

    def test_invalid_upload_id(self):
        """Test upload with invalid upload_id format"""
        with TestClient(app) as client:
            headers = {"X-API-Key": "test_secret_key"}
            response = client.post(
                "/upload/chunk",
                data={
                    "upload_id": "not-a-uuid",
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "filename": "test.mp4"
                },
                files={"file": ("file", b"content")},
                headers=headers
            )
            assert response.status_code == 400
            assert response.json()["detail"] == "Invalid upload_id format"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
