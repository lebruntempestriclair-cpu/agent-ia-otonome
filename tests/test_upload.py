"""
Tests for chunked upload functionality
"""

import pytest
import os
import io
import shutil
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app, settings
settings.REQUIRE_API_KEY = False
client = TestClient(app)

def test_chunked_upload_and_reassembly():
    """Test the full flow of chunked upload and file reassembly"""
    settings.REQUIRE_API_KEY = False

    # 1. Create a task
    task_data = {"title": "Upload Test", "source_language": "fr", "target_language": "en"}
    res = client.post("/task/create", json=task_data)
    task_id = res.json()["task_id"]

    # 2. Upload chunks
    content1 = b"Hello "
    content2 = b"World!"
    total_chunks = 2

    # Chunk 0
    res1 = client.post(
        "/upload/chunk",
        data={"task_id": task_id, "chunk_index": 0, "total_chunks": total_chunks},
        files={"file": ("chunk0", io.BytesIO(content1), "application/octet-stream")}
    )
    assert res1.status_code == 200

    # Chunk 1
    res2 = client.post(
        "/upload/chunk",
        data={"task_id": task_id, "chunk_index": 1, "total_chunks": total_chunks},
        files={"file": ("chunk1", io.BytesIO(content2), "application/octet-stream")}
    )
    assert res2.status_code == 200

    # 3. Verify task status and media_url
    # Reassembly is now in background, so we might need to wait or check status change
    import time
    for _ in range(10):
        task_res = client.get(f"/task/{task_id}")
        task_info = task_res.json()
        if task_info["status"] == "ready":
            break
        time.sleep(0.1)

    assert task_info["status"] == "ready"
    assert task_info["media_url"].endswith(f"{task_id}_final.mp4")

    # 4. Verify reassembled file content
    final_path = task_info["media_url"]
    assert os.path.exists(final_path)
    with open(final_path, "rb") as f:
        assert f.read() == b"Hello World!"

    # Cleanup
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR)
        os.makedirs(settings.UPLOAD_DIR)
