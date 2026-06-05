import pytest
from fastapi.testclient import TestClient
from main import app, settings
import os
from unittest.mock import patch

client = TestClient(app)

def test_no_information_leakage_on_error():
    """
    Test that the application DOES NOT leak exception details in the response.
    """
    with patch("main.logger.info", side_effect=Exception("Database connection failed at 192.168.1.100")):
        response = client.post("/task/create", json={"title": "test", "description": "test"})
        assert response.status_code == 500
        # Should NOT contain sensitive details
        assert "Database connection failed" not in response.json()["detail"]
        assert response.json()["detail"] == "Internal server error"

def test_authentication_required():
    """
    Test that sensitive endpoints require an API key when configured.
    """
    with patch.object(settings, 'require_api_key', True):
        with patch.object(settings, 'api_key', 'secret-key'):
            # Missing key
            response = client.post("/task/create", json={"title": "test", "description": "test"})
            assert response.status_code == 403
            assert response.json()["detail"] == "Invalid or missing API Key"

            # Wrong key
            response = client.post("/task/create",
                                  json={"title": "test", "description": "test"},
                                  headers={"X-API-Key": "wrong-key"})
            assert response.status_code == 403

            # Correct key
            response = client.post("/task/create",
                                  json={"title": "test", "description": "test"},
                                  headers={"X-API-Key": "secret-key"})
            assert response.status_code == 200

def test_cors_restricted_in_development():
    """
    Test that CORS is restricted to localhost:3000 in development.
    """
    # In development (default in Settings)
    with patch.object(settings, 'deployment_env', 'development'):
        # Evil origin
        response = client.options("/task/create", headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "POST"
        })
        # Should be rejected or at least not have Access-Control-Allow-Origin: http://evil.com
        assert response.headers.get("access-control-allow-origin") != "http://evil.com"

        # Allowed origin
        response = client.options("/task/create", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
