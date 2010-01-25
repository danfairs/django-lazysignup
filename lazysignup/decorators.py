
from lazysignup.middleware import ALLOW_LAZY_REGISTRY

class allow_lazy(object):
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            args += self.args
            kwargs.update(self.kwargs)
            return func(*args, **kwargs)
        ALLOW_LAZY_REGISTRY[wrapped_func] = True
        return wrapped_func
