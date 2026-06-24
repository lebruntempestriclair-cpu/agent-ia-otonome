import pytest
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_chunk():
    """Test uploading a chunk"""
    data = {
        "chunk_index": 0,
        "total_chunks": 2,
        "filename": "test_video.mp4",
        "upload_id": "test_session_123"
    }
    files = {"file": ("chunk_0", b"some binary data", "application/octet-stream")}
    response = client.post("/upload/chunk", data=data, files=files)
    assert response.status_code == 200
    assert response.json()["message"] == "Chunk 0/2 received"

def test_upload_complete():
    """Test completing an upload"""
    # First upload two chunks
    client.post("/upload/chunk", data={
        "chunk_index": 0, "total_chunks": 2, "filename": "test_video.mp4", "upload_id": "test_session_complete"
    }, files={"file": ("chunk_0", b"part1", "application/octet-stream")})

    client.post("/upload/chunk", data={
        "chunk_index": 1, "total_chunks": 2, "filename": "test_video.mp4", "upload_id": "test_session_complete"
    }, files={"file": ("chunk_1", b"part2", "application/octet-stream")})

    # Complete upload
    response = client.post("/upload/complete", data={
        "filename": "test_video.mp4",
        "upload_id": "test_session_complete",
        "total_chunks": 2
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Upload complete"
    assert "file_path" in response.json()

def test_start_dubbing():
    """Test starting the dubbing pipeline"""
    # Use valid API key if requirement is enabled in settings (it is in test_main.py patch)
    headers = {"X-API-Key": "test_secret_key"}
    # Need to provide gdpr_consent as form data
    data = {"gdpr_consent": "true"}
    response = client.post("/dub?video_path=uploads/test_video.mp4&target_lang=en", headers=headers, data=data)
    assert response.status_code == 200
    assert "Dubbing process started" in response.json()["message"]

def test_start_dubbing_no_consent():
    """Test starting the dubbing pipeline without consent should fail"""
    headers = {"X-API-Key": "test_secret_key"}
    data = {"gdpr_consent": "false"}
    response = client.post("/dub?video_path=uploads/test_video.mp4&target_lang=en", headers=headers, data=data)
    assert response.status_code == 400
    assert "GDPR consent is required" in response.json()["detail"]

def test_path_traversal_prevention():
    """Test that path traversal is prevented in upload endpoints"""
    data = {
        "chunk_index": 0,
        "total_chunks": 1,
        "filename": "../../evil.py",
        "upload_id": "session_123"
    }
    files = {"file": ("chunk_0", b"print('hacked')", "application/octet-stream")}
    client.post("/upload/chunk", data=data, files=files)

    # Complete upload and check that file is NOT in root
    client.post("/upload/complete", data={
        "filename": "../../evil.py",
        "upload_id": "session_123",
        "total_chunks": 1
    })

    assert not os.path.exists("evil.py")
    assert os.path.exists("uploads/evil.py")
