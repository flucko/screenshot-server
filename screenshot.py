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
        <img src="latest.png?t={timestamp}" alt="Latest Screenshot">
    </div>
    <button id="fullscreenBtn" onclick="toggleFullscreen()">Fullscreen</button>
    <script>
        function toggleFullscreen() {{
            var elem = document.documentElement;
            
            // Try standard fullscreen API first
            if (elem.requestFullscreen) {{
                elem.requestFullscreen();
            }} else if (elem.webkitRequestFullscreen) {{ // Safari/old Chrome
                elem.webkitRequestFullscreen();
            }} else if (elem.mozRequestFullScreen) {{ // Firefox
                elem.mozRequestFullScreen();
            }} else if (elem.msRequestFullscreen) {{ // IE/Edge
                elem.msRequestFullscreen();
            }} else {{
                // For iOS 9 and other devices without fullscreen API
                // Hide the button and rely on meta tags for web app mode
                document.body.classList.add('fullscreen-mode');
                // Prompt user to add to home screen for true fullscreen
                if (navigator.standalone === false) {{
                    alert('For fullscreen on iOS: tap Share button and "Add to Home Screen"');
                }}
            }}
        }}
        
        // Hide button if already in standalone mode (iOS web app)
        if (window.navigator.standalone === true) {{
            document.getElementById('fullscreenBtn').style.display = 'none';
        }}
        
        // Listen for fullscreen changes
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
        document.addEventListener('mozfullscreenchange', handleFullscreenChange);
        document.addEventListener('MSFullscreenChange', handleFullscreenChange);
        
        function handleFullscreenChange() {{
            if (!document.fullscreenElement && !document.webkitFullscreenElement && 
                !document.mozFullScreenElement && !document.msFullscreenElement) {{
                document.body.classList.remove('fullscreen-mode');
            }} else {{
                document.body.classList.add('fullscreen-mode');
            }}
        }}
        
        // Prevent default touch behaviors that might interfere
        document.addEventListener('touchmove', function(e) {{
            e.preventDefault();
        }}, {{ passive: false }});
    </script>
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
