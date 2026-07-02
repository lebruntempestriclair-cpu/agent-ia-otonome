import pytest
import io
import os
from unittest.mock import patch

# Mock settings
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    import main
    import importlib
    importlib.reload(main)
    from main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

API_HEADERS = {"X-API-Key": "test_secret_key"}

def test_chunked_upload_flow():
    """Test the full flow of a chunked upload."""
    # 1. Start upload
    response = client.post("/upload/start", headers=API_HEADERS)
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]

    # 2. Upload chunks
    chunks = [b"Chunk 1 ", b"Chunk 2 ", b"Chunk 3"]
    for i, chunk_data in enumerate(chunks):
        file = io.BytesIO(chunk_data)
        response = client.post(
            "/upload/chunk",
            data={"upload_id": upload_id, "chunk_index": i},
            files={"file": ("blob", file, "application/octet-stream")},
            headers=API_HEADERS
        )
        assert response.status_code == 200

    # 3. Finalize via /dub
    response = client.post(
        "/dub",
        data={
            "target_lang": "en",
            "gdpr_consent": "true",
            "upload_id": upload_id,
            "filename": "final_video.mp4"
        },
        headers=API_HEADERS
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify final file
    final_path = "uploads/user_default/final_video.mp4"
    assert os.path.exists(final_path)
    with open(final_path, 'rb') as f:
        assert f.read() == b"".join(chunks)

    # Cleanup
    os.remove(final_path)
