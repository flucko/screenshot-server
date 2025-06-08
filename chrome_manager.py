#!/usr/bin/env python3
import os
import sys
import time
import json
import psutil
import threading
import signal
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Chrome Manager - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChromeManager:
    def __init__(self):
        self.driver = None
        self.start_time = None
        self.last_memory_log = 0
        self.memory_threshold = 100  # Log every 100MB increase
        self.lock_file = '/tmp/chrome_manager.lock'
        self.status_file = '/tmp/chrome_status.json'
        self.running = True
        
        # Configuration from environment
        self.keep_open = os.environ.get('KEEP_CHROME_OPEN', 'false').lower() == 'true'
        self.max_memory_mb = int(os.environ.get('CHROME_MAX_MEMORY_MB', '1024'))
        self.restart_hours = int(os.environ.get('CHROME_RESTART_HOURS', '24'))
        self.target_url = os.environ.get('TARGET_URL', 'http://192.168.0.121:8180/')
        self.page_load_delay = int(os.environ.get('PAGE_LOAD_DELAY', '10'))
        
        # Chrome configuration
        self.resolution = os.environ.get('RESOLUTION', '1024x768')
        self.width, self.height = map(int, self.resolution.split('x'))
        
    def setup_chrome_options(self):
        """Configure Chrome options for persistent mode"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={self.width},{self.height}')
        
        # Enable remote debugging for persistent connection
        chrome_options.add_argument('--remote-debugging-port=9222')
        
        # Use a persistent user data directory
        chrome_options.add_argument('--user-data-dir=/tmp/chrome-profile')
        
        # Additional optimizations for long-running Chrome
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-dev-tools')
        
        return chrome_options
    
    def start_chrome(self):
        """Start Chrome browser instance"""
        try:
            logger.info("Starting Chrome browser...")
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=self.setup_chrome_options())
            self.start_time = datetime.now()
            
            # Load initial page
            logger.info(f"Loading initial page: {self.target_url}")
            self.driver.get(self.target_url)
            time.sleep(self.page_load_delay)
            
            # Write status
            self.write_status('running')
            logger.info("Chrome started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Chrome: {e}")
            self.write_status('error', str(e))
            return False
    
    def stop_chrome(self):
        """Stop Chrome browser instance"""
        if self.driver:
            try:
                logger.info("Stopping Chrome browser...")
                self.driver.quit()
                self.driver = None
                self.write_status('stopped')
                logger.info("Chrome stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Chrome: {e}")
    
    def restart_chrome(self, reason="Manual restart"):
        """Restart Chrome browser"""
        logger.info(f"Restarting Chrome: {reason}")
        self.stop_chrome()
        time.sleep(2)  # Brief pause before restart
        return self.start_chrome()
    
    def get_chrome_memory_usage(self):
        """Get Chrome process memory usage in MB"""
        if not self.driver:
            return 0
            
        try:
            # Get Chrome process PID
            chrome_pid = self.driver.service.process.pid
            
            # Get total memory for Chrome and all child processes
            total_memory = 0
            parent = psutil.Process(chrome_pid)
            
            # Include parent process
            total_memory += parent.memory_info().rss
            
            # Include all child processes
            for child in parent.children(recursive=True):
                try:
                    total_memory += child.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return total_memory / 1024 / 1024  # Convert to MB
            
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return 0
    
    def monitor_memory(self):
        """Monitor and log Chrome memory usage"""
        current_memory = self.get_chrome_memory_usage()
        
        if current_memory > self.last_memory_log + self.memory_threshold:
            logger.info(f"Chrome memory usage: {current_memory:.1f} MB (increased by {current_memory - self.last_memory_log:.1f} MB)")
            self.last_memory_log = current_memory
        
        # Check if memory limit exceeded
        if current_memory > self.max_memory_mb:
            logger.warning(f"Chrome memory usage ({current_memory:.1f} MB) exceeds limit ({self.max_memory_mb} MB)")
            self.restart_chrome(f"Memory limit exceeded: {current_memory:.1f} MB > {self.max_memory_mb} MB")
    
    def check_restart_schedule(self):
        """Check if Chrome needs scheduled restart"""
        if self.driver and self.start_time:
            runtime = datetime.now() - self.start_time
            if runtime > timedelta(hours=self.restart_hours):
                self.restart_chrome(f"Scheduled restart after {self.restart_hours} hours")
    
    def write_status(self, status, error=None):
        """Write Chrome status to file"""
        status_data = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'pid': self.driver.service.process.pid if self.driver else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'memory_mb': self.get_chrome_memory_usage(),
            'error': error
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f)
        except Exception as e:
            logger.error(f"Failed to write status: {e}")
    
    def health_check(self):
        """Check if Chrome is still responsive"""
        if not self.driver:
            return False
            
        try:
            # Try to get current URL - simple health check
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        monitor_interval = 30  # Check every 30 seconds
        
        while self.running:
            try:
                if self.driver:
                    # Check health
                    if not self.health_check():
                        logger.error("Chrome is unresponsive")
                        self.restart_chrome("Chrome unresponsive")
                    
                    # Monitor memory
                    self.monitor_memory()
                    
                    # Check restart schedule
                    self.check_restart_schedule()
                    
                    # Update status
                    self.write_status('running')
                
                time.sleep(monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(monitor_interval)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_chrome()
        
        # Clean up files
        for file in [self.lock_file, self.status_file]:
            if os.path.exists(file):
                os.remove(file)
        
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        if not self.keep_open:
            logger.info("KEEP_CHROME_OPEN is not enabled, exiting Chrome Manager")
            sys.exit(0)
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Create lock file
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Start Chrome
        if not self.start_chrome():
            logger.error("Failed to start Chrome, exiting")
            sys.exit(1)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("Chrome Manager is running")
        
        # Keep main thread alive
        while self.running:
            time.sleep(1)

if __name__ == '__main__':
    manager = ChromeManager()
    manager.run()