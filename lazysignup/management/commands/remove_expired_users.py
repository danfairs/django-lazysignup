import datetime
from django.conf import settings

from django.core.management.base import NoArgsCommand

from lazysignup.models import LazyUser


class Command(NoArgsCommand):
    help = u"""Remove all users whose sessions have expired and who haven't
               set a password. This assumes you are using database sessions"""

    def handle_noargs(self, **options):
        # Delete each of these users. We don't use the queryset delete()
        # because we want cascades to work (including, of course, the LazyUser
        # object itself)
        for lazy_user in self.to_delete():
            lazy_user.user.delete()

    def to_delete(self):
        delete_before = datetime.datetime.now() - datetime.timedelta(
            seconds=settings.SESSION_COOKIE_AGE)
        return LazyUser.objects.filter(
            user__last_login__lt=delete_before
        ).select_related('user')
