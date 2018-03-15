import re
from django.conf import settings

LAZYSIGNUP_USER_MODEL = getattr(settings, 'LAZYSIGNUP_USER_MODEL', settings.AUTH_USER_MODEL)
LAZYSIGNUP_USER_NAME_FIELD = getattr(settings, 'LAZYSIGNUP_USER_NAME_FIELD', 'username')
LAZYSIGNUP_CUSTOM_USER_CREATION_FORM = getattr(
    settings,
    'LAZYSIGNUP_CUSTOM_USER_CREATION_FORM',
    None
)


DEFAULT_BLACKLIST = (
    'slurp',
    'googlebot',
    'yandex',
    'msnbot',
    'baiduspider',
)
USER_AGENT_BLACKLIST = []

for user_agent in getattr(settings, 'LAZYSIGNUP_USER_AGENT_BLACKLIST', DEFAULT_BLACKLIST):
    USER_AGENT_BLACKLIST.append(re.compile(user_agent, re.I))
