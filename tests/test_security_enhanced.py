"""
Enhanced security tests for Agent IA Autonome
"""

import pytest
import os
from unittest.mock import patch
from main import Settings

class TestProductionSafeguard:
    """Tests for the production API key safeguard"""

    def test_production_with_default_key_fails(self):
        """Test that Settings fails in production if API key is default"""
        env_vars = {
            "REQUIRE_API_KEY": "true",
            "DEPLOYMENT_ENV": "production",
            "API_KEY": "default_secret_key"
        }
        with patch.dict(os.environ, env_vars):
            with pytest.raises(ValueError) as excinfo:
                Settings()
            assert "API_KEY must be changed from default in production environment" in str(excinfo.value)

    def test_production_with_custom_key_succeeds(self):
        """Test that Settings succeeds in production if API key is custom"""
        env_vars = {
            "REQUIRE_API_KEY": "true",
            "DEPLOYMENT_ENV": "production",
            "API_KEY": "my_secure_prod_key"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.API_KEY == "my_secure_prod_key"

    def test_development_with_default_key_succeeds(self):
        """Test that Settings succeeds in development even if API key is default"""
        env_vars = {
            "REQUIRE_API_KEY": "true",
            "DEPLOYMENT_ENV": "development",
            "API_KEY": "default_secret_key"
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.API_KEY == "default_secret_key"
