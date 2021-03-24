from django.contrib.auth import get_user_model, authenticate
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

from django.http import HttpRequest
from django.test import TestCase

from lazysignup.utils import is_lazy_user


class CustomUserModelTests(TestCase):
    """
    Test for custom user model
    """

    def setUp(self):
        super(CustomUserModelTests, self).setUp()
        self.request = HttpRequest()
        SessionMiddleware().process_request(self.request)

        # We have to save the session to cause a session key to be generated.
        self.request.session.save()

    def test_good_custom_convert_form(self):
        self.client.get("/lazy/")
        self.client.post(
            reverse("test_good_convert"),
            {
                "username": "foo",
                "password1": "password",
                "password2": "password",
            },
        )
        users = get_user_model().objects.all()
        self.assertEqual(1, len(users))
        user = users[0]

        # The credentials returned by get_credentials should have been used
        self.assertEqual(user, authenticate(username="demo", password="demo"))

        # The user should no longer be lazy
        self.assertFalse(is_lazy_user(user))
