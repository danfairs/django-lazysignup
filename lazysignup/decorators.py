from lazysignup.middleware import ALLOW_LAZY_REGISTRY

def allow_lazy(func):
    ALLOW_LAZY_REGISTRY[func] = True
    return func