from typing import BinaryIO

import boto3
from botocore.client import Config

from app.services.bucket.base import BucketService


class MinioBucketService(BucketService):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 4, "mode": "standard"},
                connect_timeout=5,
                read_timeout=300,
            ),
        )
        self.public_url_base = f"{endpoint}/{bucket}"

    def get_presigned_url(self, filename: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": filename},
            ExpiresIn=expires_in,
        )

    def upload(
        self, file_obj: BinaryIO, filename: str, content_type: str, public: bool = False
    ) -> str:
        try:
            data = file_obj.getvalue()
        except AttributeError:
            try:
                file_obj.seek(0)
            except Exception as e:
                raise e
            data = file_obj.read()

        key = filename.lstrip("/")
        extra = {
            "ContentType": content_type,
            "ContentDisposition": f'inline; filename="{key.rsplit("/", 1)[-1]}"',
            "ContentLength": len(data),
        }
        if public:
            extra["ACL"] = "public-read"

        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)

        return f"{self.public_url_base}/{key}" if public else self.get_presigned_url(key)

    def delete(self, filename: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=filename)

    def get_url(self, filename: str) -> str:
        return f"{self.public_url_base}/{filename}"
