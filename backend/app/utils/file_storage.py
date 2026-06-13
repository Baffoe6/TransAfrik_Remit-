import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings
from app.storage import get_storage

settings = get_settings()


def ensure_upload_dir() -> Path:
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def validate_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.allowed_upload_extensions}",
        )


async def save_upload(file: UploadFile, subdirectory: str) -> tuple[str, str]:
    validate_upload(file)
    content = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    ext = Path(file.filename).suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    key = f"{subdirectory}/{stored_name}"

    storage = get_storage()
    storage.save(key, content)
    return key, file.filename


def save_bytes(content: bytes, subdirectory: str, filename: str) -> str:
    key = f"{subdirectory}/{filename}"
    get_storage().save(key, content)
    return key


def read_file(key: str) -> bytes:
    return get_storage().read(key)


def file_url(key: str) -> str | None:
    return get_storage().get_url(key)
