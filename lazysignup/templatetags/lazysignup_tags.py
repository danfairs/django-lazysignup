from django.template import Library
from lazysignup.models import LazyUser
register = Library()

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
    return bool(LazyUser.objects.filter(user=user).count() > 0)

is_lazy_user = register.filter(is_lazy_user)