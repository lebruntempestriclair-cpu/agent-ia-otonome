"""
Enhanced security tests for Agent IA Autonome
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

def test_production_default_key_safeguard():
    """Test that the application raises ValueError if default key is used in production"""
    # Import Settings inside the test to allow environment variable manipulation
    from main import Settings

    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }):
        with pytest.raises(ValueError) as excinfo:
            Settings()
        assert "API_KEY must be changed from default in production" in str(excinfo.value)

def test_production_with_custom_key():
    """Test that the application starts in production with a custom API key"""
    from main import Settings

    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "secure_and_custom_key"
    }):
        settings = Settings()
        assert settings.API_KEY == "secure_and_custom_key"
        assert settings.DEPLOYMENT_ENV == "production"

def test_security_headers():
    """Test that security headers are present in responses"""
    from main import app
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
