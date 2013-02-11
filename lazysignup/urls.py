try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url

from django.views.generic import TemplateView

# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
    url(r'^$', 'convert', name='lazysignup_convert'),
    url(r'^done/$',
        TemplateView.as_view(template_name='lazysignup/done.html'),
        name='lazysignup_convert_done'),
)
