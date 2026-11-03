"""Abstract base storage class for file persistence."""

from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    async def save_file(self, file_bytes: bytes, storage_key: str, content_type: str = "") -> str:
        """Saves file content and returns its permanent storage URI or key."""
        pass

    @abstractmethod
    async def get_file(self, storage_key: str) -> bytes | None:
        """Retrieves raw file content by storage key."""
        pass

    @abstractmethod
    async def delete_file(self, storage_key: str) -> bool:
        """Deletes file by storage key."""
        pass

