import os

import falcon

from pic_swap.images import Image, ImageStore
import dotenv


dotenv.load_dotenv()


def create_app(image_store: ImageStore) -> falcon.App:
    app = falcon.App()
    app.add_route('/images', Image(image_store))
    return app


def get_app() -> falcon.App:
    return create_app(ImageStore(os.getenv('LOOK_STORE_PATH', '.')))
