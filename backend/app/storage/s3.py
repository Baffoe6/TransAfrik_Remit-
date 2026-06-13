import logging

from app.config import get_settings
from app.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class S3StorageBackend(StorageBackend):
    def __init__(self):
        settings = get_settings()
        import boto3
        from botocore.config import Config

        self.bucket = settings.s3_bucket
        self.region = settings.s3_region
        kwargs = {"region_name": self.region, "config": Config(signature_version="s3v4")}
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            kwargs["aws_access_key_id"] = settings.aws_access_key_id
            kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        if settings.s3_endpoint_url:
            kwargs["endpoint_url"] = settings.s3_endpoint_url
        self.client = boto3.client("s3", **kwargs)

    @property
    def backend_code(self) -> str:
        return "s3"

    def save(self, key: str, content: bytes, *, content_type: str | None = None) -> str:
        extra = {"ContentType": content_type} if content_type else {}
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, **extra)
        return key

    def save_file(self, key: str, file_obj) -> str:
        self.client.upload_fileobj(file_obj, self.bucket, key)
        return key

    def read(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def get_url(self, key: str, *, expires_in: int = 3600) -> str | None:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def health(self) -> dict:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return {"status": "healthy", "backend": "s3", "bucket": self.bucket}
        except Exception as exc:
            return {"status": "unhealthy", "backend": "s3", "error": str(exc)}
