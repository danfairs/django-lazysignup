import hashlib


def username_from_session(session_key, username_length=None,
    username_field='username'):
    """ Return the username based on the provided session key. """
    from lazysignup.models import LazyUser
    user_class = LazyUser.get_user_class()
    if not username_length:
        username_length = user_class._meta.get_field(
            username_field).max_length
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
