import base64
from PIL import Image
import os


def decoder(image_64_encode, name):
    image_64_decode = base64.decodestring(image_64_encode)
    image_result = open(f'static/img/{name}', 'wb')  # create a writable image and write the decoding result
    image_result.write(image_64_encode)
    print(image_64_encode)
    print(image_64_decode)
    # image = Image.frombytes('RGBA', (128, 128), image_64_encode, 'raw')
    return image_result
