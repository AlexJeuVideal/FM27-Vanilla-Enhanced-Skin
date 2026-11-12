"""Fiche joueur (et rapports) : listes Pour / Contre de FM27 en pastilles colorées selon la note (comme l'infobulle).

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

MARKER = os.path.join(backup.BACKUP_DIR, "listes_pour_contre.actif")
MODELES = [ppc.LISTE_FM] + list(ppc.LIGNES_RAPPORT)   # + lignes du rapport de l'adjoint (onglet Prestation)

def main(argv):
    ppc.main(argv, MODELES, MARKER, "listes Pour / Contre")


if __name__ == "__main__":
    main(sys.argv[1:])
