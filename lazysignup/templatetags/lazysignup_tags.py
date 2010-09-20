from django.template import Library

register = Library()

def is_lazy_user(user):
    backend = getattr(user, 'backend', None)
    if backend == 'lazysignup.backends.LazySignupBackend':
        return True
    return False
is_lazy_user = register.filter(is_lazy_user)