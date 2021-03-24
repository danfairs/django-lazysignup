from custom_user_tests.models import CustomUser
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


class GoodUserCreationForm(forms.ModelForm):
    """Hardcoded credentials to demonstrate that the get_credentials method
    is being used
    """

    error_messages = {
        "duplicate_username": _("A user with that username already exists."),
        "password_mismatch": _("The two password fields didn't match."),
    }
    username = forms.RegexField(
        label=_("Username"),
        max_length=30,
        regex=r"^[\w.@+-]+$",
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and " "@/./+/-/_ only."
        ),
        error_messages={
            "invalid": _(
                "This value may contain only letters, numbers and "
                "@/./+/-/_ characters."
            )
        },
    )
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
    )

    def get_credentials(self):
        return {
            "username": "demo",
            "password": "demo",
        }

    class Meta:
        model = CustomUser
        fields = ("username",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            get_user_model()._default_manager.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages["duplicate_username"],
            code="duplicate_username",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def save(self, commit=True):
        instance = super(GoodUserCreationForm, self).save(commit=False)
        creds = self.get_credentials()
        instance.username = creds["username"]
        instance.set_password(creds["password"])
        if commit:
            instance.save()
        return instance
