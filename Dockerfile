# Stage 1: Build dependencies that need compilation (psutil)
FROM python:3.9-alpine AS builder

RUN apk add --no-cache gcc musl-dev linux-headers \
    && pip install --no-cache-dir --prefix=/install psutil==5.9.6 selenium==4.15.2 pillow==10.1.0

# Stage 2: Runtime image
FROM python:3.9-alpine

# Install runtime dependencies only
RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    nginx \
    supervisor \
    bash \
    tzdata

# Copy pre-built Python packages from builder
COPY --from=builder /install /usr/local

# Create necessary directories
RUN mkdir -p /app /var/www/html /var/log/supervisor

# Copy application files
COPY config.py /app/
COPY screenshot.py /app/
COPY nginx.conf /etc/nginx/http.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start.sh /app/

# Make start script executable
RUN chmod +x /app/start.sh

# Healthcheck via nginx
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO /dev/null http://localhost:80/ || exit 1

# Expose port for web server
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]