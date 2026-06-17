import os
import shutil
import uuid
from typing import Dict

# Dictionary to store upload metadata in memory for this prototype
# In production, this should be in Redis
active_uploads: Dict[str, dict] = {}

UPLOAD_DIR = "uploads"

def init_upload(filename: str, total_size: int, content_type: str) -> str:
    """Initialize a chunked upload and return a unique ID"""
    upload_id = str(uuid.uuid4())
    temp_dir = os.path.join(UPLOAD_DIR, upload_id)
    os.makedirs(temp_dir, exist_ok=True)

    active_uploads[upload_id] = {
        "filename": filename,
        "total_size": total_size,
        "content_type": content_type,
        "chunks_received": set(),
        "temp_dir": temp_dir
    }
    return upload_id

async def save_chunk(upload_id: str, chunk_index: int, chunk_data: bytes) -> bool:
    """Save a single chunk to disk"""
    if upload_id not in active_uploads:
        return False

    temp_dir = active_uploads[upload_id]["temp_dir"]
    chunk_filename = f"chunk_{chunk_index}"
    chunk_path = os.path.join(temp_dir, chunk_filename)

    with open(chunk_path, "wb") as f:
        f.write(chunk_data)

    active_uploads[upload_id]["chunks_received"].add(chunk_index)
    return True

def complete_upload(upload_id: str, total_chunks: int) -> str:
    """Reassemble all chunks into the final file"""
    if upload_id not in active_uploads:
        raise ValueError("Invalid upload ID")

    metadata = active_uploads[upload_id]
    if len(metadata["chunks_received"]) != total_chunks:
        raise ValueError("Missing chunks")

    temp_dir = metadata["temp_dir"]
    final_filename = f"{upload_id}_{metadata['filename']}"
    final_path = os.path.join(UPLOAD_DIR, final_filename)

    with open(final_path, "wb") as outfile:
        for i in range(total_chunks):
            chunk_path = os.path.join(temp_dir, f"chunk_{i}")
            with open(chunk_path, "rb") as infile:
                shutil.copyfileobj(infile, outfile)
            # Remove chunk after merging
            os.remove(chunk_path)

    # Clean up temp directory
    os.rmdir(temp_dir)
    del active_uploads[upload_id]

    return final_path
