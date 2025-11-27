# Configuración específica para testing
from .settings import *

# === CONFIGURACIÓN DE BASE DE DATOS PARA TESTS ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de datos en memoria para velocidad
    }
}

# === CONFIGURACIÓN DE CACHE PARA TESTS ===
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# === CONFIGURACIÓN DE PASSWORD HASHERS (MÁS RÁPIDO) ===
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Más rápido para tests
]

# === DESHABILITAR LOGGING DURANTE TESTS ===
LOGGING_CONFIG = None

# === DESHABILITAR MIGRACIONES PARA VELOCIDAD ===
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# === EMAIL BACKEND PARA TESTS ===
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# === CONFIGURACIÓN DE MEDIA PARA TESTS ===
MEDIA_ROOT = '/tmp/los_lirios_test_media'