#!/bin/bash

# Valtronics Backup Script
# This script handles database and system backups

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="valtronics"
BACKUP_DIR="/backups/${PROJECT_NAME}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30
S3_BUCKET=""  # Set if using S3 backup

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_success "Dependencies check completed"
}

setup_backup_dir() {
    log_info "Setting up backup directory..."
    
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/configs"
    mkdir -p "$BACKUP_DIR/logs"
    
    log_success "Backup directory created: $BACKUP_DIR"
}

backup_database() {
    log_info "Backing up database..."
    
    local backup_file="$BACKUP_DIR/database/valtronics_db_$DATE.sql"
    
    # Create database backup
    docker-compose exec -T postgres pg_dump -U valtronics valtronics_db > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    log_success "Database backup completed: ${backup_file}.gz"
    
    # Upload to S3 if configured
    if [ ! -z "$S3_BUCKET" ]; then
        log_info "Uploading database backup to S3..."
        aws s3 cp "${backup_file}.gz" "s3://$S3_BUCKET/database/"
        log_success "Database backup uploaded to S3"
    fi
}

backup_configs() {
    log_info "Backing up configuration files..."
    
    local config_backup="$BACKUP_DIR/configs/configs_$DATE.tar.gz"
    
    # Backup configuration files
    tar -czf "$config_backup" \
        docker-compose.yml \
        .env.example \
        config/ \
        cloud/kubernetes/ \
        scripts/ \
        2>/dev/null || true
    
    log_success "Configuration backup completed: $config_backup"
    
    # Upload to S3 if configured
    if [ ! -z "$S3_BUCKET" ]; then
        log_info "Uploading config backup to S3..."
        aws s3 cp "$config_backup" "s3://$S3_BUCKET/configs/"
        log_success "Configuration backup uploaded to S3"
    fi
}

backup_logs() {
    log_info "Backing up logs..."
    
    local log_backup="$BACKUP_DIR/logs/logs_$DATE.tar.gz"
    
    # Create logs backup
    mkdir -p "/tmp/valtronics_logs"
    
    # Collect logs from all services
    docker-compose logs --no-color > "/tmp/valtronics_logs/docker-compose_$DATE.log" 2>/dev/null || true
    
    # Archive logs
    tar -czf "$log_backup" -C "/tmp" "valtronics_logs" 2>/dev/null || true
    
    # Cleanup temp directory
    rm -rf "/tmp/valtronics_logs"
    
    log_success "Logs backup completed: $log_backup"
    
    # Upload to S3 if configured
    if [ ! -z "$S3_BUCKET" ]; then
        log_info "Uploading logs backup to S3..."
        aws s3 cp "$log_backup" "s3://$S3_BUCKET/logs/"
        log_success "Logs backup uploaded to S3"
    fi
}

restore_database() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        exit 1
    fi
    
    log_info "Restoring database from: $backup_file"
    
    # Check if backup file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    # Stop services
    log_info "Stopping services..."
    docker-compose stop backend || true
    
    # Restore database
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -c "$backup_file" | docker-compose exec -T postgres psql -U valtronics -d valtronics_db
    else
        docker-compose exec -T postgres psql -U valtronics -d valtronics_db < "$backup_file"
    fi
    
    # Start services
    log_info "Starting services..."
    docker-compose start backend
    
    log_success "Database restore completed"
}

list_backups() {
    log_info "Listing available backups..."
    
    echo ""
    echo "Database Backups:"
    ls -la "$BACKUP_DIR/database/" 2>/dev/null || echo "No database backups found"
    
    echo ""
    echo "Configuration Backups:"
    ls -la "$BACKUP_DIR/configs/" 2>/dev/null || echo "No configuration backups found"
    
    echo ""
    echo "Log Backups:"
    ls -la "$BACKUP_DIR/logs/" 2>/dev/null || echo "No log backups found"
}

cleanup_old_backups() {
    log_info "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    # Clean up old database backups
    find "$BACKUP_DIR/database" -name "*.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Clean up old config backups
    find "$BACKUP_DIR/configs" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Clean up old log backups
    find "$BACKUP_DIR/logs" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Clean up S3 if configured
    if [ ! -z "$S3_BUCKET" ]; then
        log_info "Cleaning up old S3 backups..."
        aws s3 ls "s3://$S3_BUCKET/database/" | while read -r line; do
            createDate=$(echo $line | awk '{print $1" "$2}')
            createDate=$(date -d"$createDate" +%s)
            olderThan=$(date -d"$RETENTION_DAYS days ago" +%s)
            if [[ $createDate -lt $olderThan ]]; then
                fileName=$(echo $line | awk '{print $4}')
                if [[ $fileName != "" ]]; then
                    aws s3 rm "s3://$S3_BUCKET/database/$fileName"
                fi
            fi
        done
    fi
    
    log_success "Old backups cleaned up"
}

verify_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Backup file not specified"
        exit 1
    fi
    
    log_info "Verifying backup: $backup_file"
    
    # Check file exists and is not empty
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    if [ ! -s "$backup_file" ]; then
        log_error "Backup file is empty: $backup_file"
        exit 1
    fi
    
    # For database backups, check if it's valid SQL
    if [[ "$backup_file" == *.sql* ]]; then
        if [[ "$backup_file" == *.gz ]]; then
            if ! gunzip -t "$backup_file" 2>/dev/null; then
                log_error "Database backup is corrupted (invalid gzip)"
                exit 1
            fi
        fi
        
        log_success "Backup verification completed"
    else
        log_success "Backup file exists and is not empty"
    fi
}

show_help() {
    echo "Valtronics Backup Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  full               Create full backup (database, configs, logs)"
    echo "  database           Backup database only"
    echo "  configs            Backup configuration files only"
    echo "  logs               Backup logs only"
    echo "  restore <file>     Restore database from backup"
    echo "  list               List available backups"
    echo "  cleanup            Clean up old backups"
    echo "  verify <file>      Verify backup integrity"
    echo "  help               Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  S3_BUCKET          S3 bucket for cloud backups"
    echo "  RETENTION_DAYS     Number of days to keep backups (default: 30)"
    echo "  BACKUP_DIR         Local backup directory (default: /backups/valtronics)"
    echo ""
    echo "Examples:"
    echo "  $0 full"
    echo "  $0 database"
    echo "  $0 restore /backups/valtronics/database/valtronics_db_20240101_120000.sql.gz"
    echo "  $0 list"
}

# Main script logic
case "${1:-}" in
    "full")
        check_dependencies
        setup_backup_dir
        backup_database
        backup_configs
        backup_logs
        cleanup_old_backups
        log_success "Full backup completed successfully"
        ;;
    "database")
        check_dependencies
        setup_backup_dir
        backup_database
        log_success "Database backup completed"
        ;;
    "configs")
        check_dependencies
        setup_backup_dir
        backup_configs
        log_success "Configuration backup completed"
        ;;
    "logs")
        check_dependencies
        setup_backup_dir
        backup_logs
        log_success "Logs backup completed"
        ;;
    "restore")
        check_dependencies
        restore_database "$2"
        ;;
    "list")
        list_backups
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "verify")
        verify_backup "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        show_help
        exit 1
        ;;
esac
