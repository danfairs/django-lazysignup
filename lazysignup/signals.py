import django.dispatch

converted = django.dispatch.Signal(providing_args=['user'])
lazy_user_logged_in = django.dispatch.Signal(
    providing_args=['request', 'user', 'lazy_user']
)
