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
    'custom_user_tests',
    'lazysignup',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
)

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "lazysignup.backends.LazySignupBackend",
)

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

LAZYSIGNUP_USER_AGENT_BLACKLIST = [
    "^search",
]
LAZYSIGNUP_CUSTOM_USER_CREATION_FORM = 'custom_user_tests.forms.GoodUserCreationForm'
AUTH_USER_MODEL = 'custom_user_tests.CustomUser'

ROOT_URLCONF = 'lazysignup.tests.urls'
SECRET_KEY = 'non-empty-key'
DEBUG = False
