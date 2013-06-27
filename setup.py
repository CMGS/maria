#!/usr/local/bin/python2.7
#coding:utf-8
import os
from setuptools import setup, find_packages

# package meta info
NAME = "maria"
VERSION = "0.1.0"
DESCRIPTION = "A way to serve git repo through ssh protocol like github"
AUTHOR = "CMGS"
AUTHOR_EMAIL = "ilskdw@gmail.com"
LICENSE = "BSD"
URL = "https://github.com/CMGS/maria"
KEYWORDS = "ssh proxy"
CLASSIFIERS = []

# package contents
MODULES = []
PACKAGES = find_packages(exclude=['tests.*', 'tests', 'examples.*', 'examples'])
ENTRY_POINTS = """
[console_scripts]
run-maria = maria.run:main
"""

# dependencies
INSTALL_REQUIRES = ['gevent',]

here = os.path.abspath(os.path.dirname(__file__))


def read_long_description(filename):
    path = os.path.join(here, filename)
    if os.path.exists(path):
        return open(path).read()
    return ""

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description('README.md'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    py_modules=MODULES,
    packages=PACKAGES,
    install_package_data=True,
    zip_safe=False,
    entry_points=ENTRY_POINTS,
    install_requires=INSTALL_REQUIRES,
)

