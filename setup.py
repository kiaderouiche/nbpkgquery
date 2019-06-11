#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import isfile
import json

if isfile ('README.md'):
    with open('README.md') as frmd:
        long_description = frmd.read()

import os.path
import json


with open(os.path.join("nbpkg", "common", "version.json")) as f:
    __version__ = '.'.join(str(part) for part in json.load(f))

__appinfo__ = {}
with open(os.path.join("nbpkg", "common", "__appinfo__.py")) as f:
    exec(f.read(), __appinfo__)

modname = __appinfo__['__nameapp__']
distname = __appinfo__.get('distname', modname)
data_files = __appinfo__.get('data_files', None)
include_dirs = __appinfo__.get('include_dirs', [])
install_requires = __appinfo__.get('install_requires', None)

setup(
    name =distname,
    license=__appinfo__['__license__'],
    version=__version__,
    description= __appinfo__['__ldescr__'],
    long_description=__appinfo__['__ldescr__'],
    author=__appinfo__['__author__'],
    author_email= __appinfo__['__email__'],
    url=__appinfo__['__url__'],
    platforms = __appinfo__['__platform__'],
    packages= find_packages(),
    classifiers=__appinfo__['__classifiers__'],
    data_files=data_files,
    install_requires= __appinfo__['__install_requires__'],
    entry_points = {
        'console_scripts': [
            'nbquery = nbpkg.__main__:main',
        ],
    },
)
