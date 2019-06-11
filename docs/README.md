Usage
-----

        >>> from nbpkginspec.nbpkg import NBPKG
        >>> nb = NBPKG('package-1.0.1nb.tgz')
        >>> nb.binary # from pkgsrc framework
        True
        >>> nb.name()
        'package'
        >>> nb.package()
        'package-1.0.1nb'
        >>> nb[template.NBPKG_DESCRIPTION]
        'package description'
        >>> nb[template.NBPKG_ARCH]
        'i586's

