from django.test import TestCase
from django.contrib.auth import get_user_model

from lazysignup.templatetags.lazysignup_tags import is_lazy_user
from lazysignup.models import LazyUser


class TemplateTagTests(TestCase):
    """
    Tests the template tags
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password'
        )
        self.lazy_user, self.lazy_username = LazyUser.objects.create_lazy_user()

    def test_is_not_lazy(self):
        is_lazy = is_lazy_user(self.user)

        self.assertFalse(is_lazy)

    def test_is_lazy(self):
        is_lazy = is_lazy_user(self.lazy_user)
        self.assertTrue(is_lazy)
