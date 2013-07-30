from django.conf import settings

LAZY_USER_DEFAULT_EMAIL = getattr(settings, 'LAZY_USER_DEFAULT_EMAIL', '')