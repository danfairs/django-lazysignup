from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase


class UserCreationForm(UserCreationFormBase):
    def get_credentials(self):
        return {
            "username": self.cleaned_data["username"],
            "password": self.cleaned_data["password1"],
        }
