#!/bin/bash
#
# 💾 Polymarket Hype Trading System - Database Backup Script
#
# Automated daily backups:
#   - Compress with gzip
#   - Keep last 7 days
#   - Verify integrity
#   - Optional: Upload to Google Drive
#
# Usage:
#   ./backup-database.sh
#
# Cron setup (daily at 3 AM):
#   0 3 * * * /path/to/backup-database.sh >> /path/to/logs/backup.log 2>&1
#
# Author: Wom + Borat AI

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"
DB_FILE="$WORKSPACE/polymarket_data.db"
BACKUP_DIR="$WORKSPACE/backups"
KEEP_DAYS=7

# Google Drive upload (optional)
GDRIVE_ENABLED=false
GDRIVE_FOLDER_ID=""  # Get from Google Drive folder URL

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    exit 1
}

# ============================================================================
# MAIN BACKUP PROCESS
# ============================================================================

log "🔄 Starting database backup..."

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    error "Database not found: $DB_FILE"
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_NAME="polymarket_data_${TIMESTAMP}.db"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
BACKUP_GZ="${BACKUP_PATH}.gz"

# Check database size
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
log "📊 Database size: $DB_SIZE"

# Copy database
log "📋 Copying database..."
cp "$DB_FILE" "$BACKUP_PATH"

# Verify copy
if [ ! -f "$BACKUP_PATH" ]; then
    error "Backup file not created"
fi

BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
log "✅ Backup created: $BACKUP_NAME ($BACKUP_SIZE)"

# Compress with gzip
log "🗜️  Compressing..."
gzip "$BACKUP_PATH"

if [ ! -f "$BACKUP_GZ" ]; then
    error "Compression failed"
fi

COMPRESSED_SIZE=$(du -h "$BACKUP_GZ" | cut -f1)
log "✅ Compressed: ${BACKUP_NAME}.gz ($COMPRESSED_SIZE)"

# Verify integrity
log "🔍 Verifying integrity..."
gunzip -t "$BACKUP_GZ"

if [ $? -eq 0 ]; then
    log "✅ Integrity check passed"
else
    error "Backup file is corrupted!"
fi

# Clean up old backups
log "🧹 Cleaning up old backups (keeping last $KEEP_DAYS days)..."
find "$BACKUP_DIR" -name "polymarket_data_*.db.gz" -type f -mtime +$KEEP_DAYS -delete

REMAINING=$(find "$BACKUP_DIR" -name "polymarket_data_*.db.gz" -type f | wc -l)
log "📦 Backups remaining: $REMAINING"

# Optional: Upload to Google Drive
if [ "$GDRIVE_ENABLED" = true ]; then
    if command -v gdrive &> /dev/null; then
        log "☁️  Uploading to Google Drive..."
        
        gdrive files upload --parent "$GDRIVE_FOLDER_ID" "$BACKUP_GZ" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            log "✅ Uploaded to Google Drive"
        else
            log "⚠️  Google Drive upload failed"
        fi
    else
        log "⚠️  gdrive CLI not installed, skipping upload"
    fi
fi

# Summary
TOTAL_BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
log "✅ Backup complete! Total backup size: $TOTAL_BACKUP_SIZE"

# Exit success
exit 0
