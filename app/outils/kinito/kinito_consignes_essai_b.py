"""[AJOUT KINITO] 26.13 — Tactiques > Consignes d'équipe : l'écran « Terrain » façon FM24, avec et sans le ballon,
derrière un bouton « Cartes / Terrain ». Né « essai 2 » (26.14) d'une autre disposition de kinito_consignes_essai ;
GARDÉ par Kinito le 12/11/2026 (v5 validée en jeu avant-match, texte « Plus grand » compris, avec et sans le ballon) ;
kinito_consignes_essai est sorti du menu, ce script passe donc au n° 13 du menu 26.

Tout le reste vient de kinito_consignes_essai (boutons de FM, cases, infobulles, langues, construction, retrait) : ce
script l'IMPORTE et ne remplace que la disposition des deux vues ; kinito_consignes_essai.py doit donc rester dans
outils\\kinito\\. Les deux posent leurs éléments au même endroit du même bloc : appliquer celui-ci retire l'ancienne
disposition et efface sa marque.

Avec le ballon : les noms des phases de FM (Relance, Avancée, 30 derniers mètres) TOUT EN HAUT des trois colonnes,
puis Caract. direct des passes, Transition offensive et Style de centres, les terrains (celui des 30 derniers mètres
a Liberté créative dans sa bande du bas), et Rythme, Perdre du temps et CPA en bas.
Sans le ballon (consignes de Kinito) :
- colonnes 42,5 / 15 / 42,5 % (chacune garde sa largeur où qu'elle soit) ;
- à gauche et à droite : le terrain aux proportions d'un vrai terrain (105 × 68 : hauteur = 1,544 × largeur, tenue
  par un « padding » en % de la largeur du BLOC, comme en v2 / v5 ; lignes aux vraies mesures), puis sa tuile
  (Comportement de la ligne, En taclant), qui prend toute la hauteur qui reste ;
- au milieu : le déclenchement du pressing sur du gazon sans marquage (bandes d'herbe alignées sur celles des
  terrains), son nom en titre en haut, ses 5 crans en boutons de FM (icônes seules, nom en infobulle), 3/5 de la
  hauteur ; puis la tuile Transition défensive (contre-pressing au-dessus de regroupement), 2/5 ; les titres de cette
  colonne étroite à la taille maximale de leur langue (v9 : TAILLES_DECLENCH, TAILLES_TRANSITION) ;
- tuiles : titre en haut, cases qui remplissent la place qui reste ; les trois colonnes finissent en bas du bloc.
v6 (Kinito, 12/10) : la vue « sans le ballon » se personnalise, avec l'icône d'échange des séances (26.6, deux flèches
en cercle de FM) et le même fonctionnement en deux clics :
- COLONNES : une icône à côté de chaque titre ; 1er clic, la colonne est retenue (icône jaune, anneau blanc de FM
  autour d'elle) ; 2e clic sur une AUTRE colonne : les deux échangent leur place (n'importe quelle paire, choix de
  Kinito) ; 2e clic sur la même : annulé ;
- HAUT / BAS : une icône en haut à droite du terrain et de la tuile de chaque colonne (au milieu : à côté de leur
  titre) ; 1er clic, l'élément est retenu ; 2e clic sur l'autre élément de SA colonne : ils échangent haut et bas ;
- une icône qui ne peut pas répondre est grisée (un élément retenu : les icônes des colonnes et des autres colonnes) ;
- l'ordre choisi est GARDÉ d'une ouverture à l'autre : variables « Persistent » de FM, le mécanisme de FM pour
  « Avec / Sans le ballon » (choix de Kinito) ; ce qui est retenu (1er clic) ne l'est pas.
v7 (Kinito, 12/10, « c'est juste parfait » sur la v6, vue en jeu et gardée d'une ouverture à l'autre) : la même chose
« avec le ballon » :
- COLONNES (Relance, Avancée, 30 derniers mètres, avec leurs tuiles) : l'icône à côté du nom de la phase, deux clics,
  n'importe quelle paire ; mêmes largeurs et mêmes écarts de 10 px qu'avant ;
- DANS UNE COLONNE, ses trois éléments (tuile du haut, terrain, tuile du bas) se rangent comme on veut (Kinito :
  « terrain en haut, au milieu ou en bas ; échanger chaque tuile d'une colonne ») : icône en haut à droite de chacun,
  deux clics sur deux éléments de la même colonne -> ils échangent leur place (les 6 rangements possibles) ;
- les tuiles ont une hauteur FIXE (H_TUILE), celle qu'elles ont déjà : mesurée sur les captures de Kinito, 94 px
  réels, la même en texte Petit et Plus grand (leurs titres ne grandissent pas) ; le terrain prend le reste. Une
  colonne = deux calques : celui des tuiles (une cale qui grandit avant, entre ou après les deux tuiles, et les deux
  tuiles dans une paire normale ou inversée) et celui du terrain (cales de hauteur fixe au-dessus / au-dessous) ;
- ordre des colonnes, place du terrain et ordre des tuiles gardés (« Persistent »), à part de « sans le ballon ».
v8 (Kinito, 12/10) : terrain Relance sans fond derrière « Réception des passes » (bandes d'herbe sur tout le terrain),
« Équilibrées » à droite et « RELANCER VERS » à gauche du gardien (NOS traductions) ; Rythme et Perdre du temps
estompés comme les autres consignes, la largeur du jeu offensif et le déclenchement du pressing aussi ; Progression : axe et côtés
s'estompent l'un l'autre.
v9 (Kinito, 12/10) : relance courte du gardien en une seule case « oui », au centre (un clic l'applique, un 2e remet
« non ») ; « Cartes / Terrain » à l'allure de « Vue d'ensemble », l'autre vue assombrie ; les trois titres de colonne
pareils, le texte centré sur sa colonne ; « Déclench. pressing » et « Transition défensive » centrés, icône dans le
coin, à la taille maximale de leur langue.
v10 (Kinito, 12/10, captures de la v9) : ces deux titres passent SOUS l'icône du coin, sur toute la largeur de la tuile,
à la taille maximale de leur langue (recalculée, plafond 13) ; les tuiles gardent leur hauteur, les écarts entre les
boutons sont rognés pour rattraper la place du titre. Un bouton « Partir de zéro » dans l'en-tête (au centre de
l'espace libre entre « Vue d'ensemble » et « Cartes », choix de Kinito), dans les deux vues : il choisit le style de
FM « Partir de zéro » (valeur 10 de Tactic.TacticalStyle), après une fenêtre « êtes-vous sûr ? » faite des morceaux
de la fenêtre de confirmation de FM (GenericModalDialog), avec sa case « Ne plus afficher ce message. » (gardée).
v11 (Kinito, 13/10, v10 vue en jeu, « le bouton fonctionne ») : colonne du milieu seulement, l'icône d'échange de ses
deux tuiles en haut au milieu (plus dans le coin), le titre toujours dessous.
v12 (Kinito, 15/10, capture de la v11 en jeu) : l'en-tête. « Partir de zéro », « Terrain » et « Tuiles » ont la hauteur
de « Vue d'ensemble » (comme son menu de FM : 25 de haut à l'intérieur, la bordure de 1 autour) et perdent les marges
cachées du bouton de FM ; « Partir de zéro » juste après « Vue d'ensemble » (5 px) ; « Terrain » d'abord, puis
« Tuiles » (l'ancien « Cartes », NOS traductions), à 5 px l'un de l'autre, calés à droite : un mot plus long pousse
vers la gauche, rien ne se chevauche. La vue choisie (Terrain ou Tuiles) est gardée d'une ouverture à l'autre
(variable « Persistent » de FM, comme l'ordre des colonnes) ; la toute première fois : Terrain.
v13 (Kinito, 28/10, capture de la v12) : sans le ballon, chaque consigne montre toutes ses options (standard compris),
celles qui ne sont pas choisies toujours estompées ; « Équilibré » écrit pour le piège et les centres ; relance courte
« Non » + « Oui » ; plus d'infobulle sur les bandes de la hauteur du pressing et de la ligne défensive.
v14 (Kinito, 28/10, même capture) : la même chose AVEC le ballon, sans toucher à la largeur des trois colonnes :
réception des passes, sorties de but, relances GB (vitesse), transition offensive, stratégie d'attaques placées et
liberté créative en trois cases (standard au milieu, icône de FM) ; patience, tirs de loin et dribbles avec un
« Standard » écrit sous leurs cases, rétrécies d'autant ; la progression avec un « Équilibré » écrit sous ses trois
cases (resserrées, leur nom plus près du bas) ; la patience et la stratégie d'attaques placées ont leur titre ;
toutes les options qui ne sont pas choisies estompées, même quand l'option par défaut l'est (Rythme, Perdre du temps,
largeur, style de centres, CPA, caract. direct des passes, progression, zones « Relancer vers »).
v15 (Kinito, 28/10, v14 installée) : partout, un 2e clic sur l'option choisie remet l'option neutre de la consigne
(« standard », « équilibré » : celle que FM nomme …None / …Standard), comme le piège du pressing (bouton_b : cases à
bascule) ; seule la hauteur du pressing, qui n'en a pas, n'a pas ce retour. « Équilibré » du pressing sur centres à
l'allure d'« Empêcher de centrer » (même taille, capitales).
v16 (Kinito, 28/10, v15 installée) : plus de trait blanc pour la cage sur les cinq terrains (les autres traits
restent) ; chaque titre de consigne sur un terrain centré en hauteur entre ce qui est au-dessus (le bord du terrain,
le « Standard » ou l'« Équilibré » du dessus) et ses cases ; « Équilibré » du piège à la taille et à l'allure de celui
des centres (les cases du piège remontées pour lui faire la place).
v17 (Kinito, 28/10, capture de la v16) : le piège n'a plus que sa rangée de flèches du haut ; son « Équilibré » (même
case) centré entre ses cartes et la ligne médiane ; le titre des centres dans sa moitié de terrain.
v18 (Kinito, 28/10, v17 vue en jeu : « tout le reste est bon ») : le déclenchement du pressing estompe aussi ses crans
non choisis quand le standard l'est, comme toutes les autres consignes.
Comment (rien n'est recopié en double, aucun bouton de consigne n'est touché) : chaque colonne est posée dans son
propre calque, sur toute la largeur du bloc ; des cales vides (une par ordre possible, masquées par la classe
« hidden-item » de FM sauf celle de l'ordre en cours) la mettent à sa place ; haut / bas = la colonne en
« column-direction-normal » ou « interest-cell-stepper » (colonne inversée), classes de FM qui ne règlent QUE ça. Les
classes sont posées et RETIRÉES par la fonction de FM BindIntComparisonToAOrBUssClass (celle qui allume déjà les
boutons Cartes / Terrain) : SIStyleSetter.SetClassStyle retire la classe d'avant (mesuré dans le code du jeu).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai_b.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai_b.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_consignes_essai_b.py etat
"""
import copy
import json
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kinito_consignes_essai as base  # noqa: E402
import kinito_consignes_ecran as ecran37  # noqa: E402  (v54 : l'écran plein de la vue Terrain)
from kinito_consignes_essai import (pc, cadre_css, COUL, PHASES, TITRES_SANS, TITRES_SANS_LANGUES,  # noqa: E402
                                    PLAFOND_ICONE, BASCULES, CRANS, CASE, BANDE_BAS, TITRE_BAS, HAUT_BANDE,
                                    TRAITS_FINITION, degrade, tuile, piege, avancee, case_abs,
                                    champ_terrain, langue, backup, copier, liste, PLACES, recaler_parent,
                                    TEXTE_ZONES, TRAITS_RELANCE, ZONES_GB, HAUT_TUILE, BANDE, DEFAUTS, calque_selon,
                                    ligne_consigne, Y_PRESSING, Y_LIGNE, BANDES_PRESSING, BANDES_LIGNE)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402

base.sm.PROPRIETES.setdefault("tint", (196610, 4))   # v22 : -unity-background-image-tint-color (comme 26.14)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
TUILES_HAUT = (1, 3, 26)   # avec le ballon : au-dessus des terrains : Caract. direct des passes, Transition offensive,
#                            Style de centres (v3, Kinito : échangé avec Liberté créative, qui passe dans la bande du
#                            bas du terrain des 30 derniers mètres)
TUILES_BAS = (21, 7, 6)    # en dessous : Rythme, Perdre du temps, Obtenir des CPA
BAS_FINITION = 5           # v3 : la consigne de la bande du bas du terrain des 30 derniers mètres (Liberté créative)
LARGEURS_SANS = (42.5, 15.0, 42.5)   # sans le ballon : largeur des colonnes, en parts (v4, Kinito ; v2 / v3 : 40 / 20 / 40)
ECART = 1.1                # écart entre colonnes, en % de la largeur du bloc
RAPPORT_TERRAIN = 105 / 68   # vrai terrain : longueur / largeur
HAUT_TERRAINS = RAPPORT_TERRAIN * LARGEURS_SANS[0] / sum(LARGEURS_SANS) * (100 - 2 * ECART)   # v5 (comme la v2) :
#                            hauteur de la rangée des terrains en % de la largeur du BLOC (= 1,544 × leur largeur)
PARTS_MILIEU = (61.2, 38.8)   # colonne du milieu : déclenchement du pressing / transition défensive (v3 : 3 / 2, Kinito).
#                            v13 (Kinito : « ajuste la hauteur des deux blocs pour rendre harmonieux transition déf avec
#                            les 3 boutons ») : les boutons des deux tuiles à la même hauteur. Mesuré sur sa capture de
#                            la v12 (1920 × 1080, px réels) : colonne 740 = déclenchement 439 + écart 11 + transition 290 ;
#                            hors boutons, déclenchement 84 (titre 48, 4 écarts de 7, bas 8), transition 66 avec 3
#                            boutons (titre 49, 2 écarts de 6, bas 5) ; 84 + 5 h + 66 + 3 h = 729 -> h = 72,4 ->
#                            445,9 / 283,1 = 61,2 / 38,8 % (les deux ont une base de 0 : la place se partage ainsi)
CRANS_DECLENCH = (4, 3, 2, 1, 0)   # de haut en bas : beaucoup plus souvent … beaucoup moins souvent (comme 26.13)
REMPLI_TUILES_SANS = 0.72  # v2 : part de sa case que prend le dessin d'une icône des tuiles du bas (26.13 : 0,86 ;
#                            Kinito : de l'air autour des icônes)
# v3 : bande d'herbe du gazon du milieu = celle des terrains (10 % de la hauteur de leur herbe), comptée sur la largeur
# de l'herbe du milieu (un « padding » en % se compte sur la largeur). Herbe d'un terrain : 1,544 × largeur de sa
# colonne − 2 (bords du cadre) ; colonnes dans le rapport k = 42,5 / 15 ; herbe du milieu : largeur de sa colonne − 2.
# D'où bande = 10 × 1,544 × k % de la largeur de l'herbe du milieu, + 0,2 × (1,544 × k − 1) px (v4 : posés en marge
# entre les bandes ; sans eux, les bandes dérivaient de 0,7 px chacune)
_K = LARGEURS_SANS[0] / LARGEURS_SANS[1]
BANDE_HERBE = 10 * RAPPORT_TERRAIN * _K
MARGE_BANDE = 0.2 * (RAPPORT_TERRAIN * _K - 1)
NB_BANDES = 24             # assez pour couvrir la colonne (la suite est coupée par le cadre)
# v9 (Kinito, 12/10) : les titres de colonne sont tous trois en thematic-sm (taille du texte de FM), le texte centré sur
# sa colonne (v6 à v8 : celui du milieu en 9 px fixes, centré avec son icône).
# v10 (Kinito, 12/10, « il y a largement la place ») : « Déclench. pressing » et « Transition défensive » (noms de FM)
# SOUS l'icône du coin, sur toute la largeur de la tuile, à la taille MAXIMALE qui tient, langue par langue (choix de
# Kinito, v9) : place = 127 px réels (mesuré sur la capture v9 de Kinito : colonne de 135 px bord à bord, x = 411 à 545 ;
# moins les deux bords et 2 px d'air de chaque côté) ; noms de FM lus dans data\game_simulation\languages.fmf (19
# langues, outils-analyse\langues_toutes.py) ; largeur calculée avec les polices du jeu en capitales (ABC Social
# Condensed, gras +5,6 % ; grec, cyrillique, arabe, chinois, japonais, coréen : polices de secours de FM, Noto) puis
# CORRIGÉE par la mesure : sur la capture, « DÉCLENCH. PRESSING » à 8,0 fait 69 px (calcul : 81,9) et « TRANSITION
# DÉFENSIVE » à 7,4 fait 66 px (calcul : 82,4) : le calcul surestime ; on garde le rapport le plus prudent (0,8425)
# pour ABC Social Condensed ; polices de secours : calcul brut (pas mesurées). Arrondi vers le bas, plafond 13 (titres
# des autres tuiles) ; « Transition défensive » a deux textes dans le fichier : le plus long. Ces titres ne suivent pas
# la taille du texte de FM (mesuré : les titres thematic-xs des tuiles font la même largeur en Petit et en Plus grand).
# v9 : place 82,5 px (titre à côté de l'icône) ; français 8,0 / 7,4.
TAILLES_DECLENCH = [
    ("english", 13.0), ("english (us)", 13.0), ("french", 13.0), ("german", 13.0), ("italian", 11.9),
    ("spanish", 13.0), ("spanish (latam)", 13.0), ("portuguese", 13.0), ("portuguese (bra)", 13.0), ("dutch", 13.0),
    ("danish", 13.0), ("norwegian", 13.0), ("swedish", 13.0), ("polish", 12.9), ("russian", 9.5), ("turkish", 13.0),
    ("greek", 8.9), ("indonesian", 13.0), ("japanese", 13.0), ("korean", 13.0), ("chinese", 13.0),
    ("chinese (traditional)", 13.0), ("arabic", 13.0)]
DEFAUT_DECLENCH = 8.9      # langue non prévue (tchèque, thaï…) : la plus petite
TAILLES_TRANSITION = [
    ("english", 13.0), ("english (us)", 13.0), ("french", 13.0), ("german", 8.9), ("italian", 13.0),
    ("spanish", 13.0), ("spanish (latam)", 13.0), ("portuguese", 13.0), ("portuguese (bra)", 13.0), ("dutch", 11.1),
    ("danish", 13.0), ("norwegian", 13.0), ("swedish", 10.7), ("polish", 12.7), ("russian", 6.6), ("turkish", 13.0),
    ("greek", 9.6), ("indonesian", 13.0), ("japanese", 7.0), ("korean", 13.0), ("chinese", 13.0),
    ("chinese (traditional)", 13.0), ("arabic", 11.0)]
DEFAUT_TRANSITION = 6.6
HAUT_TITRE_MILIEU = 23     # v10 : la ligne de ces titres commence sous l'icône du coin, à 23 du bord extérieur de la
#                            tuile : l'icône (absolue, top COIN) finit à COIN + ICONE = 22 de ce bord, + 1 d'air.
#                            Mesuré sur la capture v9 : le dessin de l'icône commence 10 px réels sous le bord extérieur
#                            dans les DEUX tuiles (déclenchement : cadre à bord ; transition : boîte sans bord) ; le
#                            « top » d'un élément absolu se compte donc depuis le bord extérieur
DEBORD_TITRE = 6           # v10 : la ligne du titre déborde de 6 de chaque côté sur la marge intérieure (8) de la tuile :
#                            il reste 2 d'air jusqu'au bord ; titre centré sur toute la largeur
ECART_BOUTONS_MILIEU = 2   # v10 : écart entre les boutons des deux tuiles du milieu (v9 : 5 pour le déclenchement, 6 pour
#                            la transition) : rattrape la ligne du titre (Kinito : « on rogne dans les marges »)
BAS_DECLENCH = 6           # v10 : marge intérieure du bas du déclenchement (v9 : 8)
BAS_TRANSITION = 2         # v10 : marge intérieure du bas de la tuile Transition défensive (v9 : 6)
RELANCE_COURTE = (26, 5.5, 48, 14.5)   # v9 : la case « oui » de la relance courte du gardien, seule, au centre de la
#                            largeur (Kinito) : x, y, largeur, hauteur en % du terrain ; un peu plus grande que les deux
#                            cases d'avant (45,5 × 13 % : + 2,5 % ≈ + 9,5 px de large, + 1,5 % ≈ + 9 px de haut)
# v13 (Kinito, 28/10, capture de la v12) : « sans le ballon », chaque consigne montre TOUTES ses options, celles qui ne
# sont pas choisies toujours estompées (option(estompe=True), plus de case à bascule) :
TUILES_3 = {12: (0, 1, 2),   # En taclant : « Ne vous jetez pas » à gauche, « Standard » (icône de FM), « Engagez-vous
            #                  plus » à droite (v26 à v12 : Engagez-vous plus à gauche, Ne vous jetez pas à droite)
            15: (2, 1, 0),   # Comportement de la ligne : rester plus bas (DropOff) à gauche, « équilibré » (icône de
            #                  FM), rester plus haut (HoldLine) à droite (v12 : plus haut à gauche, plus bas à droite)
            11: (2, 1, 0)}   # Transition défensive, de haut en bas : contre-pressing, « Standard » (icône de FM),
#                              regroupement (v12 : contre-pressing au-dessus du regroupement)
RELANCE_COURTE_2 = {0: (8, 5.5, 40, 14.5),    # v13 : « Non » (option par défaut de FM) à gauche, « Oui » à droite, même
                    1: (52, 5.5, 40, 14.5)}   # hauteur que la case seule de la v9 ; 40 % chacune : l'icône garde sa
#                            taille (case de 151 × 85 px réels, au rapport de la toile des icônes de FM, 124 × 72)
EQUILIBRE_PIEGE = (29, 34.7, 42, 11)   # v13 : « Équilibré » (texte) sous « Attirer vers l'axe », au-dessus du milieu
#                            de terrain (50 %) ; v16 (Kinito : « grossis-le, rends son intégration harmonieuse ») : la
#                            taille et l'allure de celui des centres (EQUILIBRE_CENTRES, TEXTE_EMPECHER, capitales), en
#                            miroir de part et d'autre de la ligne médiane (v13 à v15 : 30 / 41 / 40 / 7,5, label-sm
#                            TEXTE_ZONES) ; v17 (Kinito : « vire les flèches du bas, place mieux Équilibré ») : même case,
#                            centrée entre le bas des cartes (31 %, 3 px de marge) et la ligne médiane (50 %) : 35 % moins
#                            les 1,5 px de cette marge (≈ 0,3 %) ; v16 : à 38 %
PIEGE_CASES = (13, 18)     # v16 : haut et hauteur des trois cases du piège (v13 à v15 : 13 / 22) : remontées pour faire la
#                            place d'« Équilibré » ; leurs icônes ne rapetissent pas (elles suivent la largeur des cases)
PIEGE_FLECHES = (9,)       # v17 (Kinito) : la seule rangée de flèches du piège, au-dessus de ces cases (v16 : 9 et 35
#                            au-dessous ; v13 à v15 : 9 / 39)
CENTRES_FLECHES = 57.5     # la rangée de flèches du pressing sur centres (comme 26.13)
HALO_FLECHE = 5            # px : le halo d'une flèche dépasse de 5 au-dessus de sa ligne (fleche() de 26.13)
EQUILIBRE_CENTRES = (29, 61, 42, 11)   # v13 : « Équilibré » du pressing sur centres, même allure, à la place de son icône
TEXTE_EMPECHER = 17        # v13 : « Empêcher de centrer » (écrit à la verticale sur les côtés) : 11 avant. Mesuré sur la
#                            capture de la v12 : à 11, « EMPÊCHER DE CENTRER » fait 118 px réels pour une case de 209 px de
#                            haut ; à 17 : ~182 px, toute la hauteur (Kinito : « utilise toute la hauteur de la case »)
LARGEUR_EMPECHER = 277     # v13 : la boîte du texte (tournée d'un quart de tour) en % de la LARGEUR de sa case (une
#                            largeur en % se compte sur la largeur) : case 69 × 203 px réels à l'intérieur du bouton
#                            (mesurés), 94 % de sa hauteur = 191 px = 277 % de 69 ; un texte plus long (polonais, grec :
#                            jusqu'à 35 lettres) passe sur deux lignes au lieu de déborder
HAUT_EMPECHER = 54         # v13 : hauteur de cette boîte (avant le quart de tour) : deux lignes à 17, moins que la case (60)
# v6 : la personnalisation (Kinito, 12/10)
ORDRES = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]   # place 0, 1, 2 -> n° de colonne (0 =
#                            Hauteur & bloc défensif, 1 = Intensité & transitions, 2 = Duels & zones d'intervention)
V_ORDRE = "kinitoordre"    # n° de l'ordre en cours (ORDRES) : persistant
V_HB = ("kinitohb0", "kinitohb1", "kinitohb2")   # 1 = la colonne a son haut et son bas échangés : persistants
V_COL = "kinitoechcol"     # colonne retenue (1er clic) : 0 aucune, 1 + n° de colonne
V_ELT = "kinitoechelt"     # élément retenu : 0 aucun, 1 + 2 × n° de colonne + (0 : terrain / déclenchement ; 1 : tuile)
V_PHASE24 = "kinitophase24"   # v19 : phase ouverte de la vue FM24 : 0 avec le ballon, 1 en transition, 2 sans ; persistante
CLE_PERSISTANCE = "kinito-consignes-sans"   # notre clé (FM : {teaminstructionstab-bool}{inpossession})
ICONE_ECHANGE = "game-concepts-transfer_small"   # l'icône des séances (26.6) : deux flèches en cercle de FM, 16 x 16
CLASSE_JAUNE = "injury-severity-image-colour-minor"   # la teinte jaune de FM (icône de ce qui est retenu, comme 26.6)
BOUTON_NU = "buttons-controls-pc-default--active-false"   # le contrôle de FM nu (celui de la poubelle des contrats)
SOURCE_BOUTON = ("ContractNegotiationAddOnItem", "buttons-controls-pc-default")   # le bouton-icône de 26.6
SOURCE_ANNEAU = ("Training_TrainingSession_Any_Flex_Edit_Session", "SelectionRing")   # l'anneau blanc de 26.6
CLASSE_ANNEAU = "calendar-training-session-selected"   # la classe de FM qui montre l'anneau (règle « > » de FM)
CLASSE_CACHEE = "hidden-item"              # FM : display none, et rien d'autre
CLASSES_HB = ("column-direction-normal", "interest-cell-stepper")   # FM : flex-direction column / column-reverse, seuls
GUID_CLASSE = "140747f179a528b4b9e2447e9eb7122f"   # BindIntComparisonToAOrBUssClass (classe A si égal, sinon B)
ICONE = 16                 # px, place occupée par l'icône (comme 26.6)
ZONE_CLIC = (22, 24)       # px, zone cliquable autour d'elle (26.6 v3) ; marges négatives : la place reste 16 x 16
DEBORD = {"margin-left": -4, "margin-right": -2, "margin-top": -4, "margin-bottom": -4}
GRISE = 0.30               # opacité d'une icône qui ne peut pas répondre
COIN = 6                   # px, l'icône d'un terrain ou d'une tuile de côté : à 6 px du haut et de la droite
# v7 : « avec le ballon »
H_TUILE = 83               # px (unités de l'interface) : hauteur fixe des tuiles « avec le ballon ». Mesuré sur la capture
#                            de Kinito (Plus grand, 12/10) : 94 px réels (bords à y = 329 / 422 et 971 / 1064, dans les
#                            trois colonnes) = 82,25 unités (1920 px pour 1680) ; la même hauteur en Petit (leurs titres
#                            ne grandissent pas : « Caract. direct des passes » 153 px dans les deux) ; 83 pour ne rien rogner
ECART_AVEC = 10            # px, écart entre les colonnes « avec le ballon » (comme avant)
ECART_TUILE = 8            # px, écart entre une tuile et le terrain ou l'autre tuile (comme avant)
MIN_TERRAIN_AVEC = 280     # px, hauteur minimale d'un terrain (comme la rangée des terrains avant)
V_AORDRE = "kinitoaordre"  # ordre des colonnes « avec » (ORDRES) : persistant
V_APOS = ("kinitoapos0", "kinitoapos1", "kinitoapos2")   # place du terrain dans sa colonne : 0 haut, 1 milieu, 2 bas
V_AREV = ("kinitoarev0", "kinitoarev1", "kinitoarev2")   # 1 = la tuile du bas d'origine passe avant celle du haut
V_ACOL = "kinitoavcol"     # colonne retenue (1er clic) : 0 aucune, 1 + n° de colonne
V_AECOL = "kinitoavecol"   # colonne de l'élément retenu : 0 aucun, 1 + n° de colonne
V_AEELT = "kinitoaveelt"   # élément retenu dans cette colonne : 1 tuile du haut d'origine, 2 terrain, 3 tuile du bas
# v8 (Kinito, 12/10, v7 vue en jeu : « tout a l'air de fonctionner »)
# (v8 à v13 : CRANS_GRISES = Rythme et Perdre du temps estompés seulement quand une autre option que celle par défaut
#  était choisie ; v14 : toutes les consignes « avec le ballon » estompées comme ci-dessous)
# v15 (Kinito, 28/10, v14 installée) : un 2e clic sur l'option choisie remet l'option neutre de la consigne (« standard »,
# « équilibré » : celle que FM nomme …None ou …Standard dans ses données, DEFAUTS ; relevé releve-28-consignes.txt),
# comme le piège du pressing : toutes les autres options en cases à bascule (bouton_b). Sauf :
SANS_RETOUR = {8}   # Hauteur du pressing : FM ne lui donne pas d'option neutre (LineOfEngagementLow / Mid / High)
# (la progression et les courses de soutien le faisaient déjà : un clic sur un côté allumé le retire)
# v14 (Kinito, 28/10, capture de la v12) : « avec le ballon » aussi, chaque consigne montre TOUTES ses options, celles
# qui ne sont pas choisies toujours estompées (option(estompe=True)), même quand l'option par défaut est choisie (v8 à
# v13 : estompées seulement quand une autre l'était) ; plus de case à bascule (v15 : revenues). Les deux côtés +
# l'option par défaut au milieu, avec l'icône « standard » de FM (vérifié dans ses données : place 1 de chacune) :
TROIS_AVEC = {20: (0, 1, 2),   # Réception des passes : dans les pieds, standard, dans les espaces
              29: (0, 1, 2),   # Sorties de but : courtes, mixtes, longues
              17: (0, 1, 2),   # Relances GB (vitesse) : ralentir, équilibrées, rapides
              3: (0, 1, 2),    # Transition offensive : rester en place, standard, contre-attaque (BASCULES[3])
              24: (0, 1, 2),   # Stratégie d'attaques placées : gérer le pressing, standard, contourner le pressing
              5: (0, 1, 2)}    # Liberté créative : plus disciplinés, équilibrée, plus d'expression
PROGRESSION_B = (38.5, 27.0)   # v14 : haut et hauteur des cases de la progression, en % du terrain Avancée (26.13 :
#                            40,5 / 36) : resserrée pour faire la place de son « Équilibré » écrit (dessous, STANDARD_B :
#                            65,5 à 73) et du titre de la stratégie ; v16 : leur titre est centré dans l'écart au-dessus
#                            (titre_entre ; v14 / v15 : à 34 %)
TEXTE_PROGRESSION_B = 0.24   # v14 (Kinito : « rogne la marge au-dessus de Gauche, Droite et Axiale ») : part du bas de
#                            ces cases pour leur nom (26.13 : 0,30, nom centré dedans) ; le schéma : 27 × 0,76 = 20,5 %
#                            de la hauteur du terrain (v12 : 36 × 0,70 = 25,2 %)
STRATEGIE_B = (80.0, 20.0)     # v14 : haut et hauteur des trois cases de la stratégie d'attaques placées (26.13 :
#                            80 / 20, deux cases) ; son titre (26.13 : aucun) centré au-dessus (v16 ; v14 / v15 : à 73,5 %)
# v14 : le terrain des 30 derniers mètres, de haut en bas (% du terrain) : chaque consigne a son titre (Patience aussi),
# ses cases, et un bouton « Standard » écrit dessous (option de FM, à l'allure d'« Équilibrées » des relances du gardien)
ECART_TITRE_B = 6.5        # du haut d'un titre au haut de ses cases (26.13 : 6,5 pour Tirs de loin et Dribbles) ; v16 :
#                            ces « titres » ne servent plus qu'à placer les cases (inchangées), le texte du titre est centré
#                            dans l'écart entre le bord du terrain ou le « Standard » du dessus et ses cases (titre_entre)
STANDARD_B = (32, 36, 7.5)   # x, largeur, hauteur d'un bouton « Standard » écrit, centré sous les cases de sa consigne
PATIENCE_B = (0.6, 18.0)   # titre (nouveau), hauteur de la case « jouer dans la surface » (7,1 à 25,1 ; 26.13 : 0 à
#                            30, sans titre) ; « Centrer de loin » sur les flancs, du haut de cette case à 56 % (26.13 :
#                            6 à 56) ; son « Standard » de 25,1 à 32,6
ACTIONS_B = {27: (33.0, 16.5),   # Tirs de loin : titre, hauteur des cases (39,5 à 56, « Standard » à 63,5 ; 26.13 :
             #                     titre à 30,6, cases de 26)
             19: (64.0, 21.0)}   # Dribbles : titre, hauteur des cases (70,5 à 91,5, « Standard » à 99 ; 26.13 : titre à
#                                  62,8, cases de 30)
ARC_FINITION = 32.6        # v14 : l'arc de la surface sous le « Standard » de la patience (26.13 : 30, sous la case),
#                            derrière le titre de Tirs de loin comme avant
ZONES_GB_B = {**ZONES_GB, 0: [(64, 87.5, 34, 10.5)]}   # « Équilibrées » à DROITE (Kinito) : le miroir de sa place
#                            d'avant (2 -> 36 %) : alignée à droite sur les cases du dessus (98 %), jusqu'avant la surface
#                            de but (63 %)
ZONE_TITRE_GB = (2, 87.5, 34, 10.5)   # à gauche du gardien, à la place d'avant d'« Équilibrées » : « RELANCER VERS »
RELANCER_VERS = langue.texte("RELANCER\nVERS", "DISTRIBUTE\nTO")   # les mots de Kinito, sur deux lignes ; FM nomme
#                            cette consigne « Relances GB » (sa carte), Kinito préfère « Relancer vers » (12/10)
RELANCER_VERS_LANGUES = [   # NOS traductions (FM n'a pas ce texte ici) ; langue illisible : RELANCER_VERS
    ("english", "DISTRIBUTE\nTO"), ("english (us)", "DISTRIBUTE\nTO"), ("french", "RELANCER\nVERS"),
    ("german", "ABSPIEL\nAUF"), ("italian", "RILANCIO\nVERSO"), ("spanish", "SACAR\nHACIA"),
    ("spanish (latam)", "SACAR\nHACIA"), ("portuguese", "REPOR\nPARA"), ("portuguese (bra)", "REPOR\nPARA"),
    ("dutch", "UITVERDEDIGEN\nNAAR"), ("danish", "UDSPIL\nTIL"), ("norwegian", "UTSPILL\nTIL"),
    ("swedish", "UTSPEL\nTILL"), ("polish", "ROZEGRANIE\nDO"), ("czech", "ROZEHRÁT\nNA"),
    ("russian", "ВВОД МЯЧА\nНА"), ("turkish", "TOPU\nDAĞIT"), ("greek", "ΔΙΑΝΟΜΗ\nΠΡΟΣ"),
    ("indonesian", "DISTRIBUSI\nKE"), ("japanese", "配球\n先"), ("korean", "배급\n대상"), ("chinese", "分球\n给"),
    ("chinese (traditional)", "分球\n給"), ("thai", "ส่งบอล\nไปยัง"), ("arabic", "التوزيع\nإلى")]
# v10 : « Partir de zéro » (Kinito, 12/10 : réinitialiser TOUTES les consignes « comme le style Partir de zéro de FM »,
# son choix : choisir ce style comme FM). Mesuré : le menu « Style » de FM (TacticalPlannerHeader) écrit l'option
# choisie dans tactic.TacticalStyleDropdown (une référence de la liste tactic.TacticalStyleDropdownOptions : on ne peut
# pas la désigner, aucun des 9 999 chemins de liaison du jeu ne prend un élément de liste par son rang) ; le style est
# aussi Tactic.TacticalStyle, un entier (relevé F7 du 09/10 : 1 = Gegenpress ; options 0 … 10, 10 = Partir de zéro).
# Le bouton copie 10 dans Tactic.TacticalStyle, comme FM écrit dans la tactique depuis ses boutons (« tempselection ->
# tactic.Formation » de FormationEditConfirmCancelButtonsBlock) ; ForceUpdate = 1 (SetDatastoreValueEventContext :
# 1er octet de fin de la copie, champ m_forceUpdate, lu dans le code du jeu) pour que le style soit réécrit même s'il
# vaut déjà 10. À VÉRIFIER EN JEU : que le moteur applique bien le style (consignes remises) dans les deux cas.
CHEMIN_STYLE = "Tactic.TacticalStyle"
STYLE_ZERO = 10
V_STYLE_ZERO = "kinitostylezero"      # Int 10 (les constantes de FM s'arrêtent à const.Seven)
V_ZERO_FENETRE = "kinitozerofenetre"  # Int : 1 = la fenêtre « êtes-vous sûr ? » est ouverte
V_ZERO_CASE = "kinitozerocase"        # Bool : la case « Ne plus afficher ce message. » (cochée dans la fenêtre)
V_ZERO_SANS = "kinitozerosans"        # Bool PERSISTANTE : plus de fenêtre (case cochée puis « Oui »)
SOURCE_FENETRE = "GenericModalDialog"  # la fenêtre de confirmation de FM : carte, titre, texte, case, boutons
SOURCE_PRINCIPAL = "buttons-button-primary-default"   # le bouton principal de FM (modèle inclus de la fenêtre)
ID_SUR = (25317, "Are you sure you want to continue?")   # texte de FM (table de l'interface, traduit par le jeu) :
#                            n° de traduction lu dans notifications-modal-dialog-default-default
ZERO_LANGUES = [   # « Partir de zéro » : le nom de FM du style (clé 466667 de languages.fmf), dans chaque langue
    ('english', 'Clean Slate'), ('english (us)', 'Clean Slate'), ('french', 'Partir de zéro'),
    ('german', 'Leere Tafel'), ('italian', 'Tabula rasa'), ('spanish', 'Pizarra en blanco'),
    ('spanish (latam)', 'Pizarra en blanco'), ('portuguese', 'Novo Começo'), ('portuguese (bra)', 'Novo Começo'),
    ('dutch', 'Onbeschreven Blad'), ('danish', 'Ren tavle'), ('norwegian', 'Ny start'), ('swedish', 'Blankt papper'),
    ('polish', 'Czysta karta'), ('russian', 'Чистый лист'), ('turkish', 'Özel Sistem'), ('greek', 'Κενό'),
    ('indonesian', 'Mulai dari Nol'), ('japanese', '無設定'), ('korean', '전술 생성'), ('chinese', '空​白'),
    ('chinese (traditional)', '空​白'), ('arabic', 'سجل نظيف')]
OUI_LANGUES = [   # « Oui » de FM (clé 542706)
    ('english', 'Yes'), ('english (us)', 'Yes'), ('french', 'Oui'), ('german', 'Ja'), ('italian', 'Sì'),
    ('spanish', 'Sí'), ('spanish (latam)', 'Sí'), ('portuguese', 'Sim'), ('portuguese (bra)', 'Sim'), ('dutch', 'Ja'),
    ('danish', 'Ja'), ('norwegian', 'Ja'), ('swedish', 'Ja'), ('polish', 'Tak'), ('russian', 'Да'),
    ('turkish', 'Evet'), ('greek', 'Ναι'), ('indonesian', 'Ya'), ('japanese', 'は​い'), ('korean', '예'),
    ('chinese', '是'), ('chinese (traditional)', '是'), ('arabic', 'نعم')]
NON_LANGUES = [   # « Non » de FM (clé 542707, la suivante)
    ('english', 'No'), ('english (us)', 'No'), ('french', 'Non'), ('german', 'Nein'), ('italian', 'No'),
    ('spanish', 'No'), ('spanish (latam)', 'No'), ('portuguese', 'Não'), ('portuguese (bra)', 'Não'),
    ('dutch', 'Nee'), ('danish', 'Nej'), ('norwegian', 'Nei'), ('swedish', 'Nej'), ('polish', 'Nie'),
    ('russian', 'Нет'), ('turkish', 'Hayır'), ('greek', 'Όχι'), ('indonesian', 'Tidak'),
    ('japanese', 'い​い​え'), ('korean', '아니요'), ('chinese', '否'), ('chinese (traditional)', '否'),
    ('arabic', 'لا')]
VOILE_ZERO = (0.0, 0.0, 0.0, 0.55)   # le fond assombri derrière la fenêtre, sur tout le bloc des consignes
# v12 (Kinito, 15/10 : « Partir de zéro » et « Cartes / Terrain » de la taille de « Vue d'ensemble ») : mesuré sur sa
# capture de la v11 (1920 × 1080) : « Vue d'ensemble » 149 × 30 px réels, nos boutons 20 px de haut (même texte : lettres
# de 259 à 267 dans les deux). Le menu de FM est un bouton à bordure de 1 (buttons-combo-button-base-default : border 1px,
# padding 0 en haut et en bas, align-items center, max-height 32px) autour d'un champ de 25 de haut au moins (règle de FM
# « .si-dropdown-no-border .si-dropdown__selection-field » : min-height 25px, lue avec outils-analyse\regle_exacte.py) ;
# journal de la sonde du 13/10 : menu 26,3 unités, champ 24,5, bordure 0,9 (= 1 + 28 + 1 px réels). On refait la même
# chose : notre bouton (même classe, même bordure) autour d'un contenu d'au moins HAUT_ENTETE, centré ; ainsi la
# hauteur suit aussi celle de « Vue d'ensemble » quand le texte grandit (au-delà de 25, les deux grandissent pareil).
HAUT_ENTETE = 25
# Le bouton de FM se donne des marges (journal du 13/10 : 4,3 / 4,5 à gauche / droite, 1,7 / 1,8 en haut / bas autour
# de « Cartes » : d'où les 15 px entre « Cartes » et « Terrain » avec nos 4) : annulées ; nos écarts sont alors exacts.
ECART_ENTETE = 4   # v12 (Kinito) : 4 unités = 5 px réels entre « Vue d'ensemble » et « Partir de zéro », et entre
#                    « Terrain » et « Tuiles »
TEXTE_TUILES = langue.texte("Tuiles", "Tiles")   # v12 (Kinito) : « Tuiles » au lieu de « Cartes »
TUILES_LANGUES = {   # v12 : « Tuiles » dans la langue du jeu ; NOS traductions (FM n'a pas ce mot : ni « Tuiles » ni
    # « Tiles » dans languages.fmf, vérifié le 15/10 avec langues_toutes.py) ; le mot des écrans en tuiles de chaque langue
    "english": "Tiles", "english (us)": "Tiles", "french": "Tuiles", "german": "Kacheln", "italian": "Riquadri",
    "spanish": "Mosaicos", "spanish (latam)": "Mosaicos", "portuguese": "Mosaicos", "portuguese (bra)": "Blocos",
    "dutch": "Tegels", "danish": "Felter", "norwegian": "Fliser", "swedish": "Paneler", "polish": "Kafelki",
    "czech": "Dlaždice", "russian": "Плитки", "turkish": "Kutucuklar", "greek": "Πλακίδια", "indonesian": "Ubin",
    "japanese": "タイル", "korean": "타일", "chinese": "磁贴", "chinese (traditional)": "磚", "thai": "ไทล์",
    "arabic": "مربعات"}
# =====================================================================================================

# v48 (Kinito, 06/11) : trois OPTIONS de l'app d'Alex (page Options, section Kinito ; écrites dans son options.py par
# remettre_mes_ajouts.py, OPTIONS_AJOUTS ; la 1re valeur = celle de qui ne touche à rien) :
# - OPTION_DISPOSITION : la vue FM24 des consignes d'équipe en miroir (phases | consignes | terrain, v47) ou dans
#   l'ordre de FM 27 (terrain | consignes | phases) ;
# - OPTION_ARRIVEE : la vue des consignes d'équipe à la première arrivée (Tuiles, FM24 ou Terrain), puis la dernière
#   cliquée (son choix : « la 1re fois seulement ») ;
# - OPTION_ARRIVEE_INDIV : de même pour les consignes individuelles (FM 27 ou FM24).
# La valeur de chaque arrivée est aussi dans le nom de sa clé persistante : changer le réglage repart de lui.
OPTION_DISPOSITION = "consignes_fm24_disposition"
OPTION_ARRIVEE = "consignes_arrivee"
OPTION_ARRIVEE_INDIV = "consignes_indiv_arrivee"
# v49 (Kinito, 06/11 : « terrain à gauche ») : qui ne touche à rien a l'ordre de FM 27 (terrain | consignes | phases)
VALEURS_OPTIONS = {OPTION_DISPOSITION: ("fm27", "miroir"), OPTION_ARRIVEE: ("tuiles", "fm24", "terrain"),
                   OPTION_ARRIVEE_INDIV: ("fm27", "fm24")}


def _option(nom):
    """la valeur de l'option nom : imposée par KINITO_OPTION_<NOM> (bancs), sinon celle de l'app d'Alex, sinon la 1re"""
    valeurs = VALEURS_OPTIONS[nom]
    force = os.environ.get("KINITO_OPTION_" + nom.upper())
    if force in valeurs:
        return force
    try:
        import options
        v = options.get(nom)
        return v if v in valeurs else valeurs[0]
    except Exception:   # l'option n'est pas (encore) dans l'app (KeyError), ou pas de module options
        return valeurs[0]


ONGLET24, ARRIVEE24, ARRIVEE_INDIV24 = (_option(OPTION_DISPOSITION), _option(OPTION_ARRIVEE),
                                             _option(OPTION_ARRIVEE_INDIV))
VERSION = f"99-{ONGLET24}-{ARRIVEE24}-{ARRIVEE_INDIV24}{langue.SUFFIXE}"   # v48 : dépend des options (règle
#               d'Alex : sinon « déjà appliqué »)
#               v54 (Kinito, 09/11 : « construis EXACTEMENT comme la maquette » 37, un essai d'abord) : en vue Terrain,
#               l'écran de la maquette 37 sur tout l'onglet (kinito_consignes_ecran : trois terrains en perspective
#               dans leur stade, les cartes des consignes), dessiné d'après la maquette ; En taclant seule branchée
#               (ESSAI) ; la vue Terrain d'avant reste dessous, cachée
#               v55 (Kinito, v54 vue en jeu : « ça ressemble à la maquette » ; toit sombre dans les virages, textes
#               coupés à gauche, nom et choix des cartes pas alignés ; hauteur du pressing) : toit prolongé aux jonctions et
#               pressing 60,9 / 74,7 / 88,5 m (dans la maquette, réexportée) ; police « condensed » de FM au lieu de
#               « thematic », textes accrochés comme dans la maquette, capitales écrites (kinito_consignes_ecran)
#               v56 (Kinito, v55 vue en jeu : « fallait mettre de bas en haut » la colonne de droite, « et ensuite tu
#               branches ») : colonne « Sans le ballon » de bas en haut (maquette) ; les 28 consignes branchées (cartes,
#               zones, flèches, courses, bandes du bloc : kinito_consignes_ecran) ; textes accrochés selon la mesure de
#               la maquette ; l'écran 8 unités plus bas
#               v57 (Kinito, 10/11, v56 vue en jeu : « ça a l'air de fonctionner », puis séries de maquettes 6 et 7 ; il
#               choisit la 53) : l'écran de la maquette 53 (récapitulatif au-dessus des terrains, relance + progression
#               sur le terrain 1, pastilles à icône, courses de soutien et centres en flèches de points, étiquettes du
#               terrain 3 sur deux lignes, sliders refaits) ; même construction que la v56 (kinito_consignes_ecran)
#               v58 (Kinito, 10/11, v57 vue en jeu : icônes qui mordent sur le texte, « Arrières latéraux » cassé en
#               morceaux, pastilles à cheval sur la touche ; « centrer de loin » et « jouer le ballon dans la surface » sur
#               deux lignes) : la maquette réserve la largeur du vrai gras de FM (15 à 20 % plus large, mesuré), pastilles
#               sur une ligne, celles du bord rentrées ; réexportée
#               v59 (Kinito, 10/11) : « Gauche / Axiale / Droite » sous les flèches du terrain 1 (plus dedans), la zone
#               de clic de chaque flèche jusqu'à son nom ; maquette 53 réexportée
#               v60 (Kinito, 10/11, v59 vue en jeu et EN MATCH : « ça ne va pas du tout », l'écran sous la barre des
#               onglets et sous celle du match, ni clic ni défilement en bas ; récapitulatif plus gros) : l'écran dans un
#               défilement de FM, calé en haut (kinito_consignes_ecran) ; récapitulatif 12,5 / 14 points (maquette)
#               v61 (Kinito, 10/11, v60 vue en jeu : hors match l'écran était coupé en bas et défilait ; intitulés du
#               récapitulatif encore trop petits) : #Body ne fait que ~707 unités hors match (ma mesure de la v60, 722,
#               était fausse) ; l'écran de la maquette passe de 722 à 704 ; intitulés 14,5 points, plus clairs
#               v62 (Kinito, 10/11, v61 vue hors match : « toujours pas bon » : sous l'écran, les tuiles de FM qui
#               dépassent de #Body se voyaient ; puis « arrondir les 4 coins comme les tuiles ») : la vue descend jusqu'en
#               bas de la grille de FM, le cadre porte bordure et coins arrondis, l'écran revient à 722 (kinito_consignes_ecran)
#               v63 (Kinito, 10/11, grand écran 2560 x 1440 Small, maquette A) : la vue Terrain laisse voir le
#               visualiseur de FM à gauche quand il y a la place, l'écran grandit jusqu'à 1,2 fois (élément de FM qui
#               l'ajuste) ; en 1080p hors match rien ne change, en match l'écran rétrécit au lieu de défiler
#               (kinito_consignes_ecran). Les tuiles en bas : plus tard. Et (Kinito, même jour, capture d'un joueur
#               en 5120 x 1440 en disposition miroir : tuiles à l'envers) la règle de la v52 vise désormais TOUTE tuile
#               de la grille (classe si-tile), nos trois blocs mis à part (voir CLASSE_TUILE)
#               v64 (Kinito, 10/11, v63 vue en 2560 x 1440 Small : « il manque les tuiles, le reste c'est ok ») :
#               sous l'écran, la bande des tuiles de FM (copies de ses modèles : centre des données, rapport adversaire,
#               capitaines, CPA, penalties, efficacité tactique, consignes adverses, entraînement, entraînement
#               individuel en bas à droite), seulement quand elle tient (kinito_consignes_ecran, TUILES)
#               v65 (Kinito, 10/11, v64 vue en 1080p : « tu as tout cassé ») : en 1080p rien ne passait à la ligne, le
#               jeu rétrécissait le cadre et la zone ; ils ont maintenant une taille fixée, sans rétrécir (plafond à
#               100 %), comme les colonnes de tuiles qui, elles, passaient bien à la ligne. Colonnes de tuiles 304 et
#               écart 12 (la 6e ne tenait pas en 2560) ; le rapport sur le prochain adversaire, comme dans la grille
#               v66 (Kinito, 10/11 : en vue FM24, « tout aligné à gauche et les tuiles à droite ») : en vue FM24, la
#               grille de FM plafonnée à 23 colonnes (FM n'y pose plus ses tuiles, ses blocs retournés collés à gauche)
#               et nos copies de ses tuiles à droite (voir CLASSE_FM24, poser_tuiles24)
#               v67 (Kinito, v66 vue en 2560 Small : « dans le bon sens », mais la 2e colonne de tuiles coupée au bord) :
#               colonnes fixées, qui ne paraissent qu'entières ; une tuile qui ne tient pas en hauteur se cache
#               (kinito_consignes_ecran, TUILES24)
#               v68 (Kinito, 10/11 : « 22 colonnes ») : la grille de la vue FM24 plafonnée à 22 colonnes au lieu de 23 :
#               en 2560 Small, les deux colonnes de tuiles tiennent (LARGEUR_GRILLE24)
#               v69 (Kinito, 10/11, v68 vue en 3440 Small : « possible d'ajouter un truc à droite ? », puis le terrain
#               de gauche de « Positionnement de l'équipe », avec SEULEMENT vue combinée / avec / sans le ballon, et « le
#               mettre à gauche de l'écran, décaler le reste, sans toucher aux autres résolutions ») : en vue FM24, une
#               copie de ce terrain à gauche, la grille et nos tuiles décalées à droite, seulement quand les trois
#               tiennent (~2 912 unités : 3440 Small oui, 2560 Small et 1080p non, rien n'y change) (poser_tuiles24,
#               kinito_consignes_ecran.poser_terrain24)
#               v70 (Kinito, 10/11, v69 vue en jeu dans six tailles) : vue FM24 — une colonne de tuiles ne paraît
#               qu'entière (2 560 Moyen : la 1re était coupée), les neuf tuiles en deux colonnes égales, la 2e colonne
#               visible en 3 440 Petit, le terrain de Positionnement calé sur les blocs de FM et présent aussi en 3 440
#               Moyen (BASE_INTERIEUR24) ; vue Terrain — l'écran grandit jusqu'à 1,3, calé en haut, « Partir de zéro »
#               écarté de « Consignes », et en 3 440 Petit les tuiles à droite au lieu d'en bas (kinito_consignes_ecran)
#               v71 (Kinito, 10/11, v70 vue en jeu dans six tailles) : vue FM24 — grille de 20 colonnes, une seule
#               colonne de tuiles (consignes particulières en haut), le terrain de Positionnement aussi en 2 560 Petit,
#               les deux terrains (avec et sans ballon, sans boutons) en 3 440 Petit ; vue Terrain large (3 440 Petit) —
#               terrain de Positionnement et centre des données à gauche, l'écran et quatre tuiles dessous, une copie du
#               visualiseur à droite (kinito_consignes_ecran.vue_large)
#               v72 (Kinito, 11/11, v71 vue en jeu) : vue large — consignes adverses ajoutées sous l'écran, écran
#               jusqu'à 1,34 ; vue FM24 — boutons cachés au-dessus des deux terrains, écarts de ~16 entre eux et
#               jusqu'au premier bloc, le terrain avant la colonne de tuiles (3 440 Grand : le dispositif à gauche)
#               v73 (Kinito, 11/11) : vue FM24 — la Vue d'ensemble de FM (copie) à la place de la colonne de tuiles ;
#               panneaux coupés sous les terrains (dispositif, les deux terrains, visualiseur de FM : aussi en vue
#               Terrain) et sous la Vue d'ensemble, des tuiles dessous (kinito_consignes_ecran, poser_bas_visualiseur)
#               v74 (Kinito, 11/11, v73 vue en jeu) : tout coupé à 724 (terrains, nos blocs FM24, Vue d'ensemble), une
#               bande de tuiles dessous en vue FM24, les remplaçants sous le dispositif (vue FM24, vue large) et sous le
#               visualiseur de FM (vue Terrain), les deux terrains à 476 sur le terrain simple
#               v75 (Kinito, 11/11, v74 vue en jeu) : affichage Moyen (settings.AdaptiveScalingLevelIndex) — une
#               rangée de six tuiles 4 x 2 en vue FM24, une rangée sous l'écran en vue Terrain ; remplaçants coupés au
#               bas de la bande en Petit ; vue Terrain : notre dispositif à gauche, bouton « Visualiseur » / « Dispositif »,
#               et cette colonne dès 2 560 Moyen (l'écran rétrécit)
#               v76 (Kinito, 11/11, v75 vue en jeu) : le choix « Dispositif | Visualiseur » en boutons segmentés à droite
#               de l'en-tête ; vue FM24, terrain seul : notre dispositif par-dessus le visualiseur (miroir gardé) ; la
#               rangée du Moyen sans écart dessous ; remplaçants au bas de la 2e rangée ; trois tuiles sous les deux
#               terrains ; 2 560 Moyen Terrain : quatre tuiles juste sous l'écran ; vue large : entraînement en plus
#               v77 (Kinito, 11/11, v76 vue en jeu) : 3 440 Petit FM24 réparé (remplaçants des deux terrains à leur
#               hauteur, le terrain simple caché dessous) ; vue Terrain : colonne de gauche dès 1080p et 2 560 Grand,
#               rangée de tuiles posée juste sous l'écran (sauf en Petit)
#               v78 (Kinito, 11/11, v77 vue en jeu) : 1080p et 2 560 Grand, vue Terrain, de nouveau les consignes seules ;
#               2 560 Moyen : six tuiles 4 x 4 réduites sous l'écran, le centre des données à droite
#               v79 (Kinito, 11/11) : le travail grand écran de la vue FM24 aussi dans l'ordre FM 27 (option « fm27 »,
#               terrain à gauche), la grille non retournée
#               v80 (Kinito, 11/11, captures en match) : EN MATCH seulement, la vue Terrain sur la ligne de FM (plus
#               rien sous la barre Annuler / Confirmer), les blocs de FM masqués dessous, 3 440 Petit sans tuiles ni
#               visualiseur à droite et l'écran agrandi (kinito_consignes_ecran.CLASSE_MATCH)
#               v81 (Kinito, 11/11, FMSonde 0.28.0 en match) : la vue FM24 en match (sans tuiles, Vue d'ensemble ni
#               remplaçants ; x1,449 en Petit, x1,113 en Moyen, x0,885 en Grand ; voir ECHELLE_MATCH24) ; un seul
#               bouton à icône de FM pour passer du dispositif au visualiseur (kinito_consignes_ecran.bascule)
#               v82 (Kinito, v81 vue en match) : la vue FM24 en match ajustée par l'ajusteur de FM à la hauteur
#               réelle, en direct (plafond x1,5), au lieu d'une classe d'affichage qui ne suivait pas le changement
#               v83 (Kinito, v82 vue en 2 560 Grand : rien de réduit) : l'ajusteur en absolu (dans le flux, il
#               agrandissait son parent : FM le comparait à lui-même)
#               v84 (Kinito, v83 vue en 3 440) : la vue FM24 en match un peu plus petite (HAUT_LIGNE_MATCH24 745),
#               une marge au-dessus de la barre Annuler / Confirmer
#               ; et les règles de l'ajusteur enfin appliquées (la feuille rattachée à lui, pas seulement à
#               l'enveloppe sous lui : en v82, v83, il ne réduisait rien)
#               v85 (Kinito, 11/11, v84 vue en match : « c'est mieux ») : hors match, en Moyen, vue FM24, la Vue
#               d'ensemble remplacée par Efficacité tactique et Centre des données (kinito_consignes_ecran,
#               TUILES_HAUTES_MOYEN)
#               v86 (Kinito, v85 vue en 3 440 Moyen : les deux tuiles hautes absentes, Entraînement en haut) : la
#               hauteur de leur zone par flex-basis (le réglage de FM remettait height à « auto »)
#               v87 (Kinito, 11/11) : 3 440 Petit hors match, vue FM24 : colonne de droite et tuiles du bas retirées,
#               une seule rangée, tout agrandi x1,2 ; trois classes sur #Body (hors match, écran « 3440 x 1440 »,
#               Petit), dont deux par la fonction de FM qui compare un texte (reglage_texte, poser_3440)
#               v88 (Kinito, 11/11) : 2 560 hors match, vue FM24 : en Moyen, colonne de droite et rangée du bas
#               retirées, x1,2 ; en Petit, panneau unique (dispositif + bouton visualiseur), colonne retirée, une
#               rangée (remplaçants, rapport, CPA, capitaines), x1,27 (ECHELLE_2560_MOYEN, ECHELLE_2560_PETIT)
#               v89 (Kinito, 11/11, v88 vue) : 2 560 Petit x1,24 et Efficacité + Centre des données à droite ;
#               2 560 Moyen x1,23 ; 3 440 Grand et Moyen fusionnés (dispositif sur le visualiseur), à droite une
#               colonne (Grand) ou trois (Moyen), et en Moyen les remplaçants sous le panneau (BASE_INTERIEUR_3440_GRAND)
#               v90 (Kinito, 11/11) : 3 440 Petit, ordre FM 27 : panneau fusionné, remplaçants dessous, consignes et
#               récapitulatif zoomés jusqu'en bas, deux colonnes de tuiles à droite, x1,25 (ECHELLE_3440_FUSION)
#               v91 (Kinito, 11/11, v90 vue) : le récapitulatif agrandi n'est plus coupé au bord de la grille (la zone
#               de défilement de FM, sans_coupe) ; 3 440 Moyen, ordre FM 27 : même refonte (ZOOM_CONSIGNES_3440_MOYEN)
#               v92 (Kinito, 11/11, v90 vue en 2 560 Petit) : trois grandes tuiles à droite (COL_2560_PETIT ; sa mesure
#               de hauteur : elles passent à x1,24), les trois petites de la rangée rapprochées et centrées
#               v93 (Kinito, v92 vue) : le centrage marche (« justify-content » sorti du style intégré, qui passait
#               devant la règle) ; 3 440 Petit et Moyen : l'Entraînement remonté au niveau de Consignes particulières
#               v94 (Kinito, 11/11, en match en 1080p : la vue FM24 défilait) : l'enveloppe plafonnée à
#               HAUT_LIGNE_MATCH24 en match (règle 94.0) : dessinée, elle fait la hauteur de l'onglet
#               v95 (Kinito, 13/11 : « traduire dans les langues du jeu », ses choix : la langue réglée dans FM, en
#               direct ; « … » quand c'est trop long ; nos mots traduits par nous) : la vue Terrain dans la langue du
#               jeu (kinito_consignes_ecran : noms de consigne et d'option par leur n° de traduction, nos mots et ceux de
#               FM par langue, chaque texte sur sa place libre). ESSAI : la vue FM24 et les consignes individuelles
#               ensuite
#               v96 (Kinito, 13/11, v95 vue en anglais et en allemand : ça marche ; « l'infobulle correspondant au
#               choix de la consigne, comme sur la vue FM24 », et la phrase entière au survol d'un texte coupé) :
#               kinito_consignes_ecran (bulles_options, DisplayTooltipWhenElided de FM)
#               v97 (Kinito, 13/11 : « fais les vues FM24 ») : la vue FM24 des consignes d'équipe, sa colonne des
#               phases et les consignes individuelles FM24 dans la langue du jeu : nos mots (TEXTES24_LANGUES) en
#               copies par langue sous un conteneur de langue par bloc (langue24, traduire24) ; les noms de FM y
#               étaient déjà (données du jeu)
#               v99 (Kinito, 14/11, v98 vue en espagnol : tout traduit, mais « Más en… / Más dir… » coupés sans
#               moyen de lire la suite) : en vue FM24, un texte coupé par « … » reçoit le survol (la phrase entière,
#               comme la vue Terrain en v96) quand il ne couvre aucune case (survol_libre24)
#               v98 (Kinito, 13/11, v97 vue en italien : vue Terrain et vue FM24 d'équipe traduites, mais les mots
#               des cases et les en-têtes des consignes individuelles restés en anglais) : un texte posé directement
#               dans un interrupteur de FM passe d'abord dans une boîte (envelopper24)
#               v53 (Kinito, 08/11, v52 vue en 3440 x 1440 : « le vert du vide n'est pas le même que celui des
#               colonnes », « laisser la même marge sur le côté que sur le haut ») : en vue FM24, le cadre des
#               proportions passe DANS le panneau sombre des colonnes : le panneau va d'un bord à l'autre (liseré
#               de 6 points sur les côtés comme en haut), seules les colonnes restent centrées ; la légende reprend
#               sa place de la v51, sous le panneau (RAPPORT_VUE24)
#               v52 (Kinito, 08/11, capture d'un joueur en 1440p, disposition « miroir ») : en grand écran, FM
#               ajoute à droite de l'onglet des tuiles « en option » (rapport, centre des données, capitaines,
#               coups de pied arrêtés…) ; le miroir les passait à gauche ET les écrivait à l'envers. Une règle à
#               sélecteurs les retourne sur elles-mêmes en vue FM24 (voir TUILES_EN_OPTION). Kinito, même capture :
#               « et le terrain ? il ne rentre pas dans l'écran » : en grand écran le bloc est ~2,5 fois plus large,
#               et nos terrains, dont la hauteur suit la largeur, ne tiennent plus en hauteur. Les vues Terrain et
#               FM24 gardent désormais les proportions du 16:9, au centre (voir RAPPORT_VUE)
#               v51 (Kinito, 07/11, v50 vue : « Normal », « Plus », les ronds, la légende, « Centrez vers » bougent
#               encore d'un pixel ; mesuré par FMSonde 0.22.1) : les deux vues posées sur la MÊME zone exacte de la
#               grille (ZONE_INDIV24), par des pourcentages de la grille, plus aucun chiffre tiré d'une capture
#               (voir ZONE_INDIV24)
#               v49 (Kinito, 06/11, v48 vue : même hauteur, encore un pixel en largeur) : la disposition par défaut
#               devient « terrain à gauche » (ordre de FM 27) ; avec le ballon, la vue a la MÊME LARGEUR que sans le
#               ballon (LARGEUR_VUE24 : les deux cadres venaient de deux mesures, 729 et 730 px, d'où 1,2 px de plus
#               avec le ballon ; mesuré sur ses captures 38 / 39 : boutons 1 px plus larges, et le CALE_AVEC24 de la
#               v48 avait poussé toute la vue d'un pixel ENTIER, pas d'un demi : le bord gauche, juste, est gardé)
#               v50 (Kinito, 07/11, v49 vue : « encore un décalage, uniquement en largeur ») : avec le ballon, la vue
#               1 px plus large que la v49 (AJUSTE_AVEC24 : v48 trop large, v49 trop étroite, mesuré sur 38 à 41)
#               v48 (Kinito, 06/11, v47 validée) : les trois options (OPTION_DISPOSITION…) ; le bouton FM24 AVANT
#               FM 27 dans la ligne des consignes individuelles ; avec le ballon, la vue FM24 posée exactement comme sans
#               le ballon (CALE_AVEC24 : mesuré sur ses deux captures, sans le ballon tout était 4 px plus haut, la
#               légende 1 px, et un demi-pixel à droite)
#               v1 : première disposition (38,5 / 23 / 38,5, totem dans une tuile, tuiles du bas au
#               titre posé en bas : 83 px de vide au-dessus, mesuré sur la capture de Kinito du 12/10) ;
#               v2 (Kinito, 12/10) : 40 / 20 / 40 strict, totem sur une colonne de terrain (badge sur le rail, nom de
#               la consigne dans le badge), tuiles du bas titre en haut et cases qui remplissent, noms des phases en
#               haut des colonnes « avec le ballon » ;
#               v3 (Kinito, 12/10, captures de la v2) : sans le ballon, colonne du milieu sur toute la hauteur : gazon
#               sans marquage, titre, 5 boutons de FM (3/5), tuile Transition défensive en colonne (2/5) ; avec le
#               ballon, Style de centres et Liberté créative échangés ;
#               v4 (Kinito, 12/10, vu un vide sous les colonnes 1 et 3 de la v3, cause non mesurée faute de capture) :
#               42,5 / 15 / 42,5 ; les tuiles grandissent par une boîte simple dans laquelle elles s'étirent (mécanisme
#               de la v2, vu en jeu ; v3 : la tuile elle-même grandissait en hauteur dans sa colonne, jamais vu) ; titres
#               de la colonne du milieu en px fixes (TITRE_MILIEU, TITRES_DEDANS) ; bandes d'herbe du milieu recalées ;
#               v5 (Kinito, 12/10, capture de la v4 : tuiles des côtés finies à y = 1031, 34 px au-dessus du bas du bloc
#               (1065, où finit la colonne du milieu), tuile de 103 px au lieu des 137 calculés ; terrain 382 × 589 et
#               bandes d'herbe justes) : retour à la disposition de la v2 (vue en jeu sans vide) : rangée des terrains
#               (hauteur en % de la largeur du bloc), rangée des tuiles qui prend tout le reste ; la colonne du milieu
#               posée par-dessus les deux rangées. v3 / v4 calculaient la hauteur du terrain sur la largeur de SA colonne :
#               c'est là que le vide est apparu (cause exacte non prouvée) ;
#               v6 (Kinito, 12/10) : échanger les colonnes et le haut / bas de chaque colonne (voir en tête) ; chaque
#               colonne dans son calque pleine largeur (la hauteur du terrain reste un % de la largeur du BLOC, règle
#               de la v5) ; les titres de colonnes passent dans des en-têtes posés de la même façon (celui de la
#               colonne 0 dans le flux : il donne la hauteur de la rangée) ; titres du milieu 9 / 8 px ;
#               v7 (Kinito, 12/10, v6 validée en jeu) : la même personnalisation « avec le ballon », les trois éléments
#               d'une colonne rangés librement (voir en tête) ;
#               v8 (Kinito, 12/10, v7 vue en jeu) : terrain Relance sans fond derrière « Réception des passes » (les
#               bandes d'herbe sur tout le terrain, comme les deux autres) ; « Équilibrées » à droite, « RELANCER VERS »
#               à gauche du gardien ; Rythme et Perdre du temps estompés comme les autres consignes ; Progression :
#               « Axiale » estompée quand un côté (ou les deux) est choisi, les côtés quand « Axiale » l'est
#               ; largeur du jeu offensif et déclenchement du pressing estompés comme Rythme (Kinito)
#               v9 (Kinito, 12/10, v8 vue en jeu) : relance courte du gardien en une case « oui » au centre ;
#               « Cartes / Terrain » à l'allure de « Vue d'ensemble » (l'autre vue assombrie) ; titres de colonne
#               tous trois en thematic-sm, le texte centré sur sa colonne, l'icône juste après ; « Déclench. pressing » et
#               « Transition défensive » centrés sur la ligne de l'icône du coin, à la taille maximale de leur langue ;
#               v10 (Kinito, 12/10, v9 vue en jeu) : ces deux titres sous l'icône, sur toute la largeur, tailles
#               recalculées (français 13 / 13) ; écarts entre leurs boutons rognés ; bouton « Partir de zéro » + fenêtre
#               de confirmation (case « Ne plus afficher ce message. » gardée) ;
#               v11 (Kinito, 13/10, v10 vue en jeu : « le bouton fonctionne ») : l'icône d'échange des deux tuiles de
#               la colonne du milieu en haut AU MILIEU (coin(centre=True)), plus dans le coin ; rien d'autre
#               v12 (Kinito, 15/10, capture de la v11) : l'en-tête : « Partir de zéro », « Terrain », « Tuiles » à la
#               hauteur de « Vue d'ensemble » (HAUT_ENTETE), marges du bouton de FM annulées ; « Partir de zéro » juste
#               après « Vue d'ensemble » ; « Terrain » puis « Tuiles » (ex-« Cartes », TUILES_LANGUES), ECART_ENTETE
#               entre eux, calés à droite (le plus long pousse à gauche) ; la vue choisie gardée (« Persistent »,
#               declarer), Terrain la toute première fois
#               v13 (Kinito, 28/10, capture de la v12) : sans le ballon, toutes les options montrées, les autres estompées
#               (TUILES_3 : En taclant, Comportement de la ligne, Transition défensive en trois cases, l'ordre changé ;
#               relance courte du gardien « Non » + « Oui » ; « Équilibré » en texte pour le piège et les centres) ;
#               « Empêcher de centrer » plus grand ; plus d'infobulle sur les bandes de la hauteur du pressing et de la
#               ligne défensive (elle gênait les clics suivants) ; colonne du milieu PARTS_MILIEU (boutons égaux)
#               v14 (Kinito, 28/10, même capture) : avec le ballon, toutes les options montrées, les autres estompées
#               (TROIS_AVEC, tuile_avec_b ; « Standard » écrit sous la patience, les tirs de loin et les dribbles,
#               STANDARD_B ; « Équilibré » sous la progression, TEXTE_PROGRESSION_B) ; titres de la patience et de la
#               stratégie d'attaques placées (PROGRESSION_B, STRATEGIE_B) ; zones « Relancer vers » estompées aussi
#               v15 (Kinito, 28/10, v14 installée) : 2e clic -> option neutre partout (bouton_b, SANS_RETOUR) ;
#               « Équilibré » des centres en TEXTE_EMPECHER, capitales
#               v16 (Kinito, 28/10, v15 installée) : plus de but (sans_but, traits_reels) ; titres centrés
#               (titre_entre) ; « Équilibré » du piège comme celui des centres (equilibre_grand, PIEGE_CASES)
#               v17 (Kinito, 28/10, capture de la v16) : plus de flèches sous les cartes du piège (PIEGE_FLECHES),
#               « Équilibré » recentré dessous (EQUILIBRE_PIEGE)
#               v18 (Kinito, 28/10, v17 vue en jeu) : déclenchement du pressing estompé standard compris (declench)
#               v19 (Kinito, 04/11, captures 7 à 9 de FM24) : une 3e vue, « FM24 » (vue_fm24) : un 3e bouton dans
#               l'en-tête (Terrain, Tuiles, FM24), la colonne des phases (avec le ballon, en transition, sans le
#               ballon : résumé des consignes choisies, « Changer » / « OK ») puis les consignes de la phase ouverte,
#               aux couleurs de FM24 ; Terrain et Tuiles inchangés ; v20 (Kinito, 04/11 matin, v19 vue en jeu) :
#               les phases à la place de la colonne de droite de FM (PhasesTeamInstructionsBlock), les consignes sur
#               toute la largeur du bloc, l'écran refait au plus près de FM24 (vue_fm24, poser_droite, poser_ecran) ;
#               v21 (Kinito, 04/11, v20 vue en jeu : « la DA est pas folle encore, des trucs sont mal placés ») :
#               zones jointives aux places de FM24 avec ses phrases, icônes et triangles ▼▲ des curseurs, icônes des
#               phases, réception des passes sur une ligne, centres sans titre, lignes de pressing blanche et de
#               défense jaune doré (couleurs choisies pour rester lisibles par les daltoniens, sur le vert) ;
#               v22 (Kinito, 04/11, v21 vue en jeu, captures 22 à 31) : pions de la formation (lue par son nom) sur
#               la largeur (qui bougent avec elle) et sur deux terrains de transition, flèches de FM24, zones sans
#               espace, « Gérer le pressing » en bande, relance du gardien comme FM24 (sans « Équilibrées »), boutons
#               empilés sans espace, relances courtes du gardien en UN bouton (plus sur le terrain des lignes) ;
#               v23 (Kinito, 04/11, v22 vue en jeu, captures 32 à 37) : pions plus gros, sur 5 lignes, lus dans une
#               table des formations de FM 27 (nom complet), largeur sans recopier les pions (classes de marge de FM),
#               flèches courbes et par-dessus les zones, flèches de « Gérer le pressing », de la patience et des tirs,
#               boutons sans bord (plus d'encadré quand ils sont choisis), espaces / pieds et encourager / dissuader
#               dans l'ordre de FM24, tirs à parts égales, « Contourner le pressing » plus grand ; sans le ballon :
#               pions qui suivent les deux lignes, points des crans à gauche du terrain, pressing en trois tiers ;
#               v24 (v23 vue en jeu : seul le gardien) : formation reconnue en deux temps (sans les mots, puis le nom
#               complet de la variante, tel quel et en majuscules), variante de base à défaut ; nom lu affiché ;
#               VERSION DE TEST : les postes de chaque joueur lus sous la largeur (lecture_postes24), pour placer
#               ensuite chaque pion à son poste (formations personnalisées) ;
#               v25 (Kinito, 04/11, v24 vue en jeu sur trois tactiques) : un pion par joueur à son POSTE LU
#               (POSTES24 : les 24 postes de Kinito), avec ballon sur la largeur et la transition, sans ballon sur
#               le terrain des lignes (son choix) ; la table des 57 formations et les lignes de test retirées ;
#               v26 (Kinito, 04/11, v25 vue en jeu) : deux centraux seuls sur leur ligne se rapprochent (MD, MC,
#               MOC, BT ; occupation24), le terrain des lignes décalé à droite avec ses encadrés à gauche sur la ligne
#               prolongée, le terrain de la largeur aux vraies proportions (rond central rond) et ses pions plus grands ;
#               v27 (Kinito, 04/11, v26 vue en jeu) : la ligne prolongée du point du cran au terrain seulement, les
#               terrains de transition aux vraies proportions, le terrain sans ballon plus grand (66 %) et ses pions
#               proportionnels (PART_PION24), la construction plus haute (1,25), et la construction et la finition
#               rétrécies en Grand / Plus grand (REDUIT24), pour tenir sans défiler ;
#               v28 (Kinito, 04/11, v27 vue en jeu dans les 4 tailles du texte) : la colonne des encadrés à la largeur
#               de chaque taille (LARGEUR_GAUCHE24), le texte des zones et du bouton des coups de pied arrêtés à la
#               taille du Normal en Grand et Plus grand (selon_taille24) ;
#               v29 (Kinito, 04/11, v28 vue en jeu) : la colonne de gauche du terrain des lignes rentrée de 1 px en haut
#               et en bas (le cadre du terrain) : la ligne prolongée rejoint exactement celle du terrain ;
#               v30 (VERSION DE TEST, Kinito, 04/11 nuit) : un cadre orange dans la fenêtre des consignes
#               individuelles, à la place des tuiles (poser_indiv) : avant de construire leur vue FM24 ;
#               v31 (TEST 2 : quatre tuiles passaient devant le cadre) : avec le ballon, le cadre part de la dernière
#               tuile créée (poser_indiv_tuile) ; le bloc de gauche ne le montre plus que sans le ballon ;
#               v32 (TEST 3, test 2 vu : plus rien devant, cadre un peu trop grand) : cadre corrigé au pixel, et des
#               boutons d'essai qui écrivent une consigne individuelle (tacles sans le ballon, dribbles avec) ;
#               v33 (test 3 vu : les boutons écrivent la consigne, la tuile de FM change avec) : la vraie vue FM24 des
#               consignes individuelles (vue_indiv24), le bouton FM 27 / FM24 dans le bloc de gauche, retenu par la
#               fiche (PlayerInstructionsCard) ;
#               v34 (v33 vue : « il me faut des schémas comme sur le 24 ») : les schémas de FM24 (éventail, camembert,
#               curseurs, grilles), ses cinq états, le bouton FM 27 / FM24 dans la barre des onglets ;
#               v35 (v34 vue : le bouton ne se voyait plus, coupé par la grille de la fenêtre) : le bouton dans le coin en
#               bas à droite du bloc de gauche ;
#               v36 (v35 vue en jeu, ses demandes) : bouton à droite de « Sélectionné actuellement », fond de FM 27,
#               titres courts et centrés, jauges pleines, flèches, secteurs exacts, grilles propres, « Attaquer la
#               surface » en haut, options impossibles au poste grisées (drapeau « Disabled » de la liste de FM 27) ;
#               v37 (v36 vue) : bouton sous #HasPlayerSwitch (il était sur « Attribuer à »), disques sans fond et plus
#               grands, jauges sans espace, tailles revues pour « Plus grand » ;
#               v38 (v37 vue, ses demandes) : un seul bouton FM 27 / FM24, grilles sans fond aux cases collées, mots des
#               cases à la taille du Normal à toute taille, infobulles d'explication (individuelles et d'équipe),
#               « Mouvements » sous la direction, en-tête « Sans ballon (équipe) », boutons l'un sous l'autre ;
#               v39 (v38 vue) : plus aucun espace (marges par défaut des boutons de FM annulées), bouts des jauges
#               au-dessus, disques de rayon 74, noms des quarts dans leur case, sous-titres plus grands ;
#               v40 (Kinito) : le bouton FM 27 / FM24 dans la ligne du haut, avant « Annuler sél. », à son allure grise ;
#               v41 (v40 vue) : les deux boutons FM 27 et FM24, le choisi en violet ; la grille « Côté » plus grande
#               (46 px par rangée, mots de 12) ; « Normal » au milieu des jauges, sur la ligne de leurs bouts ;
#               v42 (v41 vue) : « Normales » au milieu de la jauge des passes ;
#               v43 (Kinito) : la vue FM24 des consignes d'équipe en « sarcelle », les verts sombres de l'écran des
#               tactiques de FM 27 (les consignes individuelles gardent leurs couleurs, à sa demande) ;
#               v44 (v43 : « c'est mieux ») : la carte de la phase ouverte en sarcelle claire au lieu du violet, la
#               colonne des phases écrite plus grand (nom 15, résumé 14, « OK / CHANGER » 13), À LA MÊME TAILLE à
#               toute taille du texte de FM, lignes à hauteur fixe : elle tient en « Plus grand » avec toutes les consignes
#               v45 (v44 validée ; Kinito : « c'est pas beau le terrain ») : la formation défensive (sans le ballon)
#               réorganisée : les deux encadrés côte à côte AU-DESSUS du terrain (ligne défensive à gauche, hauteur du
#               pressing à droite), le terrain centré et aussi grand que la hauteur le permet (vraies proportions), les
#               points des crans SUR les lignes de touche (gauche et droite), la ligne s'arrête sur eux
#               v46 = VERSION DE TEST (Kinito, 06/11 : « quand l'écran choisi est FM24, la colonne de droite à gauche,
#               ensuite les consignes, ensuite le terrain interactif ; que pour l'onglet FM24 ») : le MIROIR (MIROIR24) :
#               en vue FM24, la grille de l'onglet retournée à l'horizontale, chacun de ses trois blocs retourné sur
#               lui-même (son contenu redevient à l'endroit) ; Tuiles et Terrain : rien ne change
#               v47 (v46 vue : « Marche pas », rien de retourné) : la variable --rlt-x-flip écrite dans NOTRE style
#               intégré n'est pas lue (FM n'en déclare jamais dans un style intégré, 0 dans tous ses modèles ; seulement
#               dans ses feuilles, sur :root). À la place, la seule classe de FM qui retourne SANS variable
#               (« scale: -1 1 », CLASSE_MIROIR), posée par le SIStyleSetter sur LUI-MÊME (le geste éprouvé de
#               selon_classe ; la v46 la posait sur son enfant, jamais essayé) ; ses largeur, hauteur et marge annulées
#               par notre style intégré
MARKER =os.path.join(backup.BACKUP_DIR, "kinito_consignes_essai_b.actif")
NOM = f"{base.PREFIXE}-b-v{VERSION}"
RACINE = f"{base.PREFIXE}-b-v"
AUTRE_MARQUEUR = "kinito_consignes_essai.actif"

CADRE_TERRAIN = {"flex-direction": "column", "overflow": "hidden", "background-color": COUL["herbe2"],
                 **cadre_css(1, COUL["cadre"], 10)}
PLEIN = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
TAILLE_ICONE = {"width": ICONE, "height": ICONE, "flex-shrink": 0}
_UTILE = 100 - 2 * ECART
LARG = [part / sum(LARGEURS_SANS) * _UTILE for part in LARGEURS_SANS]   # v6 : largeur de chaque colonne, % du bloc


def decalage(p, k):
    """v6 : où commence la colonne k dans l'ordre p, en % de la largeur du bloc"""
    o = ORDRES[p]
    i = o.index(k)
    return sum(LARG[o[j]] for j in range(i)) + i * ECART


def echange(p, a, b):
    """v6 : l'ordre obtenu en échangeant les colonnes a et b dans l'ordre p"""
    o = list(ORDRES[p])
    ia, ib = o.index(a), o.index(b)
    o[ia], o[ib] = b, a
    return ORDRES.index(tuple(o))


def persistant(propriete):
    """v6 : la clé de persistance, écrite comme celle de FM (« (Persistent,Explicit,{objet},{propriété}) »)"""
    return f"(Persistent,Explicit,{{{CLE_PERSISTANCE}}},{{{propriete}}})"


VARIABLES = [(V_ORDRE, f"Int|0|{persistant('ordre')}")] + \
    [(v, f"Int|0|{persistant(f'haut-bas-{k}')}") for k, v in enumerate(V_HB)] + \
    [(V_COL, "Int|0|"), (V_ELT, "Int|0|")] + \
    [(V_AORDRE, f"Int|0|{persistant('ordre-avec')}")] + \
    [(v, f"Int|1|{persistant(f'terrain-avec-{k}')}") for k, v in enumerate(V_APOS)] + \
    [(v, f"Int|0|{persistant(f'tuiles-avec-{k}')}") for k, v in enumerate(V_AREV)] + \
    [(V_ACOL, "Int|0|"), (V_AECOL, "Int|0|"), (V_AEELT, "Int|0|")] + \
    [(V_STYLE_ZERO, f"Int|{STYLE_ZERO}|"), (V_ZERO_FENETRE, "Int|0|"), (V_ZERO_CASE, "Bool|0|"),
     (V_ZERO_SANS, f"Bool|0|{persistant('sans-confirmation')}")]   # v10 : « Partir de zéro » (Bool persistante : écrite comme
#    « inpossession » de FM, Bool|1|(Persistent,…)) ; v19 : la phase ouverte de la vue FM24 (gardée d'une ouverture à
#    l'autre, comme la vue) ; v20 : elle et la vue sont déclarées par l'onglet (VARIABLES_ECRAN, poser_ecran)


def traits_reels(haut, bas, couloirs=False):
    """lignes d'un vrai terrain (68 × 105 m) en % : ligne médiane, rond central (9,15 m de rayon), surfaces de
    réparation (40,32 × 16,5 m), de but (18,32 × 5,5 m) ; haut / bas : surfaces de ce côté. v16 (Kinito) : plus le
    but (7,32 m), le trait blanc de la cage"""
    L = COUL["ligne"]
    out = [("milieu", {"left": 0, "width": pc(100), "top": pc(50), "height": 0, "border-top-width": 1,
                       "border-top-color": L}),
           ("rond", {"left": pc(50 - 26.91 / 2), "top": pc(50 - 17.43 / 2), "width": pc(26.91), "height": pc(17.43),
                     **cadre_css(1, L, pc(50))})]
    for cote, oui in (("haut", haut), ("bas", bas)):
        if not oui:
            continue
        bord = {"top": -1} if cote == "haut" else {"bottom": -1}
        out += [(f"surface-{cote}", {"left": pc(20.35), "width": pc(59.29), **bord, "height": pc(15.71),
                                     **cadre_css(1, L)}),
                (f"six-metres-{cote}", {"left": pc(36.53), "width": pc(26.94), **bord, "height": pc(5.24),
                                        **cadre_css(1, L)})]   # v16 : plus de but (le trait blanc de la cage, Kinito)
    if couloirs:   # les couloirs du piège (côtés / axe), comme 26.13
        out += [(f"couloir-{x}-{y}", {"left": pc(x), "top": pc(y), "height": pc(h), "width": 0, "border-left-width": 2,
                                      "border-left-color": (1.0, 1.0, 1.0, 0.40)})
                for x in (27, 73) for y, h in ((6, 46), (56.5, 43.5))]
    return out


def sans_but(traits):
    """v16 (Kinito : « vire le trait blanc qui représente la cage ») : les traits d'un terrain de 26.13 sans son but"""
    return [(nom, css) for nom, css in traits if nom != "but"]


def titre_entre(fab, env, nom, haut, bas, marge_bas=0):
    """v16 (Kinito : « centre les titres au milieu de l'espace entre le bord du terrain et la première carte en
    dessous ») : le titre de la consigne de l'enveloppe, sur toute la largeur du terrain, centré en hauteur entre haut
    (le bord du terrain, ou le bas de la case du dessus) et bas (le haut de la case du dessous), en % du terrain. Les
    cases (case_abs) ont 3 px de marge en haut comme en bas : leurs bords donnent le milieu exact de l'écart visible.
    marge_bas, en px : ce qui dépasse au-dessus de bas (le halo des flèches du piège, HALO_FLECHE)"""
    return fab.titre(env, nom, css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(haut),
                                    "height": pc(bas - haut), "margin-bottom": 0, "padding-bottom": marge_bas,
                                    "-unity-text-align": "middle-center"})


def lignes_b(fab, cadre, traits):
    """v9 : le terrain des lignes de 26.13 (lignes()), recopié tel quel, sauf la relance courte du gardien (23) : une
    seule case, « oui » (PreventShortGKDistribution), au centre de la largeur et un peu plus grande (RELANCE_COURTE) ;
    case à bascule de FM : un clic l'applique, un 2e clic remet « non », l'option par défaut du jeu (Kinito).
    v13 (Kinito) : les deux cases « Non » / « Oui » côte à côte (RELANCE_COURTE_2), celle qui n'est pas choisie
    estompée ; les bandes de clic de la hauteur du pressing (8) et de la ligne défensive (9) sans infobulle : une fois
    apparue, elle gênait les clics suivants sur le terrain (il fallait en sortir pour recliquer) ; le badge de la ligne
    dit déjà l'option choisie"""
    champ = champ_terrain(fab, cadre, "lignes", traits)
    e = fab.enveloppe(champ, 8, "pressing-env", traverse=True)
    calque_selon(fab, e, 8, lambda par, k: ligne_consigne(fab, par, 8, k, Y_PRESSING[k], COUL["pressing"],
                                                          (True, False, COUL["voile-pressing"]), "pressing"),
                 "pressing-ligne")
    e = fab.enveloppe(champ, 9, "defense-env", traverse=True)
    calque_selon(fab, e, 9, lambda par, k: ligne_consigne(fab, par, 9, k, Y_LIGNE[k], COUL["defense"],
                                                          (False, True, COUL["voile-defense"]), "defense"),
                 "defense-ligne")
    for n, bandes in ((8, BANDES_PRESSING), (9, BANDES_LIGNE)):   # les bandes de clic, par-dessus les lignes
        e = fab.enveloppe(champ, n, f"bandes-env-{n}", traverse=True)
        for k, (y0, y1) in enumerate(bandes):
            bouton_b(fab, e, n, k, nu=True, texte=False, bulle=False,   # v13 : sans infobulle (v9 à v12 : bulle=True)
                          css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y0), "height": pc(y1 - y0)})
    e = fab.enveloppe(champ, 23, "relance-courte-env", traverse=True)
    titre_entre(fab, e, "relance-courte", 0, min(y for _, y, _, _ in RELANCE_COURTE_2.values()))   # v16 : centré
    ech = fab.echelle(23, (0, 1))   # la même échelle d'icône pour les deux cases
    for p, (x, y, w, h) in RELANCE_COURTE_2.items():   # v13 : « Non » et « Oui », l'autre estompée
        bouton_b(fab, case_abs(fab, e, f"relance-courte-{p}", x, y, w, h), 23, p, css={"flex-grow": 1}, icone=True,
                      echelle=ech, petit=True, texte=False, bulle=True, estompe=True)


def vue_comme_ensemble(fab):
    """v9 (Kinito) : les boutons « Cartes / Terrain » (posés par kinito_consignes_essai.bascule) à l'allure de « Vue
    d'ensemble » : la classe de FM du menu #PhasesDropdown (buttons-combo-button-base-default : fond, filet, coins,
    32 px de haut au plus) ; la vue affichée telle quelle, l'autre ASSOMBRIE (classe de FM dimmed-look : opacité 50 %,
    et rien d'autre). Le SIStyleSetter de chaque bouton (BindIntComparisonToAOrBUssClass sur kinitovue, posé sur son
    enfant) pose désormais « rien » si c'est sa vue, « dimmed-look » sinon ; rien d'autre ne change (événements, textes).
    v12 (Kinito) : « Terrain » d'abord, puis « Tuiles » (le bouton « cartes » : son mot vient de TUILES_LANGUES, posé par
    main), ECART_ENTETE entre eux ; les deux à la hauteur de « Vue d'ensemble » (comme_vue_ensemble) ; rien ne rétrécit :
    la rangée est poussée à droite par l'espace de l'en-tête, un mot plus long la fait donc grandir vers la gauche"""
    t = fab.t
    noms = {t.name(r): r for r in t.walk()}
    rangee = noms.get(f"{base.PREFIXE}-boutons-vue")
    if rangee is None:
        raise ValueError("boutons « Cartes / Terrain » (introuvable)")
    t.elem(rangee)["m_Classes"], t.elem(rangee)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    t.styles.style(t, rangee, {"flex-shrink": 0})
    reglages = {}
    for nom in ("cartes", "terrain"):
        reglage, bouton = noms.get(f"{base.PREFIXE}-allume-{nom}"), noms.get(f"{base.PREFIXE}-bouton-{nom}")
        if reglage is None or bouton is None or t.parent[reglage] != rangee:
            raise ValueError(f"bouton « {nom} » (introuvable)")
        f = t.sd(reglage)["BindFunction"]
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        if len(args) != 7 or not all(bytes(args[i][0]).endswith(b"StringVisualArg") for i in (3, 4)):
            raise ValueError(f"réglage du bouton « {nom} » : arguments inattendus (introuvable)")
        args[3][1], args[4][1] = _texte_arg(""), _texte_arg("dimmed-look")
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.elem(bouton)["m_Classes"] = ["buttons-combo-button-base-default"]
        comme_vue_ensemble(fab, bouton, f"vue-{nom}-langue")
        reglages[nom] = reglage
    if len(t.children(rangee)) != 2:
        raise ValueError("boutons « Cartes / Terrain » : forme inattendue (introuvable)")
    base.deplacer(t, reglages["terrain"], rangee, 0)   # v12 : Terrain, puis Tuiles
    t.styles.style(t, reglages["terrain"], {"flex-shrink": 0})
    t.styles.style(t, reglages["cartes"], {"flex-shrink": 0, "margin-left": ECART_ENTETE})


def comme_vue_ensemble(fab, bouton, nom_langue):
    """v12 (Kinito : « la même taille que le bouton Vue d'ensemble ») : un SIButton de l'en-tête (classe
    buttons-combo-button-base-default, comme le menu de FM : bordure de 1, align-items center) bâti comme « Vue
    d'ensemble » : son contenu (le conteneur de langue nom_langue, posé par selon_langue) fait au moins HAUT_ENTETE de
    haut, comme le champ du menu de FM, le texte centré dedans (le 1er interrupteur de langue ne s'étire plus : il
    garde la hauteur du texte) ; les marges du bouton de FM annulées (journal de la sonde du 13/10 : ~4,4 sur les côtés,
    ~1,7 en haut et en bas) ; il ne rétrécit jamais"""
    t = fab.t
    t.styles.style(t, bouton, {"margin-top": 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0,
                               "flex-shrink": 0})
    env = first(t, lambda r: t.name(r) == f"{base.PREFIXE}-{nom_langue}", root=bouton)
    sw0 = first(t, lambda r: t.name(r) == f"{base.PREFIXE}-{nom_langue}-0", root=bouton)
    if env is None or sw0 is None or t.parent[env] != bouton or t.parent[sw0] != env:
        raise ValueError(f"texte du bouton {t.name(bouton)} : forme inattendue (introuvable)")
    t.styles.style(t, env, {"min-height": HAUT_ENTETE, "justify-content": "center"})
    t.styles.style(t, sw0, {"flex-grow": 0})


# ---------- v10 : « Partir de zéro » (bouton de l'en-tête, fenêtre de confirmation de FM) ----------
class SourcesZero:
    """v10 : les morceaux de FM de la fenêtre de confirmation (GenericModalDialog : carte, titre, texte, rangée des
    boutons, bouton secondaire, case « Ne plus afficher ce message. ») et du bouton principal
    (buttons-button-primary-default), lus dans les originaux, jamais modifiés"""
    def __init__(self):
        f = ouvrir(SOURCE_FENETRE, depart_original=True)
        p = ouvrir(SOURCE_PRINCIPAL, depart_original=True)
        self.tf = tf = f[3] if f else None
        self.tp = tp = p[3] if p else None
        self.carte = self.contenu = self.cadre = self.textes = self.titre = self.texte = None
        self.actions = self.confirmer = self.place = self.secondaire = self.case = self.case_bouton = None
        self.traduit = self.principal = None
        if tf is not None:
            def nom(n, ty=None):
                return first(tf, lambda r: tf.name(r) == n and (ty is None or typ(tf, r) == ty))

            def classe(c):
                return first(tf, lambda r: c in (tf.elem(r).get("m_Classes") or []))
            self.carte = nom("dialog-card")
            self.contenu = classe("notifications--notifications-modal-dialog-default-default")
            self.cadre = nom("frame")
            self.textes = tf.children(self.cadre)[0] if self.cadre is not None and tf.children(self.cadre) else None
            self.titre = nom("dialog-title", "SIText")
            self.texte = nom("dialog-description", "SIText")
            self.actions = first(tf, lambda r: tf.name(r) == "notifications-modal-dialog-actions-default"
                                 and "row-direction-normal" in (tf.elem(r).get("m_Classes") or []))
            self.confirmer = classe("notifications-modal-dialog-actions-default-type-confirm")
            self.place = nom("buttons-button-quaternary-default", "VisualElement")
            self.secondaire = nom("buttons-button-quaternary-default", "SIButton")
            self.case = nom("do-not-show-panel")
            self.case_bouton = nom("dont-show-again-checkbox", "SICheckBox")
            self.traduit = self.case and first(tf, lambda r: typ(tf, r) == "SIText" and (
                ((tf.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
                "m_guid") == "eae2be944eee9e2449baef416111a087", root=self.case)
        if tp is not None:
            self.principal = first(tp, lambda r: tp.name(r) == SOURCE_PRINCIPAL and typ(tp, r) == "SIButton")

    def ok(self):
        if None in (self.carte, self.contenu, self.cadre, self.textes, self.titre, self.texte, self.actions,
                    self.confirmer, self.place, self.secondaire, self.case, self.case_bouton, self.traduit,
                    self.principal):
            return False
        tf, tp = self.tf, self.tp
        return ((tf.sd(self.case_bouton).get("SelectionBinding") or {}).get("m_path") == "doNotShowAgain"
                and [typ(tf, k) for k in tf.children(self.secondaire)] == ["SIText"]
                and "SIText" in [typ(tp, k) for k in tp.children(self.principal)]
                and (tf.sd(self.traduit).get("TextBinding") or {}).get("m_kind") == 2)


def recopie_seule(fab, ts, r, parent, nom, index=None):
    """v10 : un élément de FM recopié SANS ses enfants (ses classes, son style intégré et ses règles recopiées)"""
    t = fab.t
    c = t.clone(r, parent, index, src=ts)
    for k in list(t.children(c)):
        t.remove(k)
    t.styles.copy_from(ts.styles, t, c)
    recaler_parent(t, c)
    fab._nom(c, nom)
    return c


def recopie(fab, ts, r, parent, nom):
    """v10 : un élément de FM recopié avec ses enfants (styles recopiés : sinon le jeu plante, v3 de 26.13)"""
    t = fab.t
    c = t.clone(r, parent, src=ts)
    t.styles.copy_from(ts.styles, t, c)
    recaler_parent(t, c)
    fab._nom(c, nom)
    return c


def texte_fige(t, r, mot):
    """v10 : un SIText de FM qui affiche un texte fixe (recette de 26.4 : sa liaison et sa fonction de texte vidées)"""
    sd = t.sd(r)
    sd.update(text=mot, text_UxmlAttributeFlags=1, DebugDisplay=mot)
    tb = sd.get("TextBinding")
    if isinstance(tb, dict):
        tb["m_kind"] = 0
        tb["m_direct"]["Path"]["m_path"] = ""
        base.fonction_vide(tb["m_visualFunction"])
    f = sd.get("BindTextFunction")
    if isinstance(f, dict) and (f.get("m_target") or {}).get("m_guid"):
        base.fonction_vide(f)


def texte_langues(fab, texte, nom, langues, defaut):
    """v10 : le SIText texte remplacé, à sa place, par une copie par langue du jeu (selon_langue), texte fixe chacune
    (comme les mots de « Cartes / Terrain », kinito_consignes_essai.bascule)"""
    t = fab.t
    parent = t.parent[texte]
    rang = t.children(parent).index(texte)
    texte_fige(t, texte, defaut)

    def mot_(par, mot):
        c = t.clone_shallow(texte, par)
        fab.n += 1
        fab._nom(c, f"{nom}-{fab.n}")
        t.sd(c).update(text=mot, DebugDisplay=mot)
    env = fab.selon_langue(parent, f"{nom}-langue", mot_, langues, defaut, css={})
    base.deplacer(t, env, parent, rang)
    t.remove(texte)
    return env


def texte_traduit(fab, zs, parent, nom, ident, anglais):
    """v10 : le texte de la fenêtre de FM (dialog-description : sa classe, son style) qui affiche le texte n° ident de
    la table de l'interface de FM, TRADUIT PAR LE JEU : la liaison de traduction de la case « Ne plus afficher ce
    message. » (fonction eae2be944…, argument TranslationID = n° + texte anglais de secours) recopiée avec notre n°"""
    t = fab.t
    r = recopie(fab, zs.tf, zs.texte, parent, nom)
    tb = copy.deepcopy(zs.tf.sd(zs.traduit)["TextBinding"])
    f = tb["m_visualFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != 1 or not bytes(args[0][0]).endswith(b"[SI.Translation.TranslationID]"):
        raise ValueError("liaison de traduction de FM : arguments inattendus (introuvable)")
    args[0][1] = struct.pack("<i", ident) + _texte_arg(anglais)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd = t.sd(r)
    sd["TextBinding"], sd["TextBinding_UxmlAttributeFlags"] = tb, 1
    sd["DebugDisplay"] = anglais
    return r


def evenements(t, b, contenus):
    sd = t.sd(b)
    sd["Events"], sd["Events_UxmlAttributeFlags"] = {"m_bytes": liste(contenus)}, 1


def bouton_entete(fab, parent, nom, contenus):
    """v10 : « Partir de zéro » dans l'en-tête : le bouton de FM des boutons « Cartes / Terrain » (bouton segmenté des
    cartes de chaleur), à l'allure de « Vue d'ensemble » (buttons-combo-button-base-default, comme vue_comme_ensemble),
    son texte dans la langue du jeu (nom de FM du style) ; contenus : ce que le clic fait"""
    t, src = fab.t, fab.src
    th = src.th
    reglages = th.children(src.segments)
    modele = th.children(reglages[0])[0] if reglages and th.children(reglages[0]) else None
    if modele is None or typ(th, modele) != "SIButton":
        raise ValueError("bouton segmenté des cartes de chaleur (introuvable)")
    b = recopie(fab, th, modele, parent, nom)
    t.elem(b)["m_Classes"] = ["buttons-combo-button-base-default"]
    evenements(t, b, contenus)
    for k in list(t.children(b)):
        if t.name(k) == "controllers-keyboard-container":   # raccourci clavier de FM : pas le nôtre
            t.remove(k)
    texte = next((k for k in t.children(b) if typ(t, k) == "SIText"), None)
    if texte is None:
        raise ValueError("texte du bouton segmenté (introuvable)")
    t.elem(texte)["m_Classes"] = [c for c in t.elem(texte)["m_Classes"] if c != "margin-right-global-gap-regular"]
    texte_langues(fab, texte, f"{nom}-texte", ZERO_LANGUES, langue.texte("Partir de zéro", "Clean Slate"))
    comme_vue_ensemble(fab, b, f"{nom}-texte-langue")   # v12 : hauteur de « Vue d'ensemble », sans marges
    return b


def fenetre_zero(fab, zs, zone, style):
    """v10 : la fenêtre « êtes-vous sûr ? », faite des morceaux de la fenêtre de confirmation de FM, posée par-dessus
    tout le bloc des consignes (les deux vues) sur un voile sombre qui prend les clics ; montrée quand
    V_ZERO_FENETRE vaut 1 (SIStyleSetter de FM : hidden-item sinon). Titre « Partir de zéro » (nom de FM du style,
    langue du jeu), texte de FM « Are you sure you want to continue? » (traduit par le jeu), « Non » (bouton
    secondaire de FM) puis « Oui » (bouton principal de FM, à droite comme chez FM), la case de FM « Ne plus afficher
    ce message. » liée à V_ZERO_CASE. « Oui » : la case est retenue (V_ZERO_SANS, persistante), le style est choisi,
    la fenêtre se ferme ; « Non » : la fenêtre se ferme, la case est décochée"""
    t = fab.t
    tf = zs.tf
    voile = selon_classe(fab, zone, "zero-fenetre", V_ZERO_FENETRE, 1, "", CLASSE_CACHEE,
                         css={**PLEIN, "background-color": VOILE_ZERO, "justify-content": "center",
                              "align-items": "center"})
    carte = recopie_seule(fab, tf, zs.carte, voile, "zero-carte")
    contenu = recopie_seule(fab, tf, zs.contenu, carte, "zero-contenu")
    cadre = recopie_seule(fab, tf, zs.cadre, contenu, "zero-cadre")
    textes = recopie_seule(fab, tf, zs.textes, cadre, "zero-textes")
    titre = recopie(fab, tf, zs.titre, textes, "zero-titre")
    texte_langues(fab, titre, "zero-titre", ZERO_LANGUES, langue.texte("Partir de zéro", "Clean Slate"))
    texte_traduit(fab, zs, textes, "zero-question", *ID_SUR)
    actions = recopie_seule(fab, tf, zs.actions, cadre, "zero-actions")
    boutons = recopie_seule(fab, tf, zs.confirmer, actions, "zero-boutons")
    fermer = [copier("const.Zero", V_ZERO_FENETRE, 0), copier("const.False", V_ZERO_CASE, 0)]
    place = recopie_seule(fab, tf, zs.place, boutons, "zero-non-place")
    non = recopie(fab, tf, zs.secondaire, place, "zero-non")
    evenements(t, non, fermer)
    texte_langues(fab, t.children(non)[0], "zero-non-texte", NON_LANGUES, langue.texte("Non", "No"))
    place = recopie_seule(fab, tf, zs.place, boutons, "zero-oui-place")
    oui = recopie(fab, zs.tp, zs.principal, place, "zero-oui")
    for k in list(t.children(oui)):   # sans l'icône « tick » ni le chevron du modèle (comme les boutons de la fenêtre)
        if t.name(k) in ("ui-concepts-tick_small", "ui-concepts-chevron-right_small"):
            t.remove(k)
    evenements(t, oui, [copier(V_ZERO_CASE, V_ZERO_SANS, 1), style] + fermer)
    texte = next(k for k in t.children(oui) if typ(t, k) == "SIText")
    texte_langues(fab, texte, "zero-oui-texte", OUI_LANGUES, langue.texte("Oui", "Yes"))
    case = recopie(fab, tf, zs.case, contenu, "zero-case")
    coche = first(t, lambda r: typ(t, r) == "SICheckBox", root=case)
    t.sd(coche)["SelectionBinding"]["m_path"] = V_ZERO_CASE
    return voile


def partir_de_zero(fab):
    """v10 (Kinito) : le bouton « Partir de zéro » dans la rangée de l'en-tête, au centre de l'espace libre entre « Vue
    d'ensemble » et « Cartes » (choix de Kinito : centré pile sur la colonne du milieu, il chevauchait « Vue
    d'ensemble » d'environ 4 px, mesuré sur sa capture v9) : l'espace qui pousse « Cartes / Terrain » à droite est
    coupé en deux, le bouton entre les deux moitiés (même classe flex-grow-class de FM). Présent dans les deux vues
    (l'en-tête est au-dessus de l'interrupteur « Cartes / Terrain »). Un interrupteur de FM sur V_ZERO_SANS (Bool,
    comme « inpossession ») : faux -> le clic ouvre la fenêtre ; vrai (« Ne plus afficher » coché puis « Oui ») -> le
    clic choisit le style tout de suite.
    v12 (Kinito, 15/10 : « tu le places à côté de Vue d'ensemble, dans sa continuité ») : juste après la boîte de « Vue
    d'ensemble » (celle de FM, margin-left-8), ECART_ENTETE avant lui, et plus d'espace coupé en deux : l'espace de
    l'en-tête (celui de 26.13) vient après lui et pousse « Terrain / Tuiles » à droite"""
    t = fab.t
    zs = SourcesZero()
    if not zs.ok():
        raise ValueError("fenêtre de confirmation de FM (GenericModalDialog) ou bouton principal : forme inattendue "
                         "(introuvable)")
    espace = first(t, lambda r: t.name(r) == f"{base.PREFIXE}-espace")
    if espace is None:
        raise ValueError("espace de l'en-tête (introuvable)")
    rangee = t.parent[espace]
    i = t.children(rangee).index(espace)
    avant = t.children(rangee)[i - 1] if i else None
    if avant is None or first(t, lambda r: t.name(r) == "PhasesDropdown", root=avant) is None:
        raise ValueError("boîte de « Vue d'ensemble » juste avant l'espace de l'en-tête (introuvable)")
    style = copier(V_STYLE_ZERO, CHEMIN_STYLE, 1)   # ForceUpdate = 1 : réécrit même si le style vaut déjà 10
    sw = fab.interrupteur(rangee, "zero", V_ZERO_SANS, css={"flex-shrink": 0, "margin-left": ECART_ENTETE}, index=i)
    fab.traverse(sw)
    bouton_entete(fab, sw, "zero-demander", [copier("const.One", V_ZERO_FENETRE, 1)])   # rang 0 : faux
    bouton_entete(fab, sw, "zero-direct", [style])                                       # rang 1 : vrai
    zone = t.parent[t.parent[rangee]]
    fenetre_zero(fab, zs, zone, style)


# ---------- v6 : les morceaux de FM de l'échange (ceux de 26.6, lus dans les originaux, jamais modifiés) ----------
class SourcesEchange:
    def __init__(self):
        b = ouvrir(SOURCE_BOUTON[0], depart_original=True)
        self.tb = b[3] if b else None
        self.bouton = self.tb and first(self.tb, lambda r: self.tb.name(r) == SOURCE_BOUTON[1]
                                        and typ(self.tb, r) == "SIButton")
        a = ouvrir(SOURCE_ANNEAU[0], depart_original=True)
        self.ta = a[3] if a else None
        self.anneau = self.ta and first(self.ta, lambda r: self.ta.name(r) == SOURCE_ANNEAU[1])

    def ok(self):
        icones = self.bouton is not None and [k for k in self.tb.children(self.bouton)
                                              if typ(self.tb, k) == "VisualElement"]
        return (self.bouton is not None and self.anneau is not None and len(icones or []) == 1
                and len(self.tb.children(self.bouton)) == 1 and not self.ta.children(self.anneau))


def _texte_arg(s):
    b = s.encode("utf-8")
    if len(b) > 127:
        raise ValueError(f"classe trop longue : {s}")
    return bytes([1, len(b)]) + b


def selon_classe(fab, parent, nom, chemin, valeur, si_oui, si_non, css=None, index=None):
    """v6 : un SIStyleSetter de FM (celui d'un bouton segmenté des cartes de chaleur, vidé) qui pose sur LUI-MÊME la
    classe si_oui quand <chemin> == valeur, si_non sinon ("" : aucune) ; fonction BindIntComparisonToAOrBUssClass,
    qui retire la classe d'avant à chaque changement (SIStyleSetter.SetClassStyle, désassemblé le 12/10)"""
    t, src = fab.t, fab.src
    modele = next((r for r in src.th.children(src.segments) if typ(src.th, r) == "SIStyleSetter"), None)
    if modele is None:
        raise ValueError("SIStyleSetter des boutons segmentés de FM (introuvable)")
    s = t.clone(modele, parent, index, src=src.th)
    for k in list(t.children(s)):
        t.remove(k)
    recaler_parent(t, s)
    fab._nom(s, nom)
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    f = t.sd(s).get("BindFunction") or {}
    if (f.get("m_target") or {}).get("m_guid") != GUID_CLASSE:
        raise ValueError("fonction de classe des boutons segmentés de FM : autre que prévu (introuvable)")
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    fins = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
            b"BooleanVisualArg", b"BooleanVisualArg")
    if len(args) != len(fins) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, fins)):
        raise ValueError("fonction de classe des boutons segmentés de FM : arguments inattendus (introuvable)")
    args[0][1] = _texte_arg(chemin)
    args[1][1] = struct.pack("<i", 2)          # ComparisonOperator : égal
    args[2][1] = struct.pack("<i", valeur)
    args[3][1], args[4][1] = _texte_arg(si_oui), _texte_arg(si_non)
    args[5][1] = args[6][1] = bytes([0])       # ni sur l'enfant ni sur le parent : sur lui-même
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    if css:
        t.styles.style(t, s, css)
    return s


def cales(fab, rangee, k, nom):
    """v6 : dans une rangée, devant la colonne k : une cale vide par ordre où elle ne commence pas au bord gauche,
    large de son décalage ; seule celle de l'ordre en cours est montrée (les autres : hidden-item de FM)"""
    for p in range(len(ORDRES)):
        d = decalage(p, k)
        if d < 0.01:
            continue
        fab.traverse(selon_classe(fab, rangee, f"{nom}-cale-{p}", V_ORDRE, p, "", CLASSE_CACHEE,
                                  css={"width": pc(d), "flex-shrink": 0, "flex-grow": 0}))


def anneau(fab, ech, element, nom, chemin, valeur):
    """v6 : l'anneau blanc de FM (celui de la séance retenue, 26.6) sur tout l'élément, montré quand <chemin> ==
    valeur : notre SIStyleSetter pose alors la classe de FM dont #SelectionRing est l'enfant direct"""
    t = fab.t
    s = selon_classe(fab, element, nom, chemin, valeur, CLASSE_ANNEAU, "", css=PLEIN)
    fab.traverse(s)
    a = t.clone(ech.anneau, s, src=ech.ta)
    t.styles.copy_from(ech.ta.styles, t, a)
    recaler_parent(t, a)
    fab._nom(a, f"{nom}-cercle")
    fab.traverse(a)


def _drapeau(source):
    return 0 if source == "const.Zero" else 1   # comme FM (cartes de chaleur : 0 pour const.Zero, 1 pour const.One)


def bouton_echange(fab, ech, parent, nom, copies, jaune=False):
    """v6 : le bouton-icône de FM de 26.6 (poubelle des contrats), icône d'échange (jaune : ce qui est retenu) ;
    copies = [(constante, variable)] : ce que le clic écrit"""
    t = fab.t
    b = t.clone(ech.bouton, parent, src=ech.tb)
    t.styles.copy_from(ech.tb.styles, t, b)
    recaler_parent(t, b)
    fab._nom(b, nom)
    t.elem(b)["m_Classes"] = [BOUTON_NU]
    t.sd(b)["Events"] = {"m_bytes": liste([copier(c, v, _drapeau(c)) for c, v in copies])}
    t.sd(b)["Events_UxmlAttributeFlags"] = 1
    largeur, hauteur = ZONE_CLIC
    t.styles.style(t, b, {"width": largeur, "min-width": largeur, "height": hauteur, "min-height": hauteur,
                          "padding-top": 0, "padding-bottom": 0, "padding-left": 0, "padding-right": 0,
                          "flex-shrink": 0, "justify-content": "center", "align-items": "center", **DEBORD})
    icone = next(k for k in t.children(b) if typ(t, k) == "VisualElement")
    fab._nom(icone, f"{nom}-icone")
    t.elem(icone)["m_Classes"] = [ICONE_ECHANGE] + ([CLASSE_JAUNE] if jaune else [])
    t.styles.style(t, icone, {"width": ICONE, "height": ICONE})
    return b


def icone_grise(fab, parent, nom):
    """v6 : l'icône seule, estompée, sans clic (ce clic n'aurait pas de sens)"""
    fab.traverse(fab.boite(parent, nom, css={**TAILLE_ICONE, "opacity": GRISE}, classes=(ICONE_ECHANGE,)))


def interrupteur(fab, parent, nom, chemin):
    """v6 : interrupteur de FM (montre l'enfant n° <valeur de chemin>), à la taille de l'icône, sans prendre de clic"""
    s = fab.interrupteur(parent, nom, chemin, css=TAILLE_ICONE)
    fab.traverse(s)
    return s


def icone_colonne(fab, ech, parent, k, nom):
    """v6 : l'icône d'échange d'une colonne (deux clics, comme les séances) : grisée si un élément est retenu ; sinon,
    selon la colonne retenue : aucune -> la retenir ; elle-même -> annuler (icône jaune) ; une autre -> échanger les
    deux (une variante par ordre en cours : l'ordre d'après est écrit tel quel)"""
    sv = interrupteur(fab, parent, f"{nom}-elt", V_ELT)
    sc = interrupteur(fab, sv, f"{nom}-col", V_COL)            # enfant 0 de sv : aucun élément retenu
    for v in range(1, 7):
        icone_grise(fab, sv, f"{nom}-grise-{v}")
    for c in range(4):
        if c == 0:
            bouton_echange(fab, ech, sc, f"{nom}-retenir", [(PLACES[k + 1], V_COL)])
        elif c == k + 1:
            bouton_echange(fab, ech, sc, f"{nom}-annuler", [("const.Zero", V_COL)], jaune=True)
        else:
            so = interrupteur(fab, sc, f"{nom}-avec-{c - 1}", V_ORDRE)
            for p in range(len(ORDRES)):
                bouton_echange(fab, ech, so, f"{nom}-avec-{c - 1}-{p}",
                               [(PLACES[echange(p, k, c - 1)], V_ORDRE), ("const.Zero", V_COL)])


def icone_element(fab, ech, parent, k, part, nom):
    """v6 : l'icône d'échange haut / bas d'un élément de la colonne k (part 0 : terrain ou déclenchement ; 1 : tuile) :
    grisée si une colonne est retenue ; sinon, selon l'élément retenu : aucun -> le retenir ; lui-même -> annuler
    (jaune) ; l'autre élément de sa colonne -> échanger haut et bas ; un élément d'une autre colonne -> grisée"""
    code, autre = 1 + 2 * k + part, 1 + 2 * k + (1 - part)
    sc = interrupteur(fab, parent, f"{nom}-col", V_COL)
    sv = interrupteur(fab, sc, f"{nom}-elt", V_ELT)            # enfant 0 de sc : aucune colonne retenue
    for c in range(1, 4):
        icone_grise(fab, sc, f"{nom}-grise-c{c}")
    for v in range(7):
        if v == 0:
            bouton_echange(fab, ech, sv, f"{nom}-retenir", [(PLACES[code], V_ELT)])
        elif v == code:
            bouton_echange(fab, ech, sv, f"{nom}-annuler", [("const.Zero", V_ELT)], jaune=True)
        elif v == autre:
            sh = interrupteur(fab, sv, f"{nom}-hb", V_HB[k])
            for h in (0, 1):
                bouton_echange(fab, ech, sh, f"{nom}-echanger-{h}", [(PLACES[1 - h], V_HB[k]), ("const.Zero", V_ELT)])
        else:
            icone_grise(fab, sv, f"{nom}-grise-e{v}")


def coin(fab, ech, element, k, part, nom, centre=False):
    """v6 : sur un terrain ou une tuile de côté : l'anneau (élément retenu) et l'icône en haut à droite. v11 (Kinito,
    colonne du milieu seulement) : centre -> l'icône en haut AU MILIEU de la largeur (même hauteur), le titre dessous"""
    anneau(fab, ech, element, f"{nom}-anneau", V_ELT, 1 + 2 * k + part)
    cote = {"left": pc(50), "margin-left": -ICONE / 2} if centre else {"right": COIN}
    place = fab.boite(element, f"{nom}-place", css={"position": "absolute", "top": COIN, **cote, **TAILLE_ICONE})
    fab.traverse(place)
    icone_element(fab, ech, place, k, part, nom)


def titre_langues(fab, parent, nom, tailles, defaut, haut):
    """v9 : le titre de FM de l'enveloppe (le nom de la consigne, dans la langue du jeu), à la taille maximale qui tient
    pour CETTE langue (tailles : [(langue du jeu, px)], mesurées ; langue non prévue : defaut, la plus petite) : un
    titre par langue, derrière l'aiguillage de langue de FM (selon_langue). v10 (Kinito) : SOUS l'icône du coin (haut :
    marge au-dessus de la ligne, pour qu'elle commence à HAUT_TITRE_MILIEU du bord extérieur de la tuile), sur toute la
    largeur (la ligne déborde de DEBORD_TITRE sur les marges intérieures), hauteur = celle du texte (v9 : 16, sur la
    ligne de l'icône)"""
    rangee = fab.boite(parent, f"{nom}-tete", css={"flex-shrink": 0, "flex-direction": "row", "justify-content": "center",
                                                   "align-items": "center", "margin-top": haut, "margin-bottom": 1,
                                                   "margin-left": -DEBORD_TITRE, "margin-right": -DEBORD_TITRE})
    fab.traverse(rangee)

    def faire(par, taille):
        fab.n += 1
        fab.titre(par, f"{nom}-{fab.n}", css={"font-size": taille, "margin-bottom": 0, "white-space": "nowrap",
                                              "flex-grow": 1, "-unity-text-align": "middle-center"})
    fab.selon_langue(rangee, f"{nom}-langue", faire, tailles, defaut, css={"flex-grow": 1})


def gazon(fab, cadre, nom):
    """v3 : du gazon sans marquage (Kinito), aux bandes alignées sur celles des terrains voisins (même hauteur de
    bande : BANDE_HERBE % de la largeur) ; rend la zone. v6 : deux piles de bandes, l'une partant du haut (bande
    claire d'abord, comme le haut d'un terrain), l'autre du bas (bande sombre d'abord, comme le bas d'un terrain),
    montrées selon que la colonne du milieu est à l'endroit ou inversée : alignées sur les terrains quand ils sont du
    même côté"""
    c = fab.boite(cadre, f"{nom}-champ", css={"flex-grow": 1, "background-color": COUL["herbe2"], "overflow": "hidden"})
    for bas in (False, True):
        cote = "bas" if bas else "haut"
        pile = selon_classe(fab, c, f"{nom}-herbe-{cote}", V_HB[1], 1, "" if bas else CLASSE_CACHEE,
                            CLASSE_CACHEE if bas else "",
                            css={"position": "absolute", "left": 0, **({"bottom": 0} if bas else {"top": 0}),
                                 "width": pc(100), "flex-direction": "column-reverse" if bas else "column"})
        fab.traverse(pile)
        for i in range(NB_BANDES):   # en haut : claire, sombre… ; en bas : sombre, claire…
            fab.traverse(fab.boite(pile, f"{nom}-herbe-{cote}-{i}", css={
                "height": 0, "padding-bottom": pc(BANDE_HERBE), ("margin-top" if bas else "margin-bottom"): MARGE_BANDE,
                "flex-shrink": 0, **({"background-color": COUL["herbe1"]} if i % 2 == (1 if bas else 0) else {})}))
    return c


def declench(fab, colonne, css):
    """v3 : le déclenchement du pressing sur du gazon sans marquage : son nom en titre en haut (comme « Piège du
    pressing »), ses 5 crans en boutons de FM l'un sous l'autre (beaucoup plus souvent en haut), icônes seules à la
    taille de leur case, nom en infobulle, le cran choisi entouré de vert. v9 (Kinito) : titre centré sur la ligne de
    l'icône du coin (posée par coin()), à la taille maximale de sa langue. v10 (Kinito) : titre sous l'icône, sur toute
    la largeur ; écarts entre les crans 2 (v9 : 5), marge du bas 6 (v9 : 8) ; rend le cadre"""
    cadre = fab.boite(colonne, "declench", css={**CADRE_TERRAIN, **css})
    champ = gazon(fab, cadre, "declench")
    e = fab.enveloppe(champ, 10, "declench-env", traverse=True,
                      css={"flex-direction": "column", "padding-top": 0, "padding-bottom": BAS_DECLENCH,
                           "padding-left": 8, "padding-right": 8})
    # la ligne du titre sous l'icône du coin : bord du cadre 1 + marge intérieure 0 + 22 = HAUT_TITRE_MILIEU
    titre_langues(fab, e, "declench", TAILLES_DECLENCH, DEFAUT_DECLENCH, HAUT_TITRE_MILIEU - 1)
    ech = fab.echelle(10, CRANS_DECLENCH)
    for i, p in enumerate(CRANS_DECLENCH):   # v8 : estompés comme les autres consignes (Kinito) ; v18 (Kinito) : toujours
        #                                      estompés quand ils ne sont pas choisis, standard compris (v8 à v17 :
        #                                      seulement quand un autre cran que le standard l'était)
        bouton_b(fab, e, 10, p, icone=True, echelle=ech, petit=True, texte=False, bulle=True, plafond=PLAFOND_ICONE,
                      estompe=True, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                         "margin-top": ECART_BOUTONS_MILIEU if i else 0})
    return cadre


def bouton_b(fab, parent, n, p, css=None, **kw):
    """v15 (Kinito : « le 1er clic sélectionne, le 2e remet en standard », comme le piège du pressing) : le bouton de
    l'option p de la consigne n. L'option neutre de la consigne (DEFAUTS) : un bouton de FM simple ; les autres : une
    case à bascule (Fab.bascule : éteinte, elle choisit son option ; allumée, un clic remet l'option neutre), avec les
    mêmes réglages (estompe, icône, infobulle…) ; consignes sans option neutre (SANS_RETOUR) : bouton simple. Rend
    l'élément posé (css s'y applique)"""
    d = DEFAUTS.get(n)
    if d is None or p == d or n in SANS_RETOUR:
        return fab.option(parent, n, p, css=css, **kw)
    return fab.bascule(parent, n, p, d, css=css, **kw)


def tuile_b(fab, parent, n, place, colonne=False, tailles=None):
    """une tuile « sans le ballon » (Kinito) : titre EN HAUT, les deux cases remplissent la place qui reste, côte à
    côte, ou l'une sous l'autre (colonne, v3 : Transition défensive). v1 (tuile() de 26.13) : titre en bas de sa
    place, 83 px de vide au-dessus. v4 : la tuile est posée dans une boîte simple qui prend sa place (place : flex-grow,
    marges) et dans laquelle elle s'étire, comme en v2 (vu en jeu). v9 : tailles = (table par langue, défaut) : titre
    centré sur la ligne de l'icône du coin, à la taille maximale de sa langue (titre_langues) ; v10 : sous l'icône du
    coin, sur toute la largeur, écart entre les cases ECART_BOUTONS_MILIEU (v9 : 6), marge du bas BAS_TRANSITION (v9 : 6) ;
    v13 (Kinito) : les consignes de TUILES_3 montrent leurs trois options dans l'ordre donné (option par défaut au
    milieu, avec son icône de FM), boutons de FM simples (plus de bascule), ceux qui ne sont pas choisis toujours
    estompés ; la tuile garde sa taille, elle est coupée en trois cases au lieu de deux ; rend la boîte"""
    if n in CRANS:
        raise ValueError(f"tuile_b : la consigne {n} est en crans (tuile() de 26.13)")
    boite = fab.boite(parent, f"tuile-{n}-place", css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, **place,
                                                       "flex-direction": "row"})
    e = fab.enveloppe(boite, n, f"tuile-{n}", css={**CASE, "justify-content": "flex-start",
                                                    **({} if tailles is None else {"padding-bottom": BAS_TRANSITION})})
    degrade(fab, e, f"tuile-{n}")
    if tailles is None:
        fab.titre(e, f"tuile-{n}")   # en haut (titre de FM : centré, en capitales, 4 px dessous)
    else:   # v10 : la ligne du titre sous l'icône du coin : bord 1 + marge intérieure de la case (6) + 16 = 23
        titre_langues(fab, e, f"tuile-{n}", *tailles, HAUT_TITRE_MILIEU - 1 - CASE["padding-top"])
    rang = fab.boite(e, f"tuile-{n}-boutons", css={"flex-direction": "column" if colonne else "row", "flex-grow": 1})
    if n in TUILES_3:   # v13
        places, defaut = TUILES_3[n], None
    else:
        places, defaut = BASCULES.get(n, (tuple(range(len(fab.src.options[n]))), None))
    ech = fab.echelle(n, places)
    ecart = 6 if tailles is None else ECART_BOUTONS_MILIEU
    for j, p in enumerate(places):
        css_ = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                ("margin-top" if colonne else "margin-left"): ecart if j else 0}
        kw = dict(icone=True, echelle=ech, petit=True, texte=False, bulle=True, plafond=PLAFOND_ICONE,
                  rempli=REMPLI_TUILES_SANS,
                  **({"estompe": True} if n in TUILES_3 else {"assombrir": True}))
        if n in TUILES_3:   # v15 : 2e clic -> option neutre (bouton_b)
            bouton_b(fab, rang, n, p, css=css_, **kw)
        elif defaut is None:
            fab.option(rang, n, p, css=css_, **kw)
        else:
            fab.bascule(rang, n, p, defaut, css=css_, **kw)
    return boite


def texte_vertical_plein(fab, var):
    """v13 (Kinito : « grossis la police d'Empêcher de centrer, utilise toute la hauteur de la case ») : le texte
    vertical d'une option (option(vertical=True), écrit de bas en haut par un quart de tour) en TEXTE_EMPECHER, dans une
    boîte presque aussi longue que la case est haute (LARGEUR_EMPECHER, en % de sa largeur), sur deux lignes s'il le
    faut (langues aux textes longs). v15 : var peut être une case à bascule (deux boutons de FM, un texte chacun)"""
    t = fab.t
    txts = [r for r in t.walk(var) if typ(t, r) == "SIText"]
    if not 1 <= len(txts) <= 2:
        raise ValueError("texte vertical d'une option : forme inattendue")
    w = LARGEUR_EMPECHER
    for txt in txts:
        t.styles.style(t, txt, {"width": pc(w), "margin-left": pc(-w / 2), "height": HAUT_EMPECHER,
                                "margin-top": -HAUT_EMPECHER / 2, "white-space": "normal",
                                "font-size": TEXTE_EMPECHER})


def piege_b(fab, cadre, traits):
    """v13 : le terrain du piège du pressing (25) et du pressing sur centres (22) de 26.13 (piege()), recopié, sauf
    (Kinito, 28/10) : chaque option choisie seule, les autres toujours estompées (estompe=True) ; « Équilibré » en texte
    à l'allure d'« Équilibrées » des relances du gardien (option de FM, classe label-sm, TEXTE_ZONES), sous « Attirer
    vers l'axe » pour le piège (EQUILIBRE_PIEGE), à la place de son icône pour les centres (EQUILIBRE_CENTRES) ;
    « Empêcher de centrer » plus grand (texte_vertical_plein). v15 : 2e clic sur « Empêcher de centrer » ou « Laisser
    centrer » -> « Équilibré » (bouton_b) ; « Équilibré » des centres à l'allure d'« Empêcher de centrer ». v16
    (Kinito) : « Équilibré » du piège pareil (equilibre_grand), les cases du piège remontées pour lui faire la place
    (PIEGE_CASES, PIEGE_FLECHES) ; les deux titres centrés dans leur écart (titre_entre), au-dessus des flèches"""
    champ = champ_terrain(fab, cadre, "piege", traits)
    e = fab.enveloppe(champ, 25, "piege-env", traverse=True)
    calque_selon(fab, e, 25, lambda par, k: base.fleches(fab, par, k, "piege", base.FLECHES_PIEGE, PIEGE_FLECHES),
                 "piege-fleches")
    titre_entre(fab, e, "piege", 0, PIEGE_FLECHES[0], HALO_FLECHE)
    ech = fab.echelle(25, (0, 2))
    y, h = PIEGE_CASES
    for p, x, w in ((2, 2, 23), (0, 30, 40), (2, 75, 23)):   # côtés sur les flancs, axe au milieu (comme 26.13)
        fab.bascule(case_abs(fab, e, f"piege-{p}-{x}", x, y, w, h), 25, p, 1, css={"flex-grow": 1}, icone=True,
                    echelle=ech, part=(23 / w, 1.0), petit=True, texte=False, bulle=True, estompe=True)
    equilibre_grand(fab, e, 25, "piege-1-equilibre", EQUILIBRE_PIEGE)
    e = fab.enveloppe(champ, 22, "centres-env", traverse=True)
    calque_selon(fab, e, 22, lambda par, k: base.fleches(fab, par, k, "centres", base.FLECHES_CENTRES,
                                                         (CENTRES_FLECHES,)),
                 "centres-fleches")
    # v17 : dans sa moitié de terrain : sous la ligne médiane (« Équilibré » du piège finit au-dessus, à 45,7 %)
    titre_entre(fab, e, "centres-sans", max(50, EQUILIBRE_PIEGE[1] + EQUILIBRE_PIEGE[3]), CENTRES_FLECHES,
                HALO_FLECHE)
    ech = fab.echelle(22, (1, 2))   # comme 26.13 : « Laisser centrer » garde la taille de son icône
    for p, x, y, w, h in ((0, 2, 61, 23, 37), (2, 29, 74, 42, 24), (0, 75, 61, 23, 37)):
        cote_ = p == 0   # « Empêcher de centrer » sur les côtés, écrit à la verticale
        var = bouton_b(fab, case_abs(fab, e, f"centres-{p}-{x}", x, y, w, h), 22, p, icone=not cote_, echelle=ech,
                            petit=True, vertical=cote_, texte=cote_, bulle=not cote_, estompe=True,
                            css={"flex-grow": 1}, taille_texte=TEXTE_ZONES if cote_ else None)
        if cote_:
            texte_vertical_plein(fab, var)
    equilibre_grand(fab, e, 22, "centres-1-equilibre", EQUILIBRE_CENTRES)


def equilibre_grand(fab, env, n, nom, zone):
    """v15 (Kinito : « plus gros, harmonieux avec sa case ») : « Équilibré » (option neutre, place 1) du pressing sur
    centres à l'allure des deux « Empêcher de centrer » de sa consigne : même classe, TEXTE_EMPECHER, capitales ;
    v16 : celui du piège aussi. zone = (x, y, largeur, hauteur) en % du terrain"""
    x, y, w, h = zone
    var = fab.option(case_abs(fab, env, nom, x, y, w, h), n, 1, petit=True, taille_texte=TEXTE_EMPECHER, estompe=True,
                     css={"flex-grow": 1})
    for txt in (r for r in fab.t.walk(var) if typ(fab.t, r) == "SIText"):
        sd = fab.t.sd(txt)
        if "TextCase" in sd:   # en capitales, comme le texte vertical de Fab.option
            sd["TextCase"], sd["TextCase_UxmlAttributeFlags"] = 1, 1


def a_sa_place(k):
    """v6 : la place de la colonne k dans une rangée de cales : sa largeur, sans grandir ni rétrécir"""
    return {"width": pc(LARG[k]), "flex-basis": pc(LARG[k]), "flex-grow": 0, "flex-shrink": 0}


def sans_b(fab, conteneur):
    """sans le ballon, disposition de Kinito (voir en tête). v6 : trois calques pleine largeur, un par colonne, posés
    à leur place par des cales ; haut / bas par la direction de la colonne (classes de FM)"""
    ech = SourcesEchange()
    if not ech.ok():
        raise ValueError("bouton d'échange (ContractNegotiationAddOnItem) ou anneau de FM (introuvable)")
    # 1. les titres des colonnes, avec l'icône d'échange à côté : celui de la colonne 0 dans le flux (il donne la
    # hauteur de la rangée, comme les titres de côté de la v5) ; les deux autres en calques par-dessus
    titres = fab.boite(conteneur, "sans-titres", css={"flex-direction": "row", "margin-bottom": 4})
    for k in range(len(TITRES_SANS)):
        if k == 0:
            rangee = titres
        else:
            rangee = fab.boite(titres, f"sans-titres-calque-{k}", css={**PLEIN, "flex-direction": "row"})
            fab.traverse(rangee)
        cales(fab, rangee, k, f"sans-titre-{k}")
        tete = fab.boite(rangee, f"sans-entete-{k}", css={**a_sa_place(k), "flex-direction": "row",
                                                           "justify-content": "center", "align-items": "flex-end"})
        fab.traverse(tete)
        # v9 (Kinito) : les trois titres pareils (taille du texte de FM, thematic-sm) ; le TEXTE seul centré sur sa
        # colonne (il peut en déborder des deux côtés, la colonne du milieu est étroite) ; l'icône posée juste après
        # lui, hors du centrage
        groupe = fab.boite(tete, f"sans-entete-{k}-groupe", css={"flex-shrink": 0, "flex-direction": "row",
                                                                 "align-items": "flex-end"})
        fab.traverse(groupe)

        def titre_(par, mots, k=k):   # dans la langue du jeu, comme 26.13
            fab.n += 1
            fab.texte_fixe(par, f"sans-titre-{k}-{fab.n}", mots[k], classe="thematic-sm",
                           css={"-unity-text-align": "lower-center", "white-space": "nowrap"})
        fab.selon_langue(groupe, f"sans-titre-{k}", titre_, TITRES_SANS_LANGUES, TITRES_SANS, css={"flex-shrink": 0})
        place = fab.boite(groupe, f"sans-entete-{k}-echange", css={**TAILLE_ICONE, "position": "absolute",
                                                                   "left": pc(100), "bottom": 2, "margin-left": 4})
        fab.traverse(place)
        icone_colonne(fab, ech, place, k, f"echange-colonne-{k}")
    # 2. le corps : rien dans le flux (il prend la place qui reste), trois calques pleine largeur par-dessus
    corps = fab.boite(conteneur, "sans-corps", css={"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1,
                                                    "flex-basis": 0})
    for k, n_tuile, terrain in ((0, 15, "lignes"), (2, 12, "piege")):
        # colonne de côté : la rangée du terrain (hauteur en % de la largeur du bloc, v5), un écart, la rangée de la
        # tuile (le reste) ; la direction (classe de FM) met le terrain en haut ou en bas
        cal = selon_classe(fab, corps, f"sans-calque-{k}", V_HB[k], 1, CLASSES_HB[1], CLASSES_HB[0], css=PLEIN)
        fab.traverse(cal)
        haut = fab.boite(cal, f"sans-haut-{k}", css={"height": 0, "padding-bottom": pc(HAUT_TERRAINS),
                                                      "flex-shrink": 0})
        fab.traverse(haut)
        dedans = fab.boite(haut, f"sans-haut-dedans-{k}", css={**PLEIN, "flex-direction": "row"})
        fab.traverse(dedans)
        cales(fab, dedans, k, f"sans-terrain-{k}")
        cadre = fab.boite(dedans, f"sans-cadre-{k}", css={**a_sa_place(k), **CADRE_TERRAIN})
        if terrain == "lignes":
            lignes_b(fab, cadre, traits_reels(True, True))   # v9 : relance courte en une case
        else:
            piege_b(fab, cadre, traits_reels(False, True, True))   # v13 (v5 à v12 : piege() de 26.13)
        coin(fab, ech, cadre, k, 0, f"echange-{k}-terrain")
        fab.traverse(fab.boite(cal, f"sans-ecart-{k}", css={"height": 8, "flex-shrink": 0}))
        bas = fab.boite(cal, f"sans-bas-{k}", css={"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1,
                                                    "flex-basis": 0, "min-height": 90})
        fab.traverse(bas)
        cales(fab, bas, k, f"sans-tuile-{k}")
        boite = tuile_b(fab, bas, n_tuile, a_sa_place(k))   # Comportement de la ligne / En taclant
        coin(fab, ech, boite, k, 1, f"echange-{k}-tuile")
    # la colonne du milieu : déclenchement du pressing (3/5), un écart, Transition défensive (2/5) ; la direction
    # (classe de FM) les échange
    cal = fab.boite(corps, "sans-calque-1", css={**PLEIN, "flex-direction": "row"})
    fab.traverse(cal)
    cales(fab, cal, 1, "sans-milieu")
    milieu = selon_classe(fab, cal, "sans-colonne-1", V_HB[1], 1, CLASSES_HB[1], CLASSES_HB[0], css=a_sa_place(1))
    fab.traverse(milieu)
    cadre = declench(fab, milieu, {"flex-grow": PARTS_MILIEU[0], "flex-shrink": 1, "flex-basis": 0})
    coin(fab, ech, cadre, 1, 0, "echange-1-declench", centre=True)   # v11 : icône en haut au milieu (Kinito ; v9 / v10 : dans le coin)
    fab.traverse(fab.boite(milieu, "sans-ecart-1", css={"height": 8, "flex-shrink": 0}))
    boite = tuile_b(fab, milieu, 11, {"flex-grow": PARTS_MILIEU[1]}, colonne=True,
                    tailles=(TAILLES_TRANSITION, DEFAUT_TRANSITION))
    coin(fab, ech, boite, 1, 1, "echange-1-tuile", centre=True)   # v11 : au milieu aussi
    # 3. l'anneau de la colonne retenue, sur toute sa hauteur (un calque par colonne, posé comme elle)
    for k in range(len(TITRES_SANS)):
        couche = fab.boite(corps, f"sans-anneau-calque-{k}", css={**PLEIN, "flex-direction": "row"})
        fab.traverse(couche)
        cales(fab, couche, k, f"sans-anneau-{k}")
        place = fab.boite(couche, f"sans-anneau-place-{k}", css=a_sa_place(k))
        fab.traverse(place)
        anneau(fab, ech, place, f"echange-colonne-{k}-anneau", V_COL, k + 1)


def declarer(fab, racine):
    """v6 : nos variables, déclarées avec celle du bouton « Cartes / Terrain » (composant du bloc posé par
    kinito_consignes_essai.bascule) ; l'ordre et les haut / bas avec une clé « Persistent », comme la variable
    « Avec / Sans le ballon » de FM (TacticalPlannerTeamInstructions : inpossession)"""
    t = fab.t
    zone = t.parent[t.parent[racine]]
    var = next((k for k in t.children(zone) if t.elem(k).get("m_FullTypeName") == "SI.Bindable.BindingVariablesComponent"
                and any(f"{{{base.VARIABLE}}}" in (p.get("value") or "") for p in t.elem(k).get("m_Properties") or [])),
               None)
    if var is None:
        raise ValueError("variable « Cartes / Terrain » du bloc (introuvable)")
    props = [p for p in t.elem(var).get("m_Properties") or [] if p.get("name") == "value-vars"]
    donnees = [r["data"] for r in t.refs.values() if r and "ValueVariables" in (r.get("data") or {})
               and r["data"].get("uxmlAssetId") == t.elem(var)["m_Id"]]
    if len(props) != 1 or len(donnees) != 1 or not donnees[0]["ValueVariables"]:
        raise ValueError("déclaration de la variable « Cartes / Terrain » : forme inattendue (introuvable)")
    modele = donnees[0]["ValueVariables"][0]
    # v12 (Kinito, 15/10 : « si l'utilisateur va sur Tuiles et y reste, quand il revient il doit être sur Tuiles, et
    # inversement ») : la vue affichée (base.VARIABLE, 0 = tuiles de FM, 1 = terrain) devient « Persistent » comme
    # l'ordre des colonnes (v6, gardé d'une ouverture à l'autre en jeu) ; base.VUE_DEPART (terrain) n'est que la valeur
    # de la toute première fois
    avant = f"{{{base.VARIABLE}}}{{Int|{base.VUE_DEPART}|}}"
    vue = f"Int|{base.VUE_DEPART}|{persistant('vue')}"
    if props[0]["value"].count(avant) != 1 or modele.get("m_name") != base.VARIABLE \
            or modele["m_scopeValue"]["m_serializedData"] != f"Int|{base.VUE_DEPART}|":
        raise ValueError("déclaration de la variable « Cartes / Terrain » : forme inattendue (introuvable)")
    props[0]["value"] = props[0]["value"].replace(avant, f"{{{base.VARIABLE}}}{{{vue.replace(',', '&#44;')}}}")
    modele["m_scopeValue"]["m_serializedData"] = vue
    props[0]["value"] += "".join(",{" + nom + "}{" + valeur.replace(",", "&#44;") + "}" for nom, valeur in VARIABLES)
    modele = copy.deepcopy(modele)
    modele["m_scopeValue"]["m_serializedData"] = f"Int|{base.VUE_DEPART}|"   # le modèle des nôtres : tel qu'avant
    for nom, valeur in VARIABLES:
        v = copy.deepcopy(modele)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = nom, valeur
        donnees[0]["ValueVariables"].append(v)


# ---------- v7 : « avec le ballon » ----------
def disposition(pos, rev):
    """v7 : de haut en bas, les éléments d'une colonne « avec » (0 tuile du haut d'origine, 1 terrain, 2 tuile du bas
    d'origine) pour une place du terrain (pos) et un ordre des tuiles (rev)"""
    tuiles = iter((0, 2) if rev == 0 else (2, 0))
    return [1 if s == pos else next(tuiles) for s in range(3)]


def echange_vertical(pos, rev, a, b):
    """v7 : (place du terrain, ordre des tuiles) après l'échange des éléments a et b d'une colonne"""
    d = disposition(pos, rev)
    ia, ib = d.index(a), d.index(b)
    d[ia], d[ib] = b, a
    return d.index(1), 0 if d.index(0) < d.index(2) else 1


def cales_avec(fab, rangee, k, nom, apres):
    """v7 : les cales « avec le ballon » (trois colonnes de même largeur, 10 px entre elles, comme avant) : à la place s,
    la colonne k (une part) a devant elle une cale de s parts et de marge 10 × s, derrière elle une cale de 2 - s parts
    et de marge 10 × (2 - s) ; la place libre se partage en 3 parts égales, comme les trois colonnes d'avant"""
    for p in range(len(ORDRES)):
        s = ORDRES[p].index(k)
        n = (2 - s) if apres else s
        if n == 0:
            continue
        css = {"flex-grow": n, "flex-shrink": 1, "flex-basis": 0,
               ("margin-left" if apres else "margin-right"): ECART_AVEC * n}
        fab.traverse(selon_classe(fab, rangee, f"{nom}-cale-{'apres' if apres else 'avant'}-{p}", V_AORDRE, p, "",
                                  CLASSE_CACHEE, css=css))


def anneau_deux(fab, ech, element, nom, chemin1, valeur1, chemin2, valeur2):
    """v7 : l'anneau de FM quand chemin1 == valeur1 ET chemin2 == valeur2 (deux SIStyleSetter l'un dans l'autre)"""
    s = selon_classe(fab, element, nom, chemin1, valeur1, "", CLASSE_CACHEE, css=PLEIN)
    fab.traverse(s)
    anneau(fab, ech, s, f"{nom}-2", chemin2, valeur2)


def icone_colonne_avec(fab, ech, parent, k, nom):
    """v7 : l'icône d'échange d'une colonne « avec » (comme icone_colonne, sur les variables « avec »)"""
    se = interrupteur(fab, parent, f"{nom}-elt", V_AECOL)
    sc = interrupteur(fab, se, f"{nom}-col", V_ACOL)          # enfant 0 de se : aucun élément retenu
    for c in range(1, 4):
        icone_grise(fab, se, f"{nom}-grise-{c}")
    for c in range(4):
        if c == 0:
            bouton_echange(fab, ech, sc, f"{nom}-retenir", [(PLACES[k + 1], V_ACOL)])
        elif c == k + 1:
            bouton_echange(fab, ech, sc, f"{nom}-annuler", [("const.Zero", V_ACOL)], jaune=True)
        else:
            so = interrupteur(fab, sc, f"{nom}-avec-{c - 1}", V_AORDRE)
            for p in range(len(ORDRES)):
                bouton_echange(fab, ech, so, f"{nom}-avec-{c - 1}-{p}",
                               [(PLACES[echange(p, k, c - 1)], V_AORDRE), ("const.Zero", V_ACOL)])


def icone_element_avec(fab, ech, parent, k, e, nom):
    """v7 : l'icône d'un élément e (0 tuile du haut d'origine, 1 terrain, 2 tuile du bas d'origine) de la colonne k :
    grisée si une colonne est retenue ; sinon, selon l'élément retenu : aucun -> le retenir ; lui-même -> annuler
    (jaune) ; un autre élément de SA colonne -> échanger les deux (une variante par place du terrain et ordre des
    tuiles en cours : le rangement d'après est écrit tel quel) ; un élément d'une autre colonne -> grisée"""
    sc = interrupteur(fab, parent, f"{nom}-col", V_ACOL)
    se = interrupteur(fab, sc, f"{nom}-ecol", V_AECOL)        # enfant 0 de sc : aucune colonne retenue
    for c in range(1, 4):
        icone_grise(fab, sc, f"{nom}-grise-c{c}")
    for c in range(4):
        if c == 0:
            bouton_echange(fab, ech, se, f"{nom}-retenir", [(PLACES[k + 1], V_AECOL), (PLACES[e + 1], V_AEELT)])
        elif c != k + 1:
            icone_grise(fab, se, f"{nom}-grise-e{c}")
        else:
            sl = interrupteur(fab, se, f"{nom}-elt", V_AEELT)
            for v in range(4):
                if v == e + 1:
                    bouton_echange(fab, ech, sl, f"{nom}-annuler", [("const.Zero", V_AECOL), ("const.Zero", V_AEELT)],
                                   jaune=True)
                elif v == 0:
                    icone_grise(fab, sl, f"{nom}-grise-rien")
                else:
                    sp = interrupteur(fab, sl, f"{nom}-avec-{v - 1}", V_APOS[k])
                    for pos in range(3):
                        sr = interrupteur(fab, sp, f"{nom}-avec-{v - 1}-p{pos}", V_AREV[k])
                        for rev in (0, 1):
                            npos, nrev = echange_vertical(pos, rev, e, v - 1)
                            bouton_echange(fab, ech, sr, f"{nom}-avec-{v - 1}-p{pos}-r{rev}",
                                           [(PLACES[npos], V_APOS[k]), (PLACES[nrev], V_AREV[k]),
                                            ("const.Zero", V_AECOL), ("const.Zero", V_AEELT)])


def coin_avec(fab, ech, element, k, e, nom):
    """v7 : sur un élément « avec » : l'anneau (élément retenu) et l'icône en haut à droite"""
    anneau_deux(fab, ech, element, f"{nom}-anneau", V_AECOL, k + 1, V_AEELT, e + 1)
    place = fab.boite(element, f"{nom}-place", css={"position": "absolute", "top": COIN, "right": COIN,
                                                     **TAILLE_ICONE})
    fab.traverse(place)
    icone_element_avec(fab, ech, place, k, e, nom)


def tuile_avec_b(fab, rangee, n, css):
    """une tuile « avec le ballon » : tuile() de 26.13 (icônes seules, titre en bas de sa place), recopiée, sauf
    (Kinito) : v8 : Rythme et Perdre du temps estompés comme les autres consignes (tuile_crans_b) ; v14 : TOUTES les
    tuiles par ici, boutons de FM simples (plus de case à bascule), ceux qui ne sont pas choisis toujours estompés ;
    Transition offensive en trois cases (TROIS_AVEC) ; rend la tuile"""
    e = fab.enveloppe(rangee, n, f"tuile-{n}", css={**CASE, "margin-left": 0, "justify-content": "flex-start", **css})
    degrade(fab, e, f"tuile-{n}")
    fab.titre(e, f"tuile-{n}", css={"flex-grow": 1, "-unity-text-align": "lower-center"})
    rang = fab.boite(e, f"tuile-{n}-boutons", css={"flex-direction": "row", "justify-content": "center"})
    places = TROIS_AVEC.get(n, tuple(range(len(fab.src.options[n]))))
    ech = fab.echelle(n, places)
    ecart = 4 if n in CRANS else 6   # comme tuile() de 26.13
    for j, p in enumerate(places):
        bouton_b(fab, rang, n, p, icone=True, echelle=ech, texte=False, petit=True, bulle=True, estompe=True,
                      css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "margin-left": ecart if j else 0,
                           "height": HAUT_TUILE})
    return e


def relance_b(fab, cadre):
    """v8 : le terrain « Relance » de 26.13 (relance()), recopié, sauf (Kinito) : plus de fond derrière « Réception des
    passes » : les bandes d'herbe couvrent la réception et le terrain, comme sur les deux autres terrains ;
    « Équilibrées » à droite (ZONES_GB_B) ; « RELANCER VERS » sur deux lignes à gauche du gardien, police des titres de
    tuiles (FM nomme la consigne « Relances GB », qu'on ne comprend pas). v14 : réception des passes, sorties de but et
    relances GB (vitesse) en trois cases (TROIS_AVEC), boutons de FM simples, ceux qui ne sont pas choisis toujours
    estompés ; les zones « Relancer vers » aussi (à leur place)"""
    t = fab.t
    zone = fab.boite(cadre, "relance-zone", css={"flex-grow": 1, "flex-direction": "column",
                                                 "background-color": COUL["herbe2"], "overflow": "hidden"})
    for i in range(5):   # comme champ_terrain : une bande claire sur deux, 10 % de la hauteur chacune
        fab.traverse(fab.boite(zone, f"relance-herbe-{i}", css={"position": "absolute", "left": 0, "width": pc(100),
                                                                "top": pc(20 * i), "height": pc(10),
                                                                "background-color": COUL["herbe1"]}))
    haut = fab.boite(zone, "reception", css={k: v for k, v in BANDE.items() if k != "background-color"})
    e = fab.enveloppe(haut, 20, "reception-env", css={"flex-direction": "column"})
    fab.titre(e, "reception")
    duo = fab.boite(e, "reception-duo", css={"flex-direction": "row"})
    places = TROIS_AVEC[20]
    ech = fab.echelle(20, places)
    for i, p in enumerate(places):
        bouton_b(fab, duo, 20, p, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                                       "margin-left": 6 if i else 0},
                      icone=True, echelle=ech, petit=True, texte=False, bulle=True, estompe=True)
    champ = fab.boite(zone, "relance-champ", css={"flex-grow": 1, "min-height": 160})   # sans fond : la zone le porte
    for n, css in sans_but(TRAITS_RELANCE):   # v16 : plus de but
        fab.traverse(fab.boite(champ, f"relance-{n}", css={"position": "absolute", **css}))
    e = fab.enveloppe(champ, 16, "gb-env", traverse=True)
    for p, zones in ZONES_GB_B.items():   # v14 : les zones qui ne sont pas choisies toujours estompées (Kinito : même
        #                                   quand « Équilibrées » l'est ; v8 à v13 : seulement quand une autre l'était)
        for x, y, w, h in zones:
            bouton_b(fab, e, 16, p, petit=True, classe="label-sm", estompe=True, taille_texte=TEXTE_ZONES,
                          css={"position": "absolute", "left": pc(x), "top": pc(y), "width": pc(w), "height": pc(h)})
    x, y, w, h = ZONE_TITRE_GB   # « RELANCER VERS », dans la langue du jeu (NOS traductions)
    place = fab.boite(champ, "relancer-vers", css={"position": "absolute", "left": pc(x), "top": pc(y), "width": pc(w),
                                                   "height": pc(h)})
    fab.traverse(place)

    def mot(par, texte):
        fab.n += 1
        r = fab.texte_fixe(par, f"relancer-vers-{fab.n}", texte, classe="thematic-xs",
                           css={"flex-grow": 1, "-unity-text-align": "middle-center", "white-space": "normal"})
        t.elem(r)["m_Classes"] = ["thematic-xs", "global-text-secondary"]   # comme les titres des tuiles (Fab.titre)
        fab.traverse(r)
    fab.selon_langue(place, "relancer-vers-langue", mot, RELANCER_VERS_LANGUES, RELANCER_VERS, css={"flex-grow": 1})
    fab.traverse(fab.boite(champ, "gardien-point", css={"position": "absolute", "left": pc(50), "top": pc(95), "width": 13,
                                                        "height": 13, "margin-left": -6.5, "margin-top": -6.5,
                                                        "background-color": COUL["blanc"],
                                                        **cadre_css(2, COUL["gardien"], pc(50))}))
    bas = fab.boite(cadre, "gardien", css={**BANDE_BAS, "flex-direction": "row"})   # la bande du bas : comme 26.13
    for j, n in enumerate((29, 17)):
        e = fab.enveloppe(bas, n, f"gardien-env-{n}", css={"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1,
                                                           "flex-basis": 0, "margin-left": 5 if j else 0})
        fab.titre(e, f"gardien-{n}", css=TITRE_BAS)
        rang = fab.boite(e, f"gardien-{n}-boutons", css={"flex-direction": "row"})
        places = TROIS_AVEC[n]
        ech = fab.echelle(29, TROIS_AVEC[29], (17, TROIS_AVEC[17]))   # les 6 icônes de la bande à la même échelle
        for i, p in enumerate(places):
            bouton_b(fab, rang, n, p, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                                           "margin-left": 4 if i else 0}, icone=True, echelle=ech, petit=True,
                          texte=False, bulle=True, estompe=True)


def avancee_b(fab, cadre):
    """le terrain « Avancée » de 26.13 (avancee()). v8 : posé par avancee() avec deux remplaçants : la progression
    (progression_grisee : « Axiale » estompée quand un côté l'était, les côtés quand « Axiale » l'était) et la largeur
    du jeu offensif estompée (Kinito : « fais la même pour la largeur »). v14 : recopié ici, sauf (Kinito, 28/10) : la
    progression resserrée en hauteur (PROGRESSION_B, TEXTE_PROGRESSION_B), un bouton « Équilibré » écrit sous ses trois
    cases, et chaque case qui n'est pas allumée estompée (« Équilibré » choisi : les trois ; un côté : l'axe et l'autre
    côté…) ; la stratégie d'attaques placées a son titre (STRATEGIE_B : la seule consigne sans nom du terrain) et passe
    en trois cases (gérer le pressing, standard, contourner le pressing) ; stratégie et largeur du jeu offensif en
    boutons de FM simples, ceux qui ne sont pas choisis toujours estompés. Couloirs et courses de soutien : comme
    avant"""
    t = fab.t
    champ = champ_terrain(fab, cadre, "avancee", base.TRAITS_AVANCEE)
    # les deux couloirs suivent la largeur du jeu offensif (traits pleins : l'interface n'a pas de pointillés)
    e = fab.enveloppe(champ, 4, "couloirs-env", traverse=True)

    def couloirs(par, k):
        b = fab.boite(par, f"couloirs-{k}", css={"flex-grow": 1})
        fab.traverse(b)
        for x in base.COULOIRS[k]:
            fab.traverse(fab.boite(b, f"couloir-{k}-{x}", css={"position": "absolute", "left": pc(x), "top": 0,
                                                               "height": pc(100), "width": 0, "border-left-width": 2,
                                                               "border-left-color": (1.0, 1.0, 1.0, 0.45)}))
    sel = fab.selon(e, 4, couloirs, "couloirs", css={"flex-grow": 1})
    fab.traverse(sel)
    for r in t.walk(sel):
        if typ(t, r) == "BindableSwitchElement":
            fab.traverse(r)
    # courses de soutien : extérieures (31) sur les bords, intérieures (28) au milieu ; icônes de FM en portrait
    e28 = fab.enveloppe(champ, 28, "courses-env-28", traverse=True)
    titre_entre(fab, e28, "courses", 0, 4.6)   # v16 : centré entre le bord et « Extérieur / Intérieur » (4,6 %)
    e31 = fab.enveloppe(champ, 31, "courses-env-31", traverse=True)
    ech = fab.echelle(28, (1, 2), (31, (1, 2)))
    for n, autre, env, gauche, x, w in ((31, 28, e31, True, 0, 22), (28, 31, e28, True, 22, 28),
                                        (28, 31, e28, False, 50, 28), (31, 28, e31, False, 78, 22)):
        place = case_abs(fab, env, f"course-{n}-{'g' if gauche else 'd'}", x, 9, w, 22)
        base.course(fab, place, n, autre, gauche, ech, (22 / w, 1.0))

    def mots(par, ext_int):
        b = fab.boite(par, f"courses-noms-{fab.n}", css={"flex-grow": 1})
        fab.n += 1
        fab.traverse(b)
        base.etiquettes(fab, b, f"courses-noms-{fab.n}", 4.6, [(0, 22, ext_int[0]), (22, 56, ext_int[1]),
                                                               (78, 22, ext_int[0])])
    fab.selon_langue(e31, "courses-langue", mots, base.COURSES_LANGUES,
                     (base.TEXTES_COURSES["ext"], base.TEXTES_COURSES["int"]),
                     css={"position": "absolute", "left": 0, "top": 0, "width": pc(100), "height": pc(100)})
    # progression : flanc gauche, axe, flanc droit ; v14 : estompées quand elles ne sont pas allumées (une case
    # éteinte s'allume sur le code de l'option qu'elle enverrait, jamais celle en cours : « is-selected » faux), puis
    # « Équilibré » (option 0) écrit dessous
    y, h = PROGRESSION_B
    e30 = fab.enveloppe(champ, 30, "progression-env", traverse=True)
    titre_entre(fab, e30, "progression", 9 + 22, y)   # v16 : centré entre les courses (9 + 22 %) et ses cases
    ech = fab.echelle(30, (2, 1, 3))
    for cle, montre, x, w in (("G", 2, 0, 30), ("A", 1, 30, 40), ("D", 3, 70, 30)):
        place = case_abs(fab, e30, f"progression-{cle}", x, y, w, h)
        fab.etats(place, 30, base.REGLES_PROGRESSION[cle], montre, css={"flex-grow": 1}, icone=True, echelle=ech,
                  part=(30 / w, 1.0), tourne=True, petit=True, rempli=base.REMPLI_PROGRESSION,
                  texte_bas=TEXTE_PROGRESSION_B, estompe=True)
    sx, sw, sh = STANDARD_B
    fab.option(case_abs(fab, e30, "progression-equilibre", sx, y + h, sw, sh), 30, 0, petit=True, classe="label-sm",
               taille_texte=TEXTE_ZONES, estompe=True, css={"flex-grow": 1})
    # stratégie d'attaques placées (24) : v14 : son titre, et ses trois options côte à côte
    sous_progression = y + h + STANDARD_B[2]   # le bas de son « Équilibré »
    y, h = STRATEGIE_B
    e24 = fab.enveloppe(champ, 24, "strategie-env", traverse=True)
    titre_entre(fab, e24, "strategie", sous_progression, y)   # v16 : centré entre « Équilibré » et ses cases
    places = TROIS_AVEC[24]
    ech = fab.echelle(24, places)
    w = 100 / len(places)
    for i, p in enumerate(places):
        bouton_b(fab, case_abs(fab, e24, f"strategie-{p}", w * i, y, w, h), 24, p, css={"flex-grow": 1}, icone=True,
                      echelle=ech, petit=True, texte=False, bulle=True, estompe=True)
    # en bas : largeur du jeu offensif, les 5 options en icônes
    bas = fab.boite(cadre, "largeur", css=BANDE_BAS)
    e = fab.enveloppe(bas, 4, "largeur-env", css={"flex-direction": "column"})
    fab.titre(e, "largeur", css=TITRE_BAS)
    rang = fab.boite(e, "largeur-boutons", css={"flex-direction": "row"})
    ech = fab.echelle(4, range(5))
    for p in range(len(fab.src.options[4])):
        bouton_b(fab, rang, 4, p, icone=True, echelle=ech, texte=False, petit=True, bulle=True, estompe=True,
                      css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                           "margin-left": 4 if p else 0})


def colonne_avec(fab, ech, corps, k):
    """v7 : une colonne « avec le ballon » dans son calque pleine largeur, posée par les cales : deux calques, celui des
    tuiles (une cale qui grandit avant, entre ou après la paire de tuiles ; la paire normale ou inversée) et celui du
    terrain (cales de la hauteur d'une ou deux tuiles au-dessus / au-dessous, le terrain prend le reste)"""
    t = fab.t
    cal = fab.boite(corps, f"avec-calque-{k}", css={**PLEIN, "flex-direction": "row"})
    fab.traverse(cal)
    cales_avec(fab, cal, k, f"avec-colonne-{k}", False)
    col = fab.boite(cal, f"avec-colonne-{k}", css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    fab.traverse(col)
    cales_avec(fab, cal, k, f"avec-colonne-{k}", True)
    pousse = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0}
    fixe = {"flex-grow": 0, "flex-shrink": 0, "flex-basis": H_TUILE, "height": H_TUILE}
    # le calque des tuiles
    ct = fab.boite(col, f"avec-tuiles-{k}", css={**PLEIN, "flex-direction": "column"})
    fab.traverse(ct)
    fab.traverse(selon_classe(fab, ct, f"avec-avant-{k}", V_APOS[k], 0, "", CLASSE_CACHEE, css=pousse))
    paire = selon_classe(fab, ct, f"avec-paire-{k}", V_APOS[k], 1, "flex-grow-class", "")   # FM : flex-grow 1, seul
    fab.traverse(paire)
    dedans = selon_classe(fab, paire, f"avec-paire-dedans-{k}", V_AREV[k], 1, CLASSES_HB[1], CLASSES_HB[0],
                          css={"flex-grow": 1})
    fab.traverse(dedans)
    def poser(n):   # v14 : toutes les tuiles par tuile_avec_b (v8 à v13 : les crans par tuile_crans_b, le reste tuile())
        return tuile_avec_b(fab, dedans, n, fixe)
    t1 = poser(TUILES_HAUT[k])
    fab.traverse(selon_classe(fab, dedans, f"avec-entre-{k}", V_APOS[k], 1, "", CLASSE_CACHEE, css=pousse))
    fab.traverse(selon_classe(fab, dedans, f"avec-ecart-{k}", V_APOS[k], 1, CLASSE_CACHEE, "",
                              css={"height": ECART_TUILE, "flex-shrink": 0}))
    t2 = poser(TUILES_BAS[k])
    fab.traverse(selon_classe(fab, ct, f"avec-apres-{k}", V_APOS[k], 2, "", CLASSE_CACHEE, css=pousse))
    # le calque du terrain
    cp = fab.boite(col, f"avec-terrain-{k}", css={**PLEIN, "flex-direction": "column"})
    fab.traverse(cp)
    une = H_TUILE + ECART_TUILE
    for nom, valeur, h in ((f"avec-dessus-1-{k}", 1, une), (f"avec-dessus-2-{k}", 2, 2 * une)):
        fab.traverse(selon_classe(fab, cp, nom, V_APOS[k], valeur, "", CLASSE_CACHEE, css={"height": h, "flex-shrink": 0}))
    cadre = fab.boite(cp, f"cadre-{k}", css={**pousse, "min-height": MIN_TERRAIN_AVEC, **CADRE_TERRAIN})
    for nom, valeur, h in ((f"avec-dessous-1-{k}", 1, une), (f"avec-dessous-0-{k}", 0, 2 * une)):
        fab.traverse(selon_classe(fab, cp, nom, V_APOS[k], valeur, "", CLASSE_CACHEE, css={"height": h, "flex-shrink": 0}))
    (relance_b, avancee_b, finition_b)[k](fab, cadre)   # v8 : Relance et Avancée retouchés (voir chacun)
    # les icônes et les anneaux
    coin_avec(fab, ech, t1, k, 0, f"echange-avec-{k}-haut")
    coin_avec(fab, ech, cadre, k, 1, f"echange-avec-{k}-terrain")
    coin_avec(fab, ech, t2, k, 2, f"echange-avec-{k}-bas")
    anneau(fab, ech, col, f"echange-avec-colonne-{k}-anneau", V_ACOL, k + 1)


def avec_b(fab, conteneur):
    """v7 : avec le ballon : les noms des phases de FM tout en haut (v2), l'icône d'échange à côté ; puis chaque colonne
    (tuile du haut, terrain, tuile du bas) dans son calque, à sa place"""
    t, src = fab.t, fab.src
    ech = SourcesEchange()
    if not ech.ok():
        raise ValueError("bouton d'échange (ContractNegotiationAddOnItem) ou anneau de FM (introuvable)")
    titres = fab.boite(conteneur, "phases", css={"flex-direction": "row", "margin-bottom": 4})
    for k, (texte, _, _) in enumerate(PHASES):
        if k == 0:
            rangee = titres   # dans le flux : il donne la hauteur de la rangée
        else:
            rangee = fab.boite(titres, f"phases-calque-{k}", css={**PLEIN, "flex-direction": "row"})
            fab.traverse(rangee)
        cales_avec(fab, rangee, k, f"phase-{k}", False)
        tete = fab.boite(rangee, f"phase-tete-{k}", css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                                         "min-width": 0, "flex-direction": "row",
                                                         "justify-content": "center", "align-items": "center"})
        fab.traverse(tete)
        cales_avec(fab, rangee, k, f"phase-{k}", True)
        p = t.clone(src.phases[texte], tete, src=src.tq)
        t.styles.copy_from(src.tq.styles, t, p)
        fab._nom(p, f"phase-{k}")
        t.elem(p)["m_Classes"], t.elem(p)["m_RuleIndex"] = ["thematic-sm", "global-text-primary"], -1
        t.styles.style(t, p, {"-unity-text-align": "middle-center", "flex-shrink": 1, "min-width": 0})
        place = fab.boite(tete, f"phase-{k}-echange", css={**TAILLE_ICONE, "margin-left": 4})
        fab.traverse(place)
        icone_colonne_avec(fab, ech, place, k, f"echange-avec-colonne-{k}")
    corps = fab.boite(conteneur, "avec-corps", css={"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1,
                                                    "flex-basis": 0,
                                                    "min-height": 2 * (H_TUILE + ECART_TUILE) + MIN_TERRAIN_AVEC})
    for k in range(len(PHASES)):
        colonne_avec(fab, ech, corps, k)


def finition_b(fab, cadre):
    """v3 : le terrain des 30 derniers mètres de 26.13 (finition), recopié tel quel, sauf sa bande du bas : Liberté
    créative (BAS_FINITION) au lieu de Style de centres, qui monte dans la tuile du haut (Kinito). v14 (Kinito,
    28/10) : la patience a son titre, comme les autres consignes du terrain ; patience, tirs de loin et dribbles ont un
    bouton « Standard » écrit sous leurs cases (STANDARD_B), dont la hauteur est réduite pour lui faire la place
    (PATIENCE_B, ACTIONS_B) ; Liberté créative en trois cases (TROIS_AVEC) ; partout, boutons de FM simples (plus de
    case à bascule), ceux qui ne sont pas choisis toujours estompés ; l'arc de la surface suit (ARC_FINITION). v15 :
    2e clic -> option neutre (bouton_b). v16 : plus de but ; titres centrés dans leur écart (titre_entre)"""
    traits = [(nom, {**css, "top": pc(ARC_FINITION)} if nom == "arc" else css)
              for nom, css in sans_but(TRAITS_FINITION)]   # v16 : plus de but
    champ = champ_terrain(fab, cadre, "finition", traits)
    sx, sw, sh = STANDARD_B

    def standard(env, n, nom, y):   # le bouton « Standard » écrit (option par défaut de FM, place 1), centré
        fab.option(case_abs(fab, env, nom, sx, y, sw, sh), n, 1, petit=True, classe="label-sm",
                   taille_texte=TEXTE_ZONES, estompe=True, css={"flex-grow": 1})
    # patience (18) : 0 centrer de loin (les deux flancs), 1 standard, 2 jouer le ballon dans la surface
    y_titre, h = PATIENCE_B
    y = y_titre + ECART_TITRE_B
    e18 = fab.enveloppe(champ, 18, "patience-env", traverse=True)
    titre_entre(fab, e18, "patience", 0, y)   # v16 : centré entre le bord du terrain et ses cases
    bouton_b(fab, case_abs(fab, e18, "surface", 20, y, 60, h), 18, 2, css={"flex-grow": 1}, icone=True, petit=True,
                  texte=False, bulle=True, estompe=True)
    standard(e18, 18, "patience-standard", y + h)
    dessus = y + h + sh   # le bas du « Standard » au-dessus de la consigne suivante
    for cle, x in (("g", 2), ("d", 82)):
        bouton_b(fab, case_abs(fab, e18, f"loin-{cle}", x, y, 16, 56 - y), 18, 0, css={"flex-grow": 1}, petit=True,
                      vertical=True, classe="heading-xsmall-14px", estompe=True)
    # tirs de loin (27) et dribbles (19) : 0 dissuader à gauche, 2 encourager à droite, « Standard » dessous
    for n, cases in ((27, ((0, 20, 29.5), (2, 50.5, 29.5))), (19, ((0, 2, 47), (2, 51, 47)))):
        y_titre, h = ACTIONS_B[n]
        y = y_titre + ECART_TITRE_B
        e = fab.enveloppe(champ, n, f"actions-env-{n}", traverse=True)
        titre_entre(fab, e, f"actions-{n}", dessus, y)   # v16 : centré entre le « Standard » du dessus et ses cases
        ech = fab.echelle(n, [p for p, _, _ in cases])
        for p, x, w in cases:
            bouton_b(fab, case_abs(fab, e, f"actions-{n}-{p}", x, y, w, h), n, p, css={"flex-grow": 1}, icone=True,
                          echelle=ech, petit=True, texte=False, bulle=True, estompe=True)
        standard(e, n, f"actions-{n}-standard", y + h)
        dessus = y + h + sh
    # la bande du bas : Liberté créative (titre en TITRE_BAS, icônes) ; v14 : ses trois options
    n = BAS_FINITION
    bas = fab.boite(cadre, f"finition-bas-{n}", css=BANDE_BAS)
    e = fab.enveloppe(bas, n, f"finition-bas-env-{n}", css={"flex-direction": "column"})
    fab.titre(e, f"finition-bas-{n}", css=TITRE_BAS)
    rang = fab.boite(e, f"finition-bas-{n}-boutons", css={"flex-direction": "row"})
    places = TROIS_AVEC[n]
    ech = fab.echelle(n, places)
    for i, p in enumerate(places):
        bouton_b(fab, rang, n, p, css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": HAUT_BANDE,
                                       "margin-left": 4 if i else 0},
                      icone=True, echelle=ech, petit=True, texte=False, bulle=True, estompe=True)


# ---------- v19-v20 : la vue « FM24 » (Kinito, 04/11, captures 7 à 9 de FM24) ----------
# v19 : l'écran des consignes de FM24 en 3e vue, la colonne des phases DANS notre bloc, entre le terrain de FM et les
# consignes. v20 (Kinito, 04/11 matin, la v19 vue en jeu : « pas ce que je voulais. Je voulais faire disparaître la
# colonne de droite pour utiliser cette place pour mettre [les phases] ; ainsi on utilise la largeur de l'écran pour
# refaire l'écran FM24 », et « refaire EXACTEMENT visuellement ce qu'il y a sur FM24, ou le plus proche possible ») :
# - LA COLONNE DE DROITE : c'est un autre bloc de la grille de l'onglet (PhasesTeamInstructionsBlock : « Vue
#   d'ensemble », « 30 derniers mètres »… et leurs « Sélectionner »), posé par TacticalPlannerTeamInstructions
#   (composition TacticalPlannerTeamInstructionsTabComposition-Large : terrain 6, consignes 10, colonne 4, sur 20). En
#   vue FM24, les cartes des phases la recouvrent entièrement (un calque posé par-dessus son contenu, qui n'est pas
#   touché) ; nos consignes prennent toute la largeur de notre bloc.
# - LES VARIABLES PARTAGÉES : les deux blocs lisent la vue (kinitovue) et la phase ouverte (kinitophase24). Elles sont
#   déclarées dans TacticalPlannerTeamInstructions, comme « inpossession » de FM (que les trois blocs lisent), avec
#   leur clé de persistance d'avant (la vue choisie et la phase restent celles de la dernière fois), retirées de notre
#   bloc, et ajoutées aux paramètres attendus des deux blocs (BindingExpect), comme celles de FM (selectedphase…).
# - AU PLUS PRÈS DE FM24 (captures 7 à 9, couleurs relevées au pixel) : titres dans la police du texte de FM 27 en
#   gras (heading-small-12px, en capitales), boutons pleine largeur (vert vif : choisi ; rouge : une autre option
#   choisie ; vert sombre : libre ; 2e clic : option neutre), curseurs à piste fine allumée jusqu'au cran choisi, avec
#   un trait et les deux repères du réglage par défaut, terrains à lignes blanches : la largeur (le couloir occupé),
#   la construction (dédoublements extérieurs et intérieurs, progression, stratégie : zones écrites), les 30 derniers
#   mètres (patience et tirs de loin : zones écrites), la relance du gardien, la formation défensive.
# - PAS ENCORE : la formation de l'équipe sur le terrain de la largeur (FM24 y dessine les joueurs), les petits
#   terrains à flèches de la transition, les icônes des curseurs et des phases, le style et la mentalité en haut de la
#   colonne des phases (FM 27 les a en haut de l'écran). Sans colonne de droite (grille « Standard » de FM, petits
#   écrans), la vue FM24 n'a pas ses cartes : la phase ouverte reste celle de la dernière fois.
def _hexa(h, a=1.0):
    return (int(h[1:3], 16) / 255, int(h[3:5], 16) / 255, int(h[5:7], 16) / 255, a)


VUE_FM24 = 2   # valeur de base.VARIABLE (kinitovue) pour cette vue (0 : tuiles de FM, 1 : terrain)
TEXTE_FM24 = "FM24"   # le mot du bouton de l'en-tête (le même dans toutes les langues)
# v43 (Kinito, 05/11 : « que les couleurs de ce qu'on a ajouté matchent mieux avec l'écran » ; il a choisi, sur un
# aperçu, la palette « sarcelle ») : les verts vifs de FM24 juraient avec les verts sombres, tirant sur le bleu, de
# l'écran des tactiques de FM 27 (relevés au pixel sur sa capture : le bloc de gauche #046152, son terrain #0e4d3a).
# Le code de FM24 reste (vert-bleu : choisi ; rouge brique : incompatible ; sombre : libre), dans ces teintes. Les
# couleurs de FM24 (v19-v42) : panneau #017d3e, cadre #03342c, filet #199557, choisi #13dc68, indispo #b76857,
# bouton #005429, vide #00562b, piste #12fd70, fermée #1a463e, points #06ff6f / #ff5455, flèche des pions #2bd16b
SARCELLE24 = {"cadre": "#046152", "terrain": "#0e4d3a", "choisi": "#1fa483", "piste": "#2cc79e",
              "contraire": "#8e4f47", "libre": "#0a382c", "role": "#5cc7a7",
              "ouverte": "#17806f", "resume": "#d3ece4"}
# v44 (Kinito : « la couleur du bloc sélectionné à droite est un peu agressive ») : la carte de la phase ouverte en
# sarcelle claire (entre le cadre et l'onglet choisi « Avec le ballon » de FM 27, #188b79), bordée de vert-bleu ; les
# cartes fermées restent sombres : la carte ouverte se lit à sa clarté. Le résumé en blanc verdi (v19-v43 : violet
# #321450 bordé de blanc #f1ffff, résumé #a8a2bd)
C24 = {   # couleurs relevées sur les captures 7 à 9 de Kinito (FM24, 1920 × 1080, PIL) ; v43 : en sarcelle
    "panneau": _hexa(SARCELLE24["terrain"]), "cadre": _hexa(SARCELLE24["cadre"]), "filet": _hexa(SARCELLE24["cadre"]),
    "choisi": _hexa(SARCELLE24["choisi"]), "indispo": _hexa(SARCELLE24["contraire"]),
    "bouton": _hexa(SARCELLE24["libre"]), "vide": _hexa(SARCELLE24["libre"]),
    "piste": _hexa(SARCELLE24["piste"]), "repere": _hexa("#ecfff7"), "ouverte": _hexa(SARCELLE24["ouverte"]),
    "ouverte-bord": _hexa(SARCELLE24["piste"]),
    "fermee": _hexa(SARCELLE24["terrain"]), "resume": _hexa(SARCELLE24["resume"]), "couloir": _hexa(SARCELLE24["piste"], 0.16),
    "point-choisi": _hexa(SARCELLE24["choisi"]), "point-indispo": _hexa(SARCELLE24["contraire"]),
    "ligne": (1.0, 1.0, 1.0, 0.55),
    # v22 : pions (FM24 : la couleur de l'équipe ; ici le bordeaux des captures), gardien noir, flèches
    "pion": _hexa("#8a1d3f"), "pion-bord": _hexa("#4a0c20"), "pion-gb": _hexa("#111111"),
    "pion-gb-bord": _hexa("#6b6b6b"), "fleche": (0.86, 1.0, 0.9, 0.85), "fleche-pion": _hexa(SARCELLE24["piste"])}
COUL_FM24 = {   # COUL de 26.13 le temps de construire la vue FM24 (Fab.option, Fab.lisere, champ_terrain, traits_reels)
    "case-fond": C24["bouton"], "case-bord": C24["bouton"], "choisi-fond": C24["choisi"], "choisi": C24["choisi"],
    "anneau": (0.0, 0.0, 0.0, 0.0), "contraire": C24["indispo"], "contraire-bord": C24["indispo"],
    "herbe1": C24["panneau"], "herbe2": C24["panneau"], "ligne": C24["ligne"],
    # v21 (Kinito : « harmoniser les couleurs des lignes de pressing et de défense ») : pressing en blanc (les lignes de
    # FM24), défense en jaune doré : deux couleurs que toutes les formes
    # de daltonisme distinguent, et sur le vert (le vert du pressing de 26.13 ne se voyait plus sur le vert de FM24)
    "pressing": _hexa("#ffffff"), "defense": _hexa("#f2c94c"), "voile-pressing": (1.0, 1.0, 1.0, 0.07)}
COUL_ZONES24 = {**COUL_FM24,   # v21 : les zones des terrains de FM24 (relevées : vert vif, rouge, vert sombre), à 85 %
    "case-fond": _hexa(SARCELLE24["libre"], 0.85), "case-bord": _hexa(SARCELLE24["libre"], 0.0),
    "choisi-fond": _hexa(SARCELLE24["choisi"], 0.85), "choisi": _hexa(SARCELLE24["choisi"], 0.0),
    "contraire": _hexa(SARCELLE24["contraire"], 0.85), "contraire-bord": _hexa(SARCELLE24["contraire"], 0.0)}
#   v43 : en sarcelle (v21-v42 : #0b5a2e, #13dc68, #b76857)
#   v22 : un filet vert foncé au bord de chaque zone ; v23 (Kinito : « enlever les encadrés ») : plus de bord du tout
RAYONS_FM24 = {8: 3, 9: 3, 10: 3, 11: 3}   # coins des cases (26.13 : 8 à 11) ; FM24 : ~3 px
CLASSE_TITRE24 = "heading-small-12px"   # v20 : la police du texte de FM 27, en gras (FM24 : titres en gras, ~12 px)
CLASSE_TEXTE24 = "body-md"             # v20 : boutons, valeur d'un curseur, légende (FM24 : ~14 px, normal)
CLASSE_PETIT24 = "body-sm"             # v20 : zones des terrains (v20-v43 : aussi les résumés des phases)
CLASSE_RESUME24 = "body-md"            # v44 (Kinito : « augmenter la police de cette colonne ») (body-sm : 12 px)
# v44 (Kinito, capture en « Plus grand » de la v43 : avec beaucoup de consignes, la 3e carte sortait par le bas ; « il
# faut que ça rentre, mais il faut aussi utiliser plus de place dans les autres tailles ») : la colonne des phases a
# la MÊME taille à toute taille du texte de FM (une variante par taille, la police multipliée par 100 / taille, comme
# texte_comp24 ; les hauteurs en px, elles, ne sont pas agrandies par le jeu : mesuré sur ses captures, 30 px pour un
# bouton en Normal comme en Plus grand), et chaque ligne du résumé a une hauteur fixe. Le pire cas, les 28 consignes
# des trois phases réglées (15 + 5 + 8), fait ~760 px pour ~795 de place en 1080p (calcul, pas mesuré) ; son cas de
# la capture (26 lignes) ~720. v20-v43 : nom et résumé à 12 px, agrandis par le jeu (14,4 en Plus grand)
TAILLE_NOM_PHASE24, TAILLE_RESUME_PHASE24, TAILLE_PIED_PHASE24 = 15, 14, 13   # px, à l'écran (toute taille du texte)
H_LIGNE_RESUME24 = 19   # px : une ligne du résumé (v20-v43 : sa hauteur naturelle, 16 en Normal, 22 en Plus grand)
H_BOUTON24 = 28     # px, hauteur d'un bouton écrit (FM24 : 28 en 1080p)
ECART_BOUTON24 = 0  # px entre deux boutons d'une consigne (v22, Kinito : « pas d'espace » ; v19-v21 : 4)
ECART_BOUTON_SEUL24 = 4   # v22 : au-dessus d'un bouton seul (relances courtes du gardien, sous le curseur)
ECART_CONSIGNE24 = 16   # px au-dessus d'une consigne (FM24 : ~20)
H_PISTE24 = 20      # px, la piste d'un curseur, repères compris
TEXTE_ZONE24 = 11   # px, le texte des zones des terrains
RAPPORT_ZONES24 = 1.1   # hauteur / largeur des terrains (FM24 : 228 × 203 px)
HAUT_GB24 = 230     # px, le terrain « relancer vers »
PART_LIGNES24 = 66   # v27 (Kinito : « augmenter un peu le terrain sans ballon ») ; v26 : 62 ; % de sa colonne, le terrain des lignes (à droite : les encadrés et les crans à gauche)
PART_FORMATION24 = 66   # % de sa colonne : le terrain de la formation défensive (sans le ballon) ; v23 : avec la
#                        colonne des crans, à gauche (v19-v22 : 62)
ORDRE24 = {30: (2, 1, 3, 4), 18: (2, 0), 27: (2, 0), 5: (2, 0), 11: (2, 0), 3: (2, 0), 17: (2, 0), 20: (2, 0),
           19: (2, 0)}   # v23 : dans les espaces avant dans les pieds, encourager avant dissuader (Kinito) ; 3 :
#            contre-attaque (place 2) avant rester en place (place 0 : les noms d'icônes de FM disent l'inverse, les
#            noms affichés font foi : vu en jeu par Kinito sur la v22, capture 37)
INVERSE24 = {29, 12}   # v23 (Kinito) : options dans l'ordre inverse du jeu : longues avant courtes (sorties de but),
#                        engagez-vous plus avant ne vous jetez pas (tacles)   # v22 : 3 = contre-attaque puis rester en place (FM24)   # places montrées,
#           dans l'ordre de FM24 (sinon : toutes sauf l'option neutre, dans l'ordre du jeu)
AVEC24 = [4, 20, 24, 1, 21, 7, 30, 28, 31, 26, 18, 27, 19, 5, 6]   # dans l'ordre des panneaux (résumés des phases)
TRANSITION24 = [11, 3, 17, 16, 29]
SANS24 = [8, 9, 23, 10, 12, 15, 25, 22]
PHASES24 = [(langue.texte("AVEC LE BALLON", "IN POSSESSION"), ("AVEC LE BALLON", "IN POSSESSION"), AVEC24),
            (langue.texte("EN TRANSITION", "IN TRANSITION"), ("EN TRANSITION", "IN TRANSITION"), TRANSITION24),
            (langue.texte("SANS LE BALLON", "OUT OF POSSESSION"), ("SANS LE BALLON", "OUT OF POSSESSION"), SANS24)]
# v21 : les terrains à zones, en % du terrain (attaque en haut), relevés sur la capture 7 de FM24 ; les phrases de
# FM24 (vues sur la capture, en français ; en anglais : celles de FM) posées dans les zones
# v97 (Kinito, 13/11 : « fais les vues FM24 », dans la langue du jeu comme la vue Terrain, v95) : nos mots des vues FM24
# (consignes d'équipe, colonne des phases, consignes individuelles) dans chaque langue du jeu. Recopiés des fichiers des
# langues de FM 24 (data\shared.fmf) et de FM 27 (languages.fmf) par la clé du texte français (sinon de l'anglais),
# gardés quand l'anglais de la clé concorde ; relus et corrigés à la main là où FM parle d'autre chose (mot court hors
# contexte : « Moins » = « Senken », « DIRECTION » = « direction du transfert » en coréen…) ; nos expressions (« Plus de
# courses », « ATTAQUER LA SURFACE », « Plus durement »…) traduites par nous, relues par personne de langue
# maternelle. Le français : toujours celui de la vue. Fusion : chantier-consignes\v97 (fusion24.py)
ORDRE_TEXTES24 = ("english", "english (us)", "french", "german", "italian", "spanish", "spanish (latam)", "portuguese",
                  "portuguese (bra)", "dutch", "danish", "norwegian", "swedish", "polish", "czech", "russian", "turkish",
                  "greek", "indonesian", "japanese", "korean", "chinese", "chinese (traditional)", "thai", "arabic")
TEXTES24_LANGUES = {   # (français, anglais) de nos mots -> leur texte dans chaque langue de ORDRE_TEXTES24
    ('AVEC LE BALLON', 'IN POSSESSION'): (
        'IN POSSESSION', 'IN POSSESSION', 'AVEC LE BALLON', 'IN BALLBESITZ', 'IN POSSESSO', 'CON POSESIÓN',
        'CON POSESIÓN', 'COM POSSE DE BOLA', 'COM POSSE DE BOLA', 'IN BALBEZIT', 'I BOLDBESIDDELSE', 'MED BALL',
        'MED BOLL', 'PRZY PIŁCE', 'IN POSSESSION', 'С МЯЧОМ', 'TOPA SAHİPKEN', 'ΚΑΤΟΧΗ', 'SAAT MENGUASAI BOLA',
        'ポ\u200bゼッション時', '공 소유 시', '持\u200b球阶\u200b段', '持\u200b球阶\u200b段', 'IN POSSESSION', 'الاستحواذ',),
    ('EN TRANSITION', 'IN TRANSITION'): (
        'IN TRANSITION', 'IN TRANSITION', 'EN TRANSITION', 'UMSCHALTSPIEL', 'IN TRANSIZIONE', 'EN TRANSICIÓN',
        'EN TRANSICIÓN', 'EM TRANSIÇÃO', 'EM TRANSIÇÃO', 'IN OMSCHAKELING', 'OMSTILLING', 'UNDER OVERGANGER',
        'OMSTÄLLNINGAR', 'W PRZEJŚCIU', 'IN TRANSITION', 'ПЕРЕХОД МЯЧА', 'GEÇİŞ OYUNUNDA', 'ΜΕΤΑΒΑΣΗ',
        'SAAT TRANSISI', 'ト\u200bランジ\u200bション時', '전환 시', '转\u200b换阶\u200b段', '转\u200b换阶\u200b段', 'IN TRANSITION',
        'في التحول',),
    ('SANS LE BALLON', 'OUT OF POSSESSION'): (
        'OUT OF POSSESSION', 'OUT OF POSSESSION', 'SANS LE BALLON', 'GEGNER IN BALLBESITZ', 'NON IN POSSESSO',
        'SIN POSESIÓN', 'SIN POSESIÓN', 'SEM POSSE DE BOLA', 'SEM POSSE DE BOLA', 'ZONDER BALBEZIT',
        'UDEN BOLDBESIDDELSE', 'UTEN BALL', 'UTAN BOLL', 'BEZ PIŁKI', 'OUT OF POSSESSION', 'БЕЗ МЯЧА',
        'TOP RAKİPTEYKEN', 'ΧΩΡΙΣ ΜΠΑΛΑ', 'SAAT TIDAK MENGUASAI BOLA', '非ポ\u200bゼッション時', '소유권 없을 때',
        '无\u200b球阶\u200b段', '无\u200b球阶\u200b段', 'OUT OF POSSESSION', 'عدم الاستحواذ',),
    ('Dédoublements extérieurs gauches', 'Overlap Left'): (
        'Overlap Left', 'Overlap Left', 'Dédoublements extérieurs gauches', 'Hinterlaufen links',
        'Cercate di sovrapporvi a sinistra', 'Doblar por la izquierda', 'Doblar por la izquierda',
        'Sobrepo. Ext. Esquerda', 'Sobrepo. Ext. Esquerda', 'Links over elkaar heen gaan', 'Overlap venstre',
        'Overlapp venstre', 'Överlappning vänster', 'Obieg z lewej', 'Overlap Left', 'Забегания по флангу слева',
        'Sol Bek Desteğe Gelsin', 'Overlap Αριστερά', 'Overlap Kiri', '左サ\u200bイ\u200bド\u200bオーバーラップ', '왼쪽 오버래핑',
        '左\u200b侧套\u200b边插\u200b上', '左\u200b侧套\u200b边插\u200b上', 'Overlap Left', 'أوفر لاب من ناحية اليسار',),
    ('Dédoublements intérieurs gauches', 'Underlap Left'): (
        'Underlap Left', 'Underlap Left', 'Dédoublements intérieurs gauches', 'Anspiel links innen',
        'Cercate l’imbucata a sinistra', 'Doblar por dentro a la izquierda', 'Doblar por dentro a la izquierda',
        'Sobrepo. Int. Esquerda', 'Sobrepo. Int. Esquerda', 'Links binnendoor snijden', 'Underlap venstre',
        'Underlapp venstre', 'Insideslöpning vänster', 'Obieg od środka z lewej', 'Underlap Left',
        'Подключаться в центр слева', 'Soldan İçe Bindirene Pas At', 'Underlap Αριστερά', 'Underlap Kiri',
        '左サ\u200bイ\u200bド\u200bアンダーラップ', '왼쪽 언더래핑', '左\u200b侧肋\u200b部插\u200b上', '左\u200b侧肋\u200b部插\u200b上',
        'Underlap Left', 'أندر لاب من ناحية اليسار',),
    ('Dédoublements intérieurs droits', 'Underlap Right'): (
        'Underlap Right', 'Underlap Right', 'Dédoublements intérieurs droits', 'Anspiel rechts innen',
        'Cercate l’imbucata a destra', 'Doblar por dentro a la derecha', 'Doblar por dentro a la derecha',
        'Sobrepo. Int. Direita', 'Sobrepo. Int. Direita', 'Rechts binnendoor snijden', 'Underlap højre',
        'Underlapp høyre', 'Insideslöpning höger', 'Obieg od środka z prawej', 'Underlap Right',
        'Подключаться в центр справа', 'Sağdan İçe Bindirene Pas At', 'Underlap Δεξιά', 'Underlap Kanan',
        '右サ\u200bイ\u200bド\u200bアンダーラップ', '오른쪽 언더래핑', '右\u200b侧肋\u200b部插\u200b上', '右\u200b侧肋\u200b部插\u200b上',
        'Underlap Right', 'أندر لاب من ناحية اليمين',),
    ('Dédoublements extérieurs droits', 'Overlap Right'): (
        'Overlap Right', 'Overlap Right', 'Dédoublements extérieurs droits', 'Hinterlaufen rechts',
        'Cercate di sovrapporvi a destra', 'Doblar por la derecha', 'Doblar por la derecha', 'Sobrepo. Ext. Direita',
        'Sobrepo. Ext. Direita', 'Rechts over elkaar heen gaan', 'Overlap højre', 'Overlapp høyre',
        'Överlappning höger', 'Obieg z prawej', 'Overlap Right', 'Забегания по флангу справа',
        'Sağ Bek Desteğe Gelsin', 'Overlap Δεξιά', 'Overlap Kanan', '右サ\u200bイ\u200bド\u200bオーバーラップ', '오른쪽 오버래핑',
        '右\u200b侧套\u200b边插\u200b上', '右\u200b侧套\u200b边插\u200b上', 'Overlap Right', 'أوفر لاب من ناحية اليمين',),
    ("Concentrez le jeu sur l'aile gauche", 'Focus Play Down The Left Flank'): (
        'Focus Play Down The Left', 'Focus Play Down The Left', "Concentrez le jeu sur l'aile gauche",
        'Linke Seite fokussieren', 'Concentrate il gioco sulla sinistra', 'Enfocar el juego por la izquierda',
        'Enfocar el juego por la izquierda', 'Focar o Jogo pela Esquerda', 'Focar o Jogo pela Esquerda',
        'Focus op spel vanaf linkerflank', 'Fokus på spil via venstre side', 'Fokus på spill på venstre side',
        'Fokusera spel längs vänsterkanten', 'Ataki lewym skrzydłem', 'Focus Play Down The Left',
        'Играть через левый фланг', 'Sol Kanadı Kullan', 'Εστίαση Παιχνιδιού Αριστερά', 'Fokus Main di Sisi Kiri',
        '左サ\u200bイ\u200bド\u200b攻撃重視', '왼쪽 측면을 노려라', '多\u200b走左\u200b路', '多\u200b走左\u200b路',
        'Focus Play Down The Left', 'تركيز اللعب على الجانب الأيسر',),
    ("Concentrez le jeu dans l'axe", 'Focus Play Through The Middle'): (
        'Focus Play Through The Middle', 'Focus Play Through The Middle', "Concentrez le jeu dans l'axe",
        'Zentrum fokussieren', 'Concentrate il gioco al centro', 'Enfocar el juego por el centro',
        'Enfocar el juego por el centro', 'Focar o Jogo Pelo Meio', 'Focar o Jogo Pelo Meio',
        'Focus Op Spelen Door Het Midden', 'Fokus på spil gennem midten', 'Fokus på å spille gjennom midten',
        'Fokusera spel via mitten', 'Ataki środkiem pola', 'Focus Play Through The Middle', 'Играть через центр',
        'Göbekten Oyna', 'Εστίαση Παιχνιδιού Κεντρικά', 'Fokus Main di Area Tengah', '中央か\u200bら\u200b崩せ', '중앙을 노려라',
        '多\u200b走中\u200b路', '多\u200b走中\u200b路', 'Focus Play Through The Middle', 'تركيز اللعب في المنتصف',),
    ("Concentrez le jeu sur l'aile droite", 'Focus Play Down The Right Flank'): (
        'Focus Play Down the Right', 'Focus Play Down the Right', "Concentrez le jeu sur l'aile droite",
        'Rechte Seite fokussieren', 'Concentra il gioco sulla destra', 'Centrar el juego por la derecha',
        'Centrar el juego por la derecha', 'Concentração no lado direito', 'Concentração no lado direito',
        'Focus op spel vanaf rechterflank', 'Fokusér på opspil i højre side', 'Fokus på spill på høyre side',
        'Fokusera spel längs högerkanten', 'Gra głównie prawym skrzydłem', 'Focus Play Down the Right',
        'Играть через правый фланг', 'Sağ Kanadı Kullanın', 'Εστίαση Παιχνιδιού Από Τα Δεξιά',
        'Fokus Main di Sisi Kanan', '右サ\u200bイ\u200bド\u200b集中攻撃', '오른쪽 측면을 노려라', '主\u200b攻右\u200b路',
        '主\u200b攻右\u200b路', 'Focus Play Down the Right', 'تركيز اللعب على الجانب الأيمن',),
    ('Empêchez rel. courtes du GB', 'Prevent Short GK Distribution'): (
        'Prevent Short GK Distribution', 'Prevent Short GK Distribution', 'Empêchez rel. courtes du GB',
        'TW an kurzem Abspiel hindern', 'Impedite i passaggi corti del Por', 'Evitar pases en corto del portero',
        'Evitar pases en corto del portero', 'Evitar Distribuição Curta do GR', 'Evitar Distribuição Curta do GR',
        'Kort afspelen van keeper voorkomen', 'Afskær målmanden fra at distribuere kort',
        'Hindre korte avleveringer fra keeper', 'Hindra korta målvaktsuppspel',
        'Przeszkadzaj bramkarzowi w krótkim rozegraniu', 'Prevent Short GK Distribution',
        'Мешать короткому вводу мяча вратарем', 'Rakip Kaleci Top Çıkartırken Defansa Baskı',
        'Εμποδίστε Κοντινό Μοίρασμα ΤΦ', 'Cegah Distribusi Bola Pendek',
        'GKか\u200bら\u200bの\u200b短い\u200b配球を\u200b阻止', '상대 골키퍼 긴 패스 유도', '逼\u200b抢门\u200b将', '逼\u200b抢门\u200b将',
        'Prevent Short GK Distribution', 'منع انتشار حارس المرمى القصير',),
    ('Tirez à vue', 'Shoot On Sight'): (
        'Shoot On Sight', 'Shoot On Sight', 'Tirez à vue', 'Schießen bei freier Bahn', 'Tirate appena possibile',
        'Disparar cuando se pueda', 'Disparar cuando se pueda', 'Rematar Sempre que Possível',
        'Rematar Sempre que Possível', 'Elke schietkans benutten', 'Skyd første gang', 'Skyt ved mulighet',
        'Tidiga avslut', 'Strzały z każdej pozycji', 'Shoot On Sight', 'Бить при любой возможности',
        'Kaleyi Gördüğünde Vur', 'Σουτ Σε Κάθε Ευκαιρία', 'Tembak Langsung', '積極的に\u200bシュート', '슛을 아끼지 말아라',
        '有\u200b机会\u200b就射\u200b门', '有\u200b机会\u200b就射\u200b门', 'Shoot On Sight', 'التسديد متى سنحت الفرصة',),
    ('Moins de tirs de loin', 'Shoot Less Often'): (
        'Shoot Less Often', 'Shoot Less Often', 'Moins de tirs de loin', 'Seltener schießen', 'Tira di meno',
        'Disparar menos a menudo', 'Disparar menos a menudo', 'Rematar Menos', 'Rematar Menos',
        'Minder op doel schieten', 'Skyd mindre', 'Skyt sjeldnere', 'Skjut mindre', 'Rzadziej strzelaj',
        'Shoot Less Often', 'Бить реже', 'Daha Az Şut Çek', 'Μη Σουτάρεις Τόσο Συχνά', 'Kurangi Tembakan',
        'シュート\u200bを\u200b減ら\u200bせ', '적게 슈팅하라', '少\u200b些打\u200b门', '少\u200b些打\u200b门', 'Shoot Less Often',
        'إرسال تسديدات أقل',),
    ('SANS BALLON (ÉQUIPE)', 'TEAM OUT OF POSSESSION'): (
        'TEAM OUT OF POSSESSION', 'TEAM OUT OF POSSESSION', 'SANS BALLON (ÉQUIPE)', 'MANNSCHAFT OHNE BALL',
        'SQUADRA NON IN POSSESSO', 'EQUIPO SIN BALÓN', 'EQUIPO SIN BALÓN', 'EQUIPA SEM BOLA', 'EQUIPA SEM BOLA',
        'TEAM ZONDER BAL', 'HOLD UDEN BOLD', 'LAG UTEN BALL', 'LAG UTAN BOLL', 'DRUŻYNA BEZ PIŁKI',
        'TEAM OUT OF POSSESSION', 'КОМАНДА БЕЗ МЯЧА', 'TAKIM TOPSUZKEN', 'ΟΜΑΔΑ ΧΩΡΙΣ ΜΠΑΛΑ', 'TIM TANPA BOLA',
        'チーム：非保持時', '팀 공 미소유 시', '团队无球', '团队无球', 'TEAM OUT OF POSSESSION', 'الفريق دون الكرة',),
    ('PRESSING', 'PRESSING'): (
        'PRESSING', 'PRESSING', 'PRESSING', 'PRESSING', 'PRESSING', 'PRESIÓN', 'PRESIÓN', 'PRESSÃO', 'PRESSÃO',
        'PRESSING', 'PRES', 'PRESS', 'PRESS', 'PRESSING', 'PRESSING', 'ПРЕССИНГ', 'PRES', 'ΠΙΕΣΗ', 'PRESSING',
        'プ\u200bレッシング', '압박 수비', '压\u200b迫', '压\u200b迫', 'PRESSING', 'الضغط',),
    ('Moins', 'Less'): (
        'Less', 'Less', 'Moins', 'Weniger', 'Meno', 'Menos', 'Menos', 'Menos', 'Menos', 'Minder', 'Mindre', 'Mindre',
        'Mindre', 'Mniej', 'Less', 'Меньше', 'Daha az', 'Λιγότερο', 'Lebih sedikit', '少なく', '적게', '更少', '更少', 'Less',
        'أقل',),
    ('Plus', 'More'): (
        'More', 'More', 'Plus', 'Mehr', 'Più', 'Más', 'Más', 'Mais', 'Mais', 'Meer', 'Mere', 'Mer', 'Mer', 'Więcej',
        'More', 'Больше', 'Daha fazla', 'Περισσότερο', 'Lebih banyak', '多く', '많이', '更多', '更多', 'More', 'أكثر',),
    ('MARQUAGE', 'MARKING'): (
        'MARKING', 'MARKING', 'MARQUAGE', 'DECKUNG', 'MARCATURA', 'MARCAJE', 'MARCAJE', 'MARCAÇÃO', 'MARCAÇÃO',
        'MANDEKKEN', 'MARKERING', 'MARKERING', 'MARKERINGSSPEL', 'KRYCIE', 'MARKING', 'ОПЕКА', 'MARKAJ',
        'ΜΑΡΚΑΡΙΣΜΑ', 'PENJAGAAN', 'マーキング', '마크', '盯\u200b人', '盯\u200b人', 'MARKING', 'الرقابة',),
    ('De plus près', 'Tighter'): (
        'Tighter', 'Tighter', 'De plus près', 'Enger', 'Più stretta', 'Más cerca', 'Más cerca', 'Mais apertada',
        'Mais apertada', 'Strakker', 'Tættere', 'Tettere', 'Tätare', 'Ciaśniej', 'Tighter', 'Плотнее', 'Daha sıkı',
        'Πιο στενά', 'Lebih ketat', 'より密着', '더 밀착', '更紧', '更紧', 'Tighter', 'لصيقة أكثر',),
    ('Plus durement', 'Harder'): (
        'Harder', 'Harder', 'Plus durement', 'Härter', 'Più duri', 'Más fuerte', 'Más fuerte', 'Mais duro',
        'Mais duro', 'Harder', 'Hårdere', 'Hardere', 'Hårdare', 'Ostrzej', 'Harder', 'Жёстче', 'Daha sert',
        'Πιο σκληρά', 'Lebih keras', '激しく', '더 거칠게', '更凶狠', '更凶狠', 'Harder', 'بقوة أكبر',),
    ('Moins durement', 'Ease off'): (
        'Ease off', 'Ease off', 'Moins durement', 'Vorsichtiger', 'Meno duri', 'Más suave', 'Más suave',
        'Menos duro', 'Menos duro', 'Voorzichtiger', 'Blødere', 'Mykere', 'Mjukare', 'Delikatniej', 'Ease off',
        'Мягче', 'Daha yumuşak', 'Πιο ήπια', 'Lebih lunak', '控えめに', '덜 거칠게', '更克制', '更克制', 'Ease off', 'بقوة أقل',),
    ('TACLES', 'TACKLING'): (
        'TACKLING', 'TACKLING', 'TACLES', 'TACKLING', 'CONTRASTI', 'ENTRADAS', 'ENTRADAS', 'DESARME', 'DESARME',
        'TACKELEN', 'TACKLINGER', 'TAKLINGER', 'TACKLINGAR', 'ODBIÓR PIŁKI', 'TACKLING', 'ОТБОР', 'TOPA HAMLE',
        'ΤΑΚΛΙΝ', 'TEKEL', 'タック\u200bル', '태클', '铲\u200b抢', '铲\u200b抢', 'TACKLING', 'التدخل',),
    ('Individuel', 'Man'): (
        'Individual', 'Individual', 'Individuel', 'Individuell', 'Individuale', 'Individual', 'Individual',
        'Individual', 'Individual', 'Individueel', 'Individuel', 'Individuell', 'Individuell', '1 na 1',
        'Individual', 'Индивидуальные', 'Bireysel', 'Ατομική', 'Individu', '個別', '개인', '个\u200b人', '个\u200b人',
        'Individual', 'رقابة اللاعب',),
    ('De zone', 'Zonal'): (
        'Zonal', 'Zonal', 'De zone', 'Zonal', 'A zona', 'En zona', 'En zona', 'Zonal', 'Zonal', 'Zonaal', 'Zonal',
        'Zonal', 'Zonal', 'Strefowe', 'Zonal', 'Зональная', 'Alan', 'Ζώνη', 'Zona', 'ゾーン', '지역 방어', '区域防守',
        '区\u200b域', 'Zonal', 'منطقة',),
    ('TYPE DE MARQUAGE', 'MARKING TYPE'): (
        'MARKING STYLE', 'MARKING STYLE', 'TYPE DE MARQUAGE', 'DECKUNGSART', 'TIPO DI MARCATURA', 'TIPO DE MARCAJE',
        'TIPO DE MARCAJE', 'TIPO DE MARCAÇÃO', 'TIPO DE MARCAÇÃO', 'DEKKING', 'MARKERINGSSTIL', 'MARKERINGSTYPE',
        'MARKERINGSTYP', 'RODZAJ KRYCIA', 'MARKING STYLE', 'ТИП ОПЕКИ', 'MARKAJ TARZI', 'ΣΤΥΛ ΜΑΡΚΑΡΙΣΜΑΤΟΣ',
        'GAYA MARKING', 'マーキング\u200bス\u200bタ\u200bイ\u200bル', '수비 방식', '盯\u200b人方\u200b式', '盯\u200b人方\u200b式',
        'MARKING STYLE', 'أسلوب يعتمد على الرقابة',),
    ('AVEC BALLON (ÉQUIPE)', 'TEAM IN POSSESSION'): (
        'TEAM IN POSSESSION', 'TEAM IN POSSESSION', 'AVEC BALLON (ÉQUIPE)', 'MANNSCHAFT IN BALLBESITZ',
        'SQUADRA IN POSSESSO', 'EQUIPO CON BALÓN', 'EQUIPO CON BALÓN', 'EQUIPA COM BOLA', 'EQUIPA COM BOLA',
        'TEAM IN BALBEZIT', 'HOLD MED BOLDEN', 'LAG MED BALL', 'LAG MED BOLL', 'DRUŻYNA PRZY PIŁCE',
        'TEAM IN POSSESSION', 'КОМАНДА С МЯЧОМ', 'TAKIM TOPA SAHİPKEN', 'ΟΜΑΔΑ ΜΕ ΤΗΝ ΜΠΑΛΑ', 'TIM MENGUASAI BOLA',
        'チーム：ボール保持時', '팀 공 소유 시', '团队持球', '团队持球', 'TEAM IN POSSESSION', 'الفريق مستحوذ على الكرة',),
    ('ATTAQUER LA SURFACE', 'ATTACKING THE BOX'): (
        'ATTACKING THE BOX', 'ATTACKING THE BOX', 'ATTAQUER LA SURFACE', 'STRAFRAUM ATTACKIEREN', "ATTACCARE L'AREA",
        'ATACAR EL ÁREA', 'ATACAR EL ÁREA', 'ATACAR A ÁREA', 'ATACAR A ÁREA', 'DE ZESTIEN AANVALLEN',
        'ANGRIB FELTET', 'ANGRIP BOKSEN', 'ANFALLA STRAFFOMRÅDET', 'ATAK NA POLE KARNE', 'ATTACKING THE BOX',
        'АТАКА ШТРАФНОЙ', 'CEZA SAHASINA HÜCUM', 'ΕΠΙΘΕΣΗ ΣΤΗΝ ΠΕΡΙΟΧΗ', 'MENYERANG KOTAK PENALTI', 'ペナルティエリアへの侵入',
        '박스 공략', '冲击禁区', '冲击禁区', 'ATTACKING THE BOX', 'مهاجمة منطقة الجزاء',),
    ('Côté', 'Side'): (
        'Side', 'Side', 'Côté', 'Seite', 'Lato', 'Lado', 'Lado', 'Lado', 'Lado', 'Kant', 'Side', 'Side', 'Sida',
        'Strona', 'Side', 'Сторона', 'Bölge', 'Πλευρά', 'Sisi', 'サ\u200bイ\u200bド', '측면', '侧', '边\u200b路位\u200b置',
        'Side', 'جانب',),
    ('1er poteau', 'Near post'): (
        'Near Post', 'Near Post', '1er poteau', 'Kurzer Pfosten', 'Primo palo', 'Primer palo', 'Primer palo',
        'Primeiro poste', 'Primeiro poste', 'Eerste paal', 'Nærmeste stolpe', 'Nærmeste stolpe', 'Främre stolpen',
        'Bliższy słupek', 'Near Post', 'Ближняя штанга', 'Yakın Direk', 'Πρώτο Δοκάρι', 'Tiang Dekat',
        'ニ\u200bア\u200bポ\u200bス\u200bト', '가까운 포스트', '近\u200b门柱', '近\u200b门柱', 'Near Post', 'على القائم القريب',),
    ('2e poteau', 'Far post'): (
        'Far Post', 'Far Post', '2e poteau', 'Langer Pfosten', 'Secondo palo', 'Segundo palo', 'Segundo palo',
        'Segundo poste', 'Segundo poste', 'Tweede paal', 'Fjerneste stolpe', 'Bortre stolpe', 'Bortre stolpen',
        'Dalszy słupek', 'Far Post', 'Дальняя штанга', 'Uzak Direk', 'Δεύτερο Δοκάρι', 'Tiang Jauh',
        'ファーポ\u200bス\u200bト', '먼 포스트', '远\u200b门柱', '远\u200b门柱', 'Far Post', 'على القائم البعيد',),
    ('Gauche', 'Left'): (
        'Left', 'Left', 'Gauche', 'Links', 'Sinistra', 'Izquierda', 'Izquierda', 'Esquerda', 'Esquerdo', 'Links',
        'Venstre', 'Venstre', 'Vänster', 'Lewy', 'Left', 'Слева', 'Sol', 'Αριστερά', 'Kiri', '左', '왼쪽', '左', '左',
        'Left', 'يسار',),
    ('Centre', 'Centre'): (
        'Centre', 'Centre', 'Centre', 'Zentral', 'Centro area', 'Centro', 'Centro', 'Centro', 'Centro', 'Centraal',
        'Central', 'Sentral', 'Central', 'Środek', 'Centre', 'Центр', 'Merkez', 'Κέντρο', 'Tengah', 'センター', '중앙',
        '中\u200b路', '中\u200b路', 'Centre', 'الوسط',),
    ('Droite', 'Right'): (
        'Right', 'Right', 'Droite', 'Rechts', 'Destra', 'Derecha', 'Derecha', 'Direita', 'Direita', 'Rechts',
        'Højre', 'Høyre', 'Högra', 'Prawy', 'Right', 'Справа', 'Sağ', 'Δεξιά', 'Kanan', '右', '오른쪽', '右\u200b侧',
        '右\u200b侧', 'Right', 'يمين',),
    ('Profondeur', 'Depth'): (
        'Depth', 'Depth', 'Profondeur', 'Tiefe', 'Profondità', 'Profundidad', 'Profundidad', 'Profundidade',
        'Profundidade', 'Diepte', 'Dybde', 'Dybde', 'Djup', 'Głębokość', 'Depth', 'Глубина', 'Derinlik', 'Βάθος',
        'Kedalaman', '深さ', '깊이', '纵深', '纵深', 'Depth', 'العمق',),
    ('Attaquer la ligne', 'Attack the line'): (
        'Attack the line', 'Attack the line', 'Attaquer la ligne', 'Linie attackieren', 'Attaccare la linea',
        'Atacar la línea', 'Atacar la línea', 'Atacar a linha', 'Atacar a linha', 'Lijn aanvallen', 'Angrib linjen',
        'Angrip linjen', 'Anfall linjen', 'Atak na linię', 'Attack the line', 'Атака линии', 'Çizgiye hücum',
        'Επίθεση στη γραμμή', 'Serang garis', 'ラインを突く', '라인 공략', '冲击防线', '冲击防线', 'Attack the line', 'مهاجمة الخط',),
    ('Arriver en retard', 'Arrive late'): (
        'Arrive late', 'Arrive late', 'Arriver en retard', 'Spät nachrücken', 'Inserimento tardivo', 'Llegar tarde',
        'Llegar tarde', 'Chegar tarde', 'Chegar tarde', 'Laat inlopen', 'Kom sent ind', 'Kom sent inn',
        'Kom sent in', 'Późne wejście', 'Arrive late', 'Поздний подход', 'Geç gel', 'Καθυστερημένη άφιξη',
        'Datang terlambat', '遅れて進入', '늦게 침투', '后插上', '后插上', 'Arrive late', 'الوصول متأخرًا',),
    ('COURSES ET POSITION', 'RUNS AND POSITION'): (
        'RUNS AND POSITION', 'RUNS AND POSITION', 'COURSES ET POSITION', 'LAUFWEGE UND POSITION',
        'MOVIMENTI E POSIZIONE', 'DESMARQUES Y POSICIÓN', 'DESMARQUES Y POSICIÓN', 'DESMARCAÇÕES E POSIÇÃO',
        'DESMARCAÇÕES E POSIÇÃO', 'LOOPACTIES EN POSITIE', 'LØB OG POSITION', 'LØP OG POSISJON',
        'LÖPNINGAR OCH POSITION', 'WBIEGNIĘCIA I POZYCJA', 'RUNS AND POSITION', 'РЫВКИ И ПОЗИЦИЯ',
        'KOŞULAR VE POZİSYON', 'ΚΙΝΗΣΕΙΣ ΚΑΙ ΘΕΣΗ', 'PERGERAKAN DAN POSISI', '走り込みとポジション', '침투와 위치', '跑位与站位',
        '跑位与站位', 'RUNS AND POSITION', 'التحركات والتمركز',),
    ("Dans l'axe", 'Narrower'): (
        'Narrower', 'Narrower', "Dans l'axe", 'Enger', 'Stretti', 'Más estrecho', 'Más estrecho', 'Mais por dentro',
        'Compacto', 'Smaller', 'Smallere', 'Smalere', 'Smalare', 'Węziej', 'Narrower', 'Более узко', 'Dar Alan',
        'Στενότερα', 'Lebih Sempit', '幅を\u200b狭く', '좁게', '相\u200b对收\u200b缩', '相\u200b对收\u200b缩', 'Narrower', 'أضيق',),
    ('Excentré', 'Wider'): (
        'Wider', 'Wider', 'Excentré', 'Breiter', 'Larghi', 'Más ancho', 'Más ancho', 'Mais aberto', 'Largura',
        'Breder', 'Bredere', 'Bredere', 'Bredare', 'Szerzej', 'Wider', 'Шире', 'Geniş Alan', 'Πλατύτερα',
        'Lebih Lebar', '幅を\u200b広く', '넓게', '相\u200b对拉\u200b开', '相\u200b对拉\u200b开', 'Wider', 'أوسع',),
    ('Plus de courses', 'More runs'): (
        'More runs', 'More runs', 'Plus de courses', 'Mehr Läufe', 'Più inserimenti', 'Más desmarques',
        'Más desmarques', 'Mais desmarcações', 'Mais desmarcações', 'Meer loopacties', 'Flere løb', 'Flere løp',
        'Fler löpningar', 'Więcej wbiegnięć', 'More runs', 'Больше рывков', 'Daha çok koşu', 'Περισσότερες κινήσεις',
        'Lebih banyak lari', '走り込みを増やす', '침투 늘리기', '多跑位', '多跑位', 'More runs', 'تحركات أكثر',),
    ('Moins de courses', 'Fewer runs'): (
        'Fewer runs', 'Fewer runs', 'Moins de courses', 'Weniger Läufe', 'Meno inserimenti', 'Menos desmarques',
        'Menos desmarques', 'Menos desmarcações', 'Menos desmarcações', 'Minder loopacties', 'Færre løb',
        'Færre løp', 'Färre löpningar', 'Mniej wbiegnięć', 'Fewer runs', 'Меньше рывков', 'Daha az koşu',
        'Λιγότερες κινήσεις', 'Lebih sedikit lari', '走り込みを減らす', '침투 줄이기', '少跑位', '少跑位', 'Fewer runs', 'تحركات أقل',),
    ('Prenez les espaces', 'Move into channels'): (
        'Move Into Channels', 'Move Into Channels', 'Prenez les espaces', 'Zwischenräume besetzen',
        'Muoversi negli spazi', 'Moverse entre líneas', 'Moverse entre líneas', 'Movimentar Pelos Espaços',
        'Movimentar Pelos Espaços', 'Tussen de linies spelen', 'Løb i dybden', 'Løp inn i rom', 'Löp i djupled',
        'Poszukiwanie wolnych stref', 'Move Into Channels', 'Смещаться в свободные зоны', 'Boş Alanlara Koşu Yap',
        'Κίνηση στους Κενούς Χώρους', 'Bergerak ke Half-Space', 'ディフェンス\u200bの\u200b隙間に\u200b入り\u200b込め',
        '수비수와 풀백 사이로 이동', '跑肋部空间\u200b接球', '跑肋部空间\u200b接球', 'Move Into Channels', 'التحرك على الرواقين',),
    ('AVEC BALLON (JOUEUR)', 'PLAYER IN POSSESSION'): (
        'PLAYER IN POSSESSION', 'PLAYER IN POSSESSION', 'AVEC BALLON (JOUEUR)', 'SPIELER IN BALLBESITZ',
        'GIOCATORE IN POSSESSO', 'JUGADOR CON BALÓN', 'JUGADOR CON BALÓN', 'JOGADOR COM BOLA', 'JOGADOR COM BOLA',
        'SPELER IN BALBEZIT', 'SPILLER MED BOLDEN', 'SPILLER MED BALL', 'SPELARE MED BOLL', 'ZAWODNIK PRZY PIŁCE',
        'PLAYER IN POSSESSION', 'ИГРОК С МЯЧОМ', 'OYUNCU TOPA SAHİPKEN', 'ΠΑΙΚΤΗΣ ΜΕ ΤΗΝ ΜΠΑΛΑ',
        'PEMAIN MENGUASAI BOLA', '選手：ボール保持時', '선수 공 소유 시', '球员持球', '球员持球', 'PLAYER IN POSSESSION',
        'اللاعب مستحوذ على الكرة',),
    ('DIRECTION', 'DIRECTION'): (
        'DIRECTION', 'DIRECTION', 'DIRECTION', 'RICHTUNG', 'DIREZIONE', 'DIRECCIÓN', 'DIRECCIÓN', 'SENTIDO',
        'SENTIDO', 'RICHTING', 'RETNING', 'RETNING', 'RIKTNING', 'KIERUNEK', 'DIRECTION', 'НАПРАВЛЕНИЕ', 'YÖN',
        'ΚΑΤΕΥΘΥΝΣΗ', 'ARAH', '方向', '방향', '方向', '去\u200b向', 'DIRECTION', 'الاتجاه',),
    ('Conserver le ballon', 'Hold up ball'): (
        'Hold Up Ball', 'Hold Up Ball', 'Conserver le ballon', 'Ball halten', 'Tenere palla', 'Aguantar el balón',
        'Aguantar el balón', 'Segurar Bola', 'Segurar Bola', 'Bal vasthouden', 'Hold på bolden', 'Hold på ballen',
        'Håll i bollen', 'Utrzymanie piłki', 'Hold Up Ball', 'Придержать мяч', 'Topu Ayağında Tut', 'Κράτημα Μπάλας',
        'Pertahankan Penguasaan Bola', 'ボール\u200bを\u200bキープ\u200bし\u200bろ', '볼 키핑', '拿\u200b住球', '拿\u200b住球',
        'Hold Up Ball', 'الاحتفاظ بالكرة',),
    ("Repiquer dans l'axe", 'Cut inside'): (
        'Cutting Inside', 'Cutting Inside', "Repiquer dans l'axe", 'Nach innen ziehen', 'Tagliare verso il centro',
        'Recortar hacia dentro', 'Recortar hacia dentro', 'Flectir para Dentro', 'Flectir para Dentro',
        'Naar binnen komen', 'Skære ind i banen', 'Skjærer inn', 'Skära inåt', 'Ścinanie do środka',
        'Cutting Inside', 'Смещение в центр', 'İçeri Katetme', 'Κόψιμο προς τα Μέσα', 'Memotong Ke Dalam', 'カットイン',
        '안쪽 파고들기', '内切', '内切', 'Cutting Inside', 'الدخول في عمق الملعب',),
    ('Prendre le couloir', 'Run wide'): (
        'Run wide', 'Run wide', 'Prendre le couloir', 'Außen vorbei', 'Andare sul fondo', 'Ir por la banda',
        'Ir por la banda', 'Ir pela ala', 'Ir pela ala', 'Over de flank', 'Gå ud på kanten', 'Gå ut på kanten',
        'Gå ut på kanten', 'Bieg skrzydłem', 'Run wide', 'Уходить на фланг', 'Kanattan git', 'Πήγαινε στην πτέρυγα',
        'Lari ke sayap', 'サイドへ持ち出す', '측면으로 돌파', '沿边路推进', '沿边路推进', 'Run wide', 'التقدم على الطرف',),
    ('Décrochez plus souvent', 'Roam from position'): (
        'Roam From Position', 'Roam From Position', 'Décrochez plus souvent', 'Position verlassen',
        'Libertà di movimento', 'Variar la posición', 'Variar la posición', 'Deambular Da Posição',
        'Deambular Da Posição', 'Zwerven', 'Frihed fra position', 'Streif fra posisjon', 'Ströva från position',
        'Szukanie gry', 'Roam From Position', 'Смещаться с позиции', 'Mevkinden Bağımsız Oyna',
        'Περιπλανήσου Από Τη Θέση', 'Berpindah dari Posisi', 'ポ\u200bジ\u200bションに\u200b縛ら\u200bれ\u200bる\u200bな',
        '포지션 자유', '灵\u200b活跑\u200b位', '灵\u200b活跑\u200b位', 'Roam From Position', 'الخروج من المركز',),
    ('MOUVEMENTS', 'MOVEMENT'): (
        'MOVEMENT', 'MOVEMENT', 'MOUVEMENTS', 'SPIEL OHNE BALL', 'MOVIMENTO', 'MOVIMIENTO', 'MOVIMIENTO',
        'MOVIMENTAÇÃO', 'MOVIMENTAÇÃO', 'BEWEGING', 'BEVÆGELSE', 'BEVEGELSE', 'RÖRELSE', 'RUCH', 'MOVEMENT',
        'ПОДВИЖНОСТЬ', 'HAREKETLENME', 'ΚΙΝΗΣΗ', 'PERGERAKAN', 'ムーブ\u200bメント', '움직임', '无\u200b球跑', '无\u200b球跑',
        'MOVEMENT', 'الحركة',),
    ('PASSES', 'PASSING'): (
        'PASSING', 'PASSING', 'PASSES', 'PASSEN', 'PASSAGGI', 'PASE', 'PASE', 'PASSE', 'PASSE', 'PASSEN',
        'AFLEVERING', 'PASNINGER', 'PASSNINGSSPEL', 'PODANIA', 'PASSING', 'ПАС', 'PAS', 'ΠΑΣΕΣ', 'OPERAN',
        'パ\u200bス', '패스', '传\u200b球', '传\u200b球', 'PASSING', 'التمرير',),
    ('Courtes', 'Shorter'): (
        'Shorter', 'Shorter', 'Courtes', 'Kürzer', 'Più corti', 'Más en corto', 'Más en corto', 'Mais curtos',
        'Mais curtos', 'Korter', 'Kortere', 'Kortere', 'Kortare', 'Krótko', 'Shorter', 'Короче', 'Kısa Pas',
        'Κοντινότερες', 'Lebih pendek', '短く', '짧게', '短\u200b传出\u200b球', '短\u200b传出\u200b球', 'Shorter', 'أقصر',),
    ('Directes', 'More direct'): (
        'More Direct', 'More Direct', 'Directes', 'Vertikaler', 'Più diretti', 'Más directo', 'Más directo',
        'Mais directos', 'Mais directos', 'Directer', 'Mere direkte', 'Mer direkte', 'Rakare',
        'Bardziej bezpośrednio', 'More Direct', 'Более прямолинейно', 'Dikine Uzun Paslı', 'Πιο Άμεσες',
        'Lebih Langsung', '直線的に', '더 다이렉트하게', '更\u200b多直\u200b传', '更\u200b多直\u200b传', 'More Direct', 'مباشر أكثر',),
    ('Normales', 'Normal'): (
        'Standard', 'Standard', 'Normales', 'Standard', 'Standard', 'Normales', 'Normales', 'Padrão', 'Padrão',
        'Standaard', 'Standard', 'Standard', 'Standard', 'Standardowe', 'Standard', 'Стандартная',
        'Standart Seviyede', 'Κανονικός', 'Standar', '標準的', '기본', '标\u200b准', '标\u200b准', 'Standard', 'عادية',),
    ('Ligne de but', 'Byline'): (
        'Byline', 'Byline', 'Ligne de but', 'Torauslinie', 'Linea di fondo', 'Línea de fondo', 'Línea de fondo',
        'Linha de fundo', 'Linha de fundo', 'Achterlijn', 'Baglinje', 'Dødlinja', 'Kortlinje', 'Linia końcowa',
        'Byline', 'Лицевая линия', 'Aut Çizgisi', 'Γραμμή Τέρματος', 'Garis Gawang', 'ゴールライン', '골라인', '底线', '底线',
        'Byline', 'خط المرمى',),
    ('En profondeur', 'Early'): (
        'Early', 'Early', 'En profondeur', 'Früh', 'In anticipo', 'Temprano', 'Temprano', 'Cedo', 'Cedo', 'Vroeg',
        'Tidligt', 'Tidlig', 'Tidigt', 'Wcześnie', 'Early', 'Раньше', 'Erken', 'Νωρίς', 'Lebih awal', '早めに', '일찍',
        '提前', '提前', 'Early', 'مبكرًا',),
    ('CENTRER DE', 'CROSS FROM'): (
        'CROSS FROM', 'CROSS FROM', 'CENTRER DE', 'FLANKE VON', 'CROSS DA', 'CENTRAR DESDE', 'CENTRAR DESDE',
        'CRUZAR DE', 'CRUZAR DE', 'VOORZETTEN VANAF', 'SLÅ INDLÆG FRA', 'LEGG INN FRA', 'INLÄGG FRÅN',
        'DOŚRODKOWANIA Z', 'CROSS FROM', 'НАВЕСЫ С', 'ORTA AÇMA ŞEKLİ', 'ΣΕΝΤΡΑ ΑΠΟ', 'UMPAN SILANG DARI', 'クロス供給',
        '크로스 위치', '起\u200b球点', '起\u200b球点', 'CROSS FROM', 'إرسال العرضية من',),
    ('Dribblez plus', 'Dribble more'): (
        'Dribble More', 'Dribble More', 'Dribblez plus', 'Häufiger dribbeln', 'Dribbla di più', 'Regatear más',
        'Regatear más', 'Fintar Mais', 'Fintar Mais', 'Meer dribbelen', 'Flere driblinger', 'Drible mer',
        'Dribbla mer', 'Więcej drybluj', 'Dribble More', 'Больше дриблинга', 'Daha Fazla Dripling Yap',
        'Ντρίμπλαρε Περισσότερο', 'Perbanyak Menggiring Bola', 'もっと\u200bド\u200bリ\u200bブ\u200bル\u200bし\u200bろ',
        '자주 드리블하라', '增\u200b加盘\u200b带', '增\u200b加盘\u200b带', 'Dribble More', 'تنفيذ مراوغات أكثر',),
    ('Dribblez moins', 'Dribble less'): (
        'Dribble Less', 'Dribble Less', 'Dribblez moins', 'Seltener dribbeln', 'Dribbla di meno', 'Regatear menos',
        'Regatear menos', 'Fintar Menos', 'Fintar Menos', 'Minder dribbelen', 'Færre driblinger', 'Drible mindre',
        'Dribbla mindre', 'Mniej drybluj', 'Dribble Less', 'Меньше дриблинга', 'Driplingi Azalt',
        'Ντρίμπλαρε Λιγότερο', 'Kurangi Menggiring Bola',
        'あ\u200bま\u200bり\u200bド\u200bリ\u200bブ\u200bル\u200bす\u200bる\u200bな', '적게 드리블하라', '减\u200b少盘\u200b带',
        '减\u200b少盘\u200b带', 'Dribble Less', 'تنفيذ مراوغات أقل',),
    ('BALLE AU PIED', 'DRIBBLING'): (
        'DRIBBLING', 'DRIBBLING', 'BALLE AU PIED', 'DRIBBLING', 'DRIBBLING', 'REGATE', 'REGATE', 'FINTA', 'FINTA',
        'DRIBBELEN', 'DRIBLING', 'DRIBLING', 'DRIBBLINGAR', 'DRYBLING', 'DRIBBLING', 'ДРИБЛИНГ', 'DRİPLİNG',
        'ΝΤΡΙΜΠΛΑ', 'DRIBEL', 'ド\u200bリ\u200bブ\u200bル', '드리블', '盘\u200b带', '盘\u200b带', 'DRIBBLING', 'المراوغة',),
    ('Plus souvent', 'Shoot more'): (
        'More Often', 'More Often', 'Plus souvent', 'Häufiger', 'Più spesso', 'Más a menudo', 'Más a menudo',
        'Com mais frequência', 'Com mais frequência', 'Vaker', 'Oftere', 'Oftere', 'Oftare', 'Częściej',
        'More Often', 'Чаще', 'Daha sık', 'Περισσότερο Συχνά', 'Lebih Sering', '頻度を\u200b上げ\u200bろ', '더 자주', '更频繁',
        '更\u200b多紧\u200b逼', 'More Often', 'بوتيرة مرتفعة',),
    ('Moins souvent', 'Shoot less'): (
        'Less Often', 'Less Often', 'Moins souvent', 'Seltener', 'Meno spesso', 'Menos a menudo', 'Menos a menudo',
        'Com menos frequência', 'Com menos frequência', 'Minder vaak', 'I mindre grad', 'Sjeldnere', 'Mer sällan',
        'Rzadziej', 'Less Often', 'Реже', 'Daha seyrek', 'Λιγότερο Συχνά', 'Lebih Jarang', '頻度を\u200b下げ\u200bろ',
        '덜 자주', '更少', '减\u200b少紧\u200b逼', 'Less Often', 'بوتيرة منخفضة',),
    ('TIRS', 'SHOOTING'): (
        'SHOOTING', 'SHOOTING', 'TIRS', 'TORSCHÜSSE', 'TIRO', 'DISPAROS', 'DISPAROS', 'FINALIZAÇÃO', 'FINALIZAÇÃO',
        'AFWERKEN', 'SKUD', 'AVSLUTNINGER', 'SKOTT', 'STRZAŁY', 'SHOOTING', 'УДАРЫ', 'ŞUT', 'ΣΟΥΤ', 'MENEMBAK',
        'シュート', '슈팅', '射\u200b门', '射\u200b门', 'SHOOTING', 'التسديد',),
    ('Plus de risques', 'More risky'): (
        'More risky', 'More risky', 'Plus de risques', 'Riskanter', 'Più rischiosi', 'Más arriesgados',
        'Más arriesgados', 'Mais arriscados', 'Mais arriscados', 'Riskanter', 'Mere risikable', 'Mer risikable',
        'Mer riskfyllda', 'Bardziej ryzykowne', 'More risky', 'Рискованнее', 'Daha riskli', 'Πιο ριψοκίνδυνες',
        'Lebih berisiko', 'リスクを増やす', '더 위험하게', '更冒险', '更冒险', 'More risky', 'مخاطرة أكبر',),
    ('Moins de risques', 'Less risky'): (
        'Less risky', 'Less risky', 'Moins de risques', 'Sicherer', 'Meno rischiosi', 'Menos arriesgados',
        'Menos arriesgados', 'Menos arriscados', 'Menos arriscados', 'Veiliger', 'Mindre risikable',
        'Mindre risikable', 'Mindre riskfyllda', 'Mniej ryzykowne', 'Less risky', 'Безопаснее', 'Daha az riskli',
        'Λιγότερο ριψοκίνδυνες', 'Kurang berisiko', 'リスクを減らす', '덜 위험하게', '更稳妥', '更稳妥', 'Less risky', 'مخاطرة أقل',),
    ('RISQUE DES PASSES', 'PASSING RISK'): (
        'PASSING RISK', 'PASSING RISK', 'RISQUE DES PASSES', 'PASSRISIKO', 'RISCHIO PASSAGGI', 'RIESGO EN LOS PASES',
        'RIESGO EN LOS PASES', 'RISCO DO PASSE', 'RISCO DO PASSE', 'PASSINGRISICO', 'AFLEVERINGSRISIKO',
        'PASNINGSRISIKO', 'PASSNINGSRISK', 'RYZYKOWNOŚĆ PODAŃ', 'PASSING RISK', 'РИСКОВАННОСТЬ ПАСА', 'PAS RİSKİ',
        'ΡΙΣΚΟ ΠΑΣΩΝ', 'RISIKO OPERAN', 'パ\u200bス\u200bの\u200bリ\u200bス\u200bク\u200b度', '패스 위험도', '传\u200b球风\u200b险',
        '传\u200b球风\u200b险', 'PASSING RISK', 'مجازفة التمريرات',),
    ('CENTRER VERS', 'CROSS TARGET'): (
        'AIM CROSSES AT', 'AIM CROSSES AT', 'CENTRER VERS', 'FLANKENZIEL', 'INDIRIZZA I CROSS VERSO',
        'CENTRAR HACIA', 'CENTRAR HACIA', 'APONTAR CRUZAMENTOS PARA', 'APONTAR CRUZAMENTOS PARA',
        'VOORZETTEN RICHTING', 'SLÅ INDLÆG MOD', 'SLÅ INNLEGG MOT', 'RIKTA INLÄGG MOT', 'CEL DOŚRODKOWANIA',
        'AIM CROSSES AT', 'ЦЕЛЬ НАВЕСА', 'NEREYE ORTA YAPILACAK', 'ΣΤΟΧΕΥΣΗ ΣΕΝΤΡΑΣ ΣΕ', 'TARGET UMPAN SILANG',
        'ク\u200bロ\u200bス\u200bの\u200b狙い', '크로스 목표', '传\u200b中目\u200b标', '传\u200b中目\u200b标', 'AIM CROSSES AT',
        'هدف العرضيات',),
    ('Attaquant pivot', 'Target man'): (
        'Target Forward', 'Target Forward', 'Attaquant pivot', 'Zielspieler', 'Fulcro del gioco',
        'Delantero objetivo', 'Delantero objetivo', 'Avançado de referência', 'Avançado de referência',
        'Doelgerichte aanvaller', 'Targetman', 'Oppspillspunkt', 'Bollmottagare', 'Odgrywający', 'Target Forward',
        'Таргетмен', 'Pivot Santrafor', 'Επιθετικός-Στόχος', 'Pemain Depan Target', 'ターゲット\u200bフォワード', '타깃 포워드',
        '站\u200b桩中\u200b锋', '站\u200b桩中\u200b锋', 'Target Forward', 'مهاجم محطة',),
    ('Normal', 'Normal'): (
        'Normal', 'Normal', 'Normal', 'Normal', 'Normale', 'Normal', 'Normal', 'Normal', 'Normal', 'Normaal',
        'Normal', 'Normal', 'Normal', 'Normalny', 'Normal', 'Норма', 'Normal', 'Κανονικό', 'Normal', '普通', '보통',
        '正\u200b常', '正\u200b常', 'Normal', 'طبيعي',),
    ('Sélectionné', 'Selected'): (
        'Selected', 'Selected', 'Sélectionné', 'Auswahl', 'Selezionato', 'Seleccionado', 'Seleccionado',
        'Seleccionado', 'Seleccionado', 'Geselecteerd', 'Valgt', 'Valgt', 'Vald', 'Wybrany', 'Selected', 'Выбрано',
        'Seçili', 'Επιλεγμένο', 'Dipilih', '選択済み', '선택됨', '已\u200b选', '已\u200b选', 'Selected', 'محدد',),
    ('Fait partie du rôle', 'Part Of Role'): (
        'Part Of Role', 'Part Of Role', 'Fait partie du rôle', 'Teil der Rolle', 'Parte del ruolo', 'Parte del rol',
        'Parte del rol', 'Parte Do Papel', 'Parte Do Papel', 'Hoort bij rol', 'Del af rolle', 'Del av rolle',
        'Del av roll', 'Część roli', 'Part Of Role', 'Часть роли', 'Rolü İçeriyor', 'Μέρος Του Ρόλου',
        'Bagian dari peran', '選択中の\u200b役割', '이미 맡음', '位\u200b置固\u200b有', '位\u200b置固\u200b有', 'Part Of Role',
        'جزء من الدور',),
    ('Incompatible', 'Incompatible'): (
        'Conflicting', 'Conflicting', 'Incompatible', 'Kollidiert', 'Conflittuale', 'Conflictivo', 'Conflictivo',
        'Conflito', 'Conflito', 'Conflicterend', 'Konflikt', 'Konflikt', 'Konflikt', 'Konflikt', 'Conflicting',
        'Конфликт', 'Uyumsuz', 'Σε αντίθεση', 'Bertentangan', 'マッチ\u200bし\u200bな\u200bい', '충돌됨', '冲\u200b突',
        '冲\u200b突', 'Conflicting', 'متعارض',),
    ('Indisponible', 'Unavailable'): (
        'Unavailable', 'Unavailable', 'Indisponible', 'Nicht verfügbar', 'Indisponibile', 'No disponible',
        'No disponible', 'Indisponível', 'Indisponível', 'Niet beschikbaar', 'Ikke tilgængelig', 'Utilgjengelig',
        'Otillgänglig', 'Niedostępne', 'Unavailable', 'Недоступно', 'Mevcut değil', 'Μη Διαθέσιμο', 'Tidak Tersedia',
        '選択不可', '불가능', '不\u200b可用', '不\u200b可用', 'Unavailable', 'غير متاح',),
    ('CONSTRUCTION DU JEU', 'BUILD-UP PLAY'): (
        'BUILD-UP PLAY', 'BUILD-UP PLAY', 'CONSTRUCTION DU JEU', 'SPIELAUFBAU', 'COSTRUZIONE DAL BASSO',
        'CRECIMIENTO DEL JUEGO', 'CRECIMIENTO DEL JUEGO', 'FASE DE CONSTRUÇÃO', 'FASE DE CONSTRUÇÃO',
        'OPBOUW-SPEELSTIJL', 'OPBYGNINGSSPIL', 'OPPBYGGING', 'SPELUPPBYGGNAD', 'PRZYGOTOWANIE AKCJI',
        'BUILD-UP PLAY', 'ПОСТРОЕНИЕ ИГРЫ', 'OYUN KURMA', 'ΑΝΑΠΤΥΞΗ', 'MEMBANGUN SERANGAN',
        'ビ\u200bル\u200bド\u200bアップ', '빌드업 플레이', '组\u200b织战\u200b术', '组\u200b织战\u200b术', 'BUILD-UP PLAY', 'بناء اللعب',),
    ('30 DERNIERS MÈTRES', 'FINAL THIRD'): (
        'FINAL THIRD', 'FINAL THIRD', '30 DERNIERS MÈTRES', 'ANGRIFFSDRITTEL', 'TREQUARTI', 'ÚLTIMO TERCIO',
        'ÚLTIMO TERCIO', 'ÚLTIMO TERÇO', 'ÚLTIMO TERÇO', 'VOORIN', 'SIDSTE TREDJEDEL', 'SISTE TREDJEDEL',
        'SISTA TREDJEDELEN', 'NA PRZEDPOLU BRAMKI RYWALA', 'FINAL THIRD', 'ПОСЛЕДНЯЯ ТРЕТЬ', 'ÜÇÜNCÜ BÖLGE',
        'ΠΕΡΙΟΧΗ ΤΟΥ ΑΝΤΙΠΑΛΟΥ', 'SEPERTIGA AKHIR', 'ファイ\u200bナ\u200bル\u200bサード', '상대팀 진영', '进\u200b攻区\u200b域',
        '进\u200b攻区\u200b域', 'FINAL THIRD', 'الثلث الأخير',),
    ('LORS DE LA PERTE DU BALLON', 'WHEN POSSESSION IS LOST'): (
        'WHEN POSSESSION HAS BEEN LOST', 'WHEN POSSESSION HAS BEEN LOST', 'LORS DE LA PERTE DU BALLON',
        'NACH BALLVERLUST', 'QUANDO SI PERDE IL POSSESSO', 'CUANDO SE PIERDE LA POSESIÓN',
        'CUANDO SE PIERDE LA POSESIÓN', 'QUANDO SE PERDEU A POSSE DE BOLA', 'QUANDO SE PERDEU A POSSE DE BOLA',
        'WANNEER HET BALBEZIT IS VERLOREN', 'NÅR BOLDEN ER BLEVET MISTET', 'ETTER BALLTAP', 'NÄR BOLLEN TAPPATS',
        'PO STRACIE PIŁKI', 'WHEN POSSESSION HAS BEEN LOST', 'КОГДА ПОТЕРЯН МЯЧ', 'TOP KAYBEDİLDİĞİNDE',
        'ΟΤΑΝ ΧΑΣΟΥΜΕ ΤΗΝ ΚΑΤΟΧΗ', 'SAAT KEHILANGAN BOLA', 'ボール\u200bロ\u200bス\u200bト\u200b時', '공을 빼앗겼을 때',
        '失\u200b去球\u200b权时', '失\u200b去球\u200b权时', 'WHEN POSSESSION HAS BEEN LOST', 'عند فقدان الكرة',),
    ('LORS DE LA RÉCUPÉRATION DU BALLON', 'WHEN POSSESSION IS WON'): (
        'WHEN POSSESSION HAS BEEN WON', 'WHEN POSSESSION HAS BEEN WON', 'LORS DE LA RÉCUPÉRATION DU BALLON',
        'NACH BALLGEWINN', 'QUANDO SI CONQUISTA IL POSSESSO', 'CUANDO SE RECUPERA LA POSESIÓN',
        'CUANDO SE RECUPERA LA POSESIÓN', 'QUANDO SE GANHOU A POSSE DE BOLA', 'QUANDO SE GANHOU A POSSE DE BOLA',
        'WANNEER HET BALBEZIT IS GEWONNEN', 'NÅR BOLDBESIDDELSE ER BLEVET VUNDET', 'ETTER BALLGJENVINNING',
        'NÄR BOLLEN ERÖVRATS', 'PO ODBIORZE PIŁKI', 'WHEN POSSESSION HAS BEEN WON', 'КОГДА ПЕРЕХВАЧЕН МЯЧ',
        'TOP KAZANILDIĞINDA', 'ΟΤΑΝ ΚΕΡΔΙΣΟΥΜΕ ΤΗΝ ΚΑΤΟΧΗ', 'SAAT MEREBUT BOLA', 'ボール\u200b奪取時', '공을 되찾았을 때',
        '赢\u200b得球\u200b权时', '赢\u200b得球\u200b权时', 'WHEN POSSESSION HAS BEEN WON', 'عند استعادة الكرة',),
    ('GARDIEN AVEC LE BALLON', 'GOALKEEPER IN POSSESSION'): (
        'GOALKEEPER IN POSSESSION', 'GOALKEEPER IN POSSESSION', 'GARDIEN AVEC LE BALLON', 'TORHÜTER IN BALLBESITZ',
        'PORTIERE IN POSSESSO', 'PORTERO CON LA POSESIÓN', 'PORTERO CON LA POSESIÓN', 'GUARDA-REDES COM BOLA',
        'GUARDA-REDES COM BOLA', 'DOELMAN IN BALBEZIT', 'MÅLMAND I BOLDBESIDDELSE', 'NÅR MÅLVAKTEN HAR BALLEN',
        'MÅLVAKT MED BOLLEN', 'BRAMKARZ PRZY PIŁCE', 'GOALKEEPER IN POSSESSION', 'ВРАТАРЬ С МЯЧОМ',
        'TOP KALECİDEYKEN', 'ΤΕΡΜΑΤΟΦΥΛΑΚΑΣ ΜΕ ΚΑΤΟΧΗ', 'KIPER MENGUASAI BOLA', 'キーパーの\u200bポ\u200bゼッション時',
        '골키퍼가 공을 소유', '门\u200b将控\u200b球', '门\u200b将控\u200b球', 'GOALKEEPER IN POSSESSION', 'الحارس مستحوذ على الكرة',),
    ('FORMATION DÉFENSIVE', 'DEFENSIVE SHAPE'): (
        'DEFENSIVE SHAPE', 'DEFENSIVE SHAPE', 'FORMATION DÉFENSIVE', 'DEFENSIVE FORMATION', 'CONFIGURAZIONE DIFESA',
        'DIBUJO DEFENSIVO', 'DIBUJO DEFENSIVO', 'FORMA DEFENSIVA', 'FORMA DEFENSIVA', 'DEFENSIEVE VORM',
        'DEFENSIV FORMATION', 'DEFENSIV FASONG', 'DEFENSIV FORMATION', 'FORMACJA DEFENSYWNA', 'DEFENSIVE SHAPE',
        'ЗАЩИТНОЕ ПОСТРОЕНИЕ', 'SAVUNMA BÜTÜNLÜĞÜ', 'ΑΜΥΝΤΙΚΟ ΣΧΗΜΑ', 'FORMASI BERTAHAN', '守備陣形', '수비 형태',
        '防\u200b守队\u200b形', '防\u200b守队\u200b形', 'DEFENSIVE SHAPE', 'التشكيل الدفاعي',),
    ('»  CHANGER', '»  CHANGE'): (
        '»  CHANGE', '»  CHANGE', '»  CHANGER', '»  ÄNDERN', '»  CAMBIA', '»  CAMBIAR', '»  CAMBIAR', '»  ALTERAR',
        '»  ALTERAR', '»  WIJZIGEN', '»  ÆNDR', '»  ENDRE', '»  ÄNDRA', '»  ZMIEŃ', '»  CHANGE', '»  ИЗМЕНИТЬ',
        '»  DEĞİŞTİR', '»  ΑΛΛΑΓΗ', '»  UBAH', '»  変更', '»  변경', '»  更改', '»  更改', '»  CHANGE', '»  تغيير',),
}
COURSES24 = [(31, 28, True, 2, 24, ("Dédoublements extérieurs gauches", "Overlap Left")),
             (28, 31, True, 26, 24, ("Dédoublements intérieurs gauches", "Underlap Left")),
             (28, 31, False, 50, 24, ("Dédoublements intérieurs droits", "Underlap Right")),
             (31, 28, False, 74, 24, ("Dédoublements extérieurs droits", "Overlap Right"))]
#            (consigne, l'autre, côté gauche, x, largeur, phrase) : extérieurs (31) et intérieurs (28)
Y_COURSES24, H_COURSES24 = 15.5, 22
PROGRESSION24 = [("G", 2, 2, 32, ("Concentrez le jeu sur l'aile gauche", "Focus Play Down The Left Flank")),
                 ("A", 1, 34, 32, ("Concentrez le jeu dans l'axe", "Focus Play Through The Middle")),
                 ("D", 3, 66, 32, ("Concentrez le jeu sur l'aile droite", "Focus Play Down The Right Flank"))]
Y_PROGRESSION24, H_PROGRESSION24 = 37.5, 29.5
RAPPORT_CONSTRUCTION24 = 1.25   # v27 (Kinito : « l'augmenter un peu en hauteur », la place libre sous la colonne) ; v20-v26 : RAPPORT_ZONES24
STRATEGIE24 = [(0, 2, 67, 96, 15), (2, 2, 82, 32, round(100 - 82 - 2 / RAPPORT_CONSTRUCTION24, 2))]   # v27 : la marge du bas recalculée (2 % de la largeur)   # v23 : contourner : 1/3 de la largeur, même marge à gauche (2 % de la largeur) qu'en bas (1,8 % de la hauteur)   # v22 : (place, x, y, l, h) : « Gérer le pressing » en bande
#              sur toute la largeur (« Sortez de la défense » de FM24), « Contourner le pressing » dessous, à gauche
def courbe24(p0, p1, p2, n=8):
    """v23 : les points d'une courbe (Bézier du 2e degré) de p0 à p2, tirée vers p1 (flèches courbes de FM24)"""
    out = []
    for i in range(n + 1):
        u = i / n
        out.append(((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
                    (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]))
    return out


_EXT_G, _EXT_D = courbe24((14, 62), (0, 44), (12, 24)), courbe24((86, 62), (100, 44), (88, 24))
_INT_G, _INT_D = courbe24((40, 62), (31, 44), (39, 24)), courbe24((60, 62), (69, 44), (61, 24))
_AILE_G, _AILE_D, _AXE = [(50, 72), (17, 48)], [(50, 72), (83, 48)], [(50, 72), (50, 46)]
FLECHES_CONSTRUCTION24 = {   # v22-v23 : option -> [(points, pointillés)] en % du terrain (captures 7 et 33 de FM24)
    31: {1: [(_EXT_G, True)], 2: [(_EXT_D, True)], 3: [(_EXT_G, True), (_EXT_D, True)]},   # dédoublements : courbes
    28: {1: [(_INT_G, True)], 2: [(_INT_D, True)], 3: [(_INT_G, True), (_INT_D, True)]},
    30: {1: [(_AXE, False)], 2: [(_AILE_G, False)], 3: [(_AILE_D, False)], 4: [(_AILE_G, False), (_AILE_D, False)]},
    24: {0: [([(50, 81), (36, 64)], False), ([(50, 81), (50, 62)], False), ([(50, 81), (64, 64)], False)]}}
FLECHES_FINITION24 = {   # v23 : captures 34 à 36 de FM24
    18: {2: [([(22, 44), (38, 16)], False), ([(78, 44), (62, 16)], False)],          # jouer dans la surface
         0: [(courbe24((12, 46), (8, 10), (40, 8)), False), (courbe24((88, 46), (92, 10), (60, 8)), False)]},
    27: {2: [([(50, 40), (50, 8)], False)]}}                                        # tirez à vue
ZONES_GB24 = {6: [(1.5, 1, 97, 16.5)], 5: [(34.5, 17.5, 31, 20)],   # v22 : relances du gardien, places de FM24
              3: [(1.5, 17.5, 33, 50.5), (65.5, 17.5, 33, 50.5)], 4: [(34.5, 37.5, 31, 30.5)],
              2: [(1.5, 68, 33, 18.5), (65.5, 68, 33, 18.5)], 1: [(34.5, 68, 31, 18.5)]}
RAPPORT_GB24 = 1.2   # hauteur / largeur (FM24 : 243 × 203 px)
RAPPORT_TRANSITION24 = RAPPORT_TERRAIN   # v27 (Kinito : « comme la largeur, en proportions ») ; v22-v26 : 1,2
PART_TRANSITION24 = 92   # % de la colonne : les terrains de transition
CHEMIN_OPTION24 = "tactic.SelectedTeamInstructionOption"   # le code de l'option en cours (dans l'enveloppe)
# v25 (Kinito : « on peut faire des formations qui n'existent pas en preset », asymétriques : « il faut que les pions
# correspondent au poste choisi avec ballon ») : un pion par joueur de la tactique, à son POSTE LU. La v24 (test) l'a
# lu en jeu sur trois tactiques de Kinito : pour le joueur n° 0 à 10 de la tactique (variable « teamselectionindex »,
# 0 = le gardien), Tactic.PositionFromTeamSelectionIndex.Position (ce que lit la cellule de poste de FM,
# PlayerOverviewPositionCell) donne son poste avec ballon (variable « inpossession » vraie) ou sans ballon (fausse),
# en masque de bits : les bits de PositionCombined du plugin, plus, pour un poste central, son couloir : 2^20 = décalé
# à gauche, 2^21 = décalé à droite, aucun = au centre (vérifié sur les D, MD, M, MO et BT de Kinito)
CHEMIN_POSTE24 = "tactic.PositionFromTeamSelectionIndex.Position"
NB_JOUEURS24 = 11
B_GAUCHE24, B_DROITE24 = 1 << 20, 1 << 21
POSTES24 = {}   # poste lu -> (colonne de COLONNES24, ligne de LIGNES24) ; le gardien (1) est posé à part
for _centre, _ligne, _cotes in ((16, 1, {8: "L", 4: "R"}),          # DG, DC, DD
                                (128, 2, {64: "L", 32: "R"}),       # LATG, MDC, LATD
                                (1024, 3, {512: "L", 256: "R"}),    # MLG, MC, MLD
                                (8192, 4, {4096: "L", 2048: "R"}),  # MOG, MOC, MOD
                                (16384, 5, {})):                    # ATC
    POSTES24[_centre] = ("C", _ligne)
    POSTES24[_centre | B_GAUCHE24] = ("CL", _ligne)   # DCG, MDG, MCG, MOCG, ATG
    POSTES24[_centre | B_DROITE24] = ("CR", _ligne)   # DCD, MDD, MCD, MOCD, ATD
    for _v, _c in _cotes.items():
        POSTES24[_v] = (_c, _ligne)
if len(POSTES24) != 23:
    raise ValueError("postes de champ : 23 attendus (les 24 de Kinito moins le gardien)")
# v26 (Kinito : « rapprocher un peu les deux numéros 6 lorsqu'ils sont deux, et garder le même emplacement quand ils
# sont trois ; pareil pour les MC, les MOC et les attaquants ») : sur ces lignes (pas les défenseurs), un central décalé
# se rapproche de l'axe quand PERSONNE n'est au centre de sa ligne. Pour le savoir, chaque terrain calcule une fois,
# pour chaque ligne, « un joueur au centre ? » : le poste lu de chacun des 11 joueurs comparé au centre de la ligne
# (kinitoc<ligne>j<joueur>), puis la fonction de FM qui combine des booléens (BindMultipleBooleanArgsToDestination,
# opérateur Ou ; forme relevée dans PressConferenceDynamicCard) écrit kinitocentre<ligne>
LIGNES_DUO24 = {2: 128, 3: 1024, 4: 8192, 5: 16384}   # ligne -> poste du centre (MD, MC, MOC, ATC)
COLONNES_DUO24 = {"CL": 38, "CR": 62}                 # % de la largeur : deux centraux seuls (v23 : CL2 / CR2)
GUID_OU24 = "b6e89d1f787dcc1418384a60680a7f5a"        # BindMultipleBooleanArgsToDestination
T_LISTE24 = b"SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BooleanArg]"
T_LOGIQUE24 = b"SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.VisibleFunctions+LogicOperator]"
T_CHEMIN24 = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"
OU24 = 1   # LogicOperator : 0 = Et, 1 = Ou (ClubStaffActionsButtons, PressConferenceDynamicCard)
COLONNES24 = {"L": 9, "CL": 30, "C": 50, "CR": 70, "R": 91}   # % de la largeur (v25 : les couloirs de FM 27, relevés
#              sur le terrain du positionnement : 10 / 30 / 50 / 70 / 90 %)
LIGNES24 = {1: 79, 2: 64, 3: 49, 4: 32, 5: 14}                                       # % de la hauteur
MARGES_LARGEUR24 = [(0, 16), (0, 8), (1, 16), (2, 8), (3, 4)]   # (cran, marge de chaque côté en px) : 24, 16, 8, 4, 0
PION_GB24 = (50, 93)
TAILLE_PION24, TAILLE_FLECHE24, TIRETS24 = 15, 10, 7
PART_PION24 = round(100 * 17 / 272, 2)   # v27 (Kinito : « les pions proportionnels au terrain ») : % de la largeur du terrain sans ballon (comme 17 px sur les 272 de la largeur)
REDUIT24 = [(110, 4), (120, 8)]   # v27 : (taille du texte de FM, marge de chaque côté en px) : les terrains de la
#   construction et de la finition rétrécissent (donc raccourcissent) en Grand et Plus grand, où leurs colonnes
#   grandissent avec le texte (estimé, pas vu en jeu)
# v28 (Kinito, captures en Petit, Normal, Grand et Plus grand : « la case pour la hauteur def et le pressing est bien
# pour le petit mais pas terrible pour les autres grandeurs ») : la colonne de gauche du terrain des lignes (encadrés,
# crans) a la largeur qu'il faut à chaque taille du texte de FM (settings.TextScaling), le terrain prend le reste.
# L'encadré le plus large (« Ligne défensive / Beaucoup plus basse ») mesure 148 px en Petit sur sa capture (texte 130,
# marges et bord 18) : son texte suit la taille (130 / 0,85 × taille), plus 20 px d'air et 26 pour les crans (22 + 4).
# En Petit : 194 px, la place de la v27, que Kinito trouve bien. La première est celle d'une valeur illisible
LARGEUR_GAUCHE24 = {120: 248, 85: 194, 100: 217, 110: 232}
# v28 : le texte des zones des terrains et du bouton « Obtenir des coups de pied arrêtés » garde la taille du Normal en
# Grand et Plus grand (sur ses captures, « Dédoublements », « Centrer », « Défenseurs » se coupaient au milieu ; le
# bouton débordait) : sa police est réduite d'autant, une variante par taille (selon_taille24)
TAILLES_TEXTE24 = {110: 100 / 110, 120: 100 / 120}
TAILLE_TEXTE24 = 14   # px, la police de body-md (--body-md-size = --typography-size-14, AlwaysAppliedStyleSheet)
TAILLE_PION_LARGEUR24 = 17   # v26 : le terrain de la largeur, plus grand (aux vraies proportions)
# v23 (Kinito : « découper en 3 la partie haute du terrain pour le pressing ») : la hauteur du pressing (bloc bas,
# bloc médian, pressing haut) au milieu de chaque tiers de la moitié haute, et ses bandes de clic = les tiers
Y_PRESSING24 = [41.7, 25.0, 8.3]
BANDES_PRESSING24 = [(33.3, 50.0), (16.7, 33.3), (0.0, 16.7)]
LIGNES_SANS24 = {5: 0, 4: 25, 3: 50, 2: 75, 1: 100}   # % de la zone entre la ligne de pressing et la ligne défensive
LARGEUR_CRANS24 = 22   # px, la colonne des points des crans, à gauche du terrain des lignes (v23 à v44)
# v45 (Kinito, capture de la v44 en Petit, 05/11 : « centrer le terrain, l'agrandir au max en gardant les proportions »,
# encadrés « côte à côte au-dessus, ligne déf à gauche et pressing à droite », points des crans « sur la ligne de
# touche, gauche et droite ; la ligne s'arrête sur les points ») : le terrain est encadré de deux marges égales, une
# largeur par taille du texte (MARGE_TERRAIN_SANS24, unités), au milieu, les encadrés puis le terrain. Mesuré sur sa
# capture (Petit, 1920 × 1080, 1 u = 1,1428 px) : la colonne fait 493,5 u de large (x 616 à 1180 px) ; sous le titre,
# 588 u de haut (y 343 à 1015 px) ; un encadré 39,4 u (45 px). Calcul (pas mesuré au-delà du Petit) : l'encadré
# grandit avec le texte (32,4 u de texte en Petit : 45,1 / 48,9 / 52,7 u en Normal / Grand / Plus grand), le titre de
# 2 à 4 u ; hauteur du terrain = le reste moins l'écart (ECART_ENCADRES_SANS24) ; largeur = hauteur × 68 / 105, moins
# 2 % de garde : 343 / 338 / 335 u ; marge = (493,5 - largeur) / 2. En Plus grand, un encadré n'a plus la largeur de
# son texte (le plus long, « Beaucoup plus basse », 114 u en Petit, × 120 / 85 = 161 u ; « HAUTEUR DU PRESSING »
# 109 u, 154 u) : les deux passent sur deux lignes (+ 31 u), le terrain est compté avec : 316 u. La première valeur
# sert si la taille est illisible (comme LARGEUR_GAUCHE24) : celle du Plus grand, la plus prudente
MARGE_TERRAIN_SANS24 = {120: 89, 85: 75, 100: 78, 110: 79}
ECART_ENCADRES_SANS24 = 8   # unités, entre les deux encadrés, et entre les encadrés et le terrain
POINT_CRAN24, POINT_CRAN_CHOISI24 = 7, 12   # px, les points des crans (comme crans24) ; celui du cran en cours plus gros
FLECHES_TRANSITION24 = {   # v22 : option -> (petites flèches de chaque pion : (dx, dy en px, angle ; 0 = vers le haut),
    #                          seulement les joueurs excentrés)
    11: {2: ([(-6, -9, -35), (6, -9, 35)], False), 0: ([(0, 10, 180)], False)},   # contre-pressing ↖↗, regroupement ↓
    3: {2: ([(0, -10, 0)], False),                                               # contre-attaque ↑ (v23 : place 2)
        0: ([(-11, 0, 90), (11, 0, -90)], True)}}   # v23 : rester en place, ›●‹ sur les excentrés (capture de FM24)
EXCENTRE24 = 25   # % : écart à l'axe à partir duquel un pion est excentré
MOTS_RELANCE_COURTE24 = ("Empêchez rel. courtes du GB", "Prevent Short GK Distribution")   # capture 9 de FM24
MOTS_RESUME24 = {23: {1: MOTS_RELANCE_COURTE24}}
PATIENCE24 = [(2, 26, 0.5, 48, 16.5), (0, 1.5, 17, 22.5, 32.5), (0, 76, 17, 22.5, 32.5)]   # (place, x, y, l, h)
TIRS24 = [(2, 24, 17, 52, 16.15, ("Tirez à vue", "Shoot On Sight")),   # v23 : les deux de la même taille
          (0, 24, 33.15, 52, 16.15, ("Moins de tirs de loin", "Shoot Less Often"))]
ICONES_CURSEURS24 = {1: "game-concepts-ball-white_small", 21: "game-concepts-time-passing_small",
                     7: "game-concepts-time_small", 10: "game-concepts-trigger-press-always_small"}   # icônes de FM 27
ICONES_PHASES24 = ["game-concepts-in-possession_small", "game-concepts-in-transition_small",
                   "game-concepts-out-of-possession_small"]
REPERE_HAUT24, REPERE_BAS24 = "game-concepts-sort-arrow-down_small", "game-concepts-sort-arrow-up_small"   # ▼ ▲
TAILLE_ICONE24, TAILLE_REPERE24 = 16, 7
PARENT24 = "TacticalPlannerTeamInstructions"   # le modèle de l'onglet : ses variables passent aux trois blocs
DROITE24 = "PhasesTeamInstructionsBlock"       # la colonne de droite (« Vue d'ensemble »… « Sélectionner »)
NOM_DROITE = f"{base.PREFIXE}-droite-v{VERSION}"
# v30 (VERSION DE TEST, Kinito : « recréer aussi le réglage des consignes individuelles de FM24 », un seul écran) : la
# fenêtre des consignes individuelles de FM 27 (PlayerInstructionRoleEditCard) range ses blocs dans une grille de 12
# colonnes (compositions PlayerInstructionGroupsInPossession / OutOfPossessionComposition-NONE, bundle ui-tactics) : à
# gauche ce bloc (x0 y0 4×6, le même dans les deux onglets), les tuiles sur les 8 autres colonnes. Aucun bloc ne
# couvre toutes les tuiles : la vue FM24 partirait de ce bloc, posée à sa droite. Le test : un cadre orange à cette
# place (mesurée sur sa capture en 1920 × 1080 : colonne de grille 72,75 px, écart 21 px ; le bloc 354 px de large,
# les tuiles 729 px, à 21 px de lui), qui laisse passer les clics. À vérifier en jeu : pas coupé par la grille, posé
# AU-DESSUS des tuiles, et pile sur elles
INDIV24 = "PlayerInstructionSelectedPlayerBlock_4x6"
NOM_INDIV = f"{base.PREFIXE}-indiv-v{VERSION}"
CADRE_INDIV24 = (round(100 * 375 / 354, 1), round(100 * 729 / 354, 1))   # gauche et largeur, en % du bloc
# v31 (test 1 vu en jeu : pas coupé, pile sur les tuiles, mais « Risque des passes », « Centrer de » et les deux
# « Attaquer la surface » passent DEVANT : le jeu crée les blocs dans l'ordre de la composition, et ces quatre-là
# viennent après le bloc de gauche avec le ballon ; sans le ballon, il est le dernier) : avec le ballon, le cadre part
# de la DERNIÈRE tuile créée, « Attaquer la surface » du bas (x10 y5, 2 × 1), ancré en bas à droite ; le bloc de gauche
# ne le montre plus que sans le ballon (interrupteur sur « inpossession »). La grille est carrée (colonne et rangée
# 72,75 px, écart 21 px, sur sa capture) : la tuile fait 166,5 × 72,75 px, les tuiles 729 × 541,5 px
INDIV_TUILE24 = "PlayerInstructionGroupAttackBoxDepthTile_2x1"
NOM_INDIV_TUILE = f"{NOM_INDIV}-tuile"
# v49 : la largeur du cadre est celle de la vue sans le ballon (CADRE_INDIV24 : 205,9 % du bloc de 354 px, soit
# 728,9 px), au lieu de 730 px mesurés à part (432,0 % de la tuile de 169 px : 730,1 px, 1,2 de trop)
# v50 (Kinito : « encore un décalage, uniquement en largeur ») : mesuré sur ses captures 40 / 41 (v49), la colonne
# « Sans ballon (équipe) » est 1 px plus ÉTROITE avec le ballon, et tout ce qui est à sa droite 1 px plus à gauche ; en
# v48 (38 / 39), elle était 1 px plus LARGE. C'est elle seule qui prend les changements de largeur (les deux autres
# sont à la taille de leur contenu : disques, grilles), d'où un saut d'un pixel entier. La bonne largeur est donc
# entre la v49 et la v48 (1,19 px d'écart) : AJUSTE_AVEC24 = 1 px de plus que la v49, la seule valeur qui tombe
# juste quelle que soit la position exacte (inconnue) des bords dans leur pixel, d'après les deux mesures
AJUSTE_AVEC24 = 1.0
LARGEUR_VUE24 = 354 * CADRE_INDIV24[1] / 100 + AJUSTE_AVEC24
CADRE_TUILE24 = (round(100 * LARGEUR_VUE24 / 169, 3), round(100 * 543 / 76, 1))   # largeur, hauteur en % de la tuile
# v48 (Kinito : « quand je switch avec / sans ballon, les consignes ne doivent pas bouger d'un pixel ») : mesuré sur
# ses deux captures du 06/11 (1920 × 1080, même vue des deux côtés, au quart de pixel : outils de Claude), sans le
# ballon tout est 4 px plus HAUT (en-têtes, colonnes, boutons), la légende (calée en bas) 1 px plus haut, et le tout
# ~0,5 px plus à DROITE. La vue sans le ballon est calée sur le haut et le bas du bloc de gauche (deux rangées de la
# grille, exactes) : c'est la vue avec le ballon qui la rejoint. CALE_AVEC24 = (droite, haut du cadre, haut de la
# vue) en px : le cadre décalé de 0,5 vers la droite et de 1 vers le haut, le haut de la vue monté de 3 de plus
# v49 : le cadre, ancré à droite, a perdu 1,2 px de large (LARGEUR_VUE24) : sa marge droite passe de -0,5 à +0,7 pour
# que son bord GAUCHE reste où la v48 l'a mis (aligné sur la vue sans le ballon, mesuré sur les captures 38 / 39 ;
# v50 : toujours vrai sur 40 / 41, au sous-pixel près) ; v50 : 1 px plus large, la marge droite suit (-0,31)
CALE_AVEC24 = (round(-0.5 + (432.0 - CADRE_TUILE24[0]) * 169 / 100, 2), 1, 3)
# v51 : CADRE_INDIV24, AJUSTE_AVEC24, LARGEUR_VUE24, CADRE_TUILE24 et CALE_AVEC24 ne servent plus (gardés pour
# l'historique ci-dessus). Mesuré par FMSonde 0.22.1 (Ctrl+F11, 07/11, 1920 × 1080, les deux onglets) :
#  - la grille de la fenêtre : cases de 66, écart 16, bord 12 (GridLayoutSettings, en points) ; le bloc de gauche
#    x0 y0 4 × 6 (312 × 476), la tuile « Attaquer la surface » x10 y5 2 × 1 (148 × 66), placés au point près ;
#  - le jeu ARRONDIT AU PIXEL LES MARGES, LES BORDS ET LES ÉCARTS AVANT de placer (la marge de -0,31 de la v50 valait
#    0, celle de -0,5 de la v48 un pixel entier ; le bord de 1 du bloc vaut 0,875 point en 1080p), pas les
#    pourcentages ni les largeurs ; puis il arrondit chaque bord d'après sa place EXACTE sur l'écran. Le calcul refait
#    ainsi retrouve les places mesurées (« Plus » à 47 px avec le ballon, 48 sans) : avec le ballon, la vue était 0,6
#    point plus à gauche et 0,4 plus large, d'où les textes au tiers ou centrés qui sautaient d'un pixel ;
#  - d'où : les deux vues posées sur la même zone, les colonnes 4 à 11 de la grille (ZONE_INDIV24), en POINTS
#    ENTIERS depuis le bloc (sans le ballon) et depuis la tuile (avec) : le jeu n'arrondit pas les positions
#    fixes avant de placer (mesuré : le « joueur » des ronds, à 69 points, tombe à 79 px dans une vue et 78 dans
#    l'autre), et des points entiers s'additionnent sans erreur, là où des pourcentages (328 / 312 du bloc,
#    -492 / 148 de la tuile) laissaient 0,00003 point d'écart, de quoi faire encore sauter un élément de temps en
#    temps. La grille ne change pas de taille d'une résolution à l'autre (cases de 66 en 1080p comme dans ses
#    réglages ; le panneau fait toujours 945 points de haut) : à remesurer si FM la change. Le bord du bloc
#    (BORD_BLOC24, lu dans le modèle de FM) est annulé par une marge égale, arrondie pareil. Des deux côtés, la MÊME
#    boîte « zone » de taille fixe (640 × 476, posée en points entiers), et dedans la vue pleine avec les mêmes
#    marges (DEBORD_INDIV24) : les mêmes calculs, dans le même ordre, donc les mêmes arrondis à toute résolution
#    (avec la largeur tirée du bloc, 312 - 2 bords + 2 marges, il restait 0,00001 point d'écart en 900, 1050, 1200
#    et 1600 px de haut).
CASE24, ECART24 = 66, 16   # la grille de la fenêtre des consignes individuelles (points)
PAS24 = CASE24 + ECART24
BORD_BLOC24 = 1   # border-width du ComponentElement du bloc de gauche (son modèle d'origine : width 312, padding 12)
BLOC24 = (4 * CASE24 + 3 * ECART24, 6 * CASE24 + 5 * ECART24)          # 312 × 476, en x0 y0
TUILE24 = (2 * CASE24 + ECART24, CASE24, 10 * PAS24, 5 * PAS24)       # 148 × 66, en x10 y5 (820, 410 du bloc)
ZONE_INDIV24 = (4 * PAS24, 8 * CASE24 + 7 * ECART24)                   # colonnes 4 à 11 : 328 du bloc, 640 de large
# la boîte « zone », en points : depuis le bloc (sans le ballon) et depuis la tuile (avec le ballon)
TAILLE_ZONE24 = {"width": ZONE_INDIV24[1], "height": BLOC24[1]}                                    # 640 × 476
ZONE_BLOC24 = {"position": "absolute", "left": ZONE_INDIV24[0], "top": 0, **TAILLE_ZONE24}         # 328, 0
ZONE_TUILE24 = {"position": "absolute", "left": ZONE_INDIV24[0] - TUILE24[2], "top": -TUILE24[3],
                **TAILLE_ZONE24}                                                                   # -492, -410
assert ZONE_INDIV24[0] + ZONE_INDIV24[1] == TUILE24[2] + TUILE24[0] and BLOC24[1] == TUILE24[3] + TUILE24[1]
# ce que la vue déborde de la zone (marges, les mêmes des deux côtés) : en 1080p, la vue sans le ballon garde la place
# de la v50 (haut et bas au point près, gauche et droite à 0,4 px près ; la v50 la posait à 105,9 % du bloc)
DEBORD_INDIV24 = {"margin-left": -1, "margin-top": -5, "margin-right": -3, "margin-bottom": -2}
# v32 (test 2 vu en jeu : plus rien devant, mais le cadre dépassait de 10 px à gauche et 15 px en haut ; remesuré au
# pixel sur ses captures : la tuile, bords compris, fait 169 × 76 px, et les tuiles 730 × 543, de x 783 à 1512 et de
# y 355 à 897) ; v31 : 166,5 × 72,75 estimés par la grille
# v32 (TEST 3) : des boutons d'essai qui ÉCRIVENT une consigne individuelle. Le jeu règle ces consignes par une liste à
# choix (SIRadioGroup sur tactic.SelectedPlayerInstruction, PlayerInstructionOptionsBlock) ; pour un bouton, on prend
# l'événement « écrire une valeur » de FM (OppositionInstructionsPersonalisedInstructionsToggleCell : il écrit
# const.True dans Tactic.OppositionPlayerPersonalisedInstructionsUsed) : ici, une variable (le code de l'option) dans
# tactic.SelectedPlayerInstruction, le groupe donné par « playerinstructiongroupid ». Groupes et codes : la table
# PlayerInstructionEntry (ui-staticdataentries) : 17 groupes, 0 = l'option standard
SOURCE_ECRIRE24 = "OppositionInstructionsPersonalisedInstructionsToggleCell"   # son bouton porte l'événement
CHEMIN_CONSIGNE_INDIV24 = "tactic.SelectedPlayerInstruction"
# v33 (test 3 vu en jeu par Kinito : les boutons écrivent la consigne, la tuile de FM change avec) : LA VRAIE VUE
# FM24, sur un seul écran (ses choix du 04/11 : avec et sans le ballon ensemble, le bloc de gauche de FM 27 gardé, un
# bouton FM 27 / FM24 retenu par le jeu ; l'allure de sa capture de FM24 : fond gris, titres bleu-vert, boutons
# encadrés). La fiche de la fenêtre (PlayerInstructionsCard) déclare le choix (V_INDIV24, persistant) dans son
# BindingSetter #OptionalsDefaulter, qui tient déjà l'onglet ; les deux blocs qui portent la vue l'attendent (comme
# kinitovue en v20). Sans le ballon, la vue part du bloc de gauche ; avec le ballon, de la dernière tuile créée (v31).
# Chaque consigne : son nom (données du jeu), ses options autres que « Normal », en boutons : choisie = vert (un clic
# remet « Normal », comme FM24), une autre choisie = rouge (un clic la remplace), sinon gris clair ; verrouillée par le
# rôle (tactic.PlayerInstructionGroupIsLocked, le cadenas de FM 27) : voilée, sans clic
CARTE_INDIV24 = "PlayerInstructionsCard"   # la fiche de la fenêtre (son BindingSetter tient l'onglet ouvert)
SETTER_CARTE24 = "OptionalsDefaulter"
V_INDIV24 = "kinitoindiv24"   # 0 : les tuiles de FM 27, 1 : la vue FM24
# FM 27 à la toute première ouverture, puis le dernier choix ; v48 : la première ouverture = l'option
# OPTION_ARRIVEE_INDIV (0 FM 27, 1 FM24), sa valeur dans le nom de la clé
VALEUR_INDIV24 = f"Int|{1 if ARRIVEE_INDIV24 == 'fm24' else 0}|{persistant(f'indiv-fm24-{ARRIVEE_INDIV24}')}"
ATTENDU_INDIV24 = "teamselectionindex"   # le paramètre attendu de FM recopié pour V_INDIV24 dans les deux blocs
CHEMIN_NOM_OPTION24 = "data.TacticPlayerInstructionOption.Name"   # avec « playerinstructionoptionid » (la tuile de FM)
CHEMIN_NOM_GROUPE24 = "data.TacticPlayerInstructionGroup.Name"    # avec « playerinstructiongroupid »
CHEMIN_VERROU24 = "tactic.PlayerInstructionGroupIsLocked"
# v34 (v33 vue en jeu par Kinito : « il me faut vraiment des schémas et tout comme sur le 24 » ; ses choix : tout
# reste dans la fenêtre, les consignes de FM 27 que FM24 n'avait pas vont dans les schémas, le bouton FM 27 / FM24 dans
# la barre des onglets) : les schémas de FM24, relevés sur ses captures (la fenêtre d'un milieu offensif, capture 85) :
# l'éventail « l'équipe a le ballon » (un point rouge au centre, des secteurs pleins ; « Prenez les espaces » en bouton
# dessous, comme FM24), le camembert « le joueur a le ballon » (« Ralentissez le rythme » en demi-disque dessous = « Gardez
# la balle » de FM 27), les curseurs à trois crans (pressing, passes), la grille « Centrer vers ». Les secteurs sont des
# quarts de disque (un coin arrondi), tournés autour du centre : exacts sans découpe. Cinq états, ceux de la légende de
# FM24 : sélectionné (vert), fait partie du rôle (vert clair : verrouillée par le rôle et choisie), incompatible (rouge :
# une autre option choisie), indisponible (verrouillée), sinon gris
# v36 (v35 vue en jeu par Kinito, 7 captures : tout marche, bouton, schémas, clics, états ; ses demandes) : le bouton
# FM 27 / FM24 à droite de « Sélectionné actuellement » ; le fond de FM 27 ; la vue qui couvre aussi le haut des
# tuiles ; titres courts (ses mots) et centrés, en-têtes « Avec ballon (adversaire / équipe / joueur) » ; jauges pleines
# (pressing, passes : tout est allumé jusqu'au cran choisi) ; flèches sur les secteurs choisis (FM24) ; grilles
# propres ; « Attaquer la surface » en haut de sa colonne (côté puis profondeur), puis courses et positionnement,
# puis mouvements ; « Ligne de but » au-dessus de « En profondeur » ; les options impossibles au poste / rôle grisées
# (le drapeau « Disabled » de chaque option dans la liste de la consigne, celle de la fenêtre de FM 27). Les secteurs
# sont maintenant EXACTS : le jeu limite l'arrondi d'un coin à la moitié du plus petit côté (les quarts de disque de
# la v34 sortaient en carrés arrondis) ; chaque disque est peint par couches (un cercle entier, puis une moitié ou des
# quarts en rectangles, ou des carrés tournés de 45° dont la pointe est au centre), et un anneau de la couleur du fond
# cache tout ce qui dépasse du cercle. Les mots sont ceux du skin (sa langue), plus ceux des données du jeu
DISPOSITION24 = [   # colonnes : (en-tête (français, anglais), avec le ballon, sous-colonnes : [éléments])
    (("SANS BALLON (ÉQUIPE)", "TEAM OUT OF POSSESSION"), False, [[   # v38 (Kinito) ; v36-v37 : avec ballon (adversaire)
        {"type": "jauge", "g": 11, "ordre": (30, 0, 29), "titre": ("PRESSING", "PRESSING"),
         "bouts": (("Moins", "Less"), ("Plus", "More"))},
        {"type": "boutons", "g": 12, "options": [(33, ("De plus près", "Tighter"))], "titre": ("MARQUAGE", "MARKING")},
        {"type": "boutons", "g": 13, "options": [(31, ("Plus durement", "Harder")), (32, ("Moins durement", "Ease off"))],
         "titre": ("TACLES", "TACKLING")},
        {"type": "boutons", "g": 14, "options": [(34, ("Individuel", "Man")), (35, ("De zone", "Zonal"))],
         "titre": ("TYPE DE MARQUAGE", "MARKING TYPE")}]]),   # v38 : l'un sous l'autre
    (("AVEC BALLON (ÉQUIPE)", "TEAM IN POSSESSION"), True, [[
        {"type": "titre", "mots": ("ATTAQUER LA SURFACE", "ATTACKING THE BOX")},
        {"type": "grille", "g": 15, "sous": ("Côté", "Side"), "decor": "but", "marge": 0, "hauteurs": (46, 46),
         "taille": 12,   # v41 (Kinito : « augmenter ces boutons, presque un carré ») ; v36-v40 : 30, 30, mots de 10
         "rangs": [[(39, ("1er poteau", "Near post")), (40, ("2e poteau", "Far post"))],
                   [(37, ("Gauche", "Left")), (36, ("Centre", "Centre")), (38, ("Droite", "Right"))]]},
        {"type": "boutons", "g": 16, "sous": ("Profondeur", "Depth"), "marge": 4,   # v38 : l'un sous l'autre
         "options": [(41, ("Attaquer la ligne", "Attack the line")), (42, ("Arriver en retard", "Arrive late"))]},
        {"type": "disque", "titre": ("COURSES ET POSITION", "RUNS AND POSITION"),
         "secteurs": [(0, 26, "disque", 270, ("Dans l'axe", "Narrower"), (-0.62, 0, 0.78)),
                      (0, 25, "moitie-droite", 90, ("Excentré", "Wider"), (0.62, 0, 0.78)),
                      (3, 22, "haut", 0, ("Plus de courses", "More runs"), (0, -0.68, 1.1)),
                      (3, 23, "bas", 180, ("Moins de courses", "Fewer runs"), (0, 0.68, 1.1))]},
        {"type": "boutons", "g": 0, "options": [(27, ("Prenez les espaces", "Move into channels"))], "marge": 4}]]),
    (("AVEC BALLON (JOUEUR)", "PLAYER IN POSSESSION"), True, [[
        {"type": "disque", "titre": ("DIRECTION", "DIRECTION"),
         "secteurs": [(5, 17, "disque", None, ("Conserver le ballon", "Hold up ball"), (0, 0.5, 1.5)),
                      (1, 16, "quart-hg", 315, ("Repiquer dans l'axe", "Cut inside"), (-0.44, -0.36, 0.72)),
                      (1, 15, "quart-hd", 45, ("Prendre le couloir", "Run wide"), (0.44, -0.36, 0.72))]},
        {"type": "boutons", "g": 4, "options": [(24, ("Décrochez plus souvent", "Roam from position"))],
         "titre": ("MOUVEMENTS", "MOVEMENT")},   # v38 (Kinito) : sous la direction ; v36-v37 : colonne de l'équipe
        {"type": "jauge", "g": 7, "ordre": (1, 0, 2), "titre": ("PASSES", "PASSING"),
         "bouts": (("Courtes", "Shorter"), ("Directes", "More direct")),
         "milieu": ("Normales", "Normal")},   # v42 (Kinito) : « les passes », au féminin pluriel
        {"type": "boutons", "g": 10, "options": [(8, ("Ligne de but", "Byline")), (7, ("En profondeur", "Early"))],
         "titre": ("CENTRER DE", "CROSS FROM")}], [
        {"type": "boutons", "g": 2, "options": [(13, ("Dribblez plus", "Dribble more")),
                                                (14, ("Dribblez moins", "Dribble less"))],
         "titre": ("BALLE AU PIED", "DRIBBLING")},
        {"type": "boutons", "g": 6, "options": [(18, ("Plus souvent", "Shoot more")), (19, ("Moins souvent", "Shoot less"))],
         "titre": ("TIRS", "SHOOTING")},
        {"type": "boutons", "g": 8, "options": [(3, ("Plus de risques", "More risky")), (4, ("Moins de risques", "Less risky"))],
         "titre": ("RISQUE DES PASSES", "PASSING RISK")},
        {"type": "grille", "g": 9, "titre": ("CENTRER VERS", "CROSS TARGET"), "decor": "arc", "hauteurs": (38, 32),
         "rangs": [[(10, ("2e poteau", "Far post")), (11, ("Centre", "Centre")), (9, ("1er poteau", "Near post"))],
                   [(12, ("Attaquant pivot", "Target man"))]]}]])]
#   secteurs : (groupe, code, forme, direction de la flèche (degrés, 0 = vers le haut ; None : pas de flèche), mots,
#   place du nom (décalage x, y du centre et largeur, en rayons)) ; peints dans cet ordre (le premier : le cercle)
CI24 = {   # v36 : les fonds de FM 27 (relevés sur ses captures : tuiles #1d2129, bloc de gauche #111317)
    "fond": _hexa("#1d2129"), "bouton": _hexa("#151920"), "entete": _hexa("#a09f96"), "titre": _hexa("#6ab0c1"),
    "filet": _hexa("#2e333d"), "texte": _hexa("#ffffff"), "schema": _hexa("#111317"), "ligne-schema": _hexa("#3a3f49"),
    "point": _hexa("#ff0201"), "but": _hexa("#d9d9d9"), "fleche": _hexa("#ffffff", 0.92),
    "voile": _hexa("#151920", 0.72), "voile-case": _hexa("#262a31", 0.72)}
LIGNE24 = {"choisi": _hexa("#27984b"), "contraire": _hexa("#e06362"), "neutre": _hexa("#c8c8c8"),
           "role": _hexa("#7faf02"), "indispo": _hexa("#714946")}   # bord des boutons (FM24)
PLEIN24 = {"choisi": _hexa("#0fa643"), "contraire": _hexa("#ff5455"), "neutre": _hexa("#4a505b"),
           "role": _hexa("#7faf02"), "indispo": _hexa("#262a31")}   # secteurs, cases (FM24 ; gris et sombre de FM 27)
JAUGE24 = {"allume": _hexa("#0fa643"), "eteint": _hexa("#3a3f4a"), "role": _hexa("#7faf02"),
           "eteint-bloque": _hexa("#262a31")}
#   v43 (Kinito : « pour les consignes indiv, NE TOUCHE PAS LES COULEURS », « seulement les consignes équipe
#   FM24 ») : la palette « sarcelle » ne vaut que pour la vue FM24 des consignes d'équipe ; ici, celles de FM24 restent
H_BOUTON_INDIV24, H_JAUGE24, H_CASE24 = 24, 12, 30   # px
MOT_NORMAL24 = ("Normal", "Normal")   # v41 : le cran du milieu des jauges (v42 : « milieu » d'une jauge le remplace)
TAILLE_BOUTON24, TAILLE_SECTEUR24, TAILLE_CASE24, TAILLE_BOUT24 = 12, 10, 10, 12   # px (v39 : bouts 12)
SANS_MARGE24 = {f"{k}-{c}": 0 for k in ("margin", "padding") for c in ("top", "bottom", "left", "right")}
#   v39 : les boutons de FM ont des marges par défaut (2 px entre les crans de la jauge sur sa capture) : annulées
# v38 (Kinito : « faire entrer de manière harmonieuse le texte dans les cases, dans toutes les tailles ») : les mots
# des cases (boutons, secteurs, grilles, bouts des jauges) gardent la taille du Normal en Grand et Plus grand (le jeu
# agrandit aussi les px : leur police est réduite d'autant, une variante par taille, comme v28) ; les infobulles
# (survol) donnent l'explication de l'option, celle du jeu (CHEMIN_DESC24)
CHEMIN_DESC24 = "data.TacticPlayerInstructionOption.Description"   # l'infobulle des tuiles de FM 27
CHEMIN_DESC_EQUIPE24 = "data.TacticTeamInstructionOption.DescriptionLong"   # v38 : consignes d'équipe (12 écrans)
TAILLE_ENTETE24, TAILLE_TITRE_INDIV24, TAILLE_SOUS24 = 10, 11, 12   # px (v37 ; v39 : sous-titres 12)
# v37 (v36 vue en jeu en « Plus grand » : la colonne du milieu ne tenait pas ; le jeu agrandit aussi les tailles
# écrites en px) : en-têtes et titres plus petits (sur une ligne), la colonne du milieu plus large, écarts resserrés
POIDS_COLONNES24 = (0.85, 1.15, 2.0)   # largeurs relatives des trois colonnes (v34-v36 : 1, 1, 2)
ECART_OPTION_INDIV24, ECART_GROUPE_INDIV24 = 3, 8
R_DISQUE24, MASQUE24 = 74, 0.46   # px (v37, Kinito : « agrandir un peu le rond » ; v36 : 50) ; l'anneau qui cache ce
#                                   qui dépasse du cercle (en rayons : les coins des rectangles et les pointes des
#                                   carrés tournés vont jusqu'à 1,42 rayon) ; v37 : de la couleur du fond de la vue
#                                   (Kinito : « pas de fond noir derrière, juste le rond »)
DEBORD24 = {"margin-top": -6, "margin-left": -3, "margin-right": -3, "margin-bottom": -3}   # v36 : sur ses
#                                   captures, le haut des tuiles dépassait de 5 px au-dessus de la vue
TEXTE_FM27_INDIV24 = "FM 27"   # le bouton de gauche (TEXTE_FM24 à droite)
# v41 (v40 vue : Kinito : « ajouter un FM27 plutôt que d'en mettre qu'un en switch ; mettre en évidence celui
# sélectionné ») : les deux boutons côte à côte ; celui qui n'est pas choisi garde l'allure grise d'« Annuler sél. »
# (sa classe, dans la feuille de style commune de FM : le bouton recopié en v40 n'avait pas son fond, qui vient du bouton
# « split » de FM), celui qui est choisi prend celle du bouton choisi de « Attribuer à : Position | Joueur » (le violet
# de FM 27). Classes de AlwaysAppliedStyleSheet (relues le 05/11)
CLASSE_BASCULE_GRIS24 = "tactics-speak-to-combo-left"
CLASSE_BASCULE_CHOISI24 = "buttons-segmented-button-row-active-default-placement-{}"   # leading / trailing
H_BASCULE24, L_BASCULE24 = 32, 60   # px (la hauteur de la classe d'« Annuler sél. »)
HAUT_BASCULE24 = -9   # px : le bouton FM 27 / FM24, centré sur la ligne de « Sélectionné actuellement »
LEGENDE_INDIV24 = [("choisi", ("Sélectionné", "Selected")), ("role", ("Fait partie du rôle", "Part Of Role")),
                   ("contraire", ("Incompatible", "Incompatible")), ("indispo", ("Indisponible", "Unavailable"))]
EXTRA24 = "TacticsPlayerInstructionsExtraButtons"   # v40 : la ligne du haut (« Consigne indisponible »… « Annuler sél. »)
SOURCE_ANNULER24 = "TacticsPlayerInstructionsUndoButton"   # v40 : « Annuler sél. » (son bouton gris est recopié)
NOM_EXTRA = f"{NOM_INDIV}-annuler"
CHEMIN_OPTIONS24 = "tactic.PlayerInstructionGroupOptions"   # la liste de la consigne (fenêtre de FM 27), « Disabled »
SOURCE_ELEMENT24 = ("TransferBlockMainFrame", "firstItem")   # BindListItemUsingIndexToDestination (comme 26.x vacances)
ATTENDU_MODELE = "selectedphase"   # le paramètre attendu de FM recopié pour les nôtres (une variable entière de l'écran)
# v23 (Kinito) : à la TOUTE première arrivée, les Tuiles ; ensuite, la vue choisie (clé persistante). v48 : la vue de
# la première arrivée = l'option OPTION_ARRIVEE (0 tuiles de FM, 1 terrain, VUE_FM24), sa valeur dans le nom de la clé
VUE_DEPART24 = {"tuiles": 0, "terrain": 1, "fm24": VUE_FM24}[ARRIVEE24]
VARIABLES_ECRAN = [(base.VARIABLE, f"Int|{VUE_DEPART24}|{persistant(f'vue-{ARRIVEE24}')}"),
                   (V_PHASE24, f"Int|0|{persistant('phase-fm24')}")]


class _Palette:
    """le temps de construire une partie de la vue FM24 : des couleurs (COUL) et des coins (cadre_css) de 26.13
    remplacés, puis remis tels quels (v21 : FM24 en général, et les zones des terrains : jointives, coins carrés,
    couleurs à 85 % qui laissent voir les lignes du terrain)"""
    def __init__(self, couleurs, rayons):
        self.couleurs, self.rayons = couleurs, rayons

    def __enter__(self):
        self.avant = dict(base.COUL)
        self.cadre = base.cadre_css
        base.COUL.update(self.couleurs)
        cadre, rayons = self.cadre, self.rayons

        def cadre_fm24(largeur, couleur, rayon=None):
            if isinstance(rayon, (int, float)) and not isinstance(rayon, bool):
                rayon = rayons.get(rayon, rayon)
            return cadre(largeur, couleur, rayon)
        base.cadre_css = cadre_fm24
        return self

    def __exit__(self, *exc):
        base.COUL.clear()
        base.COUL.update(self.avant)
        base.cadre_css = self.cadre
        return False


def _PaletteFM24():
    return _Palette(COUL_FM24, RAYONS_FM24)


def _PaletteZones():
    return _Palette(COUL_ZONES24, {8: 0, 9: 0, 10: 0, 11: 0})


def mots24(fab, parent, nom, mots, classe=CLASSE_TITRE24, css=None, conteneur=None, couleur=None):
    """nos mots (FM n'a pas ces textes ici) : (français, anglais), dans la langue du skin ; v97 : un texte simple dans
    une boîte (jusqu'en v96 : une bascule de FM, français / anglais / langue du skin), traduit dans la langue du jeu par
    traduire24 (le conteneur de langue de sa vue). Ne prend pas de clic"""
    fr, en = mots
    boite = fab.boite(parent, nom, css={"flex-shrink": 0} if conteneur is None else conteneur)
    fab.traverse(boite)
    fab.n += 1
    r = fab.texte_fixe(boite, f"{nom}-{fab.n}", langue.texte(fr, en), classe=classe,
                       css={"-unity-text-align": "middle-center", "white-space": "normal",
                            **({"color": couleur} if couleur else {}), **(css or {})})
    fab.traverse(r)
    return boite


def titre24(fab, env, nom, css=None):
    """le nom de la consigne (données du jeu, comme Terrain), en capitales, gras, blanc (FM24)"""
    r = fab.titre(env, nom, css={"margin-bottom": 1, "flex-shrink": 0, **(css or {})})
    fab.t.elem(r)["m_Classes"] = [CLASSE_TITRE24, "global-text-primary"]
    return r


def places24(fab, n):
    if n in ORDRE24:
        return ORDRE24[n]
    d = DEFAUTS.get(n)
    places = tuple(p for p in range(len(fab.src.options[n])) if n in SANS_RETOUR or p != d)
    return tuple(reversed(places)) if n in INVERSE24 else places


def liste24(fab, col, n, nom, marge=ECART_CONSIGNE24, titre=True, rangee=False, compense=False):
    """une consigne en boutons écrits l'un sous l'autre (FM24), ou côte à côte (rangee) : ses options autres que
    l'option neutre ; un clic choisit, un 2e clic remet l'option neutre (bouton_b) ; une autre option choisie : rouge
    (« indisponible »)"""
    e = fab.enveloppe(col, n, f"fm24-{nom}", css={"flex-direction": "column", "flex-shrink": 0, "margin-top": marge})
    if titre:
        titre24(fab, e, f"fm24-{nom}", css={"margin-bottom": 4})
    par = fab.boite(e, f"fm24-{nom}-rangee", css={"flex-direction": "row", "flex-shrink": 0}) if rangee else e
    for i, p in enumerate(places24(fab, n)):
        css = {"height": H_BOUTON24, "flex-shrink": 0,
               **({"flex-grow": 1, "flex-basis": 0, "margin-left": ECART_BOUTON24 if i else 0} if rangee else
                  {"margin-top": ECART_BOUTON24 if i else 0})}
        if compense:   # v28 : le nom par-dessus, sa police selon la taille du texte de FM (il débordait en Plus grand)
            case = fab.boite(par, f"fm24-{nom}-{p}-case", css=css)
            bouton_b(fab, case, n, p, texte=False, icone=False, assombrir=True, css={"flex-grow": 1})
            mot_zone(fab, case, f"fm24-{nom}-{p}-mot", None, classe=CLASSE_TEXTE24, taille=TAILLE_TEXTE24,
                     option=(n, p))
            continue
        # v83 : « Ralentisser le rythme » (faute de la traduction française de FM 27) reste tel quel : Kinito l'a signalée
        # à SI, nos boutons écrivent le texte de FM et suivront sa correction
        bouton_b(fab, par, n, p, texte=True, icone=False, classe=CLASSE_TEXTE24, assombrir=True, css=css)
    return e


def curseur24(fab, col, n, nom, marge=ECART_CONSIGNE24):
    """une consigne en crans, comme le curseur de FM24 : son nom, l'option en cours écrite dessous, puis son icône
    (v21) et une piste fine, allumée (plus épaisse) jusqu'au cran choisi, qu'un trait termine ; le réglage par défaut
    marqué ▼ au-dessus et ▲ au-dessous de la piste (v21 : les flèches de tri de FM 27) ; un bouton de FM invisible par
    cran, par-dessus (un clic sur la piste choisit le cran)"""
    t = fab.t
    m = len(fab.src.options[n])
    e = fab.enveloppe(col, n, f"fm24-{nom}", css={"flex-direction": "column", "flex-shrink": 0, "margin-top": marge})
    titre24(fab, e, f"fm24-{nom}")

    def valeur(par, k):
        var, r = fab.nom_option(par, n, k, petit=False, css={"flex-shrink": 0})
        t.elem(r)["m_Classes"] = [CLASSE_TEXTE24, "global-text-primary"]
    fab.selon(e, n, valeur, f"fm24-{nom}-valeur", css={"flex-shrink": 0})
    rangee = fab.boite(e, f"fm24-{nom}-rangee", css={"flex-direction": "row", "align-items": "center",
                                                     "height": H_PISTE24, "margin-top": 2, "flex-shrink": 0})
    fab.traverse(rangee)
    if n in ICONES_CURSEURS24:
        fab.traverse(fab.boite(rangee, f"fm24-{nom}-icone", classes=[ICONES_CURSEURS24[n]], css={
            "width": TAILLE_ICONE24, "height": TAILLE_ICONE24, "flex-shrink": 0, "margin-right": 8}))
    piste = fab.boite(rangee, f"fm24-{nom}-piste", css={"flex-grow": 1, "height": H_PISTE24})
    mi = H_PISTE24 / 2

    def x(p):
        return pc(100.0 * p / (m - 1))
    fab.traverse(fab.boite(piste, f"fm24-{nom}-vide", css={"position": "absolute", "left": 0, "right": 0,
                                                           "top": mi - 2, "height": 4,
                                                           "background-color": C24["vide"]}))
    d = DEFAUTS.get(n)
    if d is not None:   # FM24 : ▼ au-dessus et ▲ au-dessous du réglage par défaut
        for j, (classe, haut) in enumerate(((REPERE_HAUT24, mi - 7 - TAILLE_REPERE24),
                                            (REPERE_BAS24, mi + 7))):
            fab.traverse(fab.boite(piste, f"fm24-{nom}-repere-{j}", classes=[classe], css={
                "position": "absolute", "left": x(d), "top": haut, "width": TAILLE_REPERE24,
                "height": TAILLE_REPERE24, "margin-left": -TAILLE_REPERE24 / 2}))

    def dessin(par, k):
        r = fab.boite(par, f"fm24-{nom}-dessin-{k}", css=PLEIN)
        fab.traverse(r)
        if k:
            fab.traverse(fab.boite(r, f"fm24-{nom}-plein-{k}", css={
                "position": "absolute", "left": 0, "top": mi - 3, "height": 6, "width": x(k),
                "background-color": C24["piste"]}))
        fab.traverse(fab.boite(r, f"fm24-{nom}-trait-{k}", css={
            "position": "absolute", "left": x(k), "top": mi - 7, "height": 14, "width": 4,
            "margin-left": 0 if k == 0 else (-4 if k == m - 1 else -2), "background-color": C24["piste"]}))
    sel = fab.selon(piste, n, dessin, f"fm24-{nom}-dessin", css=PLEIN)
    for r in t.walk(sel):
        fab.traverse(r)
    clic = fab.boite(piste, f"fm24-{nom}-clic", css={**PLEIN, "flex-direction": "row"})
    fab.traverse(clic)
    for p in range(m):   # sans infobulle (v13 : sur une bande de clic, elle gênait les clics suivants)
        fab.option(clic, n, p, nu=True, texte=False, bulle=False,
                   css={"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0})
    return e


def colonne24(fab, panneau, nom, part, premiere=False):
    return fab.boite(panneau, f"fm24-{nom}", css={
        "flex-grow": part, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "flex-direction": "column",
        "padding-left": 12, "padding-right": 12, "padding-top": 10, "overflow": "hidden",
        **({} if premiere else {"border-left-width": 1, "border-left-color": C24["filet"]})})


def entete24(fab, col, nom, mots, marge=0):
    """le titre d'un groupe de consignes (FM24 : « CONSTRUCTION DU JEU »…), nos mots"""
    mots24(fab, col, f"fm24-{nom}-entete", mots, css={"margin-bottom": 4, "margin-top": marge})


def terrain24(fab, col, nom, traits, rapport=RAPPORT_ZONES24, marge=8, largeur=100, reduit=None):
    """v20 : un terrain de FM24 (lignes blanches sur le vert du panneau, sans bandes), à la largeur de sa colonne ;
    rend son champ (les zones s'y posent en %). v27 : reduit = [(taille du texte, marge px)] : pour chacune, deux
    SIStyleSetter de FM (classe_selon24 sur settings.TextScaling) posent des classes de marge de FM de chaque côté :
    le terrain rétrécit, donc raccourcit (sa hauteur suit sa largeur)"""
    t = fab.t
    par = col
    for valeur, m in reduit or []:
        for cote in ("left", "right"):
            par = classe_selon24(fab, par, f"fm24-{nom}-reduit-{valeur}-{cote}", "settings.TextScaling", valeur,
                                 f"margin-{cote}-{m}")
            t.styles.style(t, par, {"flex-grow": 0, "flex-shrink": 0})
    if reduit:
        par = fab.boite(par, f"fm24-{nom}-reduit", css={"flex-shrink": 0, "flex-direction": "column"})
        fab.traverse(par)
    place = fab.boite(par, f"fm24-{nom}-place", css={"width": pc(largeur), "align-self": "center", "flex-shrink": 0,
                                                     "margin-top": marge})
    haut = fab.boite(place, f"fm24-{nom}-haut", css={"height": 0, "padding-bottom": pc(100 * rapport),
                                                     "flex-shrink": 0})
    cadre = fab.boite(haut, f"fm24-{nom}-cadre", css={**PLEIN, "flex-direction": "column", "overflow": "hidden",
                                                      **base.cadre_css(1, C24["ligne"])})
    return champ_terrain(fab, cadre, f"fm24-{nom}", traits)


def case24(fab, env, nom, x, y, w, h):
    """v21 : l'emplacement d'une zone d'un terrain ; v22 (Kinito : « pas de place entre les boutons ») : sans marge,
    les zones se touchent (le filet de 1 px de FM24 est le bord de leur bouton)"""
    return fab.boite(env, nom, css={"position": "absolute", "left": pc(x), "top": pc(y), "width": pc(w),
                                    "height": pc(h), "flex-direction": "row"})


def selon_taille24(fab, par, nom, faire):
    """v28 : faire(parent, facteur) pose UN élément, sur toute sa case ; facteur = 1 en Petit et en Normal, 100 / taille
    en Grand et Plus grand (TAILLES_TEXTE24) : le calcul « option choisie ? » de FM recopié sur settings.TextScaling,
    puis un interrupteur de FM par taille"""
    t = fab.t
    tailles = list(TAILLES_TEXTE24)
    sel = fab._comparer(par, nom, [(f"kinitotaille{v}", v) for v in tailles], "settings.TextScaling")
    t.styles.style(t, sel, PLEIN)
    fab.traverse(sel)

    def chaine(p, k):
        if k == len(tailles):
            faire(p, 1.0)
            return
        sw = fab.interrupteur(p, f"{nom}-si-{tailles[k]}", f"kinitotaille{tailles[k]}", css=PLEIN)
        fab.traverse(sw)
        chaine(sw, k + 1)
        faire(sw, TAILLES_TEXTE24[tailles[k]])
    chaine(sel, 0)
    return sel


def mot_zone(fab, case, nom, mots, classe=CLASSE_PETIT24, taille=TEXTE_ZONE24, option=None):
    """v21 : la phrase de FM24 écrite dans une zone (nos mots, français / anglais), par-dessus son bouton ; v22 :
    centrée au milieu de la zone, en hauteur aussi (le texte prend toute la place et se centre dedans). v28 : ou le nom
    de l'option (n, place) des données du jeu (option) ; et une variante par taille du texte de FM (selon_taille24) :
    en Grand et Plus grand, la police réduite d'autant (le texte garde la taille du Normal, plus de mot coupé)"""
    t = fab.t

    def faire(par, facteur):
        px = round(taille * facteur, 2)
        n2 = f"{nom}-{round(facteur * 100)}"
        if option is None:
            mots24(fab, par, n2, mots, classe=classe,
                   css={"white-space": "normal", "flex-grow": 1, "-unity-text-align": "middle-center",
                        "font-size": px},
                   conteneur={**PLEIN, "padding-left": 4, "padding-right": 4})
            return
        b = fab.boite(par, n2, css={**PLEIN, "padding-left": 4, "padding-right": 4})
        fab.traverse(b)
        var, txt = fab.nom_option(b, option[0], option[1], css={"flex-grow": 1})
        fab.traverse(var)
        fab.traverse(txt)
        t.elem(txt)["m_Classes"] = [classe, "global-text-primary"]
        t.styles.style(t, txt, {"flex-grow": 1, "white-space": "normal", "-unity-text-align": "middle-center",
                                "font-size": px})
    selon_taille24(fab, case, f"{nom}-taille", faire)


ZONE_KW = dict(icone=False, assombrir=True, css={"flex-grow": 1})


def zone24(fab, env, n, p, x, y, w, h, nom, mots=None):
    """une zone d'un terrain (FM24) : le bouton de l'option p de la consigne n (bouton_b : 2e clic = neutre), écrit
    du nom de l'option (données du jeu) ou, v21, d'une phrase de FM24 (mots)"""
    case = case24(fab, env, nom, x, y, w, h)
    bouton_b(fab, case, n, p, texte=False, **ZONE_KW)
    if mots is None:   # v28 : le nom de l'option (données du jeu) par-dessus, comme nos mots (selon la taille du texte)
        mot_zone(fab, case, f"{nom}-mot", None, option=(n, p))
    else:
        mot_zone(fab, case, f"{nom}-mot", mots)
    return case


def course24(fab, case, n, autre, gauche):
    """une zone des dédoublements : la case de 26.13 (base.course : intérieur et extérieur du même côté s'excluent, un
    clic sur un côté pris par l'autre consigne échange), sans texte (la phrase de FM24 est posée par-dessus)"""
    opts = fab.src.options[n]
    cote_pris = (1, 3) if gauche else (2, 3)
    ajoute = {0: 1, 2: 3} if gauche else {0: 2, 1: 3}
    retire = {1: 0, 3: 2} if gauche else {2: 0, 3: 1}
    montre = 1 if gauche else 2
    kw = dict(texte=False, icone=False, bulle=False, css={"flex-grow": 1})
    fab.n += 1
    nom = f"fm24-course-{fab.n}"

    def selon_soi(par, s_soi):
        if s_soi in cote_pris:
            fab.option(par, n, retire[s_soi], affiche=montre, allume=opts[s_soi][0], **kw)
            return
        garde = fab.retenir(par, "teaminstructionid", "kinitoida", f"{nom}-id-{s_soi}")
        env = fab.enveloppe(garde, autre, f"{nom}-autre-{s_soi}", css={"flex-grow": 1})

        def selon_autre(par2, s_autre):
            cible = ajoute[s_soi]
            if s_autre in cote_pris:   # impossible : rouge ; un clic échange
                fab.option(par2, autre, retire[s_autre], n_vue=n, affiche=montre, allume=opts[cible][0],
                           extra=("kinitoida", cible), force=True, estompe=True, **kw)
            else:
                fab.option(par2, n, cible, n_vue=n, affiche=montre, allume=opts[cible][0], cible="kinitoida",
                           force=True, **kw)
        fab.selon(env, autre, selon_autre, f"{nom}-selon-autre-{s_soi}", css={"flex-grow": 1})
    fab.selon(case, n, selon_soi, f"{nom}-selon", css={"flex-grow": 1})


def place_poste24(poste, lignes=None):
    """v25 : la place (x, y en % du terrain) d'un poste lu (POSTES24) ; lignes : la hauteur de chaque ligne (LIGNES24 :
    celle du terrain ; LIGNES_SANS24 : entre la ligne de pressing et la ligne défensive)"""
    colonne, ligne = POSTES24[poste]
    return COLONNES24[colonne], (lignes or LIGNES24)[ligne]


def joueur24(fab, par, nom, i, avec):
    """v25 : le joueur n° i de la tactique : le BindingSetter de nom_option (recopié vide, comme en v24, vu en jeu) qui
    déclare « teamselectionindex » = i et « inpossession » = avec (poste lu avec ou sans ballon) ; sur tout le terrain"""
    t, src = fab.t, fab.src
    var = t.clone(src.setter, par, src=src.ts)
    recaler_parent(t, var)
    for k in list(t.children(var)):
        t.remove(k)
    t.styles.copy_from(src.ts.styles, t, var)
    fab._nom(var, nom)
    vs = t.sd(var)
    v0 = copy.deepcopy(vs["ValueVariables"][0])
    v0["m_name"], v0["m_scopeValue"]["m_serializedData"] = "teamselectionindex", f"Int|{i}|"
    v1 = copy.deepcopy(v0)
    v1["m_name"], v1["m_scopeValue"]["m_serializedData"] = "inpossession", "Bool|1|" if avec else "Bool|0|"
    vs["ValueVariables"], vs["ValueVariables_UxmlAttributeFlags"] = [v0, v1], 1
    t.elem(var)["m_Classes"], t.elem(var)["m_RuleIndex"] = [], -1
    t.styles.style(t, var, PLEIN)
    fab.traverse(var)
    return var


def selon_poste24(fab, par, nom, postes, faire):
    """v25 : ce qui s'affiche dépend du poste lu du joueur déclaré au-dessus (CHEMIN_POSTE24) : le calcul « option
    choisie ? » de FM recopié (_comparer : kinitot<poste> = poste lu == <poste>), puis un interrupteur de FM par poste,
    chacun sur tout le terrain (selon_valeur les laisse à la taille de leur contenu : un pion posé en % n'y aurait pas
    sa place) ; faire(parent, poste) pose UN élément ; rien pour un poste hors de la liste (le gardien, un poste vide)"""
    t = fab.t
    sel = fab._comparer(par, nom, [(f"kinitot{v}", v) for v in postes], CHEMIN_POSTE24)
    t.styles.style(t, sel, PLEIN)
    fab.traverse(sel)

    def chaine(p, k):
        if k == len(postes):
            fab.traverse(fab.boite(p, f"{nom}-aucun", css={"width": 0, "height": 0}))
            return
        sw = fab.interrupteur(p, f"{nom}-si-{postes[k]}", f"kinitot{postes[k]}", css=PLEIN)
        fab.traverse(sw)
        chaine(sw, k + 1)       # rang 0 : ce n'est pas ce poste
        faire(sw, postes[k])    # rang 1 : c'est lui
    chaine(sel, 0)
    return sel


def occupation24(fab, par, nom, avec):
    """v26 : sur tout le terrain, « un joueur au centre de la ligne ? » pour chaque ligne de LIGNES_DUO24 : pour chacun
    des 11 joueurs, sa déclaration (joueur24) et le calcul « option choisie ? » de FM (_comparer : kinitoc<l>j<j> =
    poste lu == centre de la ligne l), les uns dans les autres ; puis, dedans, la fonction de FM qui combine des
    booléens (Ou) : kinitocentre<l>. Rend l'élément où poser ce qui s'en sert"""
    t = fab.t
    cur = par
    for j in range(NB_JOUEURS24):
        sj = joueur24(fab, cur, f"{nom}-j{j}", j, avec)
        cur = fab._comparer(sj, f"{nom}-j{j}-centres", [(f"kinitoc{l}j{j}", c) for l, c in LIGNES_DUO24.items()],
                            CHEMIN_POSTE24)
        t.styles.style(t, cur, PLEIN)
        fab.traverse(cur)
    ou = fab._comparer(cur, f"{nom}-ou", [(f"kinitocentre{l}", 0) for l in LIGNES_DUO24], CHEMIN_POSTE24)
    fonctions = t.sd(ou)["BindFunction"]
    if len(fonctions) != len(LIGNES_DUO24) or not all("m_target" in f for f in fonctions):
        raise ValueError("calcul « un joueur au centre ? » : forme inattendue")
    for f, l in zip(fonctions, LIGNES_DUO24):
        noms = [f"kinitoc{l}j{j}".encode() for j in range(NB_JOUEURS24)]
        liste = bytes([len(noms)]) + b"".join(bytes([1, len(v)]) + v + b"\x00" for v in noms)
        dest = f"kinitocentre{l}".encode()
        f["m_target"]["m_guid"] = GUID_OU24
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(
            [[T_LISTE24, liste], [T_LOGIQUE24, struct.pack("<i", OU24)], [T_CHEMIN24, bytes([1, len(dest)]) + dest]])
    t.styles.style(t, ou, PLEIN)
    fab.traverse(ou)
    return ou


def selon_duo24(fab, par, nom, poste, poser):
    """v26 : poser(parent, x, nom) pose UN élément à l'abscisse x du poste ; un central décalé d'une ligne de
    LIGNES_DUO24 : un interrupteur de FM sur kinitocentre<ligne> (occupation24, au-dessus) : rang 0, personne au
    centre : rapproché de l'axe (COLONNES_DUO24) ; rang 1 : sa place de toujours"""
    colonne, ligne = POSTES24[poste]
    if ligne not in LIGNES_DUO24 or colonne not in COLONNES_DUO24:
        poser(par, COLONNES24[colonne], nom)
        return
    sw = fab.interrupteur(par, f"{nom}-duo", f"kinitocentre{ligne}", css=PLEIN)
    fab.traverse(sw)
    poser(sw, COLONNES_DUO24[colonne], f"{nom}-deux")
    poser(sw, COLONNES24[colonne], f"{nom}-trois")


def pions_postes24(fab, par, nom, lignes=None, avec=True, taille=TAILLE_PION24, part=None):
    """v25 : les pions des joueurs de champ, chacun à la place de son poste lu (avec ballon, ou sans ballon : le
    terrain des lignes, choix de Kinito, comme FM24) ; le gardien est posé à part, une fois. v26 : deux centraux seuls
    sur leur ligne se rapprochent (occupation24, selon_duo24)"""
    b = fab.boite(par, nom, css=PLEIN)
    fab.traverse(b)
    occ = occupation24(fab, b, f"{nom}-centres", avec)
    for i in range(NB_JOUEURS24):
        j = joueur24(fab, occ, f"{nom}-j{i}", i, avec)

        def faire(p, v, i=i):
            y = (lignes or LIGNES24)[POSTES24[v][1]]
            selon_duo24(fab, p, f"{nom}-j{i}-{v}", v,
                        lambda q, x, n2: pion24(fab, q, n2, x, y, taille=taille, part=part))
        selon_poste24(fab, j, f"{nom}-j{i}-poste", list(POSTES24), faire)
    return b


def fleches_postes24(fab, par, nom, sens, larges=False):
    """v25 : les petites flèches de FM24 de chaque joueur de champ, à la place de son poste lu avec ballon ; larges :
    seulement les joueurs excentrés (EXCENTRE24). v26 : comme les pions, deux centraux seuls se rapprochent"""
    b = fab.boite(par, nom, css=PLEIN)
    fab.traverse(b)
    occ = occupation24(fab, b, f"{nom}-centres", True)
    postes = [v for v in POSTES24 if not (larges and abs(place_poste24(v)[0] - 50) < EXCENTRE24)]
    for i in range(NB_JOUEURS24):
        j = joueur24(fab, occ, f"{nom}-j{i}", i, True)

        def faire(p, v, i=i):
            y = place_poste24(v)[1]

            def poser(q, x, n2):
                f = fab.boite(q, n2, css=PLEIN)
                fab.traverse(f)
                for k, s_ in enumerate(sens):
                    petite_fleche24(fab, f, f"{n2}-{k}", x, y, s_)
            selon_duo24(fab, p, f"{nom}-j{i}-{v}", v, poser)
        selon_poste24(fab, j, f"{nom}-j{i}-poste", postes, faire)
    return b


def pion24(fab, par, nom, x, y, gardien=False, taille=TAILLE_PION24, part=None):
    """v22 : un pion de FM24 (rond de la couleur de l'équipe, le gardien en noir), centré sur (x, y) % du terrain ;
    v26 : taille en px (TAILLE_PION_LARGEUR24 sur le terrain de la largeur) ; v27 : part = sa taille en % de la LARGEUR
    du terrain (proportionnel au terrain) : largeur en %, hauteur nulle et marge intérieure du bas en % (qui se compte
    sur la largeur : un rond), marges de recentrage en % (elles aussi sur la largeur)"""
    fond, bord = (C24["pion-gb"], C24["pion-gb-bord"]) if gardien else (C24["pion"], C24["pion-bord"])
    if part is None:
        taille_css = {"width": taille, "height": taille, "margin-left": -taille / 2, "margin-top": -taille / 2,
                      **cadre_css(1, bord, taille / 2)}
    else:
        taille_css = {"width": pc(part), "height": 0, "padding-bottom": pc(part), "margin-left": pc(-part / 2),
                      "margin-top": pc(-part / 2), **cadre_css(1, bord, pc(50))}
    fab.traverse(fab.boite(par, nom, css={"position": "absolute", "left": pc(x), "top": pc(y),
                                          "background-color": fond, **taille_css}))


def classe_selon24(fab, parent, nom, chemin, valeur, classe):
    """v23 : le SIStyleSetter de FM des boutons segmentés (BindIntComparisonToAOrBUssClass), recopié vide : pose la
    classe de FM <classe> sur son ENFANT quand <chemin> == <valeur>, rien sinon (comme vue_comme_ensemble) ; il
    remplit sa place, en colonne"""
    t, src = fab.t, fab.src
    th = src.th
    modele = th.children(src.segments)[0] if th.children(src.segments) else None
    if modele is None or typ(th, modele) != "SIStyleSetter":
        raise ValueError("réglage d'un bouton segmenté des cartes de chaleur (introuvable)")
    s = t.clone(modele, parent, src=th)
    for k in list(t.children(s)):
        t.remove(k)
    t.styles.copy_from(th.styles, t, s)
    recaler_parent(t, s)
    fab._nom(s, nom)
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    f = t.sd(s)["BindFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != 7 or not bytes(args[0][0]).endswith(b"[SI.Bindable.BindingPath]") \
            or not bytes(args[2][0]).endswith(b"Int32VisualArg") \
            or not all(bytes(args[i][0]).endswith(b"StringVisualArg") for i in (3, 4)):
        raise ValueError("réglage d'un bouton segmenté : arguments inattendus (introuvable)")
    ch = chemin.encode("utf-8")
    args[0][1] = bytes([1, len(ch)]) + ch
    args[2][1] = struct.pack("<i", valeur)
    args[3][1], args[4][1] = _texte_arg(classe), _texte_arg("")
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, s, {"flex-grow": 1, "flex-direction": "column"})
    fab.traverse(s)
    return s


def resserre24(fab, env, nom):
    """v23 : la boîte des pions de la largeur, plus ou moins étroite selon le cran (MARGES_LARGEUR24) : une suite de
    SIStyleSetter de FM (un par côté et par marge), chacun pose une classe de marge de FM (margin-left-16…) sur
    l'élément suivant quand la largeur choisie est la sienne : les marges s'additionnent, les pions sont posés UNE
    fois (sans cela : une fois par cran). Rend la boîte où poser les pions"""
    par = fab.boite(env, f"{nom}-reglages", css=PLEIN)
    fab.traverse(par)
    for i, (k, marge) in enumerate(MARGES_LARGEUR24):
        code = fab.src.options[4][k][0]
        for cote in ("left", "right"):
            par = classe_selon24(fab, par, f"{nom}-{i}-{cote}", CHEMIN_OPTION24, code, f"margin-{cote}-{marge}")
    b = fab.boite(par, nom, css={"flex-grow": 1})
    fab.traverse(b)
    return b


def petite_fleche24(fab, par, nom, x, y, sens):
    """v22 : une petite flèche de FM24 près d'un pion (x, y en % du terrain) : sens = (dx, dy en px, angle en degrés,
    0 = vers le haut) ; la flèche de tri de FM 27 (▲), teintée du vert des flèches de FM24"""
    dx, dy, angle = sens
    fab.traverse(fab.boite(par, nom, classes=[REPERE_BAS24], css={
        "position": "absolute", "left": pc(x), "top": pc(y), "width": TAILLE_FLECHE24, "height": TAILLE_FLECHE24,
        "margin-left": dx - TAILLE_FLECHE24 / 2, "margin-top": dy - TAILLE_FLECHE24 / 2,
        "rotate": {"unit": 5, "value": float(angle)}, "tint": C24["fleche-pion"]}))


def fleche24(fab, par, nom, points, rapport, pointille=False):
    """v22 : une flèche de FM24 sur un terrain ; v23 : le long d'une suite de points (droite ou courbe, en % ; rapport
    = hauteur / largeur du terrain) : un trait par morceau (en tirets si pointille), tourné dans le bon sens, et la
    pointe (la flèche de tri de FM 27, tournée) au bout"""
    angle = 0.0
    for j in range(len(points) - 1):
        (x1, y1), (x2, y2) = points[j], points[j + 1]
        dxw, dyw = (x2 - x1) / 100, (y2 - y1) / 100 * rapport
        longueur = math.hypot(dxw, dyw)
        angle = math.degrees(math.atan2(dyw, dxw))
        part = 0.55 if pointille else (0.97 if j == len(points) - 2 else 1.08)   # sans trou entre deux morceaux
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        l = longueur * part
        fab.traverse(fab.boite(par, f"{nom}-{j}", css={
            "position": "absolute", "left": pc(cx - 50 * l), "top": pc(cy), "width": pc(100 * l), "height": 2,
            "margin-top": -1, "background-color": C24["fleche"], "rotate": {"unit": 5, "value": angle}}))
    x2, y2 = points[-1]
    fab.traverse(fab.boite(par, f"{nom}-pointe", classes=[REPERE_BAS24], css={
        "position": "absolute", "left": pc(x2), "top": pc(y2), "width": 10, "height": 10, "margin-left": -5,
        "margin-top": -5, "rotate": {"unit": 5, "value": angle + 90}, "tint": C24["fleche"]}))


def calque_fleches24(fab, champ, n, nom, fleches, rapport):
    """v22 : les flèches d'une consigne, selon l'option en cours : fleches = {option: [(points, pointillés)]} ; v23 :
    dans une enveloppe à elles, posée APRÈS les zones (par-dessus toutes, Kinito : celles des dédoublements passaient
    derrière la progression)"""
    env = fab.enveloppe(champ, n, f"{nom}-env", traverse=True)

    def faire(par, k):
        b = fab.boite(par, f"{nom}-{k}", css=PLEIN)
        fab.traverse(b)
        for i, (points, p) in enumerate(fleches.get(k, [])):
            fleche24(fab, b, f"{nom}-{k}-{i}", points, rapport, p)
    s = fab.selon(env, n, faire, nom, css=PLEIN)
    for r in fab.t.walk(s):
        fab.traverse(r)


def largeur24(fab, col):
    """LARGEUR DU JEU OFFENSIF : le curseur, puis le terrain de FM24 : les pions (v25 : chaque joueur à son poste lu
    avec ballon ; le gardien en noir), plus ou moins écartés selon la largeur choisie, comme FM24"""
    curseur24(fab, col, 4, "largeur", marge=0)
    # v26 (Kinito : « il paraît écrasé, le rond central est ovale ») : aux proportions d'un vrai terrain
    champ = terrain24(fab, col, "largeur", sans_but(traits_reels(True, True)), rapport=RAPPORT_TERRAIN)
    pion24(fab, champ, "fm24-largeur-gb", *PION_GB24, gardien=True, taille=TAILLE_PION_LARGEUR24)
    e = fab.enveloppe(champ, 4, "fm24-largeur-calque", traverse=True)
    b = resserre24(fab, e, "fm24-largeur-pions")
    pions_postes24(fab, b, "fm24-largeur-postes", taille=TAILLE_PION_LARGEUR24)   # v25 : chaque joueur à son poste


def construction24(fab, col):
    """CONSTRUCTION DU JEU (FM24) : réception des passes (« dans les espaces » au-dessus, v23), puis le terrain (zones
    jointives aux places de FM24) : dédoublements extérieurs et intérieurs (courses de soutien), « Concentrez le jeu »
    (progression : gauche, axe, droite, les deux flancs à la fois comme FM24), « Gérer le pressing » en bande sur
    toute la largeur (la place de « Sortez de la défense » de FM24), « Contourner le pressing » dessous, à gauche ; les
    flèches de FM24, par-dessus ; puis les trois curseurs"""
    entete24(fab, col, "construction", ("CONSTRUCTION DU JEU", "BUILD-UP PLAY"))
    liste24(fab, col, 20, "reception", marge=4, titre=False)
    r = RAPPORT_CONSTRUCTION24   # v27
    champ = terrain24(fab, col, "construction", sans_but(traits_reels(True, True)), rapport=r, reduit=REDUIT24)
    with _PaletteZones():
        envs = {n: fab.enveloppe(champ, n, f"fm24-courses-{n}", traverse=True) for n in (28, 31)}
        for n, autre, gauche, x, w, mots in COURSES24:
            case = case24(fab, envs[n], f"fm24-course-{n}-{'g' if gauche else 'd'}", x, Y_COURSES24, w, H_COURSES24)
            course24(fab, case, n, autre, gauche)
            mot_zone(fab, case, f"fm24-course-{n}-{'g' if gauche else 'd'}-mot", mots)
        e30 = fab.enveloppe(champ, 30, "fm24-progression", traverse=True)
        for cle, montre, x, w, mots in PROGRESSION24:
            case = case24(fab, e30, f"fm24-progression-{cle}", x, Y_PROGRESSION24, w, H_PROGRESSION24)
            fab.etats(case, 30, base.REGLES_PROGRESSION[cle], montre, texte=False, **ZONE_KW)
            mot_zone(fab, case, f"fm24-progression-{cle}-mot", mots)
        e24 = fab.enveloppe(champ, 24, "fm24-strategie", traverse=True)
        for p, x, y, w, h in STRATEGIE24:
            zone24(fab, e24, 24, p, x, y, w, h, f"fm24-strategie-{p}")
    for n in (31, 28, 30, 24):   # les flèches, par-dessus TOUTES les zones
        calque_fleches24(fab, champ, n, f"fm24-fleches-{n}", FLECHES_CONSTRUCTION24[n], r)
    curseur24(fab, col, 1, "passes")
    curseur24(fab, col, 21, "rythme")
    curseur24(fab, col, 7, "temps")


def finition24(fab, col):
    """30 DERNIERS MÈTRES (FM24) : style de centres (FM24 : un menu, ici ses boutons, sans titre), le terrain aux
    zones de FM24 (patience : jouer le ballon dans la surface en haut, centrer de loin sur les côtés ; tirs de loin au
    milieu : « Tirez à vue », et dessous, de la même taille, « Moins de tirs de loin ») et leurs flèches (v23), puis
    coups de pied arrêtés, dribbles, liberté créative"""
    entete24(fab, col, "finition", ("30 DERNIERS MÈTRES", "FINAL THIRD"))
    liste24(fab, col, 26, "centres", marge=4, titre=False)
    r = RAPPORT_ZONES24
    champ = terrain24(fab, col, "finition", sans_but(traits_reels(True, True)), rapport=r, reduit=REDUIT24)   # v27
    with _PaletteZones():
        e18 = fab.enveloppe(champ, 18, "fm24-patience", traverse=True)
        for i, (p, x, y, w, h) in enumerate(PATIENCE24):
            zone24(fab, e18, 18, p, x, y, w, h, f"fm24-patience-{i}")
        e27 = fab.enveloppe(champ, 27, "fm24-tirs", traverse=True)
        for i, (p, x, y, w, h, mots) in enumerate(TIRS24):
            zone24(fab, e27, 27, p, x, y, w, h, f"fm24-tirs-{i}", mots=mots)
    for n in (18, 27):
        calque_fleches24(fab, champ, n, f"fm24-fleches-{n}", FLECHES_FINITION24[n], r)
    liste24(fab, col, 6, "cpa", titre=False, compense=True)   # v28
    liste24(fab, col, 19, "dribbles")
    liste24(fab, col, 5, "liberte")


def avec24(fab, p):
    largeur24(fab, colonne24(fab, p, "avec-1", 1, premiere=True))
    construction24(fab, colonne24(fab, p, "avec-2", 1))
    finition24(fab, colonne24(fab, p, "avec-3", 1))


def relance24(fab, col):
    """le terrain « relancer vers » (Relances GB, 16) ; v22 (Kinito : « identique à FM24 ») : les zones de FM24
    (capture 8), jointives, sans « Équilibrées » : rien de choisi = équilibré (2e clic sur une zone : la remet)"""
    mots24(fab, col, "fm24-gb-titre", (RELANCER_VERS_LANGUES[2][1].replace("\n", " "),
                                       RELANCER_VERS_LANGUES[0][1].replace("\n", " ")),
           css={"margin-top": ECART_CONSIGNE24, "margin-bottom": 4})
    champ = terrain24(fab, col, "gb", sans_but(traits_reels(True, True)), rapport=RAPPORT_GB24, marge=0)
    with _PaletteZones():
        e = fab.enveloppe(champ, 16, "fm24-gb-env", traverse=True)
        for p, zones in ZONES_GB24.items():
            for i, (x, y, w, h) in enumerate(zones):
                zone24(fab, e, 16, p, x, y, w, h, f"fm24-gb-{p}-{i}")


def transition_terrain24(fab, col, n, nom):
    """v22 : le petit terrain de FM24 d'une consigne de transition : les pions (v25 : postes lus avec ballon,
    comme la largeur), et leurs petites flèches selon l'option choisie (FLECHES_TRANSITION24)"""
    champ = terrain24(fab, col, nom, sans_but(traits_reels(True, True)), rapport=RAPPORT_TRANSITION24,
                      marge=ECART_CONSIGNE24, largeur=PART_TRANSITION24)
    pion24(fab, champ, f"fm24-{nom}-gb", *PION_GB24, gardien=True)
    pions_postes24(fab, champ, f"fm24-{nom}-postes")   # v25
    e = fab.enveloppe(champ, n, f"fm24-{nom}-calque", traverse=True)

    def faire(par, k):
        b = fab.boite(par, f"fm24-{nom}-fleches-{k}", css=PLEIN)
        fab.traverse(b)
        sens, larges = FLECHES_TRANSITION24[n].get(k, ([], False))
        if sens:
            fleches_postes24(fab, b, f"fm24-{nom}-{k}-postes", sens, larges)   # v25
    s = fab.selon(e, n, faire, f"fm24-{nom}-fleches", css=PLEIN)
    for r in fab.t.walk(s):
        fab.traverse(r)


def transition24(fab, p):
    c = colonne24(fab, p, "transition-1", 1, premiere=True)
    entete24(fab, c, "perte", ("LORS DE LA PERTE DU BALLON", "WHEN POSSESSION IS LOST"))
    liste24(fab, c, 11, "transition-def", marge=4, titre=False)
    transition_terrain24(fab, c, 11, "perte")
    c = colonne24(fab, p, "transition-2", 1)
    entete24(fab, c, "recuperation", ("LORS DE LA RÉCUPÉRATION DU BALLON", "WHEN POSSESSION IS WON"))
    liste24(fab, c, 3, "transition-off", marge=4, titre=False)
    transition_terrain24(fab, c, 3, "recuperation")
    c = colonne24(fab, p, "transition-3", 1)
    entete24(fab, c, "gardien", ("GARDIEN AVEC LE BALLON", "GOALKEEPER IN POSSESSION"))
    liste24(fab, c, 17, "gb-vitesse", marge=4, titre=False)
    relance24(fab, c)
    liste24(fab, c, 29, "sorties")


def ligne24(fab, par, n, k, y, couleur, voile, nom, parties=("voile", "halo", "trait", "badge")):
    """v23 : une variante du terrain des lignes de la vue FM24 : la ligne de Terrain (ligne_consigne : voile, halo,
    trait, badge « nom de la consigne / option »), sans les points des crans ni les repères (Kinito : « sortir les
    points du terrain » : crans24, à gauche du terrain), le trait sur toute la largeur. v26 : parties = ce qu'on en
    dessine (Kinito : les encadrés à gauche, hors du terrain, et la ligne sur toute la largeur : le terrain n'a plus
    que le voile, le halo et le trait ; à gauche, le halo et le trait sous les crans, et les encadrés)"""
    t = fab.t
    b = fab.boite(par, f"{nom}-{k}", css={"flex-grow": 1})
    fab.traverse(b)
    haut, bas, coul_voile = voile
    if "voile" in parties:
        fab.traverse(fab.boite(b, f"{nom}-{k}-voile", css={
            "position": "absolute", "left": 0, "width": pc(100), "top": pc(y if bas else 0),
            "height": pc((100 - y) if bas else y), "background-color": coul_voile}))
    r, g, bl, _ = couleur
    if "halo" in parties:
        fab.traverse(fab.boite(b, f"{nom}-{k}-halo", css={"position": "absolute", "left": 0, "width": pc(100),
                                                           "top": pc(y), "height": 12, "margin-top": -6,
                                                           "background-color": (r, g, bl, 0.2)}))
    if "trait" in parties:
        fab.traverse(fab.boite(b, f"{nom}-{k}-trait", css={"position": "absolute", "left": 0, "width": pc(100),
                                                            "top": pc(y), "height": 3, "margin-top": -1.5,
                                                            "background-color": couleur}))
    if "badge" not in parties:
        return
    rang = fab.boite(b, f"{nom}-{k}-badge-rang", css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y),
                                                       "height": 44, "margin-top": -22, "flex-direction": "row",
                                                       "justify-content": "center", "align-items": "center"})
    fab.traverse(rang)

    def badge_(par, taille):
        badge = fab.boite(par, f"{nom}-{k}-badge-{taille}", css={"flex-direction": "column", "align-items": "center",
                                                                 "min-width": base.BADGE_LARGEURS[taille],
                                                                 "padding-top": 2, "padding-bottom": 3,
                                                                 "padding-left": 8, "padding-right": 8,
                                                                 "background-color": COUL["badge"],
                                                                 **cadre_css(1, couleur, 6)})
        fab.traverse(badge)
        tit = fab.titre(badge, f"{nom}-{k}-badge-{taille}-nom", css={"margin-bottom": 0, "color": couleur})
        fab.traverse(tit)
        var, txt = fab.nom_option(badge, n, k, petit=False)
        fab.traverse(var)
        fab.traverse(txt)
        t.styles.style(t, txt, {"color": COUL["blanc"]})
    sel = fab.selon_valeur(rang, "settings.TextScaling", list(base.BADGE_LARGEURS), badge_, f"{nom}-{k}-taille")
    for r in t.walk(sel):
        if typ(t, r) in ("BindableSwitchElement", "BindingSetter"):
            fab.traverse(r)


def crans24(fab, col, n, nom, ys, bandes, couleur):
    """v23 : les points des crans d'une ligne, À GAUCHE du terrain (Kinito), celui de l'option en cours plus gros ; et
    des bandes de clic à leur hauteur (un clic choisit le cran)"""
    r, g, bl, _ = couleur
    env = fab.enveloppe(col, n, f"{nom}-env", traverse=True)

    def faire(par, k):
        b = fab.boite(par, f"{nom}-{k}", css=PLEIN)
        fab.traverse(b)
        for j, yj in enumerate(ys):
            d = 12 if j == k else 7
            fab.traverse(fab.boite(b, f"{nom}-{k}-{j}", css={
                "position": "absolute", "left": pc(50), "top": pc(yj), "width": d, "height": d, "margin-left": -d / 2,
                "margin-top": -d / 2, "background-color": couleur if j == k else (r, g, bl, 0.4),
                **cadre_css(0, couleur, d / 2)}))
    s = fab.selon(env, n, faire, f"{nom}-selon", css=PLEIN)
    for x in fab.t.walk(s):
        fab.traverse(x)
    e = fab.enveloppe(col, n, f"{nom}-clic-env", traverse=True)
    for k, (y0, y1) in enumerate(bandes):
        bouton_b(fab, e, n, k, nu=True, texte=False, bulle=False,
                 css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y0), "height": pc(y1 - y0)})


def crans_touche24(fab, par, n, nom, ys, couleur):
    """v45 (Kinito : « les points directement sur la ligne de touche, gauche et droite ; la ligne s'arrête sur les
    points ; l'utilisateur comprend le nombre de crans ») : les points des crans d'une ligne, centrés sur les deux lignes
    de touche du terrain, celui du cran en cours plus gros et plein ; un calque qui laisse passer les clics (le terrain
    garde ses bandes de clic, lignes24). par : un calque de la taille de l'INTÉRIEUR du cadre (les lignes y sont
    placées), posé hors du cadre (qui coupe ce qui dépasse) : la moitié extérieure des points reste visible"""
    r, g, bl, _ = couleur
    env = fab.enveloppe(par, n, f"{nom}-env", traverse=True)

    def faire(p, k):
        b = fab.boite(p, f"{nom}-{k}", css=PLEIN)
        fab.traverse(b)
        for j, yj in enumerate(ys):
            d = POINT_CRAN_CHOISI24 if j == k else POINT_CRAN24
            for cote in (0, 100):
                fab.traverse(fab.boite(b, f"{nom}-{k}-{j}-{cote}", css={
                    "position": "absolute", "left": pc(cote), "top": pc(yj), "width": d, "height": d,
                    "margin-left": -d / 2, "margin-top": -d / 2,
                    "background-color": couleur if j == k else (r, g, bl, 0.55), **cadre_css(0, couleur, d / 2)}))
    s = fab.selon(env, n, faire, f"{nom}-selon", css=PLEIN)
    for x in fab.t.walk(s):
        fab.traverse(x)


def encadre24(fab, par, n, nom, couleur):
    """v45 : l'encadré d'une ligne (« LIGNE DÉFENSIVE / Plus haute »), au-dessus du terrain, dans le flux (v26 à v44 :
    à gauche du terrain, à la hauteur de sa ligne, ligne24 « badge ») : le nom de la consigne dans la couleur de sa
    ligne, l'option en cours dessous ; il prend la moitié de la largeur du terrain"""
    t = fab.t
    env = fab.enveloppe(par, n, f"{nom}-env", css={"flex-grow": 1, "flex-basis": 0, "flex-direction": "column"})

    def faire(p, k):
        badge = fab.boite(p, f"{nom}-{k}", css={"flex-grow": 1, "flex-direction": "column", "align-items": "center",
                                                 "justify-content": "center", "padding-top": 2, "padding-bottom": 3,
                                                 "padding-left": 8, "padding-right": 8,
                                                 "background-color": COUL["badge"], **cadre_css(1, couleur, 6)})
        tit = fab.titre(badge, f"{nom}-{k}-nom", css={"margin-bottom": 0, "color": couleur})
        fab.traverse(tit)
        var, txt = fab.nom_option(badge, n, k, petit=False)
        fab.traverse(var)
        fab.traverse(txt)
        t.styles.style(t, txt, {"color": COUL["blanc"]})
    fab.selon(env, n, faire, f"{nom}-selon", css={"flex-grow": 1, "flex-direction": "column"})   # ses interrupteurs
    return env                                                                                 # grandissent (selon)


def cale24(fab, par, nom, hauteur):
    """v23 : une cale de <hauteur> % de la hauteur du terrain des lignes : sa marge intérieure en % se compte sur la
    LARGEUR (règle des marges), et ce terrain a un rapport fixe (RAPPORT_TERRAIN)"""
    fab.traverse(fab.boite(par, nom, css={"height": 0, "padding-bottom": pc(hauteur * RAPPORT_TERRAIN),
                                          "flex-shrink": 0}))


def pions_sans24(fab, champ):
    """v23 (Kinito : « les pions sur le terrain sans ballon aussi ; comme FM24 ça bouge quand on bouge les lignes ») :
    une colonne sur tout le terrain : une cale jusqu'à la ligne de pressing (selon son cran), la zone des pions, une
    cale depuis la ligne défensive (selon son cran) ; les pions (v25 : postes lus SANS ballon) y sont posés UNE fois, les attaquants
    sur la ligne de pressing, les défenseurs sur la ligne défensive, les autres lignes entre les deux (LIGNES_SANS24)"""
    col = fab.boite(champ, "fm24-sans-pions", css={**PLEIN, "flex-direction": "column"})
    fab.traverse(col)
    e8 = fab.enveloppe(col, 8, "fm24-sans-cale-8-env", css={"flex-shrink": 0, "flex-direction": "column"})
    fab.traverse(e8)
    s8 = fab.selon(e8, 8, lambda par, k: cale24(fab, par, f"fm24-sans-cale-8-{k}", Y_PRESSING24[k]),
                   "fm24-sans-cale-8", css={"flex-shrink": 0})
    zone = fab.boite(col, "fm24-sans-zone", css={"flex-grow": 1})
    fab.traverse(zone)
    pions_postes24(fab, zone, "fm24-sans-postes", lignes=LIGNES_SANS24, avec=False, part=PART_PION24)   # v27   # v25 : postes sans ballon
    e9 = fab.enveloppe(col, 9, "fm24-sans-cale-9-env", css={"flex-shrink": 0, "flex-direction": "column"})
    fab.traverse(e9)
    s9 = fab.selon(e9, 9, lambda par, k: cale24(fab, par, f"fm24-sans-cale-9-{k}", 100 - Y_LIGNE[k]),
                   "fm24-sans-cale-9", css={"flex-shrink": 0})
    for s in (s8, s9):
        for x in fab.t.walk(s):
            fab.traverse(x)


def lignes24(fab, cadre, traits):
    """v22 : le terrain des lignes de Terrain (lignes_b), sans la relance courte du gardien (Kinito : elle devient UN
    bouton, comme FM24 : bouton_mots24 sous le déclenchement du pressing) ; v23 : la hauteur du pressing sur toute la
    moitié haute, en trois tiers (Y_PRESSING24, Kinito), les lignes sans les points des crans (à gauche du terrain :
    crans24), et les pions de la formation, qui suivent les deux lignes (pions_sans24)"""
    champ = champ_terrain(fab, cadre, "fm24-lignes", traits)
    e = fab.enveloppe(champ, 8, "fm24-pressing-env", traverse=True)
    calque_selon(fab, e, 8, lambda par, k: ligne24(fab, par, 8, k, Y_PRESSING24[k], COUL["pressing"],
                                                   (True, False, COUL["voile-pressing"]), "fm24-pressing",
                                                   ("voile", "halo", "trait")),
                 "fm24-pressing-ligne")
    e = fab.enveloppe(champ, 9, "fm24-defense-env", traverse=True)
    calque_selon(fab, e, 9, lambda par, k: ligne24(fab, par, 9, k, Y_LIGNE[k], COUL["defense"],
                                                   (False, True, COUL["voile-defense"]), "fm24-defense",
                                                   ("voile", "halo", "trait")),
                 "fm24-defense-ligne")
    pion24(fab, champ, "fm24-sans-gb", *PION_GB24, gardien=True, part=PART_PION24)   # v27
    pions_sans24(fab, champ)
    for n, bandes in ((8, BANDES_PRESSING24), (9, BANDES_LIGNE)):   # les bandes de clic, par-dessus les lignes
        e = fab.enveloppe(champ, n, f"fm24-bandes-env-{n}", traverse=True)
        for k, (y0, y1) in enumerate(bandes):
            bouton_b(fab, e, n, k, nu=True, texte=False, bulle=False,
                     css={"position": "absolute", "left": 0, "width": pc(100), "top": pc(y0), "height": pc(y1 - y0)})


def bouton_mots24(fab, col, n, p, nom, mots, marge=ECART_BOUTON_SEUL24):
    """v22 : UN bouton de FM24 écrit de nos mots (le nom de l'option du jeu ne dit rien seul : « Oui ») : un clic
    choisit l'option p, un 2e la remet (bouton_b)"""
    e = fab.enveloppe(col, n, f"fm24-{nom}", css={"flex-direction": "column", "flex-shrink": 0, "margin-top": marge})
    case = fab.boite(e, f"fm24-{nom}-case", css={"height": H_BOUTON24, "flex-direction": "row", "flex-shrink": 0})
    bouton_b(fab, case, n, p, texte=False, icone=False, assombrir=True, css={"flex-grow": 1})
    mot_zone(fab, case, f"fm24-{nom}-mot", mots, classe=CLASSE_TEXTE24, taille=TAILLE_TEXTE24)   # v28
    return e


def sans24(fab, p):
    c = colonne24(fab, p, "sans-1", 2, premiere=True)
    entete24(fab, c, "formation", ("FORMATION DÉFENSIVE", "DEFENSIVE SHAPE"))
    # v45 (Kinito : « centrer le terrain, l'agrandir au max en gardant les proportions ; les encadrés côte à côte
    # au-dessus, ligne déf à gauche, pressing à droite ; les points des crans sur les lignes de touche ») : une rangée
    # = marge | milieu | marge ; les deux marges ont la largeur de leur taille du texte (MARGE_TERRAIN_SANS24 : un
    # interrupteur de FM sur settings.TextScaling, selon_valeur, choisit une cale de cette largeur, sans hauteur, comme
    # la colonne de gauche de la v28) : le milieu prend le reste, centré ; dedans, les encadrés puis le terrain, dont la
    # hauteur suit la largeur (vraies proportions). (v26 à v44 : encadrés, crans et ligne prolongée à gauche du terrain)
    rangee = fab.boite(c, "fm24-formation", css={"width": pc(100), "flex-shrink": 0, "margin-top": 6,
                                                  "flex-direction": "row"})

    def marge(cote):
        m = fab.boite(rangee, f"fm24-formation-marge-{cote}", css={"flex-shrink": 0, "flex-direction": "column"})
        cale = fab.selon_valeur(m, "settings.TextScaling", list(MARGE_TERRAIN_SANS24),
                                lambda par, v: fab.traverse(fab.boite(par, f"fm24-formation-marge-{cote}-{v}", css={
                                    "width": MARGE_TERRAIN_SANS24[v], "height": 0, "flex-shrink": 0})),
                                f"fm24-formation-marge-{cote}-largeur", css={"flex-shrink": 0})
        for r in fab.t.walk(cale):
            fab.traverse(r)
    marge("g")
    milieu = fab.boite(rangee, "fm24-formation-terrain", css={"flex-grow": 1, "flex-basis": 0,
                                                               "flex-direction": "column"})
    marge("d")
    encadres = fab.boite(milieu, "fm24-formation-encadres", css={"flex-direction": "row", "flex-shrink": 0,
                                                                 "margin-bottom": ECART_ENCADRES_SANS24})
    encadre24(fab, encadres, 9, "fm24-defense-encadre", COUL["defense"])   # à gauche (Kinito)
    fab.traverse(fab.boite(encadres, "fm24-formation-encadres-ecart", css={"width": ECART_ENCADRES_SANS24,
                                                                           "flex-shrink": 0}))
    encadre24(fab, encadres, 8, "fm24-pressing-encadre", COUL["pressing"])   # à droite
    haut = fab.boite(milieu, "fm24-formation-haut", css={"height": 0, "padding-bottom": pc(100 * RAPPORT_TERRAIN),
                                                          "flex-shrink": 0})
    cadre = fab.boite(haut, "fm24-formation-cadre", css={**PLEIN, "flex-direction": "column", "overflow": "hidden",
                                                         **base.cadre_css(1, C24["ligne"])})
    lignes24(fab, cadre, traits_reels(True, True))   # hauteur du pressing, ligne défensive, pions (v23)
    # v45 : les points des crans sur les deux lignes de touche, posés HORS du cadre (il coupe ce qui dépasse), sur un
    # calque de la taille de son intérieur (v29 : le cadre a 1 px, ses lignes se placent dedans) ; les traits des
    # lignes (lignes24) vont d'une ligne de touche à l'autre : ils s'arrêtent sur les points
    points = fab.boite(haut, "fm24-formation-points", css={"position": "absolute", "left": 1, "right": 1, "top": 1,
                                                            "bottom": 1})
    fab.traverse(points)
    crans_touche24(fab, points, 8, "fm24-crans-8", Y_PRESSING24, COUL["pressing"])
    crans_touche24(fab, points, 9, "fm24-crans-9", Y_LIGNE, COUL["defense"])
    c = colonne24(fab, p, "sans-2", 1)
    curseur24(fab, c, 10, "declench", marge=0)
    bouton_mots24(fab, c, 23, 1, "relance-courte", MOTS_RELANCE_COURTE24)
    liste24(fab, c, 12, "tacles")
    liste24(fab, c, 15, "ligne")
    liste24(fab, c, 25, "piege")
    liste24(fab, c, 22, "centres-sans")


def carte24(fab, col, k, nom_mots, consignes, v="", facteur=1.0):
    """la carte d'une phase (FM24) : un bouton de FM (celui des boutons segmentés des cartes de chaleur, vidé) qui ouvre
    la phase ; dedans : son fond (violet bordé de blanc si elle est ouverte), son icône (v21 : celle de FM 27) et son
    nom, le résumé des consignes choisies (autres que l'option neutre, noms des options lus dans les données du jeu),
    « Changer » ou « OK ». v44 : v (suffixe des noms) et facteur (la police, 100 / taille du texte de FM) : une
    variante par taille du texte (cartes_selon_taille24)"""
    taille = lambda px: round(px * facteur, 2)   # noqa: E731
    t, src = fab.t, fab.src
    reglages = src.th.children(src.segments)
    modele = src.th.children(reglages[0])[0] if reglages and src.th.children(reglages[0]) else None
    if modele is None or typ(src.th, modele) != "SIButton":
        raise ValueError("bouton segmenté des cartes de chaleur (introuvable)")
    b = recopie_seule(fab, src.th, modele, col, f"fm24-phase{v}-{k}")
    t.elem(b)["m_Classes"], t.elem(b)["m_RuleIndex"] = [], -1
    evenements(t, b, [copier(PLACES[k], V_PHASE24, _drapeau(PLACES[k]))])
    t.styles.style(t, b, {"flex-direction": "column", "align-items": "stretch", "flex-shrink": 0,
                          "padding-top": 7, "padding-bottom": 7, "padding-left": 8, "padding-right": 8,
                          "margin-top": 6 if k else 0, "margin-bottom": 0, "margin-left": 0, "margin-right": 0,
                          "background-color": (0.0, 0.0, 0.0, 0.0), **cadre_css(0, (0.0, 0.0, 0.0, 0.0))})
    fond = fab.interrupteur(b, f"fm24-phase{v}-{k}-fond", V_PHASE24, css=PLEIN, index=0)
    for j in range(len(PHASES24)):
        fab.boite(fond, f"fm24-phase{v}-{k}-fond-{j}", css={"flex-grow": 1, **(
            {"background-color": C24["ouverte"], **cadre_css(1, C24["ouverte-bord"], 4)} if j == k else
            {"background-color": C24["fermee"], **cadre_css(0, C24["fermee"], 4)})})
    tete = fab.boite(b, f"fm24-phase{v}-{k}-tete", css={"flex-direction": "row", "justify-content": "center",
                                                     "align-items": "center", "flex-shrink": 0})
    fab.boite(tete, f"fm24-phase{v}-{k}-icone", classes=[ICONES_PHASES24[k]], css={
        "width": TAILLE_ICONE24, "height": TAILLE_ICONE24, "flex-shrink": 0, "margin-right": 6})
    mots24(fab, tete, f"fm24-phase{v}-{k}-nom", nom_mots, css={"font-size": taille(TAILLE_NOM_PHASE24)})   # v44
    resume = fab.boite(b, f"fm24-phase{v}-{k}-resume", css={"flex-direction": "column", "flex-shrink": 0,
                                                         "margin-top": 3})
    ligne = {"font-size": taille(TAILLE_RESUME_PHASE24), "height": H_LIGNE_RESUME24, "flex-shrink": 0,
             "white-space": "nowrap", "-unity-text-align": "middle-center", "margin-top": 0, "margin-bottom": 0,
             "padding-top": 0, "padding-bottom": 0}   # v44 : une ligne, à hauteur fixe
    for n in consignes:
        e = fab.enveloppe(resume, n, f"fm24-resume{v}-{n}", css={"flex-direction": "column", "flex-shrink": 0})

        def faire(par, place, n=n):
            if place == DEFAUTS.get(n):
                fab.boite(par, f"fm24-resume{v}-{n}-neutre-{fab.n}", css={"height": 0})
                fab.n += 1
                return
            if place in MOTS_RESUME24.get(n, {}):   # v22
                fab.n += 1
                mots24(fab, par, f"fm24-resume{v}-{n}-mots-{fab.n}", MOTS_RESUME24[n][place], classe=CLASSE_RESUME24,
                       couleur=C24["resume"], css=ligne)
                return
            _, texte = fab.nom_option(par, n, place, css={"flex-shrink": 0})
            t.elem(texte)["m_Classes"] = [CLASSE_RESUME24]
            t.styles.style(t, texte, {"color": C24["resume"], **ligne})
        fab.selon(e, n, faire, f"fm24-resume{v}-{n}-sel", css={"flex-shrink": 0})
    pied = fab.interrupteur(b, f"fm24-phase{v}-{k}-pied", V_PHASE24, css={"flex-shrink": 0, "margin-top": 4})
    for j in range(len(PHASES24)):
        mots24(fab, pied, f"fm24-phase{v}-{k}-pied-{j}",
               ("«  OK", "«  OK") if j == k else ("»  CHANGER", "»  CHANGE"),
               css={"flex-shrink": 0, "font-size": taille(TAILLE_PIED_PHASE24)})
    for r in list(t.walk(b))[1:]:   # tout le contenu laisse passer le clic : c'est la carte qui le prend
        fab.traverse(r)
    return b


def cartes_selon_taille24(fab, col):
    """v44 : les trois cartes, une variante par taille du texte de FM (la comparaison de FM sur settings.TextScaling,
    un interrupteur par taille agrandie, comme texte_comp24) : leurs mots ont la même taille à l'écran partout"""
    t = fab.t
    tailles = list(TAILLES_TEXTE24)
    css = {"flex-grow": 1, "flex-direction": "column"}
    sel = fab._comparer(col, "fm24-phases-taille", [(f"kinitotaille{x}", x) for x in tailles], "settings.TextScaling")
    t.styles.style(t, sel, css)
    fab.traverse(sel)

    def cartes(par, facteur, v):   # UNE boîte par variante : un interrupteur de FM ne montre qu'un enfant (son rang)
        boite = fab.boite(par, f"fm24-phases{v or '-normal'}", css={"flex-direction": "column", "flex-shrink": 0})
        fab.traverse(boite)
        for k, (_, mots, consignes) in enumerate(PHASES24):
            carte24(fab, boite, k, mots, consignes, v=v, facteur=facteur)

    def chaine(par, i):
        if i == len(tailles):
            cartes(par, 1.0, "")
            return
        sw = fab.interrupteur(par, f"fm24-phases-si{tailles[i]}", f"kinitotaille{tailles[i]}", css=css)
        fab.traverse(sw)
        chaine(sw, i + 1)                                               # rang 0 : pas cette taille
        cartes(sw, TAILLES_TEXTE24[tailles[i]], f"-t{tailles[i]}")      # rang 1 : cette taille
    chaine(sel, 0)


def legende24(fab, parent):
    """en bas, sous le panneau : « ● Sélectionné  ● Indisponible » (FM24)"""
    leg = fab.boite(parent, "fm24-legende", css={"flex-direction": "row", "justify-content": "center",
                                                  "align-items": "center", "height": 30, "flex-shrink": 0})
    fab.traverse(leg)
    for i, (cle, mots) in enumerate((("choisi", ("Sélectionné", "Selected")),
                                     ("indispo", ("Indisponible", "Unavailable")))):
        fab.traverse(fab.boite(leg, f"fm24-legende-{cle}", css={
            "width": 13, "height": 13, "flex-shrink": 0, "margin-left": 20 if i else 0, "margin-right": 6,
            "background-color": C24[f"point-{cle}"], **cadre_css(0, C24[f"point-{cle}"], 7)}))
        mots24(fab, leg, f"fm24-legende-{cle}-mot", mots, classe=CLASSE_TEXTE24, css={"white-space": "nowrap"})


def bouton_fm24(fab):
    """le 3e bouton de l'en-tête : une copie de « Terrain » (posé par kinito_consignes_essai.bascule, mis à l'allure
    de « Vue d'ensemble » par vue_comme_ensemble), qui écrit 2 dans la vue, assombri quand elle n'est pas affichée"""
    t = fab.t
    terrain = first(t, lambda r: t.name(r) == f"{base.PREFIXE}-allume-terrain")
    if terrain is None:
        raise ValueError("bouton « Terrain » de l'en-tête (introuvable)")
    rangee = t.parent[terrain]
    c = t.clone(terrain, rangee)
    t.styles.copy_from(t.styles, t, c)
    for r in t.walk(c):
        sd = t.sd(r)
        if "terrain" in (sd.get("name") or ""):
            sd["name"] = sd["name"].replace("terrain", "fm24")
    f = t.sd(c)["BindFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != 7 or not bytes(args[2][0]).endswith(b"Int32VisualArg"):
        raise ValueError("réglage du bouton « Terrain » : arguments inattendus (introuvable)")
    args[2][1] = struct.pack("<i", VUE_FM24)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    bouton = first(t, lambda r: t.name(r) == f"{base.PREFIXE}-bouton-fm24", root=c)
    if bouton is None:
        raise ValueError("bouton « Terrain » de l'en-tête : forme inattendue (introuvable)")
    evenements(t, bouton, [copier("const.Two", base.VARIABLE, 1)])
    textes = [r for r in t.walk(bouton) if typ(t, r) == "SIText"]
    if not textes:
        raise ValueError("texte du bouton « Terrain » (introuvable)")
    for r in textes:
        t.sd(r).update(text=TEXTE_FM24, DebugDisplay=TEXTE_FM24)
    # v23 (Kinito) : « FM24 », « Tuiles », « Terrain », dans cet ordre (avant : Terrain, Tuiles, FM24)
    base.deplacer(t, c, rangee, 0)
    base.deplacer(t, terrain, rangee, len(t.children(rangee)) - 1)
    t.styles.style(t, c, {"flex-shrink": 0, "margin-left": 0})
    t.styles.style(t, terrain, {"margin-left": ECART_ENTETE})


def derriere24(fab, racine24):
    """FM24 : le rouge « indisponible » est le FOND du bouton : la couche d'estompe (Fab.lisere : posée par-dessus le
    contenu, faite pour voiler une icône) passe derrière le texte, juste au-dessus du fond « choisi ». v23 (Kinito :
    « enlever les encadrés des boutons sélectionnés ») : les boutons sans bord (le fond « choisi » et le rouge,
    posés DANS le bord, laissaient voir le bord tout autour)"""
    t = fab.t
    n = 0
    sans_bord = {f"border-{c}-width": 0 for c in ("top", "bottom", "left", "right")}
    boutons = set()
    for r in list(t.walk(racine24)):
        p = t.parent.get(r)
        if p is None or typ(t, p) != "SIButton" or not re.search(r"-o\d+-(defaut|lisere|choisie)$", t.name(r)):
            continue
        enfants = t.children(p)
        if not enfants or not t.name(enfants[0]).endswith("-choisie"):
            raise ValueError("bouton de consigne : forme inattendue (introuvable)")
        boutons.add(p)
        if not t.name(r).endswith("-choisie"):
            base.deplacer(t, r, p, 1)
            n += 1
    for b in boutons:
        t.styles.style(t, b, sans_bord)
    for r in list(t.walk(racine24)):   # les fonds « choisi » et « rouge » eux-mêmes : sans bord non plus
        if re.search(r"-o\d+-(choisie-oui|estompe-oui)$", t.name(r)):
            t.styles.style(t, r, sans_bord)
    return n


# v52 (Kinito, 08/11, capture d'un joueur en 1440p : « le terrain ne rentre pas dans l'écran »). Nos vues Terrain et
# FM24 ont été réglées sur le bloc des consignes en 16:9 (1920 x 1080) : 804,1 x 672 px, dans les journaux de clics de
# Kinito, les mêmes du 13/10 au 29/10 (15 journaux, avant-match et en match, toute taille du texte). En grand écran, la
# composition Large laisse ce bloc grandir en largeur (m_maxSize 100 colonnes : sur la capture, ~2,5 fois sa largeur
# du 16:9) : les terrains, dont la hauteur suit la largeur (padding-bottom en %), devenaient bien plus hauts que la
# place. Chaque vue va désormais dans un SIAspectRatioFitter de FM (recopié de RecruitmentAddTransferTargetCard) en
# mode HeightControlsWidth : FM lui donne une largeur = sa hauteur x RAPPORT_VUE (lu dans GameAssembly,
# SIAspectRatioFitterCore::CalculateSize : mode 1, style.width = resolvedStyle.height x AspectRatio), et il ne dépasse
# jamais son parent (max-width 100 %, flex-shrink). En 16:9, hauteur x RAPPORT_VUE est PLUS large que le bloc (Terrain :
# 672 x 1,205 = 809,8 > 804,1 ; FM24, dans sa marge de 6 px : 666 x 1,205 = 802,5 > 792,1) : la largeur reste celle du
# bloc, rien ne bouge (calculé, pas mesuré). Plus large que le 16:9 : la vue garde les proportions du 16:9 (à 0,7 %
# près), au centre ; ses terrains ne grandissent qu'avec la hauteur, le reste (textes, boutons) est fixe : elle tient.
RAPPORT_VUE = 1.205   # largeur / hauteur (le mode HeightControlsWidth de FM : largeur = hauteur x rapport)
# v53 : en vue FM24, le cadre est DANS le panneau des colonnes (fm24-consignes), sous le liseré de 6 points et au-dessus
# de la légende (30 points). En points (1 point = 1,1428 px en 1080p) : le bloc fait 703,6 x 588,0 ; le panneau
# 703,6 - 2 x 6 = 691,6 de large et 588,0 - 6 - 30 = 552,0 de haut, soit 1,2529 : 552 x 1,26 = 695,5 > 691,6, la
# largeur reste celle du panneau en 16:9 (calculé). (v52 : ses chiffres en px valaient en points par leur rapport :
# Terrain 588,0 x 1,205 = 708,5 > 703,6 ; FM24 582,0 x 1,205 = 701,3 > 691,6.)
RAPPORT_VUE24 = 1.26
MODELE_PROPORTIONS = ("RecruitmentAddTransferTargetCard", "CloseButtonAspectRatioFitter")
_PROPORTIONS = []


def cadre_proportions(fab, racine, nom, rapport=RAPPORT_VUE):
    """v52 : racine (en ligne, centrée) > l'élément de FM qui garde les proportions de la vue (rapport : RAPPORT_VUE ;
    v53 : RAPPORT_VUE24 pour le panneau de la vue FM24) ; rend ce dernier, où se pose la vue"""
    t = fab.t
    if not _PROPORTIONS:
        o = ouvrir(MODELE_PROPORTIONS[0], depart_original=True)
        r = o and first(o[3], lambda x: o[3].name(x) == MODELE_PROPORTIONS[1]
                        and typ(o[3], x) == "SIAspectRatioFitter")
        if r is None:
            raise ValueError(f"{MODELE_PROPORTIONS[0]} : {MODELE_PROPORTIONS[1]} (introuvable)")
        _PROPORTIONS.append((o[3], r))
    ts, r = _PROPORTIONS[0]
    sd = ts.sd(r)
    if sd.get("AspectMode") != 1 or not sd.get("AspectRatio_UxmlAttributeFlags"):
        raise ValueError(f"{MODELE_PROPORTIONS[1]} : réglages inattendus (introuvable)")
    t.styles.style(t, racine, {"flex-direction": "row", "justify-content": "center", "align-items": "stretch"})
    f = t.clone(r, racine, src=ts)   # sans ses enfants, ni ses classes, ni son style (le nôtre ci-dessous)
    for k in list(t.children(f)):
        t.remove(k)
    t.elem(f)["m_Classes"], t.elem(f)["m_RuleIndex"] = [], -1
    recaler_parent(t, f)
    fab._nom(f, nom)
    fs = t.sd(f)
    fs["AspectMode"], fs["AspectRatio"] = 1, rapport
    fs["AspectMode_UxmlAttributeFlags"] = fs["AspectRatio_UxmlAttributeFlags"] = 1
    t.styles.style(t, f, {"flex-direction": "column", "flex-grow": 0, "flex-shrink": 1, "min-width": 0,
                          "max-width": pc(100)})
    return f


def vue_fm24(fab, racine):
    """v19 : la vue FM24, 3e enfant de l'interrupteur « Tuiles / Terrain » (base.VARIABLE == 2) ; v20 : les consignes
    sur toute la largeur du bloc (les phases sont dans la colonne de droite : poser_droite)"""
    t = fab.t
    vue = t.parent[racine]
    if t.name(vue) != f"{base.PREFIXE}-vue" or len(t.children(vue)) != 2:
        raise ValueError("interrupteur « Tuiles / Terrain » : forme inattendue (introuvable)")
    racine24 = fab.boite(vue, "fm24", css={"flex-grow": 1, "flex-direction": "column", "background-color": C24["cadre"],
                                           "padding-top": 6, "padding-left": 6, "padding-right": 6})
    bouton_fm24(fab)
    # v97 : le panneau et la légende sous le conteneur de la langue du jeu (une colonne qui remplit racine24)
    env_lg = langue24(fab, racine24, "fm24-langue", {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                                     "min-height": 0, "flex-direction": "column"})
    with _PaletteFM24():
        consignes = fab.boite(env_lg, "fm24-consignes", css={
            "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "flex-direction": "column",
            "background-color": C24["panneau"], "overflow": "hidden", **cadre_css(0, C24["panneau"], 3)})
        # v52 : le cadre des proportions autour de racine24 ; v53 : dans le panneau (son fond va d'un bord à l'autre)
        cadre24 = cadre_proportions(fab, consignes, "fm24-proportions", RAPPORT_VUE24)
        panneaux = fab.interrupteur(cadre24, "fm24-panneaux", V_PHASE24, css={"flex-grow": 1})
        for k, faire in enumerate((avec24, transition24, sans24)):
            faire(fab, fab.boite(panneaux, f"fm24-panneau-{k}", css={"flex-grow": 1, "flex-direction": "row",
                                                                     "padding-bottom": 6}))
        legende24(fab, env_lg)   # v53 : sous le panneau, comme la v51 (v52 : dans le cadre)
    traduire24(fab, env_lg)   # v97
    derriere24(fab, racine24)
    return racine24


# ---------- v97 : les vues FM24 dans la langue du jeu (comme la vue Terrain, kinito_consignes_ecran v95) ----------
_LANGUE24 = set()   # les modèles où nos règles de langue sont déjà posées (une fois par modèle)


def reglage_langue(t, src, parent, nom, code):
    """v97 : le réglage de FM qui pose kinito-lg-<langue> sur son parent quand la langue du jeu est code : celui des
    boutons segmentés des cartes de chaleur recopié d'un AUTRE modèle (reglage_parent, v80), sa fonction changée pour
    la comparaison de texte BindStringToAorBUssClass (comme reglage_texte, v87)"""
    s = reglage_parent(t, src, parent, nom, ecran37.CHEMIN_LANGUE, 0, "x", {"position": "absolute", "width": 0,
                                                                           "height": 0})
    f = t.sd(s)["BindFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chem, txt, oui = args[0][0], args[3][0], args[5][0]
    f["m_target"]["m_guid"] = GUID_CLASSE_TEXTE
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args([
        [chem, _texte_arg(ecran37.CHEMIN_LANGUE)],
        [txt, _texte_arg(ecran37.CLASSE_LANGUE + ecran37.slug(code))],   # True Style
        [txt, _texte_arg("")],                                           # False Style
        [oui, bytes([1])],                                               # ApplyToParent
        [oui, bytes([0])],                                               # ApplyToChildren
        [txt, _texte_arg(code)]])                                        # CompareString
    return s


def langue24(fab, parent, nom, css):
    """v97 : le conteneur de FM qui lit la langue du jeu (celui de tdd-messages-banner, comme
    kinito_consignes_ecran.conteneur_langue), un réglage par langue qui y pose sa classe, nos règles de langue
    (ecran37.regles_langues) une fois par modèle"""
    t, src = fab.t, fab.src
    env = t.clone(src.langue_env, parent, src=src.tg)
    recaler_parent(t, env)
    for k in list(t.children(env)):
        if not t.elem(k).get("m_FullTypeName", "").endswith("Component"):
            t.remove(k)
    t.styles.copy_from(src.tg.styles, t, env)
    fab._nom(env, nom)
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
    if "current_language" not in donnees or "app.NativeSettings" not in donnees:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    t.styles.style(t, env, css)
    fab.traverse(env)
    for code in ecran37.LANGUES_JEU:
        reglage_langue(t, src, env, f"{base.PREFIXE}-{nom}-{ecran37.slug(code)}", code)
    ecran37.attacher_feuille(t, env)
    if id(t.tt) not in _LANGUE24:
        ecran37.regles_langues(t)
        _LANGUE24.add(id(t.tt))
    return env


def mots24_langues():
    """{texte écrit par la vue (langue du skin) : {langue du jeu : texte}} (TEXTES24_LANGUES)"""
    if len(ORDRE_TEXTES24) != len(ecran37.LANGUES_JEU) or set(ORDRE_TEXTES24) != set(ecran37.LANGUES_JEU):
        raise ValueError("langues de TEXTES24_LANGUES : autres que celles du jeu")
    table = {langue.texte(fr, en): dict(zip(ORDRE_TEXTES24, mots)) for (fr, en), mots in TEXTES24_LANGUES.items()}
    # « RELANCER VERS » (titre du terrain des relances, sur une ligne) : sa table en 25 langues existe (nos traductions)
    rv = {lg: mot.replace("\n", " ") for lg, mot in RELANCER_VERS_LANGUES}
    table[langue.texte(rv["french"], rv["english"])] = {lg: rv.get(lg, rv["english"]) for lg in ecran37.LANGUES_JEU}
    return table


def traduire24(fab, racine):
    """v97 : chaque texte fixe de nos mots sous racine (un conteneur langue24) remplacé par une copie par texte
    différent, chacune avec la classe des langues qui l'écrivent ainsi (kinito-lt-<langue>) ; le texte d'origine devient
    le mot de secours anglais (kinito-ltd). Sur une ligne (white-space nowrap), trop long : « … », et la phrase entière
    au survol là où le texte le reçoit (le réglage de FM DisplayTooltipWhenElided ; le passage du survol n'est pas
    changé : des textes posés par-dessus une case laissent passer ses clics)"""
    t = fab.t
    table = mots24_langues()
    ws = base.sm.PROPRIETES["white-space"][0]
    n = 0
    for r in [r for r in t.walk(racine) if typ(t, r) == "SIText"]:
        sd = t.sd(r)
        if (sd.get("TextBinding") or {}).get("m_kind", 0) != 0:
            continue
        mots = table.get(sd.get("text") or "")
        if not mots:
            continue
        e = t.elem(r)
        une_ligne = e.get("m_RuleIndex", -1) >= 0 and any(
            v[0] == ws and any(x[1] == "nowrap" for x in v[-1]) for v in t.styles.values(e["m_RuleIndex"]))
        classes = list(e.get("m_Classes") or [])
        parent = t.parent[r]
        if typ(t, parent) == "BindableSwitchElement":   # v98 : voir envelopper24
            parent = envelopper24(fab, r)
        rang = t.children(parent).index(r)
        groupes = {}
        for code in ecran37.LANGUES_JEU:
            groupes.setdefault(mots[code], []).append(code)
        copies = []
        for i, (mot, codes) in enumerate(groupes.items()):
            c = t.clone_shallow(r, parent, rang + 1 + i)
            t.sd(c).update(text=mot, DebugDisplay=mot)
            t.elem(c)["m_Classes"] = classes + [ecran37.CLASSE_MOT] + [f"{ecran37.CLASSE_MOT}-{ecran37.slug(k)}"
                                                                      for k in codes]
            copies.append(c)
        sd.update(text=mots["english"], DebugDisplay=mots["english"])
        e["m_Classes"] = classes + [ecran37.CLASSE_MOT_DEFAUT]
        survol = une_ligne and survol_libre24(t, r, racine)
        for c in copies + [r]:
            if une_ligne:
                t.styles.style(t, c, {"overflow": "hidden", "text-overflow": "ellipsis"})
                t.sd(c)["DisplayTooltipWhenElided"], t.sd(c)["DisplayTooltipWhenElided_UxmlAttributeFlags"] = 1, 1
            if survol:   # v99 : il reçoit le survol (PickingMode.Position), sinon la phrase entière ne vient jamais
                t.sd(c)["pickingMode"], t.sd(c)["pickingMode_UxmlAttributeFlags"] = 0, 1
        fab.n_survols24 = getattr(fab, "n_survols24", 0) + (len(copies) + 1 if survol else 0)
        n += 1
    fab.n_traduits24 = getattr(fab, "n_traduits24", 0) + n
    return n


def absolu24(t, r):
    """l'élément est posé en position absolue (par-dessus ses voisins)"""
    e = t.elem(r)
    pos = base.sm.PROPRIETES["position"][0]
    return e.get("m_RuleIndex", -1) >= 0 and any(
        v[0] == pos and any(x[1] == "absolute" for x in v[-1]) for v in t.styles.values(e["m_RuleIndex"]))


def survol_libre24(t, r, racine):
    """v99 (Kinito, 14/11, v98 vue en espagnol : « Más en… / Más dir… » au-dessus de la jauge des passes, sans moyen
    de lire la suite) : jusqu'en v98 tous nos textes laissaient passer la souris (fab.traverse), si bien que le réglage
    de FM DisplayTooltipWhenElided ne servait nulle part. Un texte reçoit maintenant le survol s'il ne peut rien
    prendre à une case : ni dans un bouton de FM, ni posé en absolu (lui ou un parent jusqu'au conteneur de langue),
    ni voisin d'une boîte posée en absolu qui contient un bouton (une bande de clic par-dessus)"""
    p = r
    while p is not None and p != racine:
        if typ(t, p) == "SIButton" or absolu24(t, p):
            return False
        par = t.parent.get(p)
        if par is None:
            break
        for s in t.children(par):
            if s != p and absolu24(t, s) and any(typ(t, k) == "SIButton" for k in t.walk(s)):
                return False
        p = par
    return True


MISE_EN_PAGE24 = ("position", "left", "top", "right", "bottom", "width", "height", "min-width", "min-height",
                  "max-width", "max-height", "margin-top", "margin-bottom", "margin-left", "margin-right",
                  "padding-top", "padding-bottom", "padding-left", "padding-right", "flex-grow", "flex-shrink",
                  "flex-basis", "align-self")


def envelopper24(fab, r):
    """v98 (Kinito, 13/11, v97 vue en italien : les mots des cases et les en-têtes des consignes individuelles restaient
    en ANGLAIS, les titres et la légende étaient traduits) : un interrupteur de FM (BindableSwitchElement) montre UN
    enfant choisi par son rang ; un texte posé directement dedans (texte_comp24 : une variante par taille du texte)
    voyait ses copies par langue, posées à côté, jamais montrées, et le mot de secours anglais restait. Le texte passe
    dans une boîte à sa place (son style de mise en page entier : place, taille, marges, souplesse), qu'il remplit ;
    ses copies se posent à côté de lui, dans la boîte. Rend la boîte"""
    t = fab.t
    sw = t.parent[r]
    rang = t.children(sw).index(r)
    fab.n += 1
    boite = fab.boite(sw, f"mot24-{fab.n}", index=rang)
    e = t.elem(r)
    valeurs = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    if valeurs:
        t.elem(boite)["m_RuleIndex"] = t.styles.add_rule(valeurs)
    fab.traverse(boite)
    base.deplacer(t, r, boite, 0)
    mise_en_page = {base.sm.PROPRIETES[k][0] for k in MISE_EN_PAGE24 if k in base.sm.PROPRIETES}
    e["m_RuleIndex"] = t.styles.add_rule([p for p in valeurs if p[0] not in mise_en_page]) if valeurs else -1
    t.styles.style(t, r, {"flex-grow": 1, "flex-shrink": 1})
    return boite


# ---------- v20 : la vue et la phase déclarées par l'onglet, la colonne de droite ----------
def composant_variables(t, nom):
    """le BindingVariablesComponent dont la déclaration (value-vars) nomme la variable nom"""
    return [r for r in t.walk() if t.elem(r).get("m_FullTypeName") == "SI.Bindable.BindingVariablesComponent"
            and any(f"{{{nom}}}" in (p.get("value") or "") for p in t.elem(r).get("m_Properties") or [])]


def oter_composant(t, r):
    """retire un composant posé par nous (et sa donnée, dans la liste des composants de son élément), comme
    kinito_consignes_essai.retirer_essai"""
    e = t.elem(r)
    ps = t.sd(t.parent[r])
    partis = {c["rid"] for c in ps.get("m_components") or []
              if ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == e["m_Id"]}
    ps["m_components"] = [c for c in ps["m_components"] if c["rid"] not in partis]
    t.tt["references"]["RefIds"] = [x for x in t.tt["references"]["RefIds"] if x["rid"] not in partis]
    for p in partis:
        t.refs.pop(p, None)
    t.remove(r)


def ote_vue_du_bloc(fab, racine):
    """v20 : la vue (base.VARIABLE) n'est plus déclarée par notre bloc mais par l'onglet (poser_ecran) : retirée de la
    déclaration posée par kinito_consignes_essai.bascule et rendue persistante par declarer()"""
    t = fab.t
    zone = t.parent[t.parent[racine]]
    var = next((k for k in t.children(zone) if k in composant_variables(t, V_ORDRE)), None)
    if var is None:
        raise ValueError("déclaration des variables du bloc (introuvable)")
    props = [p for p in t.elem(var).get("m_Properties") or [] if p.get("name") == "value-vars"]
    donnees = [r["data"] for r in t.refs.values() if r and "ValueVariables" in (r.get("data") or {})
               and r["data"].get("uxmlAssetId") == t.elem(var)["m_Id"]]
    vue = "{" + base.VARIABLE + "}{" + f"Int|{base.VUE_DEPART}|{persistant('vue')}".replace(",", "&#44;") + "},"
    if len(props) != 1 or len(donnees) != 1 or props[0]["value"].count(vue) != 1:
        raise ValueError("déclaration de la vue dans le bloc : forme inattendue (introuvable)")
    props[0]["value"] = props[0]["value"].replace(vue, "")
    avant = len(donnees[0]["ValueVariables"])
    donnees[0]["ValueVariables"] = [v for v in donnees[0]["ValueVariables"] if v.get("m_name") != base.VARIABLE]
    if len(donnees[0]["ValueVariables"]) != avant - 1:
        raise ValueError("déclaration de la vue dans le bloc : forme inattendue (introuvable)")


def attentes(t, retirer=False):
    """v20 : nos variables de l'onglet ajoutées aux paramètres attendus (BindingExpect) qui attendent déjà la variable
    de FM ATTENDU_MODELE, recopiée (données et déclaration écrite) ; retirer : ôtées. Rend le nombre d'endroits"""
    noms = [nom for nom, _ in VARIABLES_ECRAN]
    n = 0
    for r in t.walk():
        datas = [t.sd(r)] + [((t.refs.get(c["rid"]) or {}).get("data") or {}) for c in t.sd(r).get("m_components") or []]
        for d in datas:
            params = d.get("Parameters")
            if not params or not any(p.get("name") == ATTENDU_MODELE for p in params):
                continue
            d["Parameters"] = [p for p in params if p.get("name") not in noms]
            if not retirer:
                modele = next(p for p in d["Parameters"] if p.get("name") == ATTENDU_MODELE)
                for nom in noms:
                    p = copy.deepcopy(modele)
                    p["name"] = nom
                    d["Parameters"].append(p)
            n += 1
        e = t.elem(r)
        for p in e.get("m_Properties") or []:
            if p.get("name") == "params" and f"{ATTENDU_MODELE}:" in (p.get("value") or ""):
                morceaux = [m for m in p["value"].split(",") if m.split(":")[0] not in noms]
                if not retirer:
                    morceaux += [f"{nom}:invalid:False" for nom in noms]
                p["value"] = ",".join(morceaux)
    return n


def poser_ecran(o, src):
    """v20 : la vue et la phase FM24 déclarées par l'onglet (TacticalPlannerTeamInstructions), dans un composant à
    nous recopié de celui des cartes de chaleur (comme kinito_consignes_essai.bascule) : les trois blocs de sa grille
    les voient, comme « inpossession » de FM"""
    t = o[3]
    th = src.th
    zone = first(t, lambda r: typ(t, r) == "ComponentElement")
    if zone is None:
        return [f"{PARENT24} : élément racine (introuvable)"]
    rang = sum(1 for k in t.children(zone) if t.elem(k).get("m_FullTypeName", "").endswith("Component"))
    var = t.clone(src.variable, zone, rang, src=th)
    recaler_parent(t, var)
    n = 0
    for p in t.elem(var).get("m_Properties") or []:
        if p.get("name") == "value-vars":
            p["value"] = ",".join("{" + nom + "}{" + val.replace(",", "&#44;") + "}" for nom, val in VARIABLES_ECRAN)
            n += 1
    d = copy.deepcopy(th.refs[src.variable_sd])
    d["rid"] = t.new_rid()
    dd = d["data"]
    dd["uxmlAssetId"] = t.elem(var)["m_Id"]
    if n != 1 or len(dd.get("ValueVariables") or []) != 1:
        return [f"{PARENT24} : variable des cartes de chaleur : forme inattendue (introuvable)"]
    v0 = dd["ValueVariables"][0]
    dd["ValueVariables"] = []
    for nom, val in VARIABLES_ECRAN:
        v = copy.deepcopy(v0)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = nom, val
        dd["ValueVariables"].append(v)
    t.refs[d["rid"]] = d
    t.tt["references"]["RefIds"].append(d)
    zs = t.sd(zone)
    zs.setdefault("m_components", []).append({"rid": d["rid"]})
    zs["m_components_UxmlAttributeFlags"] = 1
    return [f"{PARENT24} : la vue et la phase FM24 déclarées pour les trois blocs de l'onglet"]


def retirer_ecran(o):
    t = o[3]
    rs = composant_variables(t, V_PHASE24)
    for r in rs:
        oter_composant(t, r)
    plein = ecran37.retirer(o)   # v54 : l'écran plein de la vue Terrain (toutes versions)
    return bool(rs) or plein


def poser_droite(o, src, tb):
    """v20 : dans la colonne de droite (PhasesTeamInstructionsBlock), un calque par-dessus son contenu (qui n'est pas
    touché) : un interrupteur sur la vue, vide sauf en vue FM24, où il montre les cartes des phases sur le fond de
    FM24. Les éléments simples viennent de notre bloc (tb) : la boîte (en-tête) et l'interrupteur de FM"""
    t = o[3]
    attente = first(t, lambda r: typ(t, r) == "BindingExpect")
    proto = first(tb, lambda r: tb.name(r) == "team-instruction-header")
    inter = first(tb, lambda r: typ(tb, r) == "BindableSwitchElement" and tb.name(r) == "possession-text-switch")
    if None in (attente, proto, inter):
        return [f"{DROITE24} : BindingExpect, ou éléments de notre bloc (introuvables)"]
    fab = base.Fab.__new__(base.Fab)
    fab.t, fab.src, fab.n, fab.defile = t, src, 0, None

    def simple(r_src, parent, nom, classes):
        c = t.clone(r_src, parent, src=tb)
        for k in list(t.children(c)):
            t.remove(k)
        t.styles.copy_from(tb.styles, t, c)
        recaler_parent(t, c)
        t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = list(classes), -1
        s = t.sd(c)
        s["name"], s["name_UxmlAttributeFlags"] = nom, 1
        return c
    calque = simple(proto, attente, NOM_DROITE, [])
    fab.proto = calque
    t.styles.style(t, calque, {**PLEIN, "flex-direction": "column"})
    fab.traverse(calque)
    sw = simple(inter, calque, f"{base.PREFIXE}-droite-vue", ["flex-grow-class"])
    t.sd(sw)["Binding"]["m_direct"]["Path"]["m_path"] = base.VARIABLE
    fab.inter = sw
    fab.traverse(sw)
    for j in range(VUE_FM24):   # tuiles, terrain : rien par-dessus la colonne de FM
        fab.traverse(fab.boite(sw, f"droite-rien-{j}", css={"width": 0, "height": 0}))
    col = fab.boite(sw, "droite-phases", css={
        "flex-grow": 1, "flex-direction": "column", "background-color": C24["cadre"], "padding-top": 8,
        "padding-bottom": 8, "padding-left": 8, "padding-right": 8, "overflow": "hidden",
        **cadre_css(0, C24["cadre"], 4)})
    cs = t.sd(col)   # les boîtes recopient le calque, qui laisse passer les clics : celle-ci les prend (la colonne de
    cs["pickingMode"], cs["pickingMode_UxmlAttributeFlags"] = 0, 1   # FM dessous ne doit pas en recevoir)
    # v97 : les cartes sous le conteneur de la langue du jeu
    env_lg = langue24(fab, col, "droite-langue", {"flex-grow": 1, "flex-direction": "column"})
    with _PaletteFM24():
        cartes_selon_taille24(fab, env_lg)   # v44 : une variante par taille du texte de FM (v20-v43 : une seule)
    n24 = traduire24(fab, env_lg)
    return [f"{DROITE24} : en vue FM24, les cartes des phases par-dessus la colonne de droite ({fab.n} éléments nommés) ; "
            f"langue du jeu (v97) : {n24} textes ; phrase entière au survol (v99) : "
            f"{getattr(fab, 'n_survols24', 0)} textes"]


def fab_indiv(t, src, tb, racine, nom):
    """la fabrique posée sur un modèle de la fenêtre des consignes individuelles : sa première boîte (nom) est une
    copie vidée de l'en-tête de notre bloc (tb), enfant de racine ; rend (fab, boîte)"""
    proto = first(tb, lambda r: tb.name(r) == "team-instruction-header")
    if proto is None:
        raise ValueError("boîte de notre bloc (introuvable)")
    fab = base.Fab.__new__(base.Fab)
    fab.t, fab.src, fab.n, fab.defile = t, src, 0, None
    c = t.clone(proto, racine, src=tb)
    for k in list(t.children(c)):
        t.remove(k)
    t.styles.copy_from(tb.styles, t, c)
    recaler_parent(t, c)
    t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = [], -1
    sd = t.sd(c)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
    fab.proto = c
    fab.inter = None   # v33 : premier_inter24 pose le premier
    fab.traverse(c)
    return fab, c


def evenement_ecrire24(source, destination):
    """v32 : les octets d'un événement « écrire la valeur de source dans destination » (la forme de celui de
    OppositionInstructionsPersonalisedInstructionsToggleCell : en-tête 01×5, longueur, n° d'action, 01, puis chaque
    chemin : longueur sur 4 octets, 01 01, longueur sur 1 octet, texte ; 00 00 à la fin)"""
    def chemin(c):
        b = c.encode("utf-8")
        if len(b) > 127:
            raise ValueError("chemin trop long pour un événement")
        corps = bytes([1, 1, len(b)]) + b
        return struct.pack("<i", len(corps)) + corps
    corps = bytes.fromhex("d90fe157") + b"\x01" + chemin(source) + chemin(destination) + b"\x00\x00"
    return list(b"\x01\x01\x01\x01\x01" + struct.pack("<i", len(corps)) + corps)


def bouton_ecrire_modele():
    """v32 : le bouton de FM qui porte l'événement « écrire une valeur » (et son arbre), ou (None, None)"""
    m = ouvrir(SOURCE_ECRIRE24, depart_original=True)
    if m is None:
        return None, None
    tm = m[3]
    for r in tm.walk():
        if typ(tm, r) == "SIButton":
            ev = ((tm.sd(r).get("Events") or {}).get("m_bytes")) or []
            if b"OppositionPlayerPersonalisedInstructionsUsed" in bytes(ev) and bytes(ev[9:13]) == bytes.fromhex("d90fe157"):
                return tm, r
    return None, None


def codes_element24(el):
    """v34 : [(groupe, codes montrés)] d'un élément de DISPOSITION24 (v36 : éléments en dictionnaires)"""
    k = el["type"]
    if k == "boutons":
        return [(el["g"], [c for c, _ in el["options"]])]
    if k == "jauge":
        return [(el["g"], list(el["ordre"]))]
    if k == "grille":
        return [(el["g"], [c for rang in el["rangs"] for c, _ in rang])]
    if k == "disque":
        return [(x[0], [x[1]]) for x in el["secteurs"]]
    return []


def options_indiv24():
    """v33 : les options des consignes individuelles (PlayerInstructionEntry de ui-staticdataentries) ; v34 :
    ValueError si DISPOSITION24 ne montre pas exactement les options du jeu ; v36 : rend {groupe : tous ses codes,
    « Normal » (0) compris, dans l'ordre du jeu} : le rang d'une option dans la liste de la consigne"""
    import UnityPy
    env = UnityPy.load(os.path.join(base.chemin_jeu.AA, "ui-staticdataentries_assets_all.bundle"))
    ordres = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            d = o.read_typetree()
        except Exception:
            continue
        for g in d.get("m_playerInstructionGroups") or []:
            ordres[g["m_groupID"]] = [e["m_instructionID"] for e in g["m_playerInstructionOptionEntries"]]
    montres = {}
    for _, _, sous in DISPOSITION24:
        for elements in sous:
            for el in elements:
                for g, codes in codes_element24(el):
                    montres.setdefault(g, set()).update(c for c in codes if c)
    if {g: {c for c in v if c} for g, v in ordres.items()} != montres:
        raise ValueError(f"options des consignes individuelles du jeu : {ordres}, montrées {montres} (introuvable)")
    return ordres


def fonction_element24():
    """v36 : la fonction de FM « élément n d'une liste » (BindListItemUsingIndexToDestination), celle qui met le
    premier élément dans firstItem (SOURCE_ELEMENT24), recopiée avec ses arguments"""
    m = ouvrir(SOURCE_ELEMENT24[0], depart_original=True)
    if m is None:
        raise ValueError(f"{SOURCE_ELEMENT24[0]} (introuvable)")
    tm = m[3]
    for r in tm.walk():
        for f in tm.sd(r).get("BindFunction") or [] if isinstance(tm.sd(r).get("BindFunction"), list) else []:
            if (f.get("m_target") or {}).get("m_guid", "").startswith("21ee6b43"):
                args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
                if len(chemins) == 2 and bytes(chemins[1][1]).endswith(SOURCE_ELEMENT24[1].encode()) \
                        and sum(1 for a in args if bytes(a[0]).endswith(b"Int32VisualArg")) == 1:
                    return copy.deepcopy(f)
    raise ValueError(f"fonction « élément d'une liste » de {SOURCE_ELEMENT24[0]} (introuvable)")


def setter_carte24(t):
    return first(t, lambda r: typ(t, r) == "BindingSetter" and t.name(r) == SETTER_CARTE24)


def carte_posee(oc):
    s = setter_carte24(oc[3])
    return s is not None and any(v.get("m_name") == V_INDIV24 for v in oc[3].sd(s).get("ValueVariables") or [])


def poser_carte(oc):
    """v33 : le choix FM 27 / FM24 (V_INDIV24, persistant) déclaré par la fiche, à la suite de « selectedtab »"""
    t = oc[3]
    s = setter_carte24(t)
    vs = (t.sd(s).get("ValueVariables") or []) if s is not None else []
    if not vs:
        raise ValueError(f"{CARTE_INDIV24} : variables de {SETTER_CARTE24} (introuvables)")
    vs = [v for v in vs if v.get("m_name") != V_INDIV24]
    v = copy.deepcopy(vs[0])
    v["m_name"], v["m_scopeValue"]["m_serializedData"] = V_INDIV24, VALEUR_INDIV24
    t.sd(s)["ValueVariables"] = vs + [v]
    return [f"{CARTE_INDIV24} : le choix FM 27 / FM24 déclaré pour les deux onglets"]


def retirer_carte(oc):
    s = setter_carte24(oc[3])
    vs = (oc[3].sd(s).get("ValueVariables") or []) if s is not None else []
    reste = [v for v in vs if v.get("m_name") != V_INDIV24]
    if len(reste) == len(vs):
        return False
    oc[3].sd(s)["ValueVariables"] = reste
    return True


def attendre_indiv24(t, retirer=False):
    """v33 : V_INDIV24 ajouté aux paramètres attendus de la racine du bloc (BindingExpect, ou son composant),
    recopié de ATTENDU_INDIV24 (comme attentes(), v20) ; retirer : ôté. Rend le nombre d'endroits"""
    r0 = t.children(t.tt["m_VisualTree"]["rid"])[0]
    n = 0
    for d in [t.sd(r0)] + [((t.refs.get(c["rid"]) or {}).get("data") or {}) for c in t.sd(r0).get("m_components") or []]:
        params = d.get("Parameters")
        if not params or not any(p.get("name") == ATTENDU_INDIV24 for p in params):
            continue
        d["Parameters"] = [p for p in params if p.get("name") != V_INDIV24]
        if not retirer:
            p = copy.deepcopy(next(p for p in d["Parameters"] if p.get("name") == ATTENDU_INDIV24))
            p["name"] = V_INDIV24
            d["Parameters"].append(p)
        n += 1
    for r in [r0] + t.children(r0):
        for p in t.elem(r).get("m_Properties") or []:
            if p.get("name") == "params" and f"{ATTENDU_INDIV24}:" in (p.get("value") or ""):
                morceaux = [m for m in p["value"].split(",") if m.split(":")[0] != V_INDIV24]
                if not retirer:
                    morceaux.append(f"{V_INDIV24}:invalid:False")
                p["value"] = ",".join(morceaux)
    return n


def inter24(fab, parent, nom, chemin, css):
    """v33 : un interrupteur de FM (fab.interrupteur) sans la règle de style de celui qu'il recopie, qui laisse
    passer les clics"""
    t = fab.t
    sw = fab.interrupteur(parent, nom, chemin)
    t.elem(sw)["m_RuleIndex"] = -1
    t.styles.style(t, sw, css)
    fab.traverse(sw)
    return sw


def premier_inter24(fab, tb, parent, nom, chemin, css):
    """v33 : le premier interrupteur du modèle, recopié de #possession-text-switch de notre bloc (tb) ; inter24 recopie
    ensuite celui-ci"""
    t = fab.t
    inter = first(tb, lambda r: typ(tb, r) == "BindableSwitchElement" and tb.name(r) == "possession-text-switch")
    if inter is None:
        raise ValueError("interrupteur de notre bloc (introuvable)")
    sw = t.clone(inter, parent, src=tb)
    for k in list(t.children(sw)):
        t.remove(k)
    t.styles.copy_from(tb.styles, t, sw)
    recaler_parent(t, sw)
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    fab._nom(sw, nom)
    t.sd(sw)["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    t.styles.style(t, sw, css)
    fab.traverse(sw)
    fab.inter = sw
    return sw


def vide24(fab, parent, nom):
    fab.traverse(fab.boite(parent, nom, css={"width": 0, "height": 0}))


def setter_vars24(fab, parent, nom, variables, css):
    """v33 : un BindingSetter de FM (celui de nom_option), vidé, qui déclare [(variable, valeur écrite)]"""
    t, src = fab.t, fab.src
    var = t.clone(src.setter, parent, src=src.ts)
    recaler_parent(t, var)
    for k in list(t.children(var)):
        t.remove(k)
    t.styles.copy_from(src.ts.styles, t, var)
    fab._nom(var, nom)
    vs = t.sd(var)
    modele = vs["ValueVariables"][0]
    out = []
    for n_, val in variables:
        v = copy.deepcopy(modele)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = n_, val
        out.append(v)
    vs["ValueVariables"], vs["ValueVariables_UxmlAttributeFlags"] = out, 1
    t.elem(var)["m_Classes"], t.elem(var)["m_RuleIndex"] = [], -1
    t.styles.style(t, var, css)
    fab.traverse(var)
    return var


def option24(fab, parent, nom, code, css):
    """v34 : un BindingSetter qui déclare l'option (playerinstructionoptionid)"""
    return setter_vars24(fab, parent, f"{nom}-o{code}", [("playerinstructionoptionid", f"Int|{code}|")], css)


def texte24(fab, parent, nom, mots, css, classe=CLASSE_TEXTE24, majuscules=False):
    """v36 : nos mots (français, anglais : la langue du skin), sans clic"""
    t = fab.t
    r = fab.texte_fixe(parent, nom, langue.texte(*mots), classe=classe, css=css)
    if not majuscules and "TextCase" in t.sd(r):
        t.sd(r)["TextCase"] = 0
    fab.traverse(r)
    return r


def texte_comp24(fab, parent, nom, mots, css, taille, conteneur, classe=CLASSE_TEXTE24):
    """v38 : nos mots à la taille du Normal à toute taille du texte de FM (selon_taille24 de v28 : le calcul de FM sur
    settings.TextScaling, une variante par taille, la police réduite de 100 / taille en Grand et Plus grand) ;
    conteneur : la place du calcul (PLEIN par-dessus une case, ou dans une rangée)"""
    t = fab.t
    tailles = list(TAILLES_TEXTE24)
    absolu = conteneur.get("position") == "absolute"
    interne = PLEIN if absolu else {"flex-shrink": 0}
    sel = fab._comparer(parent, f"{nom}-taille", [(f"kinitotaille{v}", v) for v in tailles], "settings.TextScaling")
    t.styles.style(t, sel, conteneur)
    fab.traverse(sel)

    def faire(par, facteur, k):
        texte24(fab, par, f"{nom}-{k}", mots, {**css, "font-size": round(taille * facteur, 2)}, classe=classe)

    def chaine(p, k):
        if k == len(tailles):
            faire(p, 1.0, "n")
            return
        sw = inter24(fab, p, f"{nom}-si{tailles[k]}", f"kinitotaille{tailles[k]}", interne)
        chaine(sw, k + 1)
        faire(sw, TAILLES_TEXTE24[tailles[k]], tailles[k])
    chaine(sel, 0)
    return sel


def titre_indiv24(fab, parent, nom, mots, sous=False, css=None):
    """v36 : un titre centré (bleu-vert, en capitales, FM24) ; sous : un sous-titre (petit, gris)"""
    if sous:
        return texte24(fab, parent, nom, mots, {"color": CI24["entete"], "-unity-text-align": "middle-center",
                                                "font-size": TAILLE_SOUS24, "margin-bottom": 2, "flex-shrink": 0,
                                                **(css or {})}, classe=CLASSE_PETIT24)
    return texte24(fab, parent, nom, mots, {"color": CI24["titre"], "-unity-text-align": "middle-center",
                                            "font-size": TAILLE_TITRE_INDIV24, "margin-bottom": 4, "flex-shrink": 0,
                                            **(css or {})},
                   classe=CLASSE_TITRE24, majuscules=True)


def liste_options24(fab, parent, nom, n, css, fn):
    """v36 : un BindingSetter qui met l'élément i de la liste de la consigne (CHEMIN_OPTIONS24 : celle de la fenêtre de
    FM 27, où chaque option porte « Disabled ») dans kinitoit<i> (variable de référence sans type, comme 26.x
    vacances)"""
    t = fab.t
    s = setter_vars24(fab, parent, nom, [], css)
    sd = t.sd(s)
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": f"kinitoit{i}"} for i in range(n)]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    fs = []
    for i in range(n):
        f = copy.deepcopy(fn)
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
        for a, c in zip(chemins, (CHEMIN_OPTIONS24, f"kinitoit{i}")):
            a[1] = bytes([1, len(c)]) + c.encode()
        next(a for a in args if bytes(a[0]).endswith(b"Int32VisualArg"))[1] = struct.pack("<i", i)
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        fs.append(f)
    sd["BindFunction"], sd["BindFunction_UxmlAttributeFlags"] = fs, 1
    return s


def groupe24(fab, parent, nom, g, avec, codes, css, ordres, fn, titre=None, sous=None, rangee=False):
    """v34 : une consigne : ses variables (le groupe, sa phase : celle de la consigne et pas celle de l'onglet, le
    code de « Normal »), puis (v36) la liste de ses options (drapeau « Disabled »), son titre, et la comparaison de FM
    qui dit, pour « Normal » et chaque code, si c'est l'option en cours. Rend l'élément où poser les options"""
    t = fab.t
    gs = setter_vars24(fab, parent, f"{nom}-g{g}", [("playerinstructiongroupid", f"Int|{g}|"),
                                                     ("inpossession", f"Bool|{1 if avec else 0}|"),
                                                     ("kinitopi0", "Int|0|")], css)
    absolu = css.get("position") == "absolute"
    dedans = PLEIN if absolu else {"flex-direction": "column", "flex-shrink": 0}
    ls = liste_options24(fab, gs, f"{nom}-g{g}-liste", len(ordres[g]), dedans, fn)
    if titre:
        titre_indiv24(fab, ls, f"{nom}-g{g}-titre", titre)
    if sous:
        titre_indiv24(fab, ls, f"{nom}-g{g}-sous", sous, sous=True)
    choix = fab._comparer(ls, f"{nom}-g{g}-choix", [("kinitostd", 0)] + [(f"kinitosel{c}", c) for c in codes if c],
                          CHEMIN_CONSIGNE_INDIV24)
    t.styles.style(t, choix, PLEIN if absolu else {"flex-direction": "row" if rangee else "column", "flex-shrink": 0})
    fab.traverse(choix)
    return choix


def dispo24(ordres, g, c):
    """v36 : le chemin du drapeau « indisponible » de l'option c (son rang dans la liste de la consigne)"""
    return f"kinitoit{ordres[g].index(c)}.Disabled"


def etats24(fab, parent, nom, code, dispo, faire, css):
    """v34 : les états d'une option, ceux de la légende de FM24 : réglable — choisie (vert ; un clic remet « Normal »),
    une autre choisie (rouge, « incompatible » ; un clic la remplace), sinon gris ; verrouillée par le rôle (cadenas
    de la consigne) ou (v36) impossible à ce poste / rôle (drapeau « Disabled ») — choisie (« fait partie du rôle »,
    vert clair), sinon « indisponible ». faire(parent, état, source) pose UN élément ; source : ce qu'écrit un clic
    (None : sans clic). « Normal » (code 0) n'a pas de rouge"""
    sel = "kinitostd" if code == 0 else f"kinitosel{code}"

    def libre(par, n_):
        if code == 0:
            faire(par, "neutre", "kinitopi0")
        else:
            autre = inter24(fab, par, f"{n_}-autre", "kinitostd", css)   # rang 0 : pas elle
            faire(autre, "contraire", "playerinstructionoptionid")
            faire(autre, "neutre", "playerinstructionoptionid")
        faire(par, "choisi", "kinitopi0")

    def bloque(par, n_):
        b = inter24(fab, par, n_, sel, css)
        faire(b, "indispo", None)
        faire(b, "role", None)
    verrou = inter24(fab, parent, f"{nom}-verrou", CHEMIN_VERROU24, css)
    if dispo:
        ouvert = inter24(fab, verrou, f"{nom}-dispo", dispo, css)   # rang 0 : la consigne est réglable
        libre(inter24(fab, ouvert, f"{nom}-libre", sel, css), nom)   # possible à ce poste
        bloque(ouvert, f"{nom}-impossible")                          # impossible à ce poste / rôle
    else:
        libre(inter24(fab, verrou, f"{nom}-libre", sel, css), nom)
    bloque(verrou, f"{nom}-bloque")                                  # rang 1 : verrouillée par le rôle


def voile24(fab, parent, nom, code, dispo, couleur):
    """v36 : par-dessus le nom d'une option, un voile quand elle est indisponible (son nom grisé, comme FM24)"""
    sel = "kinitostd" if code == 0 else f"kinitosel{code}"

    def voile(par, n_):
        fab.boite(par, n_, css={**PLEIN, "background-color": couleur})
    verrou = inter24(fab, parent, f"{nom}-verrou", CHEMIN_VERROU24, PLEIN)
    if dispo:
        d = inter24(fab, verrou, f"{nom}-dispo", dispo, PLEIN)
        vide24(fab, d, f"{nom}-possible")
        s2 = inter24(fab, d, f"{nom}-impossible", sel, PLEIN)
        voile(s2, f"{nom}-impossible-voile")
        vide24(fab, s2, f"{nom}-impossible-choisie")
    else:
        vide24(fab, verrou, f"{nom}-libre")
    s1 = inter24(fab, verrou, f"{nom}-bloque", sel, PLEIN)
    voile(s1, f"{nom}-bloque-voile")
    vide24(fab, s1, f"{nom}-bloque-choisie")


def piece24(fab, par, nom, source, modele, style, bulle=None):
    """v36 : le bouton de FM qui écrit source dans la consigne (v32), ou une boîte sans clic (source None) ; v38 :
    bulle : l'infobulle de FM (celle de RoleLabelwIcon, posée dans l'élément même comme v16), sur ce chemin"""
    t = fab.t
    if source is not None:
        tm, rb = modele
        b = t.clone(rb, par, src=tm)
        for k in list(t.children(b)):
            t.remove(k)
        t.styles.copy_from(tm.styles, t, b)
        recaler_parent(t, b)
        t.elem(b)["m_Classes"], t.elem(b)["m_RuleIndex"] = [], -1
        fab._nom(b, nom)
        sd = t.sd(b)
        sd["Events"]["m_bytes"] = evenement_ecrire24(source, CHEMIN_CONSIGNE_INDIV24)
        sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 0, 1
    else:
        b = fab.boite(par, nom)
        if bulle:   # le survol doit l'atteindre (une option verrouillée a aussi son explication)
            t.sd(b)["pickingMode"], t.sd(b)["pickingMode_UxmlAttributeFlags"] = 0, 1
    t.styles.style(t, b, {"justify-content": "center", "align-items": "center", "overflow": "hidden", **SANS_MARGE24,
                          **style})
    if bulle:
        src = fab.src
        bu = t.clone(src.bulle, b, src=src.tu)
        t.styles.copy_from(src.tu.styles, t, bu)
        recaler_parent(t, bu)
        fab._nom(bu, f"{nom}-bulle")
        base.texte_lie(t, t.children(bu)[0], bulle, "explication")
    return b


def visuel24(fab, par, nom, etat, source, modele, css, plein=False, bulle=CHEMIN_DESC24):
    """v34 : une option FM24 dans un état : encadrée (bouton) ou pleine (secteur, case) ; v38 : son infobulle"""
    style = dict(css)
    if plein:
        style = {**{f"border-{c}-width": 0 for c in ("top", "bottom", "left", "right")}, **style}
        style["background-color"] = PLEIN24[etat]
    else:
        style.update({"background-color": CI24["bouton"], **cadre_css(2, LIGNE24[etat], 3)})
    return piece24(fab, par, nom, source, modele, style, bulle=bulle)


def option_case24(fab, choix, n, g, c, mots, dispo, modele, css, plein, hauteur, taille):
    """v36 : une option en case (bouton encadré ou case pleine) : ses états, son nom par-dessus (nos mots), le voile
    quand elle est indisponible ; v38 : le nom à la taille du Normal (texte_comp24), une infobulle par état"""
    o = option24(fab, choix, n, c, {"flex-direction": "column", "flex-shrink": 0, **css})

    def faire(par, etat, source):
        visuel24(fab, par, f"{n}-o{c}-{etat}", etat, source, modele, {"height": hauteur, "flex-shrink": 0,
                                                                         **({"flex-grow": 1} if plein else {})},
                 plein=plein)
    etats24(fab, o, f"{n}-o{c}", c, dispo, faire, {"flex-shrink": 0})
    texte_comp24(fab, o, f"{n}-o{c}-mot", mots, {**PLEIN, "-unity-text-align": "middle-center", "white-space": "normal",
                                                  "color": CI24["texte"], "padding-left": 3, "padding-right": 3},
                 taille, PLEIN)
    voile24(fab, o, f"{n}-o{c}-voile", c, dispo, CI24["voile-case" if plein else "voile"])


def boutons24(fab, col, n, el, avec, modele, ordres, fn, marge):
    """v34 : une consigne en boutons encadrés (FM24), l'un sous l'autre ou (rangee) côte à côte"""
    g, rangee = el["g"], el.get("rangee", False)
    codes = [c for c, _ in el["options"]]
    choix = groupe24(fab, col, n, g, avec, codes, {"flex-direction": "column", "flex-shrink": 0, "margin-top": marge},
                     ordres, fn, titre=el.get("titre"), sous=el.get("sous"), rangee=rangee)
    for i, (c, mots) in enumerate(el["options"]):
        css = ({"flex-grow": 1, "flex-basis": 0, **({"margin-left": 4} if i else {})} if rangee else
               ({"margin-top": ECART_OPTION_INDIV24} if i else {}))
        option_case24(fab, choix, f"{n}-g{g}", g, c, mots, dispo24(ordres, g, c), modele, css, False,
                      el.get("hauteur", H_BOUTON_INDIV24), TAILLE_BOUTON24)


def jauge24(fab, col, n, el, avec, modele, ordres, fn, marge):
    """v36 (Kinito : « une jauge pleine en ligne : on allume tout ce qui est avant ») : trois crans (gauche, « Normal »,
    droite) ; allumés jusqu'au cran choisi ; un clic sur un cran le choisit. Verrouillée par le rôle : vert clair,
    sans clic. v37 : toute la largeur, sans espace. v38 (Kinito : « Plus / Moins illisibles ») : ses deux bouts écrits
    de part et d'autre, sur la même ligne, à la taille du Normal ; une infobulle par cran"""
    g = el["g"]
    a, _, b = el["ordre"]
    choix = groupe24(fab, col, n, g, avec, (a, b), {"flex-direction": "column", "flex-shrink": 0, "margin-top": marge},
                     ordres, fn, titre=el.get("titre"))
    m = f"{n}-g{g}"
    bouts = fab.boite(choix, f"{m}-bouts", css={"flex-direction": "row", "align-items": "flex-end", "height": 16,
                                                "flex-shrink": 0})
    bout = {"color": CI24["entete"], "flex-shrink": 0, "white-space": "nowrap"}
    # v39 (Kinito) : au-dessus de la jauge, à ses deux bouts ; v41 (Kinito : « mets Normal au milieu, sur la ligne de
    # Moins / Plus ») : trois tiers, comme les trois crans dessous, chaque mot calé au-dessus du sien
    for j, (mots, place) in enumerate(((el["bouts"][0], "middle-left"),
                                       (el.get("milieu", MOT_NORMAL24), "middle-center"),
                                       (el["bouts"][1], "middle-right"))):
        texte_comp24(fab, bouts, f"{m}-bout{j}", mots, {**bout, "-unity-text-align": place}, TAILLE_BOUT24,
                     {"flex-grow": 1, "flex-basis": 0}, classe=CLASSE_PETIT24)
    barre = fab.boite(choix, f"{m}-jauge", css={"flex-direction": "row", "height": H_JAUGE24, "flex-shrink": 0,
                                                "margin-top": 1})
    for k, (c, cond, inverse) in enumerate(((a, None, False), (0, f"kinitosel{a}", True), (b, f"kinitosel{b}", False))):
        o = option24(fab, barre, f"{m}-cran", c, {"flex-grow": 1, "flex-basis": 0, "flex-direction": "column"})
        coins = ({"border-top-left-radius": 3, "border-bottom-left-radius": 3} if k == 0 else
                 {"border-top-right-radius": 3, "border-bottom-right-radius": 3} if k == 2 else {})

        def cran(par, nom_, couleur, source, coins=coins):
            piece24(fab, par, nom_, source, modele, {"flex-grow": 1, "background-color": couleur, **coins,
                                                     **{f"border-{c}-width": 0 for c in ("top", "bottom", "left",
                                                                                          "right")}},
                    bulle=CHEMIN_DESC24)
        verrou = inter24(fab, o, f"{m}-cran{c}-verrou", CHEMIN_VERROU24, {"flex-grow": 1})
        for rang, (allume, eteint, source) in enumerate(((JAUGE24["allume"], JAUGE24["eteint"],
                                                          "playerinstructionoptionid"),
                                                         (JAUGE24["role"], JAUGE24["eteint-bloque"], None))):
            if cond is None:   # le premier cran : toujours allumé
                cran(verrou, f"{m}-cran{c}-{rang}", allume, source)
                continue
            sw = inter24(fab, verrou, f"{m}-cran{c}-si{rang}", cond, {"flex-grow": 1})
            cran(sw, f"{m}-cran{c}-{rang}-non", allume if inverse else eteint, source)   # rang 0 : faux
            cran(sw, f"{m}-cran{c}-{rang}-oui", eteint if inverse else allume, source)   # rang 1 : vrai


def grille24(fab, col, n, el, avec, modele, ordres, fn, marge):
    """v34 : une consigne en cases pleines (FM24 : « Centrer vers ») ; v36 : en rangées régulières, le but en haut ou
    l'arc de la surface en bas ; v38 (Kinito : « colle les boutons », « vire le fond derrière ») : sans fond, les cases
    collées (un filet de 1 px de la couleur de la vue entre elles), une hauteur par rangée"""
    g = el["g"]
    codes = [c for rang in el["rangs"] for c, _ in rang]
    choix = groupe24(fab, col, n, g, avec, codes, {"flex-direction": "column", "flex-shrink": 0,
                                                    "margin-top": el.get("marge", marge)},
                     ordres, fn, titre=el.get("titre"), sous=el.get("sous"))
    m = f"{n}-g{g}"
    zone = fab.boite(choix, f"{m}-grille", css={"flex-direction": "column", "flex-shrink": 0})
    if el.get("decor") == "but":
        fab.boite(zone, f"{m}-but", css={"height": 3, "width": pc(36), "align-self": "center", "flex-shrink": 0,
                                         "margin-bottom": 4, "background-color": CI24["but"]})
    hauteurs = el.get("hauteurs") or [H_CASE24] * len(el["rangs"])
    for j, rang in enumerate(el["rangs"]):
        ligne = fab.boite(zone, f"{m}-rang{j}", css={"flex-direction": "row", "flex-shrink": 0})   # v39 : collées
        for i, (c, mots) in enumerate(rang):
            option_case24(fab, ligne, m, g, c, mots, dispo24(ordres, g, c), modele,
                          {"flex-grow": 1, "flex-basis": 0},
                          True, hauteurs[j], el.get("taille", TAILLE_CASE24))   # v41 : une taille par grille
    if el.get("decor") == "arc":   # FM24 : l'arc de la surface sous la grille
        arc = fab.boite(zone, f"{m}-arc", css={"height": 10, "flex-shrink": 0, "overflow": "hidden",
                                               "align-items": "center"})
        fab.boite(arc, f"{m}-arc-rond", css={"width": 44, "height": 44, "margin-top": -32, "flex-shrink": 0,
                                             **cadre_css(1, CI24["ligne-schema"], 22)})


def forme24(forme, R):
    """v36 : une couche d'un disque (2R × 2R) : le cercle entier, sa moitié droite ou un quart du haut (rectangles :
    leurs coins hors du cercle sont cachés par l'anneau), ou un carré tourné de 45°, sa pointe au centre, ses deux
    coins latéraux sur le cercle (« haut », « bas ») : il couvre exactement le quart du cercle de sa direction"""
    if forme == "disque":
        return {"position": "absolute", "left": 0, "top": 0, "width": 2 * R, "height": 2 * R,
                **{f"border-{c}-radius": R for c in ("top-left", "top-right", "bottom-left", "bottom-right")}}
    if forme == "moitie-droite":
        return {"position": "absolute", "left": R, "top": 0, "width": R, "height": 2 * R}
    if forme == "quart-hg":
        return {"position": "absolute", "left": 0, "top": 0, "width": R, "height": R}
    if forme == "quart-hd":
        return {"position": "absolute", "left": R, "top": 0, "width": R, "height": R}
    if forme in ("haut", "bas"):
        d = R / math.sqrt(2)   # du centre du carré à sa pointe
        top = R - d - R / 2 if forme == "haut" else R + d - R / 2
        return {"position": "absolute", "left": R / 2, "top": round(top, 2), "width": R, "height": R,
                "rotate": {"unit": 5, "value": 45.0}}
    raise ValueError(f"forme de secteur inconnue : {forme}")


def fleche_indiv24(fab, par, nom, angle, R):
    """v36 (Kinito : « une flèche qui pointe la case choisie, comme FM24 ») : du joueur vers le secteur, en
    pointillés blancs, avec sa pointe (un coin à deux bords, comme les flèches de 26.13)"""
    a = math.radians(angle)
    ux, uy = math.sin(a), -math.cos(a)
    col = CI24["fleche"]
    for k, (d0, d1) in enumerate(((0.13, 0.21), (0.26, 0.34))):
        d, lg = (d0 + d1) / 2 * R, (d1 - d0) * R
        fab.boite(par, f"{nom}-trait{k}", css={"position": "absolute", "left": round(R + d * ux - 1, 2),
                                               "top": round(R + d * uy - lg / 2, 2), "width": 2, "height": round(lg, 2),
                                               "background-color": col, "rotate": {"unit": 5, "value": float(angle)}})
    s, d = 7, 0.42 * R
    fab.boite(par, f"{nom}-pointe", css={"position": "absolute", "left": round(R + d * ux - s / 2, 2),
                                         "top": round(R + d * uy - s / 2, 2), "width": s, "height": s,
                                         "border-top-width": 2, "border-right-width": 2, "border-top-color": col,
                                         "border-right-color": col,
                                         "rotate": {"unit": 5, "value": float(angle - 45)}})


def disque24(fab, col, n, el, avec, modele, ordres, fn, marge):
    """v34 : l'éventail ou le camembert de FM24 ; v36 : peint par couches exactes (forme24), l'anneau de la couleur du
    fond qui cache ce qui dépasse, le rond du terrain, les noms (nos mots), les flèches des secteurs choisis, le
    joueur (point rouge) au centre"""
    R = R_DISQUE24
    if el.get("titre"):
        titre_indiv24(fab, col, f"{n}-titre", el["titre"], css={"margin-top": marge})
    panneau = fab.boite(col, f"{n}-panneau", css={
        "height": 2 * R + 4, "flex-shrink": 0, "margin-top": 0 if el.get("titre") else marge, "overflow": "hidden",
        "align-items": "center", "justify-content": "center"})   # v37 : sans fond (Kinito : « juste le rond »)
    disque = fab.boite(panneau, f"{n}-disque", css={"width": 2 * R, "height": 2 * R, "flex-shrink": 0})
    for g, c, forme, angle, mots, _ in el["secteurs"]:
        choix = groupe24(fab, disque, f"{n}-{forme}", g, avec, (c,), PLEIN, ordres, fn)
        o = option24(fab, choix, f"{n}-{forme}", c, PLEIN)

        def faire(par, etat, source, forme=forme, angle=angle):
            if angle is not None and etat in ("choisi", "role"):
                cont = fab.boite(par, f"{n}-{forme}-{etat}-avec-fleche", css=PLEIN)
                visuel24(fab, cont, f"{n}-{forme}-{etat}", etat, source, modele, forme24(forme, R), plein=True)   # v38 : infobulle
                fleche_indiv24(fab, cont, f"{n}-{forme}-{etat}-fleche", angle, R)
            else:
                visuel24(fab, par, f"{n}-{forme}-{etat}", etat, source, modele, forme24(forme, R), plein=True)
        etats24(fab, o, f"{n}-{forme}", c, dispo24(ordres, g, c), faire, PLEIN)
    w = MASQUE24 * R
    fab.boite(disque, f"{n}-masque", css={"position": "absolute", "left": -w, "top": -w, "width": 2 * (R + w),
                                          "height": 2 * (R + w), **cadre_css(w, CI24["fond"], R + w)})
    for g, c, forme, _, mots, (dx, dy, larg) in el["secteurs"]:   # v38 : à la taille du Normal (texte_comp24)
        wl, hl = larg * R, 0.5 * R
        texte_comp24(fab, disque, f"{n}-{forme}-mot", mots, {
            "position": "absolute", "left": round(R + dx * R - wl / 2, 2), "top": round(R + dy * R - hl / 2, 2),
            "width": round(wl, 2), "height": round(hl, 2), "color": CI24["texte"], "-unity-text-align": "middle-center",
            "white-space": "normal"}, TAILLE_SECTEUR24, PLEIN)
    fab.boite(disque, f"{n}-joueur", css={"position": "absolute", "left": R - 5, "top": R - 5, "width": 10,
                                          "height": 10, "background-color": CI24["point"],
                                          **cadre_css(1, (0.15, 0.0, 0.0, 1.0), 5)})


def legende_indiv24(fab, parent, nom):
    """v34 : en bas de la première colonne, la légende de FM24"""
    fab.boite(parent, f"{nom}-legende-espace", css={"flex-grow": 1})
    for i, (etat, mots) in enumerate(LEGENDE_INDIV24):
        ligne = fab.boite(parent, f"{nom}-legende-{i}", css={"flex-direction": "row", "align-items": "center",
                                                             "flex-shrink": 0, "margin-top": 3})
        couleur = LIGNE24[etat] if etat == "indispo" else PLEIN24[etat]
        fab.boite(ligne, f"{nom}-legende-{i}-point", css={"width": 10, "height": 10, "flex-shrink": 0, "margin-right": 6,
                                                          "background-color": couleur, **cadre_css(0, couleur, 5)})
        texte24(fab, ligne, f"{nom}-legende-{i}-mots", mots, {"color": CI24["texte"], "font-size": TAILLE_SOUS24,
                                                              "flex-shrink": 0}, classe=CLASSE_PETIT24)


def vue_indiv24(fab, parent, nom, css, modele, ordres, fn):
    """v33 : la vue FM24 des consignes individuelles, qui prend les clics (les tuiles de FM 27, dessous, n'en
    reçoivent pas) ; v34 : les colonnes de DISPOSITION24 ; v36 : sur le fond de FM 27, en-têtes et titres centrés"""
    t = fab.t
    racine = fab.boite(parent, nom, css={
        "flex-direction": "row", "background-color": CI24["fond"], "padding-left": 10, "padding-right": 10,
        "padding-top": 8, "padding-bottom": 8, "overflow": "hidden", **css})
    t.sd(racine)["pickingMode"], t.sd(racine)["pickingMode_UxmlAttributeFlags"] = 0, 1
    # v97 : les colonnes sous le conteneur de la langue du jeu (une rangée qui remplit la vue)
    rangee_langue = langue24(fab, racine, f"{nom}-langue", {"flex-grow": 1, "flex-direction": "row"})
    for j, (mots, avec, sous) in enumerate(DISPOSITION24):
        col = fab.boite(rangee_langue, f"{nom}-c{j}", css={
            "flex-grow": POIDS_COLONNES24[j], "flex-basis": 0, "flex-direction": "column",
            **({"margin-left": 10, "padding-left": 10, "border-left-width": 1, "border-left-color": CI24["filet"]}
               if j else {})})
        texte_comp24(fab, col, f"{nom}-c{j}-entete", mots, {"color": CI24["entete"], "-unity-text-align": "middle-center",
                                                            "white-space": "nowrap", "flex-shrink": 0},
                     TAILLE_ENTETE24, {"flex-shrink": 0, "margin-bottom": 3}, classe=CLASSE_TITRE24)   # v39 : une ligne
        rangee = fab.boite(col, f"{nom}-c{j}-rangee", css={"flex-grow": 1, "flex-direction": "row"})
        for k, elements in enumerate(sous):
            sc = fab.boite(rangee, f"{nom}-c{j}-{k}", css={"flex-grow": 1, "flex-basis": 0, "flex-direction": "column",
                                                           **({"margin-left": 10} if k else {})})
            for i, el in enumerate(elements):
                n = f"{nom}-c{j}{k}e{i}"
                marge = el.get("marge", 0 if i == 0 else ECART_GROUPE_INDIV24)
                if el["type"] == "titre":
                    titre_indiv24(fab, sc, n, el["mots"], css={"margin-top": marge})
                elif el["type"] == "boutons":
                    boutons24(fab, sc, n, el, avec, modele, ordres, fn, marge)
                elif el["type"] == "jauge":
                    jauge24(fab, sc, n, el, avec, modele, ordres, fn, marge)
                elif el["type"] == "disque":
                    disque24(fab, sc, n, el, avec, modele, ordres, fn, marge)
                else:
                    grille24(fab, sc, n, el, avec, modele, ordres, fn, marge)
            if j == 0:
                legende_indiv24(fab, sc, nom)
    traduire24(fab, rangee_langue)   # v97
    return racine


def bascule_indiv24(fab, parent):
    """v33 : le bouton FM 27 / FM24, fait des boutons segmentés des cartes de chaleur de FM (comme « Tuiles / Terrain »
    de 26.13) ; v38 (Kinito : « un seul bouton switch ») : UN bouton, celui du mode en cours (le bouton « allumé » de FM,
    coins arrondis des deux côtés) ; un clic passe à l'autre mode (interrupteur de FM sur V_INDIV24)"""
    t, src = fab.t, fab.src
    th = src.th
    sw = inter24(fab, parent, "indiv-bascule", V_INDIV24, {"flex-shrink": 0})
    for valeur, const, drapeau, mot, nom in ((0, "const.One", 1, TEXTE_FM27_INDIV24, "fm27"),
                                             (1, "const.Zero", 0, TEXTE_FM24, "fm24")):
        seg = t.clone(src.segments, sw, src=th)
        t.styles.copy_from(th.styles, t, seg)
        recaler_parent(t, seg)
        fab._nom(seg, f"indiv-bascule-{nom}")
        reglages = t.children(seg)
        if len(reglages) != 3 or any(typ(t, r) != "SIStyleSetter" for r in reglages):
            raise ValueError("boutons segmentés des cartes de chaleur : forme inattendue (introuvable)")
        t.remove(reglages[2])
        t.remove(reglages[1])
        reglage = reglages[0]
        fab._nom(reglage, f"indiv-allume-{nom}")
        rs = t.sd(reglage)
        args = decode_args(rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins = entiers = 0
        for a in args:
            if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]"):
                if bytes(a[1]) != bytes([1, 14]) + b"possessionmode":
                    raise ValueError("réglage d'un bouton segmenté : chemin inattendu (introuvable)")
                a[1] = bytes([1, len(V_INDIV24)]) + V_INDIV24.encode()
                chemins += 1
            elif bytes(a[0]).endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", valeur)   # allumé : c'est le mode en cours dans cette branche
                entiers += 1
        if (chemins, entiers) != (1, 1):
            raise ValueError("réglage d'un bouton segmenté : arguments inattendus (introuvable)")
        rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        bouton = t.children(reglage)[0]
        fab._nom(bouton, f"indiv-bouton-{nom}")
        t.sd(bouton)["Events"] = {"m_bytes": liste([copier(const, V_INDIV24, drapeau)])}
        t.styles.style(t, bouton, {f"border-{c}-radius": 4 for c in ("top-left", "top-right", "bottom-left",
                                                                     "bottom-right")})
        for k in list(t.children(bouton)):
            if t.name(k) == "controllers-keyboard-container":   # raccourci clavier de FM : pas le nôtre
                t.remove(k)
        texte = next((k for k in t.children(bouton) if typ(t, k) == "SIText"), None)
        if texte is None:
            raise ValueError("texte d'un bouton segmenté (introuvable)")
        t.elem(texte)["m_Classes"] = [c for c in t.elem(texte)["m_Classes"] if c != "margin-right-global-gap-regular"]
        fab._nom(texte, f"indiv-texte-{nom}")
        ts = t.sd(texte)
        ts.update(text=mot, text_UxmlAttributeFlags=1, DebugDisplay=mot)   # texte fixe (recette de 26.4)
        ts["TextBinding"]["m_kind"] = 0
        ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        base.fonction_vide(ts["TextBinding"]["m_visualFunction"])
    return sw


def poser_extra24(o, src, tb):
    """v40 (Kinito : « dans la ligne du haut, entre Consigne modifiée et Annuler sél., avec la DA d'Annuler sél. ») :
    le bouton FM 27 / FM24 dans TacticsPlayerInstructionsExtraButtons (la ligne des onglets de la fenêtre), juste
    avant « Annuler sél. » : le bouton gris de FM de ce dernier recopié, deux fois (un interrupteur sur V_INDIV24 :
    le mode en cours ; un clic passe à l'autre). La ligne attend V_INDIV24 (paramètre recopié de « tactic »).
    v41 (Kinito) : les DEUX boutons à chaque fois, collés, le choisi en violet (CLASSE_BASCULE_CHOISI24), l'autre gris
    (CLASSE_BASCULE_GRIS24) ; l'interrupteur choisit lequel est allumé, un clic sur l'un écrit son mode"""
    t = o[3]
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    if typ(t, racine) != "BindingExpect":
        return [f"{EXTRA24} : racine (introuvable)"]
    m = ouvrir(SOURCE_ANNULER24, depart_original=True)
    tm = m[3] if m else None
    rb = first(tm, lambda r: typ(tm, r) == "SIButton" and tm.name(r) == "button") if tm else None
    if rb is None:
        raise ValueError(f"bouton de {SOURCE_ANNULER24} (introuvable)")
    i = next((k for k, r in enumerate(t.children(racine))
              if t.elem(r).get("m_TemplateAlias") == SOURCE_ANNULER24), None)
    if i is None:
        raise ValueError(f"{SOURCE_ANNULER24} dans {EXTRA24} (introuvable)")
    fab, c = fab_indiv(t, src, tb, racine, NOM_EXTRA)
    base.deplacer(t, c, racine, i)   # juste avant « Annuler sél. »
    t.styles.style(t, c, {"flex-direction": "row", "flex-shrink": 0, "justify-content": "center",
                          "align-items": "center", "margin-right": 8})
    sw = premier_inter24(fab, tb, c, "indiv-annuler-sw", V_INDIV24, {"flex-shrink": 0})
    for rang in (0, 1):   # rang 0 : FM 27 en cours (V_INDIV24 = 0) ; rang 1 : FM24 en cours
        paire = fab.boite(sw, f"indiv-annuler-paire{rang}", css={"flex-direction": "row", "flex-shrink": 0,
                                                                "align-items": "center"})
        fab.traverse(paire)
        # v48 (Kinito) : FM24 AVANT FM 27 (k = place dans la paire ; drapeau = la valeur de V_INDIV24 du bouton)
        for k, (const, drapeau, mot, nom) in enumerate((("const.One", 1, TEXTE_FM24, "fm24"),
                                                        ("const.Zero", 0, TEXTE_FM27_INDIV24, "fm27"))):
            choisi, cote = drapeau == rang, ("left", "right")[k]
            b = t.clone(rb, paire, src=tm)
            t.styles.copy_from(tm.styles, t, b)
            recaler_parent(t, b)
            t.elem(b)["m_RuleIndex"] = -1   # v41 : sans le style intégré d'« Annuler sél. » (display: none, que
            #                                 l'interrupteur de la v40 remettait ; ici rien ne le remettrait)
            t.elem(b)["m_Classes"] = [CLASSE_BASCULE_CHOISI24.format(("leading", "trailing")[k]) if choisi
                                      else CLASSE_BASCULE_GRIS24]
            fab._nom(b, f"indiv-annuler-{nom}-{rang}")
            t.sd(b)["Events"] = {"m_bytes": liste([copier(const, V_INDIV24, drapeau)])}
            t.styles.style(t, b, {
                **SANS_MARGE24, "height": H_BASCULE24, "width": L_BASCULE24, "flex-shrink": 0,
                "justify-content": "center", "align-items": "center",
                **{f"border-{c}-width": 1 for c in ("top", "bottom", "right")}, "border-left-width": 0 if k else 1,
                **{f"border-{h}-{c}-radius": 4 if c == cote else 0 for h in ("top", "bottom") for c in ("left", "right")}})
            texte = first(t, lambda r: typ(t, r) == "SIText", b)
            if texte is None:
                raise ValueError("texte du bouton « Annuler sél. » (introuvable)")
            fab._nom(texte, f"indiv-annuler-texte-{nom}-{rang}")
            ts = t.sd(texte)
            ts.update(text=mot, text_UxmlAttributeFlags=1, DebugDisplay=mot)
            ts["TextBinding"]["m_kind"] = 0
            ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            base.fonction_vide(ts["TextBinding"]["m_visualFunction"])
    attendre_extra24(t)
    return [f"{EXTRA24} : boutons FM 27 et FM24 avant « Annuler sél. », le choisi en violet"]


def attendre_extra24(t, retirer=False):
    """v40 : V_INDIV24 dans les paramètres attendus de la ligne du haut (recopié de « tactic », type effacé)"""
    r0 = t.children(t.tt["m_VisualTree"]["rid"])[0]
    d = t.sd(r0)
    params = d.get("Parameters") or []
    reste = [x for x in params if x.get("name") != V_INDIV24]
    touche = len(reste) != len(params)
    if not retirer:
        modele = next((x for x in reste if x.get("name") == "tactic"), None)
        if modele is None:
            raise ValueError(f"paramètre « tactic » de {EXTRA24} (introuvable)")
        x = copy.deepcopy(modele)
        x["name"], x["type"] = V_INDIV24, {"id": 0}
        reste.append(x)
        touche = True
    d["Parameters"] = reste
    return touche


def poser_bascules24(fab, t):
    """v36 (Kinito : « à droite de Sélectionné actuellement, au-dessus des étoiles ») : le bouton FM 27 / FM24 dans le
    bloc de gauche, à droite de la première ligne de #HasPlayer (« Sélectionné actuellement ») et de #NoPlayer (aucun
    joueur au poste) : il suit cette ligne quelle que soit la taille du texte. v34 (barre des onglets) : coupé par la
    grille ; v35 : coin en bas à droite"""
    sw = first(t, lambda x: t.name(x) == "HasPlayerSwitch")   # v37 : le premier #HasPlayer du bloc est le bouton
    for cible in ("HasPlayer", "NoPlayer"):                   # « Joueur » de « Attribuer à » (vu en jeu en v36)
        r = next((k for k in t.children(sw) if t.name(k) == cible), None) if sw is not None else None
        if r is None:
            raise ValueError(f"#{cible} sous #HasPlayerSwitch du bloc de gauche (introuvable)")
        b = fab.boite(r, f"indiv-v{VERSION}-bascule-{cible.lower()}",
                      css={"position": "absolute", "right": 0, "top": HAUT_BASCULE24}, index=1)
        recaler_parent(t, b)
        fab.traverse(b)
        bascule_indiv24(fab, b)


def poser_indiv(o, src, tb, modele, ordres, fn):
    """v33 : dans le bloc de gauche de la fenêtre des consignes individuelles (INDIV24) : le bouton FM 27 / FM24 (les
    deux onglets) ; sans le ballon et en FM24, la vue FM24 à la place des tuiles (v51 : ZONE_INDIV24). Avec le ballon, la
    vue part de la dernière tuile (poser_indiv_tuile). v34 : bouton dans la barre des onglets (invisible : la grille de
    la fenêtre coupe ce qui dépasse au-dessus d'elle) ; v35 : coin en bas à droite du bloc ; v36 : à droite de
    « Sélectionné actuellement » (poser_bascules24)"""
    t = o[3]
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    if typ(t, racine) != "ComponentElement":
        return [f"{INDIV24} : racine (introuvable)"]
    fab, c = fab_indiv(t, src, tb, racine, NOM_INDIV)
    # v51 : tout le bloc, bord compris (le bord de FM annulé par une marge égale, arrondie au pixel comme lui)
    t.styles.style(t, c, {**PLEIN, **{f"margin-{k}": -BORD_BLOC24 for k in ("left", "top", "right", "bottom")}})
    pos = premier_inter24(fab, tb, c, "indiv-possession", "inpossession", PLEIN)
    vue = inter24(fab, pos, "indiv-vue-sans", V_INDIV24, PLEIN)   # rang 0 : sans le ballon
    vide24(fab, vue, "indiv-fm27-sans")                            # rang 0 : les tuiles de FM 27
    # rang 1 : FM24 ; v51 : dans la zone exacte de la grille (v33-v50 : CADRE_INDIV24, mesuré sur captures)
    zone = fab.boite(vue, "indiv-zone-sans", css=ZONE_BLOC24)
    fab.traverse(zone)
    vue_indiv24(fab, zone, "indiv-sans", {**PLEIN, **DEBORD_INDIV24}, modele, ordres, fn)
    vide24(fab, pos, "indiv-avec")   # rang 1 : avec le ballon (la dernière tuile)
    # v40 : le bouton FM 27 / FM24 est dans la ligne du haut (poser_extra24) ; v36-v39 : sous « Sélectionné actuellement »
    if not attendre_indiv24(t):
        return [f"{INDIV24} : paramètres attendus ({ATTENDU_INDIV24}) (introuvables)"]
    return [f"{INDIV24} : bouton FM 27 / FM24 et vue FM24 sans le ballon ({sum(1 for _ in t.walk(c))} éléments)"]


def poser_indiv_tuile(o, src, tb, modele, ordres, fn):
    """v33 : dans la dernière tuile créée avec le ballon (INDIV_TUILE24), ancrée en bas à droite sur toutes les tuiles
    (v51 : ZONE_INDIV24, la même zone que sans le ballon) : la vue FM24, en FM24 ; v36 : un peu plus grande
    (v51 : DEBORD_INDIV24)"""
    t = o[3]
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    if typ(t, racine) != "BindingExpect":
        return [f"{INDIV_TUILE24} : racine (introuvable)"]
    fab, c = fab_indiv(t, src, tb, racine, NOM_INDIV_TUILE)
    # v51 : la boîte « zone » de la grille, la même que sans le ballon, en points entiers depuis la tuile (v32-v50 :
    # CADRE_TUILE24 et CALE_AVEC24, mesurés sur captures)
    t.styles.style(t, c, ZONE_TUILE24)
    vue = premier_inter24(fab, tb, c, "indiv-vue-avec", V_INDIV24, PLEIN)
    vide24(fab, vue, "indiv-fm27-avec")              # rang 0 : les tuiles de FM 27
    vue_indiv24(fab, vue, "indiv-avec", {**PLEIN, **DEBORD_INDIV24}, modele, ordres, fn)   # rang 1 : la vue FM24
    if not attendre_indiv24(t):
        return [f"{INDIV_TUILE24} : paramètres attendus ({ATTENDU_INDIV24}) (introuvables)"]
    return [f"{INDIV_TUILE24} : vue FM24 avec le ballon ({sum(1 for _ in t.walk(c))} éléments)"]


def poser_tout_indiv(oi, ot, oc, src, tb, ox=None):
    """v33 : les trois morceaux des consignes individuelles ; un échec se termine par « (introuvable) » (rien n'est
    alors enregistré)"""
    absents = [m for m, x in ((INDIV24, oi), (INDIV_TUILE24, ot), (CARTE_INDIV24, oc), (EXTRA24, ox)) if x is None]
    if absents:
        return [f"consignes individuelles : {', '.join(absents)} absent(s) du jeu, vue FM24 non posée"]
    try:
        ordres = options_indiv24()   # v34 : la disposition montre exactement les options du jeu
        fn = fonction_element24()     # v36 : « élément n d'une liste »
        modele = bouton_ecrire_modele()
        if modele[1] is None:
            raise ValueError(f"bouton « écrire une valeur » de {SOURCE_ECRIRE24} (introuvable)")
        return (poser_carte(oc) + poser_indiv(oi, src, tb, modele, ordres, fn)
                + poser_indiv_tuile(ot, src, tb, modele, ordres, fn) + poser_extra24(ox, src, tb))
    except (ValueError, KeyError, IndexError, StopIteration) as e:
        return [f"consignes individuelles : {e!r} (introuvable)"]


def retirer_tout_indiv(oi, ot, oc, ox=None):
    """v33 : nos éléments et nos paramètres attendus des deux blocs, notre variable de la fiche ; rend les modèles
    touchés"""
    touches = []
    for x in (oi, ot):
        if x is not None and (retirer_indiv(x) | bool(attendre_indiv24(x[3], retirer=True))):
            ranger_feuille(x)
            touches.append(x)
    if oc is not None and retirer_carte(oc):
        touches.append(oc)
    if ox is not None and (retirer_indiv(ox) | attendre_extra24(ox[3], retirer=True)):   # v40
        ranger_feuille(ox)
        touches.append(ox)
    return touches


def est_indiv(nom):
    return nom.startswith(f"{base.PREFIXE}-indiv-v") and nom[len(f"{base.PREFIXE}-indiv-v"):][:1].isdigit()


def retirer_indiv(o):
    t = o[3]
    rs = [r for r in t.walk() if est_indiv(t.name(r))]
    for r in rs:
        t.remove(r)
    return bool(rs)


def est_droite(nom):
    """notre calque de la colonne de droite, toutes versions (« …-droite-v20 » ; pas « …-droite-vue », dedans)"""
    return nom.startswith(f"{base.PREFIXE}-droite-v") and nom[len(f"{base.PREFIXE}-droite-v"):][:1].isdigit()


def retirer_droite(o):
    t = o[3]
    rs = [r for r in t.walk() if est_droite(t.name(r))]
    for r in rs:
        t.remove(r)
    return bool(rs)


def ranger_feuille(o):
    """les règles de style ajoutées : feuille d'origine remise si plus aucune n'est utilisée, sinon retirées une à une
    (la fin de kinito_consignes_essai.retirer_essai)"""
    bundle, obj, tt, t = o
    orig = base.hp.original(bundle, obj)
    feuille = orig and base.hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is None:
        return
    n0 = len(feuille["m_Rules"])
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in tt["references"]["RefIds"] if r}
    if not any(i >= n0 for i in utilisees):
        t.styles.sh, t.styles.changed = feuille, True
        return
    regles = t.styles.sh["m_Rules"]
    garder = list(range(n0)) + [i for i in range(n0, len(regles)) if i in utilisees]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    t.styles.changed = True


# v46 (VERSION DE TEST) puis v47 : le MIROIR de l'onglet en vue FM24 (Kinito : la colonne de droite à gauche, puis les
# consignes, puis le terrain). Lu dans FM le 06/11 : les trois blocs sont posés par une grille (TacticalPlannerTeam
# Instructions > ScalableBindableGridLayoutElement#TeamInstructionsTabGrid) d'après une composition (bundle ui-tactics :
# Large, Large-InMatch, Standard ; elles ne placent que ces trois blocs) qui vaut pour toutes les vues : on ne la touche
# pas. À la place, quand la vue est FM24, un SIStyleSetter de FM (celui des boutons segmentés, comme selon_classe) pose
# sur LUI-MÊME une classe de FM qui retourne à l'horizontale (CLASSE_MIROIR) :
# - autour de la GRILLE : elle se retourne, l'ordre devient droite -> gauche, chaque bloc garde sa largeur ;
# - dans chaque BLOC (sous l'élément qui reçoit les variables de l'onglet, hote_miroir) : il se retourne une 2e fois sur
#   lui-même, son contenu est de nouveau à l'endroit.
# Hors vue FM24 : aucune classe, rien ne bouge. Le bloc du terrain (PITCH24) ne sert qu'à cet onglet (usages_modeles).
# v46 : rtl-horizontal-flip (« scale: var(--rlt-x-flip) 1 ») et la variable à −1 dans notre style intégré : rien de
# retourné en jeu (06/11). FM ne déclare jamais de variable dans un style intégré (0 dans tous ses modèles, mesuré) : il
# la déclare sur :root, dans ses feuilles LanguageDirectionLTR / RTL.
# v47 : CLASSE_MIROIR = la seule classe de FM dont la règle retourne sans variable (mesuré dans toutes ses feuilles :
# AlwaysAppliedStyleSheet règle 3619 et FigmaGeneratedStyles règle 2679, identiques) : height 248px, width 112px,
# scale -1 1, margin-right 32px. Notre style intégré passe devant toute règle de feuille : il remet hauteur et largeur
# à « auto » (mot-clé 2, comme 127 largeurs des feuilles de FM) et la marge à 0 ; seul reste le retournement.
MIROIR24 = ONGLET24 == "miroir"   # v48 : l'option OPTION_DISPOSITION ; v46, v47 : True
PITCH24 = "TacticalPlannerTeamInstructionsPitchBlock"
CLASSE_MIROIR = "shuffle-draft-set-transition-anim-left-tactical-area"
MOT_CLE_AUTO = 2   # StyleValueKeyword.Auto
RACINE_MIROIR = f"{base.PREFIXE}-miroir-v"
NOM_MIROIR = f"{RACINE_MIROIR}{VERSION}"
# v79 (Kinito, 11/11 : « on peut appliquer ce qu'on a fait pour terrain à droite à terrain à gauche ? ») : le travail
# grand écran de la vue FM24 (grille plafonnée, terrains de Positionnement, terrain seul avec son choix, bande de
# tuiles, Vue d'ensemble, coupes, remplaçants) vaut aussi pour l'ordre FM 27 (option « fm27 », terrain à gauche). La
# grille n'y est pas retournée : notre réglage de la grille et celui du bloc du terrain y posent CLASSE_GRILLE24, qui
# ne retourne rien, au lieu de CLASSE_MIROIR (nos règles lisent CLASSE_GRILLE) ; les blocs des consignes et des phases
# n'y sont pas retournés une 2e fois ; le terrain seul se pose sur le visualiseur de FM, à gauche (X_VISU24_FM27)
CLASSE_GRILLE24 = "kinito-consignes-grille-fm24"
CLASSE_GRILLE = CLASSE_MIROIR if MIROIR24 else CLASSE_GRILLE24


def est_miroir(nom):
    return nom.startswith(RACINE_MIROIR)


def reglage_miroir(t, src, parent, nom, css, index=None, classe=None, vue=VUE_FM24, chemin=None):
    """le SIStyleSetter de FM (comme selon_classe) qui pose CLASSE_MIROIR sur LUI-MÊME quand la vue est FM24 ; son style
    intégré : css, plus hauteur et largeur « auto » et marge droite 0 (ce que la règle de la classe impose en plus).
    v66 : classe = une autre classe à poser (la nôtre, CLASSE_FM24 : elle ne retourne rien, nos règles la lisent)"""
    modele = next((r for r in src.th.children(src.segments) if typ(src.th, r) == "SIStyleSetter"), None)
    if modele is None:
        raise ValueError("SIStyleSetter des boutons segmentés de FM (introuvable)")
    s = t.clone(modele, parent, index, src=src.th)
    for k in list(t.children(s)):
        t.remove(k)
    recaler_parent(t, s)
    sd = t.sd(s)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    f = sd.get("BindFunction") or {}
    if (f.get("m_target") or {}).get("m_guid") != GUID_CLASSE:
        raise ValueError("fonction de classe des boutons segmentés de FM : autre que prévu (introuvable)")
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    fins = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
            b"BooleanVisualArg", b"BooleanVisualArg")
    if len(args) != len(fins) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, fins)):
        raise ValueError("fonction de classe des boutons segmentés de FM : arguments inattendus (introuvable)")
    args[0][1] = _texte_arg(chemin or base.VARIABLE)   # v75 : chemin (settings.AdaptiveScalingLevelIndex)
    args[1][1] = struct.pack("<i", 2)          # égal
    args[2][1] = struct.pack("<i", vue)        # v73 : vue (VUE_FM24, ou la vue Terrain pour la coupe du visualiseur)
    args[3][1], args[4][1] = _texte_arg(classe or CLASSE_MIROIR), _texte_arg("")
    args[5][1] = args[6][1] = bytes([0])       # ni sur l'enfant ni sur le parent : sur lui-même (comme selon_classe)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, s, {**css, "flex-shrink": 1, "margin-right": 0})
    e = t.elem(s)
    pids = (base.sm.PROPRIETES["width"][0], base.sm.PROPRIETES["height"][0])
    e["m_RuleIndex"] = t.styles.add_rule([p for p in t.styles.values(e["m_RuleIndex"]) if p[0] not in pids]
                                         + [(pid, "", [(1, MOT_CLE_AUTO)]) for pid in pids])
    return s


# v80 (voir kinito_consignes_ecran.CLASSE_MATCH) : FM sait qu'on est en match (game.IsDuringMatch : la condition de ses
# propres tuiles retirées en match, dans les compositions de l'onglet). Sa fonction BindBoolToUSSClass (lue le 11/11 :
# entrées path, USSClass, ApplyToParent, ApplyToChildren ; TryGet<bool>, la classe posée si vrai, retirée sinon : rien
# ne casse si la liaison ne rend pas un oui / non) est celle de #UseDarkerHeaderIfFMC, dans l'onglet même
# (TacticalPlannerTeamInstructions) : recopié, vidé, il pose notre classe sur son PARENT
GUID_CLASSE_BOOL = "d4cdb2a2e77adec4ab06f28cdec4e783"
CHEMIN_MATCH = "game.IsDuringMatch"


def _vider_reglage(t, s, nom, css):
    for k in list(t.children(s)):
        t.remove(k)
    recaler_parent(t, s)
    sd = t.sd(s)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore
    t.elem(s)["m_Classes"], t.elem(s)["m_RuleIndex"] = [], -1
    t.styles.style(t, s, css)
    return sd


def reglage_match(t, parent, nom, classe, css):
    """v80 : le réglage de FM à oui / non (BindBoolToUSSClass) qui pose classe sur son parent pendant un match"""
    modele = next((r for r in t.walk() if typ(t, r) == "SIStyleSetter" and not t.name(r).startswith(base.PREFIXE)
                   and ((t.sd(r).get("BindFunction") or {}).get("m_target") or {}).get("m_guid") == GUID_CLASSE_BOOL),
                  None)
    if modele is None:
        raise ValueError("réglage de classe oui / non de FM (BindBoolToUSSClass, #UseDarkerHeaderIfFMC) (introuvable)")
    s = t.clone(modele, parent)
    sd = _vider_reglage(t, s, nom, css)
    f = sd["BindFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    fins = (b"BindingPath]", b"StringVisualArg", b"BooleanVisualArg", b"BooleanVisualArg")
    if len(args) != len(fins) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, fins)):
        raise ValueError("fonction de classe oui / non de FM : arguments inattendus (introuvable)")
    args[0][1] = _texte_arg(CHEMIN_MATCH)
    args[1][1] = _texte_arg(classe)
    args[2][1] = bytes([1])   # ApplyToParent
    args[3][1] = bytes([0])   # ApplyToChildren
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return s


def reglage_parent(t, src, parent, nom, chemin, valeur, classe, css):
    """v80 : le réglage de FM des boutons segmentés (BindIntComparisonToAOrBUssClass, comme reglage_miroir) qui pose
    classe sur son PARENT quand chemin vaut valeur"""
    modele = next((r for r in src.th.children(src.segments) if typ(src.th, r) == "SIStyleSetter"), None)
    if modele is None:
        raise ValueError("SIStyleSetter des boutons segmentés de FM (introuvable)")
    s = t.clone(modele, parent, src=src.th)
    sd = _vider_reglage(t, s, nom, css)
    f = sd.get("BindFunction") or {}
    if (f.get("m_target") or {}).get("m_guid") != GUID_CLASSE:
        raise ValueError("fonction de classe des boutons segmentés de FM : autre que prévu (introuvable)")
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    fins = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"StringVisualArg", b"StringVisualArg",
            b"BooleanVisualArg", b"BooleanVisualArg")
    if len(args) != len(fins) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, fins)):
        raise ValueError("fonction de classe des boutons segmentés de FM : arguments inattendus (introuvable)")
    args[0][1] = _texte_arg(chemin)
    args[1][1] = struct.pack("<i", 2)          # égal
    args[2][1] = struct.pack("<i", valeur)
    args[3][1], args[4][1] = _texte_arg(classe), _texte_arg("")
    args[5][1] = bytes([0])                    # ApplyToChildInstead
    args[6][1] = bytes([1])                    # ApplyToParentInctead
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return s


# v87 (voir kinito_consignes_ecran.CLASSE_3440) : la fonction de FM qui pose une classe d'après un TEXTE,
# BindStringToAorBUssClass (ui-visualfunctions ; entrées lues dans son graphe le 11/11 : path, True Style, False Style,
# ApplyToParent, ApplyToChildren, CompareString ; AsString de la valeur == CompareString -> True Style, sinon False
# Style). Ordre des arguments vérifié sur trois modèles de FM qui s'en servent (DisciplineTeamBlock,
# PlayerSquadNumbersRow, CalendarDropdownTitle : « app.GridBreakpoint » == « Small » / « Large »,
# « editsession.numselected.DisplayValue » == « - »). Pas de modèle dans l'onglet : on recopie le réglage oui / non
# (reglage_match) et on change sa fonction et ses arguments (comme Alex, club_amical : FN_CIBLE)
GUID_CLASSE_TEXTE = "c5ecb69a298e864428d1e90d9c8c7f80"


def reglage_texte(t, parent, nom, chemin, texte, classe, css):
    """v87 : un réglage de FM vide qui pose classe sur son PARENT quand le texte lu sous chemin vaut texte"""
    s = reglage_match(t, parent, nom, classe, css)
    f = t.sd(s)["BindFunction"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chem, txt, oui = args[0][0], args[1][0], args[2][0]
    f["m_target"]["m_guid"] = GUID_CLASSE_TEXTE
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args([
        [chem, _texte_arg(chemin)],
        [txt, _texte_arg(classe)],     # True Style
        [txt, _texte_arg("")],         # False Style
        [oui, bytes([1])],             # ApplyToParent
        [oui, bytes([0])],             # ApplyToChildren
        [txt, _texte_arg(texte)]])     # CompareString
    return s


ecran37.REGLAGE_MATCH = reglage_match   # v80
ecran37.REGLAGE_PARENT = reglage_parent
ecran37.REGLAGE_TEXTE = reglage_texte   # v87
ecran37.MOTS_KINITO = {"Partir de zéro": dict(ZERO_LANGUES), "Tuiles": dict(TUILES_LANGUES)}   # v95 : la langue du jeu


def bouton_choix(t, src, parent, nom, variable, valeur, css, icone=None, taille_icone=20):
    """v75 : un bouton de FM (le bouton segmenté des cartes de chaleur, recopié avec son texte mais sans son réglage :
    l'allure d'un bouton non choisi, comme « Avec le ballon » quand il ne l'est pas), en absolu (css), qui écrit
    valeur dans variable ; son texte, fixe : « Visualiseur » pour 1, « Dispositif » pour 0. v81 : icone, une classe
    d'icône de FM à la place du texte (son SIText vidé porte l'icône, à taille_icone : plus de texte qui grandit avec
    la taille de police de FM)"""
    th = src.th
    reglages = th.children(src.segments)
    modele = th.children(reglages[0])[0] if reglages and th.children(reglages[0]) else None
    if modele is None or typ(th, modele) != "SIButton":
        raise ValueError("bouton segmenté des cartes de chaleur (introuvable)")
    fab = ecran37.Ecran(t, src, None, None).fab
    b = recopie(fab, th, modele, parent, nom)
    t.elem(b)["m_Classes"] = ["buttons-combo-button-base-default"]   # l'allure de « Partir de zéro » (son cadre)
    clavier = [k for k in t.walk(b) if k != b and t.name(k) == "controllers-keyboard-container"]
    for k in clavier:   # raccourci clavier de FM : pas le nôtre (relevés d'abord : un retrait emporte les descendants)
        if k in t.refs and t.refs[k] is not None:
            t.remove(k)
    texte = next((k for k in t.walk(b) if typ(t, k) == "SIText"), None)
    if texte is None:
        raise ValueError("texte du bouton segmenté (introuvable)")
    if icone:   # v81
        texte_fige(t, texte, "")
        t.elem(texte)["m_Classes"] = [icone]
        t.styles.style(t, texte, {"width": taille_icone, "height": taille_icone, "min-width": taille_icone,
                                  "min-height": taille_icone, "flex-shrink": 0, "flex-grow": 0})
    else:
        texte_fige(t, texte, langue.texte("Visualiseur", "Visualiser") if valeur
                   else langue.texte("Dispositif", "Shape"))
    sd = t.sd(b)
    sd["Events"], sd["Events_UxmlAttributeFlags"] = {"m_bytes": liste([copier(PLACES[valeur], variable,
                                                                              1 if valeur else 0)])}, 1
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 0, 1
    t.styles.style(t, b, {"position": "absolute", **css, "margin-top": 0, "margin-bottom": 0, "margin-left": 0,
                          "margin-right": 0, "flex-shrink": 0,
                          **({"justify-content": "center", "align-items": "center", "padding-left": 0,
                              "padding-right": 0} if icone else {})})   # v81 : l'icône au milieu
    return b


def poser_miroir_grille(t, src):
    """la grille de l'onglet dans notre réglage : retournée en vue FM24"""
    g = first(t, lambda r: typ(t, r) == "ScalableBindableGridLayoutElement")
    if g is None:
        raise ValueError(f"{PARENT24} : grille des blocs (introuvable)")
    p = t.parent[g]
    reg = reglage_miroir(t, src, p, f"{NOM_MIROIR}-grille", {"flex-grow": 1, "flex-direction": "row"},
                         index=t.children(p).index(g), classe=None if MIROIR24 else CLASSE_GRILLE24)   # v79
    base.deplacer(t, g, reg, 0)


# v52 (Kinito, 08/11 : capture d'un joueur en 1440p, disposition « miroir », la colonne de gauche écrite à l'envers).
# En grand écran, la composition Large de l'onglet (TacticalPlannerTeamInstructionsTabComposition-Large, bundle
# ui-tactics, lue le 08/11) ajoute à DROITE des trois blocs des tuiles de FM « en option » (m_optionalSlices : m_right
# ClubTeamReport, DataHub, Captains ; m_bottomRight SetPieces, Penalties, OppositionInstructions), posées seulement
# quand l'écran a la place (jamais en 1920 x 1080 chez Kinito). Notre miroir retourne toute la grille : elles passaient
# à gauche ET leur contenu se lisait à l'envers. Ces tuiles servent à d'autres écrans (portail, vue d'ensemble) : on
# ne les touche pas. À la place, une règle À SÉLECTEURS dans la feuille intégrée du modèle, rattachée à notre réglage
# de la grille (la technique d'Alex, moteur_graphes, et de 26.19 : les règles d'une feuille rattachée à un élément
# valent pour lui et tout ce qui est dessous, éléments créés en jeu compris) : en vue FM24 (la classe du miroir posée
# sur le réglage), chaque tuile en option retournée sur elle-même. Elle reste à gauche (la grille la place là), son
# contenu se relit à l'endroit. Une tuile de grille est un BindableVariableSizedGridElement nommé comme sa place dans la
# composition, enfant direct de #GridLayoutElementContent (lu dans ses journaux de clics : #TeamInstructionsBlock,
# #DataHub, #Captains .si-tile) ; FM a d'autres éléments nommés DataHub ou Captains DANS des tuiles, d'où « enfant
# direct ». La règle part avec le réglage : retirer_miroir l'ôte, ranger_feuille retire la règle que plus rien ne cite.
TUILES_EN_OPTION = ("ClubTeamReport", "DataHub", "Captains", "SetPieces", "Penalties", "OppositionInstructions")
ID_SCALE = 327681   # StylePropertyId.Scale (deux nombres, comme la règle de CLASSE_MIROIR : -1 1)
REPERE_REGLE_MIROIR = "--kinito-consignes-miroir"   # propriété perso de notre règle à sélecteurs (la retrouver)
TYPE_CLASSE, TYPE_NOM = 3, 6   # StyleSelectorType (Class, ID)
ENFANT, DESCENDANT = 1, 2      # StyleSelectorRelationship (mesuré par 26.19 dans SIStyles)
# v63 (Kinito, 10/11 : « j'ai encore des gens qui ont des tuiles inversées », capture d'un joueur en 5120 x 1440 :
# rapport adversaire, centre des données, capitaines, coups de pied arrêtés à l'envers ; « applique-le à toutes les
# tuiles, que rien ne soit inversé »). Ces quatre tuiles sont dans TUILES_EN_OPTION depuis la v52 (chez Alex depuis sa
# v1.70 du 09/11) : le joueur a sans doute un skin posé avant. Mais la règle ne visait que six noms, enfants directs du
# contenu de la grille. Elle vise désormais AUSSI toute tuile de la grille de l'onglet, quel que soit son nom ou sa
# place : la classe que FM pose sur chaque tuile de grille (CLASSE_TUILE, lue dans ses journaux de clics ; absente des
# modèles des six tuiles et de nos trois blocs, vérifié le 10/11 : FM ne la met que sur les tuiles qu'il crée). Nos
# trois blocs, eux, se retournent déjà de l'intérieur (poser_miroir_bloc) : une 2e règle, plus forte (trois noms
# contre un nom et une classe), les laisse à leur échelle (1 1)
CLASSE_TUILE = "si-tile"
NOS_BLOCS = ("TeamInstructionsPitch", "TeamInstructionsBlock", "PhasesAndTeamInstructions")   # noms dans la composition


def _selecteur(parties, idx):
    """un sélecteur complexe (format Unity 6) : parties = [(type, valeur, relation au précédent)]"""
    return {"m_Specificity": 1 + sum(10 if ty == TYPE_CLASSE else 100 for ty, _, _ in parties),
            "m_Selectors": [{"m_Parts": [{"m_Value": v, "m_Type": ty}], "m_PreviousRelationship": rel}
                            for ty, v, rel in parties],
            "ruleIndex": idx}


def poser_miroir_tuiles(t):
    """v52 : la règle qui remet à l'endroit les tuiles en option de la grille (TUILES_EN_OPTION), en vue FM24 ; la
    feuille intégrée du modèle rattachée à notre réglage de la grille. v63 : toute tuile de la grille (CLASSE_TUILE),
    sauf nos trois blocs (NOS_BLOCS, 2e règle)"""
    reg = first(t, lambda r: t.name(r) == f"{NOM_MIROIR}-grille")
    if reg is None:
        raise ValueError("réglage du miroir de la grille (introuvable)")
    idx = t.styles.add_rule([(ID_SCALE, "", [(2, -1.0), (2, 1.0)]), (-1, REPERE_REGLE_MIROIR, [(2, 52.0)])])
    debut = [(TYPE_CLASSE, CLASSE_MIROIR, 0), (TYPE_NOM, "TeamInstructionsTabGrid", DESCENDANT)]
    complexes = [_selecteur(debut + [(TYPE_NOM, "GridLayoutElementContent", DESCENDANT), (TYPE_NOM, tuile, ENFANT)], idx)
                 for tuile in TUILES_EN_OPTION]
    complexes.append(_selecteur(debut + [(TYPE_CLASSE, CLASSE_TUILE, DESCENDANT)], idx))   # v63 : toute tuile
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = complexes
    idx2 = t.styles.add_rule([(ID_SCALE, "", [(2, 1.0), (2, 1.0)]), (-1, REPERE_REGLE_MIROIR, [(2, 63.0)])])
    t.styles.sh["m_Rules"][idx2]["m_ComplexSelectors"] = [
        _selecteur(debut + [(TYPE_NOM, "GridLayoutElementContent", DESCENDANT), (TYPE_NOM, bloc, ENFANT)], idx2)
        for bloc in NOS_BLOCS]
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(reg).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)


# v66 (Kinito, 10/11, capture 2560 Small en vue FM24 : « quand il y a des tuiles, tout aligner à gauche et les tuiles à
# droite ») : le miroir retourne toute la grille, les tuiles que FM pose à droite passaient à gauche ; les remettre à
# droite par des décalages ne se peut pas (ils vaudraient la largeur des blocs, que FM étire selon l'écran). À la place,
# EN VUE FM24 SEULEMENT : la grille de FM est plafonnée à 23 colonnes (LARGEUR_GRILLE24) — FM ne pose ses tuiles en
# option qu'à partir de 24 (20 + les 4 de la colonne de droite) : il n'en pose plus, et ses trois blocs, retournés,
# remplissent la grille collés à gauche ; la place qui reste à droite reçoit NOS copies de ses tuiles (TUILES24, comme
# la bande de la vue Terrain). Pour cela, une enveloppe (un réglage comme celui du miroir, mais qui pose notre classe
# CLASSE_FM24, qui ne retourne rien) prend la place du réglage de la grille : [réglage de la grille | nos tuiles]. Hors
# vue FM24, rien ne change (la grille prend toute la largeur, nos tuiles 0). En 1080p, la grille fait 20 colonnes
# (1 624) : le plafond ne joue pas, nos tuiles n'ont aucune place.
CLASSE_FM24 = "kinito-consignes-vue-fm24"   # notre classe (posée par l'enveloppe en vue FM24), lue par nos règles
FIN_ENVELOPPE24, FIN_TUILES24 = "-enveloppe24", "-tuiles24"
# v71 (Kinito, 10/11, v70 vue en 2560 Moyen : « une rangée de tuiles à droite est possible ? » ; en 2560 Petit, le
# terrain de Positionnement à gauche) : 20 colonnes, celles de la composition Large de FM (ses trois blocs n'en prennent
# pas plus, les deux de plus n'étaient que du vide : l'écart qu'on voyait à gauche des blocs en 3440 Moyen). 2560 Moyen
# (~2 017) : 1 624 + une colonne de tuiles (316) tiennent ; en 1080p (1 624), rien ne change
LARGEUR_GRILLE24 = 20 * 82 - 16   # 1 624. v68 à v70 : 22 colonnes (1 788) ; v66, v67 : 23 (1 870) ; pile 22 colonnes,
#                                   donc aucun vide à gauche une fois retournée. v66, v67 : 23 (1 870) ; v68 (Kinito,
#                                   10/11 : « 22 colonnes ») : en 2560 Small il restait ~575 à droite, une seule colonne
#                                   de tuiles ; avec 22, ~657 : les deux tiennent (632 demandés)


# v69 (Kinito, 10/11, v68 vue en 3440 Small : le terrain de « Positionnement de l'équipe » à GAUCHE, le reste décalé,
# « sans que ça impacte les autres résolutions ») : l'enveloppe devient une rangée À L'ENVERS qui passe à la ligne et
# coupe ce qui en sort : [intérieur (réglage de la grille | nos tuiles) | terrain]. À l'envers, le terrain vient à
# gauche, et c'est lui, le dernier, qui passe à la ligne (donc caché) quand les deux ne tiennent pas. L'intérieur fait
# toute la largeur, plafonné en vue FM24 à la grille plafonnée + deux colonnes de tuiles (LARGEUR_INTERIEUR24) ; le
# terrain prend six colonnes de la grille (PLACE_TERRAIN24) : il ne paraît qu'à partir de ~2 912 unités. En 2560 Small
# (~2 445) l'intérieur fait 2 420 (la grille, et nos deux colonnes de tuiles entières : comme la v68, 25 vides à droite au
# lieu d'être au bout de la zone des tuiles), en 1080p rien ne bouge. Hors vue FM24 : le terrain caché (règle), rien
# n'est plafonné. Pour que la coupe n'ôte rien à la grille de FM (elle descend de 20 sous son parent : margin-bottom
# -20, lu dans le modèle), l'enveloppe descend d'autant et l'intérieur garde ces 20 en bas. Le terrain est une copie du
# modèle de FM avec ses variables à lui (kinito_consignes_ecran.poser_terrain24) ; nos règles y cachent « Les deux »,
# le côté droit de l'en-tête (repli, options) et les remplaçants
# v70 (Kinito, 10/11, v69 vue en jeu) : en 3440 Petit la 2e colonne de tuiles ne paraissait pas (l'intérieur plafonné
# PILE à deux colonnes : un arrondi la faisait passer à la ligne) ; en 3440 Moyen il veut le terrain « plutôt que des
# tuiles ». Plus de plafond : en vue FM24, l'intérieur PART de BASE_INTERIEUR24 (règle : flex-basis) et grandit ; c'est
# cette base + le terrain qui décide s'il paraît, puis l'intérieur prend tout le reste (grille plafonnée, puis autant de
# colonnes de tuiles entières que la place en laisse). Mesuré sur ses captures (largeur de l'enveloppe) : 2 560 Petit
# ~2 463 (pas de terrain : il garde ses deux colonnes de tuiles), 3 440 Moyen ~2 613 (terrain, une colonne), 3 440 Petit
# ~3 199 (terrain, deux colonnes) ; le seuil (base + 490 = 2 535) est au milieu des deux premières
# v71 (Kinito, 10/11, v70 vue en jeu : en 2560 Petit « le dispositif à gauche, avec choix avec et sans ballon » et
# une colonne de tuiles ; en 3440 Petit « les deux terrains, avec et sans ballon », sans boutons) : l'intérieur part de
# la grille + UNE colonne de tuiles (1 940) ; le terrain (490) paraît dès que les deux tiennent (≥ 2 430 : 2 560 Petit
# ~2 463, 3 440 Moyen ~2 613 et Petit ~3 199 oui ; 3 440 Grand ~2 202, 2 560 Moyen ~2 017 non). Les DEUX terrains
# demandent 484 de plus (≥ 2 914 : 3 440 Petit seulement) : une 2e boîte (FIN_DEUX24), à gauche du terrain, qui passe à
# la ligne avant lui ; les deux terrains de FM (mode « Les deux ») partent d'elle, en absolu, et couvrent le terrain
# simple (même place, dessous). Sans elle, on voit le terrain simple
FIN_INTERIEUR24, FIN_TERRAIN24, FIN_DEUX24 = "-interieur24", "-terrain24", "-deux24"
FIN_BANDE24 = "-bande24"   # v74 : la bande de tuiles sous nos blocs coupés (ecran37.poser_bande24)
FIN_SEUL24 = "-seul24"     # v76 : la boîte d'où se pose le terrain seul (ecran37.poser_seul24)
# v74 (Kinito, 11/11 : « couper le terrain FM24 pour aligner sur le bas des terrains dispo et visualiseur ») : en vue
# FM24, les cases de la grille de nos blocs des consignes et des phases plafonnées à ecran37.HAUT_PANNEAU (la grille
# les place en absolu ; un plafond par règle tient malgré leur hauteur écrite en jeu). Le visualiser, lui, l'est par
# son panneau (poser_bas_visualiseur)
CASES_COUPEES24 = ("TeamInstructionsBlock", "PhasesAndTeamInstructions")
DEPASSE_GRILLE = 20
# v72 (Kinito, 11/11, v71 vue en 3440 Grand : la place libre à droite, ~260, ne prenait pas une colonne de tuiles ;
# son choix : « le dispositif à gauche ») : l'intérieur part de la grille seule ; le terrain passe AVANT la colonne de
# tuiles : dès 2 120 (3 440 Grand ~2 202 oui, 2 560 Moyen ~2 017 non) ; la colonne vient ensuite si elle tient (2 560
# Petit, 3 440 Moyen et Petit). La 2e boîte (les deux terrains) fait 600 : elle ne passe qu'à partir de 2 720 (3 440
# Petit ~3 199 oui, 3 440 Moyen ~2 613 non), et ses deux terrains prennent sa place et celle du terrain simple
BASE_INTERIEUR24 = LARGEUR_GRILLE24   # v71 : 1 940 (+ une colonne) ; v70 : 2 045


def poser_tuiles24(t, src, tb):
    """v66 : l'enveloppe [réglage de la grille | nos tuiles] et la règle qui plafonne la grille en vue FM24 ; rend le
    nombre de tuiles posées. v69 : [intérieur (réglage de la grille | nos tuiles) | terrain de Positionnement] (voir
    FIN_INTERIEUR24). v70 : l'intérieur part de BASE_INTERIEUR24 au lieu d'être plafonné"""
    reg = first(t, lambda r: t.name(r) == f"{NOM_MIROIR}-grille")
    if reg is None:
        raise ValueError("réglage du miroir de la grille (introuvable)")
    p = t.parent[reg]
    env = reglage_miroir(t, src, p, f"{NOM_MIROIR}{FIN_ENVELOPPE24}",
                         {"flex-grow": 1, "flex-direction": "row-reverse", "flex-wrap": "wrap",
                          "justify-content": "flex-end", "align-content": "flex-start", "overflow": "hidden",
                          "margin-bottom": -DEPASSE_GRILLE},
                         index=t.children(p).index(reg), classe=CLASSE_FM24)
    # v82 : l'ajusteur de FM autour de l'enveloppe (voir ECHELLE_MAX_MATCH24) : hors match il prend toute la place et
    # ne réduit rien
    e_aj = ecran37._ecran_boites(t, src, tb)
    ajuste = f"{NOM_MIROIR}{FIN_AJUSTE24}"
    aj = e_aj.seul(e_aj.se.ta, e_aj.se.ajuste, p, nom=ajuste, index=t.children(p).index(env))
    sa = t.sd(aj)
    sa["AspectMode"], sa["AspectRatio"] = ecran37.MODE_SCALE_TO_FIT, 1.0
    sa["AspectMode_UxmlAttributeFlags"] = sa["AspectRatio_UxmlAttributeFlags"] = 1
    # v83 : EN ABSOLU sur toute la place de son parent (UseDarkerHeaderIfFMC) : dans le flux, dessiné plus grand en match,
    # il agrandissait son parent, et FM le comparait à lui-même (v82 vue en 2 560 Grand : rien de réduit) ; son bas par
    # règles (poser_fm24_match)
    t.styles.style(t, aj, {"position": "absolute", "left": 0, "top": 0, "right": 0, "flex-direction": "column"})
    e_aj.fab.style_brut(aj, [(ecran37.ID_ORIGINE, [(7, "left"), (7, "top")])])
    base.deplacer(t, env, aj, 0)
    inter = ecran37.boite24(t, src, tb, env, f"{NOM_MIROIR}{FIN_INTERIEUR24}",
                            {"width": pc(100), "max-width": pc(100), "height": pc(100), "flex-grow": 1,
                             "flex-shrink": 0, "flex-direction": "row", "padding-bottom": DEPASSE_GRILLE})
    base.deplacer(t, reg, inter, 0)
    t.styles.style(t, reg, {"width": pc(100), "flex-grow": 0, "flex-shrink": 0})
    n = ecran37.poser_tuiles24(t, src, tb, inter, f"{NOM_MIROIR}{FIN_TUILES24}")
    terrain = f"{NOM_MIROIR}{FIN_TERRAIN24}"
    # v74 : coupé, les remplaçants dessous (v73 : trois tuiles)
    ecran37.poser_terrain24(t, src, tb, env, terrain, hauteur=ecran37.HAUT_TERRAIN_COUPE, remplacants=True)
    deux = f"{NOM_MIROIR}{FIN_DEUX24}"   # v71 : les deux terrains (voir FIN_DEUX24)
    # v87 : sa largeur (PLACE_DEUX24) et le bord gauche des deux terrains (GAUCHE_DEUX24) par règles (poser_3440), plus
    # dans le style intégré : en 3 440 Petit hors match, ils changent
    boite_deux = ecran37.boite24(t, src, tb, env, deux,
                                 {"height": pc(100), "flex-shrink": 0, "flex-grow": 0})
    # v74 : les deux terrains à 476 chacun, le 2e sur le terrain simple (ecran37.GAUCHE_DEUX24) ; les remplaçants
    # dessous, sur toute leur largeur (ils couvrent ceux du terrain simple)
    ecran37.poser_terrain24(t, src, tb, boite_deux, f"{deux}-terrains", mode=ecran37.MODE_LES_DEUX,
                            css={"position": "absolute", "top": 0,
                                 "width": ecran37.LARGEUR_DEUX24, "height": pc(100), "flex-direction": "column"},
                            hauteur=ecran37.HAUT_TERRAIN_COUPE, remplacants=True,
                            tuiles_dessous=ecran37.TUILES_SOUS_DEUX24)   # v76 : trois tuiles sous les remplaçants
    n += len(ecran37.TUILES_SOUS_DEUX24)
    # v76 : le terrain seul (voir ecran37.X_VISU24) : une boîte de largeur 0 juste après le terrain de Positionnement
    seul = f"{NOM_MIROIR}{FIN_SEUL24}"
    boite_seul = ecran37.boite24(t, src, tb, env, seul, {"width": 0, "height": pc(100), "flex-shrink": 0,
                                                         "flex-grow": 0},
                                 index=t.children(env).index(boite_deux))
    seul_d = ecran37.poser_seul24(t, src, tb, boite_seul, f"{seul}-terrain",
                                  x=ecran37.X_VISU24 if MIROIR24 else ecran37.X_VISU24_FM27)   # v79
    bande = f"{NOM_MIROIR}{FIN_BANDE24}"   # v74
    n += ecran37.poser_bande24(t, src, tb, inter, bande, LARGEUR_GRILLE24, visu_droite=MIROIR24)   # v88
    largeur = base.sm.PROPRIETES["max-width"][0]
    affichage = base.sm.PROPRIETES["display"][0]
    depart = base.sm.PROPRIETES["flex-basis"][0]

    def regle(valeurs, repere, selecteurs):
        idx = t.styles.add_rule(valeurs + [(-1, REPERE_REGLE_MIROIR, [(2, repere)])])
        t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [_selecteur(s, idx) for s in selecteurs]
    fm24 = (TYPE_CLASSE, CLASSE_FM24, 0)
    regle([(largeur, "", [(3, {"unit": 1, "value": float(LARGEUR_GRILLE24)})])], 66.0,
          [[fm24, (TYPE_NOM, f"{NOM_MIROIR}-grille", DESCENDANT)]])
    regle([(depart, "", [(3, {"unit": 1, "value": float(BASE_INTERIEUR24)})])], 70.0,
          [[fm24, (TYPE_NOM, f"{NOM_MIROIR}{FIN_INTERIEUR24}", ENFANT)]])
    regle([(affichage, "", [(7, "none")])], 69.1,
          [[(TYPE_NOM, nom, 0)] for nom in (terrain, deux, seul)] +
          [[(TYPE_NOM, nom, 0), (TYPE_NOM if k == "#" else TYPE_CLASSE, v, DESCENDANT)]
           for nom in (terrain, deux, seul_d) for k, v in ecran37.CACHES_TERRAIN24] +
          [[(TYPE_NOM, deux, 0), (TYPE_NOM if k == "#" else TYPE_CLASSE, v, DESCENDANT)]
           for k, v in ecran37.CACHES_DEUX24])
    regle([(affichage, "", [(7, "flex")])], 69.2, [[fm24, (TYPE_NOM, nom, ENFANT)] for nom in (terrain, deux, seul)])
    # v74 : la bande de tuiles, en vue FM24 seulement ; les cases de nos deux blocs coupées (CASES_COUPEES24)
    regle([(affichage, "", [(7, "none")])], 74.1, [[(TYPE_NOM, bande, 0)]])
    regle([(affichage, "", [(7, "flex")])], 74.2, [[fm24, (TYPE_NOM, bande, DESCENDANT)]])
    # v74 : nos remplaçants (sous les terrains) échappent à la règle 69.1, qui cache ceux du modèle de FM (plus forte :
    # deux noms et une classe contre un nom et une classe)
    regle([(affichage, "", [(7, "flex")])], 74.3,
          [[(TYPE_NOM, nom, 0), (TYPE_NOM, f"{zone}-remplacants", DESCENDANT), (TYPE_CLASSE, "tactics-subs-block",
                                                                              DESCENDANT)]
           for nom, zone in ((terrain, terrain), (deux, f"{deux}-terrains"))])
    regle([(base.sm.PROPRIETES["max-height"][0], "", [(3, {"unit": 1, "value": float(ecran37.HAUT_PANNEAU)})])], 74.0,
          [[(TYPE_CLASSE, CLASSE_GRILLE, 0), (TYPE_NOM, "TeamInstructionsTabGrid", DESCENDANT),
            (TYPE_NOM, "GridLayoutElementContent", DESCENDANT), (TYPE_NOM, case, ENFANT)] for case in CASES_COUPEES24])
    # v72 : entre les deux terrains, l'écart des blocs (voir ecran37.ECART_DEUX)
    regle([(base.sm.PROPRIETES["margin-left"][0], "", [(3, {"unit": 1, "value": float(ecran37.ECART_DEUX)})])], 72.0,
          [[(TYPE_NOM, deux, 0), (TYPE_CLASSE, "margin-left-8", DESCENDANT)]])
    poser_fm24_match(t, terrain, bande, ajuste)   # v81, v82
    poser_3440(t, terrain, deux, bande, ajuste)   # v87
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    # v84 : la feuille rattachée AUSSI à l'ajusteur, parent de l'enveloppe (sa mesure FMSonde en 3 440 Moyen, v83 : les
    # règles de l'ajusteur ne valaient pas, la feuille n'étant rattachée qu'à l'enveloppe, sous lui ; il prenait la
    # hauteur de son contenu, 706, et ne réduisait rien : x1,5 partout)
    for r in (aj, env):
        feuilles = t.elem(r).setdefault("m_Stylesheets", [])
        if ref not in feuilles:
            feuilles.append(ref)
    return n


# v81 (Kinito, 11/11, ses captures EN MATCH, puis FMSonde 0.28.0 aux six tailles de 1440p et en 1080p, vue FM24) : EN
# MATCH seulement (classes posées sur #Body de l'onglet, voir kinito_consignes_ecran.CLASSE_MATCH), la vue FM24 sans
# tuiles, Vue d'ensemble ni remplaçants, et toute l'enveloppe agrandie ou réduite depuis son coin haut gauche pour finir
# sur la ligne de FM (2 au-dessus du bas de #Body). Hauteurs mesurées : nos blocs 724 ; #Body 1 051 (3 440 Petit),
# 1 136 (2 560 Petit), 808 (3 440 Moyen), 888 (2 560 Moyen), 643 (Grand, 1080p compris). Une seule échelle par
# affichage (les règles ne lisent pas la largeur) : la plus petite des deux résolutions. Largeurs (#Body) : 3 182 / 2 443
# (Petit), 2 608 / 2 034 (Moyen), 2 198 / 1 624 (Grand) ; à ces échelles tout tient (le plus juste : 3 440 Petit,
# 2 120 x 1,449 = 3 072).
# Ses choix : 3 440 Petit, dispositif + visualiseur de FM + consignes + colonne (« A », plutôt que les deux terrains) ;
# 2 560 Petit, un seul panneau (dispositif ou visualiseur, par le bouton à icône) + consignes + colonne, à la même
# échelle ; 2 560 Moyen, le visualiseur de FM seul + consignes + colonne ; Grand, tout réduit, sans défiler.
# - Petit : l'intérieur part de BASE_INTERIEUR_PETIT_MATCH au lieu de 1 624 : le terrain de Positionnement ne paraît
#   plus qu'à partir de 2 796 (3 440 Petit oui, 2 560 Petit non : notre dispositif seul et son bouton y paraissent, sur le
#   visualiseur de FM) et les deux terrains plus du tout ;
# - Moyen : notre dispositif seul (sur le visualiseur de FM, 2 560 Moyen) caché ;
# - Grand : la grille de FM faisait 722 dans 663 : elle DÉFILAIT. L'enveloppe passe à HAUT_MIN_GRAND_MATCH (sa grille,
#   745, contient ses 722 : plus de défilement), réduite à 0,885 (724 -> 641).
# v82 (Kinito, 11/11, v81 vue en match : en Petit c'est bon, en Moyen et en Grand, 3 440 et 2 560, la vue reste
# agrandie comme en Petit ; « en Petit, un poil plus grand ? il reste de la place à droite et en bas ») : la classe
# d'affichage posée sur #Body (settings.AdaptiveScalingLevelIndex) NE SUIT PAS un changement d'affichage pendant le
# match (celle de l'ouverture de l'onglet reste ; ses mesures FMSonde l'avaient déjà montré : jamais de classe Moyen
# ni Petit). Plus de classe d'affichage : l'AJUSTEUR DE FM (SIAspectRatioFitter, ScaleToFit, comme l'écran de la vue
# Terrain) entoure l'enveloppe. Hors match il prend toute la place (échelle 1). En match et en vue FM24, il est DESSINÉ
# à ECHELLE_MAX_MATCH24 x HAUT_LIGNE_MATCH24 de haut et l'enveloppe, dedans, agrandie de ECHELLE_MAX_MATCH24 ; FM le
# réduit pour qu'il tienne dans la hauteur de #Body, en direct : échelle nette = min(1,5 ; hauteur / 727) : 3 440 Petit
# 1,446, 2 560 Petit 1,5, 3 440 Moyen 1,111, 2 560 Moyen 1,221, Grand 0,884 (la grille, 1 090 de haut, ne défile plus).
# Le plafond vient de la largeur de 2 560 Petit : un panneau + consignes + colonne = 1 624 x 1,5 = 2 436 pour 2 443.
# Ce qui paraît ne dépend plus que de la largeur : l'intérieur part de BASE_INTERIEUR_MATCH, le terrain de
# Positionnement (dispositif à côté du visualiseur de FM) ne paraît qu'à partir de 2 595 (3 440 Petit 3 182, 3 440
# Moyen 2 608 : oui ; 2 560 Petit 2 443, 3 440 Grand 2 198, 2 560 Moyen 2 034, Grand 1 624 : non, un seul panneau avec le
# bouton à icône), les deux terrains jamais (ils demandent 3 195). Différences avec ses choix de la v81 : 3 440 Grand et
# 2 560 Moyen ont le panneau à bouton (2 560 Moyen : le dispositif d'abord, le visualiseur au bouton).
ECHELLE_MAX_MATCH24 = 1.5
HAUT_LIGNE_MATCH24 = 745      # v84 (Kinito, v83 vue en 3 440 : « encore un poil grand, laisse la marge entre nos écrans
#                               et la barre FM » ; la légende Sélectionné / Indisponible, sous le bloc des consignes,
#                               passait sous la barre) : nos blocs (724) finissent 21/745 de la hauteur au-dessus du bas
#                               de #Body (Petit ~30, Grand ~18 unités ; la barre se voit 12 plus bas). v82, v83 : 727
BASE_INTERIEUR_MATCH = 2099   # 2 086 < base < 2 112 (mesures du 11/11)
FIN_AJUSTE24 = "-ajuste24"
# v87 (Kinito, 11/11, 3 440 Petit HORS match, vue FM24 : « virer toute la colonne de droite et agrandir tout le reste »,
# une seule rangée de tuiles ; ses choix au questionnaire) : sous les quatre classes de #Body (hors match, écran
# 3 440 x 1440, affichage Petit, vue FM24 ; voir kinito_consignes_ecran.CLASSE_3440) :
# - la colonne de droite (nos tuiles : la Vue d'ensemble et le centre des données) cachée, comme la rangée de tuiles
#   sous les remplaçants des deux terrains (dynamique, blessés, retours tactique), son fond (v77) et les remplaçants du
#   terrain simple (plus rien ne dépasse sous le 2e terrain : le rectangle sombre de sa capture du 11/11) ;
# - la bande : une rangée (BANDE24_3440) au lieu de deux ;
# - l'enveloppe dessinée à ECHELLE_3440 depuis son coin haut gauche ; l'ajusteur, son parent, à 100 / ECHELLE_3440 %
#   de la place : sa mise en page se fait sur la place qui, agrandie, remplit l'onglet. La largeur décide : les deux
#   terrains + la grille = GAUCHE_DEUX_3440 + 973 + 14 + 1 624 = 2 623 pour ~2 650 (3 182 à 3 199 / 1,2) ; en hauteur,
#   740 + 148 + 3 = 891 x 1,2 = 1 069 pour ~1 150 (un peu de vide en bas) ;
# - le vide à gauche des deux terrains (GAUCHE_DEUX24, 103) ramené à GAUCHE_DEUX_3440 : leur boîte rétrécit d'autant
#   (le 2e terrain couvre toujours le terrain simple) ; l'intérieur part de BASE_INTERIEUR_3440 (marge de passage à la
#   ligne : les deux terrains restent sur la 1re ligne)
ECHELLE_3440 = 1.2
GAUCHE_DEUX_3440 = 12
PLACE_DEUX_3440 = GAUCHE_DEUX_3440 + ecran37.LARGEUR_TERRAIN24 + ecran37.ECART_DEUX   # 509
BASE_INTERIEUR_3440 = 1500
# v90 (Kinito, 11/11, 3 440 Petit hors match, ordre FM 27 : « on fusionne les 3 terrains, remplaçants seulement sous
# le terrain fusionné, juste après les consignes ; zoomer les consignes et la colonne récap pour aller jusqu'en bas ;
# à droite des tuiles ; on vire les tuiles sous les consignes » ; ses choix : x1,25, consignes x1,23 de plus, deux
# colonnes) :
# - l'intérieur part de 2 300 : terrain et deux terrains passent à la ligne (mise en page ~2 546 à 2 559), notre
#   dispositif se pose sur le visualiseur avec son bouton (le panneau fusionné) ;
# - sous lui, les remplaçants (rangée « -seul », ses tuiles cachées), de 740 à 888 ;
# - les cases des consignes et du récapitulatif (grille de FM) dessinées x ZOOM_CONSIGNES_3440 depuis leur coin haut
#   gauche : leur bas (724) tombe au bas des remplaçants (888) ; le récapitulatif décalé de la largeur gagnée par les
#   consignes (804 x 0,2265), nos tuiles d'autant plus le récapitulatif (1 116 x 0,2265) ;
# - à droite : la colonne de la Vue d'ensemble en tuiles hautes (Efficacité, Centre des données) avec l'Entraînement à
#   la rangée, puis COL_3440_PETIT ; largeur : 1 624 + 253 + 2 x 324 = 2 525 pour ~2 546, x 1,25 = 3 156 pour ~3 182 ;
#   hauteur : 888 x 1,25 = 1 110 pour ~1 150.
# Pas dans la disposition miroir : la grille y est retournée (le décalage partirait dans l'autre sens) ; elle garde la v87
ECHELLE_3440_FUSION = 1.25
BASE_INTERIEUR_3440_FUSION = 2300
ZOOM_CONSIGNES_3440 = (ecran37.HAUT_TERRAIN_COUPE + ecran37.RANGEE(2)) / ecran37.HAUT_PANNEAU   # 888 / 724
DECALE_PHASES_3440 = 804 * (ZOOM_CONSIGNES_3440 - 1)              # les consignes : 10 colonnes de la grille
DECALE_TUILES_3440 = (804 + 312) * (ZOOM_CONSIGNES_3440 - 1)      # + le récapitulatif : 4 colonnes
ID_TRANSLATE = 327683   # StylePropertyId.Translate (deux longueurs ; comme kinito_cartes_jeunes)
TYPE_TYPE = 2           # v91 : StyleSelectorType.Type (le nom de la classe C# de l'élément)
# v91 (Kinito, 11/11, 3 440 Moyen hors match, ordre FM 27 : « terrain avec remplaçants en colonne 1, consignes en
# colonne 2, récap en colonne 3, tuiles en colonnes 4 et 5 », consignes et récap zoomés jusqu'au bas des remplaçants ;
# tuiles : les mêmes qu'en 3 440 Petit) : la rangée « -seul-moyen » sans ses tuiles (remplaçants seuls, 732 à 880), les
# deux cases x(880/724), à droite la colonne de la Vue d'ensemble (Efficacité, Centre, Entraînement) et la colonne 4
# (COL_3440_PETIT) ; pas d'agrandissement d'ensemble (en Moyen, aucune place en hauteur). Largeur : 1 624 + 240 +
# 2 x 324 = 2 512 pour ~2 613. En miroir, la v89 reste
ZOOM_CONSIGNES_3440_MOYEN = (ecran37.HAUT_RANGEE_MOYEN + ecran37.RANGEE(2)) / ecran37.HAUT_PANNEAU   # 880 / 724
# v93 (Kinito, v92 vue en 3 440 Petit et Moyen : « rapproche la tuile Entraînement de celle du dessus et aligne avec
# Consignes particulières ») : dans la colonne voisine, cinq petites tuiles (148) et leurs écarts (12) : la 5e commence à
# 640 ; l'Entraînement, à la rangée du Moyen (732), remonte de 92 (4 sous le Centre des données, 636)
MONTE_ENTRAINEMENT_3440 = 4 * (ecran37.RANGEE(2) + ecran37.ECART_TUILES) - ecran37.HAUT_RANGEE_MOYEN   # -92
# v88 (Kinito, 11/11, 2 560 Moyen hors match, vue FM24 : « pas moyen d'agrandir tout ? » ; en gardant tout, +3 % au plus,
# la colonne de droite touchant le bord ; son choix : retirer la colonne de droite et la rangée du bas) : sous les
# quatre classes (hors match, écran « 2560 x 1440 », Moyen, vue FM24), nos tuiles (Efficacité, Centre des données,
# Entraînement) et la bande cachées, l'enveloppe x1,2 (la largeur décide : la grille, 1 624 x 1,2 = 1 949 pour ~2 017 ;
# en hauteur 724 x 1,2 = 869 pour ~940 ; mise en page sur ~1 681, le terrain de Positionnement reste à la ligne : notre
# dispositif sur le visualiseur, avec son bouton, comme avant)
ECHELLE_2560_MOYEN = 1.23   # v89 (Kinito, v88 vue : « pas possible d'augmenter ? ») : sur sa capture, ~80 px libres à
#                             droite ; 1 624 x 1,23 = 1 998 pour ~2 017 à 2 039 (v88 : 1,2)
# v89 (Kinito, 11/11) : en 3 440 Grand et en 3 440 Moyen hors match, vue FM24, le visualiseur et le dispositif
# fusionnés (notre dispositif sur le visualiseur avec son bouton, comme en 2 560 Moyen) : l'intérieur part d'une base
# assez large pour que le terrain de Positionnement (490) passe à la ligne (Grand ~2 202 : 1 800 ; Moyen ~2 613 : 2 200),
# il garde ensuite toute la largeur. Grand : à droite de la grille, la colonne de nos tuiles en Efficacité tactique +
# Centre des données (~578 libres pour 324 ; pas de rangée en bas en Grand). Moyen : trois colonnes (~989 libres pour
# 972 : la 3e se cache d'elle-même si elle ne tient pas) et, en bas, les remplaçants sous le panneau puis rapport, CPA,
# capitaines (« -seul-moyen ») au lieu de la rangée de cinq
BASE_INTERIEUR_3440_GRAND = 1800
BASE_INTERIEUR_3440_MOYEN = 2200
# v88 (Kinito, 11/11, 2 560 Petit hors match, vue FM24 : « le visualiseur en choix sur le dispo, tout décaler, enlever
# la colonne Vue d'ensemble, une seule ligne de tuiles, remplaçants coupés au bas de la ligne ») : l'enveloppe x1,27 ;
# mise en page sur ~1 940 (2 463 / 1,27) : le terrain de Positionnement (2 114) et la colonne de tuiles passent à la
# ligne d'eux-mêmes, notre dispositif se pose sur le visualiseur avec son bouton (comme en 2 560 Moyen) ; nos tuiles
# et la bande « -petit » cachées, la rangée « -seul » montrée (remplaçants sur une rangée sous le panneau, rapport, CPA,
# capitaines). La hauteur décide : 740 + 148 + 3 = 891 x 1,27 = 1 132 pour ~1 150 (relevé sur sa capture de la v87 en
# 3 440 Petit, même hauteur) ; en largeur, la grille 1 624 x 1,27 = 2 062 pour ~2 463 (du vide à droite)
# v89 (Kinito, 11/11, v88 vue en 2 560 Petit : « on ajoute à droite Data hub, Efficacité, et Entraînement indiv si 3
# hautes passent ») : à droite de la grille, la colonne de nos tuiles (Moyen : Efficacité tactique et Centre des
# données, TUILES_HAUTES_MOYEN), sans la Vue d'ensemble ni le centre des données dessous. Trois tuiles hautes
# demandent 960 de haut pour ~905 : deux. La colonne demande 324 de large : sur sa capture, l'onglet fait ~2 444 de
# large (pas 2 463) ; à 1,27 il ne restait que ~301 à côté de la grille : 1,24 (mise en page sur ~1 970, il reste ~346)
ECHELLE_2560_PETIT = 1.24


def poser_3440(t, terrain, deux, bande, ajuste):
    """v87 : les règles du 3 440 Petit hors match (voir ECHELLE_3440), et celles de toutes les tailles qui remplacent
    le style intégré de la boîte des deux terrains (sa largeur, le bord gauche des terrains)"""
    C = TYPE_CLASSE

    def regle_c(valeurs, repere, chaines):
        idx = t.styles.add_rule(valeurs + [(-1, REPERE_REGLE_MIROIR, [(2, repere)])])
        t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [
            {"m_Specificity": 1 + sum(10 if ty == C else 100 for parts, _ in ch for ty, _ in parts),
             "m_Selectors": [{"m_Parts": [{"m_Value": v, "m_Type": ty} for ty, v in parts],
                              "m_PreviousRelationship": rel} for parts, rel in ch],
             "ruleIndex": idx} for ch in chaines]
    H = ([(C, ecran37.CLASSE_HORS_MATCH), (C, ecran37.CLASSE_3440), (C, ecran37.CLASSE_PETIT),
          (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    P = base.sm.PROPRIETES

    def sans_coupe(repere, hx):
        """v91 (Kinito, v90 vue en 3 440 Petit : le récapitulatif agrandi coupé net au bord de la grille, ~1 270 px sur
        sa capture = 1 624 x 1,25) : la grille de FM passe par une zone de défilement (SIScrollView) dont le cadre coupe
        ce qui dépasse (mesure FMSonde 0.28.0 du 11/11 : TeamInstructionsTabGrid > BindingRemapper >
        FixedAspectGridLayoutElement > SIScrollView > unity-content-and-vertical-scroll-container >
        unity-content-viewport > unity-content-container > GridLayoutElementContent > cases). Sous hx, overflow
        visible sur CETTE chaîne seulement, élément par élément (enfant direct à chaque pas, pas de joker : les zones de
        défilement DANS les blocs gardent leur coupe)"""
        pas = [(TYPE_NOM, "TeamInstructionsTabGrid"), (TYPE_TYPE, "BindingRemapper"),
               (TYPE_TYPE, "FixedAspectGridLayoutElement"), (TYPE_TYPE, "SIScrollView"),
               (TYPE_NOM, "unity-content-and-vertical-scroll-container"), (TYPE_NOM, "unity-content-viewport"),
               (TYPE_NOM, "unity-content-container"), (TYPE_NOM, "GridLayoutElementContent")]
        debut = [hx, ([(C, CLASSE_GRILLE)], DESCENDANT)]
        chaines = []
        for k in range(1, len(pas) + 1):
            chaines.append(debut + [([pas[0]], DESCENDANT)] + [([p], ENFANT) for p in pas[1:k]])
        regle_c([(P["overflow"][0], "", [(7, "visible")])], repere, chaines)

    def nom(n, rel=DESCENDANT):
        return ([(TYPE_NOM, n)], rel)

    def px(v):
        return (3, {"unit": 1, "value": float(v)})

    def pct(v):
        return (3, {"unit": 2, "value": float(v)})
    auto = (1, MOT_CLE_AUTO)
    # toutes tailles : ce que disait le style intégré (v71 à v86)
    regle_c([(P["width"][0], "", [px(ecran37.PLACE_DEUX24)])], 87.1, [[nom(deux, 0)]])
    regle_c([(P["left"][0], "", [px(ecran37.GAUCHE_DEUX24)])], 87.2, [[nom(f"{deux}-terrains", 0)]])
    # 3 440 Petit hors match. v90 : la v87 (les deux terrains, x1,2) ne reste que dans la disposition miroir ; dans
    # l'ordre FM 27, le panneau fusionné et les consignes zoomées (voir ECHELLE_3440_FUSION)
    if MIROIR24:
        regle_c([(P["width"][0], "", [px(PLACE_DEUX_3440)])], 87.3, [[H, nom(deux)]])
        regle_c([(P["left"][0], "", [px(GAUCHE_DEUX_3440)])], 87.4, [[H, nom(f"{deux}-terrains")]])
        regle_c([(P["right"][0], "", [auto]), (P["bottom"][0], "", [auto]),
                 (P["width"][0], "", [pct(100 / ECHELLE_3440)]), (P["height"][0], "", [pct(100 / ECHELLE_3440)])],
                87.5, [[H, nom(ajuste)]])
        regle_c([(ID_SCALE, "", [(2, ECHELLE_3440), (2, ECHELLE_3440)]),
                 (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])], 87.6, [[H, ([(C, CLASSE_FM24)], DESCENDANT)]])
        regle_c([(P["flex-basis"][0], "", [px(BASE_INTERIEUR_3440)])], 87.7,
                [[H, nom(f"{NOM_MIROIR}{FIN_INTERIEUR24}")]])
        regle_c([(P["display"][0], "", [(7, "none")])], 87.8,
                [[H, nom(x)] for x in (f"{NOM_MIROIR}{FIN_TUILES24}", f"{terrain}-remplacants-reglage",
                                       f"{deux}-terrains-tuiles", f"{deux}-terrains-fond", f"{bande}-petit")])
        regle_c([(P["display"][0], "", [(7, "flex")])], 87.9, [[H, nom(f"{bande}-grand")]])
    else:
        tz = f"{NOM_MIROIR}{FIN_TUILES24}"
        vz = f"{tz}-vde"
        regle_c([(P["right"][0], "", [auto]), (P["bottom"][0], "", [auto]),
                 (P["width"][0], "", [pct(100 / ECHELLE_3440_FUSION)]),
                 (P["height"][0], "", [pct(100 / ECHELLE_3440_FUSION)])], 90.0, [[H, nom(ajuste)]])
        regle_c([(ID_SCALE, "", [(2, ECHELLE_3440_FUSION), (2, ECHELLE_3440_FUSION)]),
                 (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])], 90.1, [[H, ([(C, CLASSE_FM24)], DESCENDANT)]])
        regle_c([(P["flex-basis"][0], "", [px(BASE_INTERIEUR_3440_FUSION)])], 90.2,
                [[H, nom(f"{NOM_MIROIR}{FIN_INTERIEUR24}")]])
        regle_c([(P["display"][0], "", [(7, "none")])], 90.3,
                [[H, nom(x)] for x in (f"{bande}-petit", f"{bande}-seul-tuiles", f"{vz}-fm", f"{vz}-tuiles")])
        regle_c([(P["display"][0], "", [(7, "flex")])], 90.4,
                [[H, nom(x)] for x in (f"{bande}-seul", f"{vz}-hautes", f"{vz}-tuiles-moyen", f"{tz}-col4")])
        grille = [([(C, CLASSE_GRILLE)], DESCENDANT), ([(TYPE_NOM, "TeamInstructionsTabGrid")], DESCENDANT),
                  ([(TYPE_NOM, "GridLayoutElementContent")], DESCENDANT)]
        zoom = [(ID_SCALE, "", [(2, ZOOM_CONSIGNES_3440), (2, ZOOM_CONSIGNES_3440)]),
                (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])]
        regle_c(zoom, 90.5, [[H] + grille + [([(TYPE_NOM, "TeamInstructionsBlock")], ENFANT)]])
        regle_c(zoom + [(ID_TRANSLATE, "", [px(DECALE_PHASES_3440), px(0)])], 90.6,
                [[H] + grille + [([(TYPE_NOM, "PhasesAndTeamInstructions")], ENFANT)]])
        regle_c([(P["margin-left"][0], "", [px(DECALE_TUILES_3440)])], 90.7, [[H, nom(tz)]])
        sans_coupe(91.6, H)   # v91
        # v93 (Kinito, v92 vue : « rapproche la tuile Entraînement de celle du dessus et aligne avec Consignes
        # particulières ») : sa zone (style intégré : padding-top, inaccessible aux règles) remontée par un décalage
        regle_c([(ID_TRANSLATE, "", [px(0), px(MONTE_ENTRAINEMENT_3440)])], 93.1, [[H, nom(f"{vz}-tuiles-moyen")]])
    # v88 (voir ECHELLE_2560_MOYEN) : 2 560 Moyen hors match, vue FM24
    H2 = ([(C, ecran37.CLASSE_HORS_MATCH), (C, ecran37.CLASSE_2560), (C, ecran37.CLASSE_ONGLET_MOYEN),
           (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    regle_c([(P["right"][0], "", [auto]), (P["bottom"][0], "", [auto]),
             (P["width"][0], "", [pct(100 / ECHELLE_2560_MOYEN)]),
             (P["height"][0], "", [pct(100 / ECHELLE_2560_MOYEN)])], 88.0, [[H2, nom(ajuste)]])
    regle_c([(ID_SCALE, "", [(2, ECHELLE_2560_MOYEN), (2, ECHELLE_2560_MOYEN)]),
             (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])], 88.1, [[H2, ([(C, CLASSE_FM24)], DESCENDANT)]])
    regle_c([(P["display"][0], "", [(7, "none")])], 88.2,
            [[H2, nom(x)] for x in (f"{NOM_MIROIR}{FIN_TUILES24}", bande)])
    # v88 (voir ECHELLE_2560_PETIT) : 2 560 Petit hors match, vue FM24
    vde = f"{NOM_MIROIR}{FIN_TUILES24}-vde"   # v89 : la boîte de la colonne (kinito_consignes_ecran.poser_vde24)
    H3 = ([(C, ecran37.CLASSE_HORS_MATCH), (C, ecran37.CLASSE_2560), (C, ecran37.CLASSE_PETIT),
           (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    regle_c([(P["right"][0], "", [auto]), (P["bottom"][0], "", [auto]),
             (P["width"][0], "", [pct(100 / ECHELLE_2560_PETIT)]),
             (P["height"][0], "", [pct(100 / ECHELLE_2560_PETIT)])], 88.3, [[H3, nom(ajuste)]])
    regle_c([(ID_SCALE, "", [(2, ECHELLE_2560_PETIT), (2, ECHELLE_2560_PETIT)]),
             (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])], 88.4, [[H3, ([(C, CLASSE_FM24)], DESCENDANT)]])
    # v92 : la colonne de la Vue d'ensemble cachée, la 5e (trois grandes tuiles, COL_2560_PETIT) à sa place ; les trois
    # petites de la rangée rapprochées (8 de chaque côté) et centrées entre les remplaçants et la colonne (Kinito)
    regle_c([(P["display"][0], "", [(7, "none")])], 88.5, [[H3, nom(x)] for x in (vde, f"{bande}-petit")])
    regle_c([(P["display"][0], "", [(7, "flex")])], 88.6,
            [[H3, nom(x)] for x in (f"{bande}-seul", f"{NOM_MIROIR}{FIN_TUILES24}-col5")])
    regle_c([(P["justify-content"][0], "", [(7, "center")])], 92.0, [[H3, nom(f"{bande}-seul-tuiles")]])
    regle_c([(P["margin-left"][0], "", [px(8)]), (P["margin-right"][0], "", [px(8)])], 92.1,
            [[H3, nom(f"{bande}-seul-tuiles-{i}")] for i in range(1, 1 + len(ecran37.BANDE24_2560))])   # v93 : nommées
    # v89 (voir BASE_INTERIEUR_3440_GRAND) : 3 440 Grand et 3 440 Moyen hors match, vue FM24, fusionnés
    inter = f"{NOM_MIROIR}{FIN_INTERIEUR24}"
    tuiles = f"{NOM_MIROIR}{FIN_TUILES24}"
    H4 = ([(C, ecran37.CLASSE_HORS_MATCH), (C, ecran37.CLASSE_3440), (C, ecran37.CLASSE_ONGLET_GRAND),
           (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    H5 = ([(C, ecran37.CLASSE_HORS_MATCH), (C, ecran37.CLASSE_3440), (C, ecran37.CLASSE_ONGLET_MOYEN),
           (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    regle_c([(P["flex-basis"][0], "", [px(BASE_INTERIEUR_3440_GRAND)])], 89.0, [[H4, nom(inter)]])
    regle_c([(P["display"][0], "", [(7, "none")])], 89.1, [[H4, nom(x)] for x in (f"{vde}-fm", f"{vde}-tuiles")])
    regle_c([(P["display"][0], "", [(7, "flex")])], 89.2, [[H4, nom(f"{vde}-hautes")]])
    regle_c([(P["flex-basis"][0], "", [px(BASE_INTERIEUR_3440_MOYEN)])], 89.3, [[H5, nom(inter)]])
    regle_c([(P["display"][0], "", [(7, "none")])], 89.5, [[H5, nom(f"{bande}-moyen")]])
    if MIROIR24:   # v91 : la v89 (trois colonnes, rapport / CPA / capitaines sous la grille) reste en miroir
        regle_c([(P["display"][0], "", [(7, "flex")])], 89.4,
                [[H5, nom(x)] for x in (f"{tuiles}-col2", f"{tuiles}-col3", f"{bande}-seul-moyen")])
    else:   # v91 (voir ZOOM_CONSIGNES_3440_MOYEN)
        regle_c([(P["display"][0], "", [(7, "flex")])], 91.0,
                [[H5, nom(x)] for x in (f"{tuiles}-col4", f"{bande}-seul-moyen")])
        regle_c([(P["display"][0], "", [(7, "none")])], 91.1, [[H5, nom(f"{bande}-seul-moyen-tuiles")]])
        grille_m = [([(C, CLASSE_GRILLE)], DESCENDANT), ([(TYPE_NOM, "TeamInstructionsTabGrid")], DESCENDANT),
                    ([(TYPE_NOM, "GridLayoutElementContent")], DESCENDANT)]
        zoom_m = [(ID_SCALE, "", [(2, ZOOM_CONSIGNES_3440_MOYEN), (2, ZOOM_CONSIGNES_3440_MOYEN)]),
                  (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])]
        regle_c(zoom_m, 91.2, [[H5] + grille_m + [([(TYPE_NOM, "TeamInstructionsBlock")], ENFANT)]])
        regle_c(zoom_m + [(ID_TRANSLATE, "", [px(804 * (ZOOM_CONSIGNES_3440_MOYEN - 1)), px(0)])], 91.3,
                [[H5] + grille_m + [([(TYPE_NOM, "PhasesAndTeamInstructions")], ENFANT)]])
        regle_c([(P["margin-left"][0], "", [px((804 + 312) * (ZOOM_CONSIGNES_3440_MOYEN - 1))])], 91.4,
                [[H5, nom(tuiles)]])
        sans_coupe(91.5, H5)
        regle_c([(ID_TRANSLATE, "", [px(0), px(MONTE_ENTRAINEMENT_3440)])], 93.2,
                [[H5, nom(f"{vde}-tuiles-moyen")]])   # v93 : comme en Petit


def poser_fm24_match(t, terrain, bande, ajuste):
    """v81, v82 : les règles de la vue FM24 en match (voir ECHELLE_MAX_MATCH24), dans la feuille de l'onglet"""
    C = TYPE_CLASSE

    def regle_c(valeurs, repere, chaines):
        idx = t.styles.add_rule(valeurs + [(-1, REPERE_REGLE_MIROIR, [(2, repere)])])
        t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [
            {"m_Specificity": 1 + sum(10 if ty == C else 100 for parts, _ in ch for ty, _ in parts),
             "m_Selectors": [{"m_Parts": [{"m_Value": v, "m_Type": ty} for ty, v in parts],
                              "m_PreviousRelationship": rel} for parts, rel in ch],
             "ruleIndex": idx} for ch in chaines]
    M = ([(C, ecran37.CLASSE_MATCH)], 0)
    MV = ([(C, ecran37.CLASSE_MATCH), (C, ecran37.CLASSE_ONGLET_FM24)], 0)
    F = ([(C, CLASSE_FM24)], DESCENDANT)
    A = ([(TYPE_NOM, ajuste)], DESCENDANT)
    P = base.sm.PROPRIETES

    def px(v):
        return (3, {"unit": 1, "value": float(v)})
    # l'ajusteur : toute la place (hors match, et en match hors vue FM24) ; dessiné plus grand en match et en vue FM24
    # v83 : l'ajusteur est en absolu (left, top, right 0 : poser_tuiles24) ; son bas ici : 0 (toute la place), et en
    # match en vue FM24, « auto » et la hauteur dessinée
    regle_c([(P["bottom"][0], "", [px(0)])], 82.0, [[([(TYPE_NOM, ajuste)], 0)]])
    regle_c([(P["bottom"][0], "", [(1, MOT_CLE_AUTO)]),
             (P["height"][0], "", [px(ECHELLE_MAX_MATCH24 * HAUT_LIGNE_MATCH24)])], 82.1, [[MV, A]])
    regle_c([(ID_SCALE, "", [(2, ECHELLE_MAX_MATCH24), (2, ECHELLE_MAX_MATCH24)]),
             (ecran37.ID_ORIGINE, "", [(7, "left"), (7, "top")])], 82.2, [[M, F]])
    regle_c([(P["display"][0], "", [(7, "none")])], 81.3,
            [[M, ([(TYPE_NOM, nom)], DESCENDANT)]
             for nom in (f"{NOM_MIROIR}{FIN_TUILES24}", bande, f"{terrain}-remplacants-reglage")])
    regle_c([(P["flex-basis"][0], "", [px(BASE_INTERIEUR_MATCH)])], 82.4,
            [[M, F, ([(TYPE_NOM, f"{NOM_MIROIR}{FIN_INTERIEUR24}")], ENFANT)]])
    # v94 (Kinito, 11/11, v93 en match en 1080p : « je peux scroller, je ne sais pas pourquoi ») : l'onglet est une case
    # de la grille de FM, qui défile (SIScrollView) ; l'enveloppe remplissait tout l'ajusteur (1 137 de haut pour 745
    # utiles), dessinée x1,5 puis réduite : 982 pour un onglet de 643 (sa mesure FMSonde : 1080p en match). Plafonnée à
    # HAUT_LIGNE_MATCH24 (son style intégré met la hauteur à « auto » : un plafond par règle), elle fait pile la hauteur
    # de l'onglet une fois dessinée ; la grille garde 725 pour ses blocs (724)
    regle_c([(P["max-height"][0], "", [px(HAUT_LIGNE_MATCH24)])], 94.0, [[MV, F]])


# v73 (Kinito, 11/11 : « couper la colonne du visualiseur en dessous du terrain en laissant la même marge que côté droit
# et gauche », en vue FM24 et en vue Terrain ; en vue FM24, des tuiles dessous) : dans notre bloc du terrain (PITCH24),
# sous le réglage du miroir, un 2e réglage qui pose CLASSE_VUE_TERRAIN en vue Terrain ; nos règles (feuille du bloc)
# plafonnent le panneau de FM (tactics-collapsable-pitch-container) à HAUT_PANNEAU en vue FM24 (CLASSE_MIROIR) et en
# vue Terrain, jamais en vue Tuiles ; en vue FM24 seulement, une colonne de tuiles dessous
CLASSE_VUE_TERRAIN = "kinito-consignes-vue-terrain"
PANNEAU_FM = "tactics-collapsable-pitch-container"


def poser_bas_visualiseur(t, src, tb):
    """v73 : la coupe du visualiseur et ses tuiles (voir CLASSE_VUE_TERRAIN) ; rend le nombre de tuiles. v74 : la coupe
    seule (les tuiles sont dans la bande de la vue FM24)"""
    reg = first(t, lambda r: t.name(r) == f"{NOM_MIROIR}-terrain")
    inst = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "TacticalPlannerPhasesPitches")
    if reg is None or inst is None:
        raise ValueError(f"{PITCH24} : réglage du miroir ou terrain de FM (introuvables)")
    contenu = list(t.children(reg))
    vt = reglage_miroir(t, src, reg, f"{NOM_MIROIR}-terrain-vue1", {"flex-grow": 1, "flex-direction": "column"},
                        index=0, classe=CLASSE_VUE_TERRAIN, vue=ecran37.VUE_TERRAIN)
    for j, k in enumerate(contenu):
        base.deplacer(t, k, vt, j)
    hauteur = base.sm.PROPRIETES["max-height"][0]
    ecran37.regle_selecteurs(t, [(hauteur, "", [(3, {"unit": 1, "value": float(ecran37.HAUT_PANNEAU)})])], 73.0,
                             [[(TYPE_CLASSE, classe, 0), (TYPE_CLASSE, PANNEAU_FM, DESCENDANT)]
                              for classe in (CLASSE_GRILLE, CLASSE_VUE_TERRAIN)])   # v79 : CLASSE_GRILLE
    ecran37.attacher_feuille(t, reg)
    return 0


def segments_choix(t, src, parent, nom, variable, css):
    """v76 : « Dispositif | Visualiseur » : les boutons segmentés des cartes de chaleur recopiés (comme « Tuiles |
    Terrain », kinito_consignes_essai.bascule) : le bouton du milieu retiré, chacun allumé quand variable vaut 0 / 1 et
    l'y mettant au clic, son texte fixe ; en absolu (css)"""
    th = src.th
    seg = t.clone(src.segments, parent, src=th)
    t.styles.copy_from(th.styles, t, seg)
    recaler_parent(t, seg)
    sd = t.sd(seg)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{base.PREFIXE}-{nom}", 1
    reglages = t.children(seg)
    if len(reglages) != 3 or any(typ(t, r) != "SIStyleSetter" for r in reglages):
        raise ValueError("boutons segmentés des cartes de chaleur : forme inattendue (introuvable)")
    t.remove(reglages[1])   # le bouton du milieu
    for reglage, valeur, const, drapeau, mot, cle in (
            (reglages[0], 0, "const.Zero", 0, langue.texte("Dispositif", "Shape"), "dispositif"),
            (reglages[2], 1, "const.One", 1, langue.texte("Visualiseur", "Visualiser"), "visualiseur")):
        rs = t.sd(reglage)
        rs["name"], rs["name_UxmlAttributeFlags"] = f"{base.PREFIXE}-{nom}-allume-{cle}", 1
        args = decode_args(rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
        chemins = entiers = 0
        for a in args:
            if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]"):
                a[1] = bytes([1, len(variable)]) + variable.encode()
                chemins += 1
            elif bytes(a[0]).endswith(b"Int32VisualArg"):
                a[1] = struct.pack("<i", valeur)
                entiers += 1
        if (chemins, entiers) != (1, 1):
            raise ValueError("réglage d'un bouton segmenté : arguments inattendus (introuvable)")
        rs["BindFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        bouton = t.children(reglage)[0]
        bs = t.sd(bouton)
        bs["name"], bs["name_UxmlAttributeFlags"] = f"{base.PREFIXE}-{nom}-bouton-{cle}", 1
        bs["Events"], bs["Events_UxmlAttributeFlags"] = {"m_bytes": liste([copier(const, variable, drapeau)])}, 1
        clavier = [k for k in t.walk(bouton) if k != bouton and t.name(k) == "controllers-keyboard-container"]
        for k in clavier:   # raccourci clavier de FM : pas le nôtre (relevés d'abord)
            if k in t.refs and t.refs[k] is not None:
                t.remove(k)
        texte = next((k for k in t.children(bouton) if typ(t, k) == "SIText"), None)
        if texte is None:
            raise ValueError("texte d'un bouton segmenté (introuvable)")
        t.elem(texte)["m_Classes"] = [c for c in t.elem(texte)["m_Classes"] if c != "margin-right-global-gap-regular"]
        texte_fige(t, texte, mot)
    t.styles.style(t, seg, {"position": "absolute", **css})
    return seg


ecran37.REGLAGE = reglage_miroir   # v75
ecran37.BOUTON = bouton_choix
ecran37.SEGMENTS = segments_choix   # v76


def regle_tuiles(t):
    """v52 : les numéros de nos règles à sélecteurs (tuiles en option) dans la feuille intégrée"""
    return [i for i, rg in enumerate(t.styles.sh["m_Rules"])
            if any(pr.get("m_CustomName") == REPERE_REGLE_MIROIR for pr in rg["m_Properties"])]


def hote_miroir(t):
    """l'élément d'un bloc sous lequel se pose le miroir : celui qui reçoit les paramètres de l'onglet (un BindingExpect,
    ou l'élément qui porte un BindingExpectComponent : notre vue n'est vue qu'en dessous, comme « selectedphase ») ;
    sans lui (le bloc du terrain), la racine. Lu le 06/11 : bloc des consignes = TutorialAnchorElement >
    ComponentElement (BindingExpectComponent) ; colonne de droite = BindingExpect ; terrain = TutorialAnchorElement >
    le modèle TacticalPlannerPhasesPitches"""
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    h = racine
    for _ in range(4):
        if typ(t, h) == "BindingExpect" or any(typ(t, k) == "BindingExpectComponent" for k in t.children(h)):
            return h
        ks = [k for k in t.children(h) if not (t.elem(k).get("m_FullTypeName") or "").endswith("Component")]
        if len(ks) != 1 or not t.children(ks[0]):
            break
        h = ks[0]
    return racine


def poser_miroir_bloc(t, src, nom, classe=None):
    """sous l'hôte d'un bloc (hote_miroir) : réglage (retourné en vue FM24) > le contenu d'avant"""
    racine = hote_miroir(t)
    enfants = [k for k in t.children(racine) if not (t.elem(k).get("m_FullTypeName") or "").endswith("Component")]
    if not enfants:
        raise ValueError(f"bloc {nom} : racine sans contenu (introuvable)")
    reg = reglage_miroir(t, src, racine, f"{NOM_MIROIR}-{nom}", {"flex-grow": 1, "flex-direction": "column"},
                         index=t.children(racine).index(enfants[0]), classe=classe)   # v79 : classe
    for k in enfants:
        base.deplacer(t, k, reg, len(t.children(reg)))


def retirer_miroir(t):
    """nos réglages du miroir (toutes versions) retirés, ce qu'ils contenaient remis à leur place ; rend True s'il y en
    avait"""
    def ancetre_miroir(r):
        p = t.parent.get(r)
        while p is not None:
            if est_miroir(t.name(p)):
                return True
            p = t.parent.get(p)
        return False
    # v66 : d'abord l'enveloppe des tuiles de la vue FM24 (FIN_ENVELOPPE24) : ses tuiles (FIN_TUILES24) partent, le
    # reste (le réglage de la grille, avec la grille de FM) remonte à sa place ; puis le retrait d'avant
    # v69 : nos tuiles et le terrain de Positionnement partent (où qu'ils soient dans l'enveloppe), ce que contient
    # l'intérieur (FIN_INTERIEUR24, v69 ; avant, l'enveloppe elle-même) remonte
    for env in [r for r in t.walk() if est_miroir(t.name(r)) and t.name(r).endswith(FIN_ENVELOPPE24)]:
        for k in [k for k in t.walk(env) if k != env and est_miroir(t.name(k))
                  and t.name(k).endswith((FIN_TUILES24, FIN_TERRAIN24, FIN_DEUX24, FIN_BANDE24, FIN_SEUL24))]:
            t.remove(k)
        gardes = []
        for k in t.children(env):
            gardes += list(t.children(k)) if t.name(k).endswith(FIN_INTERIEUR24) else [k]
        p = t.parent[env]
        i = t.children(p).index(env)
        for j, k in enumerate(gardes):
            base.deplacer(t, k, p, i + j)
        t.remove(env)
        ecran37.nettoyer_modeles(t)
    hauts = [r for r in t.walk() if est_miroir(t.name(r)) and not ancetre_miroir(r)]
    for h in hauts:
        c = h
        while True:
            ks = t.children(c)
            if len(ks) == 1 and est_miroir(t.name(ks[0])):
                c = ks[0]
                continue
            break
        contenu = [k for k in t.children(c) if not est_miroir(t.name(k))]
        p = t.parent[h]
        i = t.children(p).index(h)
        for j, k in enumerate(contenu):
            base.deplacer(t, k, p, i + j)
        t.remove(h)
    ecran37.nettoyer_modeles(t)   # v73 : les tuiles sous le visualiseur (bloc du terrain) partent avec le réglage
    return bool(hauts)


def miroir_pose(o):
    return o is not None and any(t_nom.startswith(NOM_MIROIR) for t_nom in (o[3].name(r) for r in o[3].walk()))


_retirer_essai_base = base.retirer_essai


def retirer_essai_b(o):
    """v20 : notre déclaration de variables du bloc ne nomme plus la vue (kinitovue) : retirée ici (reconnue à
    l'ordre des colonnes) ; nos paramètres attendus ôtés ; puis le retrait de 26.13. v46 : d'abord le miroir (ses boîtes
    contiennent des éléments de FM, que le retrait de 26.13 emporterait)"""
    t = o[3]
    retirer_miroir(t)
    for r in composant_variables(t, V_ORDRE):
        if not any(f"{{{base.VARIABLE}}}" in (p.get("value") or "") for p in t.elem(r).get("m_Properties") or []):
            oter_composant(t, r)
    attentes(t, retirer=True)
    _retirer_essai_base(o)


def ouvrir_trois():
    return ouvrir(base.BLOC), ouvrir(PARENT24), ouvrir(DROITE24)


def cmd_appliquer_b():
    o, oe, od = ouvrir_trois()
    if None in (o, oe, od):
        print(f"[Kinito] Consignes (essai) : {base.BLOC}, {PARENT24} ou {DROITE24} introuvable (renommé par une mise à "
              "jour ?), ignoré")
        return
    oi = ouvrir(INDIV24)   # v30 : le bloc de gauche des consignes individuelles
    ot = ouvrir(INDIV_TUILE24)   # v31 : la dernière tuile créée avec le ballon
    oc = ouvrir(CARTE_INDIV24)   # v33 : la fiche (le choix FM 27 / FM24)
    ox = ouvrir(EXTRA24)   # v40 : la ligne du haut (le bouton FM 27 / FM24)
    # v46 : le bloc du terrain (le miroir) ; v48 : ouvert aussi sans miroir, pour retirer celui d'une version d'avant
    # (vu au banc : passer de « miroir » à « fm27 » laissait le miroir du terrain)
    op = ouvrir(PITCH24)

    def miroir_juste(x, attendu=MIROIR24):   # v48 : notre miroir à jour si l'option le veut, aucun miroir sinon
        if x is None:                         # v79 : l'onglet et le bloc du terrain l'ont dans les deux ordres
            return True
        return miroir_pose(x) if attendu else not any(est_miroir(x[3].name(r)) for r in x[3].walk())
    if any(o[3].name(r) == base.NOM for r in base.marques(o[3])) and composant_variables(oe[3], V_PHASE24) \
            and any(od[3].name(r) == NOM_DROITE for r in od[3].walk()) \
            and (oi is None or any(oi[3].name(r) == NOM_INDIV for r in oi[3].walk())) \
            and (ot is None or any(ot[3].name(r) == NOM_INDIV_TUILE for r in ot[3].walk())) \
            and (oc is None or None in (oi, ot) or carte_posee(oc)) \
            and (ox is None or any(ox[3].name(r) == NOM_EXTRA for r in ox[3].walk())) \
            and ecran37.pose(oe, VERSION) \
            and all(miroir_juste(x) for x in (o, od)) and all(miroir_juste(x, True) for x in (oe, op)):
        print("[Kinito] Consignes (essai) : déjà appliqué")
    else:
        src = base.Sources()
        if not src.ok():
            print("[Kinito] Consignes (essai) : morceaux de FM introuvables (fenêtres Progression / Courses de soutien), "
                  "rien enregistré")
            return
        base.retirer_essai(o)   # une ancienne version, s'il y en a une (v46 : son miroir compris)
        retirer_ecran(oe)
        retirer_miroir(oe[3])   # v46
        ranger_feuille(oe)
        retirer_miroir(od[3])   # v46
        retirer_droite(od)
        attentes(od[3], retirer=True)
        ranger_feuille(od)
        for x in [op] if op is not None else []:   # v46 (et toute version d'avant)
            retirer_miroir(x[3])
            ranger_feuille(x)
        retirer_tout_indiv(oi, ot, oc, ox)   # v30-v40
        msgs = base.construire(o[3], src)
        if not any("introuvable" in m for m in msgs):
            try:
                msgs += poser_ecran(oe, src) + poser_droite(od, src, o[3])
            except (ValueError, KeyError, IndexError, StopIteration) as e:
                msgs.append(f"colonne de droite : {e} (introuvable)")
            if not any("introuvable" in m for m in msgs):   # v54 : l'écran plein de la vue Terrain (ESSAI)
                try:
                    msgs += ecran37.poser(oe, src, o[3], VERSION)
                except (ValueError, KeyError, IndexError, StopIteration, TypeError) as e:
                    msgs.append(f"écran plein : {type(e).__name__} {e} (introuvable)")
            if not attentes(o[3]) or not attentes(od[3]):
                msgs.append(f"paramètres attendus ({ATTENDU_MODELE}) des blocs (introuvables)")
            msgs += poser_tout_indiv(oi, ot, oc, src, o[3], ox)   # v33 ; v40 : ox
            if not any("introuvable" in m for m in msgs):   # v46 : le miroir ; v79 : et l'ordre FM 27
                if op is None:
                    msgs.append(f"{PITCH24} (introuvable)")
                else:
                    try:
                        poser_miroir_grille(oe[3], src)
                        if MIROIR24:
                            poser_miroir_tuiles(oe[3])   # v52
                        n24 = poser_tuiles24(oe[3], src, o[3])   # v66
                        if MIROIR24:   # v79 : retournés une 2e fois seulement si la grille l'est
                            poser_miroir_bloc(o[3], src, "consignes")
                            poser_miroir_bloc(od[3], src, "phases")
                        poser_miroir_bloc(op[3], src, "terrain", classe=None if MIROIR24 else CLASSE_GRILLE24)
                        n24 += poser_bas_visualiseur(op[3], src, o[3])   # v73
                        msgs.append("vue FM24 : l'onglet " + ("en miroir (colonne des phases à gauche, terrain à droite"
                                                             if MIROIR24 else "dans l'ordre FM 27 (terrain à gauche")
                                    + f" ; en grand écran, la grille plafonnée et nos {n24} tuiles ; en très grand "
                                    "écran, le terrain de Positionnement à gauche), VERSION DE TEST")
                        attendu = sum(len(c) for c in ecran37.BANDE24 + ecran37.TUILES_SOUS_VDE
                                      + ecran37.BANDE24_MOYEN + ecran37.TUILES_SOUS_VDE_MOYEN
                                      + ecran37.TUILES_HAUTES_MOYEN + ecran37.BANDE24_3440
                                      + ecran37.BANDE24_2560 + ecran37.BANDE24_2560) \
                            + len(ecran37.COL_3440_PETIT) + len(ecran37.COL_2560_PETIT) \
                            + len(ecran37.TUILES_SOUS_DEUX24) \
                            + sum(len(h) + len(r) for h, r in ecran37.COLS_3440_MOYEN)   # v76, v89
                        if n24 != attendu:   # v73
                            msgs.append(f"vue FM24 : {n24} tuiles sur {attendu} (introuvables)")
                    except (ValueError, KeyError, IndexError, StopIteration) as e:
                        msgs.append(f"miroir : {e} (introuvable)")
        for m in msgs:
            print(f"[Kinito] Consignes (essai) : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Consignes (essai) : rien enregistré")
            return
        for x in (o, oe, od) + tuple(y for y in (oi, ot, oc, ox, op) if y is not None):   # v46 : op
            base.enregistrer(*x)
        base.nb.save_all()
    if not base.nb.DRY_RUN:
        with open(base.MARKER, "w", encoding="utf-8") as f:
            base.json.dump({"actif": True}, f)
        autre = os.path.join(os.path.dirname(base.MARKER), base.AUTRE_MARQUEUR)   # v26 : l'autre version n'est plus active
        if os.path.exists(autre):
            os.remove(autre)


def cmd_retirer_b():
    if os.path.exists(base.MARKER) and not base.nb.DRY_RUN:
        os.remove(base.MARKER)
    o, oe, od = ouvrir_trois()
    rien = True
    if o is not None and any(base.est_racine(o[3].name(r)) for r in base.marques(o[3])):
        base.retirer_essai(o)
        base.enregistrer(*o)
        rien = False
    if oe is not None and (retirer_ecran(oe) | retirer_miroir(oe[3])):   # v46 : et le miroir
        ranger_feuille(oe)
        base.enregistrer(*oe)
        rien = False
    if od is not None and (retirer_miroir(od[3]) | retirer_droite(od) | bool(attentes(od[3], retirer=True))):
        ranger_feuille(od)
        base.enregistrer(*od)
        rien = False
    op = ouvrir(PITCH24)   # v46
    if op is not None and retirer_miroir(op[3]):
        ranger_feuille(op)
        base.enregistrer(*op)
        rien = False
    for x in retirer_tout_indiv(ouvrir(INDIV24), ouvrir(INDIV_TUILE24), ouvrir(CARTE_INDIV24),
                                ouvrir(EXTRA24)):   # v30-v40
        base.enregistrer(*x)
        rien = False
    if rien:
        print("rien à retirer")
        return
    base.nb.save_all()
    print(f"{base.BLOC}, {PARENT24}, {DROITE24}, {PITCH24}, {INDIV24}, {INDIV_TUILE24}, {CARTE_INDIV24} : essai retiré "
          "(le reste des blocs n'est pas touché)")


def cmd_etat_b():
    base_etat()
    o, oe, od = ouvrir_trois()
    if oe is not None:
        print(f"{PARENT24} : " + ("vue et phase FM24 déclarées" if composant_variables(oe[3], V_PHASE24) else
                                  "rien de nous"))
        n = len(regle_tuiles(oe[3]))   # v52
        if n or miroir_pose(oe):
            print(f"{PARENT24} : règle des tuiles en option du grand écran : {n}")
        print(f"{PARENT24} : écran plein de la vue Terrain : " + (   # v54
            "présent (à jour)" if ecran37.pose(oe, VERSION) else
            ("ANCIENNE version" if any(ecran37.est_racine(oe[3].name(r)) for r in oe[3].walk()) else "absent")))
    if od is not None:
        print(f"{DROITE24} : " + ("cartes des phases FM24 présentes (à jour)" if any(
            od[3].name(r) == NOM_DROITE for r in od[3].walk()) else
            ("ANCIENNE version" if any(est_droite(od[3].name(r)) for r in od[3].walk())
             else "rien de nous")))
    for modele, nom in ((INDIV24, NOM_INDIV), (INDIV_TUILE24, NOM_INDIV_TUILE), (EXTRA24, NOM_EXTRA)):   # v30-v40
        x = ouvrir(modele)
        if x is not None:
            print(f"{modele} : " + ("vue FM24 des consignes individuelles présente (à jour)" if any(
                x[3].name(r) == nom for r in x[3].walk()) else
                ("ANCIENNE version" if any(est_indiv(x[3].name(r)) for r in x[3].walk()) else "rien de nous")))
    oc = ouvrir(CARTE_INDIV24)   # v33
    if oc is not None:
        print(f"{CARTE_INDIV24} : " + ("choix FM 27 / FM24 déclaré" if carte_posee(oc) else "rien de nous"))
    op = ouvrir(PITCH24)   # v46
    if op is not None:
        print(f"{PITCH24} : " + ("miroir de la vue FM24 (à jour)" if miroir_pose(op) else
                                 ("ANCIEN miroir" if any(est_miroir(op[3].name(r)) for r in op[3].walk())
                                  else "rien de nous")))


base_etat = base.cmd_etat


def bulles_equipe24(fab, racine24):
    """v38 (Kinito : « même chose pour les consignes d'équipe ») : dans la vue FM24 des consignes d'équipe, l'infobulle
    de FM (v16 : dans le bouton même) avec l'explication de l'option (CHEMIN_DESC_EQUIPE24), sur chaque bouton
    d'option qui n'en a pas : ceux que déclare un BindingSetter « id » (Fab.option, Fab.nom_option)"""
    t, src = fab.t, fab.src
    n = 0
    for r in list(t.walk(racine24)):
        if typ(t, r) != "SIButton" or any(typ(t, k) == "Tooltip" for k in t.children(r)):
            continue
        p, option = r, False
        while p in t.parent:
            p = t.parent[p]
            if any(v.get("m_name") == "id" for v in t.sd(p).get("ValueVariables") or []):
                option = True
                break
            if p == racine24:
                break
        if not option:
            continue
        bu = t.clone(src.bulle, r, src=src.tu)
        t.styles.copy_from(src.tu.styles, t, bu)
        recaler_parent(t, bu)
        fab._nom(bu, f"fm24-bulle-{n}")
        base.texte_lie(t, t.children(bu)[0], CHEMIN_DESC_EQUIPE24, "explication")
        n += 1
    return n


def terrain_b(fab, racine):
    """la vue « Terrain » de 26.14 : avec le ballon : avec_b() (v7 ; avant : les noms des phases tout en haut, une
    rangée de tuiles, les trois terrains, une rangée de tuiles) ; sans le ballon : sans_b(). v19 : puis la vue FM24
    (vue_fm24), 3e vue de l'interrupteur"""
    t = fab.t
    declarer(fab, racine)   # v6 : l'ordre des colonnes, les haut / bas, ce qui est retenu
    ote_vue_du_bloc(fab, racine)   # v20 : la vue est déclarée par l'onglet (poser_ecran)
    vue_comme_ensemble(fab)   # v9 : « Cartes / Terrain » à l'allure de « Vue d'ensemble »
    partir_de_zero(fab)       # v10 : bouton « Partir de zéro » (en-tête) et sa fenêtre (par-dessus tout le bloc)
    t.styles.style(t, racine, {"flex-grow": 1, "flex-direction": "column"})
    cadre = cadre_proportions(fab, racine, "terrain-proportions")   # v52
    pos = fab.interrupteur(cadre, "possession", "inpossession", css={"flex-grow": 1})
    sans_b(fab, fab.boite(pos, "sans", css={"flex-grow": 1, "flex-direction": "column"}))   # rang 0 : sans le ballon
    avec_b(fab, fab.boite(pos, "avec", css={"flex-grow": 1, "flex-direction": "column"}))     # rang 1 : avec (v7)
    bulles_equipe24(fab, vue_fm24(fab, racine))   # v19 ; v38 : les explications en infobulle


def main(argv):
    """26.13 fait tout ; on lui donne nos noms, notre marque et notre disposition"""
    base.VERSION, base.NOM, base.RACINE = VERSION, NOM, RACINE
    base.MARKER, base.AUTRE_MARQUEUR = MARKER, AUTRE_MARQUEUR
    base.terrain = terrain_b
    base.retirer_essai = retirer_essai_b   # v20 : et l'onglet (TacticalPlannerTeamInstructions), la colonne de droite
    base.cmd_appliquer, base.cmd_retirer, base.cmd_etat = cmd_appliquer_b, cmd_retirer_b, cmd_etat_b
    # v12 (Kinito) : « Tuiles » au lieu de « Cartes » (même bouton, même vue : les cartes de FM), dans chaque langue
    manque = [lg for lg, _ in base.VUES_LANGUES if lg not in TUILES_LANGUES]
    if manque:
        raise ValueError(f"« Tuiles » sans traduction pour : {manque}")
    base.TEXTES_VUES = [TEXTE_TUILES, base.TEXTES_VUES[1]]
    base.VUES_LANGUES = [(lg, (TUILES_LANGUES[lg], mots[1])) for lg, mots in base.VUES_LANGUES]
    base.main(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
