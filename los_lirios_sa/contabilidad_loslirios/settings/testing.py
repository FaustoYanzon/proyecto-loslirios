from .base import *

# Testing configuration
DEBUG = False
TESTING = True

# Base de datos en memoria para tests rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Desactivar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email backend para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Password hashers más rápidos para testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar logging en tests
LOGGING_CONFIG = None

print("🧪 Usando configuración de TESTING")