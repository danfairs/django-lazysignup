import os

DB_CONFIGS = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lazysignup',
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'NAME': 'lazysignup',
    },
    'local-postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lazysignup',
        'USER': 'lazysignup',
        'PASSWORD': 'lazysignup',
        'HOST': 'localhost'
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'travis',
        'NAME': 'lazysignup',
    },
    'local-mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'lazysignup',
        'NAME': 'lazysignup',
        'PASSWORD': 'lazysignup',
    }
}

test_db = os.environ.get('DB', 'sqlite')
try:
    db_config = DB_CONFIGS[test_db]
except KeyError:
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

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.i18n",
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                "django.template.context_processors.tz",
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
