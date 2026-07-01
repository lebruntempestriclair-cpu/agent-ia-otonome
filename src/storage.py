import os
import aiofiles
import uuid
import logging
import shutil
from typing import Optional

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages file storage for uploaded media and processed jobs."""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    async def save_upload(self, upload_file, job_id: str) -> str:
        """
        Saves an uploaded file to the storage directory.
        Uses chunked writing for memory efficiency with large files.
        """
        filename = os.path.basename(upload_file.filename)
        file_ext = os.path.splitext(filename)[1]
        save_name = f"{job_id}{file_ext}"
        file_path = os.path.join(self.upload_dir, save_name)

        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await upload_file.read(1024 * 1024):  # 1MB chunks
                    await out_file.write(content)
            return file_path
        except Exception as e:
            logger.error(f"Error saving upload {filename}: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

    def generate_job_id(self) -> str:
        """Generates a unique identifier for a dubbing job."""
        return str(uuid.uuid4())

    def clear_user_data(self):
        """GDPR 'Right to be forgotten' - Clears all user-uploaded media."""
        try:
            for filename in os.listdir(self.upload_dir):
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            logger.info("All user media data has been cleared for GDPR compliance.")
        except Exception as e:
            logger.error(f"Error clearing user data: {str(e)}")
            raise
