import datetime
import hashlib
from functools import wraps

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.auth import authenticate
from django.contrib.auth import get_user
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.auth.models import UserManager
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from django.views.decorators.http import require_POST

import mock

from lazysignup.backends import LazySignupBackend
from lazysignup.decorators import (allow_lazy_user, require_lazy_user,
    require_nonlazy_user)
from lazysignup.exceptions import NotLazyError
from lazysignup.management.commands import remove_expired_users
from lazysignup.models import LazyUser
from lazysignup.utils import is_lazy_user
from lazysignup.signals import converted

_missing = object()


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
    r = HttpResponse()
    if request.user.is_authenticated():
        r.status_code = 500
    return r


@allow_lazy_user
def lazy_view(request):
    r = HttpResponse()
    if request.user.is_anonymous() or request.user.has_usable_password():
        r.status_code = 500
    return r


@require_lazy_user("view-for-nonlazy-users")
def requires_lazy_view(request):
    return HttpResponse()


@require_nonlazy_user("view-for-lazy-users")
def requires_nonlazy_view(request):
    return HttpResponse()


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


class CustomUser(User):
    objects = UserManager()
    my_custom_field = models.CharField(max_length=50, blank=True, null=True)
    custom_username = models.CharField(max_length=35)


class LazyTestCase(TestCase):

    def setUp(self):
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)

        # We have to save the session to cause a session key to be generated.
        self.request.session.save()

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def test_session_already_exists(self, mock_resolve):
        # If the user id is already in the session, this decorator should do
        # nothing.
        f = allow_lazy_user(lambda request: 1)
        user = User.objects.create_user('test', 'test@test.com', 'test')
        self.request.user = AnonymousUser()
        login(self.request, authenticate(username='test', password='test'))
        mock_resolve.return_value = (f, None, None)

        f(self.request)
        self.assertEqual(user, self.request.user)

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def test_bad_session_already_exists(self, mock_resolve):
        # If the user id is already in the session, but the user doesn't
        # exist, then a user should be created
        f = allow_lazy_user(lambda request: 1)
        self.request.session[SESSION_KEY] = 1000
        mock_resolve.return_value = (f, None, None)

        f(self.request)
        self.failIf(self.request.user.username is None)
        self.assertEqual(False, self.request.user.has_usable_password())

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def test_create_lazy_user(self, mock_resolve):
        # If there isn't a setup session, then this middleware should create a
        # user with a random username and an unusable password.
        f = allow_lazy_user(lambda request: 1)
        mock_resolve.return_value = (f, None, None)
        f(self.request)
        self.failIf(self.request.user.username is None)
        self.assertEqual(False, self.request.user.has_usable_password())

    @mock.patch('django.core.urlresolvers.RegexURLResolver.resolve')
    def test_banned_user_agents(self, mock_resolve):
        # If the client's user agent matches a regex in the banned
        # list, then a user shouldn't be created.
        self.request.META['HTTP_USER_AGENT'] = 'search engine'
        f = allow_lazy_user(lambda request: 1)
        mock_resolve.return_value = (f, None, None)

        f(self.request)
        self.failIf(hasattr(self.request, 'user'))
        self.assertEqual(0, len(User.objects.all()))

    def test_normal_view(self):
        # Calling our undecorated view should *not* create a user. If one is
        # created, then the view will set the status code to 500.
        response = self.client.get('/nolazy/')
        self.assertEqual(200, response.status_code)

    def test_decorated_view(self):
        # Calling our undecorated view should create a user. If one is
        # created, then the view will set the status code to 500.
        self.assertEqual(0, len(User.objects.all()))
        response = self.client.get('/lazy/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(User.objects.all()))

    def test_remove_expired_users_uses_lazy_model(self):
        # remove_expired_users used to be hardcoded to look for an unusable
        # password and the Django user model. Make sure that it actually
        # uses the LazyUser mechanism.
        User.objects.create_user('dummy2', '')
        user, _ = LazyUser.objects.create_lazy_user()
        user.last_login = datetime.datetime(1972, 1, 1)
        user.save()
        c = remove_expired_users.Command()
        c.handle()
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertEqual('dummy2', users[0].username)

    def test_remove_expired_users_session_cookie_age(self):
        # The remove_expired_users should look at SESSION_COOKIE_AGE to figure
        # out whether to delete users. It will delete users who have not
        # logged in since datetime.datetime.now - SESSION_COOKIE_AGE.
        user1, _ = LazyUser.objects.create_lazy_user()
        user2, _ = LazyUser.objects.create_lazy_user()
        user1.last_login = datetime.datetime(1972, 1, 1)
        user1.save()
        c = remove_expired_users.Command()
        c.handle()
        users = User.objects.all()
        self.assertEqual(1, len(users))
        self.assertEqual(user2.username, users[0].username)

    def test_convert_ajax(self):
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
        self.assertNotEqual('lazysignup.backends.LazySignupBackend',
            self.client.session[BACKEND_SESSION_KEY])

    def test_convert_custom_template(self):
        # Check a custom template is used, if specified.
        response = self.client.get('/custom_convert/')
        self.assertEqual(['lazysignup/done.html'],
            [t.name for t in response.templates])

    def test_convert_ajax_custom_template(self):
        # If a custom ajax template is provided, then it should be used when
        # rendering an ajax GET of the convert view. (Usually, this would be
        # a 'chromeless' version of the regular template)
        response = self.client.get('/custom_convert_ajax/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(['lazysignup/done.html'],
            [t.name for t in response.templates])

    def test_convert_non_ajax(self):
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

    def test_convert_mismatched_passwords_ajax(self):
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

    def test_user_exists_ajax(self):
        User.objects.create_user('demo', '', 'foo')
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)
        self.failIf(response.content.find('username') == -1)

    def test_convert_mismatched_no_ajax(self):
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

    def test_user_exists_no_ajax(self):
        User.objects.create_user('demo', '', 'foo')
        self.client.get('/lazy/')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(200, response.status_code)
        self.failIf(response.content.find('username') == -1)

    def test_convert_existing_user_ajax(self):
        User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.client.login(username='dummy', password='dummy')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, response.status_code)

    def test_convert_existing_user_no_ajax(self):
        User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.client.login(username='dummy', password='dummy')
        response = self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(302, response.status_code)

    def test_get_convert(self):
        self.client.get('/lazy/')
        response = self.client.get('/convert/')
        self.assertEqual(200, response.status_code)

    def test_get_convert_via_ajax(self):
        # Load convert.html via AJAX
        self.client.get('/lazy/')
        response = self.client.get(reverse('lazysignup_convert'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)

    @no_lazysignup
    def test_convert_anon(self):
        # If the Convert view gets an anonymous user, it should redirect
        # to the login page. Not much else it can do!
        response = self.client.get('/convert/')
        self.assertEqual(302, response.status_code)
        self.assertEqual('http://testserver' + settings.LOGIN_URL,
            response['location'])

    def test_conversion_keeps_same_user(self):
        self.client.get('/lazy/')
        self.client.post('/convert/', {
            'username': 'demo',
            'password1': 'password',
            'password2': 'password',
        })
        self.assertEqual(1, len(User.objects.all()))

    @no_lazysignup
    def test_no_lazysignup_decorator(self):
        response = self.client.get('/lazy/')
        self.assertEqual(500, response.status_code)

    def test_bad_custom_convert_form(self):
        # Passing a form class to the conversion view that doesn't have
        # a get_credentials method should raise an AttributeError
        self.assertRaises(AttributeError, self.client.post,
            reverse('test_bad_convert'), {
                'username': 'demo',
                'password1': 'password',
                'password2': 'password',
            })

    def test_good_custom_convert_form(self):
        self.client.get('/lazy/')
        self.client.post(reverse('test_good_convert'), {
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

    def test_username_not_based_on_session_key(self):
        # The generated username should not look like the session key. While
        # doing so isn't a security problem in itself, any client software
        # that blindly displays the logged-in user's username risks showing
        # most of the session key to the world.
        session_key = self.request.session.session_key
        assert session_key
        user, username = LazyUser.objects.create_lazy_user()
        self.failIf(session_key.startswith(username))

    def test_decorator_order(self):
        # It used to be the case that allow_lazy_user had to be first in the
        # decorator list. This is no longer the case.
        self.request.user = AnonymousUser()
        self.request.method = 'POST'
        v = require_POST(lazy_view)

        response = v(self.request)
        self.assertEqual(200, response.status_code)

    def test_is_lazy_user_anonymous(self):
        user = AnonymousUser()
        self.assertEqual(False, is_lazy_user(user))

    def test_is_lazy_user_model_backend(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        self.assertEqual(False, is_lazy_user(user))

    def test_is_lazy_user_unusable_password(self):
        user = User.objects.create_user('dummy', 'dummy@dummy.com')
        self.assertEqual(False, is_lazy_user(user))

    def test_is_lazy_user_lazy(self):
        self.request.user = AnonymousUser()
        lazy_view(self.request)
        self.assertEqual(True, is_lazy_user(self.request.user))

    def test_lazy_user_not_logged_in(self):
        # Check that the is_lazy_user works for users who were created
        # lazily but are not the current logged-in user
        user, username = LazyUser.objects.create_lazy_user()
        self.assertTrue(is_lazy_user(user))

    def test_anonymous_not_lazy(self):
        # Anonymous users are not lazy
        self.assertFalse(is_lazy_user(AnonymousUser()))

    def test_backend_get_user_annotates(self):
        # Check that the lazysignup backend annotates the user object
        # with the backend, mirroring what Django's does
        lazy_view(self.request)
        backend = LazySignupBackend()
        pk = User.objects.all()[0].pk
        self.assertEqual('lazysignup.backends.LazySignupBackend',
            backend.get_user(pk).backend)

    def test_bad_session_user_id(self):
        self.request.session[SESSION_KEY] = 1000
        self.request.session[BACKEND_SESSION_KEY] = \
            'lazysignup.backends.LazySignupBackend'
        lazy_view(self.request)

    def test_convert_good(self):
        # Check that the convert() method on the lazy user manager
        # correctly converts the lazy user
        user, username = LazyUser.objects.create_lazy_user()
        d = {
            'username': 'test',
            'password1': 'password',
            'password2': 'password',
        }
        form = GoodUserCreationForm(d, instance=user)
        self.assertTrue(form.is_valid())

        user = LazyUser.objects.convert(form)
        self.assertFalse(is_lazy_user(user))

    def test_convert_non_lazy(self):
        # Attempting to convert a non-lazy user should raise a TypeError
        user = User.objects.create_user('dummy', 'dummy@dummy.com', 'dummy')
        form = GoodUserCreationForm(instance=user)
        self.assertRaises(NotLazyError, LazyUser.objects.convert, form)

    def test_user_field(self):
        # We should find that our LAZSIGNUP_CUSTOM_USER setting has been
        # respected.
        self.assertEqual(CustomUser, LazyUser.get_user_class())

    def test_authenticated_user_class(self):
        # We should find that the class of request.user is that of
        # LAZSIGNUP_CUSTOM_USER
        request = HttpRequest()
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        lazy_view(request)
        self.assertEqual(CustomUser, type(request.user))

    def test_backend_get_custom_user_class(self):
        # The get_user method on the backend should also return instances of
        # the custom user class.
        lazy_view(self.request)
        backend = LazySignupBackend()
        user_class = LazyUser.get_user_class()
        pk = user_class.objects.all()[0].pk
        self.assertEqual(user_class, type(backend.get_user(pk)))

    def test_session_name_conflict(self):
        # Test for issue #6. If a user object exists with the same name as
        # the sha-1 hash of the session id (well, the first
        # username.max_length characters thereof) then we should not see an
        # error when the user is created. This was actually fixed by changing
        # the mechanism to associate a lazy user with a session.

        # Calling get_user triggers a session key cycle the first time. Do it
        # now, so we can grab the final session key.
        get_user(self.request)
        key = self.request.session.session_key
        username = hashlib.sha1(key).hexdigest()[:30]
        User.objects.create_user(username, '')
        r = lazy_view(self.request)
        self.assertEqual(200, r.status_code)

    def test_converted_signal(self):
        # The `converted` signal should be dispatched when a user is
        # successfully converted.
        user, username = LazyUser.objects.create_lazy_user()
        d = {
            'username': 'test',
            'password1': 'password',
            'password2': 'password',
        }
        form = GoodUserCreationForm(d, instance=user)
        # setup signal
        self.handled = False

        def handler(sender, **kwargs):
            self.assertEqual(kwargs['user'], user)
            self.handled = True
        converted.connect(handler)
        # convert user
        user = LazyUser.objects.convert(form)
        # check signal
        self.assertTrue(self.handled)

    def test_lazy_user_enters_requires_lazy_decorator(self):
        self.request.user, _ = LazyUser.objects.create_lazy_user()
        response = requires_lazy_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_lazy_user_enters_requires_nonlazy_decorator(self):
        self.request.user, _ = LazyUser.objects.create_lazy_user()
        try:
            requires_nonlazy_view(self.request)
        except NoReverseMatch, e:
            self.assert_("view-for-lazy-users" in e.args[0])

    def test_nonlazy_user_enters_requires_nonlazy_decorator(self):
        self.request.user = AnonymousUser()
        response = requires_nonlazy_view(self.request)
        self.assertEqual(response.status_code, 200)

    def test_nonlazy_user_enters_requires_lazy_decorator(self):
        self.request.user = AnonymousUser()
        try:
            requires_lazy_view(self.request)
        except NoReverseMatch, e:
            self.assert_("view-for-nonlazy-users" in e.args[0])
