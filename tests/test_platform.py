import pytest
import os
import shutil
from fastapi.testclient import TestClient
from main import app, settings

client = TestClient(app)

def setup_module(module):
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def teardown_module(module):
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)

class TestChunkedUpload:
    def test_chunked_upload_flow(self):
        headers = {"X-API-Key": settings.API_KEY}
        upload_id = "test_upload_123"
        filename = "test_video.mp4"
        content = b"This is a dummy video file content split into chunks."
        chunk_size = 10
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        total_chunks = len(chunks)

        # Upload chunks
        for i, chunk in enumerate(chunks):
            response = client.post(
                "/upload/chunk",
                headers=headers,
                data={
                    "upload_id": upload_id,
                    "chunk_index": i,
                    "total_chunks": total_chunks
                },
                files={"file": (f"chunk_{i}", chunk)}
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

        # Complete upload
        response = client.post(
            "/upload/complete",
            headers=headers,
            data={
                "upload_id": upload_id,
                "filename": filename,
                "target_lang": "fr"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        task_id = data["task_id"]

        # Verify task status
        response = client.get(f"/task/{task_id}", headers=headers)
        assert response.status_code == 200
        task_data = response.json()
        assert task_data["status"] in ["pending", "processing", "completed"]

        # Wait for completion (optional, since it's a background task)
        # In a real test, we might poll until completed.

    def test_incomplete_upload(self):
        headers = {"X-API-Key": settings.API_KEY}
        upload_id = "incomplete_123"

        # Upload only 1 chunk out of 2
        client.post(
            "/upload/chunk",
            headers=headers,
            data={"upload_id": upload_id, "chunk_index": 0, "total_chunks": 2},
            files={"file": ("chunk_0", b"part1")}
        )

        response = client.post(
            "/upload/complete",
            headers=headers,
            data={"upload_id": upload_id, "filename": "fail.mp4"}
        )
        assert response.status_code == 400
        assert "Not all chunks received" in response.json()["detail"]
