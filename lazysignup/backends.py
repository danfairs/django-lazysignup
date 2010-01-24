from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class LazySignupBackend(ModelBackend):
    
    def authenticate(self, username=None):
        users = [u for u in User.objects.filter(username=username) 
                 if not u.has_usable_password()]
        if len(users) != 1:
            return None
        return users[0]
        
        