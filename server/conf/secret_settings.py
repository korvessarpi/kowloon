SECRET_KEY = "sefsefiwwj3 dasfe59af_35afgsdhjlqw whewiu hwejfpoiwjrpw09&afeewfe"

# Database configuration for SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/server/evennia.db3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Disable migrations for SQLite in production
MIGRATION_MODULES = {}

# Time zone
TIME_ZONE = 'UTC'
USE_TZ = True
