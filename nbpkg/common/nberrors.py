class NbpkgError(Exception):
    """Exception de base pour nbpkg."""
    pass

class FileNotFoundError(NbpkgError):
    """Exception levée quand un file n'est pas trouvé."""
    pass

class PackageNotFoundError(NbpkgError):
    """Exception levée quand un paquet n'est pas trouvé."""
    pass

class PackageParsingError(NbpkgError):
    """Exception levée quand un paquet n'est pas trouvé."""
    pass

class InvalidPackageError(NbpkgError):
    """Exception levée pour un paquet invalide."""
    pass

class RepositoryError(NbpkgError):
    """Exception levée pour une erreur de dépôt."""
    pass

class NetworkError(NbpkgError):
    """Exception levée pour une erreur de réseau."""
    pass

class CorruptedPackageError(Exception):
    """Exception levée lorsqu'un fichier de la base de données des paquets est mal formé."""
    pass

class AmbiguousPackageError(Exception):
    """Exception levée lorsqu'un paquet est trouvé dans plusieurs sources."""
    def __init__(self, message, source_pkg_data=None, binary_pkg_data=None):
        super().__init__(message)
        self.source_pkg_data = source_pkg_data
        self.binary_pkg_data = binary_pkg_data
