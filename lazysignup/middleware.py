from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User

USERNAME_LENGTH = 30

class LazySignupMiddleware(object):
    
    def process_request(self, request):
        assert hasattr(request, 'session'), "You need to have the session app installed"
        
        # If there's already a key in the session for the user, then we don't 
        # need to do anything
        if request.session.has_key(SESSION_KEY):
            return
            
        # If not, then we have to create a user, and log them in. Set the user id
        # in the session here to prevent the login call cycling the session key.
        username = request.session.session_key[:USERNAME_LENGTH]
        User.objects.create_user(username, '')
        request.user = None
        user = authenticate(username=username)
        assert user, "Lazy user creation and authentication failed. Have you got lazysignup.backends.LazySignupBackend in AUTHENTICATION_BACKENDS?"
        request.session[SESSION_KEY] = user.id
        login(request, user)

            
        