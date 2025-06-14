import os
from pathlib import Path
import logging
from nbpkg.config.__appconfig__ import (
    PKGSRCDIR, PKG_DBDIR, LOCALBASE, CROSSBASE, DISTDIR, SYSCONFBASE, VARBASE,
    PKGINFODIR, PKGMANDIR, PKGSRCWIP, PKGSRCSE, PKGSRCORG
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.search_pkgsrc = True
        self.search_pkgdb = True

    def validate(self):
        """Valide la configuration."""
        if not self.search_pkgsrc and not self.search_pkgdb:
            raise ValueError("Au moins une source de recherche doit être activée (pkgsrc ou pkgdb).")

# Gestion de la configuration
class ConfigManager:
    """Classe pour gérer la configuration de pkgsrc."""
    DEFAULT_CONFIG = {
        "PKGSRCDIR": PKGSRCDIR,
        "PKG_DBDIR": PKG_DBDIR,
        "LOCALBASE": LOCALBASE,
        "CROSSBASE": CROSSBASE,
        "DISTDIR": DISTDIR,
        "SYSCONFBASE": SYSCONFBASE,
        "VARBASE": VARBASE,
        "PKGINFODIR": PKGINFODIR,
        "PKGMANDIR": PKGMANDIR,
        "PKGSRCWIP": PKGSRCWIP,
        "PKGSRCSE": PKGSRCSE,
        "PKGSRCORG": PKGSRCORG
    }

    def __init__(self):
        self.config = self.load_pkgsrc_config()

    def load_pkgsrc_config(self):
        """
        Charge les variables de configuration depuis /usr/pkg/etc/mk.conf ou /etc/mk.conf.
        Les variables d'environnement ont la priorité.
        """
        config = self.DEFAULT_CONFIG.copy()
        mk_conf_files = [Path("/usr/pkg/etc/mk.conf"), Path("/etc/mk.conf")]

        for mk_conf in mk_conf_files:
            if mk_conf.exists():
                with mk_conf.open() as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        for key in config.keys():
                            if line.startswith(f"{key}="):
                                config[key] = line.split("=", 1)[1].strip()
                                logger.debug(f"{key} trouvé dans {mk_conf}: {config[key]}")
                                break

        for key in config.keys():
            env_value = os.environ.get(key)
            if env_value:
                config[key] = env_value
                logger.debug(f"{key} remplacé par la variable d'environnement: {env_value}")

        return config

    def get(self, key):
        """Récupère une valeur de configuration."""
        return self.config.get(key)