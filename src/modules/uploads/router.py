import logging
import time

from fastapi import APIRouter, Depends, UploadFile

from src.clients.s3 import upload_file
from src.core.config import settings
from src.core.exceptions import BadRequestError
from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User

logger = logging.getLogger(__name__)
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
):
    if len(files) > 10:
        logger.warning('Rejected upload: user_id=%s, reason=too_many_files, count=%d', user.id, len(files))
        raise BadRequestError(detail='Maximum 10 files per request')

    timestamp = int(time.time())
    urls = []
    total_size = 0

    for i, file in enumerate(files, start=1):
        if file.content_type not in settings.UPLOAD_ALLOWED_TYPES:
            logger.warning('Rejected upload: user_id=%s, reason=invalid_type, file=%s', user.id, file.filename)
            raise BadRequestError(detail=f'File "{file.filename}": only JPEG, PNG and WebP are allowed')

        content = await file.read()

        if len(content) > settings.UPLOAD_MAX_SIZE:
            logger.warning('Rejected upload: user_id=%s, reason=file_too_large, file=%s', user.id, file.filename)
            raise BadRequestError(detail=f'File "{file.filename}" exceeds 5 MB limit')

        total_size += len(content)
        extension = EXTENSION_MAP.get(file.content_type, 'jpg')
        url = await upload_file(
            content=content,
            content_type=file.content_type,
            extension=extension,
            user_id=user.id,
            timestamp=timestamp,
            file_number=i,
        )
        urls.append(url)

    logger.info('Photos uploaded: user_id=%s, count=%d, total_size=%d', user.id, len(urls), total_size)
    return {'urls': urls}
