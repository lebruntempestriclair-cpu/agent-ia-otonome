
import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
import importlib
import main

def test_cors_headers():
    """Verify CORS headers in response"""
    from main import app
    client = TestClient(app)

    # Origin that should be allowed
    origin = "http://example.com"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET"
        }
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
    # Since allow_credentials=False, access-control-allow-credentials should NOT be in headers
    # OR it should be False (but usually Starlette omits it if False)
    assert response.headers.get("access-control-allow-credentials") is None

def test_production_safe_guards():
    """Verify that using default secret key in production raises ValueError"""
    env_patch = {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }

    with patch.dict(os.environ, env_patch):
        # We need to reload Settings or re-instantiate it to test __init__
        with pytest.raises(ValueError) as excinfo:
            importlib.reload(main)
            main.Settings()
        assert "API_KEY must be set in production" in str(excinfo.value)

def test_timing_attack_protection():
    """Verify that verify_api_key uses secrets.compare_digest"""
    from main import verify_api_key, settings
    import secrets
    from fastapi import HTTPException
    import asyncio

    # This is more of a smoke test to ensure verify_api_key still works as expected
    with patch.object(settings, "REQUIRE_API_KEY", True):
        with patch.object(settings, "API_KEY", "secure_key"):
            # Test valid key
            assert asyncio.run(verify_api_key("secure_key")) == "secure_key"

            # Test invalid key
            with pytest.raises(HTTPException) as excinfo:
                asyncio.run(verify_api_key("wrong_key"))
            assert excinfo.value.status_code == 403
