import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import shutil
import pathlib

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_path(path: str) -> str:
    """
    Prevents path traversal by ensuring the path stays within the intended directory.
    """
    return os.path.basename(path)

@router.post("/chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    upload_id: str = Form(...)
):
    """
    Handles chunked file uploads using non-blocking I/O.
    """
    safe_upload_id = sanitize_path(upload_id)
    chunk_dir = os.path.join(UPLOAD_DIR, safe_upload_id)
    os.makedirs(chunk_dir, exist_ok=True)

    chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index}")

    async with aiofiles.open(chunk_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):  # Read in 1MB chunks
            await out_file.write(content)

    return {"message": f"Chunk {chunk_index}/{total_chunks} received"}

@router.post("/complete")
async def complete_upload(
    filename: str = Form(...),
    upload_id: str = Form(...),
    total_chunks: int = Form(...)
):
    """
    Assembles the chunks into a single file using non-blocking I/O.
    """
    safe_upload_id = sanitize_path(upload_id)
    safe_filename = sanitize_path(filename)

    chunk_dir = os.path.join(UPLOAD_DIR, safe_upload_id)
    if not os.path.exists(chunk_dir):
        raise HTTPException(status_code=404, detail="Upload session not found")

    final_path = os.path.join(UPLOAD_DIR, safe_filename)

    async with aiofiles.open(final_path, "wb") as final_file:
        for i in range(total_chunks):
            chunk_path = os.path.join(chunk_dir, f"chunk_{i}")
            if not os.path.exists(chunk_path):
                raise HTTPException(status_code=400, detail=f"Missing chunk {i}")

            async with aiofiles.open(chunk_path, "rb") as chunk_file:
                content = await chunk_file.read()
                await final_file.write(content)

    # Cleanup chunks
    shutil.rmtree(chunk_dir)

    return {"message": "Upload complete", "file_path": final_path}
