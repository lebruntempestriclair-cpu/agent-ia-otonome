import requests
import sys

BASE_URL = "http://localhost:8000"

def demo_pipeline():
    print("🚀 Starting Pipeline Demo...")

    # 1. Create Project
    print("1. Creating Project...")
    project_data = {
        "title": "Demo Project",
        "voice_settings": {
            "language_code": "fr-FR",
            "gender": "female"
        }
    }
    res = requests.post(f"{BASE_URL}/project/create", json=project_data)
    if res.status_code != 200:
        print(f"❌ Error creating project: {res.text}")
        return
    project = res.json()
    project_id = project["id"]
    print(f"✅ Project Created: {project_id}")

    # 2. Init Upload
    print("2. Initializing Upload...")
    upload_data = {"filename": "demo.mp4", "total_size": 100}
    res = requests.post(f"{BASE_URL}/upload/init", data=upload_data)
    upload_id = res.json()["upload_id"]
    print(f"✅ Upload Initialized: {upload_id}")

    # 3. Upload Chunks (Simulated)
    print("3. Uploading Chunks...")
    chunk_content = b"fake-media-content"
    upload_files = {"file": ("demo.mp4", chunk_content)}
    upload_form = {
        "upload_id": upload_id,
        "chunk_index": 0,
        "total_chunks": 1,
        "project_id": project_id
    }
    res = requests.post(f"{BASE_URL}/upload/chunk", data=upload_form, files=upload_files)
    print(f"✅ Chunk Uploaded: {res.json()}")

    # 4. Process Project
    print("4. Starting Processing...")
    res = requests.post(f"{BASE_URL}/project/{project_id}/process")
    print(f"✅ Processing Started: {res.json()}")

    # 5. Check Status
    print("5. Checking Final Status...")
    res = requests.get(f"{BASE_URL}/project/{project_id}")
    print(f"✅ Final Project State: {res.json()}")

if __name__ == "__main__":
    demo_pipeline()
