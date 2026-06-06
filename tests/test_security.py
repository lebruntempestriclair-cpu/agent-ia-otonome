import pytest
from fastapi.testclient import TestClient
from main import app
import main

client = TestClient(app)

def test_information_leakage_on_500():
    """
    Test that internal exception details are not leaked in the response.
    We monkeypatch the logger or a route to raise an exception.
    """
    # Trigger an error in /task/create by sending invalid data that causes an exception
    # or by monkeypatching a function it calls.
    # Since it's mostly TODOs, we can monkeypatch the logger to raise an error
    # when it's called inside the try block.

    original_logger_info = main.logger.info
    def mock_info(msg):
        if "Creating task:" in msg:
            raise Exception("Sensitive internal database connection error: password=12345")
        original_logger_info(msg)

    main.logger.info = mock_info

    try:
        task_data = {
            "title": "Exploit Task",
            "description": "Trigger leakage",
            "priority": 1
        }
        response = client.post("/task/create", json=task_data)

        assert response.status_code == 500
        # Check if the sensitive info is leaked
        assert "password=12345" not in response.text
        assert "Internal server error" in response.text
    finally:
        main.logger.info = original_logger_info

def test_cors_configuration():
    """
    Check if CORS is overly permissive.
    """
    response = client.options("/health", headers={
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET"
    })
    # If allow_origins is ["*"], it might return the origin or *
    # But with allow_credentials=True, it MUST NOT be *
    assert response.headers.get("access-control-allow-origin") != "*"
