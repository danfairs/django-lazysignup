from django.urls import path
from django.views.generic import TemplateView

from .views import convert

# URL patterns for lazysignup

urlpatterns = [
    path('', convert, name='lazysignup_convert'),
    path('done/',
        TemplateView.as_view(template_name='lazysignup/done.html'),
        name='lazysignup_convert_done'),
]
