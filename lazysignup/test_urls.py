from django.conf.urls.defaults import *
from lazysignup.urls import urlpatterns

# URL test patterns for lazysignup. Use this file to ensure a consistent
# set of URL patterns are used when running unit tests. 

urlpatterns += patterns('lazysignup.tests',
    url(r'^nolazy/$', 'view', name='test_view'),
    url(r'^lazy/$', 'lazy_view', name='test_lazy_view'),
)
