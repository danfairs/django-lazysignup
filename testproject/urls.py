from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.forms import UserCreationForm

from lazysignup.tests import GoodUserCreationForm

# URL test patterns for lazysignup. Use this file to ensure a consistent
# set of URL patterns are used when running unit tests.

urlpatterns = patterns('',
    (r'^convert/', include('lazysignup.urls')),
    (r'^custom_convert/', 'lazysignup.views.convert', {
        'template_name': 'lazysignup/done.html'
        }),
    (r'^custom_convert_ajax/', 'lazysignup.views.convert', {
        'ajax_template_name': 'lazysignup/done.html'
        }),
)

urlpatterns += patterns('lazysignup.tests',
    url(r'^nolazy/$', 'view', name='test_view'),
    url(r'^lazy/$', 'lazy_view', name='test_lazy_view'),
)

urlpatterns += patterns('lazysignup.views',
    url(r'^bad-custom-convert/$', 'convert', {
        'form_class': UserCreationForm}, name='test_bad_convert'),
    url(r'^good-custom-convert/$', 'convert', {
        'form_class': GoodUserCreationForm}, name='test_good_convert'),
)
