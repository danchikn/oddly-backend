import pytest

from src.clients.s3 import upload_file
from src.core.config import settings


@pytest.mark.s3
@pytest.mark.asyncio
async def test_real_s3_upload_and_url():
    content = b'\xff\xd8\xff\xe0' + b'\x00' * 100
    url = await upload_file(
        content=content,
        content_type='image/jpeg',
        extension='jpg',
        user_id='00000000-0000-0000-0000-000000000000',
        timestamp=1234567890,
        file_number=1,
    )

    print(url)
    assert url.startswith(settings.S3_PUBLIC_URL)
    assert '00000000-0000-0000-0000-000000000000' in url
    assert '1234567890' in url
    assert url.endswith('_1.jpg')
