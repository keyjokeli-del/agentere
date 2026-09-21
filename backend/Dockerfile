# ==============================================================================
# STAGE 1: Build Dependencies in Virtual Environment
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies if needed, create lightweight venv
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# STAGE 2: Ultra-Lean Production Runtime (RAM Optimized for Free Tier)
# ==============================================================================
FROM python:3.11-slim AS runner

WORKDIR /app

# RAM optimization flags:
# - MALLOC_TRIM_THRESHOLD_=100000 forces glibc to return free memory pages to OS
# - PYTHONUNBUFFERED=1 ensures real-time log flushing to stdout
# - PYTHONDONTWRITEBYTECODE=1 avoids disk writes and startup overhead
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_TRIM_THRESHOLD_=100000 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Copy pre-built virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create unprivileged system user for security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Copy backend source code
COPY --chown=appuser:appgroup . /app

USER appuser

EXPOSE 8000

# Health check to ensure zero-downtime restarts without curl dependency
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + str(8000) + '/').read()"

# Single-worker uvicorn with bounded concurrency to guarantee < 150MB RAM footprint
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --limit-concurrency 100"]
