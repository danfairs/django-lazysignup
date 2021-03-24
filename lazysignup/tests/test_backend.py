from django.contrib.auth import get_user_model
from django.test import TestCase
from lazysignup.backends import LazySignupBackend


class BackendTests(TestCase):
    """
    Tests for LazySignupBackend
    """

    def setUp(self):
        self.backend = LazySignupBackend()

    def test_authenticate_no_user(self):
        """
        Test no user exists
        """
        self.assertIsNone(self.backend.authenticate("nobody"))

    def test_authenticate(self):
        """
        :return:
        """
        user = get_user_model().objects.create_user(
            username="admin", email="admin@example.com", password="password"
        )

        self.assertEqual(user.email, self.backend.authenticate(None, "admin").email)
