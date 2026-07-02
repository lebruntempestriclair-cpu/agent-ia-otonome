"""
Enhanced security tests for Agent IA Autonome
"""

import pytest
import os
from unittest.mock import patch
import importlib
import main

def test_production_default_key_safeguard():
    """
    Test that the application raises a ValueError if REQUIRE_API_KEY is true,
    API_KEY is default, and DEPLOYMENT_ENV is production.
    """
    env_vars = {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }

    with patch.dict(os.environ, env_vars):
        # We need to re-instantiate Settings since it's instantiated at module level
        with pytest.raises(ValueError) as excinfo:
            main.Settings()
        assert "SECURITY ERROR: Default API key cannot be used in production environment." in str(excinfo.value)

def test_production_custom_key_allowed():
    """
    Test that the application allows a custom API key in production.
    """
    env_vars = {
        "DEPLOYMENT_ENV": "production",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "secure_and_custom_key_123"
    }

    with patch.dict(os.environ, env_vars):
        settings = main.Settings()
        assert settings.API_KEY == "secure_and_custom_key_123"

def test_development_default_key_allowed():
    """
    Test that the application allows the default API key in development.
    """
    env_vars = {
        "DEPLOYMENT_ENV": "development",
        "REQUIRE_API_KEY": "true",
        "API_KEY": "default_secret_key"
    }

    with patch.dict(os.environ, env_vars):
        settings = main.Settings()
        assert settings.API_KEY == "default_secret_key"
