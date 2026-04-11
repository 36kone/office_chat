from app.core.config import settings
from app.services.bucket.base import BucketService
from app.services.bucket.minio_service import MinioBucketService


def get_bucket_service() -> BucketService:
    return MinioBucketService(
        endpoint=settings.BUCKET_ENDPOINT,
        access_key=settings.BUCKET_ACCESS_KEY,
        secret_key=settings.BUCKET_SECRET,
        bucket=settings.BUCKET_NAME,
    )
