import hashlib
from django.contrib.auth.models import User

def username_from_session(session_key, username_length=None):
    if not username_length:
        username_length = User._meta.get_field('username').max_length
    return hashlib.sha1(session_key).hexdigest()[:username_length]

def is_lazy_user(user):
    backend = getattr(user, 'backend', None)
    if backend == 'lazysignup.backends.LazySignupBackend':
        return True
    return False
