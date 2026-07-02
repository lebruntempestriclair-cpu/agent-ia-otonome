import os
import aiofiles
import shutil
import logging
from typing import List
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def get_user_dir(self, user_id: str) -> str:
        """Get the directory for a specific user, creating it if it doesn't exist."""
        # Sanitize user_id to prevent directory traversal
        safe_user_id = os.path.basename(user_id)
        user_dir = os.path.join(self.base_dir, safe_user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def get_upload_temp_dir(self, user_id: str, upload_id: str) -> str:
        """Get a temporary directory for a specific chunked upload."""
        user_dir = self.get_user_dir(user_id)
        # Sanitize upload_id
        safe_upload_id = os.path.basename(upload_id)
        temp_dir = os.path.join(user_dir, "temp", safe_upload_id)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    async def save_chunk(self, user_id: str, upload_id: str, chunk_index: int, file: UploadFile):
        """Save a single chunk to the temporary upload directory."""
        temp_dir = self.get_upload_temp_dir(user_id, upload_id)
        chunk_path = os.path.join(temp_dir, f"chunk_{chunk_index:05d}")

        async with aiofiles.open(chunk_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024): # 1MB chunks internally
                await out_file.write(content)

        logger.info(f"Saved chunk {chunk_index} for upload {upload_id} in {temp_dir}")

    async def finalize_upload(self, user_id: str, upload_id: str, filename: str) -> str:
        """Merge all chunks into a final file and clean up."""
        temp_dir = self.get_upload_temp_dir(user_id, upload_id)
        user_dir = self.get_user_dir(user_id)

        # Sanitize filename
        safe_filename = os.path.basename(filename)
        final_path = os.path.join(user_dir, safe_filename)

        # Get sorted list of chunks
        chunks = sorted([f for f in os.listdir(temp_dir) if f.startswith("chunk_")])

        async with aiofiles.open(final_path, 'wb') as out_file:
            for chunk_name in chunks:
                chunk_path = os.path.join(temp_dir, chunk_name)
                async with aiofiles.open(chunk_path, 'rb') as in_file:
                    while content := await in_file.read(1024 * 1024):
                        await out_file.write(content)

        # Cleanup temp directory
        shutil.rmtree(temp_dir)
        # Also cleanup 'temp' folder if empty
        parent_temp = os.path.dirname(temp_dir)
        if not os.listdir(parent_temp):
            os.rmdir(parent_temp)

        logger.info(f"Finalized upload {upload_id} as {final_path}")
        return final_path

    async def save_file(self, user_id: str, file: UploadFile, chunk_size: int = 1024 * 1024) -> str:
        """Save an uploaded file in chunks to the user's directory (Legacy/Single shot)."""
        user_dir = self.get_user_dir(user_id)
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(user_dir, safe_filename)

        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(chunk_size):
                await out_file.write(content)

        logger.info(f"File saved: {file_path} for user {user_id}")
        return file_path

    def delete_user_data(self, user_id: str):
        """GDPR compliant: delete all data for a specific user."""
        user_dir = self.get_user_dir(user_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            logger.info(f"Deleted all data for user {user_id}")

    def list_user_files(self, user_id: str) -> List[str]:
        """List all files uploaded by a user."""
        user_dir = self.get_user_dir(user_id)
        if not os.path.exists(user_dir):
            return []
        return [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))]
