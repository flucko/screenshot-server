# Screenshot Server for Legacy Devices

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
  screenshot-server
```

## How It Works

1. Takes a screenshot of the target URL at specified intervals
2. Serves the latest screenshot at `/latest.png`
3. Auto-refreshing HTML page displays the screenshot
4. Optimized for low-bandwidth and legacy browsers

## Files

- `latest.png` - Most recent screenshot
- `screenshot_YYYYMMDD_HHMMSS.png` - Timestamped screenshots
- `index.html` - Auto-refreshing viewer page

## Pushing to Docker Registry

### Docker Hub

```bash
# Build and tag the image
docker build -t screenshot-server .
docker tag screenshot-server:latest yourusername/screenshot-server:latest

# Login to Docker Hub
docker login

# Push the image
docker push yourusername/screenshot-server:latest
```

### Private Registry

```bash
# Tag for private registry
docker tag screenshot-server:latest your-registry.com/screenshot-server:latest

# Login to private registry
docker login your-registry.com

# Push the image
docker push your-registry.com/screenshot-server:latest
```

### AWS ECR

```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Create repository (if needed)
aws ecr create-repository --repository-name screenshot-server

# Tag and push
docker tag screenshot-server:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/screenshot-server:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/screenshot-server:latest
```

### Using from Registry

Update `docker-compose.yml` to use the registry image:

```yaml
services:
  screenshot-server:
    image: yourusername/screenshot-server:latest  # Instead of 'build: .'
    ports:
      - "8080:80"
    # ... rest of configuration
```