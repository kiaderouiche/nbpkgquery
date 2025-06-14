import json
import os

def get_version()->str:
    """Lit et retourne la version du projet depuis version.json."""
    version_file = os.path.join(os.path.dirname(__file__), "version.json")

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return f"{data.get('version', 'unknown')} (build {data.get('build', 'N/A')}, {data.get('release', 'N/A')})"
    except Exception as e:
        return f"Erreur: Impossible de récupérer la version ({e})"
