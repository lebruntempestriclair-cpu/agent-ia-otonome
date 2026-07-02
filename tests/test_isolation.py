import pytest
import io
import os
from unittest.mock import patch

# Mock settings before importing app
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    import main
    import importlib
    importlib.reload(main)
    from main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

API_HEADERS = {"X-API-Key": "test_secret_key"}

def test_user_isolation():
    """Test that User A's data is isolated from User B."""
    # User A uploads a file
    headers_a = {**API_HEADERS, "Authorization": "Bearer user_a"}
    file_a = io.BytesIO(b"user a data")
    client.post(
        "/dub",
        files={"file": ("video_a.mp4", file_a, "video/mp4")},
        data={"target_lang": "en", "gdpr_consent": "true"},
        headers=headers_a
    )

    # User B uploads a file
    headers_b = {**API_HEADERS, "Authorization": "Bearer user_b"}
    file_b = io.BytesIO(b"user b data")
    client.post(
        "/dub",
        files={"file": ("video_b.mp4", file_b, "video/mp4")},
        data={"target_lang": "en", "gdpr_consent": "true"},
        headers=headers_b
    )

    # Verify directories exist
    assert os.path.exists("uploads/user_a")
    assert os.path.exists("uploads/user_b")

    # Check that user_a's directory contains their file (or at least one file)
    files_a = os.listdir("uploads/user_a")
    assert any("video_a" in f or "final" in f or "-" in f for f in files_a) # job_id based naming

    # User A deletes their data
    client.delete("/user/data", headers=headers_a)
    assert not os.path.exists("uploads/user_a")
    assert os.path.exists("uploads/user_b") # User B's data should still be there

    # Cleanup
    client.delete("/user/data", headers=headers_b)
    assert not os.path.exists("uploads/user_b")
