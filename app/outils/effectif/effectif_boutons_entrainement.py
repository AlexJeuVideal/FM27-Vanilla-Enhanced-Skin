"""Écran Effectif (liste des joueurs) : boutons FM normaux « Entraînement », « Entraînement individuel » et
« Programme des rencontres » à droite du menu des vues (« Infos générales »…), pour l'équipe affichée, seulement pour
les équipes du club du joueur (team.Club.UniqueId == human.Club.UniqueId). Clic = calendrier d'entraînement /
entraînement individuel / rencontres de l'équipe.

Modèle : TeamSquadBlock (seul propriétaire : appliquer repart de l'original sauvegardé, retirer le remet).
Code commun (événement « ouvrir un écran », bouton « Aujourd'hui » recopié) : entrainement\\entrainement_equipes.py.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import entrainement_equipes as ee  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION de entrainement_equipes.py)
# =====================================================================================================
# un seul bouton FM normal (style « Aujourd'hui »), celui de l'équipe affichée, jamais surligné
EFFECTIF = {"actif": True, "texte": 1378, "descendre": 0, "marge": 0}   # 1378 = traduction FM « Training »
# 2e bouton à droite de « Entraînement » -> entraînement individuel de l'équipe affichée
EFFECTIF_INDIVIDUEL = {"actif": True, "texte": 8962, "ecart": 8}   # 8962 = traduction FM « Individual Training »
# 3e bouton -> programme des rencontres de l'équipe affichée (calendrier, onglet Rencontres)
EFFECTIF_PROGRAMME = {"actif": True, "texte": 8487, "ecart": 8}    # 8487 = traduction FM « Fixture Schedule »
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "effectif_boutons_entrainement.actif")

if __name__ == "__main__":
    ee.EMPLACEMENTS["effectif"], ee.EFFECTIF_INDIVIDUEL = EFFECTIF, EFFECTIF_INDIVIDUEL
    ee.EFFECTIF_PROGRAMME = EFFECTIF_PROGRAMME
    ee.MODELES_SCRIPT, ee.MARKER = [ee.EFFECTIF], MARKER
    ee.main(sys.argv[1:])
