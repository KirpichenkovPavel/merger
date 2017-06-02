import os

DEBUG =True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'polyana_merger',
        'USER': 'polyana',
        'PASSWORD': 'p01yana',
        'HOST': 'localhost',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

MANAGEMENT_USER_NAME = "proxyadmin"
MANAGEMENT_USER_PASS = "Qwerty123"
#HYPOSTASIS_CACHE_TTL = 600

DEBUG_TRUE_LOG_LEVEL = "DEBUG"
