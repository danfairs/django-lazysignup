Custom User classes
===================

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
