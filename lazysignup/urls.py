try:  # removed in Django 4.0, deprecated since 3.1
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from django.views.generic import TemplateView

from .views import convert

# URL patterns for lazysignup

urlpatterns = [
    url(r'^$', convert, name='lazysignup_convert'),
    url(r'^done/$',
        TemplateView.as_view(template_name='lazysignup/done.html'),
        name='lazysignup_convert_done'),
]
