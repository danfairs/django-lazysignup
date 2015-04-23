Helping Out
===========

If you want to add a feature or fix a bug, please go ahead! Fork the project
on `GitHub`_ and when you're done with your changes, let me know. Fixes and
features with tests have a greater chance of being merged. To run the tests,
do:

.. code-block:: bash

  git clone https://github.com/danfairs/django-lazysignup
  cd django-lazysignup

  # Install dependencies and requirements
  pip install -e .[all]

  # To test against a PostgreSQL Database locally
  psql -C "CREATE USER lazysignup with login createdb password 'lazysignup';"
  psql -C "CREATE DATABASE lazysignup with OWNER lazysignup;"
  export DB="local-postgres"

  # To test against a MySQL Database locally
  mysql -e "CREATE DATABASE lazysignup CHARACTER SET utf8;"
  mysql -e "CREATE USER 'lazysignup'@'localhost' IDENTIFIED BY 'lazysignup';"
  mysql -e "GRANT ALL PRIVILEGES ON lazysignup.* to 'lazysignup'@'localhost';"
  mysql -e "FLUSH PRIVILEGES;"
  export DB="local-mysql"

  # To test against a SQLite Database locally
  export DB="sqlite"

  # Run the tests and report coverage
  coverage run manage.py test
  coverage report --fail-under=98

  coverage run manage.py test --settings=custom_user_tests.settings
  coverage report --fail-under=98

.. _GitHub: https://github.com/danfairs/django-lazysignup


Build the docs
--------------

To build and view the documentation, run ::

    pip install -e .[all]
    python setup.py build_sphinx
    open docs/_build/html/index.html

