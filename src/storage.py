import os
import aiofiles
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages file storage, upload chunking, and GDPR compliance."""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = 1024 * 1024  # 1MB chunks
        self.max_file_size = 700 * 1024 * 1024  # 700MB limit

    async def save_upload(self, upload_file, user_id: str) -> str:
        """Saves an uploaded file in chunks and returns the file path."""
        file_id = str(uuid.uuid4())
        extension = Path(upload_file.filename).suffix
        # Sanitize filename components (mitigate directory traversal)
        safe_filename = f"{file_id}{extension}"
        user_storage_path = self.upload_dir / user_id
        user_storage_path.mkdir(parents=True, exist_ok=True)

        file_path = user_storage_path / safe_filename

        size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await upload_file.read(self.chunk_size):
                size += len(chunk)
                if size > self.max_file_size:
                    await f.close()
                    os.remove(file_path)
                    raise ValueError("File size exceeds 700MB limit")
                await f.write(chunk)

        return str(file_path)

    async def delete_user_data(self, user_id: str):
        """GDPR 'Right to be forgotten' - Clears user uploaded media."""
        user_path = self.upload_dir / user_id
        if user_path.exists() and user_path.is_dir():
            for file in user_path.iterdir():
                file.unlink()
            user_path.rmdir()
            logger.info(f"Deleted data for user {user_id}")
        else:
            logger.warning(f"No data found for user {user_id}")
