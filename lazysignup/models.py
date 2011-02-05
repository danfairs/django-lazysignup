import re
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from lazysignup.decorators import USER_AGENT_BLACKLIST

DEFAULT_BLACKLIST = (
    'slurp',
    'googlebot',
    'yandex',
    'msnbot',
    'baiduspider',
)

for user_agent in getattr(settings, 'LAZYSIGNUP_USER_AGENT_BLACKLIST', DEFAULT_BLACKLIST):
    USER_AGENT_BLACKLIST.append(re.compile(user_agent, re.I))

class LazyUserManager(models.Manager):

    def create_lazy_user(self, username):
        user = User.objects.create_user(username, '')
        self.create(user=user)
        return user


class LazyUser(models.Model):
    user = models.ForeignKey('auth.User', unique=True)
    objects = LazyUserManager()