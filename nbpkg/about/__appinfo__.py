#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2019. K.I.A.Derouiche (Algiers, ALGERIA).
# along with this program.  If not, see <https://www.mozilla.org/en-US/MPL/2.0/>.

from colorama import Fore, Style

long_description = """\
nbpkgquery is a CLI and Powerfull tool that finds and extracts information from a NetBSD package using the pkgsrc framework.
"""

__nameapp__ = "nbpkgquery"
__author__  = "K.I.A. Derouiche"
__email__   = "kamel.derouiche@gmail.com"
__descr__   = "nbpkgquery is a Powerfull tool to search and extract information from NetBSD packages."
__ldescr__  = long_description
__platform__ = ["NetBSD", "Linux", "FreeBSD", "OpenBSD", "DragonFlyBSD", "Windows"]
__url__      = "https://github.com/kiaderouiche/nbpkgquery"
__license__  = "MPL-2.0"
__keywords__ = ["checksum", "md5", "sha-1", "sha256"]
__install_requires__ = ["click"]
__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: Mozilla Public License (MPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.7',
    'Topic :: Security'
]

def get_about() -> str:
    """Retourne les informations générales du projet avec bordures et couleurs."""
    return f"""\
{Fore.GREEN}╔════════════════════════════════════╗{Style.RESET_ALL}
{Fore.GREEN}║ {__nameapp__:<33} ║{Style.RESET_ALL}
{Fore.GREEN}╚════════════════════════════════════╝{Style.RESET_ALL}
{Fore.CYAN}{__descr__}{Style.RESET_ALL}
{Fore.BLUE}Auteur      :{Style.RESET_ALL} {__author__}
{Fore.BLUE}Email       :{Style.RESET_ALL} {__email__}
{Fore.BLUE}Licence     :{Style.RESET_ALL} {__license__}
{Fore.BLUE}Plateformes :{Style.RESET_ALL} {", ".join(__platform__)}
{Fore.BLUE}Site Web    :{Style.RESET_ALL} {__url__}
{Fore.YELLOW}Description :{Style.RESET_ALL} {__ldescr__.strip()}
"""
