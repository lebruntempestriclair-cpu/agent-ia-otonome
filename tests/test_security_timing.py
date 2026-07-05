import os
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest

# Mock settings before importing app
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secure_test_key"}):
    from main import app
    client = TestClient(app)

def test_api_key_validation_with_compare_digest():
    """Test that the API key validation still works correctly after the update"""
    # Valid key
    response = client.get("/tasks", headers={"X-API-Key": "secure_test_key"})
    assert response.status_code == 200

    # Invalid key
    response = client.get("/tasks", headers={"X-API-Key": "wrong_key"})
    assert response.status_code == 403

    # Missing key
    response = client.get("/tasks")
    assert response.status_code == 403

def test_health_check_no_key_required():
    """Verify health check doesn't require key even if REQUIRE_API_KEY is true"""
    response = client.get("/health")
    assert response.status_code == 200
