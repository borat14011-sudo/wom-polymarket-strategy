# 💾 Polymarket Hype Trading System - Database Backup Script (Windows)
#
# Automated daily backups:
#   - Compress with built-in compression
#   - Keep last 7 days
#   - Verify integrity
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File backup-database.ps1
#
# Task Scheduler setup (daily at 3 AM):
#   See DEPLOYMENT-GUIDE.md for instructions
#
# Author: Wom + Borat AI

# ============================================================================
# CONFIGURATION
# ============================================================================

$WORKSPACE = Split-Path -Parent $MyInvocation.MyCommand.Path
$DB_FILE = Join-Path $WORKSPACE "polymarket_data.db"
$BACKUP_DIR = Join-Path $WORKSPACE "backups"
$KEEP_DAYS = 7

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

function Write-Error-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Error "[$Timestamp] ERROR: $Message"
    exit 1
}

# ============================================================================
# MAIN BACKUP PROCESS
# ============================================================================

Write-Log "🔄 Starting database backup..."

# Check if database exists
if (-Not (Test-Path $DB_FILE)) {
    Write-Error-Log "Database not found: $DB_FILE"
}

# Create backup directory
if (-Not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Generate backup filename with timestamp
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BACKUP_NAME = "polymarket_data_${Timestamp}.db"
$BACKUP_PATH = Join-Path $BACKUP_DIR $BACKUP_NAME
$BACKUP_ZIP = "${BACKUP_PATH}.zip"

# Check database size
$DB_SIZE = (Get-Item $DB_FILE).Length / 1MB
Write-Log "📊 Database size: $([math]::Round($DB_SIZE, 2)) MB"

# Copy database
Write-Log "📋 Copying database..."
Copy-Item $DB_FILE $BACKUP_PATH

# Verify copy
if (-Not (Test-Path $BACKUP_PATH)) {
    Write-Error-Log "Backup file not created"
}

$BACKUP_SIZE = (Get-Item $BACKUP_PATH).Length / 1MB
Write-Log "✅ Backup created: $BACKUP_NAME ($([math]::Round($BACKUP_SIZE, 2)) MB)"

# Compress with built-in Windows compression
Write-Log "🗜️  Compressing..."
Compress-Archive -Path $BACKUP_PATH -DestinationPath $BACKUP_ZIP -Force

if (-Not (Test-Path $BACKUP_ZIP)) {
    Write-Error-Log "Compression failed"
}

# Remove uncompressed backup
Remove-Item $BACKUP_PATH

$COMPRESSED_SIZE = (Get-Item $BACKUP_ZIP).Length / 1MB
Write-Log "✅ Compressed: ${BACKUP_NAME}.zip ($([math]::Round($COMPRESSED_SIZE, 2)) MB)"

# Verify integrity (test extraction)
Write-Log "🔍 Verifying integrity..."
try {
    $TestPath = Join-Path $BACKUP_DIR "test_extract"
    Expand-Archive -Path $BACKUP_ZIP -DestinationPath $TestPath -Force
    
    if (Test-Path (Join-Path $TestPath $BACKUP_NAME)) {
        Write-Log "✅ Integrity check passed"
        Remove-Item -Path $TestPath -Recurse -Force
    } else {
        Write-Error-Log "Backup file is corrupted!"
    }
} catch {
    Write-Error-Log "Integrity check failed: $_"
}

# Clean up old backups
Write-Log "🧹 Cleaning up old backups (keeping last $KEEP_DAYS days)..."
$CutoffDate = (Get-Date).AddDays(-$KEEP_DAYS)
Get-ChildItem -Path $BACKUP_DIR -Filter "polymarket_data_*.zip" | 
    Where-Object { $_.LastWriteTime -lt $CutoffDate } | 
    Remove-Item -Force

$Remaining = (Get-ChildItem -Path $BACKUP_DIR -Filter "polymarket_data_*.zip").Count
Write-Log "📦 Backups remaining: $Remaining"

# Summary
$TotalSize = (Get-ChildItem -Path $BACKUP_DIR -Filter "*.zip" | 
              Measure-Object -Property Length -Sum).Sum / 1MB
Write-Log "✅ Backup complete! Total backup size: $([math]::Round($TotalSize, 2)) MB"

exit 0
