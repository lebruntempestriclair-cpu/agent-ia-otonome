import pytest
import os
import io
import shutil
from fastapi.testclient import TestClient
from main import app, settings
from src.storage import StorageManager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup: ensure uploads dir is clean
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")
    # Reset settings for tests
    settings.REQUIRE_API_KEY = False
    yield
    # Teardown: clean up
    if os.path.exists("uploads"):
        shutil.rmtree("uploads")

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "development"

def test_dub_endpoint_missing_consent():
    file_content = b"fake video content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/dub",
        files={"file": ("test.mp4", file, "video/mp4")},
        data={
            "target_lang": "fr",
            "voice_id": "voice_1",
            "gdpr_consent": "false"
        }
    )
    assert response.status_code == 400
    assert "GDPR consent is mandatory" in response.json()["detail"]

def test_dub_endpoint_unsupported_extension():
    file_content = b"fake content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/dub",
        files={"file": ("test.txt", file, "text/plain")},
        data={
            "target_lang": "fr",
            "voice_id": "voice_1",
            "gdpr_consent": "true"
        }
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]

def test_dub_endpoint_success():
    # We need to ensure app.state is initialized (lifespan)
    # TestClient as a context manager triggers lifespan events
    with TestClient(app) as client:
        file_content = b"fake video content"
        file = io.BytesIO(file_content)

        response = client.post(
            "/dub",
            files={"file": ("test.mp4", file, "video/mp4")},
            data={
                "target_lang": "fr",
                "voice_id": "voice_1",
                "gdpr_consent": "true"
            }
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "job_id" in response.json()

def test_delete_user_data():
    with TestClient(app) as client:
        # First upload something
        file = io.BytesIO(b"content")
        client.post(
            "/dub",
            files={"file": ("test.mp4", file, "video/mp4")},
            data={"target_lang": "fr", "voice_id": "v1", "gdpr_consent": "true"}
        )

        # Verify directory exists
        assert os.path.exists("uploads/user_456")

        # Delete data
        response = client.delete("/user/data")
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify directory is gone
        assert not os.path.exists("uploads/user_456")

@pytest.mark.asyncio
async def test_storage_manager_size_limit():
    storage = StorageManager(upload_dir="test_uploads")
    storage.max_file_size = 10  # 10 bytes limit

    class MockFile:
        def __init__(self, content):
            self.content = io.BytesIO(content)
            self.filename = "test.mp4"
        async def read(self, n):
            return self.content.read(n)

    mock_file = MockFile(b"this is more than 10 bytes")

    with pytest.raises(ValueError, match="File size exceeds 700MB limit"):
        await storage.save_upload(mock_file, "user_test")

    if os.path.exists("test_uploads"):
        shutil.rmtree("test_uploads")
