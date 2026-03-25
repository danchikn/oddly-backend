from loguru import logger
from datetime import date
from uuid import UUID

import aioboto3

from src.core.config import settings



class S3Client:
    def __init__(self) -> None:
        self._session = aioboto3.Session()
        self._endpoint_url = settings.S3_ENDPOINT_URL or None
        self._access_key = settings.S3_ACCESS_KEY
        self._secret_key = settings.S3_SECRET_KEY
        self._region = settings.S3_REGION
        self._bucket = settings.S3_BUCKET
        self._public_url = settings.S3_PUBLIC_URL.rstrip('/')

    def _get_client(self):
        return self._session.client(
            's3',
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
        )

    async def upload_file(
        self,
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
            async with self._get_client() as client:
                await client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=content,
                    ContentType=content_type,
                )
        except Exception as e:
            logger.error('S3 upload failed: key=%s, error=%s', key, e)
            raise
        logger.info('File uploaded to S3: key=%s', key)
        return f'{self._public_url}/{key}'
