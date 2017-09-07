from django.contrib.auth.backends import ModelBackend
from lazysignup.models import LazyUser
from lazysignup.constants import LAZYSIGNUP_USER_NAME_FIELD


class LazySignupBackend(ModelBackend):

    def authenticate(self, username=None):
        user_class = LazyUser.get_user_class()
        try:
            return user_class.objects.get(**{
                LAZYSIGNUP_USER_NAME_FIELD: username
            })
        except user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        # Annotate the user with our backend so it's always available,
        # not just when authenticate() has been called. This will be
        # used by the is_lazy_user filter.
        user_class = LazyUser.get_user_class()
        try:
            user = user_class.objects.get(pk=user_id)
        except user_class.DoesNotExist:
            user = None
        else:
            user.backend = 'lazysignup.backends.LazySignupBackend'
        return user
