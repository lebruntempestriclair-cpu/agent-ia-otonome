import requests
import os

BASE_URL = "http://localhost:8000"

def test_path_traversal():
    print("🛡️ Testing Path Traversal Protection...")

    # 1. Create Project
    project_data = {"title": "Security Test", "voice_settings": {"language_code": "en"}}
    res = requests.post(f"{BASE_URL}/project/create", json=project_data)
    project_id = res.json()["id"]

    # 2. Try malicious upload
    upload_form = {
        "upload_id": "vuln_test",
        "chunk_index": 0,
        "total_chunks": 1,
        "project_id": project_id
    }
    # Attempting to go up levels
    files = {"file": ("../../evil.txt", b"malicious content")}

    res = requests.post(f"{BASE_URL}/upload/chunk", data=upload_form, files=files)
    print(f"Response: {res.json()}")

    # Check if evil.txt exists outside uploads
    if os.path.exists("evil.txt"):
        print("❌ VULNERABILITY DETECTED: evil.txt was created in root!")
    else:
        print("✅ SUCCESS: Path traversal blocked (or at least evil.txt not found in root).")

    # Check where it actually landed
    res = requests.get(f"{BASE_URL}/project/{project_id}")
    media_path = res.json()["media_path"]
    print(f"Media landed at: {media_path}")
    if ".." in media_path:
        print("❌ VULNERABILITY DETECTED: Path still contains '..'")
    else:
        print("✅ SUCCESS: Media path is safe.")

if __name__ == "__main__":
    test_path_traversal()
