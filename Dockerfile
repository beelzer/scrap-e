# Multi-stage build for optimal size
FROM python:3.13-slim AS builder

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies
RUN uv pip install --system --no-cache .

# Runtime stage
FROM python:3.13-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    # For web scraping
    chromium \
    chromium-driver \
    firefox-esr \
    # For file processing
    libxml2 \
    libxslt1.1 \
    # For database connections
    libpq5 \
    # Utils
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && playwright install chromium firefox webkit \
    && playwright install-deps

# Create non-root user
RUN useradd -m -u 1000 scraper && \
    mkdir -p /app /data && \
    chown -R scraper:scraper /app /data

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=scraper:scraper . .

USER scraper

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/home/scraper/.cache/ms-playwright

VOLUME ["/data"]

ENTRYPOINT ["python", "-m", "scrap_e.cli"]
