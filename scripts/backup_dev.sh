#!/usr/bin/env bash
set -e

DB_NAME="jobskills_dev"
SERVICE_DB="db"
BACKUP_DIR="backups"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

echo "📦 Backing up database '$DB_NAME'..."
docker compose exec -T "$SERVICE_DB" pg_dump \
  -U postgres \
  -d "$DB_NAME" \
  -Fc > "$BACKUP_FILE"

echo "✅ Backup created:"
echo "   $BACKUP_FILE"
