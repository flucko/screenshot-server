FROM python:3.9-slim

# Install dependencies for Chromium and nginx
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    nginx \
    cron \
    supervisor \
    ca-certificates \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install selenium pillow

# Create necessary directories
RUN mkdir -p /app /var/www/html /var/log/supervisor

# Copy application files
COPY screenshot.py /app/
COPY nginx.conf /etc/nginx/sites-available/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start.sh /app/

# Make start script executable
RUN chmod +x /app/start.sh

# Expose port for web server
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]