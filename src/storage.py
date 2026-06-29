import os
import aiofiles
import logging

logger = logging.getLogger(__name__)

class StorageManager:
    """Abstract storage manager to facilitate switching between local and cloud storage (S3)"""
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, job_id: str, filename: str, stream):
        """Saves a file stream to storage"""
        file_ext = os.path.splitext(filename)[1].lower()
        file_path = os.path.join(self.upload_dir, f"{job_id}{file_ext}")

        async with aiofiles.open(file_path, 'wb') as out_file:
            content_length = 0
            while content := await stream.read(1024 * 1024):  # 1MB chunks
                content_length += len(content)
                # Max size check is done here now
                from main import settings
                if content_length > settings.MAX_UPLOAD_SIZE:
                    await out_file.close()
                    os.remove(file_path)
                    from fastapi import HTTPException, status
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large"
                    )
                await out_file.write(content)

        return file_path

    async def delete_job_files(self, job_id: str):
        """Deletes all files associated with a job ID"""
        for filename in os.listdir(self.upload_dir):
            if filename.startswith(job_id):
                file_path = os.path.join(self.upload_dir, filename)
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")

    async def delete_all_user_files(self, username: str):
        """
        Stub for deleting all files associated with a user.
        In a real scenario, this would look up job IDs for the user in a DB.
        """
        logger.info(f"Deleting all files for user: {username}")
        # Implementation depends on DB mapping
