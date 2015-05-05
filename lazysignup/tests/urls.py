from django.conf.urls import patterns, url, include
from django.contrib.auth.forms import UserCreationForm

from django.conf import settings

if settings.AUTH_USER_MODEL is 'auth.User':  # pragma: no cover
    from lazysignup.tests.forms import GoodUserCreationForm
else:  # pragma: no cover
    from custom_user_tests.forms import GoodUserCreationForm

from django.contrib import admin

admin.autodiscover()


# URL test patterns for lazysignup. Use this file to ensure a consistent
# set of URL patterns are used when running unit tests.

urlpatterns = patterns(
    '',
    url(r'^admin/?', include(admin.site.urls)),
    (r'^convert/', include('lazysignup.urls')),
    (r'^custom_convert/', 'lazysignup.views.convert', {
        'template_name': 'lazysignup/done.html'
    }),
    (r'^custom_convert_ajax/', 'lazysignup.views.convert', {
        'ajax_template_name': 'lazysignup/done.html'
    }),
)

urlpatterns += patterns(
    'lazysignup.tests.views',
    url(r'^nolazy/$', 'view', name='test_view'),
    url(r'^lazy/$', 'lazy_view', name='test_lazy_view'),
)

urlpatterns += patterns(
    'lazysignup.views',
    url(r'^bad-custom-convert/$', 'convert', {
        'form_class': UserCreationForm}, name='test_bad_convert'),
    url(r'^good-custom-convert/$', 'convert', {
        'form_class': GoodUserCreationForm}, name='test_good_convert'),
)
