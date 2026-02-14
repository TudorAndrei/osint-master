"""S3-compatible document storage service (RustFS)."""

from __future__ import annotations

import hashlib
import re

import boto3
import logfire
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import settings

S3_BUCKET_MIN_LENGTH = 3
S3_BUCKET_MAX_LENGTH = 63
S3_BUCKET_HASH_LEN = 10
S3_BUCKET_PREFIX_MAX = 52


class StorageService:
    """Handle upload and download of raw documents in object storage."""

    def __init__(self) -> None:
        self.bucket_prefix = settings.s3_bucket_name
        secret_key = settings.s3_secret_key or settings.s3_access_key
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=secret_key,
            region_name=settings.s3_region,
            use_ssl=settings.s3_secure,
            config=Config(
                signature_version="s3v4",
                s3={
                    "addressing_style": "path",
                    "payload_signing_enabled": False,
                },
            ),
        )

    def _bucket_name_for(self, investigation_id: str) -> str:
        raw = f"{self.bucket_prefix}-{investigation_id}".lower()
        cleaned = re.sub(r"[^a-z0-9.-]", "-", raw)
        cleaned = re.sub(r"-+", "-", cleaned).strip("-.")
        if len(cleaned) < S3_BUCKET_MIN_LENGTH:
            cleaned = f"{self.bucket_prefix}-inv"
        if len(cleaned) > S3_BUCKET_MAX_LENGTH:
            digest = hashlib.blake2s(cleaned.encode("utf-8"), digest_size=8).hexdigest()
            cleaned = f"{cleaned[:S3_BUCKET_PREFIX_MAX].rstrip('-')}-{digest[:S3_BUCKET_HASH_LEN]}"
        return cleaned

    @logfire.instrument("ensure storage bucket", extract_args=False)
    def ensure_bucket(self, investigation_id: str) -> str:
        """Create the bucket if it does not exist yet."""
        bucket_name = self._bucket_name_for(investigation_id)
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError as exc:
            error_code = str(exc.response.get("Error", {}).get("Code", ""))
            # Some S3-compatible providers return 403 for missing bucket.
            if error_code not in {"403", "404", "NoSuchBucket", "NotFound", "AccessDenied"}:
                raise
        else:
            return bucket_name

        try:
            if settings.s3_region and settings.s3_region != "us-east-1":
                self.client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": settings.s3_region},
                )
            else:
                self.client.create_bucket(Bucket=bucket_name)
        except ClientError as exc:
            error_code = str(exc.response.get("Error", {}).get("Code", ""))
            if error_code in {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}:
                return bucket_name
            raise
        return bucket_name

    @logfire.instrument("upload object bytes", extract_args=False)
    def upload_bytes(
        self,
        investigation_id: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> str:
        """Upload file bytes and return the object key."""
        bucket_name = self.ensure_bucket(investigation_id)
        safe_filename = filename or "upload.bin"
        key = f"{document_id}/{safe_filename}"

        self.client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type or "application/octet-stream",
            Metadata={
                "investigation_id": investigation_id,
                "document_id": document_id,
                "filename": safe_filename,
            },
        )
        return key

    @logfire.instrument("download object bytes", extract_args=False)
    def download_bytes(self, investigation_id: str, key: str) -> bytes:
        """Download file bytes by object key."""
        bucket_name = self._bucket_name_for(investigation_id)
        response = self.client.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read()

    def object_url(self, investigation_id: str, key: str) -> str:
        """Return a stable URI-like path for object provenance."""
        bucket_name = self._bucket_name_for(investigation_id)
        return f"s3://{bucket_name}/{key}"
