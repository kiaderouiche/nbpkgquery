#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import isfile

version = '0.0.1rc1'

if isfile ('README.md'):
    with open('README.md') as frmd:
        long_description = frmd.read()

setup(
      name='nbpkginspec',
      version=version,
      description="A pure python NetBSD package reader",
      long_description=long_description,
      author="K.I.A.Derouiche",
      author_email="kamel.derouiche@gmail.com",
      url="https://github.com/kiaderouiche/nbpkgquery",
      license="GPLv3",
      packages=find_packages,
      classifiers=[
    	'Development Status :: 4 - Beta',
    	'License :: OSI Approved :: GPLv3 License',
      'Programming Language :: Python :: 3.7'
      ],
)
