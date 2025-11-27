#!/bin/bash
# Script de deployment para Los Lirios SA

set -e  # Salir si hay error

echo "🚀 Iniciando deployment de Los Lirios SA..."

# === VARIABLES ===
PROJECT_NAME="los_lirios_sa"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="/var/backups/los_lirios"
NGINX_SITES="/etc/nginx/sites-available"
SYSTEMD_DIR="/etc/systemd/system"

# === FUNCIÓN DE LOGGING ===
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# === CREAR DIRECTORIOS ===
log "📁 Creando directorios necesarios..."
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p /var/log/gunicorn
sudo mkdir -p /var/log/nginx

# === BACKUP DE BASE DE DATOS ===
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    log "💾 Creando backup de base de datos..."
    sudo cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
fi

# === ACTUALIZAR CÓDIGO ===
log "📥 Actualizando código..."
if [ -d "$PROJECT_DIR/.git" ]; then
    cd $PROJECT_DIR
    sudo git pull origin main
else
    sudo git clone https://github.com/tu-usuario/los-lirios-sa.git $PROJECT_DIR
    cd $PROJECT_DIR
fi

# === CONFIGURAR ENTORNO VIRTUAL ===
log "🐍 Configurando entorno virtual Python..."
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv $VENV_DIR
fi

sudo $VENV_DIR/bin/pip install --upgrade pip
sudo $VENV_DIR/bin/pip install -r requirements.txt

# === CONFIGURAR VARIABLES DE ENTORNO ===
log "🔐 Configurando variables de entorno..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    sudo cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    log "⚠️  ATENCIÓN: Configura las variables en $PROJECT_DIR/.env"
fi

# === EJECUTAR MIGRACIONES ===
log "🗃️  Ejecutando migraciones de Django..."
sudo $VENV_DIR/bin/python manage.py collectstatic --noinput
sudo $VENV_DIR/bin/python manage.py migrate

# === CREAR SUPERUSUARIO ===
log "👤 Verificando superusuario..."
sudo $VENV_DIR/bin/python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@losliriossa.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
EOF

# === OPTIMIZAR BASE DE DATOS ===
log "⚡ Optimizando base de datos..."
sudo $VENV_DIR/bin/python manage.py optimize_db --full-optimization

# === CONFIGURAR GUNICORN SERVICE ===
log "🔧 Configurando servicio Gunicorn..."
sudo tee $SYSTEMD_DIR/gunicorn-los-lirios.service > /dev/null << EOF
[Unit]
Description=Gunicorn daemon for Los Lirios SA
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py los_lirios_sa.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

# === CONFIGURAR NGINX ===
log "🌐 Configurando Nginx..."
sudo cp nginx.conf $NGINX_SITES/los-lirios
sudo ln -sf $NGINX_SITES/los-lirios /etc/nginx/sites-enabled/
sudo nginx -t

# === CONFIGURAR PERMISOS ===
log "🔒 Configurando permisos..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 644 $PROJECT_DIR/staticfiles

# === REINICIAR SERVICIOS ===
log "🔄 Reiniciando servicios..."
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-los-lirios
sudo systemctl restart gunicorn-los-lirios
sudo systemctl reload nginx

# === VERIFICAR ESTADO ===
log "✅ Verificando estado de servicios..."
sudo systemctl status gunicorn-los-lirios --no-pager
sudo systemctl status nginx --no-pager

# === CONFIGURAR SSL (Let's Encrypt) ===
log "🔐 Configurando SSL..."
if command -v certbot &> /dev/null; then
    sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com --non-interactive --agree-tos --email admin@yourdomain.com
else
    log "⚠️  Certbot no encontrado. Instala Let's Encrypt para SSL automático"
fi

log "🎉 ¡Deployment completado exitosamente!"
log "📱 Aplicación disponible en: https://yourdomain.com"
log "🔧 Panel admin: https://yourdomain.com/admin/"
log "📊 Logs: /var/log/gunicorn/ y /var/log/nginx/"