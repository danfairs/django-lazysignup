from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import UNUSABLE_PASSWORD
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from lazysignup.middleware import username_from_session

class Command(NoArgsCommand):
    help = u"Remove all users whose sessions have expired and who haven't set a password"
    
    def handle_noargs(self, **options):
        usernames = [username_from_session(sk) for sk in Session.objects.all().values_list('session_key', flat=True)]

        # Find all the users who have an unusable password, whose usernames 
        # aren't in the list of valid sessions:
        session_users = User.objects.filter(
            password=UNUSABLE_PASSWORD
        ).exclude(
            username__in=usernames
        )

        # Delete each of these users. We don't use the queryset delete() because
        # we want cascades to work.
        for user in session_users:
            user.delete()
            
    def get_username(self, session_key, username_length=None):
        return username_from_session(session_key, username_length)
