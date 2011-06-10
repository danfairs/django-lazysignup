Introduction
============

``django-lazysignup`` is a package designed to allow users to interact with a
site as if they were authenticated users, but without signing up. At any time,
they can convert their temporary user account to a real user account.

``django-lazysignup`` is beta software. Bug reports, patches and extensions
are welcomed. While this package is in beta, backwards-compatibility will be
maintained for a single point release and a DeprecationWarning issued.

Requirements
============

Tested on Django 1.2.x, though should work on Django 1.0 and later
(although you  will need to customise one of the templates.) It requires
``django.contrib.auth`` to be in the ``INSTALLED_APPS`` list.

Installation
============

django-lazysignup can be installed with your favourite package management tool
from PyPI::

  pip install django-lazysignup

Once that's done, you need to add ``lazysignup`` to your ``INSTALLED_APPS``.
You will also need to add ``lazysignup``'s authentication backend to your
site's ``AUTHENTICATION_BACKENDS`` setting::

  AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lazysignup.backends.LazySignupBackend',
  )

If you are using Django prior to 1.2, you should override the
``lazysignup/convert.html``  template to remove the ``{% csrf_token %}``
template tag. This may be handled more elegantly in a future release.

Next, you need to ensure that the tables that ``lazysignup`` uses are created.
You should either run ``python manage.py syncdb``, or use the South support
and run ``python manage.py migrate lazysignup``.

Finally, you need to add lazysignup to your URLConf, using something like
this::

  urlpatterns += (''
      (r'^convert/', include('lazysignup.urls')),
  )


Usage
=====

The package works by creating temporary user accounts based on a user's
session key whenever a flagged view is requested. You can specify which
views trigger this behaviour using the ``lazysignup.decorators.allow_lazy_user``
decorator.

When an anonymous user requests such a view, a temporary user account will be
created for them, and they will be logged in. The user account will have
an unusable password set, so that it can't be used to log in as a regular
user. The way to tell a regular use from a temporary user is to call
the ``is_lazy_user()`` function from ``lazysignup.templatetags.lazysignup_tags``.
If this returns ``True``, then the user is temporary. Note that
``user.is_anonymous()`` will return ``False``  and ``user.is_authenticated()``
will return ``True``. See below for more information on ``is_lazy_user``.

A view is provided to allow such users to convert their temporary account into
a real user account by providing a username and a password.

A Django management command is provided to clear out stale, uncoverted user
accounts - although this depends on your use of database-backed sessions, and
assumes that all user accounts with an expired session are safe to delete. This
may not be the case for all apps, so you may wish to provide your own cleaning
script.

The ``allow_lazy_user`` decorator
---------------------------------

Use this decorator to indicate that accessing the view should cause anonymous
users to have temporary accounts created for them.

For example::

  from django.http import HttpResponse
  from lazysignup.decorators import allow_lazy_user

  @allow_lazy_user
  def my_view(request):
    return HttpResponse(request.user.username)

When accessing the above view, a very simple response containing the generated
username will be displayed.

The ``is_lazy_user`` template filter
------------------------------------

This template filter (which can also be imported from ``lazysignup.utils``
and used in your own code) will return True if the user is a generated user.
You need to pass it the user to test. For example, a site navigation
template might look like this::

    {% load i18n lazysignup_tags %}

    <nav id="account-bar">
      <ul>
        <li><a href="{% url home %}">{% trans "Home" %}</a></li>
        {% if not user|is_lazy_user %}
          <li><a href="#">{% trans "Account" %}</a></li>
          <li><a href="{% url auth_logout %}">{% trans "Log out" %}</a></li>
        {% else %}
          <li><a href="{% url lazysignup_convert %}">{% trans "Save your data" %}</a> {% trans "by setting a username and password" %}</li>
        {% endif %}
      </ul>
    </nav>

This filter is very simple, and can be used directly in view code, or tests. For example::

    from lazysignup.utils import is_lazy_user

    def testIsLazyUserAnonymous(self):
        user = AnonymousUser()
        self.assertEqual(False, is_lazy_user(user))

Note that as of version 0.6.0, the user tested no longer needs to have been
authenticated by the ``LazySignupBackend`` for lazy user detection to work.

User agent blacklisting
-----------------------

The middleware will not created users for certain requests from blacklisted
user agents. This is simply a fairly crude method for preventing many spurious
users being created by passing search engines.

The blacklist is specified with the ``USER_AGENT_BLACKLIST`` setting. This
should be an iterable of regular expression strings. If the user agent string
of a request matches a regex (``search()`` is used, so the match can be anywhere
in the string) then a user will not be created.

If the list is not specified, then the default is as follows

  - slurp
  - googlebot
  - yandex
  - msnbot
  - baiduspider

Specifying your own ``USER_AGENT_BLACKLIST`` will replace this list.

Using the convert view
----------------------

Users will be able to visit the ``/convert/`` view. This provides a form with
a username, password and password confirmation. As long as they fill in valid
details, their temporary user account will be converted into a real user
account that they can log in with as usual.

You may pass your own form class into the `convert` view in order to customise
user creation. The code requires expects the following:

  - It expects to be able to create the form passing in the generated ``User``
    object with an ``instance`` kwarg (in general, this is fine when using a
    ModelForm based on the User model)
  - It expects to be able to call ``save()`` on the form to convert the user
    to a real user
  - It expects to be able to call a ``get_credentials()`` method on the form
    to obtain a set of credentials to authenticate the new user with. The
    result of this call should be a dictionary suitable for passing to
    ``django.contrib.auth.authenticate()``. Typically, this would be a dict
    with ``username`` and ``password`` keys - but this may vary if you're using
    a different authentication backend.

The default configuration, using the provided ``UserCreationForm``, should
be enough for most users, but the customisation point is there if you need
it.

Custom User classes
-------------------

Many projects use a custom ``User`` class, augmenting that from
``django.contrib.auth``. If you want to use such a custom class with
``lazysignup``, then you should set the ``LAZYSIGNUP_USER_MODEL`` setting.
This should be a standard dotted Django name for a model, eg::

    LAZYSIGNUP_USER_MODEL = 'myapp.CustomUser'

The setting defaults to ``auth.User``, so using Django's own ``User`` model.

If you do use a custom user class, note that ``lazysignup`` expects that
class' default manager to have a ``create_user`` method, with the same
signature and semantics as ``django.contrib.auth.models.UserManager``. If your
model actually subclasses Django's own user model, you may well be able to
use this manager directly. For example::

    from django.contrib.auth.models import User, UserManager

    class MyCustomUser(User):
        objects = UserManager()

        notes = models.TextField(blank=True, null=True)

``lazysignup`` also expects that it can fetch instances of your custom user
class using a ``get`` method on the object's manager, and that looking them
up by primary key and by ``username`` will work. See ``lazysignup.backends``
for more detail.

Maintenance
-----------

Over time, a number of user accounts that haven't been converted will build up.
To avoid performance problems from an excessive number of user accounts, it's
recommended that the ``remove_expired_users`` management command is run on
a regular basis. It runs from the command line::

  python manage.py remove_expired_users

In a production environment, this should be run from cron or similar.

This works be removing user accounts from the system whose associated sessions
have expired. ``user.delete()`` is called for each user, so related data will
be removed as well.

Note of course that these deletes will cascade, so if you need to keep data
associated with such users, you'll need to write your own cleanup job. If
that's not the case, then you'll again need to write your own cleanup.
Finally, if you're using a custom user class where the user isn't a subclass
of Django's own user model, you'll again need your own cleanup script.

Helping Out
-----------

If you want to add a feature or fix a bug, please go ahead! Fork the project
on GitHub, and when you're done with your changes, let me know. Fixes and
features with tests have a greater chance of being merged. To run the tests,
do::

  python manage.py test --settings=lazysignup.test_settings lazysignup


Note that the tests require the ``mock`` package.