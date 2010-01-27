Introduction
============

``django-lazysignup`` is a package designed to allow users to interact with a 
site as if they were authenticated users, but without signing up. At any time, 
they can convert their temporary user account to a real user account.

``django-lazysignup`` is alpha software. Bug reports, patches and extensions
are welcomed.

Requirements
============

Tested on Django 1.2alpha1, though should work on Django 1.0 and later 
(although you  will need to customise one of the templates.) It requires 
``django.contrib.auth`` to be in the ``INSTALLED_APPS`` list.

Installation
============

Install the django-lazysignup egg as you would any other development egg from 
a source control system. For example, with pip::

  pip install -e git://github.com/danfairs/django-lazysignup.git#egg=django-lazysignup
  
Once that's done, you need to add ``lazysignup`` to your ``INSTALLED_APPS``. 
You will also need to add ``lazysignup``'s authentication backend to your 
site's ``AUTHENTICATION_BACKENDS`` setting::

  AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'lazysignup.backends.LazySignupBackend',
  )
  
You'll also need the middleware installed. It should come between the session
and auth backends::

  MIDDLEWARE_CLASSES = (
      "django.middleware.common.CommonMiddleware",
      "django.contrib.sessions.middleware.SessionMiddleware",
      "django.middleware.csrf.CsrfViewMiddleware",
      "lazysignup.middleware.LazySignupMiddleware",
      "django.contrib.auth.middleware.AuthenticationMiddleware",
      "django.contrib.messages.middleware.MessageMiddleware",
      "django.middleware.doc.XViewMiddleware",
  )
  

If you are using Django prior to 1.2, you should override the 
``lazysignup/convert.html``  template to remove the ``{% csrf_token %}`` 
template tag. This may be handled more elegantly in a future release.

Finally, you need to add lazysignup to your URLConf, using something like
this::

  urlpatterns += (''
      (r'^convert/', include('lazysignup.urls')),
  )


Usage
=====

The package works by creating temporary user accounts based on a user's 
session key whenever a flagged view is requested. You can specify which
views trigger this behaviour using the ``lazysignup.decorators.allow_lazy``
decorator.

When an anonymous user requests such a view, a temporary user account will be 
created for them, and they will be logged in. The user account will have
an unusable password set, so that it can't be used to log in as a regular
user. Hence, the way to tell a regular use from a temporary user is to call
the ``user.has_usable_password()`` method. If this returns ``False``, then the
user is temporary. Note that ``user.is_anonymous()`` will return ``False`` 
and ``user.is_authenticated()`` will return ``True``.

A view is provided to allow such users to convert their temporary account into
a real user account by providing a username and a password.

A Django management command is provided to clear out stale, uncoverted user
accounts. 

The ``allow_lazy`` decorator
----------------------------

Use this decorator to indicate that accessing the view should cause anonymous
users to have temporary accounts created for them. It's probably unwise to put
this on your homepage view!

For example::

  from django.http import HttpResponse
  from lazysignup.decorators import allow_lazy
  
  @allow_lazy
  def my_view(request):
    return HttpResponse(request.user.username)

When accessing the above view, a very simple response containing the generated
username will be displayed. 


Using the convert view
----------------------

Users will be able to visit the ``/convert/`` view. This provides a form with 
a username, password and password confirmation. As long as they fill in valid
details, their temporary user account will be converted into a real user 
account that they can log in with as usual.


Maintenance
-----------

Over time, a number of user accounts that haven't been converted will build up.
To avoid performance problems from an excessive number of user accounts, it's
recommended that the ``remove_expired_users`` management command is run on
a regular basis. It runs from the command line::

  python manage.py remove_expired_users
  
In a production environment, this should be run from cron or similar.

This works be removing user accounts from the system whose associated sessions
are no longer in the session table. ``user.delete()`` is called for each user,
so related data will be removed as well.


Helping Out
-----------

If you want to add a feature or fix a bug, please go ahead! Fork the project
on GitHub, and when you're done with your changes, let me know. Fixes and
features with tests have a greater chance of being merged. To run the tests,
do::

  python manage.py test --settings=lazysignup.test_settings lazysignup
  

Note that the tests require the ``mock`` package.