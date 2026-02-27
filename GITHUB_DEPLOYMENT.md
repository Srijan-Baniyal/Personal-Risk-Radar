# GitHub Container Registry Deployment

## Automated Builds

This repository is configured with GitHub Actions to automatically build and push Docker images to GitHub Container Registry (GHCR) on every push to the main branch.

## Image Location

The latest image is available at:
```
ghcr.io/srijan-baniyal/personal-risk-radar:latest
```

## Pulling the Image

The image is public and can be pulled by anyone:

```bash
docker pull ghcr.io/srijan-baniyal/personal-risk-radar:latest
```

## Running the Deployed Image

### Quick Start

```bash
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/personal_risk_radar.db:/app/personal_risk_radar.db \
  --name risk-radar \
  ghcr.io/srijan-baniyal/personal-risk-radar:latest
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  risk-radar:
    image: ghcr.io/srijan-baniyal/personal-risk-radar:latest
    container_name: personal-risk-radar
    ports:
      - "8000:8000"   # FastAPI
      - "8501:8501"   # Streamlit Dashboard
    volumes:
      - ./personal_risk_radar.db:/app/personal_risk_radar.db
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## Accessing the Application

After starting the container:

- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Available Image Tags

- `latest` - Latest build from main branch
- `main` - Main branch builds
- `develop` - Development branch builds
- `v*.*.*` - Version tags (when available)
- `main-<sha>` - Specific commit builds

## Verify the Deployment

Check the image is working:

```bash
# Pull the image
docker pull ghcr.io/srijan-baniyal/personal-risk-radar:latest

# Run it
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  --name risk-radar-test \
  ghcr.io/srijan-baniyal/personal-risk-radar:latest

# Check health
curl http://localhost:8000/health

# View logs
docker logs risk-radar-test

# Stop and remove
docker stop risk-radar-test && docker rm risk-radar-test
```

## Manual Push (Alternative)

If you need to push manually:

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u srijan-baniyal --password-stdin

# Build and tag
docker build -t ghcr.io/srijan-baniyal/personal-risk-radar:latest .

# Push
docker push ghcr.io/srijan-baniyal/personal-risk-radar:latest
```

You'll need a GitHub Personal Access Token with `write:packages` permission.
Create one at: https://github.com/settings/tokens/new?scopes=write:packages

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/docker-publish.yml`) automatically:

1. ✅ Builds the Docker image
2. ✅ Tags it appropriately (latest, branch name, commit SHA)
3. ✅ Pushes to GitHub Container Registry
4. ✅ Creates multi-platform builds (amd64, arm64)
5. ✅ Generates build attestations for security

## Monitoring Builds

Check the build status:
- Go to the [Actions tab](https://github.com/Srijan-Baniyal/Personal-Risk-Radar/actions)
- Look for the "Build and Push Docker Image" workflow
- View logs for any build failures

## Package Visibility

To make the package public (so anyone can pull without authentication):

1. Go to https://github.com/users/Srijan-Baniyal/packages/container/personal-risk-radar/settings
2. Scroll to "Danger Zone"
3. Click "Change visibility"
4. Select "Public"
