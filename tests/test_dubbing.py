"""
Additional tests for Dubbing and GDPR features
"""

import pytest
import os
import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestDubbingEndpoint:
    """Tests for the /dub endpoint"""

    def test_dub_missing_consent(self):
        """Test that /dub requires GDPR consent"""
        file_data = {"file": ("test.mp3", b"fake audio content", "audio/mpeg")}
        form_data = {"target_lang": "en"}
        # Without gdpr_consent field, it should fail validation or return 400
        response = client.post("/dub", files=file_data, data=form_data)
        # It should be 422 because gdpr_consent is a required Form field
        assert response.status_code == 422

    def test_dub_consent_false(self):
        """Test that /dub fails if gdpr_consent is false"""
        file_data = {"file": ("test.mp3", b"fake audio content", "audio/mpeg")}
        form_data = {"target_lang": "en", "gdpr_consent": "false"}
        response = client.post("/dub", files=file_data, data=form_data)
        assert response.status_code == 400
        assert "GDPR consent is required" in response.json()["detail"]

    def test_dub_invalid_extension(self):
        """Test that /dub rejects unsupported extensions"""
        file_data = {"file": ("test.txt", b"fake text content", "text/plain")}
        form_data = {"target_lang": "en", "gdpr_consent": "true"}
        response = client.post("/dub", files=file_data, data=form_data)
        assert response.status_code == 400
        assert "Unsupported file extension" in response.json()["detail"]

    def test_dub_success(self):
        """Test successful dubbing request"""
        file_data = {"file": ("test.mp3", b"fake audio content", "audio/mpeg")}
        form_data = {"target_lang": "en", "gdpr_consent": "true"}
        response = client.post("/dub", files=file_data, data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "processing"

class TestGDPRDelete:
    """Tests for the /user/data DELETE endpoint"""

    def test_delete_user_data(self):
        """Test GDPR data deletion endpoint"""
        response = client.delete("/user/data")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "deleted from storage" in response.json()["message"]
