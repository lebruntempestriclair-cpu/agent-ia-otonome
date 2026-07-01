import pytest
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_gdpr_delete_data():
    """Test that /user/data clears the uploads directory"""
    # 1. Ensure there is some data
    test_file = "uploads/gdpr_test.txt"
    os.makedirs("uploads", exist_ok=True)
    with open(test_file, "w") as f:
        f.write("sensitive data")

    assert os.path.exists(test_file)

    # 2. Call deletion endpoint
    response = client.delete("/user/data")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 3. Verify directory is empty
    assert len(os.listdir("uploads")) == 0
