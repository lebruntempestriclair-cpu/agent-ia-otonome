import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

# IMPORTANT: We need to import the app after setting environment variables
# or use a monkeypatch because settings are loaded at module level in main.py.

def test_api_key_required_when_enabled():
    """Test that API Key is required when REQUIRE_API_KEY is true"""
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secret-token"}):
        # We need to reload the module or re-import it to pick up the new env vars
        # if the app was already imported. In a real scenario, we might use a factory pattern.
        # For this test, we'll import it inside the patch context.
        import main
        import importlib
        importlib.reload(main)

        client = TestClient(main.app)

        # Unauthorized request
        response = client.post("/task/create", json={"title": "Test", "description": "Test"})
        assert response.status_code == 403

        # Authorized request
        response = client.post(
            "/task/create",
            json={"title": "Test", "description": "Test"},
            headers={"X-API-Key": "secret-token"}
        )
        assert response.status_code == 200

def test_internal_error_hides_details():
    """Test that internal errors return a generic message instead of leaking details"""
    import main
    import importlib
    # Ensure default settings for this test
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "false"}):
        importlib.reload(main)
        client = TestClient(main.app)

        # We need to force an exception in one of the routes.
        # Let's monkeypatch the logger or some other part to raise an exception.
        with patch("main.logger.info", side_effect=Exception("Database connection failed!")):
            response = client.post("/task/create", json={"title": "Test", "description": "Test"})

            assert response.status_code == 500
            assert response.json()["detail"] == "Internal server error"
            # Ensure the actual error message isn't in the response
            assert "Database connection failed!" not in str(response.content)

def test_api_key_fail_securely_if_not_set():
    """Test that the app fails securely if REQUIRE_API_KEY is true but API_KEY is missing"""
    with patch.dict(os.environ, {"REQUIRE_API_KEY": "true"}, clear=True):
        if "API_KEY" in os.environ:
            del os.environ["API_KEY"]

        import main
        import importlib
        importlib.reload(main)

        client = TestClient(main.app)

        # Any protected request should result in a 500 error due to misconfiguration,
        # but the message should be generic.
        response = client.post("/task/create", json={"title": "Test", "description": "Test"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
