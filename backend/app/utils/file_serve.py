import mimetypes
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from app.storage import get_storage


def serve_upload_file(relative_path: str, download_name: str | None = None) -> StreamingResponse:
    storage = get_storage()
    if not storage.exists(relative_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    content = storage.read(relative_path)
    filename = download_name or Path(relative_path).name
    media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
