import hashlib
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import get_model

def username_from_session(session_key, username_length=None):
    if not username_length:
        username_length = User._meta.get_field('username').max_length
    return hashlib.sha1(session_key).hexdigest()[:username_length]

def is_lazy_user(user):
    """ Return True if the passed user is a lazy user. """
    # Anonymous users are not lazy.
    if user.is_anonymous():
        return False

    # Check the user backend. If the lazy signup backend
    # authenticated them, then the user is lazy.
    backend = getattr(user, 'backend', None)
    if backend == 'lazysignup.backends.LazySignupBackend':
        return True

    # Otherwise, we have to fall back to checking the database.
    from lazysignup.models import LazyUser
    return bool(LazyUser.objects.filter(user=user).count() > 0)

def get_user_class():
    """ Try loading an alternate user class according to an optional
    setting (USER_MODEL).
    If one isn't provided, or is misconfigured, return the default one.
    """
    try:
        user_class = get_model(*settings.USER_MODEL.split('.', 2))
    except AttributeError:
        user_class = None

    if not user_class:
        user_class = User

    return user_class
