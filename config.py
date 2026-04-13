import os

# Screenshot target
TARGET_URL = os.environ.get('TARGET_URL', 'http://192.168.0.121:8180/')
PAGE_LOAD_DELAY = int(os.environ.get('PAGE_LOAD_DELAY', '10'))

# Resolution settings
RESOLUTION = os.environ.get('RESOLUTION', '1024x768')
try:
    WIDTH, HEIGHT = map(int, RESOLUTION.split('x'))
except ValueError:
    WIDTH, HEIGHT = 1024, 768

# Image output settings
IMAGE_FORMAT = os.environ.get('IMAGE_FORMAT', 'jpeg').lower()  # jpeg or webp
IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY', '80'))
