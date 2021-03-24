from django.http import HttpResponse
from lazysignup.decorators import (
    allow_lazy_user,
    require_lazy_user,
    require_nonlazy_user,
)


def view(request):
    r = HttpResponse()
    try:
        if request.user.is_authenticated():
            r.status_code = 500
    except TypeError:
        if request.user.is_authenticated:
            r.status_code = 500

    return r


@allow_lazy_user
def lazy_view(request):
    r = HttpResponse()

    if request.user.is_anonymous or request.user.has_usable_password():
        r.status_code = 500
    return r


@require_lazy_user("view-for-nonlazy-users")
def requires_lazy_view(request):
    return HttpResponse()


@require_nonlazy_user("view-for-lazy-users")
def requires_nonlazy_view(request):
    return HttpResponse()
