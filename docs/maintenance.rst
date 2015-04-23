Maintenance
===========

Over time, a number of user accounts that haven't been converted will build up.
To avoid performance problems from an excessive number of user accounts, it's
recommended that the ``remove_expired_users`` management command is run on
a regular basis. It runs from the command line::

  python manage.py remove_expired_users

In a production environment, this should be run from cron or similar.

There is also an action in the Django Admin for removing expired users. To use,
select all LazyUser instances, select the action "Delete selected lazy users
and unconverted users older than settings.SESSION_COOKIE_AGE", and click "Go".

This works by removing user accounts from the system whose associated sessions
have expired. ``user.delete()`` is called for each user, so related data will
be removed as well.

Note of course that these deletes will cascade, so if you need to keep data
associated with such users, you'll need to write your own cleanup job.
