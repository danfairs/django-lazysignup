from django.test import TestCase
from mock import Mock

from lazysignup.models import LazyUser


class LazyUserManagerTests(TestCase):
    """
    Tests for LazyUserManager
    """
    def test_generate_username_no_method(self):
        """
        Tests auto generated UUID username
        """
        mock_user_class = Mock(generate_username=1)
        del mock_user_class.generate_username

        mock_user_class._meta.get_field.return_value.max_length = 32

        username = LazyUser.objects.generate_username(mock_user_class)

        self.assertEqual(len(username), 32)

    def test_generate_username_has_method(self):
        """
        Tests auto generated UUID username
        """
        mock_user_class = Mock()
        mock_user_class.generate_username.return_value = 'testusername'

        username = LazyUser.objects.generate_username(mock_user_class)

        mock_user_class.generate_username.assert_called_once_with()
        self.assertEqual(username, 'testusername')
