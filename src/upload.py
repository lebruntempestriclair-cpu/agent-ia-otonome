import os
import uuid
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Mock storage for chunked uploads
# In production, this would be Redis
upload_sessions: Dict[str, dict] = {}

UPLOAD_DIR = "/tmp/agent_ia_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_upload(filename: str, total_chunks: int) -> str:
    upload_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{upload_id}_{filename}")

    upload_sessions[upload_id] = {
        "filename": filename,
        "total_chunks": total_chunks,
        "received_chunks": set(),
        "path": file_path
    }

    # Create an empty file
    with open(file_path, "wb") as f:
        pass

    logger.info(f"Initialized upload {upload_id} for {filename} at {file_path}")
    return upload_id

def receive_chunk(upload_id: str, chunk_index: int, chunk_data: bytes) -> bool:
    if upload_id not in upload_sessions:
        logger.error(f"Upload session {upload_id} not found")
        return False

    session = upload_sessions[upload_id]
    file_path = session["path"]

    # Write chunk at correct offset
    # Assuming all chunks except the last one have the same size.
    # For this prototype, we'll just append or write to specific positions if needed.
    # A more robust way would be to store chunks separately and merge them.
    # Here we simplify by writing sequentially or to the file.

    with open(file_path, "r+b") as f:
        # Simple implementation: we expect chunks to be received in any order,
        # so we need to know the chunk size to seek.
        # For prototype simplicity, we append if it's the next chunk,
        # but better to seek if we know chunk_size.
        # Let's assume a fixed chunk size of 1MB for seeking if we had it.
        # Without it, we just write to a temporary per-chunk file and merge at the end.

        chunk_file = f"{file_path}.chunk_{chunk_index}"
        with open(chunk_file, "wb") as cf:
            cf.write(chunk_data)

    session["received_chunks"].add(chunk_index)

    is_complete = len(session["received_chunks"]) == session["total_chunks"]
    if is_complete:
        # Merge chunks
        with open(file_path, "wb") as outfile:
            for i in range(session["total_chunks"]):
                chunk_file = f"{file_path}.chunk_{i}"
                if os.path.exists(chunk_file):
                    with open(chunk_file, "rb") as infile:
                        outfile.write(infile.read())
                    os.remove(chunk_file)
        logger.info(f"Upload {upload_id} complete and merged at {file_path}")

    return is_complete

def get_upload_path(upload_id: str) -> Optional[str]:
    session = upload_sessions.get(upload_id)
    return session["path"] if session else None
