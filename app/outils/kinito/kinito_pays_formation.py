"""[AJOUT KINITO] 26.21 — Page d'un pays (Vue d'ensemble) : dans la bande du haut, à côté de Population, la NOTE DE
FORMATION des jeunes du pays (hommes et femmes, en chiffre) et la PLAGE D'ARRIVÉE DES JEUNES du pays (du premier au
dernier jour où ses clubs reçoivent leurs jeunes).
Demande de Kinito (07/11/2026) : « une note de formation des pays, l'afficher dans la barre du haut à côté de la
population » ; « chaque pays a une date de début de spawn des newgens et une date de fin ; les meilleurs clubs spawnent
en premier ; ce que je veux trouver c'est la plage de date de chaque pays ». Ses choix : le chiffre seul, hommes et
femmes.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie « Ajouts Kinito » du menu.

Comment (tout mesuré le 07/11/2026, dans le code du jeu et EN JEU par la sonde FMSonde 0.23, partie de Kinito) :
- L'ÉCRAN : le modèle de FM NationSiteHeaderTemplate (bundle global), inclus par le SEUL NationSiteHeader : rien ne
  change ailleurs. Aucun script d'Alex ne le cite. Sa rangée #RHS : Population | Langues | (Devise) | Accords, chaque
  case = un titre (texte traduit de FM) au-dessus d'une valeur, séparées par layout-divider-solid-vertical.
- LA NOTE : jusqu'en v3, « YouthRating » d'un NationalTeamContainerReference (Nation.MainMenTeamContainer /
  MainWomanTeamContainer) : un PALIER de 11 à 20 (France 18 et 19), seul chiffre que le jeu donne. Titre : le texte
  de FM de sa tuile des sélections (n° 37377, « National Youth Rating »), traduit par le jeu ; « Hommes » / « Femmes » :
  les textes de FM des onglets de la liste des clubs du pays (n° 20775, 20776).
- v4, LA NOTE SUR 200 AU DÉPART (Kinito, 07-08/11 : « la note sur 200, pas sur 20 » ; puis « la note de base, toujours
  la même au début »). Le palier vient du champ NYRt (sur 200) de la sélection ; le jeu ne donne NYRt à aucun écran
  (vérifié dans son code : seul YouthRating s'en sert ; la table de debug est vide dans le jeu publié ; l'éditeur
  intégré est absent d'une partie normale), et le fait bouger d'un point de temps en temps. La note de chaque pays au
  DÉPART d'une partie est donc ÉCRITE ICI (NOTES_DEPART, 251 pays, lue en mémoire par la sonde FMSonde 0.24.1 dans une
  partie neuve). Le skin la choisit par l'identifiant du pays de la page (Nation.UniqueId) : un commutateur de FM par
  pays et par sexe, mené par la liaison de FM BindIntComparisonToSwitch (f6f314e9, recopiée de ClubBoardTile_4x8) :
  TryCastToInt (une valeur vide n'est jamais une erreur, contrairement à Get<int> qui a fermé FM en v1), « == »,
  puis l'enfant 1 (la note, texte fixe comme ceux du skin d'Alex) si vrai, l'enfant 0 (vide) sinon. Deux enfants
  seulement : le commutateur de FM cache ses enfants par un masque de 64 bits (SI.UI.SwitchElement.SetVisible).
  Un pays absent de la table (autre base de données) : pas de chiffre. Fausse avec une autre base de données.
- LA PLAGE : FM ne range la date d'arrivée des jeunes que par CLUB (Club.IntakeDate). Mesuré sur 6 pays : les clubs
  arrivent dans l'ordre de réputation (1 à 3 par jour), tous les autres le dernier jour ; la liste des clubs du pays
  (Nation.ClubListNation, déjà triée par réputation) a donc le PREMIER jour sur son 1er club et le DERNIER sur son
  dernier. La durée change d'un pays à l'autre (28 jours en Europe, 7 au Brésil) : on lit bien le dernier club.
  ClubListNation exige deux contextes (NationReference::GetContextsInternal) : « Gender » (Bool) et « FilterListID »
  (Int) ; déclarés ici comme le fait la tuile de FM NationClubsListTile (gender False = hommes, FilterListID 0).
  Le 1er club : BindFirstItemOrNullFromList (35447e7a, recopiée de ActionsListWidget) ; le dernier : le NOMBRE de
  clubs par BindListItemsCountToInt (2fe07f5c), son rang par BindListLastIndexToDestination (2849202c) — les deux
  comme FM les enchaîne dans FinancesDebtsAndLoansBlock_8x3 —, puis
  BindListItemUsingIndexBindingToDestinationIfNotNull (908f68f4, de ClubInfoReportBlock ; un rang hors de la liste
  y donne « rien », jamais une erreur : GetTypedValueOrNullAtIndex).
  PIÈGE (v1, vu en jeu le 07/11 : FM se fermait à l'ouverture d'une page Pays) : malgré son nom, 2849202c ne prend
  PAS une liste mais un NOMBRE (son entrée s'appelle countBinding : « nombre - 1 ») ; lui donner la liste fait
  « Unable to cast List to DynamicNumber », exception que FM ne rattrape pas. Lire les ENTRÉES d'une fonction de FM
  (son graphe dans ui-visualfunctions) et son usage d'origine, jamais seulement son nom.
- LA GARDE DE FM : la date d'un club n'est lue que si Club.ClubNationHasValidRuleGroupRules est vrai (FM fait pareil
  dans sa tuile YouthSetupTile) : un pays non joué dans la partie (Algérie) n'a pas de plage, la case ne s'affiche pas.
- ATTENTION, MESURÉ : UNE équipe de France (rang 1115 sur 1963, partie de Kinito) FIGE LE JEU dès qu'on lit son nom.
  On ne lit donc QUE le 1er et le dernier club, jamais la liste entière ; le dernier club s'est lu sans blocage dans
  les 6 pays essayés, sans preuve que ce soit vrai partout.
- TEXTES : titre « [%date#1-year] Youth Intake » de FM (n° 14242, celui de sa tuile des jeunes), traduit par le jeu,
  avec l'année du 1er club ; valeur « [%date#1-date_short_month] - [%date#2-date_short_month] » (formats de date de FM).
- PETITS ÉCRANS : comme la Devise de FM, rien sur téléphone ni en petit affichage (mêmes deux SIVisible recopiés).
- v5, LA FIN DE LA PLAGE : FM ne donne pas de date à toutes les équipes (équipes B, quelques clubs : 35 des 400
  premières d'Allemagne, sonde 0.23.4) ; vu en jeu le 08/11, le dernier club d'Allemagne n'en avait pas et FM écrivait
  « date#2 ». On essaie donc les 6 derniers clubs, du dernier vers l'avant (rang : « nombre - 1 » de FM, enchaîné), et
  on garde le premier QUI A une date : une garde de FM (SIVisible) sur sa Club.IntakeDate (une valeur vide vaut faux :
  BindableWidgetUtils.EvaluateAsBoolean, lu dans le code du jeu). Une garde cachée ne lie pas ses enfants : le club
  suivant n'est lu que si le précédent n'a pas de date. Aucun des 6 : « 10 mar - ? » (la fin n'est jamais devinée).
- v5, LA PAGE D'UNE SÉLECTION (« Allemagne (Hommes) », modèle NationalTeamSiteHeader, bundle gameworld, cité par la
  seule fabrique des en-têtes ReportHeaderFactory ; aucun script d'Alex ne le cite) : après Classement mondial, deux
  cases recopiées de lui (titre, icône de FM, valeur) : la note sur 200 au départ du SEUL sexe de l'équipe, et
  l'arrivée des jeunes de la liste des clubs de ce sexe (contexte « gender » vrai pour les femmes). Un commutateur de
  FM choisit le bloc, recopié de NewsNationalTeamSiteHeader, où FM fait la même chose (« teamcontainer.Gender == 0 » :
  enfant 1, « mentext ») ; il n'instancie que le bloc montré. Les chemins passent par le renvoi « nation » que FM
  pose dans cet en-tête (NTContainer.Nation).

- v6, TOUTES LES PLAGES TROUVÉES (Kinito, 09/11 : « ajoute toutes les dates qu'on a trouvées à tous les pays ») : un
  pays SANS règles dans la partie (le jeu ne donne aucune date à ses clubs) montrait « dans N jours », qui n'est PAS une
  date d'arrivée (vérifié en jeu le 08/11). Il montre maintenant sa plage relevée en jeu (table PLAGES_TROUVEES : la
  liste « Arrivées jeunes » de chaque pays sur 5 saisons, sondes 0.27.3 et 0.27.4), sous le titre de FM sans année ;
  un commutateur de FM par pays, comme la note. Un pays AVEC règles garde la date en direct de ses clubs (année
  comprise). La page d'un pays montre maintenant les hommes ET les femmes (« Hommes 10 mar - 7 avr », « Femmes … »),
  chaque sexe sa liste de clubs et sa garde ; la page d'une sélection, son seul sexe.

- v8, LES TITRES (Kinito, 10/11) : « Note de formation des jeunes » et « Arrivée des jeunes », écrits tels quels
  (texte fixe), sans l'année ; ils remplacent les textes de FM « Niveau général de la formation » et
  « Arrivées des jeunes : 2032 » / « Arrivées des jeunes en ».

- v9, LA GÉORGIE (Kinito, 12/11 : « quand j'arrive sur la Géorgie en faisant défiler les pays, le jeu crash, à chaque
  fois ») : FM se fermait sans un mot dans son journal. Seul pays SANS règles que le code du jeu cite nommément ; pour
  elle, plus aucune lecture de club : sa plage trouvée, écrite telle quelle (GEORGIE, bloc_dates).

- v10, PLUS AUCUNE LECTURE DE CLUB (Kinito, 12/11 : la v9 passe la Géorgie, mais FM se ferme sur Gibraltar ; « afficher
  les dates qu'on a trouvées en dur pour tous les pays ») : l'arrivée des jeunes de CHAQUE pays, hommes et femmes, est
  la plage relevée en jeu (PLAGES_TROUVEES), écrite en dur ; tout ce qui est décrit plus haut sur la liste des clubs,
  le 1er et les derniers clubs, la garde des règles, est retiré.

- v11, LA LANGUE DU JEU (Kinito, 13/11 : « Oui, traduis ») : la langue réglée dans FM, lue en direct (recette 19 :
  le conteneur de FM de tdd-messages-banner, un interrupteur par langue) ; titres : ceux de FM (« Youth Rating »,
  « Youth Intake » et leurs traductions), en français ceux de Kinito ; dates : les mois abrégés, l'ordre du jour et du
  mois et les ordinaux de FM dans chaque langue (« 9th Mar », « 9. Mär », « 3月9日 »), tirés de son fichier de langues ;
  les notes (chiffres) et « Hommes » / « Femmes » (textes de FM) suivaient déjà la langue.

Touché : NationSiteHeaderTemplate (bundle global) : UNE enveloppe à nous dans #RHS, après la case Population et son
trait (nom UIPickerKinito-pays-formation-v<n>), ses règles de style intégrées ; v5, NationalTeamSiteHeader (bundle
gameworld) : UNE enveloppe à nous après Classement mondial et son trait (UIPickerKinito-pays-formation-selection-v<n>).
Retirer les enlève avec leurs règles.
Lus seulement : les originaux de ces modèles et des modèles sources (fonctions, BindingSetter, commutateurs, textes).

Usage (jeu fermé) :
  python outils\\kinito\\kinito_pays_formation.py appliquer [--dry-run]
  python outils\\kinito\\kinito_pays_formation.py retirer
  python outils\\kinito\\kinito_pays_formation.py etat
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories de l'app d'Alex)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import no_styles  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402
try:   # app d'Alex 1.62 et plus : recopie un type de référence qu'un bundle ne déclare pas (ici : tous déjà déclarés)
    from elements import types_ref_manquants  # noqa: E402
except ImportError:   # pragma: no cover
    def types_ref_manquants(obj, tt):
        return []

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
MODELE = "NationSiteHeaderTemplate"
POPULATION = "Population"             # la case de FM recopiée pour nos deux cases
DEVISE = "Currency"                   # sa double garde (téléphone, petit affichage) recopiée autour de l'ajout
TRAIT = "layout-divider-solid-vertical"

NOTE_H, NOTE_F = "Nation.MainMenTeamContainer.YouthRating", "Nation.MainWomanTeamContainer.YouthRating"
# v8 : les deux titres, écrits par Kinito (10/11/2026 : « pour la date d'arrivée on met comme intitulé "Arrivée des
# jeunes", c'est tout, rien de plus » ; « pour la note on met "Note de formation jeune" », corrigé en « des jeunes »,
# comme l'autre titre). Texte fixe, comme les valeurs : plus le titre de FM « Niveau général de la formation » (n° 37377)
# ni ses « Arrivées des jeunes : 2032 » / « Arrivées des jeunes en » (n° 14242 et 14243, avec l'année du 1er club).
# v11 : ces deux titres sont ceux du FRANÇAIS ; dans les autres langues du jeu, ceux de FM (« Youth Rating »,
# « Youth Intake » et leurs traductions : LANGUES_PAGE)
TITRE_NOTE = "Note de formation des jeunes"
TITRE_ARRIVEE = "Arrivée des jeunes"
T_HOMMES, T_FEMMES = (20775, "Mens"), (20776, "Womens")    # onglets de FM de la liste des clubs (ClubsListPanel)

FONCTION_TRADUIT = "eae2be944eee9e2449baef416111a087"     # StaticText (un n° de traduction de FM)
FONCTION_FORMAT = "aeb3536b8c3b6e64b8690d740a14587c"      # FormatTextWithArguments (modèle + données)
ESPACE_MOT = 4           # entre « Hommes » et sa note (unités)
ESPACE_GENRE = 10        # entre la note des hommes et « Femmes »

# v4 : la note sur 200 au départ (table NOTES_DEPART ci-dessous), choisie par l'identifiant du pays de la page
UID_PAYS = "Nation.UniqueId"
# v11 : la langue du jeu (recette 19, celle de 26.13 v24 et 26.18) : le conteneur de FM de tdd-messages-banner (bundle
# global) qui lit le réglage de langue, et son interrupteur (texte == languagesetting.PropertyValue)
SOURCE_LANGUE = "tdd-messages-banner"
FONCTION_LANGUE = "7980ef35a33c35e43940a2b7add470dd"
LANGUE_DEFAUT = "english"   # aussi « english (us) » (mêmes textes) et une langue que FM 27 n'a pas (czech, thai…)
SOURCE_COMMUTATEUR = "ActiveNationCheckbox"               # un BindableSwitchElement du MÊME bundle (global) que l'en-tête
SOURCE_COMPARAISON = ("ClubBoardTile_4x8", "f6f314e9")    # BindIntComparisonToSwitch, liaison d'un commutateur de FM
EGAL = 2                                                  # ComparisonOperator.Equal (SI.VisualScripting : 0 <, 1 <=, 2 ==)

# v5 : la page d'une sélection (« Allemagne (Hommes) »), après Classement mondial
MODELE_SELECTION = "NationalTeamSiteHeader"     # bundle gameworld, cité par la seule fabrique ReportHeaderFactory
CLASSEMENT, SURNOM = "WorldRanking", "Nickname"   # la case recopiée ; la double garde (téléphone, petit) recopiée
ICONE_FM = "game-concepts-draft-league-knockout_small"                       # l'icône de la case Classement mondial
ICONE_NOTE, ICONE_DATE = "game-concepts-youth-squad_small", "ui-concepts-calendar_small"   # icônes de FM (FMImages)
GENRE_EQUIPE = "NTContainer.Gender"             # 0 : hommes (lu dans NewsNationalTeamSiteHeader, « == 0 » -> mentext)
UID_SEL = "nation.UniqueId"                     # « nation » : le renvoi de FM de cet en-tête
SOURCE_COMMUTATEUR_SEL = "NewsNationalTeamSiteHeader"      # le commutateur hommes / femmes de FM, même bundle
# =====================================================================================================

# v4 : la NOTE SUR 200 de chaque pays AU DÉPART d'une partie (champ NYRt de chaque sélection nationale), lue en
# mémoire par FMSonde 0.24.1 (Ctrl+F7) le 08/11/2026 à 1 h 35, dans une partie NEUVE au premier jour (jeu 27.0.0.2493426,
# base de données d'origine). Source : chantier-pays\notes-formation-depart-FM27.json. Le jeu ne la montre nulle part
# (seulement le palier 11 à 20) et la fait bouger d'un point de temps en temps en cours de partie : c'est la note du
# DÉBUT, fausse avec une autre base de données. Après une mise à jour du jeu : refaire Ctrl+F7 dans une partie neuve.
NOTES_DEPART = {   # identifiant du pays : (hommes, femmes), sur 200
    5: (102, 64),   # Algérie
    6: (75, 33),   # Angola
    7: (55, 11),   # Bénin
    8: (42, 45),   # Botswana
    9: (70, 47),   # Burkina Faso
    10: (40, 16),   # Burundi
    11: (100, 76),   # Cameroun
    12: (46, 31),   # Cap-Vert
    13: (17, 23),   # République centrafricaine
    14: (26, 5),   # Tchad
    15: (7, 5),   # Djibouti
    16: (125, 65),   # Égypte
    17: (28, 65),   # Guinée Équatoriale
    18: (51, 45),   # Éthiopie
    19: (49, 43),   # Gabon
    20: (49, 55),   # Gambie
    21: (99, 75),   # Ghana
    22: (64, 15),   # Guinée
    23: (18, 60),   # Guinée-Bissau
    24: (105, 72),   # Côte d'Ivoire
    25: (55, 45),   # Kenya
    26: (25, 15),   # Lesotho
    27: (32, 14),   # Liberia
    28: (46, 5),   # Libye
    29: (28, 14),   # Madagascar
    30: (51, 29),   # Malawi
    31: (73, 63),   # Mali
    32: (25, 25),   # Mauritanie
    33: (21, 13),   # Île Maurice
    34: (85, 82),   # Maroc
    35: (64, 13),   # Mozambique
    36: (39, 33),   # Namibie
    37: (31, 12),   # Niger
    38: (120, 95),   # Nigeria
    39: (42, 12),   # Rwanda
    40: (7, 0),   # São Tomé-et-Príncipe
    41: (80, 62),   # Sénégal
    42: (21, 12),   # Seychelles
    43: (29, 35),   # Sierra Leone
    44: (9, 0),   # Somalie
    45: (95, 88),   # Afrique du Sud
    46: (74, 5),   # Soudan
    47: (14, 12),   # Eswatini
    48: (80, 47),   # Tanzanie
    49: (50, 55),   # Congo
    50: (64, 48),   # Togo
    51: (82, 72),   # Tunisie
    52: (59, 39),   # Ouganda
    53: (101, 63),   # République démocratique du Congo
    54: (61, 79),   # Zambie
    55: (44, 51),   # Zimbabwe
    106: (19, 5),   # Afghanistan
    107: (82, 60),   # Bahreïn
    108: (36, 49),   # Bangladesh
    109: (6, 1),   # Sultanat de Brunei
    110: (60, 106),   # Chine
    111: (47, 53),   # Hong Kong (RP de Chine)
    112: (86, 77),   # Inde
    113: (56, 51),   # Indonésie
    114: (110, 80),   # Iran
    115: (103, 18),   # Irak
    116: (112, 137),   # Japon
    117: (90, 76),   # Jordanie
    118: (8, 47),   # Cambodge
    119: (66, 75),   # Kazakhstan
    120: (75, 5),   # Koweït
    121: (46, 51),   # Kirghizistan
    122: (7, 64),   # Laos
    123: (85, 51),   # Liban
    124: (5, 14),   # Macao (RP de Chine)
    125: (35, 34),   # Malaisie
    126: (50, 32),   # Maldives
    127: (50, 85),   # Birmanie
    128: (13, 54),   # Népal
    129: (84, 115),   # Corée du Nord
    130: (70, 0),   # Oman
    131: (37, 32),   # Pakistan
    132: (105, 5),   # Qatar
    133: (105, 36),   # Arabie saoudite
    134: (35, 52),   # Singapour
    135: (110, 107),   # Corée du Sud
    136: (16, 41),   # Sri Lanka
    137: (85, 28),   # Syrie
    138: (14, 90),   # Taipei chinois (RP de Chine)
    139: (46, 34),   # Tadjikistan
    140: (86, 88),   # Thaïlande
    141: (30, 93),   # Philippines
    142: (40, 38),   # Turkménistan
    143: (97, 49),   # Émirats arabes unis
    144: (85, 87),   # Ouzbékistan
    145: (70, 83),   # Vietnam
    146: (55, 0),   # Yémen
    359: (30, 11),   # Antigua-et-Barbuda
    360: (20, 11),   # Aruba
    361: (34, 30),   # Barbade
    362: (15, 17),   # Bélize
    363: (28, 34),   # Bermudes
    364: (54, 125),   # Canada
    365: (16, 13),   # Îles Caïmans
    366: (66, 87),   # Costa Rica
    367: (51, 59),   # Cuba
    368: (15, 55),   # Dominique
    370: (55, 59),   # Salvador
    371: (26, 6),   # Grenade
    373: (58, 75),   # Guatemala
    374: (37, 51),   # Guyana
    375: (59, 60),   # Haïti
    376: (68, 46),   # Honduras
    377: (59, 90),   # Jamaïque
    379: (120, 109),   # Mexique
    380: (35, 27),   # Curaçao
    381: (18, 48),   # Nicaragua
    382: (49, 51),   # Panama
    383: (30, 61),   # Porto Rico
    384: (28, 33),   # Sainte-Lucie
    385: (28, 49),   # Saint-Kitts et Névis
    386: (34, 43),   # Saint-Vincent
    387: (47, 51),   # Suriname
    388: (11, 26),   # Bahamas
    389: (57, 78),   # Trinité-et-Tobago
    390: (110, 165),   # États-Unis
    574: (0, 0),   # C.A.E.M.
    575: (0, 0),   # Tchécoslovaquie
    577: (0, 0),   # Allemagne de l'Est
    583: (0, 0),   # Union Soviétique
    584: (0, 0),   # Allemagne de l'Ouest
    752: (65, 83),   # Albanie
    753: (36, 42),   # Andorre
    754: (47, 52),   # Arménie
    755: (79, 118),   # Autriche
    756: (48, 61),   # Azerbaïdjan
    757: (120, 113),   # Belgique
    758: (62, 76),   # Biélorussie
    759: (78, 88),   # Bosnie-Herzégovine
    760: (72, 74),   # Bulgarie
    761: (98, 90),   # Croatie
    762: (74, 62),   # Chypre
    763: (94, 104),   # République tchèque
    764: (91, 124),   # Danemark
    765: (135, 161),   # Angleterre
    766: (62, 69),   # Estonie
    767: (42, 71),   # Îles Féroé
    768: (75, 105),   # Finlande
    769: (155, 160),   # France
    770: (81, 63),   # Géorgie
    771: (155, 155),   # Allemagne
    772: (94, 84),   # Grèce
    773: (68, 76),   # Hongrie
    774: (67, 115),   # Islande
    775: (84, 84),   # Israël
    776: (144, 125),   # Italie
    777: (63, 60),   # Lettonie
    778: (42, 75),   # Liechtenstein
    779: (59, 70),   # Lituanie
    780: (35, 67),   # Luxembourg
    781: (71, 59),   # Macédoine du Nord
    782: (42, 68),   # Malte
    783: (46, 55),   # Moldavie
    784: (132, 138),   # Pays-Bas
    785: (79, 91),   # Irlande du Nord
    786: (82, 126),   # Norvège
    787: (94, 103),   # Pologne
    788: (134, 119),   # Portugal
    789: (83, 109),   # Irlande
    790: (91, 93),   # Roumanie
    791: (118, 101),   # Russie
    792: (29, 4),   # Saint-Marin
    793: (83, 107),   # Écosse
    794: (79, 93),   # Slovaquie
    795: (78, 95),   # Slovénie
    796: (145, 160),   # Espagne
    797: (88, 140),   # Suède
    798: (90, 113),   # Suisse
    799: (124, 81),   # Turquie
    800: (110, 99),   # Ukraine
    801: (71, 90),   # Pays de Galles
    802: (100, 102),   # Serbie
    1435: (90, 126),   # Australie
    1436: (8, 39),   # Îles Cook
    1437: (36, 67),   # Îles Fidji
    1438: (88, 97),   # Nouvelle-Zélande
    1439: (34, 41),   # Papouasie-Nouvelle-Guinée
    1440: (40, 51),   # Îles Salomon
    1441: (39, 43),   # Tahiti
    1442: (8, 48),   # Îles Tonga
    1443: (33, 26),   # Vanuatu
    1444: (14, 46),   # Samoa
    1649: (140, 110),   # Argentine
    1650: (59, 69),   # Bolivie
    1651: (163, 132),   # Brésil
    1652: (93, 98),   # Chili
    1653: (117, 111),   # Colombie
    1654: (94, 83),   # Équateur
    1655: (90, 87),   # Paraguay
    1656: (97, 80),   # Pérou
    1657: (90, 81),   # Uruguay
    1658: (71, 89),   # Venezuela
    1662: (51, 41),   # Palestine
    100349: (0, 0),   # Tamil
    103277: (0, 0),   # Zaïre
    114502: (0, 0),   # Pays Basque
    129504: (5, 1),   # Samoa américaines
    129505: (15, 45),   # Mongolie
    129508: (6, 55),   # Guam
    129511: (8, 5),   # Érythrée
    129514: (8, 12),   # Anguilla
    129517: (10, 41),   # Îles Vierges
    129520: (8, 0),   # Montserrat
    129523: (8, 26),   # Îles Vierges US
    129526: (9, 24),   # Îles Turks-et-Caïcos
    129532: (34, 48),   # Nouvelle-Calédonie
    131012: (4, 25),   # Bhoutan
    142527: (35, 28),   # République dominicaine
    145174: (0, 0),   # Grande-Bretagne
    208996: (0, 0),   # Yémen du Sud
    209002: (1, 0),   # Kiribati
    214394: (40, 58),   # Gibraltar
    214395: (15, 1),   # Bonaire
    215446: (1, 0),   # Crimée
    217945: (60, 68),   # Kosovo
    219003: (0, 0),   # Royaume-Uni
    788980: (0, 0),   # SEA chinoise
    788987: (0, 0),   # Singh
    788995: (0, 0),   # Bornéo (Malais)
    788999: (0, 0),   # Malaisie occidentale
    917496: (40, 0),   # Guyane
    917498: (48, 0),   # Guadeloupe
    917502: (46, 0),   # Martinique
    917506: (10, 0),   # Saint-Martin (PB)
    917508: (10, 0),   # Saint-Martin
    917510: (7, 0),   # La Réunion
    918740: (7, 0),   # Mayotte
    918745: (3, 0),   # Îles Wallis-et-Futuna
    918748: (5, 0),   # Saint-Pierre-et-Miquelon
    919586: (7, 23),   # Comores
    5626565: (0, 0),   # Vietnam du Sud
    5626837: (5, 31),   # Timor Oriental
    5630219: (0, 0),   # Birmanie
    8162661: (0, 0),   # Monaco
    13100103: (7, 0),   # Zanzibar
    13113220: (7, 23),   # Soudan du Sud
    13116454: (0, 0),   # Haute-Volta
    15064643: (2, 0),   # Micronésie
    23008660: (1, 0),   # Îles Mariannes du Nord
    23088616: (5, 18),   # Tuvalu
    29118470: (0, 0),   # République arabe unie
    52024163: (0, 0),   # Irlande
    62002127: (60, 76),   # Monténégro
    62003815: (0, 0),   # Yougoslavie
    82082526: (20, 0),   # Saint-Barthélemy
    82082540: (1, 0),   # Antilles néerlandaises
}

# v6-v11 : la PLAGE D'ARRIVÉE DES JEUNES de chaque pays, relevée par FMSonde 0.27.3 et 0.27.4 (Ctrl+Maj+F7, 09/11/2026) :
# la liste « Arrivées jeunes » de chaque pays, mois par mois, sur 5 saisons d'une partie simulée (base complète, jeu
# 27.0.0.2493426) ; jour de début et de fin les plus fréquents. v10 : écrite EN DUR pour TOUS les pays (plus aucune
# lecture de club : FM se fermait sur la Géorgie et Gibraltar) ; un pays à règles propres a ses dates à lui (la partie
# Rodez et la partie simulée ont les mêmes 70 règles). v11 : en chiffres (jour, mois de début, jour, mois de fin ; une
# 2e période qui revient 3 saisons ou plus après la 1re ; [] : aucune arrivée en 5 saisons), écrite dans chaque langue
# par ecrire_plages() avec LANGUES_PAGE. Écrite par FM27-mod/outils/plages-pour-skin.mjs (chantier-pays/
# plages-skin-FM27.json) : ne pas la retoucher à la main.
PLAGES_RELEVEES = {   # identifiant du pays : (hommes, femmes)
    5: ([(8, 4, 6, 5)], [(8, 4, 13, 4)]),   # Algérie
    6: ([(8, 4, 6, 5)], [(8, 4, 10, 4)]),   # Angola
    7: ([(9, 4, 26, 4)], [(8, 4, 8, 4)]),   # Bénin
    8: ([(8, 4, 6, 5)], [(8, 4, 18, 4)]),   # Botswana
    9: ([(8, 4, 6, 5)], [(9, 4, 12, 4)]),   # Burkina Faso
    10: ([(8, 4, 1, 5)], [(8, 4, 11, 4)]),   # Burundi
    11: ([(8, 4, 6, 5)], [(8, 4, 17, 4)]),   # Cameroun
    12: ([(8, 4, 6, 5)], [(8, 4, 15, 4)]),   # Cap-Vert
    13: ([(8, 4, 19, 4)], [(9, 4, 14, 4)]),   # République centrafricaine
    14: ([(8, 4, 15, 4)], [(8, 4, 9, 4)]),   # Tchad
    15: ([(8, 4, 14, 4)], [(8, 4, 12, 4)]),   # Djibouti
    16: ([(29, 3, 26, 4)], [(8, 4, 17, 4)]),   # Égypte
    17: ([(8, 4, 26, 4)], [(8, 4, 13, 4)]),   # Guinée Équatoriale
    18: ([(8, 4, 6, 5)], [(8, 4, 12, 4)]),   # Éthiopie
    19: ([(8, 4, 30, 4)], [(8, 4, 11, 4)]),   # Gabon
    20: ([(8, 4, 6, 5)], [(8, 4, 10, 4)]),   # Gambie
    21: ([(8, 4, 6, 5)], [(8, 4, 28, 4)]),   # Ghana
    22: ([(8, 4, 2, 5)], [(9, 4, 10, 4)]),   # Guinée
    23: ([(22, 9, 20, 10)], [(22, 9, 24, 9)]),   # Guinée-Bissau
    24: ([(8, 4, 6, 5)], [(8, 4, 11, 4)]),   # Côte d'Ivoire
    25: ([(8, 4, 6, 5)], [(8, 4, 26, 4)]),   # Kenya
    26: ([(8, 4, 25, 4)], [(8, 4, 13, 4)]),   # Lesotho
    27: ([(8, 4, 30, 4)], [(8, 4, 13, 4)]),   # Liberia
    28: ([(8, 4, 7, 5)], []),   # Libye
    29: ([(21, 9, 3, 10)], [(21, 9, 26, 9)]),   # Madagascar
    30: ([(21, 9, 12, 10)], [(21, 9, 23, 9)]),   # Malawi
    31: ([(21, 9, 19, 10)], [(21, 9, 25, 9)]),   # Mali
    32: ([(8, 4, 2, 5)], [(8, 4, 11, 4)]),   # Mauritanie
    33: ([(8, 4, 30, 4)], [(9, 4, 15, 4)]),   # Île Maurice
    34: ([(8, 4, 6, 5)], [(8, 4, 30, 4)]),   # Maroc
    35: ([(21, 9, 19, 10)], [(21, 9, 24, 9)]),   # Mozambique
    36: ([(8, 4, 30, 4)], [(8, 4, 17, 4)]),   # Namibie
    37: ([(8, 4, 23, 4)], [(8, 4, 15, 4)]),   # Niger
    38: ([(8, 4, 6, 5)], [(8, 4, 17, 4)]),   # Nigeria
    39: ([(8, 4, 1, 5)], [(8, 4, 10, 4)]),   # Rwanda
    40: ([(21, 9, 13, 10)], [(21, 9, 26, 9)]),   # São Tomé-et-Príncipe
    41: ([(8, 4, 6, 5)], [(9, 4, 11, 4)]),   # Sénégal
    42: ([(8, 4, 27, 4)], [(8, 4, 13, 4)]),   # Seychelles
    43: ([(8, 4, 18, 4)], [(8, 4, 13, 4)]),   # Sierra Leone
    44: ([(21, 9, 7, 10)], []),   # Somalie
    45: ([(3, 4, 1, 5)], [(8, 4, 24, 4)]),   # Afrique du Sud
    46: ([(8, 4, 2, 5)], []),   # Soudan
    47: ([(8, 4, 3, 5)], [(9, 4, 9, 4)]),   # Eswatini
    48: ([(8, 4, 6, 5)], [(8, 4, 15, 4)]),   # Tanzanie
    49: ([(21, 9, 6, 10)], [(21, 9, 21, 9)]),   # Congo
    50: ([(8, 4, 5, 5)], [(9, 4, 13, 4)]),   # Togo
    51: ([(8, 4, 6, 5)], [(8, 4, 17, 4)]),   # Tunisie
    52: ([(8, 4, 6, 5)], [(8, 4, 18, 4)]),   # Ouganda
    53: ([(8, 4, 6, 5)], [(9, 4, 10, 4)]),   # République démocratique du Congo
    54: ([(8, 4, 6, 5)], [(8, 4, 29, 4)]),   # Zambie
    55: ([(21, 9, 19, 10)], [(21, 9, 23, 9)]),   # Zimbabwe
    106: ([(22, 9, 2, 10)], []),   # Afghanistan
    107: ([(8, 4, 1, 5)], [(8, 4, 14, 4)]),   # Bahreïn
    108: ([(21, 9, 20, 10)], [(21, 9, 25, 9)]),   # Bangladesh
    109: ([(8, 4, 29, 4)], []),   # Sultanat de Brunei
    110: ([(5, 10, 2, 11)], [(21, 9, 3, 11)]),   # Chine
    111: ([(20, 4, 18, 5)], [(8, 4, 6, 5)]),   # Hong Kong (RP de Chine)
    112: ([(3, 4, 1, 5)], [(9, 4, 16, 4)]),   # Inde
    113: ([(23, 7, 23, 7)], [(8, 4, 23, 4)]),   # Indonésie
    114: ([(8, 4, 6, 5)], [(8, 4, 18, 4)]),   # Iran
    115: ([(8, 4, 6, 5)], [(8, 4, 10, 4)]),   # Irak
    116: ([(13, 3, 10, 4)], [(20, 3, 17, 4)]),   # Japon
    117: ([(8, 4, 6, 5)], [(8, 4, 16, 4)]),   # Jordanie
    118: ([(21, 9, 10, 10)], [(21, 9, 26, 9)]),   # Cambodge
    119: ([(21, 9, 19, 10)], [(21, 9, 11, 10)]),   # Kazakhstan
    120: ([(8, 4, 26, 4)], []),   # Koweït
    121: ([(21, 9, 19, 10)], [(21, 9, 30, 9)]),   # Kirghizistan
    122: ([(8, 4, 6, 5)], [(9, 4, 13, 4)]),   # Laos
    123: ([(8, 4, 6, 5)], [(8, 4, 20, 4)]),   # Liban
    124: ([(21, 9, 19, 10)], [(21, 9, 26, 9)]),   # Macao (RP de Chine)
    125: ([(20, 3, 17, 4)], [(8, 4, 29, 4)]),   # Malaisie
    126: ([(21, 9, 24, 9)], [(22, 9, 29, 9)]),   # Maldives
    127: ([(21, 9, 19, 10)], [(21, 9, 23, 9)]),   # Birmanie
    128: ([(22, 9, 17, 10)], [(21, 9, 26, 9)]),   # Népal
    129: ([(21, 9, 6, 10)], [(21, 9, 27, 9)]),   # Corée du Nord
    130: ([(8, 4, 6, 5)], []),   # Oman
    131: ([(8, 4, 23, 4)], [(9, 4, 15, 4)]),   # Pakistan
    132: ([(8, 4, 1, 5)], []),   # Qatar
    133: ([(9, 3, 6, 4)], [(8, 4, 2, 5)]),   # Arabie saoudite
    134: ([(13, 4, 11, 5)], [(8, 4, 29, 4)]),   # Singapour
    135: ([(19, 9, 17, 10)], [(21, 9, 28, 9)]),   # Corée du Sud
    136: ([(22, 9, 29, 9)], [(21, 9, 24, 9)]),   # Sri Lanka
    137: ([(8, 4, 6, 5)], [(8, 4, 15, 4)]),   # Syrie
    138: ([(21, 9, 19, 10)], [(21, 9, 22, 9)]),   # Taipei chinois (RP de Chine)
    139: ([(21, 9, 17, 10)], [(21, 9, 29, 9)]),   # Tadjikistan
    140: ([(8, 4, 6, 5)], [(8, 4, 16, 4)]),   # Thaïlande
    141: ([(22, 9, 5, 10)], [(21, 9, 23, 9)]),   # Philippines
    142: ([(21, 9, 30, 9)], [(21, 9, 1, 10)]),   # Turkménistan
    143: ([(4, 3, 1, 4)], [(8, 4, 20, 4)]),   # Émirats arabes unis
    144: ([(21, 9, 19, 10)], [(21, 9, 7, 10)]),   # Ouzbékistan
    145: ([(21, 9, 19, 10)], [(21, 9, 24, 9)]),   # Vietnam
    146: ([(8, 4, 27, 4)], [(8, 4, 11, 4)]),   # Yémen
    359: ([(8, 4, 14, 4)], [(8, 4, 10, 4)]),   # Antigua-et-Barbuda
    360: ([(8, 4, 18, 4)], [(8, 4, 15, 4)]),   # Aruba
    361: ([(22, 9, 29, 9)], [(22, 9, 23, 9)]),   # Barbade
    362: ([(8, 4, 14, 4)], [(8, 4, 14, 4)]),   # Bélize
    363: ([(8, 4, 20, 4)], [(9, 4, 13, 4)]),   # Bermudes
    364: ([(21, 9, 19, 10)], [(21, 9, 19, 10)]),   # Canada
    365: ([(9, 4, 15, 4)], [(8, 4, 15, 4)]),   # Îles Caïmans
    366: ([(8, 4, 6, 5)], [(8, 4, 18, 4)]),   # Costa Rica
    367: ([(21, 9, 26, 9)], [(22, 9, 25, 9)]),   # Cuba
    368: ([(8, 4, 16, 4)], [(8, 4, 14, 4)]),   # Dominique
    370: ([(8, 4, 6, 5)], [(8, 4, 23, 4)]),   # Salvador
    371: ([(21, 9, 28, 9)], [(21, 9, 24, 9)]),   # Grenade
    373: ([(8, 4, 6, 5)], [(9, 4, 20, 4)]),   # Guatemala
    374: ([(21, 9, 1, 10)], [(21, 9, 23, 9)]),   # Guyana
    375: ([(21, 9, 9, 10)], [(22, 9, 25, 9)]),   # Haïti
    376: ([(8, 4, 6, 5)], [(9, 4, 17, 4)]),   # Honduras
    377: ([(8, 4, 6, 5)], [(8, 4, 22, 4)]),   # Jamaïque
    379: ([(3, 3, 31, 3)], [(8, 4, 25, 4)]),   # Mexique
    380: ([(8, 4, 17, 4)], [(9, 4, 14, 4)]),   # Curaçao
    381: ([(8, 4, 6, 5)], [(9, 4, 15, 4)]),   # Nicaragua
    382: ([(8, 4, 4, 5)], [(8, 4, 23, 4)]),   # Panama
    383: ([(8, 4, 22, 4)], [(8, 4, 13, 4)]),   # Porto Rico
    384: ([(21, 9, 5, 10)], [(22, 9, 22, 9)]),   # Sainte-Lucie
    385: ([(8, 4, 22, 4)], [(8, 4, 12, 4)]),   # Saint-Kitts et Névis
    386: ([(21, 9, 2, 10)], [(22, 9, 22, 9)]),   # Saint-Vincent
    387: ([], [(9, 4, 13, 4)]),   # Suriname
    388: ([(8, 4, 13, 4)], [(8, 4, 14, 4)]),   # Bahamas
    389: ([(8, 4, 6, 5)], [(9, 4, 12, 4)]),   # Trinité-et-Tobago
    390: ([(21, 9, 22, 9)], [(21, 9, 24, 9)]),   # États-Unis
    752: ([(8, 4, 6, 5)], [(8, 4, 20, 4)]),   # Albanie
    753: ([(8, 4, 25, 4)], []),   # Andorre
    754: ([(8, 4, 6, 5)], [(8, 4, 18, 4)]),   # Arménie
    755: ([(8, 3, 5, 4)], [(8, 4, 6, 5)]),   # Autriche
    756: ([(8, 4, 6, 5)], [(8, 4, 21, 4)]),   # Azerbaïdjan
    757: ([(19, 3, 16, 4)], [(8, 4, 6, 5)]),   # Belgique
    758: ([(5, 10, 2, 11)], [(21, 9, 6, 10)]),   # Biélorussie
    759: ([(8, 4, 6, 5)], [(8, 4, 16, 4)]),   # Bosnie-Herzégovine
    760: ([(7, 3, 4, 4)], [(8, 4, 11, 4)]),   # Bulgarie
    761: ([(9, 3, 6, 4)], [(8, 4, 26, 4)]),   # Croatie
    762: ([(8, 4, 6, 5)], [(8, 4, 17, 4)]),   # Chypre
    763: ([(19, 3, 16, 4)], [(8, 4, 27, 4)]),   # République tchèque
    764: ([(19, 3, 16, 4)], [(19, 3, 8, 4)]),   # Danemark
    765: ([(14, 3, 11, 4)], [(14, 3, 11, 4)]),   # Angleterre
    766: ([(21, 9, 19, 10)], [(21, 9, 4, 10)]),   # Estonie
    767: ([(21, 9, 8, 10)], [(21, 9, 28, 9)]),   # Îles Féroé
    768: ([(13, 9, 11, 10)], [(21, 9, 19, 10)]),   # Finlande
    769: ([(9, 3, 6, 4), (20, 6, 20, 6)], [(9, 3, 6, 4)]),   # France
    770: ([(21, 9, 19, 10)], [(21, 9, 16, 10)]),   # Géorgie
    771: ([(9, 3, 6, 4)], [(9, 3, 6, 4)]),   # Allemagne
    772: ([(9, 3, 7, 4)], [(8, 4, 6, 5)]),   # Grèce
    773: ([(9, 3, 6, 4)], [(8, 4, 22, 4)]),   # Hongrie
    774: ([(13, 9, 11, 10)], [(21, 9, 15, 10)]),   # Islande
    775: ([(9, 3, 7, 4)], [(8, 4, 6, 5)]),   # Israël
    776: ([(18, 3, 15, 4)], [(19, 3, 16, 4)]),   # Italie
    777: ([(21, 9, 19, 10)], [(21, 9, 2, 10)]),   # Lettonie
    778: ([], []),   # Liechtenstein
    779: ([(21, 9, 20, 10)], [(21, 9, 3, 10)]),   # Lituanie
    780: ([(8, 4, 6, 5)], [(8, 4, 4, 5)]),   # Luxembourg
    781: ([(8, 4, 6, 5)], [(8, 4, 28, 4)]),   # Macédoine du Nord
    782: ([(8, 4, 6, 5)], [(8, 4, 16, 4)]),   # Malte
    783: ([(21, 9, 19, 10)], [(21, 9, 22, 9)]),   # Moldavie
    784: ([(26, 3, 23, 4)], [(8, 4, 24, 4)]),   # Pays-Bas
    785: ([(14, 3, 11, 4)], [(8, 4, 27, 4)]),   # Irlande du Nord
    786: ([(6, 2, 5, 3)], [(21, 9, 19, 10), (7, 2, 8, 2)]),   # Norvège
    787: ([(17, 3, 14, 4)], [(8, 4, 7, 5)]),   # Pologne
    788: ([(19, 3, 16, 4)], [(8, 4, 6, 5)]),   # Portugal
    789: ([(22, 9, 20, 10)], [(21, 9, 4, 10)]),   # Irlande
    790: ([(19, 3, 16, 4)], [(8, 4, 13, 4)]),   # Roumanie
    791: ([(3, 3, 31, 3)], [(8, 4, 20, 4)]),   # Russie
    792: ([(30, 3, 23, 4)], []),   # Saint-Marin
    793: ([(14, 3, 11, 4)], [(8, 4, 6, 5)]),   # Écosse
    794: ([(18, 3, 15, 4)], [(8, 4, 24, 4)]),   # Slovaquie
    795: ([(20, 3, 17, 4)], [(8, 4, 23, 4)]),   # Slovénie
    796: ([(29, 3, 26, 4)], [(29, 3, 26, 4)]),   # Espagne
    797: ([(14, 9, 12, 10)], [(21, 9, 19, 10)]),   # Suède
    798: ([(19, 3, 17, 4)], [(8, 4, 6, 5)]),   # Suisse
    799: ([(9, 3, 6, 4)], [(8, 4, 7, 5)]),   # Turquie
    800: ([(16, 3, 13, 4)], [(8, 4, 22, 4)]),   # Ukraine
    801: ([(14, 3, 11, 4)], [(14, 3, 11, 4)]),   # Pays de Galles
    802: ([(5, 3, 2, 4)], [(8, 4, 24, 4)]),   # Serbie
    1435: ([(21, 9, 4, 10)], [(14, 1, 20, 1), (21, 9, 21, 9)]),   # Australie
    1436: ([(21, 9, 27, 9)], [(21, 9, 23, 9)]),   # Îles Cook
    1437: ([(21, 9, 11, 10)], [(21, 9, 25, 9)]),   # Îles Fidji
    1438: ([(22, 9, 5, 10)], [(22, 9, 1, 10)]),   # Nouvelle-Zélande
    1439: ([(21, 9, 4, 10)], [(22, 9, 25, 9)]),   # Papouasie-Nouvelle-Guinée
    1440: ([(21, 9, 7, 10)], [(21, 9, 22, 9)]),   # Îles Salomon
    1441: ([(8, 4, 6, 5)], [(9, 4, 9, 4)]),   # Tahiti
    1442: ([(21, 9, 1, 10)], [(21, 9, 28, 9)]),   # Îles Tonga
    1443: ([(8, 4, 2, 5)], [(8, 4, 13, 4)]),   # Vanuatu
    1444: ([(8, 4, 19, 4)], [(8, 4, 11, 4)]),   # Samoa
    1649: ([(27, 4, 25, 5)], [(21, 9, 19, 10), (1, 5, 4, 5)]),   # Argentine
    1650: ([(21, 9, 20, 10)], [(21, 9, 9, 10)]),   # Bolivie
    1651: ([(14, 1, 20, 1)], [(21, 9, 19, 10), (14, 1, 20, 1)]),   # Brésil
    1652: ([(21, 9, 19, 10)], [(21, 9, 19, 10)]),   # Chili
    1653: ([(17, 1, 14, 2)], [(21, 9, 19, 10)]),   # Colombie
    1654: ([(21, 9, 19, 10)], [(21, 9, 18, 10)]),   # Équateur
    1655: ([(21, 9, 19, 10)], [(21, 9, 4, 10)]),   # Paraguay
    1656: ([(21, 9, 19, 10)], [(21, 9, 8, 10)]),   # Pérou
    1657: ([(18, 1, 15, 2)], [(21, 9, 12, 10)]),   # Uruguay
    1658: ([(21, 9, 19, 10)], [(21, 9, 18, 10)]),   # Venezuela
    1662: ([(8, 4, 6, 5)], [(8, 4, 10, 4)]),   # Palestine
    129504: ([(21, 9, 27, 9)], [(21, 9, 21, 9)]),   # Samoa américaines
    129505: ([(21, 9, 8, 10)], [(22, 9, 22, 9)]),   # Mongolie
    129508: ([(8, 4, 10, 4)], [(9, 4, 12, 4)]),   # Guam
    129511: ([(22, 9, 28, 9)], [(21, 9, 22, 9)]),   # Érythrée
    129514: ([(8, 4, 17, 4)], [(9, 4, 13, 4)]),   # Anguilla
    129517: ([(21, 9, 29, 9)], [(22, 9, 25, 9)]),   # Îles Vierges
    129520: ([(8, 4, 14, 4)], []),   # Montserrat
    129523: ([(8, 4, 13, 4)], [(8, 4, 14, 4)]),   # Îles Vierges US
    129526: ([(22, 9, 25, 9)], [(21, 9, 25, 9)]),   # Îles Turks-et-Caïcos
    129532: ([(21, 9, 19, 10)], [(21, 9, 25, 9)]),   # Nouvelle-Calédonie
    131012: ([(21, 9, 1, 10)], [(21, 9, 22, 9)]),   # Bhoutan
    142527: ([(21, 9, 11, 10)], [(22, 9, 27, 9)]),   # République dominicaine
    209002: ([], []),   # Kiribati
    214394: ([(9, 3, 20, 3)], [(8, 4, 12, 4)]),   # Gibraltar
    214395: ([(22, 9, 30, 9)], [(21, 9, 25, 9)]),   # Bonaire
    217945: ([(8, 4, 6, 5)], [(8, 4, 19, 4)]),   # Kosovo
    917496: ([(21, 9, 20, 10)], [(22, 9, 25, 9)]),   # Guyane
    917498: ([(8, 4, 9, 4)], [(8, 4, 18, 4)]),   # Guadeloupe
    917502: ([(8, 4, 6, 5)], [(9, 4, 17, 4)]),   # Martinique
    917506: ([(8, 4, 15, 4)], []),   # Saint-Martin (PB)
    917508: ([(8, 4, 16, 4)], []),   # Saint-Martin
    917510: ([(21, 9, 29, 9)], []),   # La Réunion
    918740: ([], []),   # Mayotte
    918745: ([], []),   # Îles Wallis-et-Futuna
    918748: ([], []),   # Saint-Pierre-et-Miquelon
    919586: ([(22, 9, 9, 10)], [(21, 9, 22, 9)]),   # Comores
    5626837: ([(21, 9, 9, 10)], [(21, 9, 26, 9)]),   # Timor Oriental
    13100103: ([], []),   # Zanzibar
    13113220: ([(9, 4, 30, 4)], [(9, 4, 11, 4)]),   # Soudan du Sud
    15064643: ([(9, 4, 9, 4)], []),   # Micronésie
    23008660: ([(21, 9, 29, 9)], [(21, 9, 24, 9)]),   # Îles Mariannes du Nord
    23088616: ([(21, 9, 22, 9)], []),   # Tuvalu
    62002127: ([(8, 4, 6, 5)], [(8, 4, 20, 4)]),   # Monténégro
    82082526: ([(9, 4, 10, 4)], []),   # Saint-Barthélemy
}

# v11 : pour chaque valeur du réglage de langue de FM (languagesetting.PropertyValue), de quoi écrire une date comme FM et
# les deux titres. Recopié du fichier de langues du jeu (languages.fmf) par identifiant, jamais retapé (même outil) :
# mois abrégés 0x1003d02c-37 ; ordre du jour et du mois 0x1003d01a ({j} le jour, {m} le mois ; « -nth » chez FM :
# le jour prend son ordinal) ; ordinaux 0x1003d045 (le 1) puis 0x1003d046-49 (1st, 2nd, 3rd, 4th) ; titres « Youth
# Rating » 0x10050372 et « Youth Intake » 0x1004d566 de FM ; en français, ceux de Kinito. « spanish (latam) » :
# l'espagnol (la table du jeu est partielle) ; « portuguese (bra) » : le portugais du jeu (une seule table).
LANGUES_PAGE = {
    "arabic": dict(   # اَلْعَرَبِيَّةُ
        mois=('يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'),
        motif="{j} {m}", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="تقييم فرق الشباب", arrivee="قبول الناشئين"),
    "chinese": dict(   # 简体中文
        mois=('1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'),
        motif="{m}{j}日", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="青​训评​分", arrivee="青​年队​转入"),
    "danish": dict(   # Dansk
        mois=('Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Juni', 'Juli', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'),
        motif="{j} {m}", ordinaux=('{n}.', '{n}.', '{n}.', '{n}.', '{n}.'),
        note="Ungdomskarakter", arrivee="Ungdomsspillere tilført"),
    "dutch": dict(   # Nederlands
        mois=('jan', 'feb', 'maa', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'),
        motif="{j} {m}", ordinaux=('{n}e', '{n}e', '{n}e', '{n}e', '{n}e'),
        note="Jeugdwaardering", arrivee="Ingestroomde jeugdspelers"),
    "english": dict(   # English
        mois=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        motif="{j} {m}", ordinaux=('{n}st', '{n}st', '{n}nd', '{n}rd', '{n}th'),
        note="Youth Rating", arrivee="Youth Intake"),
    "english (us)": dict(   # English (US)
        mois=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'),
        motif="{j} {m}", ordinaux=('{n}st', '{n}st', '{n}nd', '{n}rd', '{n}th'),
        note="Youth Rating", arrivee="Youth Intake"),
    "french": dict(   # Français
        mois=('jan', 'fév', 'mar', 'avr', 'mai', 'juin', 'jui', 'aoû', 'sep', 'oct', 'nov', 'déc'),
        motif="{j} {m}", ordinaux=None,
        note="Note de formation des jeunes", arrivee="Arrivée des jeunes"),
    "german": dict(   # Deutsch
        mois=('Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'),
        motif="{j} {m}", ordinaux=('{n}.', '{n}.', '{n}.', '{n}.', '{n}.'),
        note="Jugendbewertung", arrivee="Aufnahme von Jugendspielern"),
    "greek": dict(   # Ελληνικά
        mois=('Ιαν', 'Φεβ', 'Μαρ', 'Απρ', 'Μαι', 'Ιουν', 'Ιουλ', 'Αυγ', 'Σεπ', 'Οκτ', 'Νοε', 'Δεκ'),
        motif="{j}η {m}", ordinaux=None,
        note="Αξιολόγηση Ακαδημιών", arrivee="Εισροή Παικτών Ομάδας Νέων"),
    "indonesian": dict(   # Bahasa Indonesia
        mois=('Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'),
        motif="{j} {m}", ordinaux=None,
        note="Rating Pemuda", arrivee="Penerimaan Pemain Muda"),
    "italian": dict(   # Italiano
        mois=('Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'),
        motif="{j} {m}", ordinaux=None,
        note="Valutazione giovani", arrivee="Giovani del vivaio"),
    "japanese": dict(   # 日本語
        mois=('1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'),
        motif="{m}{j}日", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="ユース​評価点", arrivee="ユース​加入"),
    "korean": dict(   # 한국어
        mois=('1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'),
        motif="{m} {j}일", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="유소년 평점", arrivee="유소년 입학"),
    "norwegian": dict(   # Norsk
        mois=('Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des'),
        motif="{j} {m}", ordinaux=('{n}.', '{n}.', '{n}.', '{n}.', '{n}.'),
        note="Ungdomsrating", arrivee="Inntak av unge spillere"),
    "polish": dict(   # Polski
        mois=('sty.', 'lut.', 'mar.', 'kwi.', 'maj', 'cze.', 'lip.', 'sie.', 'wrz.', 'paź.', 'lis.', 'gru.'),
        motif="{j} {m}", ordinaux=None,
        note="Poziom juniorów", arrivee="Nabór juniorów"),
    "portuguese": dict(   # Português
        mois=('Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'),
        motif="{j} {m}", ordinaux=None,
        note="Classificação Jovem", arrivee="Contratação de Jovens"),
    "portuguese (bra)": dict(   # Português
        mois=('Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'),
        motif="{j} {m}", ordinaux=None,
        note="Classificação Jovem", arrivee="Contratação de Jovens"),
    "russian": dict(   # Русский
        mois=('Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'),
        motif="{j} {m}", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="Молодежный рейтинг", arrivee="Из молодежной команды"),
    "spanish": dict(   # Español
        mois=('ene.', 'feb.', 'mar.', 'abr.', 'may.', 'jun.', 'jul.', 'ago.', 'sep.', 'oct.', 'nov.', 'dic.'),
        motif="{j} {m}", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="Valoración juvenil", arrivee="Juveniles admitidos"),
    "spanish (latam)": dict(   # Español
        mois=('ene.', 'feb.', 'mar.', 'abr.', 'may.', 'jun.', 'jul.', 'ago.', 'sep.', 'oct.', 'nov.', 'dic.'),
        motif="{j} {m}", ordinaux=('{n}', '{n}', '{n}', '{n}', '{n}'),
        note="Valoración juvenil", arrivee="Juveniles admitidos"),
    "swedish": dict(   # Svenska
        mois=('jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'),
        motif="{j} {m}", ordinaux=('{n}:a', '{n}:a', '{n}:a', '{n}:e', '{n}:e'),
        note="Ungdomsranking", arrivee="Ungdomsförvärv"),
    "turkish": dict(   # Türkçe
        mois=('Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'),
        motif="{j} {m}", ordinaux=('{n}.', '{n}.', '{n}.', '{n}.', '{n}.'),
        note="Altyapı Derecesi", arrivee="Altyapıya Oyuncu Alımı"),
}

# les titres de Kinito en français (v8) : les mêmes que ceux de la table
assert (LANGUES_PAGE["french"]["note"], LANGUES_PAGE["french"]["arrivee"]) == (TITRE_NOTE, TITRE_ARRIVEE)

def ecrire_date(lg, j, mo):
    """v11 : une date (jour, mois) écrite comme FM dans la langue lg (LANGUES_PAGE)"""
    l = LANGUES_PAGE[lg]
    n = str(j)
    if l["ordinaux"]:
        un, o1, o2, o3, o4 = l["ordinaux"]
        o = un if j == 1 else o1 if j % 10 == 1 and j % 100 != 11 else o2 if j % 10 == 2 and j % 100 != 12 \
            else o3 if j % 10 == 3 and j % 100 != 13 else o4
        n = o.replace("{n}", str(j))
    return l["motif"].replace("{j}", n).replace("{m}", l["mois"][mo - 1])


def ecrire_plages(lg, plages):
    """v11 : les plages d'un pays (PLAGES_RELEVEES, un sexe) dans la langue lg : « 9 mar - 6 avr, 20 juin » ; « — »"""
    if not plages:
        return "—"
    return ", ".join(ecrire_date(lg, j1, m1) if (j1, m1) == (j2, m2) else
                     f"{ecrire_date(lg, j1, m1)} - {ecrire_date(lg, j2, m2)}" for j1, m1, j2, m2 in plages)


VERSION = 11   # v1 (07/11/2026) : première version, construite par Claude seul (Kinito absent) ; vue en jeu le même
#               soir : FM SE FERMAIT à l'ouverture d'une page Pays (2849202c recevait la liste au lieu d'un nombre).
#               v2 : le nombre de clubs d'abord (2fe07f5c), puis nombre - 1 (2849202c), la chaîne exacte de FM ; vue en
#               jeu le 07/11 au soir (France bonne, Bhoutan : note seule).
#               v3 : un pays NON jouable (règles non valides) montre « dans N jours » (choix de Kinito) : son
#               IntakeDate est vide mais DaysUntilYouthIntake répond (sonde 0.23.6, Bhoutan 226 j = 28/03/2028).
#               v4 (08/11/2026) : la note SUR 200 au départ (demande de Kinito : « la note sur 200, pas sur 20 ») au lieu
#               du palier : un commutateur de FM par pays et par sexe (table NOTES_DEPART, sonde 0.24.1).
#               Vue en jeu le 08/11 (« tout marche ») : France, Brésil, Algérie, Bhoutan, Tanzanie, Allemagne ; mais
#               l'Allemagne écrivait « 10 mar - date#2 » (partie FC Villefranche) : son dernier club n'a pas de date.
#               v5 (08/11/2026) : la fin = le dernier club QUI A une date (6 essayés), sinon « ? » ; et la page d'une
#               SÉLECTION (demande de Kinito : « à côté du classement mondial, la note femme pour les femmes, la note
#               homme pour les hommes ; la date d'arrivée aussi »).
#               v6 (09/11/2026) : un pays SANS règles montre sa plage TROUVÉE (PLAGES_TROUVEES, sondes 0.27.3 et 0.27.4)
#               au lieu de « dans N jours » (pas une date d'arrivée) ; la page d'un pays montre hommes ET femmes
#               (demande de Kinito : « ajoute toutes les dates qu'on a trouvées à tous les pays »). Installée par
#               Kinito le 09/11 à 19 h 54.
#               v7 (09/11/2026) : la table seule corrigée : un pays SANS règles montre TOUJOURS sa date relevée. La v6
#               montrait la plage prêtée (8 avr - 6 mai) à Saint-Marin, qui n'a de règles dans aucune des deux parties
#               relevées mais dont les jeunes arrivent du 30/03 au 23/04 : c'était faux. Seul Saint-Marin change.
#               Installée par Kinito le 10/11 à 0 h 15, vue en jeu (Saint-Marin, Algérie, France : justes).
#               v8 (10/11/2026) : les deux titres de Kinito, en texte fixe : « Note de formation des jeunes » et
#               « Arrivée des jeunes » (plus « Niveau général de la formation », ni l'année, ni « en »). Installée
#               et validée par Kinito le 10/11.
#               v9 (12/11/2026) : la Géorgie ne lit aucun club (FM se fermait à chaque arrivée sur sa page) : sa plage
#               trouvée en texte fixe, derrière un commutateur « identifiant != 770 » (GEORGIE). Installée le
#               12/11 : la Géorgie passe, mais FM se ferme sur Gibraltar (à règles propres).
#               v10 (12/11/2026) : plus AUCUNE lecture de club : la plage trouvée de chaque pays écrite en dur (Kinito :
#               « afficher les dates qu'on a trouvées en dur pour tous les pays ») ; plus de date en direct ni d'année.
#               Installée et validée par Kinito le 12/11 (43 pages Pays sans plantage).
#               v11 (13/11/2026) : la page dans la langue du jeu (Kinito : « Oui, traduis ») : titres de FM (« Youth
#               Rating », « Youth Intake » ; en français ceux de Kinito) et dates écrites comme FM dans chaque langue.
PREFIXE = "UIPickerKinito-pays-formation"
NOM = f"{PREFIXE}-v{VERSION}"
NOM_SEL = f"{PREFIXE}-selection-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_pays_formation.actif")

for _k, _v in {"margin-right": (131092, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)   # StylePropertyId d'Unity 6


# ---------- outils ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def chaine(s):
    b = s.encode("utf-8")
    return bytes([1]) + bytes(_enc_varint(len(b))) + b


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    for n in types_ref_manquants(obj, tt):
        print(f"[Kinito] Pays : type {n} déclaré dans le bundle (recopié)")
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def liaison_de(modele, guid8):
    """v4 : la liaison (Binding) d'un commutateur de FM d'un modèle d'ORIGINE, menée par la fonction guid8, recopiée ;
    on exige sa forme : opérateur de comparaison, entier, chemin (BindIntComparisonToSwitch)"""
    o = ouvrir(modele, depart_original=True)
    if o is None:
        return None
    t = o[3]
    for r in t.walk():
        if r not in t.refs or not typ(t, r).endswith("BindableSwitchElement"):
            continue
        b = t.sd(r).get("Binding")
        if not isinstance(b, dict):
            continue
        f = b.get("m_visualFunction") or {}
        if b.get("m_kind") != 2 or not (f.get("m_target") or {}).get("m_guid", "").startswith(guid8):
            continue
        try:
            a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        except Exception:
            continue
        if (len(a) == 3 and bytes(a[0][0]).endswith(b"ComparisonOperator]") and bytes(a[1][0]).endswith(b"Int32VisualArg")
                and bytes(a[2][0]).endswith(b"[SI.Bindable.BindingPath]")):
            return copy.deepcopy(b)
    return None


class Sources:
    """tout ce qui est lu ailleurs (originaux) ; manque_pays() / manque_selection() : ce qui n'a pas été trouvé"""

    def __init__(self):
        # v4 : un commutateur du bundle de l'en-tête, et la liaison de FM « nombre comparé à un entier » d'un autre écran
        o = ouvrir(SOURCE_COMMUTATEUR, depart_original=True)
        self.tc = o[3] if o is not None else None
        self.commut = next((r for r in self.tc.walk() if r in self.tc.refs
                            and typ(self.tc, r).endswith("BindableSwitchElement")), None) if self.tc else None
        self.comparaison = liaison_de(*SOURCE_COMPARAISON)
        # v5, page d'une sélection (bundle gameworld) : un commutateur de CE bundle
        o = ouvrir(SOURCE_COMMUTATEUR_SEL, depart_original=True)
        self.tc_sel = o[3] if o is not None else None
        self.commut_sel = next((r for r in self.tc_sel.walk() if r in self.tc_sel.refs
                                and commutateur_du_sexe(self.tc_sel, r)), None) if self.tc_sel else None
        # v11 : le réglage de langue du jeu (recette 19) : le conteneur de FM et son interrupteur
        o = ouvrir(SOURCE_LANGUE, depart_original=True)
        self.tg = o[3] if o is not None else None
        self.langue_env = self.langue_sw = None
        if self.tg is not None:
            tg = self.tg
            self.langue_env = next((r for r in tg.walk() if typ(tg, r) == "ComponentElement" and any(
                "languagesetting" in json.dumps((tg.refs.get(c["rid"]) or {}).get("data") or {})
                for c in tg.sd(r).get("m_components") or [])), None)
            self.langue_sw = next((r for r in tg.walk() if typ(tg, r) == "BindableSwitchElement" and (
                ((tg.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get("m_target") or {}).get(
                "m_guid") == FONCTION_LANGUE), None)
        # v5 : le texte « modèle + données » de FM (valeur de Population), pour les valeurs de la page d'une sélection
        self.tb_format = None
        o = ouvrir(MODELE, depart_original=True)
        if o is not None:
            p = pieces(o[3])
            if p is not None:
                valeur = [k for k in o[3].children(p["population"]) if typ(o[3], k).endswith("SIText")][1]
                self.tb_format = copy.deepcopy(o[3].sd(valeur)["TextBinding"])

    def _commun(self):
        return (("comparaison d'entiers", self.comparaison), ("conteneur de langue de FM", self.langue_env),
                ("interrupteur de langue de FM", self.langue_sw))

    def manque_pays(self):
        return [n for n, v in self._commun() + (("commutateur", self.commut),) if v is None]

    def manque_selection(self):
        return [n for n, v in self._commun() + (("commutateur hommes / femmes de FM", self.commut_sel),
                                                 ("texte formaté de FM", self.tb_format)) if v is None]


def commutateur_du_sexe(t, r):
    """v5 : le commutateur de FM de NewsNationalTeamSiteHeader : « teamcontainer.Gender == 0 » (BindIntComparisonToSwitch)
    montre son enfant 1, « mentext » : c'est ce qui prouve que 0 = hommes et que l'enfant 1 est celui du « vrai »"""
    if not typ(t, r).endswith("BindableSwitchElement"):
        return False
    b = t.sd(r).get("Binding")
    if not isinstance(b, dict) or b.get("m_kind") != 2:
        return False
    f = b.get("m_visualFunction") or {}
    if not (f.get("m_target") or {}).get("m_guid", "").startswith(SOURCE_COMPARAISON[1]):
        return False
    try:
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    except Exception:
        return False
    enfants = [t.name(k) for k in t.children(r)]
    return (len(a) == 3 and struct.unpack_from("<i", bytes(a[0][1]))[0] == EGAL
            and struct.unpack_from("<i", bytes(a[1][1]))[0] == 0 and bytes(a[2][1]).lower().endswith(b".gender")
            and enfants == ["womentext", "mentext"])


def pieces(t):
    """{rhs, population, trait, garde_tel, garde_petit} de l'en-tête de FM ; None si la forme a changé"""
    pop = next((r for r in t.walk() if t.name(r) == POPULATION), None)
    dev = next((r for r in t.walk() if t.name(r) == DEVISE), None)
    if pop is None or dev is None:
        return None
    rhs = t.parent.get(pop)
    enfants = t.children(rhs)
    i = enfants.index(pop)
    trait = enfants[i + 1] if i + 1 < len(enfants) else None
    if trait is None or t.elem(trait).get("m_TemplateAlias") != TRAIT:
        return None
    petit = t.parent.get(dev)
    tel = t.parent.get(petit)
    if not typ(t, petit).endswith("SIVisible") or not typ(t, tel).endswith("SIVisible") or t.parent.get(tel) != rhs:
        return None
    textes = [k for k in t.children(pop) if typ(t, k).endswith("SIText")]
    if len(textes) != 2:
        return None
    for k, guid in zip(textes, (FONCTION_TRADUIT, FONCTION_FORMAT)):
        f = (t.sd(k).get("TextBinding") or {}).get("m_visualFunction") or {}
        if (f.get("m_target") or {}).get("m_guid") != guid:
            return None
    return {"rhs": rhs, "population": pop, "trait": trait, "garde_tel": tel, "garde_petit": petit}


def pieces_selection(t):
    """v5 : {rangee, classement, trait, garde_tel, garde_petit} de l'en-tête d'une sélection ; None si la forme a changé.
    La case #WorldRanking = une colonne : titre (texte traduit de FM), puis une rangée (icône, valeur)."""
    cl = next((r for r in t.walk() if t.name(r) == CLASSEMENT), None)
    nick = next((r for r in t.walk() if t.name(r) == SURNOM), None)
    if cl is None or nick is None:
        return None
    rangee = t.parent.get(cl)
    enfants = t.children(rangee)
    i = enfants.index(cl)
    trait = enfants[i + 1] if i + 1 < len(enfants) else None
    if trait is None or t.elem(trait).get("m_TemplateAlias") != TRAIT:
        return None
    petit = t.parent.get(nick)
    tel = t.parent.get(petit)
    if not typ(t, petit).endswith("SIVisible") or not typ(t, tel).endswith("SIVisible") or t.parent.get(tel) != rangee:
        return None
    if [t.binding(x) for x in (tel, petit)] != ["app.GridBreakpointIsPhoneLandscape", "app.GridBreakpointIsSmall"]:
        return None
    col = t.children(cl)
    if len(col) != 1:
        return None
    morceaux = t.children(col[0])
    if len(morceaux) != 2 or not typ(t, morceaux[0]).endswith("SIText"):
        return None
    f = (t.sd(morceaux[0]).get("TextBinding") or {}).get("m_visualFunction") or {}
    if (f.get("m_target") or {}).get("m_guid") != FONCTION_TRADUIT:
        return None
    ligne = t.children(morceaux[1])
    if len(ligne) != 2 or ICONE_FM not in (t.elem(ligne[0]).get("m_Classes") or []) \
            or not typ(t, ligne[1]).endswith("SIText"):
        return None
    return {"rangee": rangee, "classement": cl, "trait": trait, "garde_tel": tel, "garde_petit": petit}


# ---------- textes ----------
def _fonction_texte(t, r):
    return t.sd(r)["TextBinding"]["m_visualFunction"]


def traduit(t, r, numero, secours):
    """texte de FM par son n° de traduction (StaticText), secours anglais écrit à côté comme FM"""
    f = _fonction_texte(t, r)
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(a) != 1 or not bytes(a[0][0]).endswith(b"[SI.Translation.TranslationID]"):
        raise ValueError("texte traduit de FM : arguments inattendus")
    s = secours.encode("utf-8")
    a[0][1] = struct.pack("<i", numero) + bytes([1, len(s)]) + s
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    t.sd(r)["DebugDisplay"] = secours


# ---------- les deux en-têtes ----------
def page_pays(t, p, src):
    """v5 : ce que l'en-tête de la page d'un pays fournit (cases recopiées de Population)"""
    def case(parent, nom, icone=None):
        c = t.clone(p["population"], parent)
        recaler_parent(t, c)
        nommer(t, c, nom)
        titre, valeur = [k for k in t.children(c) if typ(t, k).endswith("SIText")]
        return c, titre, valeur
    return {"uid": UID_PAYS, "tc": src.tc, "commut": src.commut, "trait": p["trait"], "case": case}


def page_selection(t, p, src):
    """v5 : ce que l'en-tête de la page d'une sélection fournit (cases recopiées de Classement mondial : titre, icône,
    valeur ; la valeur prend le texte « modèle + données » de FM)"""
    def case(parent, nom, icone):
        c = t.clone(p["classement"], parent)
        recaler_parent(t, c)
        nommer(t, c, nom)
        titre, ligne = t.children(t.children(c)[0])
        ic, valeur = t.children(ligne)
        nommer(t, ic, icone)
        t.elem(ic)["m_Classes"] = [icone] + [k for k in t.elem(ic)["m_Classes"] if k != ICONE_FM]
        t.sd(valeur)["TextBinding"] = copy.deepcopy(src.tb_format)
        t.sd(valeur)["TextBinding_UxmlAttributeFlags"] = 1
        return c, titre, valeur
    return {"uid": UID_SEL, "tc": src.tc_sel, "commut": src.commut_sel, "trait": p["trait"], "case": case}


# ---------- pièces à nous ----------
def texte_fixe(t, r, s):
    """v4 : un texte écrit tel quel, comme les textes du skin d'Alex : pas de fonction, le champ « text » d'Unity"""
    sd = t.sd(r)
    sd["TextBinding"] = {"m_kind": 0, "m_direct": {"Path": {"m_path": ""}, "Nullable": 0},
                         "m_visualFunction": {"m_target": {"m_guid": ""},
                                              "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                              "m_outputs": {"m_variable": {"m_argumentBytes": []}}}}
    sd["TextBinding_UxmlAttributeFlags"] = 1
    sd["text"], sd["text_UxmlAttributeFlags"] = s, 1
    sd["DebugDisplay"], sd["DebugDisplay_UxmlAttributeFlags"] = s, 1


def comparaison(src, valeur, chemin, operateur=EGAL):
    """v4 : la liaison de FM « chemin == valeur » (BindIntComparisonToSwitch : TryCastToInt, puis l'enfant 1 si vrai,
    l'enfant 0 sinon ; une valeur vide n'est jamais une erreur)"""
    b = copy.deepcopy(src.comparaison)
    f = b["m_visualFunction"]
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    a[0][1] = struct.pack("<i", operateur)
    a[1][1] = struct.pack("<i", valeur)
    a[2][1] = chaine(chemin)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    return b


def commutateur(t, m, parent):
    """un commutateur de FM (du même bundle), vidé de ses enfants et de son style"""
    sw = t.clone(m["commut"], parent, src=m["tc"])
    for k in list(t.children(sw)):
        t.remove(k)
    no_styles(t, sw)
    t.elem(sw)["m_Classes"] = []
    if "m_SerializedDataOverride" in t.elem(sw):
        t.elem(sw)["m_SerializedDataOverride"] = []
    recaler_parent(t, sw)
    t.sd(sw)["name"] = ""
    return sw


def selon_langue(t, src, parent, faire, css):
    """v11, recette 19 (26.13 v24, 26.18) : le conteneur de FM qui lit la langue du jeu (tdd-messages-banner), puis un
    interrupteur par langue de LANGUES_PAGE (rang 1 = c'est elle, rang 0 = la suivante) ; LANGUE_DEFAUT sinon.
    faire(par, langue) pose le contenu d'une langue. Un interrupteur de FM n'instancie que l'enfant montré : le jeu ne
    construit que la langue réglée."""
    env = t.clone(src.langue_env, parent, src=src.tg)
    recaler_parent(t, env)
    for k in list(t.children(env)):
        if not (t.elem(k).get("m_FullTypeName") or "").endswith("Component"):
            t.remove(k)
    t.styles.copy_from(src.tg.styles, t, env)
    t.sd(env)["name"] = ""
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    donnees = json.dumps([(t.refs.get(c["rid"]) or {}).get("data") for c in t.sd(env).get("m_components") or []])
    if "current_language" not in donnees or "app.NativeSettings" not in donnees:
        raise ValueError("conteneur de langue de FM (tdd-messages-banner) : forme inattendue")
    t.styles.style(t, env, css)
    langues = [lg for lg in LANGUES_PAGE if lg not in (LANGUE_DEFAUT, "english (us)")]

    def suite(par, i):
        if i == len(langues):
            faire(par, LANGUE_DEFAUT)
            return
        sw = t.clone(src.langue_sw, par, src=src.tg)
        recaler_parent(t, sw)
        for k in list(t.children(sw)):
            t.remove(k)
        t.styles.copy_from(src.tg.styles, t, sw)
        t.sd(sw)["name"] = ""
        t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
        fn = t.sd(sw)["Binding"]["m_visualFunction"]
        a = decode_args(fn["m_inputs"]["m_variable"]["m_argumentBytes"])
        mots = [x for x in a if bytes(x[0]).endswith(b"StringVisualArg")]
        if len(mots) != 1 or bytes(mots[0][1]) != bytes([1, 7]) + b"english":
            raise ValueError("interrupteur de langue de FM : arguments inattendus")
        mots[0][1] = chaine(langues[i])
        fn["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
        t.styles.style(t, sw, css)
        suite(sw, i + 1)            # rang 0 : pas cette langue
        faire(sw, langues[i])       # rang 1 : c'est elle

    suite(env, 0)
    return env


def titre_selon_langue(t, src, titre, cle):
    """v11 : le titre d'une case, dans la langue du jeu (LANGUES_PAGE[langue][cle], texte fixe) : le titre de FM
    recopié dans chaque langue, à la place de l'original"""
    parent = t.parent[titre]

    def faire(par, lg):
        n = t.clone(titre, par)
        recaler_parent(t, n)
        texte_fixe(t, n, LANGUES_PAGE[lg][cle])
    env = selon_langue(t, src, parent, faire, {"flex-direction": "column"})
    kids = t.elem(parent)["m_Children"]          # à la place du titre (l'ordre est celui de m_Children)
    e = next(k for k in kids if k["rid"] == env)
    kids.remove(e)
    kids.insert(next(i for i, k in enumerate(kids) if k["rid"] == titre), e)
    t.remove(titre)
    return env


def groupe_notes(t, m, src, rangee, valeur, sexe, marge):
    """v4 : les notes sur 200 d'un sexe (0 hommes, 1 femmes)"""
    return groupe_textes(t, m, src, rangee, valeur, {uid: str(n[sexe]) for uid, n in NOTES_DEPART.items()}, marge)


def groupe_textes(t, m, src, rangee, valeur, textes, marge, parent=None):
    """v4 : un texte par pays ({identifiant : texte}) : un commutateur de FM par pays de la table, enfant 0 vide,
    enfant 1 le texte fixe. Un seul s'allume : celui du pays de la page. Un pays absent de la table (autre base de
    données) n'en allume aucun. v6 : sert aussi aux plages trouvées. v11 : parent (sous un interrupteur de langue),
    sinon dans rangee, dont il recopie la forme."""
    g = t.clone_shallow(rangee, parent if parent is not None else rangee)
    recaler_parent(t, g)
    t.sd(g)["name"] = ""
    t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    if marge:
        t.styles.style(t, g, {"margin-right": marge})
    modele = None
    for uid, texte in sorted(textes.items()):
        if modele is None:
            sw = modele = commutateur(t, m, g)
        else:
            sw = t.clone_shallow(modele, g)
            recaler_parent(t, sw)
            t.sd(sw)["name"] = ""
        t.sd(sw)["Binding"], t.sd(sw)["Binding_UxmlAttributeFlags"] = comparaison(src, uid, m["uid"]), 1
        vide = t.clone_shallow(g, sw)
        recaler_parent(t, vide)
        t.elem(vide)["m_Classes"], t.elem(vide)["m_RuleIndex"] = [], -1
        n = t.clone_shallow(valeur, sw)
        recaler_parent(t, n)
        texte_fixe(t, n, texte)
    return g


def case_note(t, m, src, parent):
    """Note de formation | Hommes 155 · Femmes 160 (page d'un pays) : la case Population recopiée ; sa valeur devient une
    rangée. v4 : la note sur 200 au départ (NOTES_DEPART) au lieu du palier 11-20 (YouthRating)."""
    c, titre, valeur = m["case"](parent, f"{NOM}-note")
    rangee = t.clone_shallow(c, c)
    recaler_parent(t, rangee)
    t.sd(rangee)["name"] = ""
    t.elem(rangee)["m_Classes"], t.elem(rangee)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    for (num, sec), sexe, marge in ((T_HOMMES, 0, ESPACE_GENRE), (T_FEMMES, 1, 0)):
        mot = t.clone(titre, rangee)
        recaler_parent(t, mot)
        traduit(t, mot, num, sec)
        t.elem(mot)["m_Classes"] = ["body-md", "global-text-secondary"]
        t.styles.style(t, mot, {"margin-right": ESPACE_MOT})
        groupe_notes(t, m, src, rangee, valeur, sexe, marge)
    t.remove(valeur)
    titre_selon_langue(t, src, titre, "note")   # v11 (v8 : après les mots, recopiés du titre tant qu'il est de FM)
    return c


def case_note_selection(t, m, src, parent, sexe):
    """v5 : Note de formation | [icône] 155 (page d'une sélection) : la note de CE sexe seulement (choix de Kinito :
    « la note femme pour les femmes, la note homme pour les hommes »)"""
    c, titre, valeur = m["case"](parent, f"{NOM}-note", ICONE_NOTE)
    titre_selon_langue(t, src, titre, "note")
    groupe_notes(t, m, src, t.parent[valeur], valeur, sexe, 0)
    t.remove(valeur)
    return c


def mettre_mot(t, c, titre, valeur, mot):
    """v6 (page d'un pays) : la valeur précédée de « Hommes » / « Femmes » (textes de FM), comme la case de la note ;
    le mot est recopié du titre tant qu'il est un texte traduit de FM. Rend la nouvelle valeur."""
    rangee = t.clone_shallow(c, c)
    recaler_parent(t, rangee)
    t.sd(rangee)["name"] = ""
    t.elem(rangee)["m_Classes"], t.elem(rangee)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    m_ = t.clone(titre, rangee)
    recaler_parent(t, m_)
    traduit(t, m_, *mot)
    t.elem(m_)["m_Classes"] = ["body-md", "global-text-secondary"]
    t.styles.style(t, m_, {"margin-right": ESPACE_MOT})
    v = t.clone(valeur, rangee)
    recaler_parent(t, v)
    t.remove(valeur)
    return v


def case_trouvee(t, m, src, parent, sexe, mot=None):
    """« Arrivée des jeunes | 9 mar - 6 avr » : la plage TROUVÉE du pays (PLAGES_RELEVEES, ce sexe), un commutateur de
    FM par pays, comme la note. v10 : pour tous les pays, sans rien lire de leurs clubs. v11 : le titre et les dates
    dans la langue du jeu (un groupe de commutateurs par langue ; le jeu ne construit que la langue réglée)."""
    c, titre, valeur = m["case"](parent, f"{NOM}-trouvee", ICONE_DATE)
    if mot:
        valeur = mettre_mot(t, c, titre, valeur, mot)
    titre_selon_langue(t, src, titre, "arrivee")
    ligne = t.parent[valeur]
    selon_langue(t, src, ligne, lambda par, lg: groupe_textes(
        t, m, src, ligne, valeur, {uid: ecrire_plages(lg, p[sexe]) for uid, p in PLAGES_RELEVEES.items()}, 0, par),
        {"flex-direction": "row", "align-items": "center"})
    t.remove(valeur)
    return c


def trait(t, m, parent):
    r = t.clone(m["trait"], parent)
    recaler_parent(t, r)
    return r


def bloc_dates(t, m, src, parent, genre, mot=None):
    """v10 : l'arrivée des jeunes du pays, écrite en dur (PLAGES_RELEVEES), sans rien lire de ses clubs. Jusqu'en v9, la
    liste des clubs du pays (Nation.ClubListNation, 1er club et 6 derniers : Club.ClubNationHasValidRuleGroupRules,
    Club.IntakeDate) donnait la date en direct ; vu en jeu le 12/11 : FM se fermait (plantage natif) sur la page de la
    Géorgie, puis, la Géorgie mise à part (v9), sur celle de Gibraltar. Kinito : « afficher les dates qu'on a trouvées en
    dur pour tous les pays »."""
    case_trouvee(t, m, src, parent, genre, mot)
    trait(t, m, parent)


# ---------- poser / retirer ----------
def poser(t, src):
    p = pieces(t)
    if p is None:
        return ["en-tête Pays de FM : forme inattendue (le jeu a changé ?) : introuvable"]
    manque = src.manque_pays()
    if manque:
        return [f"morceaux de FM introuvables : {', '.join(manque)}"]
    m = page_pays(t, p, src)
    rang = t.children(p["rhs"]).index(p["trait"]) + 1
    # l'enveloppe : la double garde de la Devise (rien sur téléphone ni en petit affichage)
    tel = t.clone_shallow(p["garde_tel"], p["rhs"], rang)
    recaler_parent(t, tel)
    nommer(t, tel, NOM)
    t.elem(tel)["m_RuleIndex"] = -1
    petit = t.clone_shallow(p["garde_petit"], tel)
    recaler_parent(t, petit)
    t.sd(petit)["name"] = ""
    t.elem(petit)["m_RuleIndex"] = -1
    case_note(t, m, src, petit)
    trait(t, m, petit)
    bloc_dates(t, m, src, petit, 0, T_HOMMES)   # v6 : les hommes, puis les femmes
    bloc_dates(t, m, src, petit, 1, T_FEMMES)
    return [f"page d'un pays : note de formation sur 200 au départ (hommes / femmes, {len(NOTES_DEPART)} pays), plage "
            f"d'arrivée des jeunes, hommes et femmes (trouvée en jeu, écrite en dur, {len(PLAGES_RELEVEES)} pays, dans la langue du jeu) posées "
            f"après Population (v{VERSION})"]


def poser_selection(t, src):
    """v5 : après « Classement mondial » de l'en-tête d'une sélection : la note sur 200 de son sexe et l'arrivée des
    jeunes de son sexe (v10 : écrite en dur). Un commutateur de FM choisit le bloc des hommes ou des femmes, recopié de
    NewsNationalTeamSiteHeader : « Gender == 0 » -> enfant 1 (hommes), sinon enfant 0 (femmes) ; il n'instancie que
    l'enfant montré (les commutateurs des notes de l'autre sexe ne sont pas créés)."""
    p = pieces_selection(t)
    if p is None:
        return ["en-tête d'une sélection de FM : forme inattendue (le jeu a changé ?) : introuvable"]
    manque = src.manque_selection()
    if manque:
        return [f"morceaux de FM introuvables (sélection) : {', '.join(manque)}"]
    m = page_selection(t, p, src)
    rang = t.children(p["rangee"]).index(p["trait"]) + 1
    # l'enveloppe : la double garde du Surnom (rien sur téléphone ni en petit affichage)
    tel = t.clone_shallow(p["garde_tel"], p["rangee"], rang)
    recaler_parent(t, tel)
    nommer(t, tel, NOM_SEL)
    t.elem(tel)["m_RuleIndex"] = -1
    petit = t.clone_shallow(p["garde_petit"], tel)
    recaler_parent(t, petit)
    t.sd(petit)["name"] = ""
    t.elem(petit)["m_RuleIndex"] = -1
    sw = commutateur(t, m, petit)
    t.sd(sw)["Binding"], t.sd(sw)["Binding_UxmlAttributeFlags"] = comparaison(src, 0, GENRE_EQUIPE), 1
    for sexe in (1, 0):   # enfant 0 : femmes (Gender != 0), enfant 1 : hommes (Gender == 0), comme FM
        b = t.clone_shallow(p["classement"], sw)
        recaler_parent(t, b)
        t.sd(b)["name"] = ""
        t.elem(b)["m_Classes"], t.elem(b)["m_RuleIndex"] = ["row-direction-normal", "align-self-stretch"], -1
        case_note_selection(t, m, src, b, sexe)
        trait(t, m, b)
        bloc_dates(t, m, src, b, sexe)
    return [f"page d'une sélection : note de formation sur 200 au départ de son sexe ({len(NOTES_DEPART)} pays) et "
            f"arrivée des jeunes (trouvée en jeu, écrite en dur) posées après Classement mondial (v{VERSION})"]


def retirer(t):
    """notre enveloppe et ses règles retirées ; True si quelque chose a changé"""
    fait = False
    enlever = set()
    tous = set(marques(t))

    def sous_un_autre(r):
        p = t.parent.get(r)
        while p is not None:
            if p in tous:
                return True
            p = t.parent.get(p)
        return False

    for r in [x for x in tous if not sous_un_autre(x)]:   # seulement les enveloppes du haut (une par version)
        for k in t.walk(r):
            enlever.add(t.elem(k).get("m_RuleIndex", -1))
        t.remove(r)
        fait = True
    retirer_regles(t, enlever)
    return fait


def retirer_regles(t, enlever):
    """retire les règles de la feuille intégrée dont les numéros sont dans enlever et que plus rien n'utilise, puis les
    valeurs qu'elles avaient ajoutées en fin de table (comme 26.16)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
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
        for pr in regle["m_Properties"]:
            for v in pr["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    t.styles.changed = True


def a_jour(t, nom):
    return [t.name(r) for r in marques(t) if t.name(r) == nom] == [nom]


# ---------- commandes ----------
ECRANS = ((MODELE, NOM, poser, "page d'un pays"), (MODELE_SELECTION, NOM_SEL, poser_selection, "page d'une sélection"))


def cmd_appliquer():
    src = None
    for modele, nom, poser_fn, ecran in ECRANS:
        o = ouvrir(modele)
        if o is None:
            print(f"[Kinito] Pays : {modele} introuvable (renommé par une mise à jour ?), {ecran} ignorée")
            continue
        t = o[3]
        if a_jour(t, nom):
            print(f"[Kinito] Pays : {ecran} déjà appliquée")
            continue
        src = src or Sources()
        retirer(t)   # une ancienne version, s'il y en a une
        msgs = poser_fn(t, src)
        for msg in msgs:
            print(f"[Kinito] Pays : {msg}")
        if any("introuvable" in msg for msg in msgs):
            print(f"[Kinito] Pays : {ecran} : rien enregistré")
            continue
        enregistrer(*o)
    nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for modele, _nom, _poser, ecran in ECRANS:
        o = ouvrir(modele)
        if o is not None and retirer(o[3]):
            enregistrer(*o)
            fait = True
            print(f"{modele} : {ecran} : notre ajout retiré")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele, nom, _poser, _ecran in ECRANS:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        t = o[3]
        forme = pieces(t) if modele == MODELE else pieces_selection(t)
        print(f"{modele} : " + (f"posé (à jour, v{VERSION})" if a_jour(t, nom) else
                                "ANCIENNE version" if marques(t) else
                                "en-tête de FM introuvable (forme inattendue)" if forme is None else "en-tête de FM"))
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
            print("[Kinito] Pays : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
