
FROM python:3.12-slim

WORKDIR /app/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 \
PYTHONPATH=/app

# uv setup
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /bin/uv

# Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen --compile-bytecode --no-cache

# Copy application code
COPY . .


