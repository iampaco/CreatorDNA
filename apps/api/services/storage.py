import uuid
from functools import lru_cache

import boto3
from botocore.client import Config

from apps.api.config import get_settings


@lru_cache
def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
        config=Config(signature_version="s3v4"),
    )


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = get_s3_client()

    def upload_bytes(self, *, key: str, data: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.settings.storage_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def download_bytes(self, key: str) -> bytes:
        response = self.client.get_object(Bucket=self.settings.storage_bucket, Key=key)
        return response["Body"].read()

    def build_media_key(self, video_id: uuid.UUID) -> str:
        return f"videos/{video_id}/capture.webm"

    def build_frame_key(self, video_id: uuid.UUID, frame_index: int) -> str:
        return f"frames/{video_id}/frame_{frame_index:04d}.jpg"
