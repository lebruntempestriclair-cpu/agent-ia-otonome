import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chunked_upload():
    file_content = b"fake video chunk content"
    file = io.BytesIO(file_content)

    data = {
        "upload_id": "test_upload_123",
        "chunk_index": 0,
        "total_chunks": 1
    }
    files = {"file": ("test.mp4", file, "video/mp4")}

    response = client.post("/upload", data=data, files=files)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["upload_id"] == "test_upload_123"

def test_create_project():
    project_data = {
        "name": "Test Project",
        "source_language": "fr",
        "target_language": "en",
        "voice_style": "natural",
        "media_url": "s3://bucket/test.mp4"
    }
    response = client.post("/projects", json=project_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "project_id" in response.json()

def test_get_project_status():
    project_id = "test-uuid"
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["project_id"] == project_id
    assert "status" in response.json()

def test_execute_pipeline():
    project_id = "test-uuid"
    response = client.post(f"/projects/{project_id}/execute")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_get_results():
    project_id = "test-uuid"
    response = client.get(f"/results/{project_id}")
    assert response.status_code == 200
    assert "video_url" in response.json()
    assert "metrics" in response.json()
    assert "wer" in response.json()["metrics"]
