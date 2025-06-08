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

## Configuration

Edit the environment variables in `docker-compose.yml`:

- `TARGET_URL`: The webpage to capture (default: `http://192.168.0.121:8180/`)
- `RESOLUTION`: Screenshot resolution (default: `1024x768`)
- `SCREENSHOT_INTERVAL`: Screenshot frequency in minutes (default: `60`)
- `PAGE_LOAD_DELAY`: Wait time in seconds before taking screenshot (default: `10`)
- `TZ`: Timezone for timestamps (default: `America/Toronto`)

### Chrome Persistence Mode (Optional)

To reduce API calls and improve performance, you can enable Chrome persistence mode which keeps the browser open between screenshots:

- `KEEP_CHROME_OPEN`: Enable persistent Chrome mode (default: `false`)
- `CHROME_MAX_MEMORY_MB`: Maximum memory usage before Chrome restart (default: `1024`)
- `CHROME_RESTART_HOURS`: Hours before scheduled Chrome restart (default: `24`)

Example resolutions for older iPads:
- iPad 1/2: `1024x768`
- iPad 3/4: `2048x1536`
- iPad Mini 1: `1024x768`

Example intervals:
- `5` - Every 5 minutes
- `30` - Every 30 minutes
- `60` - Every hour (default)
- `120` - Every 2 hours
- `1440` - Once daily

## Using from Docker Hub

Three image variants are available on Docker Hub:

- `flucko/screenshot-server:latest` - Standard Debian-based image (~300MB)
- `flucko/screenshot-server:latest-alpine` - Alpine Linux variant (~180MB)
- `flucko/screenshot-server:latest-slim` - Optimized multi-stage build (~150MB)

Update `docker-compose.yml` to use a pre-built image:

```yaml
services:
  screenshot-server:
    image: flucko/screenshot-server:latest-slim  # Or :latest, :latest-alpine
    ports:
      - "8080:80"
    # ... rest of configuration
```

## Manual Docker Build

```bash
# Build the image
docker build -t screenshot-server .

## Run the container
docker run -d \
  -p 8080:80 \
  -e TARGET_URL="http://192.168.0.121:8180/" \
  -e RESOLUTION="1024x768" \
  -e SCREENSHOT_INTERVAL="60" \
  -e PAGE_LOAD_DELAY="10" \
  -e TZ="America/Toronto" \
  screenshot-server
```

## How It Works

1. Takes a screenshot of the target URL at specified intervals
2. Serves the latest screenshot at `/latest.png`
3. Auto-refreshing HTML page displays the screenshot
4. Optimized for low-bandwidth and legacy browsers

### Chrome Persistence Mode

When `KEEP_CHROME_OPEN=true` is set:
1. A Chrome Manager service starts and maintains a persistent browser instance
2. Screenshots reuse the existing browser connection, reducing overhead
3. Chrome automatically restarts after 24 hours or if memory limits are exceeded
4. Memory usage is monitored and logged when it increases
5. Falls back to normal operation if the persistent instance fails

## Files

- `latest.png` - Most recent screenshot
- `screenshot_YYYYMMDD_HHMMSS.png` - Timestamped screenshots
- `index.html` - Auto-refreshing viewer page

## Image Size Optimization

The default Docker image is ~300MB due to Chromium and dependencies. For a smaller footprint (~150MB), use the Alpine-based optimized build:

```bash
# Use the optimized build
docker-compose -f docker-compose.optimized.yml up -d
```

This uses:
- Alpine Linux base (5MB vs 120MB)
- Multi-stage build to exclude build dependencies
- Optimized package installation

## CI/CD with GitHub Actions

This repository includes automated Docker builds using GitHub Actions. On every push to the `main` branch:
- Builds multi-architecture images (amd64 and arm64) for all three variants
- Creates the following tags for each variant:
  - `flucko/screenshot-server:latest` (standard build)
  - `flucko/screenshot-server:latest-alpine` (Alpine variant)
  - `flucko/screenshot-server:latest-slim` (optimized build)
- Also creates branch and SHA-based tags for versioning

## Troubleshooting

### Chrome Persistence Issues

If you're having issues with Chrome persistence mode:

1. **Check Chrome Manager logs:**
   ```bash
   docker-compose logs | grep "Chrome Manager"
   ```

2. **Verify Chrome status:**
   ```bash
   docker exec <container-id> cat /tmp/chrome_status.json
   ```

3. **Monitor memory usage:**
   Look for memory logs indicating when Chrome memory increases or restarts occur.

4. **Common issues:**
   - If Chrome crashes frequently, try increasing `CHROME_MAX_MEMORY_MB`
   - For pages with memory leaks, decrease `CHROME_RESTART_HOURS` 
   - Ensure the target URL is accessible from within the container

