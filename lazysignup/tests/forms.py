from lazysignup.forms import UserCreationForm


class GoodUserCreationForm(UserCreationForm):
    """ Hardcoded credentials to demonstrate that the get_credentials method
    is being used
    """
    def get_credentials(self):
        return {
            'username': 'demo',
            'password': 'demo',
        }

    def save(self, commit=True):
        instance = super(GoodUserCreationForm, self).save(commit=False)
        creds = self.get_credentials()
        instance.username = creds['username']
        instance.set_password(creds['password'])
        if commit:
            instance.save()
        return instance
