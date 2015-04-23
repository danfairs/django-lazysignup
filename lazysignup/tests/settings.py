import os

test_db = os.environ.get('DB', None)

if test_db == 'sqlite' or test_db is None:
    # Default is SQLite
    db_config = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lazysignup',
    }
elif test_db == 'postgres':
    db_config = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'lazysignup',
    }
elif test_db == 'local-postgres':
    db_config = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lazysignup',
        'USER': 'lazysignup',
        'PASSWORD': 'lazysignup',
        'HOST': 'localhost'
    }
elif test_db == 'mysql':
    db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'travis',
        'NAME': 'lazysignup',
    }
elif test_db == 'local-mysql':
    db_config = {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'lazysignup',
        'NAME': 'lazysignup',
        'PASSWORD': 'lazysignup',
    }
else:
    raise RuntimeError('Unsupported test DB {0}'.format(test_db))

DATABASES = {
    'default': db_config
}

INSTALLED_APPS = (
    'lazysignup',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
)

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "lazysignup.backends.LazySignupBackend",
)

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    "templates",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)


LAZYSIGNUP_USER_AGENT_BLACKLIST = [
    "^search",
]

LAZYSIGNUP_USER_MODEL = 'auth.User'
AUTH_USER_MODEL = 'auth.User'

ROOT_URLCONF = 'lazysignup.tests.urls'
SECRET_KEY = 'non-empty-key'
DEBUG = True

STATIC_URL = '/static/'
ALLOWED_HOSTS = [
    'testserver'
]
