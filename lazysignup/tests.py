from django.http import HttpRequest
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase

import mock

from lazysignup.decorators import allow_lazy
from lazysignup.middleware import LazySignupMiddleware

def view(request):
    from django.http import HttpResponse
    r = HttpResponse()
    if request.user.is_authenticated():
        r.status_code = 500
    return r
    
def lazy_view(request):
    from django.http import HttpResponse
    r = HttpResponse()
    if request.user.has_usable_password() or request.user.is_anonymous():
        r.status_code = 500
    return r
lazy_view = allow_lazy(lazy_view)

class LazyTestCase(TestCase):

    urls = 'lazysignup.test_urls'
    
    def setUp(self):
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)
        self.m = LazySignupMiddleware()
    
    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testSessionAlreadyExists(self, mock_resolve):
        # If the user id is already in the session, this middleware should do nothing.
        f = allow_lazy(lambda: 1)
        self.request.session[SESSION_KEY] = 1
        mock_resolve.return_value = (f, None, None)
        
        self.m.process_request(self.request)
        self.failIf(hasattr(self.request, 'user'))
        
    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testCreateLazyUser(self, mock_resolve):
        # If there isn't a setup session, then this middleware should create a user
        # with the same name as the session key, and an unusable password.
        f = allow_lazy(lambda: 1)
        mock_resolve.return_value = (f, None, None)
        self.m.process_request(self.request)
        self.assertEqual(self.request.session.session_key[:30], self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())
        
    def testNormalView(self):
        # Calling our undecorated view should *not* create a user. If one is created, then the
        # view will set the status code to 500.
        response = self.client.get('/nolazy/')
        self.assertEqual(200, response.status_code)

    def testDecoratedView(self):
        # Calling our undecorated view should *not* create a user. If one is created, then the
        # view will set the status code to 500.
        response = self.client.get('/lazy/')
        self.assertEqual(200, response.status_code)
