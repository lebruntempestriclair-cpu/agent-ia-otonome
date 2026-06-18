import os
import aiofiles
import shutil
import logging

logger = logging.getLogger(__name__)

async def save_chunk(upload_id: str, chunk_index: int, content: bytes, temp_dir: str):
    """Saves a single chunk to a temporary directory"""
    upload_path = os.path.join(temp_dir, upload_id)
    os.makedirs(upload_path, exist_ok=True)

    chunk_filename = os.path.join(upload_path, f"chunk_{chunk_index}")
    async with aiofiles.open(chunk_filename, 'wb') as f:
        await f.write(content)
    return chunk_filename

async def assemble_chunks(upload_id: str, total_chunks: int, temp_dir: str, final_dir: str, filename: str):
    """Assembles all chunks into a final file"""
    upload_path = os.path.join(temp_dir, upload_id)
    final_path = os.path.join(final_dir, f"{upload_id}_{filename}")

    os.makedirs(final_dir, exist_ok=True)

    async with aiofiles.open(final_path, 'wb') as outfile:
        for i in range(total_chunks):
            chunk_filename = os.path.join(upload_path, f"chunk_{i}")
            if not os.path.exists(chunk_filename):
                raise FileNotFoundError(f"Chunk {i} missing for upload {upload_id}")

            async with aiofiles.open(chunk_filename, 'rb') as infile:
                await outfile.write(await infile.read())

    # Clean up chunks
    shutil.rmtree(upload_path)
    return final_path
