.. image:: https://travis-ci.com/tugcanolgun/django-lazysignup.svg?branch=master
    :target: https://travis-ci.com/tugcanolgun/django-lazysignup
    
Introduction
============

``django-lazysignup`` is a package designed to allow users to interact with a
site as if they were authenticated users, but without signing up. At any time,
they can convert their temporary user account to a real user account.

`Read the full documentation`_.

.. _Read the full documentation: http://django-lazysignup.readthedocs.org/

Updates
=======

This is a fork from `danfairsdjango-lazysignup <https://github.com/danfairs/django-lazysignup>`_.

* Replace static image at the beginning in README with an actual current status badge.
* Update it to be compatible with django 3.1.5. 
* Fix wrong use of is with == for literal comparison.
* Fix custom_user_tests to be compatible with django 3.1.5.
* Fix travis tests. Update python and django versions with 3.8-3.9 and 3.1.5.
* Fix the problem where yandex browser users treated as search engine bots.
