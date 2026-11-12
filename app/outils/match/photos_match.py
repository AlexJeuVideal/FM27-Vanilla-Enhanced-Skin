"""Photo des joueurs pendant le match : terrain du match (vue d'ensemble / formations : TacticsMatchPositionFilled,
FormationPositionFilled) et barre du bas (Effectif / remplaçants, un bloc par joueur : SquadOverviewPlayerBlock),
photo + maillot comme dans les tactiques.

Moteur : commun\\moteur_photos.py. Seul propriétaire de ses cartes : appliquer repart des originaux, retirer les
remet. Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import moteur_photos as mp  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
# Réglages par endroit :
#   photo       : taille de la photo en px
#   maillot     : "dessus" = photo par-dessus le maillot (numéro encore visible), "dessous" = maillot sur la photo,
#                 "retire" = photo seule à la place du maillot
#   chevauche   : px de photo et de maillot l'un sur l'autre (0 = côte à côte)
#   remonter    : px de remontée de la photo (décalage visuel seul, la carte ne change pas de taille)
#   decaler     : px de décalage du groupe photo + maillot vers la gauche (< 0) ou la droite (> 0)
MATCH = dict(photo=32, maillot="dessous", chevauche=0, remonter=0)       # terrain du match : validé en jeu (v1)
#   maillot_px  : taille du maillot en px (None = celle de FM)
#   centrer     : groupe photo + maillot centré dans sa zone, bas de la photo aligné sur le bas du maillot
#               (avec centrer, remonter décale tout le groupe photo + maillot)
#   maillot_bas : px de descente (> 0) ou de montée (< 0) du maillot seul, réglé à l'œil
BARRE = dict(photo=46, maillot="dessus", chevauche=17, remonter=8,    # barre du bas (v4 : photo 36, maillot FM
             maillot_px=40, centrer=True, maillot_bas=-2)                           # 32 : trop petits, décentrés ; v5 : collés
                                                                       # au nom)
#   ecart       : (maillot dessous) px entre la photo et le maillot
# tuile Formation du résumé du match (2026-11-05, le joueur : têtes et maillots de 2 voisins se chevauchaient) :
# plus petits, côte à côte avec un petit écart, centrés
RESUME = dict(photo=26, maillot="dessous", chevauche=0, remonter=0, ecart=3, maillot_px=28, centrer=True)
LOGOS_DESSUS = False         # (logos de rôle : tactiques seulement)
# cartes touchées : (modèle, repère, chemin de la personne, réglages)
#   repère "FMTacticsShirt" = le maillot sous #ShirtAndRoleMovements ; "#Shirt" = l'élément nommé Shirt
CIBLES = [
    ("TacticsMatchPositionFilled", "#Shirt", "position.MatchPlayer.Person", MATCH),
    ("FormationPositionFilled", "#Shirt", "Position.MatchPlayer.Person", RESUME),
    ("SquadOverviewPlayerBlock", "#Shirt", "playerinfo.person", BARRE),
]
# =====================================================================================================

VERSION = 18  # v18 : tuile Formation du résumé (RESUME) ; v2 : photo des tactiques remontée, logos de rôle par-dessus ; v3 : photo sur le maillot, resserrée ;
              # v4 : barre du bas photo + maillot (photo dessus), remontée ; v5 : barre plus grande, centrée, bas alignés ;
              # tactiques un peu plus grandes ; v6 : barre, groupe remonté de 4 px ; v7 : 8 px, resserré (17) ;
              # v8 : tactiques, groupe décalé à gauche (logo de rôle de droite plus sur le maillot) ;
              # v9 : barre, maillot descendu de 3 px (erreur : il dépassait déjà en bas) ; v10 : remonté de 4 px ;
              # v11 : tactiques, plus de décalage du groupe, logo de droite poussé vers l'extérieur ;
              # v12 : barre, maillot -2 (0 trop bas, -4 trop haut) ; v13 : logos sur les coins du rectangle des rôles
              # (rognés) ; v14 : logos dans la carte, sur les coins (validé, un peu trop écartés) ; v15 : -6 ;
              # v16 : et 2 px plus haut (top -8) ; v17 : logo mordait de ~7 px sur le bandeau des rôles (FM 26 : tout
              # au-dessus, ~5 px d'écart) -> top -20
MARKER = os.path.join(backup.BACKUP_DIR, "photos_match.actif")

if __name__ == "__main__":
    mp.CIBLES, mp.MARKER, mp.VERSION, mp.LOGOS_DESSUS = CIBLES, MARKER, VERSION, LOGOS_DESSUS
    mp.NOM = f"{mp.PREFIXE}-v{VERSION}"
    mp.main(sys.argv[1:])
