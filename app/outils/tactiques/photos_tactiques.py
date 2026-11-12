"""Photo des joueurs sur le terrain des tactiques (aussi l'écran tactique pendant un match) : photo à gauche du
maillot, par-dessus lui (numéro encore visible), logos de rôle sur les coins de la carte. Cartes FM :
TacticsPositionCombined (vue « Combinée ») et TacticsPositionDetailed (En / Hors possession, formes, compo conseillée).

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
TACTIQUES = dict(photo=44, maillot="dessus", chevauche=13, remonter=6,  # v3 validé en jeu : photo 40, maillot
                 maillot_px=38, logos_coins=-6, logos_haut=-14)                    # FM 34 / 35, chevauche 12
# logos_coins : logos de rôle (mouvement avec / sans ballon) centrés sur les coins supérieurs gauche / droit du
#   rectangle des rôles (px vers l'extérieur ; -8 = moitié d'un logo de 16 px) ; None = place FM.
#   logos_haut : px ajoutés à la hauteur seule (< 0 = plus haut)
#   Derniers enfants de la carte : dessinés par-dessus le rectangle. v7 : le maillot passait sous le logo de droite ;
#   v8 (groupe décalé de -12) : logo de gauche sur le visage.
LOGOS_DESSUS = True           # tactiques : logos de mouvement du rôle (à gauche / à droite) par-dessus la photo
# cartes touchées : (modèle, repère, chemin de la personne, réglages)
#   repère "FMTacticsShirt" = le maillot sous #ShirtAndRoleMovements ; "#Shirt" = l'élément nommé Shirt
CIBLES = [
    ("TacticsPositionCombined", "FMTacticsShirt", "position.Player", TACTIQUES),
    ("TacticsPositionDetailed", "FMTacticsShirt", "position.Player", TACTIQUES),
]
# =====================================================================================================

VERSION = 17  # v2 : photo des tactiques remontée, logos de rôle par-dessus ; v3 : photo sur le maillot, resserrée ;
              # v4 : barre du bas photo + maillot (photo dessus), remontée ; v5 : barre plus grande, centrée, bas alignés ;
              # tactiques un peu plus grandes ; v6 : barre, groupe remonté de 4 px ; v7 : 8 px, resserré (17) ;
              # v8 : tactiques, groupe décalé à gauche (logo de rôle de droite plus sur le maillot) ;
              # v9 : barre, maillot descendu de 3 px (erreur : il dépassait déjà en bas) ; v10 : remonté de 4 px ;
              # v11 : tactiques, plus de décalage du groupe, logo de droite poussé vers l'extérieur ;
              # v12 : barre, maillot -2 (0 trop bas, -4 trop haut) ; v13 : logos sur les coins du rectangle des rôles
              # (rognés) ; v14 : logos dans la carte, sur les coins (validé, un peu trop écartés) ; v15 : -6 ;
              # v16 : et 2 px plus haut (top -8) ; v17 : logo mordait de ~7 px sur le bandeau des rôles (FM 26 : tout
              # au-dessus, ~5 px d'écart) -> top -20
MARKER = os.path.join(backup.BACKUP_DIR, "photos_tactiques.actif")

if __name__ == "__main__":
    mp.CIBLES, mp.MARKER, mp.VERSION, mp.LOGOS_DESSUS = CIBLES, MARKER, VERSION, LOGOS_DESSUS
    mp.NOM = f"{mp.PREFIXE}-v{VERSION}"
    mp.main(sys.argv[1:])
