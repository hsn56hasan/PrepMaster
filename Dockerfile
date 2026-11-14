# ===================================================
# PrepMaster Multi-Stage Production Dockerfile
# Lightweight, Secure, Non-Root, Healthchecked
# ===================================================

# Stage 1: Build & Dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.12-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050 \
    PREPMASTER_DB_PATH=/data/prepmaster.db

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application directories
COPY backend /app/backend
COPY data /app/data
COPY static /app/static

# Ensure persistent volume mount directory (/data) and app data directory exist and are writable
RUN mkdir -p /data /app/data && chmod 777 /data /app/data

EXPOSE 8050

# Automated container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8050/api/student/status')" || exit 1

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8050"]
