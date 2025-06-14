from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict,Any
from functools import wraps
import re
import requests
import hashlib
from nbpkg.common.logger import logger
from nbpkg.core.package import SourcePackage, BinaryPackage
from nbpkg.core.pkgdb import PkgDB
from nbpkg.common.nberrors import PackageParsingError
from nbpkg.core.repository import RepositoryManager
from nbpkg.config.__appconfig__ import PKGSRCDIR

# Décorateurs
def log_operation(func):
    """Décorateur pour journaliser le début et la fin de l'exécution d'une méthode."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"🚀 Début de {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"✅ Fin de {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur dans {func.__name__} : {str(e)}")
            raise
    return wrapper

def handle_package_errors(func):
    """Décorateur pour gérer les exceptions spécifiques aux classes PkgQuery."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PackageParsingError as e:
            logger.error(f"Erreur de parsing : {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue : {str(e)}")
            raise PackageParsingError(f"Erreur lors du traitement du paquet : {str(e)}")
    return wrapper

@dataclass
class PkgDetails:
    pkgname: Optional[str] = None
    version: Optional[str] = None
    comment: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    size: Optional[str] = None
    origin: Optional[str] = None
    files: Optional[List[str]] = None
    build_info: Optional[Dict[str, str]] = None
    dependencies: Optional[List[str]] = None
    build_deps: Optional[List[str]] = None  # Ajout pour build_deps
    runtime_deps: Optional[List[str]] = None  # Ajout pour runtime_deps
    error: Optional[str] = None
    license: Optional[str] = None
    has_man_pages: Optional[bool] = None
    maintainer: Optional[str] = None
    homepage: Optional[str] = None
    master_sites: Optional[List[str]] = None  # Ajout pour master_sites

class PkgQuery:
    def __init__(self, package_name: str = None, binary: bool = False, binary_file: str = None):
        self._package_name = package_name
        self._binary = binary
        self._binary_file = binary_file
        self.details = PkgDetails()
        self._pkg = None
        self._pkg_path = None
        self._pkgdb = PkgDB() if binary else None
        self._repo_manager = RepositoryManager()  # Initialiser RepositoryManager
        if package_name:
            if binary:
                if binary_file:
                    self._pkg = BinaryPackage.from_file_or_url(binary_file)
                else:
                    self._pkg = BinaryPackage(name=package_name, version="Inconnu")
                self._load_binary_details()
            else:
                self._pkg = SourcePackage(name=package_name, version="Inconnu")
                self._load_source_details()
                self._pkg_path = self._find_package_path()

    def _find_package_path(self) -> Optional[Path]:
        # Utiliser les dépôts locaux configurés
        local_repos = [repo for repo in self._repo_manager.repositories if repo["type"] == "local"]
        for repo in local_repos:
            base = Path(repo["path"])
            if not base.exists():
                continue
            for category in base.iterdir():
                if category.is_dir():
                    pkg_path = category / self._package_name
                    if pkg_path.exists() and pkg_path.is_dir():
                        return pkg_path
        return None

    @property
    def package_name(self) -> str:
        return self._package_name

    @property
    def binary(self) -> bool:
        return self._binary

    @log_operation
    @handle_package_errors
    def _load_source_details(self):
        try:
            self._pkg.fetch_source_info()
            self.details.pkgname = self._pkg.name
            self.details.version = self._pkg.version
            self.details.comment = self._pkg.comment
            self.details.description = self._pkg.description
            self.details.dependencies = self._pkg.get_dependencies()
            self.details.categories = self._pkg.categories
            self.details.files = self._pkg.files
            self.details.maintainer = self._pkg.maintainer
            self.details.homepage = self._pkg.homepage
            self.details.license = self._pkg.license
            self.details.has_man_pages = self._pkg.has_man_pages
            self.details.master_sites = self._pkg.get_master_sites()  # Récupérer les master_sites
        except Exception as e:
            self.details.error = f"Erreur lors du chargement des détails source : {str(e)}"

    @log_operation
    @handle_package_errors
    def _load_binary_details(self):
        try:
            if self._binary_file:
                self._pkg.fetch_binary_info()
                self._pkg.sync_with_installed(self._pkgdb)
            self.details.pkgname = self._pkg.name
            self.details.version = self._pkg.version
            self.details.comment = self._pkg.comment
            self.details.description = self._pkg.description
            self.details.dependencies = self._pkg.get_dependencies()
            self.details.build_deps = self._pkg.build_deps  # Ajout des build_deps
            self.details.runtime_deps = self._pkg.runtime_deps  # Ajout des runtime_deps
            self.details.categories = self._pkg.categories
            self.details.files = self._pkg.files
            self.details.origin = self._pkg.origin
            self.details.size = str(self._pkg.size) if self._pkg.size else None
            self.details.build_info = self._pkg.build_info
            self.details.maintainer = self._pkg.maintainer
            self.details.homepage = self._pkg.homepage
            self.details.license = self._pkg.license
            self.details.has_man_pages = self._pkg.has_man_pages
            self.details.master_sites = self._pkg.master_sites  # Ajout des master_sites (peut être vide pour les binaires)
        except Exception as e:
            self.details.error = f"Erreur lors du chargement des détails binaires : {str(e)}"

    @log_operation
    @handle_package_errors
    def show(self) -> PkgDetails:
        if not self._pkg:
            self.details.error = f"Paquet {self._package_name} non initialisé"
            return self.details

        if self._binary:
            # Retourner un format compatible avec display_results() pour les binaires
            result = [{
                "name": self.details.pkgname,
                "filesize": self.details.size if self.details.size else "Aucune taille disponible",
                "build_deps": self.details.build_deps,
                "runtime_deps": self.details.runtime_deps,
                "master_sites": self.details.master_sites or []
            }]
            return result if not self.details.error else {"error": self.details.error}

        # Pour les packages source, retourner un format compatible avec display_master_sites()
        result = [{
            "name": self.details.pkgname,
            "master_sites": self.details.master_sites or [],
            "dependencies": self.details.dependencies
        }]
        return result if not self.details.error else {"error": self.details.error}

    @staticmethod
    @log_operation
    @handle_package_errors
    def search_by_maintainer(maintainer: str, by_email: bool = True) -> PkgDetails:
        details = PkgDetails()
        base = Path("/usr/pkgsrc")
        found = []
        if base.exists():
            for category in base.iterdir():
                if category.is_dir():
                    for pkg in category.iterdir():
                        if pkg.is_dir():
                            src_pkg = SourcePackage(name=pkg.name, version="Inconnu")
                            src_pkg.fetch_source_info()
                            maint_value = src_pkg.maintainer or ""
                            if by_email and maintainer.lower() in maint_value.lower():
                                found.append(f"{category.name}/{pkg.name}")
                            elif not by_email and maint_value and maintainer.lower() in maint_value.split('@')[0].lower():
                                found.append(f"{category.name}/{pkg.name}")
        details.files = found or ["Aucun paquet trouvé"]
        details.pkgname = f"Recherche pour {maintainer} ({'email' if by_email else 'nom'})"
        return details

    @staticmethod
    @log_operation
    @handle_package_errors
    def search_by_name(package_name: str, category: str = None) -> PkgDetails:
        repo_manager = RepositoryManager()
        details = PkgDetails()
        found = []
        local_repos = [repo for repo in repo_manager.repositories if repo["type"] == "local"]
        for repo in local_repos:
            base = Path(repo["path"])
            if not base.exists():
                continue
            dirs = [base / category] if category else base.iterdir()
            for cat in dirs:
                if cat.is_dir():
                    for pkg in cat.iterdir():
                        if pkg.is_dir() and package_name.lower() in pkg.name.lower():
                            src_pkg = SourcePackage(name=pkg.name, version="Inconnu")
                            src_pkg.fetch_source_info()
                            found.append({
                                "path": f"{cat.name}/{pkg.name}",
                                "version": src_pkg.version,
                                "comment": src_pkg.comment,
                                "category": cat.name,
                                "name": pkg.name,
                                "master_sites": src_pkg.get_master_sites()
                            })
        if found:
            details.files = [f"{item['path']} (Version: {item['version']}, Commentaire: {item['comment']})" for item in found]
        else:
            details.files = ["Aucun paquet trouvé"]
        details.pkgname = f"Recherche pour {package_name}" + (f" dans {category}" if category else "")
        return details

    @staticmethod
    @log_operation
    @handle_package_errors
    def get_description(package_name: str) -> PkgDetails:
        details = PkgDetails(pkgname=package_name)
        src_pkg = SourcePackage(name=package_name, version="Inconnu")
        src_pkg.fetch_source_info()
        if src_pkg.description:
            details.description = src_pkg.description
            details.categories = src_pkg.categories
        else:
            details.error = f"Description non trouvée pour {package_name}"
        return details

    @staticmethod
    @log_operation
    @handle_package_errors
    def list_installed_packages(pkg_db_path: str = None, sort_order: str = "asc", sort_by: str = "name") -> List[Dict[str, str]]:
        """
        Liste tous les packages binaires installés dans la base de données des packages.

        Args:
            pkg_db_path (str, optional): Chemin vers la base de données des packages.
                                         Si non spécifié, utilise le chemin par défaut de PkgDB.
            sort_order (str): Ordre de tri des packages ("asc" pour ascendant, "desc" pour descendant).
            sort_by (str): Critère de tri ("name", "version", ou "comment").

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires contenant les informations des packages installés.
        """
        # Validation des paramètres de tri
        valid_sort_orders = ["asc", "desc"]
        valid_sort_by = ["name", "version", "comment"]
        if sort_order not in valid_sort_orders:
            logger.warning(f"Ordre de tri invalide : {sort_order}. Utilisation de 'asc' par défaut.")
            sort_order = "asc"
        if sort_by not in valid_sort_by:
            logger.warning(f"Critère de tri invalide : {sort_by}. Utilisation de 'name' par défaut.")
            sort_by = "name"

        try:
            # Initialiser PkgDB avec le chemin spécifié ou la valeur par défaut
            pkg_db = PkgDB(db_path=pkg_db_path)
        except FileNotFoundError as e:
            logger.error(str(e))
            return [{"error": str(e)}]

        results = []
        # Lister les packages installés
        installed_pkgs = pkg_db.list_installed()
        if installed_pkgs == ["Aucun paquet installé"]:
            return [{"message": "Aucun package binaire installé trouvé."}]

        # Pour chaque package, récupérer les informations (nom, version, comment, etc.)
        for pkg_name in installed_pkgs:
            try:
                info = pkg_db.get_info(pkg_name)
                results.append({
                    "name": info["name"].rsplit("-", 1)[0] if info["version"] != "Inconnu" else info["name"],
                    "version": info["version"] if info["version"] != "Inconnu" else "unknown",
                    "comment": info["comment"] if info["comment"] else "Aucun commentaire disponible",
                    "master_sites": []  # Pas de master_sites pour les binaires installés
                })
            except ValueError as e:
                logger.error(f"Erreur lors de la récupération des informations pour {pkg_name}: {str(e)}")
                results.append({"name": pkg_name, "error": str(e)})
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la récupération des informations pour {pkg_name}: {str(e)}")
                results.append({"name": pkg_name, "error": str(e)})

        # Trier les résultats selon le critère spécifié
        if sort_by == "name":
            results.sort(key=lambda x: x["name"].lower(), reverse=(sort_order == "desc"))
        elif sort_by == "version":
            def version_key(pkg):
                ver = pkg["version"]
                if ver == "unknown":
                    return (0, 0, 0, "", 0)  # Valeur par défaut pour versions invalides

                # Séparer la version principale du suffixe (ex. "2.40nb2" -> "2.40", "nb2")
                match = re.match(r"^(.*?)(nb\d+)?$", ver)
                if not match:
                    return (0, 0, 0, "", 0)

                main_ver, suffix = match.groups()
                suffix = suffix if suffix else ""

                # Convertir la version principale en tuple pour comparaison numérique
                try:
                    ver_parts = [int(x) for x in main_ver.split(".") if x.isdigit()]
                    # Remplir avec des zéros si moins de 3 parties (ex. "1.2" -> [1, 2, 0])
                    ver_parts.extend([0] * (3 - len(ver_parts)))
                except ValueError:
                    ver_parts = [0, 0, 0]

                # Extraire le numéro du suffixe (ex. "nb2" -> 2)
                suffix_num = int(suffix.replace("nb", "")) if suffix.startswith("nb") else 0

                # Retourner un tuple pour comparaison : (parties de version, suffixe, numéro de suffixe)
                return (*ver_parts, suffix, suffix_num)

            results.sort(key=version_key, reverse=(sort_order == "desc"))
        elif sort_by == "comment":
            results.sort(key=lambda x: x["comment"].lower(), reverse=(sort_order == "desc"))

        return results
    
    # Après list_installed_packages
    @staticmethod
    @log_operation
    @handle_package_errors
    def list_package_files(package_name: str, pkg_db_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Liste les fichiers installés par un paquet donné.
        
        Args:
            package_name (str): Nom du paquet à rechercher.
            pkg_db_path (Optional[str]): Chemin vers la base de données des paquets.

        Returns:
            List[Dict[str, Any]]: Liste des fichiers ou un message d'erreur.
        """
        # Initialiser PkgDB avec le chemin spécifié ou la valeur par défaut
        pkg_db = PkgDB(db_path=pkg_db_path)

        # Vérifier si le paquet est installé
        installed_pkgs = pkg_db.list_installed()
        if package_name not in installed_pkgs and f"{package_name}-" not in [pkg.rsplit('-', 1)[0] for pkg in installed_pkgs if '-' in pkg]:
            logger.warning(f"Le paquet '{package_name}' n'est pas installé.")
            return [{"message": f"Le paquet '{package_name}' n'est pas installé."}]

        # Récupérer les informations du paquet
        try:
            package_info = pkg_db.get_info(package_name)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations pour {package_name}: {str(e)}")
            return [{"error": f"Erreur lors de la récupération des informations pour {package_name}: {str(e)}"}]

        # Extraire la liste des fichiers (supposons que get_info retourne une clé "files")
        files = package_info.get("files", [])
        if not files:
            logger.warning(f"Aucun fichier trouvé pour le paquet '{package_name}'.")
            return [{"message": f"Aucun fichier trouvé pour le paquet '{package_name}'."}]

        logger.debug(f"Fichiers trouvés pour {package_name} : {files}")
        return [{"file": f} for f in files]

    @staticmethod
    @log_operation
    @handle_package_errors
    def read_todo_files(pkgsrc_dir: str = PKGSRCDIR) -> List[Dict[str, str]]:
        """
        Lit les fichiers /usr/pkgsrc/TODO et /usr/pkgsrc/wip/TODO.

        Args:
            pkgsrc_dir (str): Chemin vers le répertoire pkgsrc (par défaut: /usr/pkgsrc).

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires contenant les informations des fichiers TODO.
        """
        results = []
        todo_files = [
            Path(pkgsrc_dir) / "TODO",
            Path(pkgsrc_dir) / "wip" / "TODO"
        ]

        for todo_file in todo_files:
            if not todo_file.exists():
                results.append({"file": str(todo_file), "content": "Fichier non trouvé"})
                continue
            try:
                with todo_file.open() as f:
                    content = f.read().strip()
                    if not content:
                        results.append({"file": str(todo_file), "content": "Fichier vide"})
                    else:
                        results.append({"file": str(todo_file), "content": content.splitlines()})
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {todo_file} : {str(e)}")
                results.append({"file": str(todo_file), "content": f"Erreur de lecture : {str(e)}"})

        return results

    @staticmethod
    @log_operation
    @handle_package_errors
    def fetch_changelog(year: str, pkgsrc_dir: str = "/usr/pkgsrc") -> List[Dict[str, str]]:
        """
        Lit ou récupère le fichier CHANGES-YEAR localement ou depuis le web.

        Args:
            year (str): Année du changelog (ex. 2025).
            pkgsrc_dir (str): Chemin vers le répertoire pkgsrc (par défaut: /usr/pkgsrc).

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires contenant les informations du changelog.
        """
        # Validation de l'année
        try:
            year_int = int(year)
            if not (1990 <= year_int <= 2025):  # 2025 est l'année actuelle
                raise ValueError(f"Année {year} invalide. Doit être entre 1990 et 2025.")
        except ValueError as e:
            logger.error(f"Année invalide : {str(e)}")
            return [{"error": f"Année invalide : {str(e)}"}]

        # Vérifier localement
        changelog_file = Path(pkgsrc_dir) / "doc" / f"CHANGES-{year}"
        if changelog_file.exists():
            try:
                with changelog_file.open() as f:
                    content = f.read().strip()
                    return [{"source": "local", "content": content.splitlines()}]
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {changelog_file} : {str(e)}")
                return [{"error": f"Erreur lors de la lecture du fichier local : {str(e)}"}]

        # Si non trouvé localement, tenter de récupérer depuis le web
        url = f"https://cdn.netbsd.org/pub/pkgsrc/current/pkgsrc/doc/CHANGES-{year}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.text.strip()
            return [{"source": "web", "content": content.splitlines()}]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du changelog depuis le web : {str(e)}")
            return [{"error": f"Erreur lors de la récupération du changelog : {str(e)}"}]

    @staticmethod
    @log_operation
    @handle_package_errors
    def verify_distfiles(package: str, category: str, pkgsrc_dir: str = "/usr/pkgsrc") -> List[Dict[str, str]]:
        """
        Vérifie les fichiers de distribution d'un package.

        Args:
            package (str): Nom du paquet (ex. py-six).
            category (str): Catégorie du paquet (ex. lang).
            pkgsrc_dir (str): Chemin vers le répertoire pkgsrc (par défaut: /usr/pkgsrc).

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires contenant les résultats de la vérification.
        """
        # Validation des arguments
        if not package or not isinstance(package, str):
            return [{"error": "Le nom du paquet est obligatoire et doit être une chaîne non vide."}]
        if not category or not isinstance(category, str):
            return [{"error": "L'option --category est obligatoire pour distlint"}]

        distinfo_file = Path(pkgsrc_dir) / category / package / "distinfo"
        if not distinfo_file.exists():
            return [{"error": f"Fichier distinfo non trouvé pour {category}/{package}"}]

        distfiles = []
        checksums = {}
        try:
            with distinfo_file.open() as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SHA1 ("):
                        parts = line.split(" = ")
                        if len(parts) != 2:
                            continue
                        filename = parts[0].replace("SHA1 (", "").rstrip(")")
                        checksum = parts[1]
                        distfiles.append(filename)
                        checksums[filename] = checksum
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier distinfo {distinfo_file} : {str(e)}")
            return [{"error": f"Erreur lors de la lecture du fichier distinfo : {str(e)}"}]

        results = []
        for distfile in distfiles:
            distfile_path = Path(pkgsrc_dir) / "distfiles" / distfile
            if not distfile_path.exists():
                results.append({"file": distfile, "status": "Fichier non trouvé"})
                continue

            try:
                sha1 = hashlib.sha1()
                with distfile_path.open("rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha1.update(chunk)
                computed_checksum = sha1.hexdigest()
                expected_checksum = checksums[distfile]

                if computed_checksum == expected_checksum:
                    results.append({"file": distfile, "status": "Checksum valide"})
                else:
                    results.append({"file": distfile, "status": f"Checksum invalide (attendu: {expected_checksum}, calculé: {computed_checksum})"})
            except Exception as e:
                logger.error(f"Erreur lors de la vérification du fichier {distfile_path} : {str(e)}")
                results.append({"file": distfile, "status": f"Erreur de vérification : {str(e)}"})

        if not results:
            results.append({"message": "Aucun fichier de distribution à vérifier."})
        return results

    @log_operation
    @handle_package_errors
    def depends(self) -> PkgDetails:
        if not self._pkg:
            self.details.error = f"Paquet {self._package_name} non initialisé"
        return self.details

    @log_operation
    @handle_package_errors
    def provides(self) -> PkgDetails:
        if not self._pkg:
            self.details.error = f"Paquet {self._package_name} non initialisé"
            return self.details
        self.details.files = self._pkg.files or ["Aucun fichier trouvé"]
        self.details.pkgname = self._package_name
        return self.details

    @log_operation
    @handle_package_errors
    def revdepends(self) -> PkgDetails:
        if not self._binary or not self._pkg:
            self.details.error = "Non implémenté pour les sources ou paquet non initialisé"
            return self.details
        self.details.files = self._pkgdb.get_reverse_dependencies(self._package_name)
        self.details.pkgname = self._package_name
        return self.details

    @log_operation
    @handle_package_errors
    def outdated(self) -> PkgDetails:
        if not self._binary or not self._pkg:
            self.details.error = "Non implémenté pour les sources ou paquet non initialisé"
            return self.details
        # Placeholder : À implémenter avec core/web/cdnpkg.py pour comparer les versions
        installed_info = self._pkgdb.get_info(self._package_name)
        self.details.version = installed_info.get("version", "Inconnu")
        self.details.comment = "Comparaison avec la version distante non implémentée (nécessite core/web/cdnpkg.py)"
        return self.details

    @log_operation
    @handle_package_errors
    def verify(self) -> PkgDetails:
        if not self._binary or not self._pkg:
            self.details.error = "Non implémenté pour les sources ou paquet non initialisé"
            return self.details
        if not self._binary_file:
            self.details.error = "Fichier binaire non spécifié pour la vérification"
            return self.details
        result = self._pkg.verify(self._binary_file)
        self.details.files = []
        if result["missing"]:
            self.details.files.append("Fichiers manquants:")
            self.details.files.extend(f"  - {f}" for f in result["missing"])
        if result["extra"]:
            self.details.files.append("Fichiers supplémentaires:")
            self.details.files.extend(f"  - {f}" for f in result["extra"])
        if not result["missing"] and not result["extra"]:
            self.details.comment = "Tous les fichiers sont corrects"
        return self.details

    @log_operation
    @handle_package_errors
    def history(self) -> PkgDetails:
        if not self._binary or not self._pkg:
            self.details.error = "Non implémenté pour les sources ou paquet non initialisé"
            return self.details
        log = Path("/var/log/pkg.log")
        if log.exists():
            with log.open() as f:
                self.details.files = [line.strip() for line in f if self._package_name in line][-10:] or ["Aucun historique"]
        else:
            self.details.error = "Journal non trouvé"
        return self.details

    @log_operation
    @handle_package_errors
    def filelist(self) -> PkgDetails:
        return self.provides()

    @log_operation
    @handle_package_errors
    def diff(self, version1: str, version2: str) -> PkgDetails:
        self.details.comment = f"Comparaison entre {version1} et {version2} non implémentée"
        return self.details

    @log_operation
    @handle_package_errors
    def sigcheck(self) -> PkgDetails:
        if not self._binary or not self._pkg:
            self.details.error = "Non implémenté pour les sources ou paquet non initialisé"
            return self.details
        self.details.comment = "Vérification des signatures non implémentée en interne"
        return self.details

    @log_operation
    @handle_package_errors
    def list_patches(self) -> List[str]:
        if self._binary:
            return ["Gestion des patches non implémentée pour les paquets binaires"]
        if not self._pkg_path:
            self._pkg_path = self._find_package_path()
            if not self._pkg_path:
                return [f"Paquet {self._package_name} non trouvé dans /usr/pkgsrc"]
        patches_dir = self._pkg_path / "patches"
        if not patches_dir.exists():
            return ["Aucun patch trouvé"]
        patches = [patch.name for patch in patches_dir.iterdir() if patch.is_file() and patch.name.startswith("patch-")]
        return patches or ["Aucun patch trouvé"]

    @log_operation
    @handle_package_errors
    def diff_patches(self) -> str:
        if self._binary:
            return "Gestion des patches non implémentée pour les paquets binaires"
        if not self._pkg_path:
            self._pkg_path = self._find_package_path()
            if not self._pkg_path:
                return f"Paquet {self._package_name} non trouvé dans /usr/pkgsrc"
        return "Analyse des différences entre patches non implémentée (nécessite deux versions)"

    @log_operation
    @handle_package_errors
    def count_patches(self) -> Dict[str, int]:
        if self._binary:
            return {"Nombre de patches": 0, "Message": "Non implémenté pour les paquets binaires"}
        if not self._pkg_path:
            self._pkg_path = self._find_package_path()
            if not self._pkg_path:
                return {"Nombre de patches": 0, "Message": f"Paquet {self._package_name} non trouvé dans /usr/pkgsrc"}
        patches_dir = self._pkg_path / "patches"
        if not patches_dir.exists():
            return {"Nombre de patches": 0}
        count = sum(1 for patch in patches_dir.iterdir() if patch.is_file() and patch.name.startswith("patch-"))
        return {"Nombre de patches": count}

    @log_operation
    @handle_package_errors
    def patch_info(self) -> Dict[str, str]:
        if self._binary:
            return {"Message": "Gestion des patches non implémentée pour les paquets binaires"}
        if not self._pkg_path:
            self._pkg_path = self._find_package_path()
            if not self._pkg_path:
                return {"Message": f"Paquet {self._package_name} non trouvé dans /usr/pkgsrc"}
        patches_dir = self._pkg_path / "patches"
        if not patches_dir.exists():
            return {"Message": "Aucun patch trouvé"}
        patches = [patch for patch in patches_dir.iterdir() if patch.is_file() and patch.name.startswith("patch-")]
        if not patches:
            return {"Message": "Aucun patch trouvé"}
        info = {}
        for patch in patches:
            size = patch.stat().st_size
            with patch.open() as f:
                first_line = f.readline().strip()
            info[patch.name] = f"Taille: {size} octets, Première ligne: {first_line}"
        return info

    @staticmethod
    @log_operation
    @handle_package_errors
    def check_package_versions(show_all: bool = False, pkgsrc_dir: str = "/usr/pkgsrc") -> List[Dict[str, str]]:
        """
        Compare les versions des packages installés avec celles dans pkgsrc.

        Args:
            show_all (bool): Si True, inclut tous les packages installés, même ceux à jour.
            pkgsrc_dir (str): Chemin vers le répertoire pkgsrc (par défaut: /usr/pkgsrc).

        Returns:
            List[Dict[str, str]]: Liste de dictionnaires contenant les informations sur les packages obsolètes.
        """
        results = []

        # Étape 1 : Lister les packages installés avec PkgDB
        pkg_db = PkgDB()
        installed_packages = {}
        try:
            installed_list = pkg_db.list_installed()
            for pkg in installed_list:
                if '-' not in pkg:
                    continue
                pkg_name, pkg_version = pkg.rsplit('-', 1)
                installed_packages[pkg_name] = pkg_version
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des packages installés : {str(e)}")
            return [{"error": f"Erreur lors de la récupération des packages installés : {str(e)}"}]

        # Étape 2 : Parcourir pkgsrc pour trouver les versions disponibles
        pkgsrc_base = Path(pkgsrc_dir)
        if not pkgsrc_base.exists():
            logger.error(f"Le répertoire {pkgsrc_dir} n'existe pas.")
            return [{"error": f"Le répertoire {pkgsrc_dir} n'existe pas."}]

        for category_dir in pkgsrc_base.iterdir():
            if not category_dir.is_dir():
                continue
            category = category_dir.name
            for pkg_dir in category_dir.iterdir():
                if not pkg_dir.is_dir():
                    continue
                pkg_name = pkg_dir.name
                if pkg_name not in installed_packages:
                    continue

                # Utiliser SourcePackage pour extraire la version
                try:
                    src_pkg = SourcePackage(name=pkg_name, version="Inconnu")
                    src_pkg.fetch_source_info()
                    pkgsrc_version = src_pkg.version()
                    installed_version = installed_packages[pkg_name]

                    # Comparaison simplifiée des versions
                    if pkgsrc_version != installed_version:
                        results.append({
                            "name": pkg_name,
                            "category": category,
                            "installed_version": installed_version,
                            "pkgsrc_version": pkgsrc_version,
                            "status": "Obsolète"
                        })
                    elif show_all:
                        results.append({
                            "name": pkg_name,
                            "category": category,
                            "installed_version": installed_version,
                            "pkgsrc_version": pkgsrc_version,
                            "status": "À jour"
                        })
                except Exception as e:
                    logger.warning(f"Erreur lors de la récupération des informations pour {pkg_name} : {str(e)}")
                    continue

        if not results:
            results.append({"message": "Tous les packages installés sont à jour."})
        return results

    @staticmethod
    @log_operation
    @handle_package_errors
    def filter_installed(results: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Filtre les résultats pour ne garder que les packages installés.

        Args:
            results (Dict[str, List[Dict[str, str]]]): Résultats à filtrer.

        Returns:
            Dict[str, List[Dict[str, str]]]: Résultats filtrés contenant uniquement les packages installés.
        """
        # Lister les packages installés avec PkgDB
        pkg_db = PkgDB()
        try:
            installed_list = pkg_db.list_installed()
            installed_pkgs = {pkg.rsplit('-', 1)[0] for pkg in installed_list if '-' in pkg}
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des packages installés : {str(e)}")
            return {"error": f"Erreur lors de la récupération des packages installés : {str(e)}"}

        filtered = {}
        for key, value in results.items():
            if isinstance(value, PkgDetails) and value.files:
                filtered[key] = PkgDetails(pkgname=value.pkgname)
                filtered[key].files = [
                    pkg for pkg in value.files
                    if pkg.split('/')[-1].rsplit('-', 1)[0] in installed_pkgs
                ] or ["Aucun paquet installé trouvé"]
            else:
                filtered[key] = value
        return filtered
