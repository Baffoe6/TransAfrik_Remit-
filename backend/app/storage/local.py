import os
from pathlib import Path

from app.config import get_settings
from app.storage.base import StorageBackend


class LocalStorageBackend(StorageBackend):
    @property
    def backend_code(self) -> str:
        return "local"

    def _full_path(self, key: str) -> Path:
        settings = get_settings()
        return Path(settings.upload_dir) / key

    def save(self, key: str, content: bytes, *, content_type: str | None = None) -> str:
        path = self._full_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def save_file(self, key: str, file_obj) -> str:
        path = self._full_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as out:
            out.write(file_obj.read())
        return key

    def read(self, key: str) -> bytes:
        return self._full_path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._full_path(key).exists()

    def delete(self, key: str) -> bool:
        path = self._full_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def get_url(self, key: str, *, expires_in: int = 3600) -> str | None:
        return os.path.join(get_settings().upload_dir, key)
