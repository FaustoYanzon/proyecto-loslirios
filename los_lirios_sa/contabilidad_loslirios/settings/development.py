from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database para desarrollo (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuraciones adicionales para desarrollo
INTERNAL_IPS = ['127.0.0.1']

# if DEBUG:
#     INSTALLED_APPS += ['debug_toolbar']
#     MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Configuraciones de cache para desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Sobrescribir logging para desarrollo (solo console)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'contabilidad_loslirios': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

print("🔧 Usando configuración de DESARROLLO")