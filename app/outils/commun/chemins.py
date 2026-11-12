"""Dossiers des catégories ajoutés au chemin de Python : chaque script trouve les autres (et la boîte à outils de
commun\\) où qu'ils soient rangés. Importé en tête de chaque script (« import chemins »)."""
import os
import sys

OUTILS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# moteur_rust (v1.62) : paquet UnityPy de remplacement, mis en tête du chemin par l'app (PYTHONPATH) seulement s'il
# se charge ; jamais ajouté ici (sinon il passerait pour UnityPy là où le vrai manque)
SANS_CHEMIN = {"moteur_rust"}
for _d in sorted(os.listdir(OUTILS)):
    _p = os.path.join(OUTILS, _d)
    if os.path.isdir(_p) and not _d.startswith(("_", ".")) and _d not in SANS_CHEMIN and _p not in sys.path:
        sys.path.append(_p)
