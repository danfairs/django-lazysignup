from django.conf.urls import url
from django.views.generic import TemplateView

from .views import convert

# URL patterns for lazysignup

urlpatterns = [
    url(r'^$', convert, name='lazysignup_convert'),
    url(r'^done/$',
        TemplateView.as_view(template_name='lazysignup/done.html'),
        name='lazysignup_convert_done'),
]
