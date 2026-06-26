import os
import aiofiles
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class StorageService(ABC):
    @abstractmethod
    async def upload(self, local_path: str, remote_name: str) -> str:
        pass

    @abstractmethod
    async def download(self, remote_name: str, local_path: str) -> str:
        pass

class LocalStorageService(StorageService):
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload(self, local_path: str, remote_name: str) -> str:
        # For local, we just move it or assume it's already in the upload_dir
        logger.info(f"Uploading {local_path} to local storage as {remote_name}")
        return os.path.join(self.upload_dir, remote_name)

    async def download(self, remote_name: str, local_path: str) -> str:
        logger.info(f"Downloading {remote_name} from local storage to {local_path}")
        return os.path.join(self.upload_dir, remote_name)

class S3StorageService(StorageService):
    """Stub for S3 Storage Service"""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    async def upload(self, local_path: str, remote_name: str) -> str:
        logger.info(f"Uploading {local_path} to S3 bucket {self.bucket_name} as {remote_name}")
        return f"s3://{self.bucket_name}/{remote_name}"

    async def download(self, remote_name: str, local_path: str) -> str:
        logger.info(f"Downloading {remote_name} from S3 bucket {self.bucket_name} to {local_path}")
        return local_path
