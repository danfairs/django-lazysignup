import django.dispatch

try:  # keyword removed in Django 4.0, deprecated since 3.1
    converted = django.dispatch.Signal(providing_args=['user'])
except TypeError:
    converted = django.dispatch.Signal()  # 'user'
