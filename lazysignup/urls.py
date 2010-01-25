from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
    url(r'^convert/$', 'convert', name='lazysignup_convert'),
    url(r'^convert/done/$', direct_to_template, { 
        'template': 'lazysignup/done.html',
        }, name='lazysignup_convert_done'),
)
