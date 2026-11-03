"""Local filesystem storage implementation."""

import os
from pathlib import Path
from app.config import get_settings
from app.core.exceptions import StorageError
from app.core.logging import logger
from app.storage.base import BaseStorage

settings = get_settings()


class LocalStorage(BaseStorage):
    def __init__(self, base_directory: str | None = None):
        self.base_dir = Path(base_directory or settings.LOCAL_STORAGE_PATH)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file_bytes: bytes, storage_key: str, content_type: str = "") -> str:
        try:
            target_path = self.base_dir / storage_key
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(file_bytes)
            logger.info("Saved file locally at %s", target_path)
            return str(target_path)
        except Exception as exc:
            raise StorageError(f"Failed to save local file {storage_key}: {exc}")

    async def get_file(self, storage_key: str) -> bytes | None:
        try:
            target_path = self.base_dir / storage_key
            if not target_path.exists():
                return None
            with open(target_path, "rb") as f:
                return f.read()
        except Exception as exc:
            logger.error("Failed to read local file %s: %exc", storage_key, exc)
            return None

    async def delete_file(self, storage_key: str) -> bool:
        try:
            target_path = self.base_dir / storage_key
            if target_path.exists():
                os.remove(target_path)
                return True
            return False
        except Exception as exc:
            logger.error("Failed to delete local file %s: %s", storage_key, exc)
            return False

