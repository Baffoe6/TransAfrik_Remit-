import mimetypes
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from app.config import get_settings

settings = get_settings()


def resolve_upload_path(relative_path: str) -> Path:
    """Resolve and validate that a file path stays within the upload directory."""
    upload_root = Path(settings.upload_dir).resolve()
    full_path = (upload_root / relative_path).resolve()
    if not str(full_path).startswith(str(upload_root)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid file path")
    if not full_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return full_path


def serve_upload_file(relative_path: str, download_name: str | None = None) -> FileResponse:
    path = resolve_upload_path(relative_path)
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type, filename=download_name or path.name)
