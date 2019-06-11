#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import click

@click.group()
@click.help_option("--help", help="Affiche ce message et quitte.", is_flag=True, is_eager=True)
def cli() -> None:
    """
    nbpkgquery is a find and extract information from a NetBSD package and pkgsrc Framework
    """
    pass

if __name__ == '__main__':
    cli()
