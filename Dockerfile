# ── Base image ──────────────────────────────────────────────
FROM python:3.11-slim

# ── Metadata labels ─────────────────────────────────────────
LABEL maintainer="College DevOps Lab"
LABEL description="College Event Management System"
LABEL version="1.0"

# ── Working directory ────────────────────────────────────────
WORKDIR /app

# ── Install dependencies first (layer cache optimisation) ───
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ──────────────────────────────────
COPY app.py .
COPY templates/ templates/
COPY static/    static/
COPY test_app.py .

# ── Ensure data directory exists (volume mount point) ───────
RUN mkdir -p /app/data

# ── Environment defaults (override at runtime) ────────────────
ENV FLASK_DEBUG=false
ENV ADMIN_PASSWORD=admin123
ENV FLASK_SECRET_KEY=change-me-in-production
ENV DATABASE_PATH=/app/data/college_events.db

# ── Expose Flask port ────────────────────────────────────────
EXPOSE 5000

# ── Health-check ─────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# ── Start application ────────────────────────────────────────
CMD ["python", "app.py"]
