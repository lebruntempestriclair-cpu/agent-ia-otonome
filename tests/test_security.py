"""
Security tests for Agent IA Autonome
"""

import os
import pytest
from fastapi.testclient import TestClient
from main import app

def test_unauthorized_access_when_enabled(monkeypatch):
    """Test that sensitive endpoints are blocked when REQUIRE_API_KEY is true and no key is provided"""
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("API_KEY", "secret_key")

    # Re-import or use a fresh client to ensure env vars are picked up if needed
    # In FastAPI, os.getenv is called inside the dependency, so monkeypatch should work
    client = TestClient(app)

    endpoints = [
        ("/task/create", "POST", {"title": "test", "description": "test"}),
        ("/tasks", "GET", None),
        ("/task/123", "GET", None),
        ("/execute?task_id=123", "POST", None),
    ]

    for path, method, json_data in endpoints:
        if method == "POST":
            response = client.post(path, json=json_data)
        else:
            response = client.get(path)

        assert response.status_code == 403
        assert response.json()["detail"] == "Could not validate credentials"

def test_authorized_access_when_enabled(monkeypatch):
    """Test that sensitive endpoints are accessible with correct API Key when enabled"""
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("API_KEY", "secret_key")

    client = TestClient(app)
    headers = {"X-API-Key": "secret_key"}

    # Test one endpoint as representative
    task_data = {"title": "Secure Task", "description": "This should work"}
    response = client.post("/task/create", json=task_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["success"] is True

def test_access_when_disabled(monkeypatch):
    """Test that endpoints are accessible without API Key when REQUIRE_API_KEY is false"""
    monkeypatch.setenv("REQUIRE_API_KEY", "false")

    client = TestClient(app)

    response = client.get("/tasks")
    assert response.status_code == 200

def test_health_is_always_public(monkeypatch):
    """Test that health endpoint remains public even if REQUIRE_API_KEY is true"""
    monkeypatch.setenv("REQUIRE_API_KEY", "true")
    monkeypatch.setenv("API_KEY", "secret_key")

    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
