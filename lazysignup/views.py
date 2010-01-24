from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

@require_POST
@login_required
def convert(request, form_class=UserCreationForm):
    """ Convert a temporary user to a real one. Reject users who don't
    appear to be temporary users (ie. they have a usable password)
    """
    if request.user.has_usable_password():
        return HttpResponseBadRequest(content=_(u"Already converted."))
    form = form_class(request.POST, instance=request.user)
    if form.is_valid():
        form.save()
        return HttpResponse()
    return HttpResponseBadRequest(content=str(form.errors))

        