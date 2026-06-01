import pytest
from fastapi.testclient import TestClient
from main import app, logger
from unittest.mock import patch

client = TestClient(app)

def test_error_leakage_on_task_create():
    """
    Test that internal exception details are leaked in the response.
    This test is expected to pass before the fix (showing the leak)
    and fail after the fix (or rather, we will update it to check for generic message).
    """
    secret_error_message = "SECRET_DATABASE_CREDENTIALS_LEAKED"

    # We monkeypatch logger.info because it's called at the start of create_task
    with patch.object(logger, 'info', side_effect=Exception(secret_error_message)):
        response = client.post("/task/create", json={
            "title": "Test Task",
            "description": "Test Description"
        })

        assert response.status_code == 500
        # The secret message should NOT be in the response
        assert response.json()["detail"] == "Internal server error"
        assert secret_error_message not in response.json()["detail"]

def test_error_leakage_on_get_task():
    """Test leakage on get_task endpoint"""
    secret_error_message = "SENSITIVE_PATH_OR_DB_ERROR"

    with patch.object(logger, 'info', side_effect=Exception(secret_error_message)):
        response = client.get("/task/task_123")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert secret_error_message not in response.json()["detail"]
