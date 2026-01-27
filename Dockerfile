FROM python:3.14-slim

LABEL maintainer="srijan"
LABEL description="Personal Risk Radar - Risk tracking and assessment system"

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

# Create directory for database persistence
RUN mkdir -p /data

# Expose ports for API and Streamlit
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run both FastAPI and Streamlit
CMD ["sh", "-c", "uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 & uv run streamlit run main.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"]
