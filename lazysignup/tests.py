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
from django.views.decorators.http import require_POST

import mock

from lazysignup.backends import LazySignupBackend
from lazysignup.decorators import allow_lazy_user
from lazysignup.exceptions import NotLazyError
from lazysignup.management.commands import remove_expired_users
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user, username_from_session

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

_missing = object()
def no_lazysignup(func):
    def wrapped(*args, **kwargs):
        if hasattr(settings, 'LAZYSIGNUP_ENABLE'):
            old = settings.LAZYSIGNUP_ENABLE
        else:
            old = _missing
        settings.LAZYSIGNUP_ENABLE = False
        try:
            result = func(*args, **kwargs)
        finally:
            if old is _missing:
                delattr(settings, 'LAZYSIGNUP_ENABLE')
            else:
                settings.LAZYSIGNUP_ENABLE = old
        return result
    return wraps(func)(wrapped)


class LazyTestCase(TestCase):

    urls = 'lazysignup.test_urls'

    def setUp(self):
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testSessionAlreadyExists(self, mock_resolve):
        # If the user id is already in the session, this decorator should do nothing.
        f = allow_lazy_user(lambda request: 1)
        user = User.objects.create_user('test', 'test@test.com', 'test')
        self.request.user = AnonymousUser()
        login(self.request, authenticate(username='test', password='test'))
        mock_resolve.return_value = (f, None, None)

        f(self.request)
        self.assertEqual(user, self.request.user)

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testBadSessionAlreadyExists(self, mock_resolve):
        # If the user id is already in the session, but the user doesn't exist,
        # then a user should be created
        f = allow_lazy_user(lambda request: 1)
        self.request.session[SESSION_KEY] = 1000
        mock_resolve.return_value = (f, None, None)

        f(self.request)
        self.assertEqual(username_from_session(self.request.session.session_key), self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testCreateLazyUser(self, mock_resolve):
        # If there isn't a setup session, then this middleware should create a user
        # with the same name as the session key, and an unusable password.
        f = allow_lazy_user(lambda request: 1)
        mock_resolve.return_value = (f, None, None)
        f(self.request)
        self.assertEqual(username_from_session(self.request.session.session_key), self.request.user.username)
        self.assertEqual(False, self.request.user.has_usable_password())

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def testBannedUserAgents(self, mock_resolve):
        # If the client's user agent matches a regex in the banned
        # list, then a user shouldn't be created.
        self.request.META['HTTP_USER_AGENT'] = 'search engine'
        f = allow_lazy_user(lambda request: 1)
        mock_resolve.return_value = (f, None, None)

        f(self.request)
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

    def testRemoveExpiredUsers(self):
        # Users wihout usable passwords who don't have a current session record should be removed.
        u1 = User.objects.create_user(username_from_session('dummy'), '')
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
        user = users[0]

        # The credentials returned by get_credentials should have been used
        self.assertEqual(user, authenticate(username='demo', password='demo'))

        # The user should no longer be lazy
        self.assertFalse(is_lazy_user(user))

    def testUsernameNotBasedOnSessionKey(self):
        # The generated username should not look like the session key. While doing
        # so isn't a security problem in itself, any client software that blindly
        # displays the logged-in user's username risks showing most of the session
        # key to the world.
        fake_session_key = 'a' * 32
        username = username_from_session(fake_session_key)
        self.failIf(fake_session_key.startswith(username))

    def testDecoratorOrder(self):
        # It used to be the case that allow_lazy_user had to be first in the
        # decorator list. This is no longer the case.
        self.request.user = AnonymousUser()
        self.request.method = 'POST'
        v = require_POST(lazy_view)

        response = v(self.request)
        self.assertEqual(200, response.status_code)

    def testIsLazyUserAnonymous(self):
        user = AnonymousUser()
        self.assertEqual(False, is_lazy_user(user))

    def testIsLazyUserModelBackend(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.assertEqual(False, is_lazy_user(user))

    def testIsLazyUserModelUnusablePassword(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com')
        self.assertEqual(False, is_lazy_user(user))

    def testIsLazyUserLazy(self):
        self.request.user = AnonymousUser()
        response = lazy_view(self.request)
        self.assertEqual(True, is_lazy_user(self.request.user))

    def testLazyUserNotLoggedIn(self):
        # Check that the is_lazy_user works for users who were created
        # lazily but are not the current logged-in user
        user = LazyUser.objects.create_lazy_user('foo')
        self.assertTrue(is_lazy_user(user))

    def testAnonymousNotLazy(self):
        # Anonymous users are not lazy
        self.assertFalse(is_lazy_user(AnonymousUser()))

    def testBackendGetUserAnnotates(self):
        # Check that the lazysignup backend annotates the user object
        # with the backend, mirroring what Django's does
        lazy_view(self.request)
        backend = LazySignupBackend()
        pk = User.objects.all()[0].pk
        self.assertEqual('lazysignup.backends.LazySignupBackend', backend.get_user(pk).backend)

    def testConvertGood(self):
        # Check that the convert() method on the lazy user manager
        # correctly converts the lazy user
        user = LazyUser.objects.create_lazy_user('foo')
        d = {
            'username': 'test',
            'password1': 'password',
            'password2': 'password',
        }
        form = GoodUserCreationForm(d, instance=user)
        self.assertTrue(form.is_valid())

        user = LazyUser.objects.convert(form)
        self.assertFalse(is_lazy_user(user))

    def testConvertNonLazy(self):
        # Attempting to convert a non-lazy user should raise a TypeError
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        form = GoodUserCreationForm(instance=user)
        self.assertRaises(NotLazyError, LazyUser.objects.convert, form)



