from io import BytesIO

from minio import Minio

from app.core.config import settings

_client: Minio | None = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
    return _client


def ensure_bucket() -> None:
    client = get_client()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def put_bytes(object_key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    ensure_bucket()
    get_client().put_object(
        settings.minio_bucket,
        object_key,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return object_key


def get_bytes(object_key: str) -> bytes:
    resp = get_client().get_object(settings.minio_bucket, object_key)
    try:
        return resp.read()
    finally:
        resp.close()
        resp.release_conn()


def presigned_get(object_key: str, expires_hours: int = 1) -> str:
    from datetime import timedelta

    return get_client().presigned_get_object(
        settings.minio_bucket, object_key, expires=timedelta(hours=expires_hours)
    )
