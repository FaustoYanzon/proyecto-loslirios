#!/bin/bash
# filepath: c:\Users\Usuario\Desktop\Proyeco Los Lirios\los_lirios_sa\deploy.sh

echo "🚀 Iniciando deployment de Los Lirios SA..."

# Configurar entorno de producción
export DJANGO_ENV=production

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate --noinput

# Recopilar archivos estáticos
python manage.py collectstatic --noinput --clear

# Crear directorios necesarios
mkdir -p logs
mkdir -p media

# Configurar permisos
chmod +x manage.py

# Configurar grupos y permisos
python manage.py setup_groups

echo "✅ Deployment completado!"
echo "📝 No olvides:"
echo "   - Configurar variables de entorno en .env"
echo "   - Configurar base de datos PostgreSQL"
echo "   - Configurar servidor web (Nginx/Apache)"
echo "   - Configurar certificados SSL"