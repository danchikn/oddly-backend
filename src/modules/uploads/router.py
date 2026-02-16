from fastapi import APIRouter, Depends, UploadFile

from src.clients.s3 import upload_file
from src.core.config import settings
from src.core.exceptions import BadRequestError
from src.modules.auth.dependencies import get_current_user
from src.modules.users.models import User

router = APIRouter(prefix='/uploads', tags=['uploads'])

EXTENSION_MAP = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
}


@router.post('')
async def upload_photo(
    file: UploadFile,
    user: User = Depends(get_current_user),
):
    if file.content_type not in settings.UPLOAD_ALLOWED_TYPES:
        raise BadRequestError(detail='Only JPEG, PNG and WebP images are allowed')

    content = await file.read()

    if len(content) > settings.UPLOAD_MAX_SIZE:
        raise BadRequestError(detail='File size exceeds 5 MB limit')

    extension = EXTENSION_MAP.get(file.content_type, 'jpg')
    url = await upload_file(content, file.content_type, extension)

    return {'url': url}
