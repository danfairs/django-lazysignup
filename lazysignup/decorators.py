from lazysignup.middleware import ALLOW_LAZY_REGISTRY

def allow_lazy_user(func):
    ALLOW_LAZY_REGISTRY[func] = True
    return func