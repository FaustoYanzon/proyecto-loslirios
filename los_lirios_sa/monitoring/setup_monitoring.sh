#!/bin/bash
# Configurar monitoreo automático

# === CREAR CRONTABS ===
(crontab -l 2>/dev/null; cat << EOF
# Los Lirios SA - Monitoreo y Backup

# Health check cada 5 minutos
*/5 * * * * /var/www/los_lirios_sa/monitoring/health_check.py

# Backup diario a las 2 AM
0 2 * * * /var/www/los_lirios_sa/monitoring/backup.sh

# Optimización de DB semanal (domingos 3 AM)
0 3 * * 0 /var/www/los_lirios_sa/venv/bin/python /var/www/los_lirios_sa/manage.py optimize_db --full-optimization

# Limpiar logs antiguos mensualmente
0 1 1 * * find /var/log -name "*.log" -type f -mtime +90 -delete

# Reiniciar servicios semanalmente (domingo 4 AM)
0 4 * * 0 systemctl restart gunicorn-los-lirios
EOF
) | crontab -

echo "✅ Crontabs configurados para monitoreo automático"