from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_string

from lazysignup.decorators import allow_lazy_user
from lazysignup.exceptions import NotLazyError
from lazysignup.models import LazyUser
from lazysignup.forms import UserCreationForm
from lazysignup import constants


@allow_lazy_user
def convert(request, form_class=None,
            redirect_field_name='redirect_to',
            anonymous_redirect=settings.LOGIN_URL,
            template_name='lazysignup/convert.html',
            ajax_template_name='lazysignup/convert_ajax.html'):
    """ Convert a temporary user to a real one. Reject users who don't
    appear to be temporary users (ie. they have a usable password)
    """
    redirect_to = 'lazysignup_convert_done'

    if form_class is None:
        if constants.LAZYSIGNUP_CUSTOM_USER_CREATION_FORM is not None:
            form_class = import_string(constants.LAZYSIGNUP_CUSTOM_USER_CREATION_FORM)
        else:
            form_class = UserCreationForm

    # If we've got an anonymous user, redirect to login
    if request.user.is_anonymous():
        return HttpResponseRedirect(anonymous_redirect)

    if request.method == 'POST':
        redirect_to = request.POST.get(redirect_field_name) or redirect_to
        form = form_class(request.POST, instance=request.user)
        if form.is_valid():
            try:
                LazyUser.objects.convert(form)
            except NotLazyError:
                # If the user already has a usable password, return a Bad
                # Request to an Ajax client, or just redirect back for a
                # regular client.
                if request.is_ajax():
                    return HttpResponseBadRequest(
                        content=_(u"Already converted."))
                else:
                    return redirect(redirect_to)

            # Re-log the user in, as they'll now not be authenticatable with
            # the Lazy backend
            login(request, authenticate(**form.get_credentials()))

            # If we're being called via AJAX, then we just return a 200
            # directly to the client. If not, then we redirect to a
            # confirmation page or to redirect_to, if it's set.
            if request.is_ajax():
                return HttpResponse()
            else:
                return redirect(redirect_to)

        # Invalid form, now check to see if is an ajax call
        if request.is_ajax():
            return HttpResponseBadRequest(content=str(form.errors))
    else:
        form = form_class()

    # If this is an ajax request, prepend the ajax template to the list of
    # templates to be searched.
    if request.is_ajax():
        template_name = [ajax_template_name, template_name]
    return render(
        request,
        template_name,
        {
            'form': form,
            'redirect_to': redirect_to
        },
    )
