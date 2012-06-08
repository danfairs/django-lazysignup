Maintenance
===========

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
