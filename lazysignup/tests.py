import datetime
from functools import wraps

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.contrib.auth import SESSION_KEY
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.test import TestCase

import mock

from lazysignup.decorators import allow_lazy_user
from lazysignup.middleware import LazySignupMiddleware
from lazysignup.management.commands import remove_expired_users

class GoodUserCreationForm(UserCreationForm):
    """ Hardcoded credentials to demonstrate that the get_credentials method
    is being used
    """
    def get_credentials(self):
        return {
            'username': 'demo',
            'password': 'demo',
        }

    def save(self, commit=True):
        instance = super(GoodUserCreationForm, self).save(commit=False)
        creds = self.get_credentials()
        instance.username = creds['username']
        instance.set_password(creds['password'])
        if commit:
            instance.save()
        return instance


def view(request):
    from django.http import HttpResponse
    r = HttpResponse()
    if request.user.is_authenticated():
        r.status_code = 500
    return r
    
def lazy_view(request):
    from django.http import HttpResponse
    r = HttpResponse()
    if request.user.is_anonymous() or  request.user.has_usable_password():
        r.status_code = 500
    return r
lazy_view = allow_lazy_user(lazy_view)

def no_lazysignup(func):
    def wrapped(*args, **kwargs):
        old = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = tuple(
                [m for m in settings.MIDDLEWARE_CLASSES 
                if m != 'lazysignup.middleware.LazySignupMiddleware']
            )
        try:
            result = func(*args, **kwargs)
        finally:
            settings.MIDDLEWARE_CLASSES = old
        return result
    return wraps(func)(wrapped)
        

class LazyTestCase(TestCase):

    urls = 'lazysignup.test_urls'
    
    def setUp(self):
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)
        self.m = LazySignupMiddleware()
    
    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testSessionAlreadyExists(self, mock_resolve):
        # If the user id is already in the session, this middleware should do nothing.
        f = allow_lazy_user(lambda: 1)
        user = User.objects.create_user('test', 'test@test.com', 'test')
        self.request.user = AnonymousUser()
        login(self.request, authenticate(username='test', password='test'))
        mock_resolve.return_value = (f, None, None)
        
        self.m.process_request(self.request)
        self.assertEqual(user, self.request.user)

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testBadSessionAlreadyExists(self, mock_resolve):
        # If the user id is already in the session, but the user doesn't exist,
        # then a user should be created
        f = allow_lazy_user(lambda: 1)
        self.request.session[SESSION_KEY] = 1000
        mock_resolve.return_value = (f, None, None)
        
        self.m.process_request(self.request)
        self.assertEqual(self.m.get_username(self.request.session.session_key), self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())
        
    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testCreateLazyUser(self, mock_resolve):
        # If there isn't a setup session, then this middleware should create a user
        # with the same name as the session key, and an unusable password.
        f = allow_lazy_user(lambda: 1)
        mock_resolve.return_value = (f, None, None)
        self.m.process_request(self.request)
        self.assertEqual(self.m.get_username(self.request.session.session_key), self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())
        
    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testBannedUserAgents(self, mock_resolve):
        # If the client's user agent matches a regex in the banned
        # list, then a user shouldn't be created.
        self.request.META['HTTP_USER_AGENT'] = 'search engine'
        f = allow_lazy_user(lambda: 1)
        mock_resolve.return_value = (f, None, None)
        self.m.process_request(self.request)
        self.failIf(hasattr(self.request, 'user'))
        self.assertEqual(0, len(User.objects.all()))
        
    def testNormalView(self):
        # Calling our undecorated view should *not* create a user. If one is created, then the
        # view will set the status code to 500.
        response = self.client.get('/nolazy/')
        self.assertEqual(200, response.status_code)

    def testDecoratedView(self):
        # Calling our undecorated view should create a user. If one is created, then the
        # view will set the status code to 500.
        self.assertEqual(0, len(User.objects.all()))
        response = self.client.get('/lazy/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(User.objects.all()))
        
    def testRemoteExpiredUsers(self):
        # Users wihout usable passwords who don't have a current session record should be removed.
        u1 = User.objects.create_user('dummy', '')
        u2 = User.objects.create_user('dummy2', '')
        s = Session(
            session_key='dummy',
            session_data='',
            expire_date=datetime.datetime.now() + datetime.timedelta(1)
        )
        s.save()
        
        c = remove_expired_users.Command()
        c.handle()
        
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertEqual(u1, users[0])
        
    def testConvertAjax(self):
        # Calling convert with an AJAX request should result in a 200
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertEqual('demo', users[0].username)

        # We should find that the auth backend used is no longer the 
        # Lazy backend, as the conversion should have logged the new 
        # user in.
        self.assertNotEqual('lazysignup.backends.LazySignupBackend', self.client.session['_auth_user_backend'])
        
    def testConvertNonAjax(self):
        # If it's a regular web browser, we should get a 301.
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(302, response.status_code)
        
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertEqual('demo', users[0].username)

    def testConvertMismatchedPasswordsAjax(self):
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'passwordx',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)
        self.failIf(response.content.find('password') == -1)
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertNotEqual('demo', users[0].username)

    def testUserExistsAjax(self):
        User.objects.create_user('demo', '', 'foo')
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)
        self.failIf(response.content.find('username') == -1)
        
    def testConvertMismatchedNoAjax(self):
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'passwordx',
        })
        self.assertEqual(200, response.status_code)
        self.failIf(response.content.find('password') == -1)
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertNotEqual('demo', users[0].username)

    def testUserExistsNoAjax(self):
        User.objects.create_user('demo', '', 'foo')
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(200, response.status_code)
        self.failIf(response.content.find('username') == -1)

    def testConvertExistingUserAjax(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.client.login(username='dummy', password='dummy')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)

    def testConvertExistingUserNoAjax(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.client.login(username='dummy', password='dummy')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(302, response.status_code)

    def testGetConvert(self):
        self.client.get('/lazy/')
        response = self.client.get('/convert/')
        self.assertEqual(200, response.status_code)
        
    @no_lazysignup
    def testConvertAnon(self):
        # If the Convert view gets an anonymous user, it should redirect
        # to the login page. Not much else it can do!
        response = self.client.get('/convert/')
        self.assertEqual(302, response.status_code)
        self.assertEqual('http://testserver' + settings.LOGIN_URL, response['location'])
        
    def testConversionKeepsSameUser(self):
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(1, len(User.objects.all()))
        
    @no_lazysignup
    def testNoLazysignupDecorator(self):
        response = self.client.get('/lazy/')
        self.assertEqual(500, response.status_code)
        
    def testBadCustomConvertForm(self):
        # Passing a form class to the conversion view that doesn't have
        # a get_credentials method should raise an AttributeError
        self.assertRaises(AttributeError, self.client.post, reverse('test_bad_convert'), {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        
    def testGoodCustomConvertForm(self):
        self.client.get('/lazy/')
        response = self.client.post(reverse('test_good_convert'), {
            'username': 'foo',
            'password1': 'password',
            'password2': 'password',
        })
        users = User.objects.all()
        self.assertEqual(1, len(users))
        
        # The credentials returned by get_credentials should have been used
        self.assertEqual(users[0], authenticate(username='demo', password='demo'))
        
        
        
    