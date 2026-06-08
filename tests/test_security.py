import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_error_leakage():
    """Verify that internal error details are not leaked in the response"""
    # We need to trigger an exception in one of the routes.
    # Let's mock the logger in create_task to raise an exception,
    # since it's the first thing called in the try block.
    with patch("main.logger.info", side_effect=Exception("Sensitive database connection string: postgresql://user:password@localhost:5432/db")):
        response = client.post("/task/create", json={"title": "Test", "description": "Test"})

    assert response.status_code == 500
    assert "Sensitive database connection string" not in response.text
    assert response.json()["detail"] == "Internal server error"
