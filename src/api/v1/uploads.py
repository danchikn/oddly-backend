import time

from fastapi import APIRouter, Depends, UploadFile
from loguru import logger

from src.api.dependencies import get_current_user
from src.clients.s3 import S3Client
from src.core.config import settings
from src.dependencies import get_s3_client
from src.domain.models.user import User

router = APIRouter(prefix='/uploads', tags=['uploads'])

EXTENSION_MAP = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
}


@router.post('')
async def upload_photos(
    files: list[UploadFile],
    user: User = Depends(get_current_user),
    s3_client: S3Client = Depends(get_s3_client),
):
    from fastapi import HTTPException, status

    if len(files) > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Maximum 10 files per request')

    timestamp = int(time.time())
    urls = []

    for i, file in enumerate(files, start=1):
        if file.content_type not in settings.UPLOAD_ALLOWED_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'File "{file.filename}": only JPEG, PNG and WebP are allowed')

        content = await file.read()

        if len(content) > settings.UPLOAD_MAX_SIZE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'File "{file.filename}" exceeds 5 MB limit')

        extension = EXTENSION_MAP.get(file.content_type, 'jpg')
        url = await s3_client.upload_file(
            content=content, content_type=file.content_type,
            extension=extension, user_id=user.id,
            timestamp=timestamp, file_number=i,
        )
        urls.append(url)

    logger.info('Photos uploaded: user_id={}, count={}', user.id, len(urls))
    return {'urls': urls}
