"""Points mensuels + valeur au survol sur les courbes financières de FM : vue d'ensemble des Finances (et Accueil),
Projections, tuiles budgets transferts / salaires / recrutement, tuiles Finances du club, revenus. Points discrets
(5 px, opacité 0.6), zone de survol invisible autour de chaque point.

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
EXCLURE = set()   # noms de modèles d'écran à laisser tels quels (ex. {"ClubFinancesSummaryTile_2x2"})
POINTS = [
    dict(modele=mg.POINT, nom=None, taille=8, opacite=None, discret=(5, 0.6),
         zone=(70, 260), trait=None),
]
REPERES = []
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "graphes_finances.actif")

if __name__ == "__main__":
    mg.EXCLURE = EXCLURE
    mg.MARKER, mg.POINTS, mg.REPERES, mg.COURBES = MARKER, POINTS, REPERES, True
    mg.main(sys.argv[1:])
