"""
Unit tests for the Multilingual Voice Dubbing Platform
"""

import pytest
import os
import io
from unittest.mock import patch
from fastapi.testclient import TestClient

# Import app after patching environment if needed
from main import app, settings

client = TestClient(app)

def test_health_check():
    """Health check should be public and return 200"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_security_headers():
    """Verify that security headers are present"""
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers

def test_upload_flow():
    """Test the basic upload initialization and consent requirement"""
    # 1. Init Upload
    response = client.post("/upload/init")
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]
    assert upload_id is not None

    # 2. Upload Chunk
    file_content = b"test content"
    file = io.BytesIO(file_content)
    response = client.post(
        "/upload/chunk",
        data={"upload_id": upload_id, "chunk_index": 0},
        files={"file": ("test.mp4", file, "video/mp4")}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 3. Complete Upload without consent
    response = client.post(
        "/upload/complete",
        data={
            "upload_id": upload_id,
            "total_chunks": 1,
            "filename": "test.mp4",
            "title": "Test Project",
            "source_language": "en",
            "target_language": "fr",
            "voice_id": "voice_1",
            "consent_given": False
        }
    )
    assert response.status_code == 400
    assert "consent" in response.json()["detail"].lower()

    # 4. Complete Upload with consent
    # Re-upload chunk because assemble_chunks cleans up
    file = io.BytesIO(file_content)
    client.post(
        "/upload/chunk",
        data={"upload_id": upload_id, "chunk_index": 0},
        files={"file": ("test.mp4", file, "video/mp4")}
    )

    response = client.post(
        "/upload/complete",
        data={
            "upload_id": upload_id,
            "total_chunks": 1,
            "filename": "test.mp4",
            "title": "Test Project",
            "source_language": "en",
            "target_language": "fr",
            "voice_id": "voice_1",
            "consent_given": True
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processing"
    assert "project_id" in response.json()

def test_get_project_status():
    """Test getting project status"""
    response = client.get("/project/some-id")
    assert response.status_code == 200
    assert response.json()["id"] == "some-id"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
