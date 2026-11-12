"""[AJOUT KINITO] Entraînement > Entraîn. individuel, vue Détails : la liste de gauche plus large, le bloc du joueur
d'autant plus étroit : 38 % de l'écran au lieu de 30 % (texte Petit, Normal, Grand), 33 % avec le texte en Plus grand,
en mode Large de l'affichage des informations seulement (v3) ; en Medium et Small, les 30 % de FM. Le tableau Détails
s'ouvre trié par la note à l'entraînement, la meilleure en haut (v4 ; FM : par poste ; un clic sur un en-tête change
toujours le tri).
But (Kinito, 12/11/2026) : de la place pour ajouter des colonnes au tableau de gauche ensuite ; « essaie 33 % en plus
grand, 38 % dans les autres », dans un ajout à part (26.15), pas dans 26.14.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu.

Comment (tout mesuré le 12/11/2026) :
- L'ÉCRAN : TeamIndividualTrainingBlock (propriétaire : entrainement_individuel_equipes d'Alex ; 26.14 y ajoute aussi
  ses morceaux, par leur nom). Vue Détails = la rangée #frame : [le bloc de la liste : ComponentElement, classe de FM
  width-30-percent] [séparateur] [le bloc du joueur : BindableSwitchElement, flex-grow-class]. Le bloc du joueur prend
  ce qui reste : élargir la liste le rétrécit. La vue Résumé (#List) est déjà pleine largeur : rien n'y change.
- LES LARGEURS : classes de FM width-33-percent et width-38-percent (règles globales, 131105 = 33 % / 38 %, lues par
  regles_selecteur.py).
- SELON LA TAILLE DU TEXTE : une boîte = le SIStyleSetter d'un bouton segmenté des cartes de chaleur de FM
  (HeatMapsMatch_Block), vidé, comme 26.13 et 26.14 (vu en jeu) ; sa fonction BindIntComparisonToAOrBUssClass
  (140747f1) compare settings.TextScaling (85 / 100 / 110 / 120 = Petit / Normal / Grand / Plus grand) à 120 (>=) :
  classe A width-33-percent, sinon B width-38-percent, posée sur son PARENT (entrées de la fonction, lues dans son
  graphe : Binding, CamparisonOperator, CompareTo, StyleA, StyleB, ApplyToChildInstead, ApplyToParentInctead ; la
  dernière à vrai) ; SetClassStyle retire la classe d'avant à chaque changement. La boîte est le dernier enfant du bloc
  de la liste, en absolu et sans taille (elle ne prend aucune place). La classe width-30-percent de FM est retirée du
  bloc (deux classes de largeur se battraient) ; retirer remet les classes de l'original et enlève la boîte.
- SEULEMENT EN MODE LARGE (v3, Kinito le 14/10 : « réserve le 38-33 au mode Large, laisse les autres ajouts ») : le
  réglage « Information Display » des préférences (Large / Medium / Small) est settings.AdaptiveScalingLevelIndex,
  0 / 1 / 2 (lu dans AdaptiveLayoutPreferences : ses trois boutons écrivent dans ce chemin les variables Int Large 0,
  Medium 1, Small 2 de leur groupe #buttons). Deux conditions à la fois : la boîte v2 n'en sait qu'une. Dans le bloc
  de la liste : une variable Bool kinito-liste-mode-large (un BindingVariablesComponent, celui de HeatMapsMatch_Block
  recopié comme 26.13 v4 : élément rangé après les composants du bloc, « value-vars », et ses données dans la liste
  m_components du bloc ; la variable vaut pour tout le bloc ; sans nom, retirer le reconnaît à sa déclaration) ; puis,
  sans place (absolus, 0 x 0), son écrivain (le BindingSetter
  data-to-send-setter de TacticTeamInstructionMultipleChoiceOptionButton, le même que 26.13 vu en jeu, sa fonction
  BindAndSetToDestinationResultOfIntComparison ffe24c8d : variable = (mode == 0) ; il écrit dans la variable du bloc,
  déclarée plus haut que lui, comme OptionalsDefaulter de FM (PlayerInstructionsCard) écrit inpossession) ; et trois
  boîtes (le SIStyleSetter de PlayerOverviewPositionCell, fonction BindIntAndBoolToStyle e86de172 : classe si (entier
  OP valeur) ET (booléen OU-EXCLUSIF inverser), "" sinon, comme FM) : 33 % si texte >= 120 et Large, 38 % si < 120 et
  Large, width-30-percent de FM si pas Large. Une seule classe de largeur à la fois. Si l'écrivain n'écrivait pas, la
  variable resterait fausse : 30 % partout (l'écran de FM), jamais un bloc sans largeur. Les colonnes (ci-dessous)
  restent dans tous les modes (Kinito).
- LE TRI DE DÉPART (v4, Kinito le 14/10 : « toujours trié par note décroissante quand on entre ; on peut changer si on
  veut ») : le StreamedTable de la vue Détails (#Table, dans le bloc de la liste) a les champs de FM SortedColumn
  (FM : "position", drapeau 1) et SortAscending (0, drapeau 1) ; posés à "training-rating" et 0. SortAscending 0 =
  l'ordre du premier clic sur l'en-tête, la plus forte valeur en haut (relevé dans les tableaux de FM : "date",
  "lastsaved", "potential-ability-stars" à 0 = le plus récent / le plus fort en haut). Le tableau Résumé (#List) n'a
  pas de tri de départ chez FM : pas touché jusqu'à la v9 ; v10 (04/11/2026) : même tri de départ, et un
  SharedPersistenceID pour que FM garde le tri choisi (voir VERSION). Retirer rend ces champs d'après l'original.
- Ce qui se coupe dans le bloc du joueur, plus étroit (mesuré sur une capture de Kinito en Plus grand) : le vide entre
  le nom du joueur et « Niveau actuel » ; un nom très long n'a pas de règle de coupure dans l'en-tête de FM
  (IndividualTrainingPlayerHeaderContent : pas d'ellipse) ; des noms d'attributs plus souvent coupés en Plus grand.

- LES COLONNES (v2, Kinito le 14/10, la v1 vue en jeu : « écourte la colonne du nom un peu ; Personnalité et
  Rapports médias avant la note d'entraînement ; la note réduite au maximum, la plus longue entière ; Position plus
  étroite ») : la vue du tableau Détails, IndividualTrainingDetailedViewTable (ui-tableviews, citée par ce seul
  écran ; entrainement_pouces d'Alex y ajoute ses pouces et repart de l'original quand il s'applique), et sa fabrique
  PlayerIndividualTrainingTableFactory (ui-tablefactories ; propriétaire moral_icone_seule d'Alex ; 26.14 y a sa
  colonne de sélection). Fabrique : personality et media-handling de PlayerTableFactory recopiées telles quelles
  (liaisons sans type binding.personality / binding.mediahandling, cellule StandardLabelCell de FM), ajoutées à la
  fin ; vue : ces deux colonnes avant training-rating (copies de son réglage, titre de la fabrique), et les poids de
  LARGEURS (le tableau répartit sa largeur en proportion des poids, minimum min(minimum, 44) : calcul pour 38 % et
  33 % dans RÉGLAGES). La fabrique d'abord (la vue cite ses colonnes) ; jamais la vue sans elles. Retirer : la vue
  d'abord (nos colonnes, largeurs de FM rendues d'après la sauvegarde de l'original), puis la fabrique (par id).

- TROIS TABLEAUX (v5, Kinito le 14/10 au soir : « la colonne du nom doit afficher au minimum 22 caractères ; on
  rogne sur Personnalité et Rapports médias, identiques en largeur ; la note au minimum pour la plus grande, le pouce
  au minimum pour le bouton, pas plus large ; seulement en display Large ; en Plus grand on vire la colonne Position ;
  Medium et Small tu ne changes pas ») : une vue n'a qu'une liste de colonnes pour tous les modes et toutes les tailles
  de texte, et le tableau répartit sa largeur en proportion des poids (ResizeColumnWidthsToFit). Donc, à la place du
  tableau Détails de FM dans son aiguillage (BindableSwitchElement : un texte si la liste est vide, le tableau sinon),
  une boîte à nous qui porte TROIS tableaux, un seul visible : celui de FM (vue IndividualTrainingDetailedViewTable,
  inchangée par la v5 : Medium et Small) et deux copies de lui (mêmes réglages, tri et case de sélection compris), dont
  la vue est une vue de FM citée par RIEN (guid_partout.py, code du jeu, scripts : 14/10) réécrite : Large (texte
  Petit / Normal / Grand, LARGEURS_LARGE, Position gardée) et Large Plus grand (LARGEURS_PLUS_GRAND, sans Position).
  Chaque tableau dans une boîte (le SIStyleSetter BindIntAndBoolToStyle de la v3) : hidden-item sauf si (taille du
  texte, mode Large) est le sien. Les copies des vues partent de la vue de FM telle que l'ont laissée Alex et 26.14
  (pouces, Critiq. cachée), seules les largeurs changent. Largeurs MESURÉES le 14/10 sur les captures de Kinito
  (Petit, Normal, Grand, Plus grand ; 1 u = 1,1428 px en 1920x1080) : avant le nom, 92,5 px fixes (portrait, icône,
  marges) ; après, 10 px ; police du nom 12,88 px en Petit (x taille du texte) ; un nom long « normal » de 22
  caractères (Maximilian Oberhausner) : 246 u en Grand, 261 u en Plus grand ; pastille de note 53 px en Grand, 56 en
  Plus grand (+ 6 avant, 2 après) ; bouton du pouce 39 px, collé à gauche (35 u). Tableau : 581 u à 38 %, ~497 u à
  33 %. Les vues s'écrivent AVANT l'écran (un tableau ne doit jamais citer une vue d'autres colonnes) ; l'écran se
  retire AVANT les vues (rendues d'après la sauvegarde de l'original).

- UN TABLEAU PAR TAILLE DE TEXTE (v6, Kinito le 15/10, capture en texte Petit : « la colonne du nom est beaucoup trop
  grande, elle affiche trop de caractères » ; « adapte la taille pour le même nombre de caractères en Petit, Normal
  et Grand ») : la v5 n'avait qu'un tableau pour Petit, Normal et Grand, réglé sur le Grand (246 u) : en Petit il
  montrait ~30 caractères. Mesuré sur sa capture : nom en 12,6 à 12,9 px (« Federico Chiesa » 88 px, « Jay Spearing »
  72 px : ABC Social à ~12,7 px) = le Petit (12,88 px). Même calcul que la v5 (92,5 px + 22 caractères de
  « Maximilian Oberhausner » + 10 px ; la police suit la taille du texte), qui redonne ses 246 u (Grand) et 260 u
  (Plus grand) : Petit 210,5 u, Normal 232 u. La place gagnée va à parts égales à Personnalité et Rapports médias
  (coupées : « Assez déter… », « Appréciés des… ») ; Position, note et pouce ne bougent pas. Quatre tableaux à nous
  au lieu de deux : Petit (TextScaling < 100), Normal (= 100), Grand (= 110), Plus grand (>= 120) : FM n'a que 85 /
  100 / 110 / 120. Deux vues de FM de plus, citées par RIEN (vues_libres.py et guid_partout.py, tous les bundles
  scènes comprises, code du jeu, scripts d'Alex et de Kinito : 15/10), même type que les autres
  (SetPieceTakerListCornerTakersTable, SetPieceTakerListDeepFreeKickTakersTable). 26.14 v25 les connaît aussi
  (VUES_26_15 : colonne Critiq. cachée).

Touché : TeamIndividualTrainingBlock : nos éléments (par leur nom, UIPickerKinito-largeur-liste-..., et notre variable
par sa variable), les classes du bloc de la liste (width-30-percent retirée, remise par notre boîte « fm ») et le tri
de départ du tableau Détails (SortedColumn, SortAscending ; 26.14 y règle SelectionCellID, un autre champ) ; IndividualTrainingDetailedViewTable (nos deux colonnes, poids de
portrait-name-job, portrait-name-position, position, training-rating) ; PlayerIndividualTrainingTableFactory (nos
deux colonnes, par leur id). Lus seulement : HeatMapsMatch_Block, TacticTeamInstructionMultipleChoiceOptionButton, PlayerOverviewPositionCell
(v3), PlayerTableFactory ; AdaptiveLayoutPreferences lu une fois le 14/10 (numéros des modes).

v11 (Kinito, 08/11/2026, en préparant le paquet pour la v1.67 d'Alex) : sa v10 (livrée dans sa v1.64, 06/11) et la
nôtre (vue Résumé triée, tri gardé, 04/11) portaient le même numéro. Sa v10 répare un défaut de la v6 : les vues
Petit / Normal du mode Large étaient SetPieceTakerListCornerTakersTable et SetPieceTakerListDeepFreeKickTakersTable,
que FM cite par path_id (SetPieceTakerListTableViewSettingsCollection, ui-datacollections) pour l'écran des tireurs
de coups de pied arrêtés : ses listes n'avaient plus que la colonne Position. Elles passent sur
NewsCompetitionLeagueTable et CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee, citées par RIEN (mesuré par
Alex, puis par Kinito le 08/11 : path_id et GUID dans les données décompressées de tous les bundles ui-*, témoins
retrouvés), et les anciennes sont rendues à FM (ANCIENNES_VUES). Fusion à trois (v1.61, sa v10, notre v10) : un
seul conflit, VERSION.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_largeur_liste.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_largeur_liste.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_largeur_liste.py etat
"""
import copy
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import json  # noqa: E402
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
VERSION = 11  # v11 (Kinito, 08/11/2026) : la v10 d'Alex (vues Petit / Normal hors de SetPieceTakerList*) + la v10
#               de Kinito (vue Résumé triée par la note, tri gardé), réunies : les deux étaient numérotées 10
#               v10 (Alex, 2026-11-06) : vues Petit / Normal hors de SetPieceTakerList* (voir TABLEAUX)
#               v6 (15/10) : un tableau par taille de texte en mode Large (22 caractères au nom en Petit, Normal, Grand)
#               v7 (15/10) : option medias_entrainement (colonne Rapports avec les médias enlevable)
#               v10 (Kinito, 04/11/2026) : le tableau de la vue Résumé trié par la note au départ, et son tri GARDÉ
# v10 (Kinito, 04/11/2026 : « quand j'arrive sur l'onglet [Résumé], le tri de base sur la note en décroissant, comme
# dans l'onglet Détails ; on peut changer ; et l'onglet doit garder en mémoire notre choix : si je range par note,
# j'avance d'un jour, je reviens, ce n'est plus rangé par note ») : le StreamedTable de la vue Résumé (#List, liste de
# colonnes fixe : InitialiseStreamedTableFromStaticList, sans vue) reçoit le tri de départ de la vue Détails
# (SortedColumn « training-rating », SortAscending 0) et un SharedPersistenceID. Mesuré dans le code du jeu (desasm,
# 04/11) : StreamedTable::GeneratePersistenceKeys fait les clés du tri gardé (« sorted-column-persistence-key »,
# « sort-ascending-persistence-key »…, SI.Core.Persistence) ; avec un SharedPersistenceID (champ 0x688), la clé est
# EXPLICITE (nom de la vue - SharedPersistenceID - panneau), sans lui elle dépend de l'élément. FM le pose sur les tableaux
# qui gardent leur état d'un écran à l'autre (TacticalPlannerTeamShape : « TacticalPlannerTool » ; la base de données :
# « PlayerDatabaseClubTable »…). Le tableau Détails n'est pas touché (Kinito : il garde déjà son tri)
RESUME_PARENT = "List"                     # le parent du tableau de la vue Résumé dans TeamIndividualTrainingBlock
PARTAGE_RESUME = "KinitoIndividualTrainingSummaryTable"   # notre SharedPersistenceID (unique : cherché dans le jeu)
CHAMPS_PARTAGE = ("SharedPersistenceID", "SharedPersistenceID_UxmlAttributeFlags")
LARGEUR_PLUS_GRAND = "width-33-percent"   # classe de FM : la liste à 33 % avec le texte en Plus grand (Kinito)
LARGEUR_AUTRES = "width-38-percent"       # classe de FM : 38 % en Petit, Normal et Grand (Kinito)
SEUIL_TEXTE = 120                         # settings.TextScaling : Plus grand = 120 (Petit 85, Normal 100, Grand 110)
# v3 (Kinito, 14/10 : « réserve le 38-33 au mode Large ; laisse les autres ajouts ») : en mode Medium ou Small de
# l'affichage des informations (préférences de FM), la liste garde ses 30 % de FM ; les colonnes ne changent pas
MODE = "settings.AdaptiveScalingLevelIndex"   # le réglage « Information Display » des préférences de FM
MODE_LARGE = 0                            # Large 0, Medium 1, Small 2 (variables Int du groupe #buttons de
#                                           AdaptiveLayoutPreferences, que ses trois boutons écrivent dans MODE)
# v2 (Kinito, 14/10 : « écourte la colonne du nom un peu ; j'aimerais la colonne Personnalité et Rapports médias,
# avant la note d'entraînement ; la colonne de la note réduite au maximum, que la note la plus longue s'affiche
# entièrement mais pas plus large ; réduire la colonne Position ») : colonnes recopiées de PlayerTableFactory,
# insérées avant la note
NOUVELLES = ["personality", "media-handling"]
# poids des colonnes dans la vue (le tableau les répartit en proportion : flex-basis 0, flex-grow = ce poids, minimum
# min(minimum, 44), code du jeu lu pour 26.12). Calculé pour un tableau de 581 u (38 %) et 501 u (33 %) : nom 145 /
# 121, poste 75 / 62, personnalité et rapports médias 107 / 90, note 58 / 48 (sa pastille fait 46 u à toutes les
# tailles de texte : 53 px mesurés sur les captures de Kinito en Normal et en Plus grand) ; pouces 44 (Alex)
LARGEURS = {"portrait-name-job": 155, "portrait-name-position": 145, "position": 80, "personality": 115,
            "media-handling": 115, "training-rating": 62}
MIN_COLONNE = 44                          # minimum de chaque colonne réglée (le jeu ne prend jamais plus de 44)
# v5 : en mode Large, deux tableaux à nous (copies de celui de FM), chacun sa vue (vues de FM citées par RIEN,
# réécrites) ; poids = largeurs en u (le tableau fait 581 u à 38 %, ~497 u à 33 %) ; colonnes non citées : inchangées
LARGEURS_LARGE = {"portrait-name-job": 246, "position": 81, "personality": 82.5, "media-handling": 82.5,
                  "training-rating": 54, "praise-training-development-button": 35}           # Grand (v5 : P, N, G)
# v6 : 22 caractères aussi en Petit et en Normal (même somme : 581 u), la place gagnée à Personnalité / Rapports médias
LARGEURS_PETIT = {"portrait-name-job": 210.5, "position": 81, "personality": 100.25, "media-handling": 100.25,
                  "training-rating": 54, "praise-training-development-button": 35}           # Petit
LARGEURS_NORMAL = {"portrait-name-job": 232, "position": 81, "personality": 89.5, "media-handling": 89.5,
                   "training-rating": 54, "praise-training-development-button": 35}          # Normal
LARGEURS_PLUS_GRAND = {"portrait-name-job": 261, "personality": 72.5, "media-handling": 72.5,
                       "training-rating": 56, "praise-training-development-button": 35}      # Plus grand
# v7 (le joueur, 15/10 : « une option pour enlever ou ajouter le rapport avec les médias ; rééquilibre les autres cases,
# surtout le nom ») : option medias_entrainement (options.py, app : sous Entraînement individuel) ; « sans » : la colonne
# media-handling pas mise dans les vues (la fabrique la garde), sa largeur va au nom (PART_NOM) et à Personnalité
PART_NOM = 0.6
COLONNES_NOM = ("portrait-name-job", "portrait-name-position")
# v8 (le joueur, 15/10, captures sans médias : « mets le poste un peu à gauche pour montrer plus les postes ; la
# personnalité un peu plus à droite ») : en Petit / Normal / Grand, du nom (toujours >= ses 22 caractères) et de
# Personnalité (« Assez professionnel » tient encore) vers Position ; même somme (581 u). Plus grand (sans Position) et
# Medium / Small : PART_NOM
# v9 (le joueur, 2026-11-12, capture : postes encore coupés « MO (C), B… ») : encore -25 au nom et -15 / -15 / -5 à
# Personnalité, donnés à Position (même somme)
SANS_MEDIAS = {
    "petit": {"portrait-name-job": 215.5, "position": 171, "personality": 105.5,
              "training-rating": 54, "praise-training-development-button": 35},
    "normal": {"portrait-name-job": 230.5, "position": 166, "personality": 95.5,
               "training-rating": 54, "praise-training-development-button": 35},
    "grand": {"portrait-name-job": 240.5, "position": 151, "personality": 100.5,
              "training-rating": 54, "praise-training-development-button": 35}}
# =====================================================================================================

ECRAN = "TeamIndividualTrainingBlock"
RANGEE = "frame"                          # la rangée de la vue Détails (liste, séparateur, bloc du joueur)
CLASSE_FM = "width-30-percent"            # la largeur de FM du bloc de la liste
TAILLE_TEXTE = "settings.TextScaling"     # racine commune à tous les écrans (RECETTES 18)
# v3 : trois morceaux de FM recopiés (modèles d'origine, lus seulement)
SOURCE_VARIABLES = "HeatMapsMatch_Block"  # son BindingVariablesComponent (possessionmode) : le même que 26.13
SOURCE_ECRIVAIN = ("TacticTeamInstructionMultipleChoiceOptionButton", "data-to-send-setter")   # le même que 26.13
SOURCE_STYLE = "PlayerOverviewPositionCell"   # son SIStyleSetter à BindIntAndBoolToStyle
FONCTION_ECRIRE = "ffe24c8d915bd7449b8ba72442257e41"   # BindAndSetToDestinationResultOfIntComparison
FONCTION_STYLE = "e86de17243ad6094f88f99c74185a1e5"    # BindIntAndBoolToStyle
ARGS_ECRIRE = (b"BindingPath]", b"BooleanVisualArg", b"ComparisonOperator]", b"BindingPath]", b"Int32VisualArg")
#               destination, forcer, opérateur, chemin de l'entier, entier (entrées lues dans le graphe de la fonction)
ARGS_STYLE = (b"BindingPath]", b"ComparisonOperator]", b"Int32VisualArg", b"BindingPath]", b"BooleanVisualArg",
              b"StringVisualArg", b"StringVisualArg", b"BooleanVisualArg", b"BooleanVisualArg")
#               chemin de l'entier, opérateur, entier, chemin du booléen, inverser, classe si vrai, classe sinon,
#               sur le parent, sur l'enfant (classe = (entier OP valeur) ET (booléen OU-EXCLUSIF inverser))
OP_INF, OP_EGAL, OP_SUP_EGAL = 0, 2, 3    # ComparisonOperator : < 0, <= 1, = 2, >= 3, > 4, != 5
# v5 : les tableaux de la vue Détails : clé : (vue de FM réécrite, son GUID, largeurs, colonnes retirées, opérateur et
# valeur sur la taille du texte, booléen « mode Large » inversé) ; la boîte d'un tableau est visible si (taille du
# texte OP valeur) ET (mode Large OU-EXCLUSIF inversé), hidden-item sinon : un seul visible à la fois
TABLEAUX = {   # v6 : petit / normal / grand (v5 : « large » pour les trois) ; un seul visible : FM n'a que 85 / 100 /
    # 110 / 120 pour la taille du texte
    # v10 (Alex, 2026-11-06, le joueur : écran des tireurs de corners de FM27 avec la seule colonne Position) : les
    # vues SetPieceTakerList* sont citées dans FM27 par SetPieceTakerListTableViewSettingsCollection (ui-datacollections,
    # par path_id : le contrôle du 15/10 ne cherchait que les GUID). Petit / Normal -> deux vues citées par RIEN dans
    # FM27 (GUID, path_id dans tous les bundles ui-* et dans le bundle des vues, nom dans le code : 2026-11-06) ;
    # les anciennes rendues d'origine (ANCIENNES_VUES)
    "petit": ("NewsCompetitionLeagueTable", "7a9ef4835c688d3438fba83446b02a87", LARGEURS_PETIT, [],
              OP_INF, 100, False),
    "normal": ("CompetitionSiteInsAndOutsTransfersTableViewSettingsNoFee", "dcd2db77eef4a0647b83061c2d211880",
               LARGEURS_NORMAL, [], OP_EGAL, 100, False),
    "grand": ("TeamPlayerSocialGroupsTable", "0566ea3cbec27f9408499acf47270a6e", LARGEURS_LARGE, [],
              OP_EGAL, 110, False),
    "plus-grand": ("TeamPlayerSocialGroupsCompactTable", "395d965670dc29f4caf592dfcce98073", LARGEURS_PLUS_GRAND,
                   ["position"], OP_SUP_EGAL, SEUIL_TEXTE, False)}
ANCIENNES_VUES = ("SetPieceTakerListCornerTakersTable", "SetPieceTakerListDeepFreeKickTakersTable")   # v10 : à FM
BOITE_FM = (OP_SUP_EGAL, 0, True)   # le tableau de FM : visible si PAS le mode Large (toute taille de texte)
CLASSE_CACHE = "hidden-item"        # classe de FM : display: none
CLASSES_BOITE_TABLEAUX = ["row-direction-normal", "align-items-stretch", "flex-grow-class", "height-100-percent"]
CLASSES_BOITE_TABLEAU = ["flex-grow-class", "height-100-percent"]
GUID_VUE_FM = "d1f0cea78666ccf4f8b97f070d513924"   # IndividualTrainingDetailedViewTable (InitFunction du tableau)
VARIABLE = "kinito-liste-mode-large"      # vraie si le mode Large est choisi (écrite par notre écrivain)
# les trois boîtes : (nom, opérateur, valeur sur la taille du texte, booléen inversé, classe) ; une seule classe de
# largeur à la fois sur le bloc (aucune règle de priorité en jeu). Si la variable ne s'écrivait pas, elle resterait
# fausse : 30 % partout, l'écran de FM, jamais un bloc sans largeur
BOITES = (("plus-grand", OP_SUP_EGAL, SEUIL_TEXTE, False, LARGEUR_PLUS_GRAND),
          ("autres", OP_INF, SEUIL_TEXTE, False, LARGEUR_AUTRES),
          ("fm", OP_SUP_EGAL, 0, True, CLASSE_FM))
INVISIBLE = {"position": "absolute", "width": 0, "height": 0}
# v4 (Kinito, 14/10 : « que le tableau soit toujours trié par note décroissante, en haut la meilleure ; on peut changer
# si on veut, mais quand on entre dans ce tableau c'est trié par note ») : le tri de départ du tableau Détails (FM :
# « position »). Champs du StreamedTable de FM : SortedColumn (la colonne), SortAscending (0 = l'ordre du premier clic
# sur l'en-tête : la plus forte en haut ; FM : "date" à 0 = la plus récente en haut), chacun avec son drapeau
TRI_COLONNE = "training-rating"
TRI_CROISSANT = 0
CHAMPS_TRI = ("SortedColumn", "SortedColumn_UxmlAttributeFlags", "SortAscending", "SortAscending_UxmlAttributeFlags")
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")             # (nom lu par essai_copies : copies)
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")   # (idem)
VUE = "IndividualTrainingDetailedViewTable"     # la vue du tableau Détails (citée par ce seul écran)
FABRIQUE = "PlayerIndividualTrainingTableFactory"   # sa fabrique (propriétaire : moral_icone_seule d'Alex)
SOURCE_COLONNES = "PlayerTableFactory"          # la fabrique de FM qui a personality et media-handling
AVANT = "training-rating"                       # nos colonnes juste avant la note à l'entraînement
PREFIXE = "UIPickerKinito-largeur-liste"
NOM_ECRIVAIN = f"{PREFIXE}-v{VERSION}-mode"
NOM_TABLEAUX = f"{PREFIXE}-v{VERSION}-tableaux"   # v5 : la boîte des trois tableaux (à la place du tableau de FM)


def nom_tableau(cle, copie=False):
    """v5 : la boîte d'un tableau (« fm », « large », « plus-grand »), ou la copie du tableau qu'elle porte"""
    return f"{PREFIXE}-v{VERSION}-tableau-{cle}" + ("-copie" if copie else "")
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_largeur_liste.actif")

for _k, _v in {"position": (131102, 7), "width": (131105, 3), "height": (131087, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


# ---------- outils ----------
def avec_medias():
    """v7 : option medias_entrainement (« avec » = choix de base)"""
    import options
    return options.get("medias_entrainement") == "avec"


def colonnes_vue():
    """v7 : nos colonnes mises dans les vues (la fabrique a toujours les deux)"""
    return NOUVELLES if avec_medias() else [c for c in NOUVELLES if c != "media-handling"]


def poids(largeurs, cle=None):
    """v7 : les largeurs voulues ; sans les médias, leur largeur va au nom (PART_NOM) et à Personnalité (v8 : tableau
    « cle » dans SANS_MEDIAS : ses largeurs)"""
    if avec_medias() or "media-handling" not in largeurs:
        return largeurs
    if cle in SANS_MEDIAS:
        return SANS_MEDIAS[cle]
    d = dict(largeurs)
    m = d.pop("media-handling")
    # au demi près : le bundle garde des float32 (270,65 n'y tombe pas juste : vue jamais « à jour »)
    gain = round(m * PART_NOM * 2) / 2   # ce que gagne le nom ; le reste (même somme) à Personnalité
    for n in COLONNES_NOM:
        if n in d:
            d[n] += gain
    d["personality"] += m - gain
    return d


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def ancetres(t, r):
    p = t.parent.get(r)
    while p is not None:
        yield p
        p = t.parent.get(p)


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def texte_arg(s):
    b = s.encode("utf-8")
    if len(b) > 127:
        raise ValueError(f"texte trop long : {s}")
    return bytes([1, len(b)]) + b


def guid_fonction(sd, cle):
    b = sd.get(cle)
    if isinstance(b, dict):
        return (b.get("m_visualFunction") or b).get("m_target", {}).get("m_guid")
    return None


def bloc_liste(t):
    """le bloc de la liste : le seul ComponentElement enfant de la rangée #frame (vue Détails) ; None sinon"""
    f = first(t, lambda r: t.name(r) == RANGEE)
    blocs = [k for k in t.children(f) if typ(t, k) == "ComponentElement"] if f is not None else []
    return blocs[0] if len(blocs) == 1 else None


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def retirer_racines(t):
    """retire NOS racines (éléments nommés PREFIXE...), les règles de style qu'elles étaient seules à utiliser et les
    valeurs que ces règles avaient ajoutées en fin de table (recopié de 26.14) ; rend True si quelque chose était là"""
    racines = [r for r in marques(t) if not any(t.name(p).startswith(PREFIXE) for p in ancetres(t, r))]
    nos_regles = {t.elem(r).get("m_RuleIndex", -1) for x in racines for r in t.walk(x)} - {-1}
    for r in racines:
        t.remove(r)
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = nos_regles - utilisees
    if enlever:
        regles = t.styles.sh["m_Rules"]
        garder = [i for i in range(len(regles)) if i not in enlever]
        nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
        t.styles.sh["m_Rules"] = [regles[i] for i in garder]
        for r in t.tt["references"]["RefIds"]:
            d = (r or {}).get("data") or {}
            if d.get("m_RuleIndex", -1) >= 0:
                d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
        tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
        servies = {}
        for regle in t.styles.sh["m_Rules"]:
            for p in regle["m_Properties"]:
                for v in p["m_Values"]:
                    if v["m_ValueType"] in tables:
                        servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
        for nom in set(tables.values()):
            valeurs = t.styles.sh.get(nom) or []
            while valeurs and len(valeurs) - 1 not in servies.get(nom, set()):
                valeurs.pop()
        t.styles.changed = True
    return bool(racines)


# ---------- poser / retirer ----------
def nom_boite(cle):
    return f"{PREFIXE}-v{VERSION}-{cle}"


def noms_bloc():
    """nos éléments posés directement dans le bloc de la liste (v3) : l'écrivain et les trois boîtes de largeur"""
    return {NOM_ECRIVAIN} | {nom_boite(b[0]) for b in BOITES}


def noms_tableaux():
    """v5 : la boîte des tableaux, les trois boîtes de tableau et les deux copies"""
    return ({NOM_TABLEAUX} | {nom_tableau(c) for c in ("fm", *TABLEAUX)} | {nom_tableau(c, True) for c in TABLEAUX})


def noms_voulus():
    return noms_bloc() | noms_tableaux()


def nos_variables(t):
    """nos BindingVariablesComponent (sans nom possible : reconnus à leur déclaration, comme 26.13)"""
    return [r for r in t.walk() if typ(t, r) == "BindingVariablesComponent"
            and any(f"{{{VARIABLE}}}" in (p.get("value") or "") for p in t.elem(r).get("m_Properties") or [])]


def donnees_composant(t, r):
    """les données d'un composant (rid), rangées dans la liste m_components de son parent (pas dans l'élément)"""
    ident = t.elem(r)["m_Id"]
    return [c["rid"] for c in t.sd(t.parent[r]).get("m_components") or []
            if ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == ident]


def sources():
    """v3 : les trois morceaux de FM recopiés, {clé: (arbre d'origine, élément)} ; élément None s'il est introuvable"""
    out = {}
    o = ouvrir(SOURCE_VARIABLES, depart_original=True)
    tv = o and o[3]
    var = tv and first(tv, lambda r: typ(tv, r) == "BindingVariablesComponent")
    donnees = donnees_composant(tv, var) if var is not None else []
    out["variables"] = (tv, (var, donnees[0]) if len(donnees) == 1 else None)
    o = ouvrir(SOURCE_ECRIVAIN[0], depart_original=True)
    te = o and o[3]
    out["ecrivain"] = (te, te and first(te, lambda r: te.name(r) == SOURCE_ECRIVAIN[1]
                                        and typ(te, r) == "BindingSetter"))
    o = ouvrir(SOURCE_STYLE, depart_original=True)
    ts = o and o[3]
    out["style"] = (ts, ts and first(ts, lambda r: typ(ts, r) == "SIStyleSetter"
                                      and guid_fonction(ts.sd(r), "BindFunction") == FONCTION_STYLE))
    return out


def recopier(t, s, rid, parent, nom=None):
    """un élément de FM recopié seul (sans enfants, classes, ni règle de style : la règle est ôtée AVANT tout style,
    sinon elle resterait orpheline au retrait, 26.14 v20)"""
    r = t.clone(rid, parent, src=s)
    recaler_parent(t, r)
    for k in list(t.children(r)):
        t.remove(k)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    if nom:
        nommer(t, r, nom)
    return r


def args_conformes(f, guid, attendus):
    """les arguments décodés d'une fonction de FM s'ils ont la forme attendue ; None sinon"""
    if not isinstance(f, dict) or (f.get("m_target") or {}).get("m_guid") != guid:
        return None
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != len(attendus) or any(not bytes(a[0]).endswith(fin) for a, fin in zip(args, attendus)):
        return None
    return args


def poser(t, src):
    """v3 : la classe de FM du bloc retirée ; dans le bloc (derniers enfants, sans place) : une variable « mode Large »
    (BindingVariablesComponent, comme le groupe #buttons des préférences de FM), son écrivain (BindingSetter de FM :
    variable = (MODE == MODE_LARGE)), et trois boîtes (SIStyleSetter de FM, BindIntAndBoolToStyle) qui posent CHACUNE
    sa classe de largeur sur le bloc (leur parent) : 33 % si Large et Plus grand, 38 % si Large et texte plus petit,
    30 % (celle de FM) si pas Large ; toujours une seule à la fois"""
    b = bloc_liste(t)
    if b is None:
        return [f"#{RANGEE} : bloc de la liste (ComponentElement unique) introuvable"]
    if CLASSE_FM not in (t.elem(b).get("m_Classes") or []):
        return [f"bloc de la liste sans la classe {CLASSE_FM} de FM : inattendu (introuvable)"]
    manque = [k for k, (_, r) in src.items() if r is None]
    if manque:
        return [f"morceaux de FM introuvables : {', '.join(manque)} (introuvable)"]
    # la variable : un composant du bloc de la liste (un ComponentElement ; comme 26.13 bascule, vu en jeu) :
    # l'élément, rangé après les autres composants du bloc, déclare « value-vars » ; ses données (ValueVariables,
    # uxmlAssetId = l'identifiant de l'élément) vont dans la liste m_components du bloc
    tv, (rv, dv) = src["variables"]
    rang = sum(1 for k in t.children(b) if (t.elem(k).get("m_FullTypeName") or "").endswith("Component"))
    v = t.clone(rv, b, rang, src=tv)
    recaler_parent(t, v)
    if "m_RuleIndex" in t.elem(v):
        t.elem(v)["m_RuleIndex"] = -1
    props = [x for x in t.elem(v).get("m_Properties") or [] if x.get("name") == "value-vars"]
    d = copy.deepcopy(tv.refs[dv])
    d["rid"] = t.new_rid()
    dd = d["data"]
    if len(props) != 1 or not dd.get("ValueVariables"):
        return [f"variable de FM ({SOURCE_VARIABLES}) : forme inattendue (introuvable)"]
    props[0]["value"] = f"{{{VARIABLE}}}{{Bool|0|}}"
    dd["uxmlAssetId"] = t.elem(v)["m_Id"]
    var = dd["ValueVariables"][0]
    var["m_name"], var["m_scopeValue"]["m_serializedData"] = VARIABLE, "Bool|0|"
    dd["ValueVariables"] = [var]
    t.refs[d["rid"]] = d
    t.tt["references"]["RefIds"].append(d)
    sb = t.sd(b)
    sb.setdefault("m_components", []).append({"rid": d["rid"]})
    sb["m_components_UxmlAttributeFlags"] = 1
    # l'écrivain : VARIABLE = (MODE == MODE_LARGE) ; il écrit dans la variable du bloc, comme OptionalsDefaulter de FM
    # (PlayerInstructionsCard) écrit inpossession, déclarée plus haut que lui
    te, re_ = src["ecrivain"]
    w = recopier(t, te, re_, b, NOM_ECRIVAIN)
    sd = t.sd(w)
    fs = [f for f in (sd.get("BindFunction") or []) if isinstance(f, dict)
          and (f.get("m_target") or {}).get("m_guid") == FONCTION_ECRIRE]
    f = copy.deepcopy(fs[0]) if len(fs) == 1 else None
    args = args_conformes(f, FONCTION_ECRIRE, ARGS_ECRIRE)
    if args is None or len(args[2][1]) != 4 or len(args[4][1]) != 4:
        return [f"écrivain de FM ({SOURCE_ECRIVAIN[0]}) : forme inattendue (introuvable)"]
    args[0][1] = texte_arg(VARIABLE)
    args[2][1] = struct.pack("<i", OP_EGAL)
    args[3][1] = texte_arg(MODE)
    args[4][1] = struct.pack("<i", MODE_LARGE)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["BindFunction"], sd["ValueVariables"] = [f], []
    t.styles.style(t, w, INVISIBLE)
    # les trois boîtes
    ts, rs = src["style"]
    for cle, op, valeur, inverse, classe in BOITES:
        s = recopier(t, ts, rs, b, nom_boite(cle))
        f = t.sd(s).get("BindFunction")
        args = args_conformes(f, FONCTION_STYLE, ARGS_STYLE)
        if args is None or len(args[1][1]) != 4 or len(args[2][1]) != 4:
            return [f"boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)"]
        args[0][1] = texte_arg(TAILLE_TEXTE)
        args[1][1] = struct.pack("<i", op)
        args[2][1] = struct.pack("<i", valeur)
        args[3][1] = texte_arg(VARIABLE)
        args[4][1] = bytes([1 if inverse else 0])
        args[5][1], args[6][1] = texte_arg(classe), texte_arg("")   # sinon : aucune classe (FM écrit "" lui aussi)
        args[7][1] = bytes([1])   # sur le PARENT : le bloc de la liste
        args[8][1] = bytes([0])   # pas sur un enfant
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.styles.style(t, s, INVISIBLE)
    t.elem(b)["m_Classes"] = [c for c in t.elem(b)["m_Classes"] if c != CLASSE_FM]
    # v4 : le tri de départ du tableau Détails (avant la v5 : ses copies le gardent)
    tab = tableau_details(t)
    if tab is None:
        return ["tableau de la vue Détails (StreamedTable du bloc de la liste) introuvable"]
    sd = t.sd(tab)
    sd["SortedColumn"], sd["SortedColumn_UxmlAttributeFlags"] = TRI_COLONNE, 1
    sd["SortAscending"], sd["SortAscending_UxmlAttributeFlags"] = TRI_CROISSANT, 1
    # v10 : la vue Résumé, même tri de départ, et son tri gardé (SharedPersistenceID)
    res = tableau_resume(t)
    if res is None:
        return [f"tableau de la vue Résumé (StreamedTable de #{RESUME_PARENT}) introuvable"]
    sr = t.sd(res)
    if CHAMPS_PARTAGE[1] not in sr:
        return [f"tableau de la vue Résumé sans le champ {CHAMPS_PARTAGE[1]} : le jeu a changé (introuvable)"]
    sr["SortedColumn"], sr["SortedColumn_UxmlAttributeFlags"] = TRI_COLONNE, 1
    sr["SortAscending"], sr["SortAscending_UxmlAttributeFlags"] = TRI_CROISSANT, 1
    sr["SharedPersistenceID"], sr["SharedPersistenceID_UxmlAttributeFlags"] = PARTAGE_RESUME, 1
    return [f"tableau Détails trié au départ par la note à l'entraînement, la meilleure en haut (FM : par poste)",
            f"tableau Résumé trié au départ par la note, la meilleure en haut, et son tri gardé "
            f"(SharedPersistenceID {PARTAGE_RESUME})",
            f"liste de gauche (vue Détails), en mode Large : {LARGEUR_AUTRES.split('-')[1]} % de l'écran (texte "
            f"Petit, Normal, Grand), {LARGEUR_PLUS_GRAND.split('-')[1]} % (texte Plus grand) ; en Medium et Small : "
            f"30 % de FM"] + poser_tableaux(t, src)


def tableau_details(t):
    """le tableau de FM de la vue Détails : le StreamedTable du bloc de la liste qui n'est pas une de nos copies (v5) ;
    None sinon"""
    b = bloc_liste(t)
    tabs = [r for r in t.walk(b) if typ(t, r) == "StreamedTable" and not t.name(r).startswith(PREFIXE)] \
        if b is not None else []
    return tabs[0] if len(tabs) == 1 else None


def tableaux(t):
    """v5 : tous les tableaux de la vue Détails (celui de FM et nos copies)"""
    b = bloc_liste(t)
    return [r for r in t.walk(b) if typ(t, r) == "StreamedTable"] if b is not None else []


def premier_nomme(t, r):
    """v10 : le nom du plus proche ancêtre nommé de r ("" s'il n'y en a pas)"""
    p = t.parent.get(r)
    while p is not None:
        if t.name(p):
            return t.name(p)
        p = t.parent.get(p)
    return ""


def tableau_resume(t):
    """v10 : le StreamedTable de la vue Résumé : le seul dont le plus proche ancêtre nommé est #List (entre les deux, un
    élément sans nom : lu le 04/11) ; None sinon"""
    tabs = [r for r in t.walk() if typ(t, r) == "StreamedTable" and premier_nomme(t, r) == RESUME_PARENT]
    return tabs[0] if len(tabs) == 1 else None


def resume_a_jour(t):
    """v10 : tri de départ et SharedPersistenceID posés sur le tableau Résumé"""
    res = tableau_resume(t)
    if res is None:
        return False
    sd = t.sd(res)
    return (sd.get("SortedColumn") == TRI_COLONNE and sd.get("SortAscending") == TRI_CROISSANT
            and sd.get("SharedPersistenceID") == PARTAGE_RESUME
            and sd.get("SortedColumn_UxmlAttributeFlags") == 1 and sd.get("SortAscending_UxmlAttributeFlags") == 1
            and sd.get("SharedPersistenceID_UxmlAttributeFlags") == 1)


def tri_a_jour(t):
    tabs = tableaux(t)
    return tableau_details(t) is not None and all(
        t.sd(x).get("SortedColumn") == TRI_COLONNE and t.sd(x).get("SortAscending") == TRI_CROISSANT for x in tabs) \
        and resume_a_jour(t)


def rendre_resume(t):
    """v10 : les champs de tri et de partage du tableau Résumé rendus d'après l'original (FM : sans tri de départ, sans
    SharedPersistenceID) ; True si quelque chose a changé"""
    res = tableau_resume(t)
    if res is None:
        return False
    sd = t.sd(res)
    if sd.get("SharedPersistenceID") != PARTAGE_RESUME and sd.get("SortedColumn") != TRI_COLONNE:
        return False
    o = ouvrir(ECRAN, depart_original=True)
    ro = o and tableau_resume(o[3])
    champs = CHAMPS_TRI + CHAMPS_PARTAGE
    origine = {k: o[3].sd(ro).get(k) for k in champs} if ro is not None else None
    if origine is None or origine.get("SharedPersistenceID") == PARTAGE_RESUME:   # (lu le 04/11 : FM n'a rien)
        origine = {"SortedColumn": "", "SortedColumn_UxmlAttributeFlags": 0, "SortAscending": 0,
                   "SortAscending_UxmlAttributeFlags": 0, "SharedPersistenceID": "",
                   "SharedPersistenceID_UxmlAttributeFlags": 0}
    for k, v in origine.items():
        if v is None:
            sd.pop(k, None)
        else:
            sd[k] = v
    return True


# ---------- v5 : les trois tableaux de la vue Détails ----------
def deplacer(t, r, parent, index):
    """déplace r (avec ses enfants, ses données et son nom) sous parent, à la place index (recopié de 26.14)"""
    ancien = t.parent[r]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != r]
    t.elem(parent)["m_Children"].insert(index, {"rid": r})
    t.elem(r)["m_Parent"] = {"rid": parent}
    t.parent[r] = parent
    recaler_parent(t, r)


def changer_vue(t, tab, guid):
    """la vue citée par l'InitFunction d'un tableau (AssetReferenceVisualArg : GUID de la vue de FM) ; False si la
    fonction n'a pas la forme attendue"""
    fs = t.sd(tab).get("InitFunction")
    fs = fs if isinstance(fs, list) else [fs]
    vieux = (b" " + GUID_VUE_FM.encode())
    for f in fs:
        if not isinstance(f, dict):
            continue
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if bytes(a[0]).endswith(b"AssetReferenceVisualArg") and bytes(a[1]).startswith(vieux):
                a[1] = b" " + guid.encode() + bytes(a[1])[len(vieux):]
                f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
                return True
    return False


def vue_citee(t, tab):
    """le GUID de la vue citée par l'InitFunction d'un tableau, ou None"""
    fs = t.sd(tab).get("InitFunction")
    for f in (fs if isinstance(fs, list) else [fs]):
        if isinstance(f, dict):
            for a in decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"]):
                if bytes(a[0]).endswith(b"AssetReferenceVisualArg") and len(bytes(a[1])) >= 33:
                    return bytes(a[1])[1:33].decode(errors="replace")
    return None


def poser_tableaux(t, src):
    """à la place du tableau de FM dans son aiguillage (BindableSwitchElement), notre boîte des tableaux : trois boîtes
    (le SIStyleSetter BindIntAndBoolToStyle de la v3, classe sur elle-même) : le tableau de FM (déplacé, visible hors
    du mode Large), et deux copies de lui, chacune citant sa vue (TABLEAUX), visibles en mode Large selon la taille du
    texte. Un tableau caché : hidden-item (display: none)"""
    tab = tableau_details(t)
    aig = t.parent.get(tab) if tab is not None else None
    if aig is None or typ(t, aig) != "BindableSwitchElement":
        return ["v5 : aiguillage du tableau Détails (BindableSwitchElement) introuvable"]
    if vue_citee(t, tab) != GUID_VUE_FM:
        return [f"v5 : le tableau Détails ne cite pas la vue {VUE} (introuvable)"]
    modele = first(t, lambda r: t.name(r) == "Table" and typ(t, r) == "VisualElement")   # la rangée « Table » de FM
    if modele is None:
        return ["v5 : élément « Table » de FM (modèle de notre boîte) introuvable"]
    rang = [k["rid"] for k in t.elem(aig)["m_Children"]].index(tab)
    boite = t.clone(modele, aig, rang)
    recaler_parent(t, boite)
    for k in list(t.children(boite)):
        t.remove(k)
    t.elem(boite)["m_Classes"], t.elem(boite)["m_RuleIndex"] = list(CLASSES_BOITE_TABLEAUX), -1
    nommer(t, boite, NOM_TABLEAUX)
    ts, rs = src["style"]
    for cle in ("fm", *TABLEAUX):
        op, valeur, inverse = BOITE_FM if cle == "fm" else TABLEAUX[cle][4:7]
        s = recopier(t, ts, rs, boite, nom_tableau(cle))
        f = t.sd(s).get("BindFunction")
        args = args_conformes(f, FONCTION_STYLE, ARGS_STYLE)
        if args is None or len(args[1][1]) != 4 or len(args[2][1]) != 4:
            return [f"boîte de style de FM ({SOURCE_STYLE}) : forme inattendue (introuvable)"]
        args[0][1] = texte_arg(TAILLE_TEXTE)
        args[1][1] = struct.pack("<i", op)
        args[2][1] = struct.pack("<i", valeur)
        args[3][1] = texte_arg(VARIABLE)
        args[4][1] = bytes([1 if inverse else 0])
        args[5][1], args[6][1] = texte_arg(""), texte_arg(CLASSE_CACHE)   # visible si vrai, cachée sinon
        args[7][1] = args[8][1] = bytes([0])   # sur elle-même
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.elem(s)["m_Classes"] = list(CLASSES_BOITE_TABLEAU)
        if cle == "fm":
            deplacer(t, tab, s, 0)
        else:
            c = t.clone(tab, s)
            recaler_parent(t, c)
            nommer(t, c, nom_tableau(cle, True))
            if not changer_vue(t, c, TABLEAUX[cle][1]):
                return [f"v5 : vue de la copie « {cle} » pas changée (introuvable)"]
    return [f"vue Détails : {1 + len(TABLEAUX)} tableaux, un seul visible : mode Large texte Petit (vue "
            f"{TABLEAUX['petit'][0]}), Normal (vue {TABLEAUX['normal'][0]}), Grand (vue {TABLEAUX['grand'][0]}), "
            f"Position gardée ; Plus grand (vue {TABLEAUX['plus-grand'][0]}, sans Position) ; Medium et Small (celui "
            f"de FM, inchangé)"]


def tableaux_a_jour(t):
    boite = first(t, lambda r: t.name(r) == NOM_TABLEAUX)
    tab = tableau_details(t)
    if boite is None or tab is None or typ(t, t.parent.get(boite)) != "BindableSwitchElement":
        return False
    boites = [t.name(k) for k in t.children(boite)]
    if boites != [nom_tableau(c) for c in ("fm", *TABLEAUX)]:
        return False
    if t.parent.get(tab) != first(t, lambda r: t.name(r) == nom_tableau("fm")):
        return False
    for cle, (_, guid, *_r) in TABLEAUX.items():
        c = first(t, lambda r: t.name(r) == nom_tableau(cle, True))
        if c is None or typ(t, c) != "StreamedTable" or t.name(t.parent[c]) != nom_tableau(cle) \
                or vue_citee(t, c) != guid:
            return False
    return True


def rendre_tableau(t):
    """v5 : le tableau de FM rendu à sa place dans l'aiguillage (celle de notre boîte), AVANT que notre boîte parte ;
    True si déplacé"""
    tab = tableau_details(t)
    if tab is None or not t.name(t.parent[tab]).startswith(PREFIXE):
        return False
    boite = t.parent.get(t.parent[tab])   # notre boîte des tableaux (parent de la boîte « fm »)
    aig = t.parent.get(boite) if boite is not None else None
    if aig is None or t.name(boite) != NOM_TABLEAUX and not t.name(boite).startswith(PREFIXE):
        return False
    rang = [k["rid"] for k in t.elem(aig)["m_Children"]].index(boite)
    deplacer(t, tab, aig, rang)
    return True


def retirer(t):
    """nos éléments retirés (par nom ; notre variable, par sa variable) ; les classes du bloc de la liste rendues
    d'après l'original ; True si quelque chose a changé"""
    fait = rendre_tableau(t)   # v5 : le tableau de FM rendu à sa place AVANT que notre boîte parte (avec nos copies)
    fait = retirer_racines(t) or fait
    for r in nos_variables(t):   # la donnée du composant (liste m_components du parent), puis l'élément
        partis = set(donnees_composant(t, r))
        ps = t.sd(t.parent[r])
        ps["m_components"] = [c for c in ps.get("m_components") or [] if c["rid"] not in partis]
        t.tt["references"]["RefIds"] = [x for x in t.tt["references"]["RefIds"] if x["rid"] not in partis]
        for x in partis:
            t.refs.pop(x, None)
        t.remove(r)
        fait = True
    b = bloc_liste(t)
    if b is not None and CLASSE_FM not in (t.elem(b).get("m_Classes") or []):
        o = ouvrir(ECRAN, depart_original=True)
        bo = o and bloc_liste(o[3])
        classes = list(o[3].elem(bo).get("m_Classes") or []) if bo is not None else None
        if classes is None or CLASSE_FM not in classes:   # (classes de FM lues le 14/10)
            classes = [CLASSE_FM]
        t.elem(b)["m_Classes"] = classes
        fait = True
    # v10 : la vue Résumé rendue d'après l'original
    fait = rendre_resume(t) or fait
    # v4 : le tri de départ de FM rendu d'après l'original (FM : « position », lu le 14/10) ; v10 : tri_a_jour regarde
    # aussi le Résumé, d'où le test de la seule vue Détails ici
    tab = tableau_details(t)
    details_tries = tab is not None and all(
        t.sd(x).get("SortedColumn") == TRI_COLONNE and t.sd(x).get("SortAscending") == TRI_CROISSANT
        for x in tableaux(t))
    if details_tries:
        o = ouvrir(ECRAN, depart_original=True)
        to = o and tableau_details(o[3])
        origine = {k: o[3].sd(to).get(k) for k in CHAMPS_TRI} if to is not None else None
        if origine is None or origine["SortedColumn"] == TRI_COLONNE:
            origine = {"SortedColumn": "position", "SortedColumn_UxmlAttributeFlags": 1, "SortAscending": 0,
                       "SortAscending_UxmlAttributeFlags": 1}
        for k, v in origine.items():
            if v is None:
                t.sd(tab).pop(k, None)
            else:
                t.sd(tab)[k] = v
        fait = True
    return fait


def a_jour(t):
    b = bloc_liste(t)
    if b is None:
        return False
    return ({t.name(r) for r in marques(t)} == noms_voulus()
            and all(t.parent.get(r) == b for r in marques(t) if t.name(r) in noms_bloc())
            and [t.parent.get(r) for r in nos_variables(t)] == [b]
            and all(len(donnees_composant(t, r)) == 1 for r in nos_variables(t))
            and CLASSE_FM not in (t.elem(b).get("m_Classes") or []) and tri_a_jour(t) and tableaux_a_jour(t))


# ---------- v2 : les colonnes (fabrique ui-tablefactories, vue ui-tableviews) ----------
def monos(env, noms):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in noms:
            yield o, o.read_typetree()


def ecrire_bundle(env, chemin):
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(chemin)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(chemin, data)


def colonnes_voulues(env):
    """les colonnes personality / media-handling de PlayerTableFactory, recopiées telles quelles (liaisons sans
    type : binding.personality, binding.mediahandling ; cellule StandardLabelCell de FM) ; None si absentes"""
    src = {r["m_id"]: r for _, tt in monos(env, {SOURCE_COLONNES}) for r in tt["m_rowData"] if r["m_id"] in NOUVELLES}
    return [copy.deepcopy(src[c]) for c in NOUVELLES] if set(src) == set(NOUVELLES) else None


def fabrique_a_jour(env):
    voulues = colonnes_voulues(env)
    rows = [r for _, tt in monos(env, {FABRIQUE}) for r in tt["m_rowData"]]
    return voulues is not None and all(any(r == v for r in rows) for v in voulues)


def fabrique_poser(env):
    """nos colonnes ajoutées à la fin de la fabrique (ou rendues conformes) ; True si changé ; None si impossible"""
    voulues = colonnes_voulues(env)
    if voulues is None:
        return None
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        rows = tt["m_rowData"]
        for v in voulues:
            if any(r == v for r in rows):
                continue
            rows[:] = [r for r in rows if r["m_id"] != v["m_id"]]
            rows.append(v)
            change = True
        if change:
            o.save_typetree(tt)
    return change


def fabrique_retirer(env):
    change = False
    for o, tt in monos(env, {FABRIQUE}):
        avant = len(tt["m_rowData"])
        tt["m_rowData"] = [r for r in tt["m_rowData"] if r["m_id"] not in NOUVELLES]
        if len(tt["m_rowData"]) != avant:
            o.save_typetree(tt)
            change = True
    return change


def config_origine():
    """la liste de colonnes de FM de la vue, dans la sauvegarde de l'original (backups\\) ; None si pas de sauvegarde"""
    orig = backup.backup_path(VUES)
    if not os.path.exists(orig):
        return None
    for _, tt in monos(UnityPy.load(orig), {VUE}):
        return tt["m_tableView"]["m_tableConfig"]
    return None


def vue_voulue(cfg):
    """la liste de colonnes actuelle (avec les pouces d'Alex s'ils y sont), nos colonnes posées avant la note (copies
    de la colonne de la note : paliers 7, tri permis), les poids de LARGEURS ; None si la note est absente"""
    cfg = [copy.deepcopy(c) for c in cfg if c["m_columnID"] not in NOUVELLES]
    ids = [c["m_columnID"] for c in cfg]
    if AVANT not in ids:
        return None
    i = ids.index(AVANT)
    modele = cfg[i]
    for cid in colonnes_vue():   # v7 : sans Rapports médias si l'option le dit
        c = copy.deepcopy(modele)
        c["m_columnID"] = cid
        c["m_columnMetadata"]["m_titleTranslationIdOverride"] = {"GameID": 0}   # titre de la fabrique
        cfg.insert(i, c)
        i += 1
    larg = poids(LARGEURS)
    for c in cfg:
        if c["m_columnID"] in larg:
            m = c["m_columnMetadata"]
            m["m_widthOverride"] = float(larg[c["m_columnID"]])
            m["m_minWidthOverride"] = float(min(larg[c["m_columnID"]], MIN_COLONNE))
    return cfg


def vue_a_jour(env):
    for _, tt in monos(env, {VUE}):
        cfg = tt["m_tableView"]["m_tableConfig"]
        return cfg == vue_voulue(cfg)
    return False


_VUE_FM = None   # v5 : la vue de FM telle que vue_poser vient de la laisser (UnityPy ne relit pas un objet modifié :
#                  read_typetree après save_typetree rend l'ANCIEN contenu, mesuré le 14/10)


def vue_poser(env):
    """True si changé ; None si la vue ou la note est introuvable"""
    global _VUE_FM
    for o, tt in monos(env, {VUE}):
        cfg = tt["m_tableView"]["m_tableConfig"]
        voulue = vue_voulue(cfg)
        if voulue is None:
            return None
        if voulue == cfg:
            _VUE_FM = copy.deepcopy(tt)
            return False
        tt["m_tableView"]["m_tableConfig"] = voulue
        o.save_typetree(tt)
        _VUE_FM = copy.deepcopy(tt)
        return True
    return None


def vue_retirer(env):
    """nos colonnes retirées, les largeurs de FM rendues d'après l'original (colonnes d'Alex non touchées)"""
    orig = {c["m_columnID"]: c for c in (config_origine() or [])}
    for o, tt in monos(env, {VUE}):
        cfg = tt["m_tableView"]["m_tableConfig"]
        neuf = [copy.deepcopy(c) for c in cfg if c["m_columnID"] not in NOUVELLES]
        for c in neuf:
            if c["m_columnID"] in LARGEURS and c["m_columnID"] in orig:
                c["m_columnMetadata"] = copy.deepcopy(orig[c["m_columnID"]]["m_columnMetadata"])
        if neuf != cfg:
            tt["m_tableView"]["m_tableConfig"] = neuf
            o.save_typetree(tt)
            return True
    return False


# ---------- v5 : les vues des deux tableaux à nous (vues de FM citées par rien, réécrites) ----------
def vue_tableau_voulue(ev, cle):
    """le m_tableView voulu pour notre tableau « cle » : celui de la vue de FM (telle que l'ont laissée Alex, 26.14 et
    la v2), sans les colonnes retirées, avec les largeurs (poids) et minimums de TABLEAUX ; None sans vue de FM"""
    _, _, largeurs, retirees, *_ = TABLEAUX[cle]
    largeurs = poids(largeurs, cle)   # v7, v8
    vues_fm = [_VUE_FM] if _VUE_FM is not None else [tt for _, tt in monos(ev, {VUE})]   # celle que vue_poser a laissée
    for tt in vues_fm:
        tv = copy.deepcopy(tt["m_tableView"])
        tv["m_tableConfig"] = [c for c in tv["m_tableConfig"] if c["m_columnID"] not in retirees]
        for c in tv["m_tableConfig"]:
            if c["m_columnID"] in largeurs:
                m = c["m_columnMetadata"]
                m["m_widthOverride"] = float(largeurs[c["m_columnID"]])
                m["m_minWidthOverride"] = float(min(largeurs[c["m_columnID"]], MIN_COLONNE))
        return tv
    return None


def vues_tableaux_a_jour(ev):
    for cle, (nom, *_) in TABLEAUX.items():
        voulue = vue_tableau_voulue(ev, cle)
        if voulue is None or not any(tt["m_tableView"] == voulue for _, tt in monos(ev, {nom})):
            return False
    origines = _origines(ANCIENNES_VUES)   # v10 : les anciennes vues rendues à FM
    return all(tt["m_tableView"] == origines.get(tt["m_Name"], tt["m_tableView"])
               for _, tt in monos(ev, set(ANCIENNES_VUES)))


def _origines(noms):
    """{nom : m_tableView de la sauvegarde de l'original} (vide sans sauvegarde)"""
    orig = backup.backup_path(VUES)
    if not os.path.exists(orig):
        return {}
    return {tt["m_Name"]: tt["m_tableView"] for _, tt in monos(UnityPy.load(orig), set(noms))}


def rendre_vues(ev, noms):
    """vues « noms » rendues d'après la sauvegarde de l'original ; True si changé"""
    origines = _origines(noms)
    change = False
    for o, tt in monos(ev, set(noms)):
        if tt["m_Name"] in origines and tt["m_tableView"] != origines[tt["m_Name"]]:
            tt["m_tableView"] = copy.deepcopy(origines[tt["m_Name"]])
            o.save_typetree(tt)
            change = True
    return change


def vues_tableaux_poser(ev):
    """True si changé ; None si une vue (la nôtre ou celle de FM) est introuvable"""
    change = False
    for cle, (nom, *_) in TABLEAUX.items():
        voulue = vue_tableau_voulue(ev, cle)
        trouvees = list(monos(ev, {nom}))
        if voulue is None or len(trouvees) != 1:
            return None
        o, tt = trouvees[0]
        if tt["m_tableView"] != voulue:
            tt["m_tableView"] = voulue
            o.save_typetree(tt)
            change = True
    return rendre_vues(ev, ANCIENNES_VUES) or change   # v10 : les vues des tireurs rendues à FM


def vues_tableaux_retirer(ev):
    """nos vues (et les anciennes, v10) rendues d'après la sauvegarde de l'original (backups\\) ; True si changé"""
    return rendre_vues(ev, [nom for nom, *_ in TABLEAUX.values()] + list(ANCIENNES_VUES))


# ---------- commandes ----------
def cmd_appliquer():
    o = ouvrir(ECRAN)
    if o is None:
        print(f"[Kinito] Largeur de la liste : {ECRAN} introuvable (renommé par une mise à jour ?), ignoré")
        return
    ef, ev = UnityPy.load(FABRIQUES), UnityPy.load(VUES)
    if a_jour(o[3]) and fabrique_a_jour(ef) and vue_a_jour(ev) and vues_tableaux_a_jour(ev):
        print("[Kinito] Largeur de la liste : déjà appliqué")
    else:
        # v2 : les colonnes. La fabrique d'abord : la vue cite ses colonnes (jamais la vue sans elles) ; v5 : les vues
        # AVANT l'écran (nos tableaux ne doivent jamais citer une vue d'autres colonnes)
        f = fabrique_poser(ef)
        v = None
        if f is None:
            print(f"[Kinito] Largeur de la liste : colonnes {', '.join(NOUVELLES)} introuvables dans "
                  f"{SOURCE_COLONNES} (le jeu a changé ?) : colonnes pas ajoutées")
        else:
            if f:
                ecrire_bundle(ef, FABRIQUES)
            v = vue_poser(ev)
            if v is None:
                print(f"[Kinito] Largeur de la liste : vue {VUE} ou sa colonne {AVANT} introuvable : vue pas touchée")
            else:
                print(f"[Kinito] Largeur de la liste : colonnes Personnalité"
                      + (" et Rapports médias" if avec_medias() else " (Rapports médias enlevée : option)")
                      + " avant la note ; largeurs (Medium, Small) : "
                      + ", ".join(f"{k} {w}" for k, w in poids(LARGEURS).items()))
        vt = vues_tableaux_poser(ev)   # v5
        if v or vt:
            ecrire_bundle(ev, VUES)
        if vt is None:
            print(f"[Kinito] Largeur de la liste : vues {', '.join(n for n, *_ in TABLEAUX.values())} ou {VUE} "
                  f"introuvables : écran pas touché")
            return
        for cle, (nom, _, largeurs, retirees, *_r) in TABLEAUX.items():
            print(f"[Kinito] Largeur de la liste : vue {nom} (mode Large, texte "
                  f"{ {'petit': 'Petit', 'normal': 'Normal', 'grand': 'Grand'}.get(cle, 'Plus grand') }) : "
                  + ", ".join(f"{k} {w}" for k, w in poids(largeurs, cle).items())
                  + (f" ; sans {', '.join(retirees)}" if retirees else ""))
        if not a_jour(o[3]):
            retirer(o[3])   # une ancienne version, s'il y en a une
            msgs = poser(o[3], sources())
            for m in msgs:
                print(f"[Kinito] Largeur de la liste : {m}")
            if any("introuvable" in m for m in msgs):
                print("[Kinito] Largeur de la liste : rien enregistré pour l'écran")
                return
            enregistrer(*o)
            nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    o = ouvrir(ECRAN)
    if o is not None and retirer(o[3]):
        enregistrer(*o)
        nb.save_all()
        print(f"{ECRAN} : liste de gauche rendue à sa largeur de FM (30 %), nos éléments retirés")
        fait = True
    ev = UnityPy.load(VUES)   # la vue d'abord (elle cite les colonnes de la fabrique), APRÈS l'écran (v5)
    v, vt = vue_retirer(ev), vues_tableaux_retirer(ev)
    if v or vt:
        ecrire_bundle(ev, VUES)
        if v:
            print(f"{VUE} : nos colonnes retirées, largeurs de FM rendues")
        if vt:
            print(f"{', '.join(n for n, *_ in TABLEAUX.values())} : vues de FM rendues d'origine")
        fait = True
    ef = UnityPy.load(FABRIQUES)
    if fabrique_retirer(ef):
        ecrire_bundle(ef, FABRIQUES)
        print(f"{FABRIQUE} : nos colonnes retirées")
        fait = True
    if not fait:
        print("rien à retirer")


def cmd_etat():
    o = ouvrir(ECRAN)
    if o is None:
        print(f"{ECRAN} : introuvable")
    else:
        t = o[3]
        b = bloc_liste(t)
        print(f"{ECRAN} : " + ("bloc de la liste introuvable" if b is None else
                               f"liste de gauche " + (f"élargie (à jour, v{VERSION})" if a_jour(t) else
                                                      ("ANCIENNE version" if marques(t) else "de FM (30 %)"))))
    ef, ev = UnityPy.load(FABRIQUES), UnityPy.load(VUES)
    print(f"{FABRIQUE} : colonnes {', '.join(NOUVELLES)} " + ("présentes" if fabrique_a_jour(ef) else "absentes"))
    print(f"{VUE} : " + ("nos colonnes et largeurs (à jour)" if vue_a_jour(ev) else "de FM ou ANCIENNE version"))
    print(f"{', '.join(n for n, *_ in TABLEAUX.values())} : " + ("nos vues (à jour)" if vues_tableaux_a_jour(ev)
                                                                 else "de FM ou ANCIENNE version"))
    if o is not None:
        t = o[3]
        print(f"{ECRAN} : tableaux de la vue Détails : " + (
            f"{1 + len(TABLEAUX)}, un seul visible selon le mode et la taille du texte (à jour)" if tableaux_a_jour(t) else
            f"{len(tableaux(t))} (celui de FM seul)" if len(tableaux(t)) == 1 else f"{len(tableaux(t))} (ANCIENNE version ?)"))
        print(f"{ECRAN} : tableau de la vue Résumé : " + (
            "trié par la note au départ, tri gardé (à jour)" if resume_a_jour(t) else
            "introuvable" if tableau_resume(t) is None else "celui de FM (sans tri de départ, tri pas gardé)"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("[Kinito] Largeur de la liste : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
