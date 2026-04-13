#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import io
import logging
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Screenshot - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = '/var/www/html'


def get_output_extension():
    """Get file extension based on configured format."""
    if config.IMAGE_FORMAT == 'webp':
        return 'webp'
    return 'jpg'


def get_pillow_format():
    """Get Pillow format string."""
    if config.IMAGE_FORMAT == 'webp':
        return 'WEBP'
    return 'JPEG'


def ensure_index_html():
    """Create index.html if it doesn't exist. Uses JS cache-busting."""
    index_path = os.path.join(OUTPUT_DIR, 'index.html')
    if os.path.exists(index_path):
        return

    ext = get_output_extension()
    index_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Viewer</title>
    <meta http-equiv="refresh" content="60">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            overflow: hidden;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
        }}
        #container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
        }}
        #fullscreenBtn {{
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px 15px;
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            z-index: 1000;
            -webkit-tap-highlight-color: transparent;
        }}
        #fullscreenBtn:active {{
            background: rgba(255,255,255,0.7);
        }}
        .fullscreen-mode #fullscreenBtn {{
            display: none;
        }}
        @media (display-mode: standalone) {{
            #fullscreenBtn {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div id="container">
        <img id="screenshot" alt="Latest Screenshot">
    </div>
    <button id="fullscreenBtn" onclick="toggleFullscreen()">Fullscreen</button>
    <script>
        // Load image with cache-busting timestamp
        var img = document.getElementById('screenshot');
        img.src = 'latest.{ext}?t=' + Date.now();

        function toggleFullscreen() {{
            var elem = document.documentElement;
            if (elem.requestFullscreen) {{
                elem.requestFullscreen();
            }} else if (elem.webkitRequestFullscreen) {{
                elem.webkitRequestFullscreen();
            }}
        }}

        if (window.navigator.standalone === true) {{
            document.getElementById('fullscreenBtn').style.display = 'none';
        }}

        document.addEventListener('touchmove', function(e) {{
            e.preventDefault();
        }}, {{ passive: false }});
    </script>
</body>
</html>'''

    with open(index_path, 'w') as f:
        f.write(index_content)
    logger.info("Created index.html")


def capture_screenshot():
    """Capture a screenshot and save as optimized JPEG/WebP."""
    target_url = config.TARGET_URL
    width, height = config.WIDTH, config.HEIGHT
    page_load_delay = config.PAGE_LOAD_DELAY

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'--window-size={width},{height}')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-features=TranslateUI')

    # Initialize driver
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the webpage
        logger.info(f"Loading {target_url}...")
        driver.get(target_url)
        time.sleep(page_load_delay)
        driver.set_window_size(width, height)

        # Take screenshot as PNG bytes
        png_data = driver.get_screenshot_as_png()

        # Convert to configured format with Pillow
        img = Image.open(io.BytesIO(png_data))
        img = img.convert('RGB')  # Drop alpha channel for JPEG

        ext = get_output_extension()
        output_path = os.path.join(OUTPUT_DIR, f'latest.{ext}')

        img.save(
            output_path,
            format=get_pillow_format(),
            quality=config.IMAGE_QUALITY,
            optimize=True,
        )

        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info(f"Screenshot saved: {output_path} ({file_size_kb:.0f} KB, {config.IMAGE_FORMAT} q{config.IMAGE_QUALITY})")

        # Ensure index.html exists
        ensure_index_html()

    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        raise

    finally:
        driver.quit()


if __name__ == '__main__':
    capture_screenshot()
