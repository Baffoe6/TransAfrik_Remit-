from functools import lru_cache

from app.config import get_settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend


@lru_cache
def get_storage() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "s3":
        from app.storage.s3 import S3StorageBackend

        return S3StorageBackend()
    return LocalStorageBackend()


def storage_health() -> dict:
    return get_storage().health()
