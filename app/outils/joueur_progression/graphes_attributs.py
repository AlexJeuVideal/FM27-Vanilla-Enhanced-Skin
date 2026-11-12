"""Progression des attributs (fiche joueur) : zone de survol plus grande autour de chaque point de la courbe
(valeur au survol plus facile à attraper). Repères verticaux par mois : essai désactivé (actif=False).

Moteur : commun\\moteur_graphes.py. Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import moteur_graphes as mg  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (voir commun\\moteur_graphes.py pour le sens de chaque champ)
# =====================================================================================================
POINTS = [
    dict(modele="ProgressReportAttributesLineChartGeometry", nom="PointColor", taille=10, opacite=None,
         zone=(40, 40), trait=None),
]
REPERES = [
    dict(modele="AttributesGraphTemplate", nom="AttributeHistoryChart", classe="fm-attribute-history-chart",
         haut=2000, largeur=58, couleur=(1, 1, 1, 0.12), actif=False),
]
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "graphes_attributs.actif")

if __name__ == "__main__":
    mg.MARKER, mg.POINTS, mg.REPERES, mg.COURBES = MARKER, POINTS, REPERES, False
    mg.main(sys.argv[1:])
