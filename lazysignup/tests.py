from django.http import HttpRequest
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase

from lazysignup.middleware import LazySignupMiddleware

class ManagerTestCase(TestCase):

    urls = 'lazysignup.test_urls'
    
    def setUp(self):
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)
        self.m = LazySignupMiddleware()
    
    def testSessionAlreadyExists(self):
        # If the user id is already in the session, this middleware should do nothing.
        self.request.session[SESSION_KEY] = 1
        self.m.process_request(self.request)
        self.failIf(hasattr(self.request, 'user'))
        
    def testCreateLazyUser(self):
        # If there isn't a setup session, then this middleware should create a user
        # with the same name as the session key, and an unusable password.
        self.m.process_request(self.request)
        self.assertEqual(self.request.session.session_key[:30], self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())
        
