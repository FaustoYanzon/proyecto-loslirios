from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts permitidos - CONFIGURAR SEGÚN TU DOMINIO
ALLOWED_HOSTS = [
    'tu-dominio.com',
    'www.tu-dominio.com',
    'loslirios.herokuapp.com',  # Si usas Heroku
    '127.0.0.1',
    'localhost',
]

# Base de datos para producción (PostgreSQL recomendado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'loslirios_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Configuraciones de seguridad para producción
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de archivos estáticos para producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Email configuration para producción
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@loslirios.com')

# Configuraciones de cache para producción
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# Logging para producción
LOGGING['handlers']['file']['filename'] = '/var/log/loslirios/django.log'

# Admins para notificaciones de errores
ADMINS = [
    ('Admin', os.environ.get('ADMIN_EMAIL', 'admin@loslirios.com')),
]

MANAGERS = ADMINS

print("🚀 Usando configuración de PRODUCCIÓN")