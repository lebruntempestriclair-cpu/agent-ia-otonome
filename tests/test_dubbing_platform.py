import pytest
import os
import io
import shutil
from fastapi.testclient import TestClient
from main import app
from services import pipeline

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: ensure uploads dir exists
    os.makedirs("uploads", exist_ok=True)
    yield
    # Teardown: clean up uploads dir
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")
    os.makedirs("uploads", exist_ok=True)
    pipeline.projects.clear()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chunked_upload_flow():
    # 1. Init
    init_data = {
        "filename": "test_video.mp4",
        "total_size": 100,
        "content_type": "video/mp4"
    }
    response = client.post("/upload/init", json=init_data)
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]

    # 2. Upload Chunk
    chunk_content = b"fake video data"
    files = {"file": ("chunk_0", io.BytesIO(chunk_content), "application/octet-stream")}
    data = {"upload_id": upload_id, "chunk_index": 0}
    response = client.post("/upload/chunk", data=data, files=files)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 3. Complete
    complete_data = {
        "upload_id": upload_id,
        "total_chunks": 1
    }
    response = client.post("/upload/complete", json=complete_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "test_video.mp4" in response.json()["filepath"]
    assert os.path.exists(response.json()["filepath"])

def test_project_creation_and_pipeline():
    # Create a dummy file first
    video_path = "uploads/dummy.mp4"
    with open(video_path, "wb") as f:
        f.write(b"dummy data")

    project_data = {
        "name": "Test Project",
        "source_language": "en",
        "target_language": "fr",
        "voice_id": "female_1",
        "consent_given": True
    }

    # Create project
    response = client.post(f"/project/create?video_path={video_path}", json=project_data)
    assert response.status_code == 200
    project_id = response.json()["project"]["id"]
    assert response.json()["success"] is True

    # Check status
    response = client.get(f"/project/{project_id}")
    assert response.status_code == 200
    assert response.json()["status"] in ["pending", "transcribing", "translating", "synthesizing", "syncing", "completed"]

def test_project_creation_no_consent():
    project_data = {
        "name": "Test Project",
        "source_language": "en",
        "target_language": "fr",
        "voice_id": "female_1",
        "consent_given": False
    }
    response = client.post("/project/create?video_path=none", json=project_data)
    assert response.status_code == 400
    assert "consent" in response.json()["detail"]

def test_list_projects():
    response = client.get("/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
