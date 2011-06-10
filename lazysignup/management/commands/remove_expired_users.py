from django.core.management.base import NoArgsCommand
from django.contrib.sessions.models import Session

from lazysignup.models import LazyUser
from lazysignup.utils import username_from_session


class Command(NoArgsCommand):
    help = u"""Remove all users whose sessions have expired and who haven't
               set a password. This assumes you are using database sessions"""

    def handle_noargs(self, **options):
        usernames = self.get_valid_usersnames()

        # Find all LazyUser objects who no longer have a valid session
        to_delete = LazyUser.objects.exclude(
            user__username__in=usernames).select_related('user')

        # Delete each of these users. We don't use the queryset delete()
        # because we want cascades to work.
        for lazy_user in to_delete:
            lazy_user.user.delete()

    def get_username(self, session_key, username_length=None):
        return username_from_session(session_key, username_length)

    def get_valid_usersnames(self):
        return [username_from_session(sk) for sk in
            Session.objects.all().values_list('session_key', flat=True)]
