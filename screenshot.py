#!/usr/bin/env python3
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import io

def capture_screenshot():
    # Get environment variables
    target_url = os.environ.get('TARGET_URL', 'http://192.168.0.121:8180/')
    resolution = os.environ.get('RESOLUTION', '1024x768')
    width, height = map(int, resolution.split('x'))
    page_load_delay = int(os.environ.get('PAGE_LOAD_DELAY', '10'))
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'--window-size={width},{height}')
    
    # Initialize driver with Chromium
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load the webpage
        print(f"Loading {target_url}...")
        driver.get(target_url)
        
        # Wait for page to load
        time.sleep(page_load_delay)
        
        # Set window size
        driver.set_window_size(width, height)
        
        # Take screenshot
        screenshot = driver.get_screenshot_as_png()
        
        # Save screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save timestamped version
        timestamped_path = f'/var/www/html/screenshot_{timestamp}.png'
        with open(timestamped_path, 'wb') as f:
            f.write(screenshot)
        
        # Save as latest.png for easy access
        latest_path = '/var/www/html/latest.png'
        with open(latest_path, 'wb') as f:
            f.write(screenshot)
        
        # Create a simple index.html
        index_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Screenshot Viewer</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body {{ margin: 0; padding: 0; background: #000; }}
        img {{ width: 100%; height: 100vh; object-fit: contain; }}
    </style>
</head>
<body>
    <img src="latest.png?t={timestamp}" alt="Latest Screenshot">
</body>
</html>'''
        
        with open('/var/www/html/index.html', 'w') as f:
            f.write(index_content)
        
        print(f"Screenshot saved successfully at {timestamp}")
        
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
    
    finally:
        driver.quit()

if __name__ == '__main__':
    capture_screenshot()