Helping Out
===========

If you want to add a feature or fix a bug, please go ahead! Fork the project
on `GitHub`_ and when you're done with your changes, let me know. Fixes and
features with tests have a greater chance of being merged. To run the tests,
do::

  cd /path/to/src/lazysignup/testproject
  python manage.py test lazysignup

Note that the tests require the `Mock`_ package. This (and any other test
dependencies) can easily be installed using the test-requirements.txt file::

  cd /path/to/src/lazysignup
  pip install -r test-requirements.txt

.. _GitHub: https://github.com/danfairs/django-lazysignup
.. _Mock: http://www.voidspace.org.uk/python/mock/
