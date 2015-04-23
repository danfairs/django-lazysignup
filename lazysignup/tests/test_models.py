from django.test import TestCase

from lazysignup.models import LazyUser


class LazyUserModelTests(TestCase):
    """
    Tests for LazyUser Model
    """
    def setUp(self):
        super(LazyUserModelTests, self).setUp()

    def test_str(self):
        """
        Tests str method on LazyUser
        """
        user, username = LazyUser.objects.create_lazy_user()
        lazyuser = user.lazyuser

        self.assertEqual(
            str(username) + ':' + str(lazyuser.created),
            str(user.lazyuser)
        )
