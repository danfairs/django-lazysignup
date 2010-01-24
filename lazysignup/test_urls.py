from django.conf.urls.defaults import *

# URL test patterns for lazysignup. Use this file to ensure a consistent
# set of URL patterns are used when running unit tests. This test_urls
# module should be referred to by your test class.

urlpatterns = patterns('lazysignup.tests',
    url(r'^nolazy/$', 'view', name='test_view'),
    url(r'^lazy/$', 'lazy_view', name='test_lazy_view'),
)
