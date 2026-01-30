#!/usr/bin/env bash
set -euo pipefail

RUN_MIGRATIONS="${RUN_MIGRATIONS:-0}"
START_SERVER="${START_SERVER:-1}"

cd /app

if [[ "${RUN_MIGRATIONS}" == "1" ]]; then
  echo "Running migrations (alembic upgrade head)..."
  if [[ -f /app/alembic.ini ]]; then
    alembic -c /app/alembic.ini upgrade head
  elif [[ -f /app/backend/alembic.ini ]]; then
    alembic -c /app/backend/alembic.ini upgrade head
  else
    echo "ERROR: Could not find alembic.ini"
    exit 1
  fi
fi

if [[ "${START_SERVER}" == "1" ]]; then
  echo "Starting API..."
  exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
else
  echo "START_SERVER=0 (not starting API). Done."
fi
