# Screenshot Server for Legacy Devices

[![Docker Build and Push](https://github.com/flucko/screenshot-server/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/flucko/screenshot-server/actions/workflows/docker-publish.yml)
[![Docker Pulls](https://img.shields.io/docker/pulls/flucko/screenshot-server)](https://hub.docker.com/r/flucko/screenshot-server)

This Docker container captures screenshots of a webpage at configurable intervals and serves them via a simple web interface, perfect for displaying on older devices that can't handle modern web technologies.

## Quick Start

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Access the screenshot viewer at:
```
http://localhost:8080
```

## Using from Docker Hub

```yaml
services:
  screenshot-server:
    image: flucko/screenshot-server:latest
    ports:
      - "8080:80"
    environment:
      - TARGET_URL=http://example.com/
      - RESOLUTION=1024x768
      - SCREENSHOT_INTERVAL=60
    restart: unless-stopped
    volumes:
      - screenshot-data:/var/www/html

volumes:
  screenshot-data:
```

## Configuration

Edit the environment variables in `docker-compose.yml`:

| Variable | Default | Description |
|---|---|---|
| `TARGET_URL` | `http://192.168.0.121:8180/` | The webpage to capture |
| `RESOLUTION` | `1024x768` | Screenshot resolution (WIDTHxHEIGHT) |
| `SCREENSHOT_INTERVAL` | `60` | Screenshot frequency in minutes |
| `PAGE_LOAD_DELAY` | `10` | Wait time in seconds before capturing |
| `TZ` | `America/Toronto` | Timezone for timestamps |
| `IMAGE_FORMAT` | `jpeg` | Output format: `jpeg` or `webp` |
| `IMAGE_QUALITY` | `80` | Compression quality (1-100) |

Example resolutions for older iPads:
- iPad 1/2: `1024x768`
- iPad 3/4: `2048x1536`
- iPad Mini 1: `1024x768`

Example intervals:
- `5` - Every 5 minutes
- `30` - Every 30 minutes
- `60` - Every hour (default)
- `1440` - Once daily

## How It Works

1. Takes a screenshot of the target URL at specified intervals using headless Chromium
2. Converts to optimized JPEG (or WebP) for minimal file size
3. Serves the screenshot at `/latest.jpg` with an auto-refreshing HTML viewer
4. Managed by Supervisord: nginx + cron + initial screenshot on startup

## Manual Docker Build

```bash
# Build the image
docker build -t screenshot-server .

# Run the container
docker run -d \
  -p 8080:80 \
  -e TARGET_URL="http://192.168.0.121:8180/" \
  -e RESOLUTION="1024x768" \
  -e SCREENSHOT_INTERVAL="60" \
  -e PAGE_LOAD_DELAY="10" \
  -e TZ="America/Toronto" \
  screenshot-server
```

## CI/CD with GitHub Actions

On every push to `main`:
- Builds multi-architecture images (amd64 and arm64)
- Publishes to Docker Hub as `flucko/screenshot-server:latest`
- Semver tags (`v1.2.3`) also create versioned images

## Breaking Changes

### v2.0

- **Single image**: The separate Alpine and Ubuntu image variants have been removed. There is now a single Alpine-based image (`latest`). If you were using `docker-compose.alpine.yml`, switch to `docker-compose.yml`.
- **JPEG output**: Screenshots are now saved as `latest.jpg` instead of `latest.png` by default. Set `IMAGE_FORMAT=webp` for WebP output. The `index.html` viewer handles this automatically.
- **Chrome persistence removed**: The `KEEP_CHROME_OPEN`, `CHROME_MAX_MEMORY_MB`, and `CHROME_RESTART_HOURS` environment variables are no longer supported. Chrome starts fresh for each screenshot.

## Troubleshooting

1. **Page not fully loaded**: Increase `PAGE_LOAD_DELAY` value
2. **Wrong timezone**: Set `TZ` environment variable in docker-compose.yml
3. **View logs**: `docker-compose logs -f`
4. **Check cron**: `docker exec <container-id> crontab -l`
5. **Check processes**: `docker exec <container-id> supervisorctl status`
