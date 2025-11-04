#!/bin/bash
# backup.sh - Backup script for Freqtrade data
# Backs up configuration, strategies, and trading database

BACKUP_DIR="$HOME/freqtrade_backups"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "========================================="
echo "FREQTRADE BACKUP"
echo "========================================="
echo "Date: $(date)"
echo "Project directory: $PROJECT_DIR"
echo "Backup directory: $BACKUP_DIR"
echo ""

# Create backup archive
echo "Creating backup archive..."
cd "$PROJECT_DIR"
tar -czf "$BACKUP_DIR/freqtrade_backup_$DATE.tar.gz" \
    --exclude='user_data/data' \
    --exclude='user_data/backtest_results' \
    --exclude='user_data/hyperopt_results' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='*.log' \
    config.json \
    .env \
    user_data/strategies/ \
    user_data/models/ \
    user_data/notebooks/ \
    user_data/*.sqlite 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Backup created successfully"
    echo "  File: $BACKUP_DIR/freqtrade_backup_$DATE.tar.gz"
    echo "  Size: $(du -h "$BACKUP_DIR/freqtrade_backup_$DATE.tar.gz" | cut -f1)"
else
    echo "✗ Backup failed"
    exit 1
fi

# Remove backups older than 30 days
echo ""
echo "Cleaning old backups (>30 days)..."
find "$BACKUP_DIR" -name "freqtrade_backup_*.tar.gz" -mtime +30 -delete
echo "✓ Old backups removed"

# Display backup statistics
echo ""
echo "Backup Statistics:"
echo "  Total backups: $(ls -1 "$BACKUP_DIR"/freqtrade_backup_*.tar.gz 2>/dev/null | wc -l)"
echo "  Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo "  Latest backup: freqtrade_backup_$DATE.tar.gz"
echo ""
echo "========================================="
echo "BACKUP COMPLETE"
echo "========================================="
