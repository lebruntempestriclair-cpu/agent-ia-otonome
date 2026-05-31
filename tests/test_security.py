
import pytest
from fastapi.testclient import TestClient
from main import app, settings
import os

client = TestClient(app)

class TestSecurity:
    """Security tests for API Key authentication"""

    def test_health_check_no_key_required(self):
        """Health check should always be accessible without a key"""
        # Ensure key is not required for health check even if REQUIRE_API_KEY is true
        # In our implementation, health check doesn't have the dependency
        response = client.get("/health")
        assert response.status_code == 200

    def test_protected_route_without_key(self, monkeypatch):
        """Protected routes should return 403 when key is required but missing"""
        monkeypatch.setattr(settings, "require_api_key", True)
        monkeypatch.setattr(settings, "api_key", "test_key")

        response = client.get("/tasks")
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden: Invalid API Key"

    def test_protected_route_with_invalid_key(self, monkeypatch):
        """Protected routes should return 403 when key is invalid"""
        monkeypatch.setattr(settings, "require_api_key", True)
        monkeypatch.setattr(settings, "api_key", "test_key")

        response = client.get("/tasks", headers={"X-API-Key": "wrong_key"})
        assert response.status_code == 403

    def test_protected_route_with_valid_key(self, monkeypatch):
        """Protected routes should return 200 when key is valid"""
        monkeypatch.setattr(settings, "require_api_key", True)
        monkeypatch.setattr(settings, "api_key", "test_key")

        response = client.get("/tasks", headers={"X-API-Key": "test_key"})
        assert response.status_code == 200

    def test_no_key_required_by_default(self, monkeypatch):
        """Routes should be accessible without key when REQUIRE_API_KEY is false"""
        monkeypatch.setattr(settings, "require_api_key", False)

        response = client.get("/tasks")
        assert response.status_code == 200

    def test_error_message_not_leaking(self, monkeypatch):
        """Internal server errors should return generic messages"""
        import main

        # Monkeypatch logger.info to raise an exception when called in the handler
        def mock_logger_info(*args, **kwargs):
            raise Exception("Secret database connection string leaked!")

        monkeypatch.setattr(main.logger, "info", mock_logger_info)

        # Disable API key for this test to reach the handler
        monkeypatch.setattr(settings, "require_api_key", False)

        response = client.post("/execute?task_id=123")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert "Secret" not in response.text
