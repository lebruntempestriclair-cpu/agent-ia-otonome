"""
Enhanced security tests for the Agent IA Autonome platform.
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# We use a separate file to ensure a clean state with patched environment
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "secure_test_key"}):
    from main import app
    client = TestClient(app)

def test_unauthenticated_dubbing():
    """Test that /dub requires API key when enabled"""
    with open("tests/media/test_video.mp4", "rb") as f:
        response = client.post(
            "/dub",
            files={"file": ("test_video.mp4", f, "video/mp4")},
            data={"target_lang": "fr", "gdpr_consent": "true"}
        )
    assert response.status_code == 403

def test_authenticated_dubbing():
    """Test that /dub works with API key when enabled"""
    headers = {"X-API-Key": "secure_test_key"}
    with open("tests/media/test_video.mp4", "rb") as f:
        response = client.post(
            "/dub",
            headers=headers,
            files={"file": ("test_video.mp4", f, "video/mp4")},
            data={"target_lang": "fr", "gdpr_consent": "true"}
        )
    assert response.status_code == 200

def test_unauthenticated_tasks():
    """Test task endpoints require API key"""
    endpoints = [
        ("/task/create", "post", {"title": "x", "description": "y"}),
        ("/task/task_123", "get", None),
        ("/tasks", "get", None),
        ("/execute?task_id=task_123", "post", None)
    ]
    for url, method, json_data in endpoints:
        func = getattr(client, method)
        if json_data:
            response = func(url, json=json_data)
        else:
            response = func(url)
        assert response.status_code == 403
