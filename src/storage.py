import os
import shutil
import aiofiles
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_dir = self.base_dir / "chunks"
        self.chunk_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: str) -> Path:
        user_dir = self.base_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _get_chunk_path(self, upload_id: str, chunk_index: int) -> Path:
        # Sanitize upload_id to prevent directory traversal
        safe_id = os.path.basename(upload_id)
        return self.chunk_dir / f"{safe_id}_{chunk_index}"

    async def save_chunk(self, upload_id: str, chunk_index: int, data: bytes):
        chunk_path = self._get_chunk_path(upload_id, chunk_index)
        async with aiofiles.open(chunk_path, "wb") as f:
            await f.write(data)

    async def assemble_file(self, user_id: str, upload_id: str, filename: str, total_chunks: int) -> str:
        user_dir = self._get_user_dir(user_id)
        # Sanitize filename
        safe_filename = os.path.basename(filename)
        final_path = user_dir / safe_filename

        async with aiofiles.open(final_path, "wb") as outfile:
            for i in range(total_chunks):
                chunk_path = self._get_chunk_path(upload_id, i)
                if not chunk_path.exists():
                    raise FileNotFoundError(f"Chunk {i} missing for upload {upload_id}")

                async with aiofiles.open(chunk_path, "rb") as infile:
                    while True:
                        chunk_data = await infile.read(1024 * 1024)  # 1MB buffer
                        if not chunk_data:
                            break
                        await outfile.write(chunk_data)

                # Cleanup chunk after assembly
                os.remove(chunk_path)

        return str(final_path)

    def delete_user_data(self, user_id: str):
        user_dir = self._get_user_dir(user_id)
        if user_dir.exists():
            shutil.rmtree(user_dir)
            logger.info(f"Deleted data for user {user_id}")

    def list_user_files(self, user_id: str) -> list[str]:
        user_dir = self._get_user_dir(user_id)
        return [f.name for f in user_dir.iterdir() if f.is_file()]
