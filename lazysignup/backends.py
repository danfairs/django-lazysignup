from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from lazysignup.utils import get_user_class 

class LazySignupBackend(ModelBackend):

    def authenticate(self, username=None):
        users = [u for u in get_user_class().objects.filter(username=username)
                 if not u.has_usable_password()]
        if len(users) != 1:
            return None
        return users[0]

    def get_user(self, user_id):
        # Annotate the user with our backend so it's always available,
        # not just when authenticate() has been called. This will be
        # used by the is_lazy_user filter.
        user = super(LazySignupBackend, self).get_user(user_id)
        if user:
            user = get_user_class().objects.get(pk=user.id)
            user.backend = 'lazysignup.backends.LazySignupBackend'
        return user
