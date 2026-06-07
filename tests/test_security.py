
import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch

def test_cors_wildcard_policy():
    """Test that allow_credentials is False when wildcard origin is used"""
    # To test this properly without re-initializing the global app,
    # we can create a local app instance or check the global one carefully.
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import main

    # We can check how CORSMiddleware is initialized in main.py
    # But since it's already done, let's verify by making a request
    # and checking the headers.
    client = TestClient(main.app)
    # If allow_credentials is True and origin is *, Starlette would have crashed.
    # If it didn't crash, and we use a wildcard, Access-Control-Allow-Credentials should NOT be true.
    response = client.options("/health", headers={
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    # For wildcard origins, Access-Control-Allow-Credentials should be absent or "false"
    assert response.headers.get("access-control-allow-credentials") != "true"

def test_error_masking():
    """Test that internal errors are masked in the response"""
    from main import app
    client = TestClient(app)

    # We'll monkeypatch a route to raise an exception by patching logger.info
    with patch("main.logger.info", side_effect=Exception("Database connection failed")):
        response = client.post("/task/create", json={"title": "test", "description": "test"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
        assert "Database connection failed" not in response.text

def test_cors_headers():
    """Test that CORS headers are present and correct"""
    from main import app
    client = TestClient(app)
    response = client.options("/health", headers={
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
