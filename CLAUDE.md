# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a containerized web screenshot service designed to capture and serve screenshots of web pages for display on legacy devices. It uses headless Chromium to render pages and serves them via Nginx.

## Architecture

The service runs multiple processes managed by Supervisord:
1. **screenshot-init**: One-time process that captures initial screenshot on startup
2. **screenshot-cron**: Manages cron daemon for periodic screenshots based on `SCREENSHOT_INTERVAL`
3. **nginx**: Serves screenshots and auto-refreshing HTML viewer

Key flow: `start.sh` → sets timezone → configures cron → runs `screenshot.py` periodically → saves to `/var/www/html/`

## Build Commands

```bash
# Build Ubuntu-based image (default)
docker build -t screenshot-server .

# Build Alpine variant (smaller size)
docker build -f Dockerfile.alpine -t screenshot-server:alpine .

# Run with docker-compose (Ubuntu-based)
docker-compose up -d

# Run Alpine version
docker-compose -f docker-compose.alpine.yml up -d
```

## Testing & Development

```bash
# View logs
docker-compose logs -f

# Check if screenshot is being served
curl http://localhost:8080/latest.png

# Verify cron job
docker exec <container-id> crontab -l

# Debug supervisor processes
docker exec <container-id> supervisorctl status
```

## Important Configuration Details

- Cron expressions are dynamically generated in `start.sh` based on `SCREENSHOT_INTERVAL`
- Screenshots are saved with both fixed name (`latest.png`) and timestamp
- Nginx cache headers prevent browser caching to ensure fresh screenshots
- The service waits `PAGE_LOAD_DELAY` seconds before capturing to allow page rendering

## Docker Image Strategy

Two optimized variants are built automatically:
- **Ubuntu-based** (default): Better compatibility, standard Python environment
- **Alpine-based**: Smaller image size, sufficient for most deployments

**Tags generated:**
- Releases: `v1.2.3`, `v1.2.3-alpine`
- Latest: `latest` (Ubuntu), `alpine` (Alpine)  
- Branches: `main-abc123`, `main-abc123-alpine`

Uses matrix strategy for parallel builds across amd64/arm64 architectures.

## Common Issues & Solutions

1. **Excessive screenshots**: Ensure supervisord.conf has `autorestart=false` for screenshot-init
2. **Wrong timezone**: Set `TZ` environment variable in docker-compose.yml
3. **Page not fully loaded**: Increase `PAGE_LOAD_DELAY` value
4. **Cron not running**: Check `exec cron -f` is used in start.sh (foreground mode)

## Memories

- Remember the release tags for future pushes