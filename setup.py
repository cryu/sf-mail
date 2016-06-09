"""
starflyer - mail
================

Mail module for starflyer

Changelog
---------

2016-07-09
**********

* implemented SMTP login. provider username and password to authenticate with an smtp server


"""
from setuptools import setup


setup(
    name='sf-mail',
    version='1.1',
    url='',
    license='BSD',
    author='Christian Scholz',
    author_email='cs@comlounge.net',
    description='mail module for starflyer',
    long_description=__doc__,
    packages=['sfext',
              'sfext.mail',
             ],
    namespace_packages=['sfext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'starflyer',
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
