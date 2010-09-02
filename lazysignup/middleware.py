import hashlib
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import authenticate
from django.contrib.auth import get_user
from django.contrib.auth import login
from django.contrib.auth.models import User

ALLOW_LAZY_REGISTRY = {}
USER_AGENT_BLACKLIST = []

def username_from_session(session_key, username_length=None):
    if not username_length:
        username_length = User._meta.get_field('username').max_length
    return hashlib.sha1(session_key).hexdigest()[:username_length]


class LazySignupMiddleware(object):
    
    def process_request(self, request):
        assert hasattr(request, 'session'), "You need to have the session app installed"
        
        # If the user agent is one we ignore, bail early
        request_user_agent = request.META.get('HTTP_USER_AGENT', '')
        for user_agent in USER_AGENT_BLACKLIST:
            if user_agent.search(request_user_agent):
                return
        
        # Mimic what django.core.base.BaseHandler does to resolve the request URL to a
        # callable
        from django.core import urlresolvers

        # Get urlconf from request object, if available.  Otherwise use default.
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
        try:
            try:
                callback, callback_args, callback_kwargs = resolver.resolve(
                        request.path_info)
            except SystemExit:
                raise
            except:
                # Meh, something went wrong in user code. Don't handle it here, 
                # it'll be handled later.
                return
        finally:
            # Reset URLconf for this thread on the way out for complete
            # isolation of request.urlconf. Only try this if the method
            # exists (which is the case for Django > 1.2)
            if hasattr(urlresolvers, 'set_urlconf'):
                urlresolvers.set_urlconf(None)
            
        # See if this view has been registered as one to skip user creation
        if not ALLOW_LAZY_REGISTRY.has_key(callback):
            return 
        
        # If there's already a key in the session for a valid user, then we don't 
        # need to do anything. If the user isn't valid, then get_user will return
        # an anonymous user.
        if not get_user(request).is_anonymous():
            return
            
        # If not, then we have to create a user, and log them in. Set the user id
        # in the session here to prevent the login call cycling the session key.
        username = self.get_username(request.session.session_key)

        User.objects.create_user(username, '')
        request.user = None
        user = authenticate(username=username)
        assert user, "Lazy user creation and authentication failed. Have you got lazysignup.backends.LazySignupBackend in AUTHENTICATION_BACKENDS?"
        request.session[SESSION_KEY] = user.id
        login(request, user)

    def get_username(self, session_key, username_length=None):
        return username_from_session(session_key, username_length)
        