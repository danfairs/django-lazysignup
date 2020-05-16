from functools import wraps

from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import authenticate
from django.contrib.auth import get_user
from django.contrib.auth import login
from django.shortcuts import redirect
from functools import WRAPPER_ASSIGNMENTS

from lazysignup.constants import USER_AGENT_BLACKLIST
from lazysignup.utils import is_lazy_user

ALLOW_LAZY_REGISTRY = {}


def allow_lazy_user(func):
    def wrapped(request, *args, **kwargs):
        assert hasattr(request, 'session'), ("You need to have the session "
                                             "app installed")
        if getattr(settings, 'LAZYSIGNUP_ENABLE', True):
            # If the user agent is one we ignore, bail early
            ignore = False
            request_user_agent = request.META.get('HTTP_USER_AGENT', '')
            for user_agent in USER_AGENT_BLACKLIST:
                if user_agent.search(request_user_agent):
                    ignore = True
                    break

            # If there's already a key in the session for a valid user, then
            # we don't need to do anything. If the user isn't valid, then
            # get_user will return an anonymous user
            if get_user(request).is_anonymous and not ignore:
                # If not, then we have to create a user, and log them in.
                from lazysignup.models import LazyUser
                user, username = LazyUser.objects.create_lazy_user()
                request.user = None
                user = authenticate(username=username)
                assert user, ("Lazy user creation and authentication "
                              "failed. Have you got "
                              "lazysignup.backends.LazySignupBackend in "
                              "AUTHENTICATION_BACKENDS?")
                # Set the user id in the session here to prevent the login
                # call cycling the session key.
                request.session[SESSION_KEY] = user.id
                login(request, user)
        return func(request, *args, **kwargs)

    return wraps(func)(wrapped)


def require_lazy_user(*redirect_args, **redirect_kwargs):
    def decorator(func):
        @wraps(func, assigned=WRAPPER_ASSIGNMENTS)
        def inner(request, *args, **kwargs):
            if is_lazy_user(request.user):
                return func(request, *args, **kwargs)
            else:
                return redirect(*redirect_args, **redirect_kwargs)
        return inner
    return decorator


def require_nonlazy_user(*redirect_args, **redirect_kwargs):
    def decorator(func):
        @wraps(func, assigned=WRAPPER_ASSIGNMENTS)
        def inner(request, *args, **kwargs):
            if not is_lazy_user(request.user):
                return func(request, *args, **kwargs)
            else:
                return redirect(*redirect_args, **redirect_kwargs)
        return inner
    return decorator
