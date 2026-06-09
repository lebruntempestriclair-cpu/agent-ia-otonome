"""
Security regression tests for Agent IA Autonome
"""

import pytest
from fastapi.testclient import TestClient
from main import app, settings
from unittest.mock import patch

client = TestClient(app)

class TestSecurityLeakage:
    """Tests for information leakage in error responses"""

    def test_error_response_does_not_leak_details(self):
        """Test that 500 error responses do not leak exception details"""
        # Patch the logger in create_task to raise an exception
        # We need to patch where it is used in main.py
        with patch("main.logger.info") as mock_info:
            mock_info.side_effect = Exception("Sensitive internal error message")

            task_data = {
                "title": "Test Task",
                "description": "This is a test task"
            }

            # Ensure API key is not required for this test to simplify
            with patch.object(settings, "require_api_key", False):
                response = client.post("/task/create", json=task_data)

            assert response.status_code == 500
            data = response.json()
            assert "Sensitive internal error message" not in data["detail"]
            assert data["detail"] == "Internal server error"

class TestAPIKeyAuth:
    """Tests for API key authentication"""

    def test_unauthorized_access_when_required(self):
        """Test that access is denied when API key is required but missing or wrong"""
        with patch.object(settings, "require_api_key", True):
            with patch.object(settings, "api_key", "secret-key"):
                # No key
                response = client.get("/tasks")
                assert response.status_code == 403

                # Wrong key
                response = client.get("/tasks", headers={"X-API-Key": "wrong-key"})
                assert response.status_code == 403

    def test_authorized_access_when_required(self):
        """Test that access with correct key is authorized"""
        with patch.object(settings, "require_api_key", True):
            with patch.object(settings, "api_key", "secret-key"):
                response = client.get("/tasks", headers={"X-API-Key": "secret-key"})
                assert response.status_code == 200

    def test_access_when_not_required(self):
        """Test that access is granted without key when not required"""
        with patch.object(settings, "require_api_key", False):
            response = client.get("/tasks")
            assert response.status_code == 200

class TestCORSSecurity:
    """Tests for CORS configuration security"""

    def test_cors_wildcard_and_credentials_safety(self):
        """
        Verify that allow_credentials is False if wildcard origin is used,
        to prevent FastAPI crash and browser security issues.
        """
        # Since middleware is added at app creation, we check the actual app instance
        from main import app as main_app
        for middleware in main_app.user_middleware:
            if "CORSMiddleware" in str(middleware.cls):
                if "*" in middleware.options.get("allow_origins", []):
                    assert middleware.options.get("allow_credentials") is False

    def test_cors_headers_present(self):
        """Verify CORS headers are present in response"""
        response = client.options(
            "/health",
            headers={
                "Origin": "https://any-site.com",
                "Access-Control-Request-Method": "GET",
            }
        )
        assert "Access-Control-Allow-Origin" in response.headers
