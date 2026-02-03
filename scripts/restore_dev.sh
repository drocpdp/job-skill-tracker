#!/usr/bin/env bash
set -e

DB_NAME="jobskills_dev"
SERVICE_DB="db"

if [ -z "$1" ]; then
  echo "❌ Usage: ./scripts/restore_dev.sh backups/filename.dump"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ File not found: $BACKUP_FILE"
  exit 1
fi

echo "⚠️  This will OVERWRITE database '$DB_NAME'"
read -p "Type 'restore' to continue: " CONFIRM

if [ "$CONFIRM" != "restore" ]; then
  echo "❌ Restore cancelled"
  exit 1
fi

echo "♻️  Restoring from $BACKUP_FILE..."

cat "$BACKUP_FILE" | docker compose exec -T "$SERVICE_DB" pg_restore \
  -U postgres \
  -d "$DB_NAME" \
  --clean \
  --if-exists

echo "✅ Restore complete"

echo "🔄 Ensuring schema is at latest revision..."
docker compose exec api alembic upgrade head

echo "✅ Database restored and migrated"
