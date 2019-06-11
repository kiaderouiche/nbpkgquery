#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2019. K.I.A.Derouiche (Algiers, ALGERIA).

# along with this program.  If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.

long_description = """\
"""

__nameapp__ = distname = "nbpkgquery"
__author__  = "K.I.A.Derouiche"
__email__   = "kamel.derouiche@gmail.com"
__descr__   = "nbpkgquery is a find and extract information from a NetBSD package."
__ldescr__  =  long_description
__platform__ = ["NetBSD", "Linux", "FreeBSD", "OpenBSD", "DragonFlyBSD", "Windows"]
__url__      = "https://github.com/kiaderouiche/nbpkgquery"
__license__  = "MPL-2.0"
__keywords__ = "checksum, md5, sha-1, sha256"
__install_requires__ = ["click"]
__classifiers__=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Mozilla Public License (MPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Security',
    ]
