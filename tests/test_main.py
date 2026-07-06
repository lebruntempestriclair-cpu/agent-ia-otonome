"""
Unit tests for the Multilingual Dubbing Platform
"""

import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Mock settings before importing app to test authentication
with patch.dict(os.environ, {"REQUIRE_API_KEY": "true", "API_KEY": "test_secret_key"}):
    from main import app
    client = TestClient(app)

class TestSecurity:
    """Tests for security features"""

    def test_unauthenticated_access(self):
        """Test that sensitive endpoints require API key when enabled"""
        endpoints = [
            ("/project/create", "post"),
            ("/project/proj_123", "get"),
            ("/projects", "get"),
            ("/upload/init", "post")
        ]
        for url, method in endpoints:
            func = getattr(client, method)
            response = func(url)
            assert response.status_code == 403
            assert response.json() == {"detail": "Could not validate credentials"}

    def test_authenticated_access(self):
        """Test that sensitive endpoints allow access with valid API key"""
        headers = {"X-API-Key": "test_secret_key"}

        # Test project creation
        project_data = {
            "title": "Test Project",
            "voice_settings": {
                "language_code": "en-US"
            }
        }
        response = client.post("/project/create", json=project_data, headers=headers)
        assert response.status_code == 200

        # Test list projects
        response = client.get("/projects", headers=headers)
        assert response.status_code == 200

    def test_health_check_remains_public(self):
        """Health check should not require API key"""
        response = client.get("/health")
        assert response.status_code == 200

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200 and correct structure"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

class TestProjectLifecycle:
    """Tests for project creation and retrieval"""
    
    def test_create_project(self):
        """Test creating a new dubbing project"""
        headers = {"X-API-Key": "test_secret_key"}
        project_data = {
            "title": "My Dubbing Project",
            "voice_settings": {
                "language_code": "fr-FR",
                "gender": "female"
            }
        }
        response = client.post("/project/create", json=project_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "My Dubbing Project"
        assert "id" in data
        assert data["status"] == "created"
        return data["id"]
    
    def test_get_project(self):
        """Test retrieving project details"""
        headers = {"X-API-Key": "test_secret_key"}
        # First create
        project_data = {"title": "FindMe", "voice_settings": {"language_code": "es-ES"}}
        create_res = client.post("/project/create", json=project_data, headers=headers)
        project_id = create_res.json()["id"]

        # Then get
        response = client.get(f"/project/{project_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == project_id

class TestMediaUpload:
    """Tests for chunked upload initialization"""
    
    def test_initialize_upload(self):
        """Test initializing a chunked upload"""
        headers = {"X-API-Key": "test_secret_key"}
        upload_data = {
            "filename": "video.mp4",
            "total_size": 10485760
        }
        response = client.post("/upload/init", data=upload_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "upload_id" in data
        assert "chunk_size" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
