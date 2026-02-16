import uuid

import aioboto3

from src.core.config import settings

_session = aioboto3.Session()


def _get_client():
    return _session.client(
        's3',
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


async def upload_file(content: bytes, content_type: str, extension: str) -> str:
    key = f'uploads/{uuid.uuid4().hex}.{extension}'
    async with _get_client() as client:
        await client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
    base_url = settings.S3_PUBLIC_URL.rstrip('/')
    return f'{base_url}/{key}'
