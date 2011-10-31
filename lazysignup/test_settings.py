# Settings to be used when running unit tests
# python manage.py test --settings=lazysignup.test_settings lazysignup

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ''
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

INSTALLED_APPS = (
    # Put any other apps that your app depends on here
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'lazysignup',
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

# This merely needs to be present - as long as your test case specifies a
# urls attribute, it does not need to be populated.
ROOT_URLCONF = ''

LAZYSIGNUP_USER_MODEL = 'lazysignup.CustomUser'

# Internal setting to discover it test settings are used
LAZYSIGNUP_TEST_SETTINGS = True
