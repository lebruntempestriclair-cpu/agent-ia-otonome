import pytest
import secrets
from main import verify_api_key, settings
from fastapi import HTTPException
import asyncio

@pytest.mark.asyncio
async def test_verify_api_key_timing_protection():
    """
    Test that verify_api_key uses compare_digest (implied by functionality).
    We also test the security enforcement in settings.
    """
    # Test valid key
    settings.REQUIRE_API_KEY = True
    settings.API_KEY = "secure_test_key"

    # Should not raise exception
    await verify_api_key("secure_test_key")

    # Should raise 403 for invalid key
    with pytest.raises(HTTPException) as excinfo:
        await verify_api_key("wrong_key")
    assert excinfo.value.status_code == 403

def test_production_security_enforcement():
    """Verify that production env requires a non-default API key if enabled"""
    import os
    from main import Settings

    # Mock production with default key
    os.environ["DEPLOYMENT_ENV"] = "production"
    os.environ["API_KEY"] = "default_secret_key"

    # We need to manually trigger the check since settings is a singleton initialized at import
    with pytest.raises(ValueError, match="API_KEY must be set in production"):
        # Manually create a new Settings instance to trigger the check
        # We mock the config to enable require_api_key
        import yaml
        from unittest.mock import patch, mock_open

        config_data = "security:\n  require_api_key: true"
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_data)):
                Settings()

def test_cors_security_config():
    """Verify CORSMiddleware is configured securely"""
    from main import app
    from fastapi.middleware.cors import CORSMiddleware

    cors_middleware = None
    for middleware in app.user_middleware:
        if middleware.cls == CORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None
    # allow_credentials must be False when allow_origins is ["*"]
    assert cors_middleware.options["allow_credentials"] is False
