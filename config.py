import os

# Chrome operation settings
KEEP_CHROME_OPEN = os.environ.get('KEEP_CHROME_OPEN', 'false').lower() == 'true'
TARGET_URL = os.environ.get('TARGET_URL', 'http://192.168.0.121:8180/')
PAGE_LOAD_DELAY = int(os.environ.get('PAGE_LOAD_DELAY', '10'))

# Resolution settings
RESOLUTION = os.environ.get('RESOLUTION', '1024x768')
try:
    WIDTH, HEIGHT = map(int, RESOLUTION.split('x'))
except ValueError:
    WIDTH, HEIGHT = 1024, 768

# Chrome Manager specific settings
CHROME_MAX_MEMORY_MB = int(os.environ.get('CHROME_MAX_MEMORY_MB', '1024'))
CHROME_RESTART_HOURS = int(os.environ.get('CHROME_RESTART_HOURS', '24'))
