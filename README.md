nbpkgquery
===========

nbpkgquery is a find and extract information from a NetBSD package and pkgsrc Framework.

**nbpkgquery v1.-1pre01** tool independante operating system for search package information based pkgsrc framework.

nbpkgquery provides three features:

1. local search

2. remote local search

3. web search

## Requirements

- Python>= 3.7
- click

## Installation

Install from source code

    pip install nbpkgquery


##Usage:


   $ nbquery root -all
   
   $ nbquery distcln package
   
   $ nbquery local -D package

   $ nbquery remote -C package

   $ nbquery web -M maintainer

   $ nbquery task (request pkgsrc/TODO file)
   
   $ nbquery inspect package.tbz package.tgz

