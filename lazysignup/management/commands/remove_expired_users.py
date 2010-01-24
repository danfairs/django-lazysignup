from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import UNUSABLE_PASSWORD
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from lazysignup.middleware import USERNAME_LENGTH

class Command(NoArgsCommand):
    
    help = u"Remove all users whose sessions have expired and who haven't set a password"
    
    def handle_noargs(self, **options):
        valid_sessions = [k[:USERNAME_LENGTH] for k in
                          Session.objects.all().values_list('session_key', 
                            flat=True)]
                          
        # Find all the users who have an unusable password, whose usernames 
        # aren't in the list of valid sessions:
        session_users = User.objects.filter(
            password=UNUSABLE_PASSWORD
        ).exclude(
            username__in=valid_sessions
        )

        # Delete each of these users. We don't use the queryset delete() because
        # we want cascades to work.
        for user in session_users:
            user.delete()
