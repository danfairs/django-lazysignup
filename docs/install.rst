Requirements
============

Tested on Django 1.2.x, though should work on Django 1.0 and later
(although you  will need to customise one of the templates.) It requires
``django.contrib.auth`` to be in the ``INSTALLED_APPS`` list.

Note that from 0.9.0, Django 1.3 or later will be required.

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

