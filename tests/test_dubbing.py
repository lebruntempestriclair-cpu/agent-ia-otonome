import pytest
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dubbing_upload_no_consent():
    """Test that /dub fails without GDPR consent"""
    with open("tests/media/test_video.mp4", "rb") as f:
        response = client.post(
            "/dub",
            files={"file": ("test_video.mp4", f, "video/mp4")},
            data={"target_lang": "fr", "gdpr_consent": "false"}
        )
    assert response.status_code == 400
    assert "GDPR consent is mandatory" in response.json()["detail"]

def test_dubbing_upload_success():
    """Test that /dub succeeds with valid data and consent"""
    with open("tests/media/test_video.mp4", "rb") as f:
        response = client.post(
            "/dub",
            files={"file": ("test_video.mp4", f, "video/mp4")},
            data={"target_lang": "fr", "gdpr_consent": "true"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "job_id" in data

    # Check if file was saved
    job_id = data["job_id"]
    assert any(job_id in f for f in os.listdir("uploads"))
