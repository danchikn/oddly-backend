import logging
from datetime import date
from uuid import UUID

import aioboto3

from src.core.config import settings

logger = logging.getLogger(__name__)

_session = aioboto3.Session()


def _get_client():
    return _session.client(
        's3',
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


async def upload_file(
    content: bytes,
    content_type: str,
    extension: str,
    user_id: UUID,
    timestamp: int,
    file_number: int,
) -> str:
    folder = date.today().isoformat()
    filename = f'{user_id}_{timestamp}_{file_number}.{extension}'
    key = f'{folder}/{filename}'
    try:
        async with _get_client() as client:
            await client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=content,
                ContentType=content_type,
            )
    except Exception as e:
        logger.error('S3 upload failed: key=%s, error=%s', key, e)
        raise
    logger.info('File uploaded to S3: key=%s', key)
    base_url = settings.S3_PUBLIC_URL.rstrip('/')
    return f'{base_url}/{key}'
