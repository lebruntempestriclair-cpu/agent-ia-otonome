import pytest
import os
import secrets
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
API_KEY = "default_secret_key"
HEADERS = {"X-API-Key": API_KEY}

def test_health_optimization():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["status"] == "healthy"

def test_chunked_upload_flow():
    # 1. Start upload
    response = client.post(
        "/upload/start",
        params={"filename": "test.mp4", "total_size": 100, "chunk_size": 50},
        headers=HEADERS
    )
    assert response.status_code == 200
    upload_id = response.json()["upload_id"]

    # 2. Upload chunks
    client.post(f"/upload/chunk/{upload_id}/0", content=b"A" * 50, headers=HEADERS)
    client.post(f"/upload/chunk/{upload_id}/1", content=b"B" * 50, headers=HEADERS)

    # 3. Complete
    response = client.post(f"/upload/complete/{upload_id}", headers=HEADERS)
    assert response.status_code == 200
    assert "file_path" in response.json()

def test_dubbing_job_creation():
    # Setup: upload a file first
    filename = "video.mp4"
    start_res = client.post(
        "/upload/start",
        params={"filename": filename, "total_size": 10, "chunk_size": 10},
        headers=HEADERS
    )
    upload_id = start_res.json()["upload_id"]
    client.post(f"/upload/chunk/{upload_id}/0", content=b"dummydata", headers=HEADERS)
    client.post(f"/upload/complete/{upload_id}", headers=HEADERS)

    # Dubbing request
    dub_data = {
        "target_language": "fr",
        "voice_model": "premium",
        "style": "cheerful",
        "gdpr_consent": True
    }
    response = client.post(
        "/dub",
        json=dub_data,
        params={"filename": filename},
        headers=HEADERS
    )
    assert response.status_code == 200
    job = response.json()
    assert job["status"] == "queued"
    assert job["target_language"] == "fr"

    # Get status
    job_id = job["job_id"]
    status_res = client.get(f"/dub/{job_id}", headers=HEADERS)
    assert status_res.status_code == 200

def test_gdpr_endpoints():
    # Consent
    consent_data = {
        "user_id": "default_user",
        "consent_given": True
    }
    res = client.post("/user/consent", json=consent_data, headers=HEADERS)
    assert res.status_code == 200

    # Get Data
    res = client.get("/user/data", headers=HEADERS)
    assert res.status_code == 200
    assert "files" in res.json()

    # Delete Data
    res = client.delete("/user/data", headers=HEADERS)
    assert res.status_code == 200
