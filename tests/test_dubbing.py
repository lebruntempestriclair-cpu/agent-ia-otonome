import pytest
import io
import os
from unittest.mock import patch

# Mock settings before importing app to test authentication
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    import main
    import importlib
    importlib.reload(main)
    from main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

HEADERS = {"X-API-Key": "test_secret_key"}

def test_dubbing_endpoint_no_consent():
    """Test that /dub fails without GDPR consent."""
    file_content = b"fake video content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/dub",
        files={"file": ("test.mp4", file, "video/mp4")},
        data={
            "target_lang": "en",
            "voice_id": "female_1",
            "gdpr_consent": "false"
        },
        headers=HEADERS
    )
    assert response.status_code == 400
    assert "GDPR consent is mandatory" in response.json()["detail"]

def test_dubbing_endpoint_invalid_extension():
    """Test that /dub fails with unsupported file extension."""
    file_content = b"fake exe content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/dub",
        files={"file": ("test.exe", file, "application/x-msdownload")},
        data={
            "target_lang": "en",
            "voice_id": "female_1",
            "gdpr_consent": "true"
        },
        headers=HEADERS
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_dubbing_endpoint_success():
    """Test successful dubbing job creation."""
    file_content = b"fake video content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/dub",
        files={"file": ("test.mp4", file, "video/mp4")},
        data={
            "target_lang": "en",
            "voice_id": "female_1",
            "gdpr_consent": "true"
        },
        headers=HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "job_id" in data
    assert "Job started successfully" in data["message"]

def test_delete_user_data():
    """Test GDPR 'Right to be forgotten' endpoint."""
    response = client.delete("/user/data", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "deleted" in response.json()["message"]
