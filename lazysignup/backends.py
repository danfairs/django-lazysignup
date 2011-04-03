from django.contrib.auth.backends import ModelBackend
from lazysignup.models import LazyUser

class LazySignupBackend(ModelBackend):

    def authenticate(self, username=None):
        lazy_users = LazyUser.objects.filter(
            user__username=username
        ).select_related('user')
        try:
            return lazy_users[0].user
        except IndexError:
            return None

    def get_user(self, user_id):
        # Annotate the user with our backend so it's always available,
        # not just when authenticate() has been called. This will be
        # used by the is_lazy_user filter.
        user = super(LazySignupBackend, self).get_user(user_id)
        if user:
            user.backend = 'lazysignup.backends.LazySignupBackend'
        return user

