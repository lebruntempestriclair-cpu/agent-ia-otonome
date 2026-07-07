import pytest
import os
import secrets
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

def test_secrets_compare_digest_used():
    """Verify that secrets.compare_digest is used for API key validation"""
    # We need to reload or re-import to ensure settings are patched
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secure_key"}):
        import main
        from importlib import reload
        reload(main)

        client = TestClient(main.app)

        with patch("secrets.compare_digest", side_effect=secrets.compare_digest) as mock_compare:
            response = client.get("/tasks", headers={"X-API-Key": "secure_key"})
            assert response.status_code == 200
            mock_compare.assert_called()

def test_cors_credentials_disabled():
    """Verify that allow_credentials is set to False for CORS"""
    from main import app
    from fastapi.testclient import TestClient
    client = TestClient(app)

    # Preflight request
    headers = {
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-API-Key",
    }
    response = client.options("/task/create", headers=headers)

    # If allow_credentials is False, Access-Control-Allow-Credentials should not be 'true'
    assert response.headers.get("access-control-allow-credentials") is None

def test_http_exception_not_masked():
    """Verify that HTTPException is not masked by generic Exception catch"""
    # This is a bit tricky to test with TestClient because it catches exceptions
    # But we can test the logic by calling the handler directly if it wasn't for Depends
    # Instead, we'll verify the code structure via inspection or trust the unit tests
    # Actually, we can trigger a 403 via verify_api_key and ensure it's returned as 403
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secure_key"}):
        import main
        from importlib import reload
        reload(main)
        client = TestClient(main.app)

        response = client.get("/tasks", headers={"X-API-Key": "wrong_key"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Could not validate credentials"

def test_settings_production_requirement():
    """Verify that Settings raises ValueError in production if API_KEY is missing and required"""
    from main import Settings

    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": ""
    }):
        # We need to clear the env var to make sure os.getenv("API_KEY") returns None or ""
        with patch("os.getenv", side_effect=lambda k, d=None: {"DEPLOYMENT_ENV": "production", "REQUIRE_API_KEY": "true", "API_KEY": ""}.get(k, d)):
            with pytest.raises(ValueError, match="API_KEY must be set when REQUIRE_API_KEY is true in production"):
                Settings()

if __name__ == "__main__":
    pytest.main([__file__])
