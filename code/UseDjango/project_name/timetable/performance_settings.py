"""
Performance Optimization Settings for Timetable Application

Add these settings to your settings.py file for improved performance.
"""

# ==============================================================================
# CACHING CONFIGURATION
# ==============================================================================

# Use Redis for production (recommended) or database/filesystem for development
# Uncomment the configuration that matches your environment

# Option 1: Redis Cache (Recommended for Production)
# Requires: pip install django-redis
"""
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'timetable',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}
"""

# Option 2: Database Cache (Development)
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'timetable_cache_table',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Run: python manage.py createcachetable
"""

# Option 3: Local Memory Cache (Simple Development)
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'timetable-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
"""

# ==============================================================================
# DATABASE OPTIMIZATION
# ==============================================================================

# Connection Pooling
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'OPTIONS': {
            'timeout': 20,
        }
    }
}
"""

# ==============================================================================
# MIDDLEWARE OPTIMIZATION
# ==============================================================================

# Enable GZip compression for responses
"""
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',  # Add this at the top
    'django.middleware.security.SecurityMiddleware',
    # ... rest of middleware
]
"""

# ==============================================================================
# TEMPLATE OPTIMIZATION
# ==============================================================================

# Cache template loaders in production
"""
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                # ... context processors
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]
"""

# ==============================================================================
# SESSION OPTIMIZATION
# ==============================================================================

# Use cached sessions for better performance
"""
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
"""

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Log slow queries for optimization
"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
"""

# ==============================================================================
# STATIC FILES OPTIMIZATION
# ==============================================================================

# Enable whitenoise for static file serving (Production)
# pip install whitenoise
"""
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add after SecurityMiddleware
    # ... rest of middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
"""

# ==============================================================================
# PAGINATION DEFAULTS
# ==============================================================================

# Default pagination size
"""
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
"""

# ==============================================================================
# QUERY OPTIMIZATION
# ==============================================================================

# Prevent N+1 queries in development
"""
# In development, log warnings for N+1 queries
if DEBUG:
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'DEBUG',
            }
        }
    }
"""

# ==============================================================================
# SECURITY & PERFORMANCE HEADERS
# ==============================================================================

"""
# Add in production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Enable HTTPS-only cookies in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
"""
