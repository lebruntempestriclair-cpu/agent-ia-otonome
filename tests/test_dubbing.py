import pytest
import io
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
headers = {"X-API-Key": "test_secret_key"}

def test_dubbing_upload_flow():
    # 1. Init upload
    response = client.post(
        "/dubbing/upload/init",
        json={"filename": "video.mp4", "total_chunks": 2},
        headers=headers
    )
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]

    # 2. Upload chunks using multipart/form-data
    # Chunk 1
    file_content_1 = b"chunk1 content"
    files_1 = {"file": ("chunk1", io.BytesIO(file_content_1), "application/octet-stream")}
    data_1 = {"upload_id": upload_id, "chunk_index": 0}
    response = client.post(
        "/dubbing/upload/chunk",
        data=data_1,
        files=files_1,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_complete"] is False

    # Chunk 2
    file_content_2 = b"chunk2 content"
    files_2 = {"file": ("chunk2", io.BytesIO(file_content_2), "application/octet-stream")}
    data_2 = {"upload_id": upload_id, "chunk_index": 1}
    response = client.post(
        "/dubbing/upload/chunk",
        data=data_2,
        files=files_2,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["is_complete"] is True

@pytest.mark.asyncio
async def test_dubbing_process_flow():
    # 0. We need a valid upload_id for get_upload_path to return something if we wanted to be thorough
    # but the code has a fallback. Let's do a quick init.
    response = client.post(
        "/dubbing/upload/init",
        json={"filename": "test.mp4", "total_chunks": 1},
        headers=headers
    )
    upload_id = response.json()["upload_id"]

    # 1. Start process
    response = client.post(
        "/dubbing/process",
        json={"upload_id": upload_id, "target_lang": "fr"},
        headers=headers
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # 2. Check status (initially processing)
    response = client.get(f"/dubbing/status/{job_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "processing"

    # 3. Wait for completion (simulation)
    await asyncio.sleep(0.1)
    response = client.get(f"/dubbing/status/{job_id}", headers=headers)
    assert response.status_code == 200
    assert "step" in response.json()
