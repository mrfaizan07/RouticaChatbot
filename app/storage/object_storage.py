"""S3-compatible Object Storage implementation."""

from app.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import logger
from app.storage.base import BaseStorage

settings = get_settings()


class S3ObjectStorage(BaseStorage):
    def __init__(self):
        import boto3
        from botocore.config import Config

        self.bucket = settings.OBJECT_STORAGE_BUCKET
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.OBJECT_STORAGE_ENDPOINT or None,
            aws_access_key_id=settings.OBJECT_STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.OBJECT_STORAGE_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

    async def save_file(self, file_bytes: bytes, storage_key: str, content_type: str = "") -> str:
        try:
            extra_args = {"ContentType": content_type} if content_type else {}
            self.client.put_object(
                Bucket=self.bucket,
                Key=storage_key,
                Body=file_bytes,
                **extra_args,
            )
            return f"s3://{self.bucket}/{storage_key}"
        except Exception as exc:
            raise StorageError(f"S3 upload failed for {storage_key}: {exc}")

    async def get_file(self, storage_key: str) -> bytes | None:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=storage_key)
            return response["Body"].read()
        except Exception as exc:
            logger.error("S3 get failed for %s: %s", storage_key, exc)
            return None

    async def delete_file(self, storage_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=storage_key)
            return True
        except Exception as exc:
            logger.error("S3 delete failed for %s: %s", storage_key, exc)
            return False


def get_storage() -> BaseStorage:
    """Storage factory based on settings.STORAGE_BACKEND."""
    if settings.STORAGE_BACKEND == "s3" and settings.OBJECT_STORAGE_BUCKET:
        return S3ObjectStorage()
    return LocalStorage()

