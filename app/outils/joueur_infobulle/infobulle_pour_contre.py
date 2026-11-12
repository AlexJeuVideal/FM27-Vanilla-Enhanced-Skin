"""Infobulle joueur : le bloc « Rapport du préparateur / du recruteur » remplacé par Niveau + Potentiel en étoiles et
les Pour / Contre en pastilles seulement, comme dans FM24 (survol d'une pastille = son texte).

Réglages des pastilles (tailles, couleurs) : commun\\pastilles_pour_contre.py.
Seul propriétaire de ses modèles : appliquer repart des originaux sauvegardés, retirer les remet.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import pastilles_pour_contre as ppc  # noqa: E402

MARKER = os.path.join(backup.BACKUP_DIR, "infobulle_pour_contre.actif")
MODELES = [ppc.BLOC, ppc.CELLULE_LIBRE, ppc.CELLULE]   # CELLULE : seulement remise d'origine (v1-v14 la réécrivaient)

if __name__ == "__main__":
    ppc.main(sys.argv[1:], MODELES, MARKER, "infobulle Pour / Contre")
