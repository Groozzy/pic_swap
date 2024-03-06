import io
import mimetypes
import os
import uuid

import falcon
import msgpack


class Image(object):
    def __init__(self, image_store):
        self._image_store = image_store

    def on_get(self, request, response):
        response.data = msgpack.packb(
            {
                    'images': [
                        {'href': '/images/image.png'},
                    ]
                },
            use_bin_type=True,
        )
        response.content_type = falcon.MEDIA_MSGPACK

    def on_post(self, request, response):
        filename = self._image_store.save(request.stream, request.content_type)
        response.status = falcon.HTTP_CREATED
        response.location = f'/images/{filename}'


class ImageStore(object):
    _CHUNK_SIZE = 4096

    def __init__(
            self, storage_path, uuid_generator=uuid.uuid4, file_open=io.open):
        self._storage_path = storage_path
        self._uuid_generator = uuid_generator
        self._file_open = file_open

    def save(self, image_stream, image_content_type):
        extension = mimetypes.guess_extension(image_content_type)
        file_name = f'{self._uuid_generator()}{extension}'
        image_path = os.path.join(self._storage_path, file_name)
        with self._file_open(image_path, 'wb') as image_file:
            while True:
                chunk = image_stream.read(self._CHUNK_SIZE)
                if not chunk:
                    break

                image_file.write(chunk)
        return file_name
