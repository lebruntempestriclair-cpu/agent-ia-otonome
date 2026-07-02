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

def test_file_size_limit():
    """Test that files exceeding 700MB are rejected."""
    # We can't easily send 700MB in a test client without memory issues,
    # but we can mock os.path.getsize

    file_content = b"fake content"
    file = io.BytesIO(file_content)

    with patch("os.path.getsize", return_value=800 * 1024 * 1024):
        response = client.post(
            "/dub",
            files={"file": ("large.mp4", file, "video/mp4")},
            data={"target_lang": "en", "gdpr_consent": "true"},
            headers=API_HEADERS
        )
        assert response.status_code == 413
        assert "File too large" in response.json()["detail"]

def test_cors_production():
    """Test CORS settings in production environment."""
    with patch.dict(os.environ, {"DEPLOYMENT_ENV": "production", "ALLOWED_ORIGINS": "https://example.com"}):
        importlib.reload(main)
        from main import app as prod_app
        prod_client = TestClient(prod_app)

        # Options request for CORS
        response = prod_client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.headers.get("access-control-allow-origin") == "https://example.com"

        response = prod_client.options(
            "/health",
            headers={
                "Origin": "https://malicious.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.headers.get("access-control-allow-origin") is None
