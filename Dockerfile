# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2 + healthchecks
RUN apt-get update \
 && apt-get install -y --no-install-recommends bash gcc libpq-dev curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better caching)
COPY backend/requirements*.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# Copy app + migrations (adjust if your alembic files live elsewhere)
COPY backend /app/backend
COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic /app/alembic

# Entrypoint
RUN chmod +x /app/backend/entrypoint.sh

EXPOSE 8000
CMD ["/app/backend/entrypoint.sh"]
