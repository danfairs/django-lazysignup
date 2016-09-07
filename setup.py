from setuptools import setup, find_packages
import os
import re


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'lazysignup/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


tests_require = [
    'coverage>=3.7.1',
    'flake8>=2.2.0',
    'mock>=1.0.1',
    'psycopg2>=2.6',
    'mysqlclient>=1.3.3',
]

install_requires = [
    'setuptools',
    'Django>=1.10.0',
    'six>=1.9'
]

extras_require = {
    'test': tests_require,
    'packaging': ['wheel'],
    'docs': ['Sphinx>=1.2.2', 'sphinx_rtd_theme'],
}

everything = set()
for deps in extras_require.values():
    everything.update(deps)
everything.update(set(install_requires))
extras_require['all'] = list(everything)


setup(
    name='django-lazysignup',
    version=get_version(),
    description="Lazy signup for Django",
    long_description=open("README.rst").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
    url='http://github.com/danfairs/django-lazysignup',
    author='Dan Fairs',
    author_email='dan@fezconsulting.com',
    keywords='django lazy signup app user',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Framework :: Django :: 1.7",
        "Framework :: Django :: 1.8",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License"
    ],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
)
