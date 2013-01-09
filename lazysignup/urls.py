import django
django_version = float('%s.%s' % (django.VERSION[0], django.VERSION[1]))

from django.conf.urls.defaults import patterns, url

# URL patterns for lazysignup

if django_version >= 1.5:
    from django.views.generic import TemplateView
    urlpatterns = patterns('lazysignup.views',
        url(r'^$', 'convert', name='lazysignup_convert'),
        url(r'^done/$', TemplateView.as_view(template_name="lazysignup/done.html"),
            name='lazysignup_convert_done'),
    )
else:
    from django.views.generic.simple import direct_to_template
    urlpatterns = patterns('lazysignup.views',
        url(r'^$', 'convert', name='lazysignup_convert'),
        url(r'^done/$', direct_to_template, {
            'template': 'lazysignup/done.html',
            }, name='lazysignup_convert_done'),
    )
