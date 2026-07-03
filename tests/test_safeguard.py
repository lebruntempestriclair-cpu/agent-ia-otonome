import pytest
import os
from unittest.mock import patch
from main import Settings

def test_production_safeguard_raises_error():
    """Test that Settings raises ValueError in production with default API key"""
    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }):
        with pytest.raises(ValueError) as excinfo:
            Settings()
        assert "Default API key is not allowed in production environment" in str(excinfo.value)

def test_production_safeguard_allows_secure_key():
    """Test that Settings allows production with a non-default API key"""
    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "a_very_secure_and_long_api_key_123"
    }):
        # Should not raise any error
        settings = Settings()
        assert settings.API_KEY == "a_very_secure_and_long_api_key_123"

def test_development_allows_default_key():
    """Test that Settings allows development with default API key"""
    with patch.dict(os.environ, {
        "DEPLOYMENT_ENV": "development",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }):
        # Should not raise any error
        settings = Settings()
        assert settings.API_KEY == "default_secret_key"
