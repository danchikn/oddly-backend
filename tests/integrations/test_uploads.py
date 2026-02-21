from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest


def _make_image(size: int = 100, content_type: str = 'image/jpeg', filename: str = 'photo.jpg'):
    return ('files', (filename, BytesIO(b'\xff\xd8' + b'\x00' * size), content_type))


MOCK_URL = 'https://s3.example.com/2026-02-16/test.jpg'


@pytest.mark.asyncio
@patch('src.modules.uploads.router.upload_file', new_callable=AsyncMock, return_value=MOCK_URL)
async def test_upload_single_photo(mock_upload, restaurant_client):
    client, _ = restaurant_client
    response = await client.post('/api/uploads', files=[_make_image()])
    assert response.status_code == 200
    data = response.json()
    assert len(data['urls']) == 1
    assert data['urls'][0] == MOCK_URL
    mock_upload.assert_called_once()


@pytest.mark.asyncio
@patch('src.modules.uploads.router.upload_file', new_callable=AsyncMock, return_value=MOCK_URL)
async def test_upload_multiple_photos(mock_upload, restaurant_client):
    client, _ = restaurant_client
    files = [_make_image(filename=f'photo{i}.jpg') for i in range(3)]
    response = await client.post('/api/uploads', files=files)
    assert response.status_code == 200
    data = response.json()
    assert len(data['urls']) == 3
    assert mock_upload.call_count == 3


@pytest.mark.asyncio
async def test_upload_no_auth(client):
    response = await client.post('/api/uploads', files=[_make_image()])
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_invalid_type(restaurant_client):
    client, _ = restaurant_client
    bad_file = _make_image(content_type='application/pdf', filename='doc.pdf')
    response = await client.post('/api/uploads', files=[bad_file])
    assert response.status_code == 400
    assert 'only JPEG, PNG and WebP' in response.json()['detail']


@pytest.mark.asyncio
async def test_upload_file_too_large(restaurant_client):
    client, _ = restaurant_client
    big_file = _make_image(size=6 * 1024 * 1024)
    response = await client.post('/api/uploads', files=[big_file])
    assert response.status_code == 400
    assert '5 MB' in response.json()['detail']


@pytest.mark.asyncio
async def test_upload_too_many_files(restaurant_client):
    client, _ = restaurant_client
    files = [_make_image(filename=f'photo{i}.jpg') for i in range(11)]
    response = await client.post('/api/uploads', files=files)
    assert response.status_code == 400
    assert '10 files' in response.json()['detail']


@pytest.mark.asyncio
@patch('src.modules.uploads.router.upload_file', new_callable=AsyncMock, return_value=MOCK_URL)
async def test_upload_passes_user_id(mock_upload, restaurant_client):
    client, user = restaurant_client
    response = await client.post('/api/uploads', files=[_make_image()])
    assert response.status_code == 200
    kwargs = mock_upload.call_args[1]
    assert kwargs['user_id'] == user.id
    assert kwargs['file_number'] == 1


@pytest.mark.asyncio
@patch('src.modules.uploads.router.upload_file', new_callable=AsyncMock, return_value=MOCK_URL)
async def test_upload_file_numbers_sequential(mock_upload, restaurant_client):
    client, _ = restaurant_client
    files = [_make_image(filename=f'photo{i}.jpg') for i in range(3)]
    response = await client.post('/api/uploads', files=files)
    assert response.status_code == 200
    file_numbers = [call[1]['file_number'] for call in mock_upload.call_args_list]
    assert file_numbers == [1, 2, 3]
