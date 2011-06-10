from django.template import Library
from lazysignup.utils import is_lazy_user

register = Library()
is_lazy_user = register.filter(is_lazy_user)
