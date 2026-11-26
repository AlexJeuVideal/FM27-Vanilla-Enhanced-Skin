"""Staff (Club > Staff) comme dans FM24 : les données et la disposition (mise en forme fine plus tard).

1. Onglets Équipe de préparateurs / de recrutement / médicale : blocs (postes, comparaison) en haut, à hauteur fixe ;
   le tableau du staff dessous prend toute la place restante (FM27 : tableau en haut, blocs écrasés). Tuiles « Base de
   données staff » / « Affectations des entraîneurs » retirées (v17) ; bouton « Affectations des entraîneurs » dans le
   bloc des postes des préparateurs. v20 : la tuile du tableau prend tout l'onglet et porte deux dispositions ; mode
   Défaut = postes / comparaison en colonne à gauche, tableau sur toute la droite ; autres modes = comme avant.
2. Vue d'ensemble : UNE grande tuile (modèle FM inutilisé MatchTopPickReasonCell réécrit) à 3 colonnes
   préparateurs | recrutement | médical = postes + mini-liste du staff (v29, essai) + comparaison avec la ligue. Grilles Small / Standard / Large
   (bundle ui-tileslayouts) calculées depuis les originaux ; l'écran Staff (ClubAllStaffTool) reste d'origine.
3. Comparaison avec la ligue (onglets Équipe de préparateurs / de recrutement / médicale) : FM27 n'affiche qu'un
attribut à la fois, choisi dans un menu. Ici, TOUS les attributs sont listés l'un sous l'autre (classement dans la
ligue, club le plus respecté, club qui peut mieux faire), dans une zone qui défile.

Comment : chez FM, le bloc pose une variable `type` (= numéro de l'attribut choisi dans le menu) puis lit
Team.Staff<Groupe>SubGroupComparison, qui dépend de ce `type`. On pose une ligne par numéro (0..TYPE_MAX), chacune
avec sa variable `type` fixe ; la ligne de FM (#HasDataCheck) n'affiche rien quand il n'y a pas de donnée, donc les
numéros qui n'existent pas restent vides.

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés) :
  ClubStaffCoachingTeamComparisonBlock, ClubStaffRecruitmentTeamComparisonBlock, ClubStaffMedicalTeamComparisonBlock
  et leurs versions …LoRes (petites tuiles), MatchTopPickReasonCell (grande tuile), ClubAllStaffBlock (bloc des postes :
  sans réaction des dirigeants, boutons en haut à droite).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\staff_fm24.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\staff_fm24.py retirer
  .venv\\Scripts\\python.exe outils\\staff_fm24.py etat
"""
import copy
import json
import struct
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L, SUFFIXE, LANGUE  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles, originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from elements import add_using, copy_usings, first, move  # noqa: E402
from notes_installations import (visible_model, new_visible, text_static, text_direct, decode_args,  # noqa: E402
                                 encode_args, _enc_varint, make_binding)
from arbre import no_styles  # noqa: E402
import arbre as sm  # noqa: E402
from entrainement_equipes import evenement_ecran  # noqa: E402  (événement FM « ouvrir un écran »)
import entrainement_equipes as ee  # noqa: E402  (rangée des équipes, v35)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
TYPE_MAX = 24                 # numéros d'attribut essayés : 0..TYPE_MAX (les numéros sans donnée restent vides)
# numéros suivis d'un groupe à l'autre (ClubAllStaffTool : défaut recrutement 14, médical 17) : préparateurs 0..13,
# recrutement 14..16, médical 17.. ; un numéro d'un autre groupe ne donne rien.
# Graphique comme FM24 : une colonne par attribut, barre verticale dont la hauteur et la couleur suivent le niveau FM
# (NIVEAU, énumération, collection TeamComparisonRatingDataCollection : 0 Meilleur, 1 Au-dessus de la moyenne,
# 2 Moyen, 3 Sous la moyenne, 4 Le pire). FM27 ne donne pas le rang en chiffre (seulement le texte « 1er en 3. Liga »,
# essai v4 : Rank, Position, Value, Count… tous vides) : 5 hauteurs possibles. Détail au survol de la colonne.
NIVEAU = "staffsubgroupcomparison.PropertyValue"
SWITCH_ENUM = "4bec613da524e244b8f48e0f1703924a"   # BindEnumIndexToSwitch (sélecteur : enfant n° valeur affiché)
NIVEAUX = [(100, (0.18, 0.62, 0.31, 1)), (80, (0.55, 0.78, 0.25, 1)), (60, (0.83, 0.71, 0.17, 1)),
           (40, (0.91, 0.45, 0.17, 1)), (20, (0.82, 0.22, 0.23, 1))]   # (hauteur %, couleur r g b a)
TITRES_CLUBS = [L("Meilleur de la ligue", "Best in league"),
                L("Plus faible de la ligue", "Weakest in league")]   # infobulle (FM : Most respected / Room…)
PISTE = (1, 1, 1, 0.06)       # fond de la piste (barre vide)
BARRE_LARGEUR = 16            # px
ZONE_MIN = 24                 # px : hauteur minimale de la barre pleine
NOM_TAILLE = 10               # px : nom complet (attribut sans diminutif)
DIMINUTIF_TAILLE = 12         # px
NOM_HAUTEUR = 26              # px : zone du nom sous la barre, fixe (2 lignes ; nom complet au survol)
DESCRIPTION = "staffsubgroupcomparison.Description"
# numéros d'attribut par groupe. Vu en jeu (v6) : préparateurs 0, 2..9 ; recrutement 14 + 2 autres, médical 17 + 1
# autre, hors de 14..18 (les numéros ne se suivent PAS d'un groupe à l'autre) -> 0..TYPE_MAX en attendant l'essai.
PLAGES = {"Coaching": [0, 2, 3, 4, 5, 6, 7, 8, 9], "Recruitment": [13, 14, 18], "Medical": [17, 20]}   # vu v7
# ESSAI v7 : le niveau vaut bien 0 / 1… (texte vu en jeu) mais BindIntToVisible et BindEnumIndexToSwitch n'affichent
# rien : nombre d'un autre type ? Barres posées par chaque fonction FM ; lettres témoins sous les colonnes.
COMPARAISONS = {   # lettre : (fonction FM, type de l'argument valeur, emballage)
    "I": ("d52cf0b2ba55c764b9ecda52092aa257", b"SI.VisualScripting.Int32VisualArg", lambda v: struct.pack("<i", v)),
    "L": ("f3c94f2743a3da249808582a5c0e3f52", b"SI.VisualScripting.Int64VisualArg", lambda v: struct.pack("<q", v)),
    "U": ("5b06bef3ca147e949b631cf5acfbe62e", b"SI.VisualScripting.Int64VisualArg", lambda v: struct.pack("<q", v)),
    "D": ("690be8be67e3d4a4c932f402d5a73176", b"SI.VisualScripting.DoubleVisualArg", lambda v: struct.pack("<d", v)),
}
# v7 vu en jeu : I L U D (niveau >= 0) et T (type == numéro) tous visibles, mais aucune barre « niveau == k ».
# ESSAI v8 : barres par Int32 seulement + barre témoin blanche (mise en page) ; lettres par (fonction, condition) :
CONDITIONS = [(2, 0), (2, 1), (0, 0), (4, 100)]   # (opérateur, valeur) : == 0, == 1, < 0, > 100
LETTRES = {"I": "abcd", "D": "efgh", "L": "ijkl"}
BARRES_PAR = ["I"]
# diminutifs FM24 sous les barres, selon le nom FM27 (jeu en français ; apostrophes droite et typographique).
# Nom absent de la liste -> nom complet. Pos (possession) et Gar (gardiens) : pas d'équivalent exact en FM24.
DIMINUTIFS = {
    "Coaching": {"Gardiens": "Gar", "Gestion des personnes": "GdP", "Entraîneur d'attaque": "Att",
                 "Entraîneur d’attaque": "Att", "Entraîneur de défense": "Déf", "Préparateur physique": "Phy",
                 "Entraînement à la possession de balle": "Pos", "Préparateur technique": "Tec",
                 "Préparation tactique": "Tct", "Entraînement aux coups de pied arrêtés": "ECpa",
                 "Mental": "Men"},
    "Recruitment": {"Évaluation joueurs": "Éval. J", "Évaluation du potentiel": "Éval. P",
                    "Analyse de données": "Ana D"},
    "Medical": {"Kiné": "Kiné", "Sciences du sport": "SdS"},
}
# jeu en anglais (langue.py en) : noms FM27 anglais pas relevés en jeu -> variantes probables ; un nom qui ne
# correspond pas affiche simplement le nom complet de FM
DIMINUTIFS_EN = {
    "Coaching": {"Goalkeepers": "GK", "Goalkeeping": "GK", "Man Management": "MM", "Attacking": "Att",
                 "Attacking Coach": "Att", "Defending": "Def", "Defending Coach": "Def", "Fitness": "Fit",
                 "Fitness Coach": "Fit", "Possession": "Pos", "Ball Possession Training": "Pos",
                 "Possession Training": "Pos", "Technical": "Tec", "Technical Coach": "Tec", "Tactical": "Tac",
                 "Tactical Coaching": "Tac", "Set Pieces": "SP", "Set Piece Training": "SP", "Set Piece Coaching": "SP",
                 "Mental": "Men",
                 # noms FM27 anglais relevés en jeu (2026-11-12)
                 "People Management": "MM", "Attack Coaching": "Att", "Defence Coaching": "Def",
                 "Fitness Coaching": "Fit", "Possession Coaching": "Pos", "Technique Coaching": "Tec"},
    "Recruitment": {"Judging Player Ability": "JPA", "Judging Player Potential": "JPP", "Data Analysis": "DA",
                    "Analysing Data": "DA"},
    "Medical": {"Physiotherapy": "Phy", "Sports Science": "SpS"},
}
if LANGUE != "fr":   # v1.31 : autres langues = abréviations anglaises
    DIMINUTIFS = DIMINUTIFS_EN
ESSAI_CHAMPS = []             # essai v4 terminé (rang en chiffre introuvable)
# ESSAI v6 : v5 = barres toujours vides (sélecteur BindEnumIndexToSwitch réglé comme chez FM) -> valeur brute du
# niveau écrite sous chaque nom pour savoir ce que FM y met (nombre ? nom d'énumération ? autre plage ?)
ESSAI_NIVEAU = False          # essai v8 / v9 terminé (barres validées en jeu)
# hauteur fixe (rangées) des blocs du haut des onglets ; v16 : 6 / 6 / 7 -> 5 (bloc des postes sans réaction des
# dirigeants ni boutons du bas : plus court ; le tableau du staff dessous gagne la place)
HAUT = {"Small": 5, "Standard": 5, "Large": 5}
VUE_COMPARAISON = 2           # (ancienne Vue d'ensemble à 6 tuiles, plus utilisé depuis la grande tuile)
# Vue d'ensemble = UNE grande tuile (demande du 2026-11-12) : 3 colonnes (préparateurs | recrutement | médical),
# chacune = bloc des postes recopié (réaction des dirigeants réduite à sa phrase) + trait + comparaison incluse.
# Elle prend la place de la tuile « préparateurs » (qui reçoit déjà l'équipe), sur toute la largeur ; les deux autres
# tuiles des postes sont retirées. Hauteur de base GRANDE_BASE (rangées), sans maximum : FM l'agrandit pour remplir
# l'écran, les petites tuiles du bas restent visibles.
GRANDE_BASE = {"Small": 5, "Standard": 5, "Large": 6}
GRANDE = "MatchTopPickReasonCell"                    # modèle FM inutilisé (aucun bundle ne cite son GUID), réécrit
GRANDE_GUID = "15cd5ec21866eb449a4f450fc9e63840"
POSTES = "ClubAllStaffBlock"
SOUS_GROUPES = {"Coaching": 0, "Recruitment": 1, "Medical": 2}   # valeur de subgrouptype (en-têtes FM)
COMPARAISON_GUID = {"Coaching": "bb6a535ad4ad38446ac0e1b3552b4c85", "Recruitment": "1a3bc8c395c7a6f44983a8f52f4322de",
                    "Medical": "9e54f89e398f44d41a54ed08d9c42a85"}
TYPE_SOUS_GROUPE = 1400140615                        # type de staffsubgroup (BindingExpect du bloc des postes)
# FM IGNORE la configuration posée dans la grille (m_gridElementConfigs) : il prend, dans la DESCRIPTION de la tuile,
# la configuration la plus large qui rentre (vu en jeu v11 : tuiles de 18 -> ClubAllStaffBlock2ColLoRes, 12x2).
# Aucune grille FM n'a la tuile préparateurs à 12 de large ou plus -> ses configurations de 12 (FM : versions LoRes)
# et une nouvelle de 18 (écran Large) donnent la grande tuile. Onglets : tuiles des postes limitées à
# POSTES_LARGEUR_MAX (11) -> config 7x4 = bloc normal (pas la version 2 colonnes aux textes qui se chevauchent).
DESCRIPTION_POSTES = "ClubCoachingStaffBlockDescription"
CONFIGS = "<Configurations>k__BackingField"
GRANDE_LARGEUR_MIN = 12
POSTES_LARGEUR_MAX = 11
REACTION = "non"              # réaction des dirigeants : "phrase" (texte seul, petit) | "non" (retirée) | "fm"
# boutons du bas du bloc des postes -> à droite du titre : « Demande aux dirigeants » en icône seule (modèle FM
# sans texte du même menu), « Passer annonce » avec son texte (version grand écran de FM)
BOUTONS_EN_HAUT = True
BOUTONS_MARGE_BLOC = 12       # px du bord droit du cadre (bloc des postes des onglets ; 0 dans la grande tuile)
# px du haut : boutons centrés entre le haut du cadre et le trait sous le titre (v19, vu en jeu v18 : grande tuile
# 1 px trop haute -> 1 ; onglets 10 px au-dessus / 4 px au-dessous avec 12 -> 9)
BOUTONS_HAUT_BLOC = 9
BOUTONS_HAUT_GRANDE = 1
BOUTONS = "ClubStaffActionsButtons"
BOUTONS_LIGNE = "LargeResBoardActions"
MENU_DIRIGEANTS = "SpeakToActionsDropdownWidgetWithDisable"
MENU_ICONE = ("dropdown-base-regular-leading-icon-trailing-icon", "f7217175ef98e1842ae4d6813fabdf7c")
# éléments du menu avec texte -> mêmes éléments du menu sans texte (surcharges : actions, icône ; le texte est retiré)
MENU_IDS = {619928808: -1492516038, 1690305146: -422139700}
# v17 (demande du 2026-11-12) : tuiles « Base de données staff » et « Affectations des entraîneurs » retirées des 3
# onglets (la base de données reste dans la Vue d'ensemble) ; la comparaison prend leur place jusqu'au bord droit.
# À la place : un bouton FM « Affectations des entraîneurs » à gauche des boutons du bloc des postes, préparateurs
# seulement (SIVisible #CoachingStaffHeaderVisible de FM recopié : subgrouptype == coaching).
TUILES_RETIREES = ["StaffSearch", "CoachAssignments"]
AFFECTATIONS_ONGLET = True     # bouton dans le bloc des postes de l'onglet Équipe de préparateurs
AFFECTATIONS_VUE = True        # idem dans la colonne préparateurs de la Vue d'ensemble (v18, demande du joueur)
AFFECTATIONS_MONTER = 0        # px : v17 un poil plus bas que les 2 menus voisins (v18 : 1) ; v22 vu 1 px trop haut
# v22 (demande du joueur) : « Affectations des entraîneurs » trop long en 1080 -> texte fixe plus court en français ;
# anglais : traduction FM 34884 « Coach Assignments » gardée (None = traduction FM)
AFFECTATIONS_COURT = L("Affectations prépa", None)   # v26 : « Affectations préparateurs » encore trop long
# v33 (demande du joueur, 2026-10-31) : texte encore trop long (chevauche le titre, ex. espagnol) -> l'icône cône des
# préparateurs (celle du titre FM) à la place du texte ; False = texte AFFECTATIONS_COURT
AFFECTATIONS_ICONE = True
ICONE_PREPA = "game-concepts-training-general_medium"   # élément et classe FM de l'icône du titre des préparateurs
# v33 : titres FM « 15 miembro(s) del cuerpo técnico » trop longs (sous les boutons) -> le nombre seul
# (staffsubgroup.Count) suivi du nom court du groupe
TITRES_COURTS = {"CoachingStaffHeader": L("Préparateurs", "Coaching"),
                 "RecruitmentStaffHeader": L("Recrutement", "Recruitment"),
                 "MedicalStaffHeader": L("Médical", "Medical")}
TITRE_ECART = 4               # px entre le nombre et le nom
# v26 : écart avec le menu voisin vu ~6 px plus grand que celui entre les 2 menus FM (même classe de marge) : marges
# propres du bouton (règle FM des boutons) mises à 0
AFFECTATIONS_BOUTON_MARGES = 0
# v21 (vu en jeu v20) : onglet Préparateurs, ligne du titre ~4 px plus basse que Recrutement / Médical (icône sifflet
# plus petite que la loupe / la croix : trait plus haut) et boutons ~2 px plus bas -> hauteur minimale des titres des 3
# groupes, rangée de boutons remontée quand elle contient « Affectations des entraîneurs »
TITRE_HAUTEUR_MIN = 24        # px (icônes medium 24 px des autres groupes)
TITRES_GROUPES = ("CoachingStaffHeader", "RecruitmentStaffHeader", "MedicalStaffHeader")
BOUTONS_MONTER_AFFECTATIONS = 2   # px
AFFECTATIONS_ECRAN = "b134c6823f6d1784c97dfd072102c8dc"   # écran ouvert par la tuile FM CoachAssignmentsTile (team)
AFFECTATIONS_TEXTE = 34884     # traduction FM « Coach Assignments » (titre de la tuile)
# même aspect que les 2 menus voisins (« Passer annonce », menu des dirigeants), sans flèche : conteneur de classe FM
# buttons-dropdown-base-regular > bouton de classe si-dropdown__selection-field (fond, bord, arrondi, hauteur, survol
# des menus FM), texte label-md comme « Passer annonce », écart margin-right-global-gap-regular comme chez FM
AFFECTATIONS_CLASSES = (["buttons-dropdown-base-regular", "margin-right-global-gap-regular"],
                        ["si-dropdown__selection-field", "label-md", "primary-text-colour"])
BOUTON_SOURCE = ("CalendarHeaderSeasonBlock", "Today")   # SIButton FM « Aujourd'hui » (comme entrainement_equipes)
COMPARAISON_MIN = 150         # px : hauteur minimale des barres de comparaison
# postes = hauteur de leur contenu (min POSTES_MIN), comparaison = le reste (v13 : partage 3/5 - 2/5 -> liste
# coupée en Défaut / Détaillé, grand vide en Condensé)
POSTES_MIN = 120              # px
TRAIT = (1, 1, 1, 0.08)       # traits de séparation
# Onglets Préparateurs / Recrutement / Médical : rangée des blocs en haut, hauteur fixe HAUT ; le tableau passe
# dessous, hauteur de base FM (3 / 3 / 4), sans maximum : il prend toute la place qui reste. Bloc des postes forcé en
# version normale (celle de la Vue d'ensemble) : la version « 2 colonnes » de FM fait se chevaucher les textes.
# Totaux de base (rangées) : onglets 8 / 8 / 10, Vue d'ensemble 9 / 9 / 10 (FM : 7 / 7 / 9) ; FM ne descend jamais
# sous la hauteur de base : garder ces totaux petits pour que rien ne sorte de l'écran (grand écran ≈ 15 rangées).
# v20 (demande du 2026-11-12) : onglets Préparateurs / Recrutement / Médical, MODE DÉFAUT : postes en haut à gauche,
# comparaison dessous (même hauteur), tableau du staff sur toute la droite. Une grille FM ne dépend pas du mode
# d'affichage -> la tuile du tableau (StaffContracts, modèle ClubStaffTeamContractBlock) prend tout l'onglet et porte
# les deux dispositions : SIVisible settings.AdaptiveScalingLevelIndex == 0 (Défaut, colonne de gauche) / > 0 (autres
# modes : rangée postes | comparaison au-dessus du tableau, comme v19). Chaque disposition est sous un SIVisible
# subgrouptype == 0 / 1 / 2 (posé par l'onglet, passé à la tuile par ClubAllStaffTool) : rien dans « Tout le staff ».
DEFAUT_COTE = True
GAUCHE_LARGEUR = 520          # px : colonne de gauche en Défaut (v25 : 600 -> 520, tableau de droite plus large)
AUTRES_HAUTEUR = 330          # px : rangée postes | comparaison des autres modes (v19 : 5 rangées de grille)
AUTRES_PARTS = (3, 7)         # largeurs relatives postes / comparaison dans cette rangée (v19 : 6 / 14 en Large)
ECART = 8                     # px entre les blocs
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Défaut, 1 Détaillé, 2 Condensé
CONTRATS = "ClubStaffTeamContractBlock"                 # modèle de la tuile StaffContracts (aussi « Tout le staff »)
CONTRATS_DONNEES = ("staffsubgroup", "subgrouptype", "club")   # données ajoutées à la tuile (comme les postes)
SANS_GROUPE = -1   # subgrouptype quand l'écran n'en donne pas (« Tout le staff ») : aucun bloc de gauche
# Vue d'ensemble, mini-liste du staff de chaque groupe entre les postes et les graphiques (ESSAI, demande du
# 2026-10-30). v29 (vue en jeu) : liste d'icônes FM + ligne InductionKeyPersonnelCell -> pas de « i » ni de barre de
# défilement. v30 (le joueur : « t'inspirer des listes existantes dans staff, changer ce qu'on voit dedans ») : le
# tableau FM des onglets (#StaffContractsTable de ClubStaffTeamContractBlock : « i », clic, défilement) recopié, sur
# team.Staff<G>SubGroup.StaffSubGroupPersonList, avec SA vue : InitFunction « une vue » du tableau du Portail
# (446475dd) sur la vue FM inutilisée LISTE_VUE (ui-tableviews, citée par rien, réécrite : colonnes LISTE_COLONNES de
# la vue Contrat du staff). Pas en mode Large (le joueur : « en large on va oublier ») : SIVisible mode > 0.
# Hauteur : moitié de la place sous les postes (l'autre = graphiques), entre LISTE_MIN_LIGNES et LISTE_MAX_LIGNES.
LISTE = True
LISTE_TABLEAU = "StaffContractsTable"                    # dans CONTRATS (original)
LISTE_INIT_SOURCE = "PortalAdaptiveContentBlock"         # son 1er StreamedTable : InitFunction à une vue
LISTE_INIT_GUID = "446475dd53423864183c52075b8f0e32"
LISTE_INIT_VUE_FM = "3a280eff0041cbd42a02cf328d097b1a"   # la vue du Portail dans cette InitFunction (remplacée)
# v34 (2026-11-06) : SetPieceTakerListThrowTakersTable (v30-v33) est citée dans FM27 par
# SetPieceTakerListTableViewSettingsCollection (ui-datacollections, par path_id) : écran des tireurs de touches cassé.
# -> vue citée par RIEN dans FM27 (GUID, path_id dans tous les bundles ui-*, nom dans le code : 2026-11-06) ;
# l'ancienne rendue d'origine (LISTE_VUE_ANCIENNE)
LISTE_VUE = "PlayerReportScoutedSquadComparisonPlayersLongTableViewSettings"   # réécrite (seul propriétaire)
LISTE_VUE_GUID = "13c5536ff0eb4b34ca92224fcfd3699a"
LISTE_VUE_ANCIENNE = "SetPieceTakerListThrowTakersTable"
LISTE_VUE_SOURCE = "NonPlayerStaffListTableContract"     # vue Contrat du tableau du staff (lue seulement)
LISTE_COLONNES = ["portrait-name", "clubjob", "context-contract-expiry-date-small"]
LISTE_LIGNE = 26              # px par ligne (estimation, pour les hauteurs min / max)
LISTE_ENTETE = 30             # px : en-tête des colonnes
LISTE_MIN_LIGNES = 2
LISTE_MAX_LIGNES = 6
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
# v31 (le joueur : « enlève la case de sélection, elle sert à rien ») : la case vient de la colonne de sélection par
# défaut du tableau ; SelectionCellID -> NOTRE colonne de sélection invisible, ajoutée à la fabrique du staff (copie de
# la colonne FM à 0 px selection-small, comme kinito_rencontres_vues v8). ui-tablefactories : moral_icone_seule
# (propriétaire, repart de l'original) rappelle fabrique_appliquer() quand ce script est actif ; sinon ce script écrit
# le bundle actuel.
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
LISTE_FABRIQUE = "NonPlayerTableFactory"
LISTE_SELECTION = "uipicker-staff-selection"
SELECTION_SOURCE = ("PlayerPositionalRolesTableFactory", "selection-small")
# v35 (demande du joueur, 2026-11-13) : rangée des équipes du club (comme le calendrier / les rencontres) dans l'espace
# vide de la ligne d'onglets (Vue d'ensemble | Équipe de préparateurs | … | Tout le staff) ; clic = Staff de l'équipe.
# Emplacement prévu par FM : ExtraTabRowButtonTemplate de l'écran (le calendrier y met CalendarHeaderSeasonBlock).
EQUIPES = True
EQUIPES_REGLAGE = {"liste": "human.Club.Teams", "largeur": None, "hauteur": 32, "descendre": 0, "marge": 0}
EQUIPES_RANGEE = "ClubAndNationRow"     # modèle FM inutilisé (scan 2026-11-13 : cité par aucun bundle ni par le code)
EQUIPES_RANGEE_GUID = "0cce345bc92f2fd478c2582642122cb1"
EQUIPES_BOUTON = "ClubIconNameRow"      # idem, réécrit en bouton d'équipe (celui du calendrier)
EQUIPES_BOUTON_GUID = "6e6e95d20d5cc794cac4ca1499da183c"
ECRAN_STAFF = "9ba550b513bf5144da547e7d87df80da"   # ClubAllStaffTool (ui-panelids, paramètre team)
EQUIPES_ONGLET = "navigation-tab-default-default"   # bouton FM des onglets de l'écran (v38 : boutons d'équipes)
EQUIPES_ECART = 16            # px entre deux boutons d'équipes
EQUIPES_DROITE = 24           # px : marge au bord droit (v40 : 0 = collé au bord de l'écran, vu en jeu ; aligné sur
                              # le bord droit des tuiles / « Passer annonce »)
EQUIPES_STYLE_LIGNE = "tabbed-grid-layout-tab-button-container-flex-start-extra-tab-flex-end"   # v39 (classe FM)
# =====================================================================================================

VERSION = f"41{SUFFIXE}"   # v41 : mini-listes du staff, largeur des colonnes réglable à la main ; v34 : vue de la mini-liste changée (LISTE_VUE) ; v35 : équipes
                           # (pas affichées : drapeau du champ à 0) ; v36 : ExtraTabRowButtonTemplate_UxmlAttributeFlags 1
                           # (toujours rien) ; v37 : racine BindingExpect au lieu de BindingRoot (VU, s'affiche) ;
                           # v38 : boutons = onglets FM en texte (VU : bons, mais morts, collés aux onglets) ;
                           # v39 : Events_UxmlAttributeFlags 1, style de ligne FM « extra-tab-flex-end » sans défilement
                           # (VU : marche, collé au bord) ; v40 : marge droite 24
INFOBULLE_SOURCE = "PlayerAttributesLargeBlock"   # modèle FM avec un SI.Bindable.Tooltip simple (bouton polygone)
CADRE = ["siblock-border", "flex-grow-class"]     # fond + bord des blocs des postes (ClubAllStaffBlock)
TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
OUTIL = "ClubAllStaffTool"     # écran Staff : donne à chaque tuile ses données (attributs, groupe…)
GROUPES = {"Coaching": "coaching", "Recruitment": "recruitment", "Medical": "medical"}
ONGLETS = {"CoachingTeamTab": "Coaching", "RecruitmentTeamTab": "Recruitment", "MedicalTeamTab": "Medical"}
TAILLES = ["Small", "Standard", "Large"]
TABLEAU = "StaffContracts"
BLOC_NORMAL = "bfec4d04a6455524fb383fca5e36787d"   # ClubAllStaffBlock (bloc des postes, version normale)
ENSEMBLE_VUE = "OverviewTabGridElementSet"
ENSEMBLE_ONGLETS = "StaffTeamTabGridElementSet"
MODELES =[f"ClubStaff{g}TeamComparisonBlock{v}" for v in ("", "LoRes")
           for g in ("Coaching", "Recruitment", "Medical")]
# grande tuile (7x5) = bloc normal ; petites tuiles (4x2, 8x2 : petits écrans / autres modes) = bloc LoRes.
# Les deux reçoivent la même ligne, celle du gabarit normal (la ligne LoRes de FM n'a pas le nom de l'attribut) :
# tout défile, donc ça tient quelle que soit la hauteur de la tuile.
GABARIT = "ClubStaffComparisonBlockTemplate"   # contenu FM du bloc (titre, menu, ligne de comparaison)
DEFILE_SOURCE = "ClubSiteBlock"                # un SIScrollView de FM à recopier
PREFIXE = "UIPickerStaffComparaison"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
NOM_GRANDE = f"{PREFIXE}Grande-v{VERSION}"
NOM_BOUTONS = f"{PREFIXE}Boutons-v{VERSION}"
NOM_ONGLET = f"{PREFIXE}Onglet-v{VERSION}"
NOM_EQUIPES = f"{PREFIXE}Equipes-v{VERSION}"
NOM_BOUTON_EQUIPE = f"{PREFIXE}BoutonEquipe-v{VERSION}"
ENSEMBLES_ONGLETS = [f"{o}GridCompositionSet" for o in ONGLETS]
MARKER = os.path.join(backup.BACKUP_DIR, "staff_fm24.actif")


for _nom, _val in {"align-items": (131073, 7), "align-self": (131074, 7), "flex-direction": (131083, 7),
                   "justify-content": (131088, 7), "white-space": (65552, 7), "-unity-text-align": (65546, 7),
                   "font-size": (65537, 3), "height": (131087, 3), "width": (131105, 3), "max-height": (131094, 3),
                   "margin-top": (131093, 3), "border-radius": (262147, 3), "padding": (262151, 3),
                   "position": (131102, 7), "left": (131089, 3), "bottom": (131080, 3), "top": (131104, 3),
                   "right": (131103, 3)}.items():
    sm.PROPRIETES.setdefault(_nom, _val)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def nommer(t, r, nom):
    t.sd(r)["name"] = nom
    t.sd(r)["name_UxmlAttributeFlags"] = 1


class Sources:
    def __init__(self):
        o = ouvrir(GABARIT)
        self.g = o and o[3]
        g = self.g
        self.titre = g and first(g, lambda r: g.name(r) == "FullHeadingFrame")
        self.ligne = g and first(g, lambda r: g.name(r) == "HasDataCheck")
        self.menu = g and first(g, lambda r: g.name(r) == "AttributeDropdown")
        d = hp.src_tree(DEFILE_SOURCE)
        self.d = d
        self.defile = d and first(d, lambda r: typ(d, r).endswith("SIScrollView"))
        # infobulle FM (SI.Bindable.Tooltip contenant un SIText), comme fiches_plus
        p = hp.src_tree(INFOBULLE_SOURCE)
        self.p = p
        self.bulle = p and first(p, lambda r: typ(p, r) == "Tooltip" and len(p.children(r)) == 1
                                 and typ(p, p.children(r)[0]) == "SIText")
        # SIVisible « chemin == entier » de FM (BindIntToVisible)
        self.vs, self.vis = visible_model()
        # SIVisible « texte == / != valeur » de FM (BindStringToVisible), comme hierarchie_pyramide
        self.sb, self.svis = visible_model(hp.VISIBLE_TEXTE_SOURCE, hp.FN_TEXTE_EGAL)
        # grande tuile : bloc des postes FM (cadre sous le BindingExpect) et bloc de comparaison FM (variables,
        # remapper, inclusion du gabarit), tous deux d'origine
        o = ouvrir(POSTES, depart_original=True)
        self.pt = o and o[3]
        pt = self.pt
        self.postes = pt and first(pt, lambda r: "siblock-border" in (pt.elem(r).get("m_Classes") or []))
        o = ouvrir(BOUTONS, depart_original=True)
        self.bt = o and o[3]
        bt = self.bt
        self.boutons = bt and first(bt, lambda r: bt.name(r) == BOUTONS_LIGNE)
        o = ouvrir(MENU_DIRIGEANTS, depart_original=True)
        self.mt = o and o[3]
        mt = self.mt
        self.menu_vars = mt and first(mt, lambda r: typ(mt, r) == "BindingVariables")
        o = ouvrir(MODELES[0], depart_original=True)
        self.ct = o and o[3]
        ct = self.ct
        self.variables = ct and first(ct, lambda r: typ(ct, r) == "BindingVariables")
        self.remapper = ct and first(ct, lambda r: typ(ct, r) == "BindingRemapper")
        self.inclusion = ct and first(ct, lambda r: ct.elem(r).get("m_TemplateAlias"))
        # bouton « Affectations des entraîneurs » : condition « préparateurs » du bloc des postes, bouton FM normal
        self.si_prepa = pt and first(pt, lambda r: pt.name(r) == "CoachingStaffHeaderVisible")
        self.cone = pt and first(pt, lambda r: pt.name(r) == ICONE_PREPA)
        o = ouvrir(BOUTON_SOURCE[0], depart_original=True)
        self.et = o and o[3]
        et = self.et
        self.bouton = et and first(et, lambda r: typ(et, r) == "SIButton" and r in et.parent
                                   and et.name(et.parent[r]) == BOUTON_SOURCE[1])
        # mini-liste du staff (Vue d'ensemble) : tableau FM des onglets + InitFunction « une vue » du Portail
        o = ouvrir(CONTRATS, depart_original=True) if LISTE else None
        self.tt_ = o and o[3]
        tt_ = self.tt_
        self.tableau = tt_ and first(tt_, lambda r: tt_.name(r) == LISTE_TABLEAU and typ(tt_, r) == "StreamedTable")
        ps = hp.src_tree(LISTE_INIT_SOURCE) if LISTE else None
        tab = ps and first(ps, lambda r: typ(ps, r) == "StreamedTable" and (ps.sd(r).get("InitFunction") or {})
                           .get("m_target", {}).get("m_guid") == LISTE_INIT_GUID and LISTE_INIT_VUE_FM.encode()
                           in bytes(ps.sd(r)["InitFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]))
        self.init_vue = None
        if tab is not None:
            f = copy.deepcopy(ps.sd(tab)["InitFunction"])
            octets = bytes(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            f["m_inputs"]["m_variable"]["m_argumentBytes"] = list(
                octets.replace(LISTE_INIT_VUE_FM.encode(), LISTE_VUE_GUID.encode()))
            self.init_vue = f

    def manque(self):
        return [n for n, v in (("titre", self.titre), ("ligne", self.ligne), ("menu", self.menu),
                               ("zone qui défile", self.defile), ("infobulle", self.bulle),
                               ("SIVisible entier", self.vis), ("SIVisible texte", self.svis),
                               ("bloc des postes", self.postes), ("variables", self.variables),
                               ("remapper", self.remapper), ("inclusion", self.inclusion),
                               ("boutons", self.boutons), ("menu des dirigeants", self.menu_vars),
                               ("condition préparateurs", self.si_prepa), ("bouton FM", self.bouton))
                if v is None] + ([n for n, v in (("tableau du staff", self.tableau), ("vue du Portail", self.init_vue))
                                  if v is None] if LISTE else [])


def construire(t, src):
    """bloc FM : BindingExpect > BindingVariables (type, menu) > remappers > gabarit inclus
    -> BindingExpect > racine [ titre FM sans menu ; défile [ par numéro : variables(type=k) > remapper > ligne ] ]"""
    expect = first(t, lambda r: typ(t, r) == "BindingExpect")
    variables = first(t, lambda r: typ(t, r) == "BindingVariables")
    groupe = first(t, lambda r: typ(t, r) == "BindingRemapper" and any(
        m.get("from") == "staffsubgroupcomparison" for m in t.sd(r).get("Mappings") or []))
    inclus = first(t, lambda r: t.elem(r).get("m_TemplateAlias"))
    if None in (expect, variables, groupe, inclus):
        return ["structure FM du bloc introuvable (mise à jour du jeu ?)"]
    chemin = next(m["to"]["m_path"] for m in t.sd(groupe)["Mappings"] if m.get("from") == "staffsubgroupcomparison")
    g = src.g

    # racine : copie de la boîte du titre du gabarit (VisualElement), vidée
    racine = t.clone(src.titre, expect, src=g)
    for k in list(t.children(racine)):
        t.remove(k)
    no_styles(t, racine)
    nommer(t, racine, NOM_RACINE)
    t.elem(racine)["m_Classes"] = list(CADRE)   # même fond / bord que les blocs des postes (FM : bloc sans cadre)
    t.styles.style(t, racine, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "overflow": "hidden",
                               "padding": 12})
    # hauteur = celle de la tuile, quel que soit le mode d'affichage : le surplus défile, rien ne sort de l'écran
    t.styles.style(t, expect, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})

    # titre FM (« Comparaison équipe de préparateurs »…) sans le menu des attributs
    titre = t.clone(src.titre, racine, src=g)
    t.styles.copy_from(g.styles, t, titre)
    copy_usings(t, g, src.titre)
    for r in list(t.walk(titre)):
        if r in t.refs and t.name(r) == "AttributeDropdown":
            t.remove(r)

    # graphique : une colonne par attribut, côte à côte (FM24) ; colonnes plus étroites si la tuile l'est
    rangee = boite(t, src, racine)
    t.styles.style(t, rangee, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "flex-direction": "row",
                               "justify-content": "space-around", "align-items": "stretch", "margin-top": 8})
    copy_usings(t, g, src.ligne)
    nom_groupe = next((gr for gr in PLAGES if f"Staff{gr}SubGroup" in chemin), None)
    plage = PLAGES.get(nom_groupe, range(TYPE_MAX + 1))
    for k in plage:
        v = t.clone_shallow(variables, rangee)
        t.sd(v)["name"] = ""
        t.elem(v)["m_Classes"] = []
        t.elem(v)["m_RuleIndex"] = -1
        t.sd(v)["ValueVariables"] = [{"m_name": "type", "m_scopeValue": {"m_serializedData": f"Int|{k}|"}}]
        t.sd(v)["ReferenceVariables"] = []
        # colonnes de même largeur qui se partagent toute la tuile
        t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                              "flex-direction": "column"})
        rm = t.clone_shallow(groupe, v)
        t.sd(rm)["name"] = ""
        t.elem(rm)["m_RuleIndex"] = -1
        t.styles.style(t, rm, {"flex-grow": 1, "min-width": 0})
        ligne = t.clone(src.ligne, rm, src=g)
        t.styles.copy_from(g.styles, t, ligne)
        t.sd(ligne)["name"] = ""
        t.styles.style(t, ligne, {"flex-grow": 1, "min-width": 0})
        # pas de donnée pour ce numéro : rien (FM écrit « Aucune donnée disponible »)
        for r in list(t.walk(ligne)):
            if r in t.refs and t.name(r) == "NoData" and typ(t, r) == "VisualElement":
                for kid in list(t.children(r)):
                    t.remove(kid)
        err = barre(t, ligne, src, k, DIMINUTIFS.get(nom_groupe, {}))
        if err:
            return [err]

    t.remove(variables)   # l'ancien contenu (variables du menu > remappers > gabarit)
    return [f"{chemin} : une barre par attribut ({min(plage)}..{max(plage)}), détail au survol"]


def boite(t, src, parent, index=None):
    """VisualElement vide sans style (copie vidée de la boîte du titre du gabarit)"""
    b = t.clone(src.titre, parent, index, src=src.g)
    for k in list(t.children(b)):
        t.remove(k)
    no_styles(t, b)
    t.sd(b)["name"] = ""
    t.elem(b)["m_Classes"] = []
    return b


def barre(t, ligne, src, numero, diminutifs):  # noqa: C901
    """ligne FM sur 3 étages (attribut + classement ; Plus grand respect + club ; Peut mieux faire + club)
    -> une ligne : nom de l'attribut | barre (longueur et couleur selon le niveau FM 0..4 : Meilleur … Le pire).
    Au survol de la ligne : l'infobulle reprend la ligne FM complète (classement, pastille, les deux clubs)."""
    hd = next((r for r in t.walk(ligne) if t.name(r) == "HasData"), None)
    if hd is None:
        return "ligne de comparaison FM inattendue (HasData introuvable)"
    desc = next((r for r in t.walk(hd) if typ(t, r) == "SIText"
                 and (t.binding(r, "TextBinding") or "").endswith("staffsubgroupcomparison.Description")), None)
    if desc is None:
        return "ligne de comparaison FM inattendue (nom de l'attribut introuvable)"
    anciens = list(t.children(hd))

    # infobulle : contenu FM d'origine (nom, classement + pastille, plus grand respect, peut mieux faire)
    bulle = t.clone(src.bulle, hd, src=src.p)
    no_styles(t, bulle)
    t.sd(bulle)["name"] = ""
    for k in list(t.children(bulle)):
        t.remove(k)
    for r in anciens:
        if (t.elem(r).get("m_TemplateAlias") or "").startswith("layout-divider"):
            t.remove(r)
        else:
            move(t, r, bulle)
    titre_bulle = t.clone(desc, t.children(bulle)[0], 0)   # le nom reste aussi en haut de l'infobulle
    t.sd(titre_bulle)["name"] = ""
    # titres FM des deux clubs (« Plus grand respect » = traduction de « Most respected ») -> libellés clairs
    for rm, libelle in zip((r for r in t.walk(bulle) if typ(t, r) == "BindingRemapper"), TITRES_CLUBS):
        tx = next((k for k in t.children(t.parent[rm]) if typ(t, k) == "SIText"), None)
        if tx is not None:
            sd = t.sd(tx)
            sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = libelle, 1, libelle
            sd["TextBinding"] = {"m_kind": 0, "m_direct": {"Path": {"m_path": ""}, "Nullable": 0},
                                 "m_visualFunction": {"m_target": {"m_guid": ""},
                                                      "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                      "m_outputs": {"m_variable": {"m_argumentBytes": []}}}}
    if ESSAI_CHAMPS:   # ESSAI : rang en chiffre caché ? « nom=valeur » en bas de l'infobulle
        essai = boite(t, src, bulle)
        t.styles.style(t, essai, {"flex-direction": "row", "flex-wrap": "wrap", "margin-top": 6})
        for champ in ESSAI_CHAMPS:
            text_static(t, desc, essai, f" {champ}=")
            text_direct(t, desc, essai, f"staffsubgroupcomparison.{champ}")

    # colonne (FM24) : piste verticale avec la barre qui monte selon le niveau, nom court dessous
    zone = boite(t, src, hd, 0)
    t.styles.style(t, zone, {"flex-grow": 1, "min-height": ZONE_MIN, "flex-direction": "column",
                             "align-items": "center", "justify-content": "flex-end"})
    piste = boite(t, src, zone)
    t.styles.style(t, piste, {"width": BARRE_LARGEUR, "height": hp.POURCENT(100), "flex-direction": "column",
                              "justify-content": "flex-end", "background-color": PISTE,
                              "border-radius": BARRE_LARGEUR / 2})
    # une barre par niveau : SIVisible « niveau == k » (condition vraie en jeu, v8), plein cadre en bas de la piste.
    # La couleur est sur un ENFANT du SIVisible (comme les pastilles d'infobulle_pour_contre, validées) : posée sur
    # le SIVisible lui-même, rien ne s'affichait (v4 à v8)
    guid, type_arg, emballe = COMPARAISONS["I"]
    for niveau, (part, couleur) in enumerate(NIVEAUX):
        v = new_visible(t, src.vs, src.vis, piste, None, "", comparaison(src, guid, type_arg, emballe(niveau), 2, NIVEAU))
        t.elem(v)["m_RuleIndex"] = -1
        t.styles.style(t, v, {"position": "absolute", "left": 0, "bottom": 0, "width": hp.POURCENT(100),
                              "height": hp.POURCENT(part)})
        fond(t, src, v, couleur)
    if ESSAI_NIVEAU:   # ESSAI v9 : témoins toujours visibles par-dessus la barre, chacun sur une moitié de la piste
        # gauche, blanc à 30 % : boîte simple en absolu (la mise en page en % marche-t-elle ?)
        fond(t, src, piste, (1, 1, 1, 0.9), {"position": "absolute", "left": 0, "bottom": 0,
                                              "width": hp.POURCENT(50), "height": hp.POURCENT(30)})
        # droite, cyan à 60 % : SIVisible toujours vrai (type == numéro) + enfant coloré (méthode des barres)
        v = new_visible(t, src.vs, src.vis, piste, None, "", comparaison(src, guid, type_arg, emballe(numero), 2, "type"))
        t.elem(v)["m_RuleIndex"] = -1
        t.styles.style(t, v, {"position": "absolute", "right": 0, "bottom": 0, "width": hp.POURCENT(50),
                              "height": hp.POURCENT(60)})
        fond(t, src, v, (0.2, 0.9, 1, 0.9))

    # sous la barre, zone de hauteur FIXE (toutes les barres partent de la même ligne) : diminutif FM24 si le nom
    # FM27 est dans DIMINUTIFS (comparaison de texte), sinon le nom complet
    etiquette = boite(t, src, hd)
    t.styles.style(t, etiquette, {"height": NOM_HAUTEUR, "flex-shrink": 0, "margin-top": 4, "overflow": "hidden",
                                  "align-items": "center"})
    t.elem(desc)["m_Classes"] = ["global-text-secondary"]
    t.elem(desc)["m_RuleIndex"] = -1
    t.styles.style(t, desc, {"font-size": NOM_TAILLE, "white-space": "normal", "-unity-text-align": "upper-center"})
    autres = etiquette
    for nom, court in diminutifs.items():
        oui = visible_texte(t, src, etiquette, nom, True)
        tx = text_static(t, desc, oui, court)
        t.sd(tx)["name"] = ""
        t.elem(tx)["m_Classes"] = ["global-text-secondary"]
        t.elem(tx)["m_RuleIndex"] = -1
        t.styles.style(t, tx, {"font-size": DIMINUTIF_TAILLE, "-unity-text-align": "upper-center",
                               "white-space": "nowrap"})
        autres = visible_texte(t, src, autres, nom, False)   # aucun nom connu -> nom complet
    move(t, desc, autres)
    if ESSAI_NIVEAU:   # ESSAI : « numéro : niveau brut » sous l'étiquette
        essai = boite(t, src, hd)
        t.styles.style(t, essai, {"flex-direction": "row", "justify-content": "center", "flex-shrink": 0})
        textes = [text_static(t, desc, essai, f"{numero} : "), text_direct(t, desc, essai, NIVEAU)]
        # témoins : une lettre par (fonction, condition) vraie ; voir LETTRES
        temoins = []
        for fonction, lettres in LETTRES.items():
            guid, type_arg, emballe = COMPARAISONS[fonction]
            for lettre, (op, val) in zip(lettres, CONDITIONS):
                temoins.append((lettre, comparaison(src, guid, type_arg, emballe(val), op, NIVEAU)))
        for lettre, liaison in temoins:
            v = new_visible(t, src.vs, src.vis, essai, None, "", liaison)
            t.elem(v)["m_RuleIndex"] = -1
            textes.append(text_static(t, desc, v, lettre))
        for x in textes:
            t.sd(x)["name"] = ""
            t.elem(x)["m_RuleIndex"] = -1   # pas la règle du nom
            t.styles.style(t, x, {"font-size": NOM_TAILLE})

    t.elem(hd)["m_Classes"] = []
    t.elem(hd)["m_RuleIndex"] = -1
    t.styles.style(t, hd, {"flex-grow": 1, "flex-direction": "column", "min-width": 0})
    return None


def fond(t, src, parent, couleur, css=None):
    """boîte colorée (plein cadre du parent par défaut), arrondie, transparente au survol"""
    d = boite(t, src, parent)
    t.elem(d)["m_RuleIndex"] = -1
    t.sd(d)["pickingMode"], t.sd(d)["pickingMode_UxmlAttributeFlags"] = 1, 1
    t.styles.style(t, d, {**(css or {"position": "absolute", "left": 0, "top": 0, "width": hp.POURCENT(100),
                                      "height": hp.POURCENT(100)}),
                          "background-color": couleur, "border-radius": BARRE_LARGEUR / 2})
    return d


def comparaison(src, guid, type_arg, valeur, op, chemin):
    """liaison « chemin OP valeur » d'après la liaison BindIntToVisible de FM : fonction guid, valeur du type type_arg
    (octets déjà emballés) ; mêmes arguments pour Int / Long / ULong / Double (opérateur, valeur, clé, chemin)"""
    b = copy.deepcopy(src.vs.sd(src.vis)["Binding"])
    vf = b["m_visualFunction"]
    vf["m_target"]["m_guid"] = guid
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].endswith(b"ComparisonOperator]"):
            a[1] = struct.pack("<i", op)
        elif a[0] == b"SI.VisualScripting.Int32VisualArg":
            a[0], a[1] = type_arg, valeur
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            c = chemin.encode()
            a[1] = b"\x01" + _enc_varint(len(c)) + c
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return b


def visible_texte(t, src, parent, valeur, egal):
    """SIVisible « Description == valeur » (egal) ou « != valeur » (fonction FM BindStringToVisible 240779c1)"""
    b = copy.deepcopy(src.sb.sd(src.svis)["Binding"])
    args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0] == b"SI.VisualScripting.StringVisualArg":
            v = valeur.encode()
            a[1] = b"\x01" + _enc_varint(len(v)) + v
        elif a[0] == b"SI.VisualScripting.BooleanVisualArg":
            a[1] = b"\x00" if egal else b"\x01"
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            c = DESCRIPTION.encode()
            a[1] = b"\x01" + _enc_varint(len(c)) + c
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    v = new_visible(t, src.sb, src.svis, parent, None, "", b)
    t.elem(v)["m_RuleIndex"] = -1
    t.elem(v)["m_Classes"] = []
    return v


def arg_chemin(chemin):
    """octets d'arguments d'une fonction visuelle à un seul argument « chemin de donnée »"""
    nom = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"
    c = chemin.encode()
    corps = bytes([len(nom)]) + nom + bytes([1, len(c)]) + c
    return list(bytes([1]) + len(corps).to_bytes(4, "little") + corps)


# ---------- grande tuile de la Vue d'ensemble ----------
def trait(t, src, parent, vertical):
    b = boite(t, src, parent)
    t.elem(b)["m_RuleIndex"] = -1
    t.styles.style(t, b, {"width": 1, "margin-left": 12, "margin-right": 12, "background-color": TRAIT,
                          "flex-shrink": 0} if vertical else
                   {"height": 1, "margin-top": 8, "margin-bottom": 8, "background-color": TRAIT, "flex-shrink": 0})
    return b


def bouton_affectations(t, src, ligne):
    """bouton « Affectations des entraîneurs » en tête de la ligne des boutons, préparateurs seulement ; clic = écran
    ouvert par la tuile FM CoachAssignments (même événement, paramètre team)"""
    vis = t.clone(src.si_prepa, ligne, 0, src=src.pt)   # SIVisible FM : subgrouptype == préparateurs
    for k in list(t.children(vis)):
        t.remove(k)
    no_styles(t, vis)
    nommer(t, vis, f"{PREFIXE}Affectations-v{VERSION}")
    t.elem(vis)["m_Classes"] = list(AFFECTATIONS_CLASSES[0])
    t.elem(vis)["m_RuleIndex"] = -1
    t.styles.style(t, vis, {"flex-shrink": 0, "flex-direction": "row", "align-items": "center"})
    b = t.clone(src.bouton, vis, src=src.et)
    for k in list(t.children(b)):
        t.remove(k)
    no_styles(t, b)
    t.elem(b)["m_Classes"] = list(AFFECTATIONS_CLASSES[1])
    t.elem(b)["m_RuleIndex"] = -1
    t.styles.style(t, b, {"flex-grow": 0, "top": -AFFECTATIONS_MONTER, "margin-left": AFFECTATIONS_BOUTON_MARGES,
                          "margin-right": AFFECTATIONS_BOUTON_MARGES})
    sd = t.sd(b)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}AffectationsBouton", 1
    sd["InputActionRef"]["m_inputActionAsset"]["m_AssetGUID"] = ""   # pas le raccourci clavier d'« Aujourd'hui »
    sd["InputActionRef"]["m_actionID"] = ""
    if AFFECTATIONS_ICONE:
        # icône seule : bouton sans texte + copie de l'icône FM du titre des préparateurs
        if src.cone is None:
            return "icône des préparateurs introuvable (bloc des postes)"
        vide = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
        sd["BindTextFunction"], sd["BindTextFunction_UxmlAttributeFlags"] = vide, 0
        sd["StaticText"], sd["StaticText_UxmlAttributeFlags"] = "", 0
        sd["text"], sd["text_UxmlAttributeFlags"] = "", 0
        ic = t.clone(src.cone, b, src=src.pt)
        no_styles(t, ic)
        t.elem(ic)["m_Classes"] = [ICONE_PREPA]
        t.elem(ic)["m_RuleIndex"] = -1
        if "pickingMode" in (t.sd(ic) or {}):
            t.sd(ic)["pickingMode"], t.sd(ic)["pickingMode_UxmlAttributeFlags"] = 1, 1   # le clic va au bouton
    elif AFFECTATIONS_COURT:
        # texte fixe : bouton sans texte + SIText enfant en texte fixe (TextBinding m_kind 0, comme les paliers de
        # notes_installations, validés en jeu). v22 (StaticText) et v23 (StaticText + text) = bouton vide en jeu.
        vide = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
        sd["BindTextFunction"], sd["BindTextFunction_UxmlAttributeFlags"] = vide, 0
        sd["StaticText"], sd["StaticText_UxmlAttributeFlags"] = "", 0
        sd["text"], sd["text_UxmlAttributeFlags"] = "", 0
        modele = first(src.pt, lambda r: typ(src.pt, r) == "SIText")   # un texte du bloc des postes FM
        if modele is None:
            return "texte FM introuvable (bloc des postes)"
        txt = t.clone(modele, b, src=src.pt)
        for k in list(t.children(txt)):
            t.remove(k)
        no_styles(t, txt)
        t.elem(txt)["m_Classes"] = ["label-md", "primary-text-colour"]
        t.elem(txt)["m_RuleIndex"] = -1
        ts = t.sd(txt)
        ts["name"], ts["name_UxmlAttributeFlags"] = "", 0
        ts["text"], ts["text_UxmlAttributeFlags"] = AFFECTATIONS_COURT, 1
        ts["DebugDisplay"] = AFFECTATIONS_COURT
        ts["pickingMode"], ts["pickingMode_UxmlAttributeFlags"] = 1, 1   # le clic va au bouton
        ts["BindTextFunction"] = copy.deepcopy(vide)
        ts["TextBinding"] = copy.deepcopy(ts["TextBinding"])
        ts["TextBinding"]["m_kind"] = 0
        ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    else:
        f = sd["BindTextFunction"]
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        n = 0
        for a in args:
            if a[0].endswith(b"TranslationID]"):
                dbg = b"UIPicker Coach Assignments"
                a[1] = struct.pack("<i", AFFECTATIONS_TEXTE) + b"\x01" + _enc_varint(len(dbg)) + dbg
                n += 1
        if not n:
            return "texte du bouton FM introuvable"
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["Events"]["m_bytes"] = evenement_ecran(AFFECTATIONS_ECRAN, [("team", "team")])
    return None


def boutons_en_haut(t, src, p, marge, affectations=False):
    """boutons du bloc des postes p (inclusion ClubStaffActionsButtons, en bas) -> en haut à droite du bloc
    (position absolue, à marge px des bords : v15 dans la ligne du titre = pas collés au bord droit)"""
    ancien = next((r for r in t.walk(p) if t.elem(r).get("m_TemplateAlias") == BOUTONS), None)
    if ancien is None:
        return "boutons introuvables"
    bt, mt = src.bt, src.mt
    ligne = t.clone(src.boutons, p, src=bt)
    t.styles.copy_from(bt.styles, t, ligne)
    copy_usings(t, bt, src.boutons)
    nommer(t, ligne, NOM_BOUTONS)
    haut, droite = marge
    if affectations:
        haut -= BOUTONS_MONTER_AFFECTATIONS
    t.styles.style(t, ligne, {"position": "absolute", "top": haut, "right": droite, "align-items": "center"})
    winc = next(r for r in t.walk(ligne) if t.elem(r).get("m_TemplateAlias") == MENU_DIRIGEANTS)
    # menu « Demande aux dirigeants » recopié en ligne, son menu FM avec texte remplacé par celui sans texte
    vars_menu = t.clone(src.menu_vars, t.parent[winc], t.children(t.parent[winc]).index(winc), src=mt)
    t.styles.copy_from(mt.styles, t, vars_menu)
    dinc = next(r for r in t.walk(vars_menu) if t.elem(r).get("m_TemplateAlias"))
    surcharges = []
    for o in t.elem(winc)["m_SerializedDataOverride"]:   # celles du bloc des boutons (texte, icône, actions)
        nouveau = MENU_IDS.get(o["m_ElementId"])
        if nouveau is None:
            continue   # le texte : le menu sans texte n'en a pas
        ref = copy.deepcopy(t.refs[o["m_SerializedData"]["rid"]])
        ref["rid"] = t.new_rid()
        ref["data"]["uxmlAssetId"] = nouveau
        t.refs[ref["rid"]] = ref
        t.tt["references"]["RefIds"].append(ref)
        surcharges.append({"m_ElementId": nouveau, "m_ElementIdsPath": [nouveau], "m_SerializedData": {"rid": ref["rid"]}})
    for o in t.elem(dinc)["m_SerializedDataOverride"]:   # surcharges du widget FM : remplacées
        t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r["rid"] != o["m_SerializedData"]["rid"]]
        t.refs.pop(o["m_SerializedData"]["rid"], None)
    t.elem(dinc)["m_SerializedDataOverride"] = surcharges
    t.elem(dinc)["m_TemplateAlias"] = MENU_ICONE[0]
    t.sd(dinc)["templateId"] = MENU_ICONE[0]
    add_using(t, {"alias": MENU_ICONE[0], "path": MENU_ICONE[1], "asset": {"m_FileID": 0, "m_PathID": 0}})
    t.remove(winc)
    t.remove(ancien)
    if affectations:
        return bouton_affectations(t, src, ligne)
    return None


def titre_court(t, r):
    """titre FM d'un groupe (« [%number#1] Coaching Staff ») -> nombre (staffsubgroup.Count) + nom court"""
    txt = next((k for k in t.children(r) if typ(t, k) == "SIText"), None)
    if txt is None or t.name(r) not in TITRES_COURTS:
        return
    i = t.children(r).index(txt)
    text_direct(t, txt, r, "staffsubgroup.Count", i)
    nom = text_static(t, txt, r, TITRES_COURTS[t.name(r)], i + 1)
    t.styles.style(t, nom, {"margin-left": TITRE_ECART})
    t.remove(txt)


def arranger_postes(t, src, p, marge, affectations=False):
    """bloc des postes p : réaction des dirigeants (REACTION), boutons en haut à droite (BOUTONS_EN_HAUT)"""
    for r in [r for r in t.walk(p) if t.name(r) in TITRES_GROUPES]:   # même hauteur (TITRE_HAUTEUR_MIN)
        t.styles.style(t, r, {"min-height": TITRE_HAUTEUR_MIN, "align-items": "center"})
        titre_court(t, r)
    reaction = next((r for r in t.walk(p) if t.name(r) == "SIVisible_IsClub"), None)
    if reaction is not None and REACTION == "non":
        t.remove(reaction)
    elif reaction is not None and REACTION == "phrase":
        phrase = next((r for r in t.walk(reaction) if (t.binding(r, "TextBinding") or "").endswith(
            "StaffSubGroupCountFeedbackString")), None)
        if phrase is not None:   # seule la phrase reste (ni trait, ni titre « Réaction des dirigeants »)
            move(t, phrase, reaction)
            for k in list(t.children(reaction)):
                if k != phrase:
                    t.remove(k)
            t.elem(phrase)["m_Classes"] = ["body-sm", "global-text-secondary"]
            t.elem(phrase)["m_RuleIndex"] = -1
            t.styles.style(t, phrase, {"white-space": "normal", "margin-top": 6})
    if BOUTONS_EN_HAUT:
        return boutons_en_haut(t, src, p, marge, affectations)
    return None


def construire_postes(t, src):
    """bloc des postes FM (ClubAllStaffBlock : onglets, sélections…) : même arrangement que dans la grande tuile"""
    p = first(t, lambda r: "siblock-border" in (t.elem(r).get("m_Classes") or []))
    if p is None:
        return ["cadre du bloc introuvable"]
    err = arranger_postes(t, src, p, (BOUTONS_HAUT_BLOC, BOUTONS_MARGE_BLOC), AFFECTATIONS_ONGLET)
    return [err] if err else [f"réaction des dirigeants : {REACTION}, boutons en haut à droite"
                              + (" + « Affectations des entraîneurs » (préparateurs)" if AFFECTATIONS_ONGLET else "")]


def contexte(t, src, parent, g, valeur):
    """cellule d'un groupe : BindingVariables (subgrouptype) > BindingRemapper (staffsubgroup, attributes)"""
    ct = src.ct
    v = t.clone(src.variables, parent, src=ct)
    for k in list(t.children(v)):
        t.remove(k)
    t.sd(v)["name"] = ""
    t.elem(v)["m_Classes"] = []
    t.elem(v)["m_RuleIndex"] = -1
    t.sd(v)["ValueVariables"] = [{"m_name": "subgrouptype", "m_scopeValue": {"m_serializedData": f"Int|{valeur}|"}}]
    t.sd(v)["ReferenceVariables"] = []
    t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0,
                          "flex-direction": "column"})
    remap = t.clone(src.remapper, v, src=ct)
    for k in list(t.children(remap)):
        t.remove(k)
    t.sd(remap)["name"] = ""
    t.elem(remap)["m_RuleIndex"] = -1
    t.sd(remap)["Mappings"] = [
        {"m_serialisedType": 0, "from": "staffsubgroup", "to": {"m_path": f"team.Staff{g}SubGroup"},
         "type": {"id": TYPE_SOUS_GROUPE}},
        {"m_serialisedType": 0, "from": "attributes", "to": {"m_path": f"team.Staff{g}SubGroupComparisonAttributes"},
         "type": {"id": 0}}]
    t.styles.style(t, remap, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "flex-direction": "column"})
    return remap


def construire_grande(t, src, comparaisons):
    """modèle FM inutilisé -> BindingExpect (team, club) > cadre en colonne :
    rangée des postes (3 groupes, hauteur du plus haut) ; trait sur toute la largeur ; rangée des graphiques (le reste
    de la hauteur : les barres des 3 groupes partent de la même ligne et ont la même hauteur)"""
    expect = first(t, lambda r: typ(t, r) == "BindingExpect")
    if expect is None:
        return ["BindingExpect introuvable"]
    for k in list(t.children(expect)):
        t.remove(k)
    pt = src.pt
    att = first(pt, lambda r: typ(pt, r) == "BindingExpect")
    t.sd(expect)["Parameters"] = [copy.deepcopy(p) for p in pt.sd(att)["Parameters"] if p["name"] in ("team", "club")]
    t.sd(expect)["Parameters_UxmlAttributeFlags"] = 1
    t.styles.style(t, expect, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})

    racine = boite(t, src, expect)
    nommer(t, racine, NOM_GRANDE)
    t.elem(racine)["m_Classes"] = list(CADRE)
    t.styles.style(t, racine, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "flex-direction": "column",
                               "padding": 12, "overflow": "hidden"})
    haut = boite(t, src, racine)
    t.styles.style(t, haut, {"flex-direction": "row", "flex-shrink": 1, "min-height": POSTES_MIN})
    trait(t, src, racine, False)
    milieu = None
    if LISTE:   # mini-listes du staff, même découpage en colonnes que les postes et les graphiques ; pas en Large
        hors_large = si_entier(t, src, racine, MODE_AFFICHAGE, 4, 0)
        t.styles.style(t, hors_large, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                                       "min-height": LISTE_ENTETE + LISTE_MIN_LIGNES * LISTE_LIGNE,
                                       "max-height": LISTE_ENTETE + LISTE_MAX_LIGNES * LISTE_LIGNE + 17})
        milieu = boite(t, src, hors_large)
        t.elem(milieu)["m_RuleIndex"] = -1
        t.styles.style(t, milieu, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        trait(t, src, hors_large, False)
    bas = boite(t, src, racine)
    t.styles.style(t, bas, {"flex-direction": "row", "flex-grow": 1, "flex-shrink": 1, "flex-basis": 0,
                            "min-height": COMPARAISON_MIN})
    for i, (g, valeur) in enumerate(SOUS_GROUPES.items()):
        if i:
            trait(t, src, haut, True)
            trait(t, src, bas, True)
            if milieu is not None:
                trait(t, src, milieu, True)
        if milieu is not None:
            mini_liste(t, src, milieu, g)
        # postes : copie du bloc FM, sans son cadre (celui de la grande tuile suffit)
        cellule = contexte(t, src, haut, g, valeur)
        p = t.clone(src.postes, cellule, src=pt)
        t.styles.copy_from(pt.styles, t, p)
        copy_usings(t, pt, src.postes)
        t.elem(p)["m_Classes"] = []
        t.styles.style(t, p, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        err = arranger_postes(t, src, p, (BOUTONS_HAUT_GRANDE, 0), AFFECTATIONS_VUE and g == "Coaching")
        if err:
            return [err]
        # graphique construit par ce script dans ClubStaff<G>TeamComparisonBlock, recopié sans son cadre
        cellule = contexte(t, src, bas, g, valeur)
        c = comparaisons[g]
        r0 = next((r for r in c.walk() if c.name(r) == NOM_RACINE), None)
        if r0 is None:
            return [f"graphique {g} introuvable"]
        k = t.clone(r0, cellule, src=c)
        t.styles.copy_from(c.styles, t, k)
        copy_usings(t, c, r0)
        t.sd(k)["name"] = ""
        t.elem(k)["m_Classes"] = []
        t.styles.style(t, k, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "padding": 0})
    groupes = " | ".join(SOUS_GROUPES)
    if LISTE:
        return [f"une tuile : postes {groupes} / trait / liste du staff ({LISTE_MIN_LIGNES}..{LISTE_MAX_LIGNES} "
                f"lignes) / trait / graphiques ; réaction des dirigeants : {REACTION}"]
    return [f"une tuile : postes {groupes} / trait / graphiques ; réaction des dirigeants : {REACTION}"]


def mini_liste(t, src, parent, g):
    """colonne du groupe g : tableau FM du staff (celui des onglets : « i », clic, défilement) sur le staff du groupe,
    colonnes de notre vue LISTE_VUE"""
    col = boite(t, src, parent)
    t.elem(col)["m_RuleIndex"] = -1
    t.styles.style(t, col, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0,
                            "flex-direction": "column"})
    tt_ = src.tt_
    tab = t.clone(src.tableau, col, src=tt_)
    t.styles.copy_from(tt_.styles, t, tab)
    t.elem(tab)["m_Classes"] = []
    sd = t.sd(tab)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}Liste{g}", 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = f"team.Staff{g}SubGroup.StaffSubGroupPersonList"
    sd["InitFunction"] = copy.deepcopy(src.init_vue)   # notre vue, sans menu des vues
    # v41 (le joueur, 2026-11-26) : largeur des colonnes réglable à la main (AllowColumnResizing 1 ; avant : 0)
    for cle, val in (("ViewDropdownName", ""), ("SortedColumn", ""), ("AllowColumnResizing", 1),
                     ("SelectionCellID", LISTE_SELECTION)):   # v31 : pas de case de sélection
        sd[cle], sd[f"{cle}_UxmlAttributeFlags"] = val, 1   # v32 : sans le drapeau, FM ignore le réglage (vu v31)
    t.styles.style(t, tab, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0,
                            "align-self": "stretch"})


# ---------- colonne de sélection invisible (ui-tablefactories, rappelée par moral_icone_seule) ----------
def _fabriques(env, noms):
    out = {}
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                n = o.peek_name()
            except Exception:
                continue
            if n in noms:
                out[n] = (o, o.read_typetree())
    return out


def actif():
    return os.path.exists(MARKER)


def fabrique_appliquer(env):
    """colonne LISTE_SELECTION (0 px, sans texte) ajoutée à LISTE_FABRIQUE de env (déjà chargé) ; True si changé.
    LISTE à False : retirée"""
    if not LISTE:
        return fabrique_retirer(env)
    f = _fabriques(env, (LISTE_FABRIQUE, SELECTION_SOURCE[0]))
    if len(f) != 2:
        print(f"staff FM24 : fabriques {LISTE_FABRIQUE} / {SELECTION_SOURCE[0]} introuvables")
        return False
    o, tt = f[LISTE_FABRIQUE]
    if any(r["m_id"] == LISTE_SELECTION for r in tt["m_rowData"]):
        return False
    src = next((r for r in f[SELECTION_SOURCE[0]][1]["m_rowData"] if r["m_id"] == SELECTION_SOURCE[1]), None)
    if src is None or len(src["m_valueBindings"]) != 1:
        print(f"staff FM24 : colonne {SELECTION_SOURCE[1]} de {SELECTION_SOURCE[0]} introuvable")
        return False
    sel = copy.deepcopy(src)
    sel["m_id"], sel["m_translationID"] = LISTE_SELECTION, {"GameID": 0}
    sel["m_defaultWidth"] = sel["m_minimumWidth"] = 0.0
    sel["m_allowWidthAutoResizing"] = 0
    sel["m_valueBindings"][0]["to"]["m_path"] = "const.EmptyString"   # pas de texte (kinito v8 : texte = ligne géante)
    tt["m_rowData"].append(sel)
    o.save_typetree(tt)
    print(f"staff FM24 : {LISTE_FABRIQUE} : colonne de sélection invisible ajoutée")
    return True


def fabrique_retirer(env):
    f = _fabriques(env, (LISTE_FABRIQUE,))
    if not f:
        return False
    o, tt = f[LISTE_FABRIQUE]
    reste = [r for r in tt["m_rowData"] if r["m_id"] != LISTE_SELECTION]
    if len(reste) == len(tt["m_rowData"]):
        return False
    tt["m_rowData"] = reste
    o.save_typetree(tt)
    print(f"staff FM24 : {LISTE_FABRIQUE} : colonne de sélection invisible retirée")
    return True


def ecrire_fabriques(retirer=False):
    """bundle actuel des fabriques : notre colonne ajoutée (ou retirée)"""
    env = UnityPy.load(FABRIQUES)
    if not (fabrique_retirer(env) if retirer else fabrique_appliquer(env)):
        return
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(FABRIQUES)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(FABRIQUES, data)


# ---------- vue de la mini-liste (ui-tableviews : LISTE_VUE, seul propriétaire) ----------
def vue_liste(env):
    objs = {}
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                n = o.peek_name()
            except Exception:
                continue
            if n in (LISTE_VUE, LISTE_VUE_SOURCE, LISTE_VUE_ANCIENNE):
                objs[n] = o
    return objs


def rendre_ancienne(objs):
    """v34 : LISTE_VUE_ANCIENNE (vue des tireurs de touches de FM27) rendue d'origine ; message ou None"""
    o = objs.get(LISTE_VUE_ANCIENNE)
    if o is None:
        return None
    tt, orig = o.read_typetree(), hp.original(VUES, o)
    if orig is None or tt == orig:
        return None
    o.save_typetree(orig)
    nb._dirty.add(VUES)   # (les appelants de poser_vue enregistrent si VUES est à écrire)
    print(f"staff FM24 : {LISTE_VUE_ANCIENNE} : remise d'origine (vue des tireurs de touches de FM)")


def colonnes_vue(tt):
    return [c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]]


def poser_vue(retirer=False):
    """LISTE_VUE = vue Contrat du staff réduite à LISTE_COLONNES (retirer : remise d'origine) ; message ou None"""
    env = nb.env_of(VUES)
    objs = vue_liste(env)
    rendre_ancienne(objs)   # v34
    o = objs.get(LISTE_VUE)
    if o is None or LISTE_VUE_SOURCE not in objs:
        return f"vues {LISTE_VUE} / {LISTE_VUE_SOURCE} introuvables"
    tt = o.read_typetree()
    orig = hp.original(VUES, o)
    if retirer:
        if orig is None or tt == orig:
            return None
        o.save_typetree(orig)
        nb._dirty.add(VUES)
        return f"{LISTE_VUE} : remise d'origine"
    import colonnes_reglables as cr   # v41 : colonnes réductibles jusqu'à 16 px (largeur réglable à la main)
    cfg = tt["m_tableView"]["m_tableConfig"]
    if colonnes_vue(tt) == LISTE_COLONNES and cr.minimums_petits(copy.deepcopy(cfg)) == cfg:
        return None
    source = hp.original(VUES, objs[LISTE_VUE_SOURCE]) or objs[LISTE_VUE_SOURCE].read_typetree()
    par_id = {c["m_columnID"]: c for c in source["m_tableView"]["m_tableConfig"]}
    if any(c not in par_id for c in LISTE_COLONNES):
        return f"{LISTE_VUE_SOURCE} : colonnes inattendues (introuvable)"
    tt["m_tableView"] = copy.deepcopy(source["m_tableView"])
    tt["m_tableView"]["m_tableConfig"] = cr.minimums_petits([copy.deepcopy(par_id[c]) for c in LISTE_COLONNES])
    o.save_typetree(tt)
    nb._dirty.add(VUES)
    return f"{LISTE_VUE} : colonnes {', '.join(LISTE_COLONNES)} (mini-liste du staff)"


# ---------- onglets : tuile du tableau du staff = tout l'onglet (v20) ----------
def si_entier(t, src, parent, chemin, op, valeur, index=None):
    """SIVisible FM « chemin OP entier » (BindIntToVisible), vide, sans style"""
    b = make_binding(src.vs.sd(src.vis)["Binding"], op, [chemin], valeur)
    v = new_visible(t, src.vs, src.vis, parent, index, "", b)
    t.elem(v)["m_RuleIndex"] = -1
    return v


def blocs_groupe(t, src, comparaisons, parent, g, valeur, colonne):
    """postes (avec leur cadre et les boutons) + comparaison du groupe g, en colonne (Défaut) ou en rangée"""
    cellule = contexte(t, src, parent, g, valeur)
    t.styles.style(t, cellule, {"flex-direction": "column" if colonne else "row"})
    pt = src.pt
    p = t.clone(src.postes, cellule, src=pt)
    t.styles.copy_from(pt.styles, t, p)
    copy_usings(t, pt, src.postes)
    err = arranger_postes(t, src, p, (BOUTONS_HAUT_BLOC, BOUTONS_MARGE_BLOC), AFFECTATIONS_ONGLET and g == "Coaching")
    if err:
        return err
    c = comparaisons[g]
    r0 = next((r for r in c.walk() if c.name(r) == NOM_RACINE), None)
    if r0 is None:
        return f"graphique {g} introuvable"
    k = t.clone(r0, cellule, src=c)
    t.styles.copy_from(c.styles, t, k)
    copy_usings(t, c, r0)
    t.sd(k)["name"] = ""
    commun = {"flex-shrink": 1, "flex-basis": 0, "min-height": 0, "min-width": 0}
    if colonne:   # même hauteur pour les deux
        t.styles.style(t, p, dict(commun, **{"flex-grow": 1, "margin-bottom": ECART}))
        t.styles.style(t, k, dict(commun, **{"flex-grow": 1}))
    else:
        t.styles.style(t, p, dict(commun, **{"flex-grow": AUTRES_PARTS[0], "margin-right": ECART}))
        t.styles.style(t, k, dict(commun, **{"flex-grow": AUTRES_PARTS[1]}))
    return None


def construire_contrats(t, src, comparaisons):
    """ClubStaffTeamContractBlock (tableau du staff) -> BindingExpect > racine en rangée :
    [par groupe : SIVisible subgrouptype == k > SIVisible Défaut > colonne postes / comparaison]
    [colonne de droite : par groupe : SIVisible subgrouptype == k > SIVisible pas Défaut > rangée postes | comparaison ;
     contenu FM (en-tête + tableau)]"""
    expect = first(t, lambda r: typ(t, r) == "BindingExpect")
    fm = expect and next((r for r in t.children(expect) if typ(t, r).endswith("SIStyleSetter")), None)
    if fm is None:
        return ["structure FM du tableau introuvable (mise à jour du jeu ?)"]
    pt = src.pt
    att = first(pt, lambda r: typ(pt, r) == "BindingExpect")
    params = t.sd(expect)["Parameters"]
    for p in pt.sd(att)["Parameters"]:
        if p["name"] in CONTRATS_DONNEES and p["name"] not in {q["name"] for q in params}:
            q = copy.deepcopy(p)
            q["isOptional"] = 1   # « Tout le staff » ne les reçoit pas
            if p["name"] == "subgrouptype":
                # v27 : vu en jeu, « Tout le staff » montrait postes + comparaison des préparateurs (sans valeur, le
                # numéro valait 0 = préparateurs) -> valeur par défaut hors des groupes : tableau seul, plein écran
                q["defaultValue"] = copy.deepcopy(q["defaultValue"])
                q["defaultValue"]["m_kind"] = 0
                q["defaultValue"]["m_scopeValue"] = {"m_serializedData": f"Int|{SANS_GROUPE}|"}
            params.append(q)
    t.sd(expect)["Parameters_UxmlAttributeFlags"] = 1

    racine = boite(t, src, expect, t.children(expect).index(fm))
    nommer(t, racine, NOM_ONGLET)
    t.elem(racine)["m_RuleIndex"] = -1
    t.styles.style(t, racine, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0,
                               "align-self": "stretch", "flex-direction": "row"})
    droite = boite(t, src, racine)
    t.elem(droite)["m_RuleIndex"] = -1
    t.styles.style(t, droite, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "min-height": 0,
                               "flex-direction": "column"})
    move(t, fm, droite)
    for g, valeur in SOUS_GROUPES.items():
        # Défaut : colonne de gauche (la largeur est sur le SIVisible intérieur : rien quand il est caché)
        a = si_entier(t, src, racine, "subgrouptype", 2, valeur, t.children(racine).index(droite))
        t.styles.style(t, a, {"flex-direction": "row", "flex-shrink": 0})
        b = si_entier(t, src, a, MODE_AFFICHAGE, 2, 0)
        t.styles.style(t, b, {"width": GAUCHE_LARGEUR, "flex-shrink": 0, "flex-direction": "column",
                              "margin-right": ECART})
        err = blocs_groupe(t, src, comparaisons, b, g, valeur, True)
        if err:
            return [err]
        # autres modes : rangée au-dessus du tableau
        a = si_entier(t, src, droite, "subgrouptype", 2, valeur, t.children(droite).index(fm))
        t.styles.style(t, a, {"flex-direction": "column", "flex-shrink": 0})
        b = si_entier(t, src, a, MODE_AFFICHAGE, 4, 0)
        t.styles.style(t, b, {"height": AUTRES_HAUTEUR, "flex-shrink": 0, "flex-direction": "row",
                              "margin-bottom": ECART})
        err = blocs_groupe(t, src, comparaisons, b, g, valeur, False)
        if err:
            return [err]
    return [f"Défaut : postes / comparaison à gauche ({GAUCHE_LARGEUR} px), tableau à droite ; autres modes : "
            f"postes | comparaison au-dessus du tableau ({AUTRES_HAUTEUR} px)"]


# ---------- écran Staff (ClubAllStaffTool) : données des comparaisons dans la Vue d'ensemble ----------
def ensembles_vue(tt, id_ensemble):
    """réglages d'onglet (GridCompositionSets) de l'outil qui pointent vers la grille de la Vue d'ensemble"""
    out = []

    def walk(x):
        if isinstance(x, dict):
            for g in x.get("GridCompositionSets") or []:
                b = g.get("m_gridCompositionSetBindings") or {}
                if (b.get("m_gridCompositionSet") or {}).get("m_PathID") == id_ensemble:
                    out.append(b)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(tt)
    return out


def outil_a_jour(tt, id_ensemble):
    bs = ensembles_vue(tt, id_ensemble)
    return bool(bs) and all(any(d["DescriptionAndMapping"]["DescriptionName"] == "ClubCoachingStaffComparison"
                                for d in b["m_gridElementBindingData"]) for b in bs)


def construire_outil(tt, id_ensemble):
    """chaque comparaison ajoutée à la Vue d'ensemble reçoit, comme dans les onglets : team, attributes (liste du
    groupe), subgrouptype (coaching / recruitment / medical = variables posées par l'outil)"""
    bs = ensembles_vue(tt, id_ensemble)
    if not bs:
        return ["réglages de la Vue d'ensemble introuvables dans l'écran Staff"]
    for b in bs:
        data = b["m_gridElementBindingData"]
        modele = next(d for d in data if d["DescriptionAndMapping"]["DescriptionName"] == "ClubCoachingStaff")
        vis = b["m_gridElementVisiblityFunctions"]
        vis_modele = next(v for v in vis if v["m_itemA"] == "ClubCoachingStaff")
        noms = b.get("m_displayNameBindingMethods") or []
        nom_modele = next((n for n in noms if n["m_itemA"]["DescriptionName"] == "ClubCoachingStaff"), None)
        for g, var in GROUPES.items():
            el = f"Club{g}StaffComparison"
            if any(d["DescriptionAndMapping"]["DescriptionName"] == el for d in data):
                continue
            for nom, chemin in (("attributes", f"Team.Staff{g}SubGroupComparisonAttributes"),
                                ("subgrouptype", var), ("team", "")):
                d = copy.deepcopy(modele)
                d["DescriptionAndMapping"]["DescriptionName"] = el
                d["DescriptionAndMapping"]["MappingName"] = nom
                d["BindingPath"]["m_path"] = chemin
                data.append(d)
                if nom_modele is not None:
                    n = copy.deepcopy(nom_modele)
                    n["m_itemA"]["DescriptionName"] = el
                    n["m_itemA"]["MappingName"] = nom
                    noms.append(n)
            v = copy.deepcopy(vis_modele)
            v["m_itemA"] = el
            vis.append(v)
    return [f"Vue d'ensemble : données des 3 comparaisons ajoutées ({len(bs)} réglage(s) d'onglet)"]


def ensembles(tt, ids):
    """réglages d'onglet (GridCompositionSets) de l'outil qui pointent vers une des grilles ids"""
    return [b for i in ids for b in ensembles_vue(tt, i)]


def outil_onglets_ok(tt, ids):
    bs = ensembles(tt, ids)
    return bool(bs) and all(any(d["DescriptionAndMapping"]["DescriptionName"] == TABLEAU
                                and d["DescriptionAndMapping"]["MappingName"] == "subgrouptype"
                                for d in b["m_gridElementBindingData"]) for b in bs)


def construire_outil_onglets(tt, ids):
    """onglets Préparateurs / Recrutement / Médical : la tuile du tableau reçoit aussi staffsubgroup, subgrouptype,
    club (mêmes liaisons que la tuile des postes : chemins vides = valeurs posées par l'onglet)"""
    bs = ensembles(tt, ids)
    if len(bs) < len(ids):
        return ["réglages des onglets introuvables dans l'écran Staff"]
    for b in bs:
        data = b["m_gridElementBindingData"]
        noms = b.get("m_displayNameBindingMethods") or []
        for nom in CONTRATS_DONNEES:
            if any(d["DescriptionAndMapping"]["DescriptionName"] == TABLEAU
                   and d["DescriptionAndMapping"]["MappingName"] == nom for d in data):
                continue
            modele = next((d for d in data if d["DescriptionAndMapping"]["DescriptionName"] == "ClubCoachingStaff"
                           and d["DescriptionAndMapping"]["MappingName"] == nom), None)
            if modele is None:
                return [f"donnée {nom} des postes introuvable dans l'écran Staff"]
            d = copy.deepcopy(modele)
            d["DescriptionAndMapping"]["DescriptionName"] = TABLEAU
            data.append(d)
            n = next((n for n in noms if n["m_itemA"]["DescriptionName"] == "ClubCoachingStaff"
                      and n["m_itemA"]["MappingName"] == nom), None)
            if n is not None:
                n = copy.deepcopy(n)
                n["m_itemA"]["DescriptionName"] = TABLEAU
                noms.append(n)
    return [f"onglets : tableau du staff + {', '.join(CONTRATS_DONNEES)} ({len(bs)} réglage(s) d'onglet)"]


# ---------- grilles (ui-tileslayouts) ----------
def objets_tuiles(env):
    """{nom: objet} des compositions / ensembles utiles"""
    voulus = {f"{o}GridComposition-{t}" for o in list(ONGLETS) + ["OverviewTab"] for t in TAILLES}
    voulus |= {ENSEMBLE_VUE, ENSEMBLE_ONGLETS, "OverviewTabGridCompositionSet", DESCRIPTION_POSTES}
    voulus |= set(ENSEMBLES_ONGLETS)
    voulus |= {f"Club{g}StaffBlockDescription" for g in GROUPES}
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in voulus:
            out[n] = o
    return out


def tuiles_origine():
    src = backup.backup_path(TUILES)
    env = UnityPy.load(src if os.path.exists(src) else TUILES)
    return {n: o.read_typetree() for n, o in objets_tuiles(env).items()}


def comp(tt, el):
    return next((c for c in tt["m_gridComponents"] if c["m_elementID"] == el), None)


def onglet_voulu(tt, taille, groupe):
    """blocs en haut (hauteur fixe), tableau dessous (hauteur de base FM, sans maximum)"""
    tab = comp(tt, TABLEAU)
    if tab is None or tab["m_location"]["y"] != 0:
        return "disposition inattendue"
    h_tab = tab["m_location"]["height"]
    if DEFAUT_COTE:   # v20 : le tableau seul, sur tout l'onglet (hauteur de base = total FM, sans maximum)
        largeur = max(c["m_location"]["x"] + c["m_location"]["width"] for c in tt["m_gridComponents"])
        hauteur = max(c["m_location"]["y"] + c["m_location"]["height"] for c in tt["m_gridComponents"])
        tt["m_gridComponents"] = [tab]
        tt["m_placementBindings"] = [p for p in tt["m_placementBindings"] if p["m_elementID"] == TABLEAU]
        tab["m_location"].update({"x": 0, "y": 0, "width": largeur, "height": hauteur})
        tab["m_minSize"] = {"x": min(tab["m_minSize"]["x"], largeur), "y": hauteur}
        tab["m_maxSize"] = {"x": 100, "y": 100}
        return None
    # tuiles retirées (base de données staff, affectations des entraîneurs) : la comparaison va jusqu'au bord droit
    tt["m_gridComponents"] = [c for c in tt["m_gridComponents"] if c["m_elementID"] not in TUILES_RETIREES]
    tt["m_placementBindings"] = [p for p in tt["m_placementBindings"] if p["m_elementID"] not in TUILES_RETIREES]
    cmp_ = comp(tt, f"Club{groupe}StaffComparison")
    if cmp_ is None:
        return "disposition inattendue"
    cmp_["m_location"]["width"] = max(cmp_["m_location"]["width"],
                                      tab["m_location"]["x"] + tab["m_location"]["width"] - cmp_["m_location"]["x"])
    autres = [c for c in tt["m_gridComponents"] if c is not tab]
    if any(c["m_location"]["y"] < h_tab for c in autres):
        return "disposition inattendue"
    for c in autres:
        c["m_location"]["y"] -= h_tab
        if c["m_elementID"] in (f"Club{groupe}Staff", f"Club{groupe}StaffComparison"):
            c["m_location"]["height"] = c["m_minSize"]["y"] = HAUT[taille]
        c["m_minSize"]["y"] = c["m_maxSize"]["y"] = c["m_location"]["height"]   # hauteur fixe
        if c["m_elementID"] == f"Club{groupe}Staff":   # bloc normal (FM choisit le modèle selon la largeur)
            c["m_maxSize"]["x"] = min(c["m_maxSize"]["x"], POSTES_LARGEUR_MAX)
    haut = max(c["m_location"]["y"] + c["m_location"]["height"] for c in autres)
    tab["m_location"]["y"] = haut
    tab["m_maxSize"]["y"] = 100
    return None


def vue_voulue(tt, taille):
    """la tuile « préparateurs » devient la grande tuile (toute la largeur, hauteur de base GRANDE_BASE, sans
    maximum) ; les tuiles recrutement / médical sont retirées ; petites tuiles du bas remontées / descendues"""
    groupes = {g: comp(tt, f"Club{g}Staff") for g in GROUPES}
    if None in groupes.values() or any(c["m_location"]["y"] != 0 for c in groupes.values()):
        return "disposition inattendue"
    h_orig = max(c["m_location"]["height"] for c in groupes.values())
    largeur = max(c["m_location"]["x"] + c["m_location"]["width"] for c in groupes.values())
    base = GRANDE_BASE[taille]
    decalage = base - h_orig
    retires = {f"Club{g}Staff" for g in GROUPES if g != "Coaching"}
    tt["m_gridComponents"] = [c for c in tt["m_gridComponents"] if c["m_elementID"] not in retires]
    tt["m_placementBindings"] = [p for p in tt["m_placementBindings"] if p["m_elementID"] not in retires]
    for c in tt["m_gridComponents"]:
        if c["m_location"]["y"] >= h_orig:
            c["m_location"]["y"] += decalage
    for opt in tt["m_optionalSlices"].values():
        if isinstance(opt, list):
            for c in opt:
                if isinstance(c, dict) and "m_location" in c and c["m_location"]["y"] >= h_orig:
                    c["m_location"]["y"] += decalage
    c = groupes["Coaching"]
    c["m_location"].update({"x": 0, "y": 0, "width": largeur, "height": base})
    c["m_minSize"] = {"x": largeur, "y": base}
    c["m_maxSize"] = {"x": 100, "y": 100}   # le modèle (grande tuile) vient de la description, selon la largeur
    return None


def tuiles_voulues(orig):
    """{nom: typetree voulu} calculé depuis les originaux, ou message d'erreur"""
    out = {}
    ens_v = orig.get(ENSEMBLE_VUE)
    if ens_v is None:
        return "ensemble de tuiles de la Vue d'ensemble introuvable"
    # ensemble de la Vue d'ensemble : sans les tuiles recrutement / médical (sinon FM les replace tout seul, vu v11)
    src = backup.backup_path(TUILES)
    par_id = {o.path_id: o for o in UnityPy.load(src if os.path.exists(src) else TUILES).objects}
    retires = {f"Club{g}StaffBlockDescription" for g in GROUPES if g != "Coaching"}
    v = copy.deepcopy(ens_v)
    v["m_gridElementDescriptions"] = [p for p in v["m_gridElementDescriptions"]
                                      if not (p["m_PathID"] in par_id and _nom(par_id[p["m_PathID"]]) in retires)]
    if len(v["m_gridElementDescriptions"]) != len(ens_v["m_gridElementDescriptions"]) - len(retires):
        return "descriptions des tuiles recrutement / médical introuvables dans la Vue d'ensemble"
    out[ENSEMBLE_VUE] = v
    # description de la tuile préparateurs : configurations larges -> grande tuile
    d = orig.get(DESCRIPTION_POSTES)
    if d is None:
        return f"{DESCRIPTION_POSTES} introuvable"
    d = copy.deepcopy(d)
    larges = [c for c in d[CONFIGS] if c["Size"]["x"] >= GRANDE_LARGEUR_MIN]
    if not larges:
        return f"{DESCRIPTION_POSTES} : configurations larges introuvables"
    for c in larges:
        c["AssetRef"]["m_AssetGUID"] = GRANDE_GUID
    largeur_max = max(c["m_location"]["x"] + c["m_location"]["width"]   # largeur de la grande tuile en Large (18)
                      for c in orig["OverviewTabGridComposition-Large"]["m_gridComponents"]
                      if c["m_elementID"] in {f"Club{g}Staff" for g in GROUPES})
    if not any(c["Size"]["x"] >= largeur_max for c in d[CONFIGS]):
        k = copy.deepcopy(larges[0])
        k["Size"] = {"x": largeur_max, "y": 1}
        d[CONFIGS].append(k)
    out[DESCRIPTION_POSTES] = d
    for t in TAILLES:
        n = f"OverviewTabGridComposition-{t}"
        if n not in orig:
            return f"{n} introuvable"
        tt = copy.deepcopy(orig[n])
        err = vue_voulue(tt, t)
        if err:
            return f"{n} : {err}"
        out[n] = tt
        for o in ONGLETS:
            n = f"{o}GridComposition-{t}"
            if n not in orig:
                return f"{n} introuvable"
            tt = copy.deepcopy(orig[n])
            err = onglet_voulu(tt, t, ONGLETS[o])
            if err:
                return f"{n} : {err}"
            out[n] = tt
    return out


def _nom(o):
    try:
        return o.peek_name()
    except Exception:
        return None


def appliquer_tuiles(retirer=False):
    """écrit les grilles voulues (ou d'origine) ; renvoie le nombre d'objets changés"""
    env = UnityPy.load(TUILES)
    actuels = objets_tuiles(env)
    orig = tuiles_origine()
    cible = orig if retirer else tuiles_voulues(orig)
    if isinstance(cible, str):
        print(f"staff FM24 : grilles : {cible} - grilles non touchées")
        return 0
    noms = [n for n in cible if n != "OverviewTabGridCompositionSet"]
    change = 0
    for n in noms:
        o = actuels.get(n)
        if o is None:
            continue
        tt = o.read_typetree()
        champs = ("m_gridComponents", "m_placementBindings", "m_optionalSlices", "m_gridElementDescriptions", CONFIGS)
        if all(tt.get(k) == cible[n].get(k) for k in champs):
            continue
        for k in champs:
            if k in cible[n]:
                tt[k] = cible[n][k]
        o.save_typetree(tt)
        change += 1
    if change:
        data = env.file.save(packer="original")
        if nb.DRY_RUN:
            print(f"(essai à blanc : rien écrit, {os.path.basename(TUILES)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(TUILES, data)
    print(f"staff FM24 : grilles : " + (f"{change} objet(s) " + ("remis d'origine" if retirer else "modifié(s)")
                                        if change else ("déjà d'origine" if retirer else "déjà appliqué")))
    return change


def id_ensemble_vue():
    env = UnityPy.load(TUILES)
    o = objets_tuiles(env).get("OverviewTabGridCompositionSet")
    return o.path_id if o is not None else None


def ids_ensembles_onglets():
    objs = objets_tuiles(UnityPy.load(TUILES))
    return [objs[n].path_id for n in ENSEMBLES_ONGLETS if n in objs]


def outil_modifie(tt, id_vue, ids_onglets):
    return outil_a_jour(tt, id_vue) or any(outil_onglets_ok(tt, [i]) for i in ids_onglets) \
        or outil_equipes(tt) not in ("", None)


# ---------- v35 : rangée des équipes dans la ligne d'onglets ----------
def _extras(tt):
    """réglages ExtraTabRowButtonTemplate de l'écran (override du modèle FigmaBaseToolTabbedTemplate)"""
    out = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("ExtraTabRowButtonTemplate"), dict):
                out.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(tt)
    return out


def outil_equipes(tt):
    """GUID du modèle posé dans la ligne d'onglets ("" = FM) ; None si l'emplacement est introuvable"""
    ex = _extras(tt)
    if not ex:
        return None
    # v36 : champ ignoré par FM sans son drapeau (v35 : rien affiché en jeu)
    e = ex[0]
    if not e.get("ExtraTabRowButtonTemplate_UxmlAttributeFlags"):
        return ""
    if e.get("TabButtonContainerStyle") != EQUIPES_STYLE_LIGNE:
        return "ancienne"   # v35-v38 : style de ligne pas posé
    return e["ExtraTabRowButtonTemplate"]["m_AssetGUID"]


def construire_outil_equipes(tt):
    ex = _extras(tt)
    if not ex:
        return ["emplacement ExtraTabRowButtonTemplate introuvable dans l'écran Staff"]
    for e in ex:
        e["ExtraTabRowButtonTemplate"]["m_AssetGUID"] = EQUIPES_RANGEE_GUID
        e["ExtraTabRowButtonTemplate_UxmlAttributeFlags"] = 1
        # v39 : rangée au bout à droite = style FM fait pour ça (StaffResponsibilitiesCard, PlayerInstructionsCard),
        # ligne d'onglets sans défilement (comme eux ; avec, le contenu ne s'étire pas)
        e["TabButtonContainerStyle"] = EQUIPES_STYLE_LIGNE
        e["TabButtonContainerStyle_UxmlAttributeFlags"] = 1
        e["AddTabButtonsHorizontalScrollView"] = 0
        e["AddTabButtonsHorizontalScrollView_UxmlAttributeFlags"] = 1
    return [f"rangée des équipes ({EQUIPES_RANGEE}) dans la ligne d'onglets"]


def construire_rangee_equipes(t, mx, outil_tt):
    """BindingRoot (team, comme l'écran) > [équipe du club du joueur] > remapper > boutons des équipes du club"""
    # v37 : racine BindingExpect (comme CalendarHeaderSeasonBlock dans le calendrier : lit les données de l'écran) ;
    # v36 gardait le BindingRoot du modèle (attend des données passées à la main) : rien affiché en jeu
    haut = t.tt["m_VisualTree"]["rid"]
    attente = first(mx.ent, lambda r: typ(mx.ent, r) == "BindingExpect")
    racine = None
    if attente is not None:
        for k in list(t.children(haut)):
            t.remove(k)
        racine = t.clone(attente, haut, src=mx.ent)
        no_styles(t, racine)
    params = None

    def walk(x):
        nonlocal params
        if params is None and isinstance(x, dict):
            p = x.get("Parameters")
            if isinstance(p, list) and any(isinstance(q, dict) and q.get("name") == "team" for q in p):
                params = p
                return
            for v in x.values():
                walk(v)
        elif params is None and isinstance(x, list):
            for v in x:
                walk(v)
    walk(outil_tt)
    if racine is None or params is None:
        return ["racine de la rangée / paramètre team de l'écran Staff introuvable"]
    for k in list(t.children(racine)):
        t.remove(k)
    t.sd(racine)["Parameters"] = [copy.deepcopy(q) for q in params if q.get("name") == "team"]
    t.sd(racine)["Parameters_UxmlAttributeFlags"] = 1
    t.elem(racine)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    # v38 : calée tout à droite de l'écran (prend la place libre de la ligne d'onglets, contenu au bout)
    t.styles.style(t, racine, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "justify-content": "flex-end",
                               "margin-right": EQUIPES_DROITE})
    c = ee.rangee(t, mx, racine, None, EQUIPES_REGLAGE, meme_club=True, guid=EQUIPES_BOUTON_GUID)
    if c is None:
        return ["morceaux de FM de la condition « équipe du club » introuvables"]
    for r in t.walk():
        n = t.name(r)
        if n == ee.NOM_RACINE:
            t.sd(r)["name"] = NOM_EQUIPES
        elif n.startswith(ee.PREFIXE):
            t.sd(r)["name"] = PREFIXE + "Equipes" + n[len(ee.PREFIXE):]
    return ["boutons des équipes du club (équipe affichée surlignée), seulement pour le club du joueur"]


def construire_bouton_equipe(t, src_bouton, mx):
    """v38 (le joueur : « même type de bouton que ceux de gauche, en texte ») : ComponentElement (BindingExpect row +
    équipe affichée) > 2 SIVisible (équipe affichée / autre) > copie du bouton d'onglet FM (navigation-tab-default-default,
    classe --active-true / --active-false) ; texte = nom court de l'équipe, clic = Staff de l'équipe"""
    s_onglet = ouvrir(EQUIPES_ONGLET)
    racine = t.tt["m_VisualTree"]["rid"]
    s_rac = src_bouton.tt["m_VisualTree"]["rid"]
    comp = next((r for r in src_bouton.children(s_rac) if typ(src_bouton, r) == "ComponentElement"), None)
    if comp is None or s_onglet is None:
        return ["bouton d'onglet FM / composant du bouton d'équipe introuvable"]
    so = s_onglet[3]
    bouton = first(so, lambda r: typ(so, r) == "SIButton")
    if bouton is None:
        return ["bouton d'onglet FM introuvable"]
    for k in list(t.children(racine)):
        t.remove(k)
    c = t.clone(comp, racine, src=src_bouton)
    for k in list(t.children(c)):
        t.remove(k)
    no_styles(t, c)
    t.elem(c)["m_Classes"] = ["row-direction-normal"]
    t.sd(c)["name"], t.sd(c)["name_UxmlAttributeFlags"] = NOM_BOUTON_EQUIPE, 1
    composants = [x["rid"] for x in t.sd(c).get("m_components") or []]
    attente = next((x for x in composants if "BindingExpect" in t.refs[x]["type"]["class"]), None)
    if attente is None:
        return ["composant BindingExpect du bouton FM introuvable"]
    autres = set(composants) - {attente}
    t.sd(c)["m_components"] = [{"rid": attente}]
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r["rid"] not in autres]
    for x in autres:
        t.refs.pop(x, None)
    params = t.refs[attente]["data"]["Parameters"]
    row = next(p for p in params if p["name"] == "row")
    equipe = copy.deepcopy(row)
    equipe["name"], equipe["type"]["id"], equipe["isOptional"] = ee.PARAM_EQUIPE, ee.TYPE_EQUIPE, 1
    params[:] = [row, equipe]
    for e in (t.elem(r) for r in t.walk(c)):
        for prop in e.get("m_Properties") or []:
            if prop["name"] == "params":
                prop["value"] = f"row:team:False,{ee.PARAM_EQUIPE}:team:True"
    ev = evenement_ecran(ECRAN_STAFF, [("team", "row")])
    for actif, op in ((True, 2), (False, 5)):   # 2 « = », 5 « ≠ »
        b = make_binding(mx.s_vis.sd(mx.vis)["Binding"], op, ["row.UniqueId", f"{ee.PARAM_EQUIPE}.UniqueId"])
        vis = new_visible(t, mx.s_vis, mx.vis, c, None, f"{PREFIXE}Equipe-{'affichee' if actif else 'autre'}", b)
        t.sd(vis)["name_UxmlAttributeFlags"] = 1
        t.styles.style(t, vis, {"margin-left": EQUIPES_ECART, "flex-shrink": 0})
        x = t.clone(bouton, vis, src=so)
        t.styles.copy_from(so.styles, t, x)
        t.elem(x)["m_Classes"] = [k.replace("--active-false", f"--active-{'true' if actif else 'false'}")
                                  for k in (t.elem(x).get("m_Classes") or [])]
        sd = t.sd(x)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}Equipe-bouton", 1
        sd["Events"]["m_bytes"] = list(ev)
        sd["Events_UxmlAttributeFlags"] = 1   # v39 : sans, clic ignoré (v38 vu : boutons morts)
        txt = next((r for r in t.walk(x) if typ(t, r) == "SIText"), None)
        if txt is None:
            return ["texte du bouton d'onglet FM introuvable"]
        tb = t.sd(txt)["TextBinding"]
        tb["m_kind"] = 1
        tb["m_direct"]["Path"]["m_path"] = "row.TeamTypeStringTypeOnly"
        tb["m_visualFunction"]["m_target"]["m_guid"] = ""
        tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
        t.sd(txt)["DebugDisplay"] = "UIPicker team"
    return ["bouton d'équipe = onglet FM en texte (équipe affichée = onglet actif), clic = Staff de l'équipe"]


# ---------- commandes ----------
VISUELS = MODELES + [GRANDE, POSTES, CONTRATS] + ([EQUIPES_RANGEE, EQUIPES_BOUTON] if EQUIPES else [])


def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in VISUELS + [OUTIL]}
    manquants = [m for m, v in actuels.items() if v is None]
    id_vue, ids_onglets = id_ensemble_vue(), ids_ensembles_onglets()
    if manquants or id_vue is None or len(ids_onglets) != len(ENSEMBLES_ONGLETS):
        print("staff FM24 : modèles introuvables (renommés par une mise à jour ?) :",
              ", ".join(manquants or ["OverviewTabGridCompositionSet / grilles des onglets"]))
        return
    blocs_ok = all(any(actuels[m][3].name(r) == NOM_RACINE for r in marques(actuels[m][3])) for m in MODELES)
    blocs_ok = blocs_ok and any(actuels[GRANDE][3].name(r) == NOM_GRANDE for r in marques(actuels[GRANDE][3]))
    blocs_ok = blocs_ok and any(actuels[POSTES][3].name(r) == NOM_BOUTONS for r in marques(actuels[POSTES][3]))
    blocs_ok = blocs_ok and (any(actuels[CONTRATS][3].name(r) == NOM_ONGLET for r in marques(actuels[CONTRATS][3]))
                             if DEFAUT_COTE else not marques(actuels[CONTRATS][3]))
    if EQUIPES:
        blocs_ok = blocs_ok and any(actuels[EQUIPES_RANGEE][3].name(r) == NOM_EQUIPES
                                    for r in marques(actuels[EQUIPES_RANGEE][3]))
        blocs_ok = blocs_ok and any(actuels[EQUIPES_BOUTON][3].name(r) == NOM_BOUTON_EQUIPE
                                    for r in marques(actuels[EQUIPES_BOUTON][3]))
    # écran Staff : Vue d'ensemble d'origine (les versions à 6 tuiles la modifiaient : remise) ; onglets : données
    # ajoutées à la tuile du tableau si DEFAUT_COTE
    outil = actuels[OUTIL][2]
    outil_ok = not outil_a_jour(outil, id_vue) and outil_onglets_ok(outil, ids_onglets) == DEFAUT_COTE
    outil_ok = outil_ok and outil_equipes(outil) == (EQUIPES_RANGEE_GUID if EQUIPES else "")
    if blocs_ok and outil_ok:
        print("staff FM24 : comparaisons : déjà appliqué")
    else:
        ancien = any(marques(actuels[m][3]) for m in VISUELS)
        travail = {m: ouvrir(m, depart_original=True) for m in VISUELS + [OUTIL]}
        if any(marques(travail[m][3]) for m in VISUELS) or outil_modifie(travail[OUTIL][2], id_vue, ids_onglets):
            print("staff FM24 : pas de sauvegarde d'origine propre, ignoré")
            return
        src = Sources()
        if src.manque():
            print("staff FM24 : morceaux de FM introuvables :", ", ".join(src.manque()), "- rien enregistré")
            return
        msgs = []
        for m in MODELES:
            msgs += [f"{m} : {x}" for x in construire(travail[m][3], src)]
        comparaisons = {g: travail[f"ClubStaff{g}TeamComparisonBlock"][3] for g in GROUPES}   # déjà construites
        msgs += [f"Vue d'ensemble ({GRANDE}) : {x}" for x in construire_grande(travail[GRANDE][3], src, comparaisons)]
        msgs += [f"{POSTES} (onglets) : {x}" for x in construire_postes(travail[POSTES][3], src)]
        if DEFAUT_COTE:
            msgs += [f"{CONTRATS} (onglets) : {x}" for x in construire_contrats(travail[CONTRATS][3], src, comparaisons)]
            msgs += [f"{OUTIL} : {x}" for x in construire_outil_onglets(travail[OUTIL][2], ids_onglets)]
        if EQUIPES:
            mx, src_b = ee.Morceaux(), ouvrir(ee.BOUTON_SOURCE)
            if src_b is None or not mx.ok():
                msgs.append("équipes : morceaux de FM (bouton, liste d'équipes) introuvables")
            else:
                msgs += [f"{EQUIPES_BOUTON} : {x}"
                         for x in construire_bouton_equipe(travail[EQUIPES_BOUTON][3], src_b[3], mx)]
                msgs += [f"{EQUIPES_RANGEE} : {x}"
                         for x in construire_rangee_equipes(travail[EQUIPES_RANGEE][3], mx, travail[OUTIL][2])]
                msgs += [f"{OUTIL} : {x}" for x in construire_outil_equipes(travail[OUTIL][2])]
        msgs += ["ancienne version remplacée"] if ancien else []
        for x in msgs:
            print(f"staff FM24 : {x}")
        if any("introuvable" in x for x in msgs):
            print("staff FM24 : rien enregistré")
            return
        for m, (bundle, obj, tt, t) in travail.items():
            if m != OUTIL:
                t.finish()
                t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
        nb.save_all()
        nb._dirty.clear()   # la vue ci-dessous : son bundle seul
    m = poser_vue(retirer=not LISTE)
    print(f"staff FM24 : {m}" if m else "staff FM24 : vue de la mini-liste : déjà appliqué")
    if (m and "introuvable" not in m) or VUES in nb._dirty:   # v34 : ou l'ancienne vue rendue
        nb.save_all()
    ecrire_fabriques()
    appliquer_tuiles()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    id_vue, ids_onglets = id_ensemble_vue(), ids_ensembles_onglets()
    for m in VISUELS + [OUTIL]:
        o = ouvrir(m)
        if o is None:
            continue
        if m == OUTIL:
            if not outil_modifie(o[2], id_vue, ids_onglets):
                continue
        elif not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{m} : remis d'origine")
    m = poser_vue(retirer=True)
    if m:
        print(m)
        fait = "introuvable" not in m or fait
    fait = fait or VUES in nb._dirty   # v34 : l'ancienne vue rendue
    if fait:
        nb.save_all()
    else:
        print("modèles : rien à retirer")
    ecrire_fabriques(retirer=True)
    appliquer_tuiles(retirer=True)


def cmd_etat():
    for m in VISUELS:
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        etat = ("à jour" if any(t.name(r) in (NOM_RACINE, NOM_GRANDE, NOM_BOUTONS, NOM_ONGLET, NOM_EQUIPES,
                                              NOM_BOUTON_EQUIPE) for r in marques(t))
                else "ANCIENNE version")
        print(f"{m} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
    o, id_vue, ids_onglets = ouvrir(OUTIL), id_ensemble_vue(), ids_ensembles_onglets()
    print(f"{OUTIL} : " + ("ANCIENNE version (6 tuiles) : relancer appliquer"
                           if o and id_vue and outil_a_jour(o[2], id_vue) else
                           "données des onglets ajoutées au tableau" if o and outil_onglets_ok(o[2], ids_onglets)
                           else "d'origine"))
    o = vue_liste(UnityPy.load(VUES)).get(LISTE_VUE)
    print(f"{LISTE_VUE} : " + ("introuvable" if o is None else "colonnes de la mini-liste"
                               if colonnes_vue(o.read_typetree()) == LISTE_COLONNES else "d'origine"))
    actuels = {n: o.read_typetree() for n, o in objets_tuiles(UnityPy.load(TUILES)).items()}
    voulu, orig = tuiles_voulues(tuiles_origine()), tuiles_origine()
    for n in sorted(k for k in actuels if "GridComposition-" in k):
        a = actuels[n]["m_gridComponents"]
        etat = ("appliqué" if not isinstance(voulu, str) and a == voulu[n]["m_gridComponents"] else
                "d'origine" if a == orig[n]["m_gridComponents"] else "autre disposition")
        print(f"{n} : {etat}")
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
            print("staff FM24 : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
