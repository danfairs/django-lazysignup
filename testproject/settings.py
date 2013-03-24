# Settings to be used when running unit tests
# python manage.py test lazysignup

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

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

ROOT_URLCONF = 'testproject.urls'
SECRET_KEY = 'non-empty-key'

SECRET_KEY = '12345'

LAZYSIGNUP_USER_MODEL = 'lazysignup.CustomUser'
