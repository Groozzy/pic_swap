import io
from unittest.mock import call, MagicMock, mock_open

import falcon
from falcon import testing
import msgpack
import pytest

import pic_swap.app
import pic_swap.images


@pytest.fixture
def mock_store():
    return MagicMock()


@pytest.fixture
def client(mock_store):
    return testing.TestClient(pic_swap.app.create_app(mock_store))


def test_get_images(client):
    response = client.simulate_get('/images')
    assert msgpack.unpackb(response.content, raw=False) == {
        'images': [
            {'href': '/images/image.png'},
        ]
    }
    assert response.status == falcon.HTTP_OK


def test_post_image(client, mock_store):
    file_name = 'fake-image-name.xyz'
    mock_store.save.return_value = file_name
    image_content_type = 'image/xyz'

    response = client.simulate_post(
        path='/images',
        body=b'fake-image-bytes',
        headers={'content-type': image_content_type},
    )
    assert response.status == falcon.HTTP_CREATED
    assert response.headers['Location'] == f'/images/{file_name}'
    # FIXME: wsgiref.validate.InputWrapper != falcon.BoundedStream
    assert isinstance(mock_store.save.call_args[0][0], falcon.BoundedStream)
    assert mock_store.save.call_args[0][1] == image_content_type


def test_save_image(monkeypatch):
    mock_file_open = mock_open()
    fake_uuid = 'fake-uuid'

    def mock_uuid_generator():
        return fake_uuid

    fake_image_bytes = b'fake-image-bytes'
    fake_request_stream = io.BytesIO(fake_image_bytes)
    storage_path = 'fake-storage-path'
    store = pic_swap.images.ImageStore(storage_path,
                                       uuid_generator=mock_uuid_generator,
                                       file_open=mock_file_open)
    assert store.save(fake_request_stream, 'image/png') == f'{fake_uuid}.png'
    assert call().write(fake_image_bytes) in mock_file_open.mock_calls
