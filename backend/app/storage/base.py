"""Storage backend abstraction for documents and compliance packs."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    @property
    @abstractmethod
    def backend_code(self) -> str:
        pass

    @abstractmethod
    def save(self, key: str, content: bytes, *, content_type: str | None = None) -> str:
        """Save content and return storage key/path."""

    @abstractmethod
    def save_file(self, key: str, file_obj: BinaryIO) -> str:
        pass

    @abstractmethod
    def read(self, key: str) -> bytes:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def get_url(self, key: str, *, expires_in: int = 3600) -> str | None:
        """Presigned URL for S3; local path for filesystem."""

    def health(self) -> dict:
        return {"status": "healthy", "backend": self.backend_code}
