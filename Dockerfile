# ═════════════════════════════════════════════════════════════════════════════
#  ESPPA — Production Dockerfile
#  Build:  docker build -t esppa .
#  Run:    docker run -e DJANGO_SETTINGS_MODULE=core.settings.prod -p 8000:8000 esppa
# ═════════════════════════════════════════════════════════════════════════════

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings.prod

WORKDIR /app

# ── System dependencies ─────────────────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ─────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ────────────────────────────────────────────────────────
COPY . .

# ── Static files ────────────────────────────────────────────────────────────
WORKDIR /app/src
RUN python manage.py collectstatic --noinput
WORKDIR /app

# ── Health check ────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/') or exit(1)"

EXPOSE 8000

# ── Run gunicorn from src/ ──────────────────────────────────────────────────
WORKDIR /app/src
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

