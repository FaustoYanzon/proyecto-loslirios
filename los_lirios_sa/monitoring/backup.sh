#!/bin/bash
# Script de backup automático para Los Lirios SA

set -e

# === VARIABLES ===
PROJECT_DIR="/var/www/los_lirios_sa"
BACKUP_DIR="/var/backups/los_lirios"
S3_BUCKET="los-lirios-backups"  # Opcional: bucket S3 para backups remotos
RETENTION_DAYS=30

# === FUNCIÓN DE LOGGING ===
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# === CREAR DIRECTORIO DE BACKUP ===
mkdir -p $BACKUP_DIR

# === BACKUP DE BASE DE DATOS ===
backup_database() {
    log "💾 Iniciando backup de base de datos..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"
    
    if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
        cp "$PROJECT_DIR/db.sqlite3" "$DB_BACKUP"
        gzip "$DB_BACKUP"
        log "✅ Backup de DB creado: ${DB_BACKUP}.gz"
    else
        log "⚠️  Base de datos no encontrada en $PROJECT_DIR/db.sqlite3"
    fi
}

# === BACKUP DE ARCHIVOS MEDIA ===
backup_media() {
    log "📁 Iniciando backup de archivos media..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    MEDIA_BACKUP="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"
    
    if [ -d "$PROJECT_DIR/media" ]; then
        tar -czf "$MEDIA_BACKUP" -C "$PROJECT_DIR" media/
        log "✅ Backup de media creado: $MEDIA_BACKUP"
    else
        log "⚠️  Directorio media no encontrado"
    fi
}

# === BACKUP DE CONFIGURACIÓN ===
backup_config() {
    log "⚙️  Iniciando backup de configuración..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    CONFIG_BACKUP="$BACKUP_DIR/config_backup_$TIMESTAMP.tar.gz"
    
    tar -czf "$CONFIG_BACKUP" -C "$PROJECT_DIR" \
        .env \
        gunicorn.conf.py \
        nginx.conf \
        --exclude='*.pyc' \
        --exclude='__pycache__'
    
    log "✅ Backup de configuración creado: $CONFIG_BACKUP"
}

# === BACKUP DE LOGS ===
backup_logs() {
    log "📄 Iniciando backup de logs..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    LOGS_BACKUP="$BACKUP_DIR/logs_backup_$TIMESTAMP.tar.gz"
    
    tar -czf "$LOGS_BACKUP" \
        /var/log/gunicorn/ \
        /var/log/nginx/ \
        "$PROJECT_DIR/logs/" 2>/dev/null || true
    
    log "✅ Backup de logs creado: $LOGS_BACKUP"
}

# === LIMPIAR BACKUPS ANTIGUOS ===
cleanup_old_backups() {
    log "🗑️  Limpiando backups antiguos (>$RETENTION_DAYS días)..."
    
    find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete
    
    log "✅ Limpieza completada"
}

# === SUBIR A S3 (OPCIONAL) ===
upload_to_s3() {
    if command -v aws &> /dev/null && [ ! -z "$S3_BUCKET" ]; then
        log "☁️  Subiendo backups a S3..."
        
        aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/backups/ \
            --exclude "*" \
            --include "*.gz" \
            --delete
        
        log "✅ Backups subidos a S3"
    else
        log "⚠️  AWS CLI no configurado o S3_BUCKET no definido"
    fi
}

# === VERIFICAR INTEGRIDAD ===
verify_backups() {
    log "🔍 Verificando integridad de backups..."
    
    for backup_file in $BACKUP_DIR/*.gz; do
        if [ -f "$backup_file" ]; then
            if gzip -t "$backup_file" 2>/dev/null; then
                log "✅ $backup_file - OK"
            else
                log "❌ $backup_file - CORRUPTO"
            fi
        fi
    done
}

# === FUNCIÓN PRINCIPAL ===
main() {
    log "🚀 Iniciando proceso de backup de Los Lirios SA"
    
    backup_database
    backup_media
    backup_config
    backup_logs
    verify_backups
    cleanup_old_backups
    upload_to_s3
    
    log "🎉 Proceso de backup completado"
}

# === EJECUCIÓN ===
main 2>&1 | tee -a /var/log/los_lirios/backup.log