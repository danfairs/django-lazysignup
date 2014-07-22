from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseRedirect
from django.shortcuts import redirect, render_to_response, resolve_url
from django.template import RequestContext
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _

from lazysignup.decorators import allow_lazy_user
from lazysignup.exceptions import NotLazyError
from lazysignup.forms import UserCreationForm
from lazysignup.models import LazyUser


@allow_lazy_user
def convert(request, form_class=UserCreationForm,
            redirect_field_name='next',
            anonymous_redirect=settings.LOGIN_URL,
            template_name='lazysignup/convert.html',
            ajax_template_name='lazysignup/convert_ajax.html'):
    """ Convert a temporary user to a real one. Reject users who don't
    appear to be temporary users (ie. they have a usable password)
    """
    # Get redirect from GET params, or use value from settings, defaulting
    # to provided "done" view
    default_redirect_url = getattr(settings, "LAZY_CONVERT_SUCCESS_URL",
                           'lazysignup_convert_done')
    redirect_to = request.REQUEST.get(redirect_field_name, default_redirect_url)

    # If we've got an anonymous user, redirect to login
    if request.user.is_anonymous():
        return HttpResponseRedirect(anonymous_redirect)

    if request.method == 'POST':
        form = form_class(request.POST, instance=request.user)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

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
            if getattr(settings, 'AUTO_LOGIN_ON_LAZY_CONVERSION', True):
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
    return render_to_response(template_name, {
            'form': form,
            redirect_field_name: redirect_to,
        }, context_instance=RequestContext(request))
