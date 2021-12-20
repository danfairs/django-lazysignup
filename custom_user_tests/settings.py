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
    raise RuntimeError(f'Unsupported test DB {test_db}')

DATABASES = {
    'default': db_config
}

INSTALLED_APPS = (
    'custom_user_tests',
    'lazysignup',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
	'django.contrib.admin',
)

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "lazysignup.backends.LazySignupBackend",
)

MIDDLEWARE = [
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
