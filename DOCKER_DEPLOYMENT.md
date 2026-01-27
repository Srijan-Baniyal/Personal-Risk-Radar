# 🐳 Docker Deployment Guide

## Quick Start

### Prerequisites

- Docker (20.10+)
- Docker Compose (v2.0+)

### Build and Run

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or using Docker directly
docker build -t personal-risk-radar .
docker run -d \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/personal_risk_radar.db:/app/personal_risk_radar.db \
  --name risk-radar \
  personal-risk-radar
```

### Access the Application

- **Dashboard (Streamlit)**: http://localhost:8501
- **API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Load example data
docker-compose exec risk-radar uv run python scripts/load_examples.py

# Execute commands inside container
docker-compose exec risk-radar bash
```

## Data Persistence

The SQLite database is mounted as a volume to persist data:

- Host: `./personal_risk_radar.db`
- Container: `/app/personal_risk_radar.db`

## Environment Variables

You can customize behavior via environment variables in `docker-compose.yml`:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - DATABASE_PATH=/app/personal_risk_radar.db
  # Add more as needed
```

## Production Considerations

For production deployment, consider:

1. **Add reverse proxy** (nginx/traefik) for HTTPS
2. **Add authentication** to Streamlit
3. **Use multi-stage builds** to reduce image size
4. **Switch to PostgreSQL** for multi-user support
5. **Add monitoring** (Prometheus/Grafana)
6. **Implement backup strategy** for database

## Troubleshooting

### Container won't start

```bash
docker-compose logs risk-radar
```

### Database permission issues

```bash
chmod 666 personal_risk_radar.db
```

### Port already in use

Change ports in `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"
  - "8502:8501"
```

## Deployment Platforms

This Docker setup works with:

- **AWS**: ECS, EC2, Lightsail
- **Google Cloud**: Cloud Run, GKE, Compute Engine
- **Azure**: Container Instances, AKS
- **DigitalOcean**: App Platform, Droplets
- **Heroku**: Container Registry
- **Railway/Render**: Direct Docker support

## Skills Demonstrated

✅ Multi-service containerization  
✅ Volume management for data persistence  
✅ Port exposure and networking  
✅ Docker Compose orchestration  
✅ Health checks  
✅ Build optimization (.dockerignore)  
✅ Environment configuration  
