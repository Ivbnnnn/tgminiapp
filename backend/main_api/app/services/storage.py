import asyncio
import json
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

from fastapi import UploadFile
from minio import Minio

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class ObjectStorage:
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET

    async def ensure_bucket(self) -> None:
        def configure() -> None:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                    }
                ],
            }
            self.client.set_bucket_policy(self.bucket, json.dumps(policy))

        await asyncio.to_thread(configure)

    async def upload_product_photo(self, product_id: int, upload: UploadFile) -> str:
        if upload.content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError("Only JPEG, PNG and WebP images are allowed")

        content = await upload.read(settings.MAX_PHOTO_SIZE_BYTES + 1)
        await upload.close()
        if not content:
            raise ValueError("Image is empty")
        if len(content) > settings.MAX_PHOTO_SIZE_BYTES:
            raise ValueError("Image exceeds the maximum allowed size")
        if not _has_valid_image_signature(content, upload.content_type):
            raise ValueError("File content does not match its image type")

        suffix = ALLOWED_IMAGE_TYPES[upload.content_type]
        object_name = f"products/{product_id}/{uuid4().hex}{suffix}"
        await asyncio.to_thread(
            self.client.put_object,
            self.bucket,
            object_name,
            BytesIO(content),
            len(content),
            content_type=upload.content_type,
        )
        return f"{settings.MINIO_PUBLIC_URL.rstrip('/')}/{self.bucket}/{object_name}"

    async def delete_by_url(self, url: str) -> None:
        parsed_path = unquote(urlparse(url).path).lstrip("/")
        bucket_prefix = f"{self.bucket}/"
        if not parsed_path.startswith(bucket_prefix):
            return
        object_name = str(Path(parsed_path.removeprefix(bucket_prefix))).replace("\\", "/")
        await asyncio.to_thread(self.client.remove_object, self.bucket, object_name)


object_storage = ObjectStorage()


def _has_valid_image_signature(content: bytes, content_type: str) -> bool:
    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    return False
