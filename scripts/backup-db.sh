#!/bin/bash
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
docker compose exec -T db pg_dump -U bookflix bookflix > "$BACKUP_DIR/bookflix_$TIMESTAMP.sql"
echo "Backup saved to $BACKUP_DIR/bookflix_$TIMESTAMP.sql"
