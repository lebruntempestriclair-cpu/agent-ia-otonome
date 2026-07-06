"""
Tests for the constant-time API key verification security fix.
"""

import pytest
from fastapi.testclient import TestClient
from main import app, settings

def test_api_key_verification():
    # Save original settings
    original_require_api_key = settings.REQUIRE_API_KEY
    original_api_key = settings.API_KEY

    try:
        # Manually patch settings object
        settings.REQUIRE_API_KEY = True
        settings.API_KEY = "secure_test_key"

        client = TestClient(app)

        # Test valid API key
        response = client.get("/tasks", headers={"X-API-Key": "secure_test_key"})
        assert response.status_code == 200

        # Test invalid API key
        response = client.get("/tasks", headers={"X-API-Key": "wrong_key"})
        assert response.status_code == 403
        assert response.json() == {"detail": "Could not validate credentials"}

        # Test missing API key
        response = client.get("/tasks")
        assert response.status_code == 403

    finally:
        # Restore original settings
        settings.REQUIRE_API_KEY = original_require_api_key
        settings.API_KEY = original_api_key
