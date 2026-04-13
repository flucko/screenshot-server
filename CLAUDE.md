# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a containerized web screenshot service designed to capture and serve screenshots of web pages for display on legacy devices. It uses headless Chromium to render pages, converts to optimized JPEG, and serves them via Nginx.

## Architecture

The service runs multiple processes managed by Supervisord:
1. **screenshot-init**: One-time process that captures initial screenshot on startup
2. **screenshot-cron**: Manages cron daemon for periodic screenshots based on `SCREENSHOT_INTERVAL`
3. **nginx**: Serves screenshots and auto-refreshing HTML viewer

Key flow: `start.sh` → sets timezone → configures cron → runs `screenshot.py` periodically → saves JPEG to `/var/www/html/`

### Screenshot Pipeline
1. `screenshot.py` launches fresh headless Chrome each time
2. Navigates to `TARGET_URL`, waits `PAGE_LOAD_DELAY` seconds
3. Captures PNG screenshot via Selenium
4. Converts to JPEG (or WebP) using Pillow with configurable quality
5. Saves as `latest.jpg` to `/var/www/html/`
6. `index.html` is created once (not regenerated) — uses JS cache-busting

## Build Commands

```bash
# Build image
docker build -t screenshot-server .

# Run with docker-compose
docker-compose up -d
```

## Testing & Development

```bash
# View logs
docker-compose logs -f

# Check if screenshot is being served
curl http://localhost:8080/latest.jpg

# Verify cron job
docker exec <container-id> crontab -l

# Debug supervisor processes
docker exec <container-id> supervisorctl status
```

## Important Configuration Details

- Single Alpine-based Docker image with multi-stage build
- Cron expressions are dynamically generated in `start.sh` based on `SCREENSHOT_INTERVAL`
- Only one screenshot file is kept: `latest.jpg` (or `latest.webp`)
- `index.html` is static — created once on first run, uses `Date.now()` for cache-busting
- Nginx cache headers prevent browser caching to ensure fresh screenshots
- The service waits `PAGE_LOAD_DELAY` seconds before capturing to allow page rendering
- Pillow converts PNG → JPEG with configurable quality (default 80)

## Docker Image Tags

- Releases: `v1.2.3`
- Latest: `latest`
- Branches: `main-abc123`

Multi-architecture: amd64 + arm64.

## Common Issues & Solutions

1. **Wrong timezone**: Set `TZ` environment variable in docker-compose.yml
2. **Page not fully loaded**: Increase `PAGE_LOAD_DELAY` value
3. **Cron not running**: Check cron logs via `docker-compose logs -f`
4. **Large screenshots**: Reduce `IMAGE_QUALITY` or switch `IMAGE_FORMAT` to `webp`