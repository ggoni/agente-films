# Use Python base image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy application code first
COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install --no-cache \
        google-adk>=0.1.0 \
        fastapi>=0.115.0 \
        uvicorn[standard]>=0.32.0 \
        pydantic>=2.9.0 \
        pydantic-settings>=2.6.0 \
        litellm>=1.50.0 \
        httpx>=0.27.0 \
        python-multipart>=0.0.12 \
        sqlalchemy>=2.0.44 \
        psycopg2-binary>=2.9.11 \
        wikipedia>=1.4.0 \
        alembic>=1.13.0

# Create non-root user and set ownership
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
