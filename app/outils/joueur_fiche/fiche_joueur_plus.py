"""Fiche joueur (gros bloc d'attributs) : Pour / Contre à la place du polygone, entraînement rapide, légende des
postes, logos Hiérarchie / Groupe social.

- colonne de droite à la place du polygone : Pour / Contre du rapport (rapport du staff pour tes joueurs, rapport de
  recrutement sinon), en deux moitiés. Cette colonne n'existe que s'il y a la largeur (pas en Défaut) : FM la gère ;
- en bas d'Infos (sous Suspensions) : note à l'entraînement + pouces Féliciter / Critiquer + roue « Actions »
  (rapport d'entraînement) pour les joueurs de ton club, s'il y a la place (v1.24 ; avant : sous les options
  d'entraînement de hors_defaut.py) ; trait au-dessus des options d'entraînement ;
- légende Clé / Préférables / Priorité sous le terrain des postes ;
- colonne Infos : logos Hiérarchie et Groupe social à droite de Réputation (libellé au survol).

Repérage par contenu (noms FM, chemins de données) : valable après une mise à jour du jeu.
Usage (jeu fermé) : fiche_joueur_plus.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import (Tree, named, make_visible, polygon_visible,  # noqa: E402,F401
                   polygon_button, CLASSE_SI_POLYGONE, Styles, no_styles,
                   LARGEUR_MAX, MOITIE, FIXE, PROPRIETES)
from elements import (src_tree, add_using, copy_usings, first, typ, move, plain, visible_model,  # noqa: E402,F401
                      action_buttons, set_text_binding, appliquer_jobs)
import lancer  # noqa: E402  (retirer : modèles d'origine remis puis tout le skin refait)
import notes_installations as ni  # noqa: E402  (SIVisible de comparaison d'entier : mode d'affichage)
import options  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402  (fiche d'origine sauvegardée : polygone et sa case)
from langue import texte as L, SUFFIXE  # noqa: E402
import fiche_fmguru as guru  # noqa: E402  (réglages du polygone de la vue Guru, repris en Large)

PROPRIETES.update({"height": (131087, 3), "max-height": (131094, 3), "width": (131105, 3)})
for _k, _v in {"position": (131102, 7), "top": (131104, 3), "right": (131103, 3), "margin-left": (131091, 3)}.items():
    PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
POUR_CONTRE_A_LA_PLACE_DU_POLYGONE = True    # fiche joueur : colonne de droite
POLYGONE_POUR_CONTRE = True                  # ... bouton à droite d'« Infos » (Medium / Small) : polygone de FM
                                             # à la place de Pour / Contre, au choix
ENTRAINEMENT_RAPIDE = True                   # Medium / Small : en bas d'Infos ; Large : sous les pieds (sous
                                             # Gardien pour un gardien) : note + pouces + roue « Actions »
                                             # (joueurs de ton club)
LEGENDE_A_GAUCHE = True                      # fiche joueur : légende Clé / Préférables / Priorité sous le terrain
SEPARATEUR_ENTRAINEMENT = True               # fiche joueur : trait au-dessus des options d'entraînement + boutons
LOGOS_DYNAMIQUE = False                      # fiche joueur, Infos : logos Hiérarchie + Groupe social à droite de
                                             # Réputation, l'un sur l'autre (rien si FM n'a pas l'info) ; 2026-11-06,
                                             # le joueur : sortis d'Infos dans tous les modes, ils vont dans la tuile
                                             # État d'esprit (tuile_forme) ; False = retirés (sans_logos)
LOGOS_INFOBULLE = True                       # ... survol d'un logo : son libellé (Joueur très influent...)
LOGOS_MARGE_DROITE = 16                      # ... px à droite des logos (= retrait du texte par rapport au trait)
LOGOS_BAS = 1                                # ... px entre le bas de la ligne et le bas du logo du bas (= bas
                                             # des lettres de « Nationale »)
ICONES_ETAT = False                          # fiche joueur, Infos : icônes condition / forme / fatigue / état
                                             # d'esprit / moral des tableaux, en ligne en haut à droite (essai ;
                                             # 2026-11-01, le joueur : retirées, False = rangée enlevée)
ICONES_MARGE_DROITE = 16                     # ... px à droite (= celle des logos)
ICONE_CASE = 22                              # ... px, hauteur de la case de chaque icône
# ... largeur de la case de chaque icône (ordre d'ICONES) = largeur visible de l'icône + même écart : mesurées en jeu
# (v2, capture 2000 px, 1 px FM = 0,8 px écran) : cœur 10, forme 9, pile 7, smiley 12, moral 11 px écran -> écart
# visible égal ~7 px écran (v3, demande du joueur : « à l'œil »)
ICONE_LARGEURS = [22, 20, 18, 24, 23]
GURU_LARGEUR_ATTRIBUTS = 565                 # option fiche FM Guru : largeur de base des attributs (FM : 860)
GURU_LARGEUR_INFOS = 590                     # ... et de la colonne Infos (FM : 295) ; décide seulement quelles colonnes FM affiche
FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS = 860, 295   # largeurs de FM (remises quand l'option revient au skin)
GURU_LARGEUR_INFOS_MAX = 210                 # ... largeur max des Infos dans cette ligne (FM : 312)
GURU_LARGEUR_LIGNE = 640                     # ... largeur fixe de Infos + polygone (FM : Infos max 312 ; 1 px FM = 1,25 px écran)
POLYGONE_LARGE = True                        # mode Large (v1.41, le joueur : « comme Guru ») : polygone à droite
                                             # d'Infos ; Medium / Small inchangés
POLYGONE_LARGE_LARGEUR = 265                # ... px de la partie polygone (trait compris) ; Large seulement
INFOS_LARGE = 170                            # ... px d'Infos en Large (Medium / Small : 312 de FM, inchangé)
                                             # v2 : Infos + polygone = 465 = largeur d'attributs de Guru (ligne
                                             # 485 avec postes 360 ; ici postes 380) ; v6 : polygone 295 -> 265
                                             # (police Normale : « (tendance) » du gardien débordait)
TAILLE_TEXTE = "settings.TextScaling"        # ... taille du texte de FM : Petit 85, Normal 100, Grand 110, Plus grand 120
# ... par taille de texte (v7) : (opérateur FM, valeur, px de la partie polygone, rayon %) ; opérateurs 0 « < »,
# 2 « = », 4 « > ». Infos = INFOS_LARGE + POLYGONE_LARGE_LARGEUR − largeur (Petit 170, Normal 200, Grand 230,
# Plus grand 260) ; étiquettes plus grosses avec le texte : rayon plus petit
# v8 (v7 en jeu : plus le texte est gros, plus les étiquettes sont coupées : elles grossissent avec le texte, la zone
# doit rester large) : zone presque fixe, c'est le polygone (rayon) qui rapetisse ; Infos 170 / 170 / 165 / 155
TAILLES_TEXTE = [(0, 90, POLYGONE_LARGE_LARGEUR, 19),   # Petit (rayon : Guru 24 ; v1 : étiquettes coupées)
                 (2, 100, 265, 16),
                 (2, 110, 270, 13),
                 (4, 115, 280, 10)]
LARGEUR_ATTRIBUTS_LARGE = 585               # ... taille prévue des attributs (FM 860), comme fiche_fmguru
FICHE_SMALL = True                           # mode Small (essai, 2026-11-12, le joueur) : Pour / Contre sous les
                                             # attributs (défilent), polygone toujours à droite (plus de bouton),
                                             # Rôles / Priorité / Intensité dans le bloc Entraînement d'Infos
SMALL_SEULEMENT = True                       # ... True : Small seulement (settings.AdaptiveScalingLevelIndex, peut-être
                                             # pas lisible dans la fiche) ; False : Medium + Small
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "fiche_joueur_plus.actif")
GROS_BLOC = "PlayerAttributesLargeBlock"
NOM_COLONNE_GAUCHE = "UIPickerColonnePostes"
LARGEUR_POSTES = 380                         # px max de la colonne des postes (taille prévue par FM, réglage 0 de
                                             # l'ExpandableContentElement)
LARGEUR_POSTES_LARGE = 360                   # ... en Large (polygone) : comme fiche_fmguru (v1.41)
NOM_SEPARATEUR = "UIPickerTraitEntrainement"
NOM_POUR_CONTRE = "UIPickerPourContre"
# 2026-11-14 (option fiche_medium_colonne, en-tête en cartes) : Medium = polygone à droite d'Infos (Pour / Contre dans
# l'en-tête, entete_tuile) ; le bouton est caché en Medium (bouton_large_seul) : polygone seul
MEDIUM_POLYGONE = (options.get("fiche_medium_colonne") == "polygone" and options.get("entete_vue") == "tuile"
                   and options.get("fiche_fmguru") != "guru")
VERSION_COLONNE = f"uipicker-colonne-v23{SUFFIXE}" + ("-mpoly2" if MEDIUM_POLYGONE else "") # mpoly2 : cale anti-flash
                                             # (langue : titre « Projets ») changer le numéro refait la colonne à la prochaine application
                                             # (v8 : bouton polygone / Pour-Contre ; v9 : variable avec portée ;
                                             # v10 : aiguillage de FM ; v11 : élément BindingVariables ; v12 :
                                             # inversion marquée posée, polygone plus petit ; v15 : Pour / Contre
                                             # et polygone construits d'office, plus de vide au retour ; v16 : Small =
                                             # polygone seul, sans bouton ; v17 : polygone en haut, Projets /
                                             # Préférés / Nationalités dessous)
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"   # 0 Large, 1 Medium, 2 Small
NOM_PC_BAS = "UIPickerPourContreBas"         # Small : Pour / Contre sous les attributs
VERSION_PC_BAS = "uipicker-pc-bas-v3"   # v2 : bloc « pas encore de rapport » (sans_rapport) ; v3 : rapport de l'adjoint
CLASSE_OPTIONS_HORS_SMALL = "uipicker-options-hors-small-v1"   # options d'entraînement (hors_defaut) cachées en Small
DEFILEMENT_SOURCE = "PlayerRecommendationsMainBlock"   # un SIScrollView de FM (recopié pour les listes Pour / Contre)
OPTIONS_VERTICALES = "PlayerIndividualTrainingOptionsBlock_4x4"   # sa version téléphone : menus l'un sous l'autre
NOM_OPTIONS_INFOS = "UIPickerOptionsInfos"
RESTE = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0}   # moitié de la hauteur qui reste
# Small, sous le polygone : (tuile de FM recopiée, titre FR / EN) ; paramètres des tuiles -> données de la fiche
# (v18, le joueur : Personnes / Clubs préférés retirés ; Projets = le bloc entier de l'onglet Personnel, onglets
# Court terme / Long terme, sans paramètres propres : ses modèles inclus lisent person / team)
# v19 : Projets sans boutons (Court terme puis Long terme), Nationalités collées en bas (dernier champ : en bas) ;
# v20 (le joueur) : Nationalités retirées (déjà dans l'en-tête), Projets seul
BLOCS_SMALL = [("PersonPersonalBlock_PlansTabGroup", ("Projets", "Plans"), ["person", "team"], False)]
REMONTEE_PROJETS = 0                         # px (v19 -24, v20 -20) ; v21 (le joueur) : alignement pas grave,
                                             # polygone / Projets = deux moitiés égales
# Small (le joueur, 2026-11-12) : légende Clé / Préférables en bas d'Infos (collée en bas), éligibilité (formé au
# club / au pays) sous les postes à sa place
NOM_SMALL_GAUCHE = "UIPickerSmallGauche"
VERSION_SMALL_GAUCHE = f"uipicker-small-gauche-v4{SUFFIXE}"   # langue : « Éligibilité » ; v2 : + Suspensions (sorties d'Infos) et langues ;
                                                     # v3 : légende en double (reste de la v1) retirée ;
                                                     # v4 : bloc des postes en double (reste de la v2) retiré
CLASSE_SMALL_HORS = "uipicker-small-gauche-hors"     # conteneur « caché en Small » (défait au changement de version)
ELIGIBILITE = ("PlayerHomegrownStatusTile_2x2", ("Éligibilité", "Eligibility"), ["player"], False)
LANGUES = "PlayerNationalitiesTile_4x2"              # seule sa ligne « Langues : ... » est gardée
FM_LARGEUR_INFOS_MAX = 312                   # largeur max de la colonne Infos chez FM (essai 280 retiré : tous modes)
RAYON_POLYGONE_PC = 26                      # polygone de la colonne, % de sa boîte (FM : 34,8 ; étiquettes
                                             # coupées sur les côtés en Medium / Small)
POLYGONE_PC = "polygonepourcontre"           # variable du bouton (polygonselected reste à FM : en Large, elle
# bascule attributs / polygone), portée par un élément BindingVariables autour de la colonne (comme le rapport du
# recruteur). v8 à v10 : ajoutée aux value-vars du composant de la fiche = jamais lue (colonne vide en jeu)
VARIABLE_POLYGONE_PC = {"m_name": POLYGONE_PC, "m_scopeValue": {"m_serializedData": "Bool|0|"}}
VARIABLES_PC_ANCIENNES = (",{polygonepourcontre}{Bool|0|}",
                          ",{polygonepourcontre}{Bool|0|(Session&#44;Implicit&#44;{}&#44;{uipicker-polygone-pour-contre})}")
VARIABLES_SOURCE = "PlayerRecommendationsMainBlock"   # modèle FM qui a un élément BindingVariables (copié)
CLASSE_BOUTON_PC = "uipicker-bouton-pc"      # conteneur du bouton, dans l'en-tête d'Infos
BOUTON_PC_HAUT = -6                          # px : bouton remonté au-dessus du trait sous « Infos »
VERSION_BOUTONS = "uipicker-boutons-v4"
VERSION_LIGNE = f"uipicker-ligne-v15{SUFFIXE}"    # (langue : « Entraînement ») changer le numéro refait les lignes de boutons (v5 : en bas d'Infos ;
                                             # v6 : titre « Entraînement » avec le plot ; v7 : tes joueurs seulement ;
                                             # v8 : titre pris dans PlayerTraitsFrameList, MAJ de FM du 2026-11-12 ;
                                             # v9 : roue calée à droite, contre le séparateur ; v10 : Small, Rôles /
                                             # Priorité / Intensité dessous ; v11 : menus bridés en largeur ;
                                             # v12 : Small seulement, Medium = sous les pieds ; v13 : bridé (roue
                                             # coupée) ; v14 : vraie cause, ligne sans le style 380 px hérité ;
                                             # v15 : bridage v13 remis, le joueur le veut pour les menus)
CLUB_HUMAIN = "person.Team.IsHuman"          # bloc Entraînement : joueur d'un club géré par toi (comme les options
                                             # d'entraînement de hors_defaut ; person.PlayerTraining existe pour tous)
NOM_OPTIONS_ENTRAINEMENT = "UIPickerEntrainementPerso"   # options d'entraînement posées par hors_defaut.py
MENUS_OPTIONS = ("iprole", "ooprole", "Focus", "Intensity")   # ses 4 menus (Rôle ALB / SLB, Priorité, Intensité)
LARGEUR_MENU_OPTIONS = 200   # px chacun : la rangée ne dépend plus du texte choisi dans les menus
CLASSE_SI_PLACE = "uipicker-si-place"        # ancienne version (masquée par le mod) ; maintenant polygon_visible
LARGEUR_COLONNE = 400                        # largeur max de la colonne Pour / Contre (px)
NOM_CALE_PC = "UIPickerCalePourContre"       # hors Small : la colonne garde cette largeur même vide (chargement)
NOM_CALE_INFOS = "UIPickerCaleInfos"         # hors Small : Infos garde FM_LARGEUR_INFOS_MAX
NOM_ENTRAINEMENT_RAPIDE = "UIPickerEntrainementRapide"
NOM_TRAIT = "UIPickerTraitPourContre"
POUR_CONTRE_SOURCE = "ScoutedProsAndCons"
RAPPORT = "Person.PlayerReportForContextTeam"
# zone Pour / Contre sans rapport (2026-11-07) : phrase « pas de rapport » de FM + son bouton Observer joueur
SANS_RAPPORT_TEXTE = ("CoachScoutReportTile_4x4", "NoScoutedInfoPlaceholder")
SANS_RAPPORT_BOUTON = ("PersonGradeOrScoutDescriptionCell", "scoutingremapper")
CHEMIN_JOUEUR = "person"
NOTE_ENTRAINEMENT = "PlayerTrainingRatingCell"
NOTE_SOURCE = "IndividualTrainingPlayerHeaderContent"   # modèle FM qui inclut déjà la note
BOUTONS_SOURCE = "PlayerReportDevelopmentProgressReportBlock"   # FMActionButton Féliciter / Critiquer de FM
# pouces : bouton de FM -> gabarit icône de Kinito (kinito_rapport_entrainement.GABARITS : pouce vert / rouge)
POUCES = {"PraisePlayerButton": "57e3e0d6ec1bc9047958da07d0f0f9da",
          "WarnPlayerButton": "3d654263b1bd0b94a959cfd0c3010f49"}
ACTIONS_SOURCE, ACTIONS_NOM = "TeamIndividualTrainingBlock", "ActionsDropdown"   # menu « Actions » d'Entraîn. indiv.
ICONE_ROUE = "ui-concepts-cog_small"         # l'engrenage de FM (celui de la v31 de Kinito)
ICONE_TRAITS = "game-concepts-game-concepts-traits"   # icône du titre « Caractéristiques » (recopié pour le nôtre)
ICONE_TITRE = "game-concepts-training-general_small"   # le plot d'entraînement de FM
TRAITS_SOURCE = "PlayerTraitsFrameList"      # depuis la MAJ de FM du 2026-11-12 : titre « Caractéristiques » ici
TABLEAU = "AttributesTableTemplate"          # tableau d'attributs (modèle inclus par la fiche ET l'infobulle du joueur)
NOM_ENTRAINEMENT_LARGE = "UIPickerEntrainementLarge"
VERSION_LARGE = f"uipicker-entrainement-large-v6{SUFFIXE}" # (langue : « Entraînement ») changer le numéro refait le bloc du mode Large (v2 : tes joueurs ;
                                                   # v3 : titre pris dans PlayerTraitsFrameList, MAJ de FM du 2026-11-12 ;
                                                   # v4 : roue calée à droite, contre le séparateur ; v5 : aussi
                                                   # en Medium = hors Small)
MASQUE = "visibilityMask"                    # colonnes affichées de la fiche (lu par la liaison du bouton polygone)
NOM_LOGOS = "UIPickerLogosDynamique"
VERSION_LOGOS = "uipicker-logos-v7"          # changer le numéro refait les logos
# (modèle FM de l'onglet Personnel qui affiche le logo, libellé du logo pour l'infobulle)
LOGOS_SOURCES = [("PersonPersonalBlock_HierarchyFrame", "person.HierarchyInfluenceCategoryString"),
                 ("PersonPersonalBlock_SocialGroup", "person.SocialGroupDetails.LongString")]
NOM_ICONES = "UIPickerIconesEtat"
VERSION_ICONES = "uipicker-icones-v3"        # changer le numéro refait la rangée
ICONE_CLASSES_RETIREES = ("data_display-table-cell", "padding-", "margin-", "height-", "align-self-",
                          "justify-content-", "align-flex-")
PROPRIETES.setdefault("justify-content", (131088, 7))
PROPRIETES.setdefault("align-items", (131073, 7))
# cellules FM des colonnes de tableaux (condition-icon, match-sharpness, fatigue-icon, happiness-icon-only,
# morale-icon-only), dans l'ordre affiché : (modèle, {paramètre: (chemin dans la fiche, type)})
JOUEUR, EQUIPE = 1145176065, 1145176088
ICONES = [("PlayerConditionIconCell", {"binding": ("person", JOUEUR)}),
          ("PlayerSharpnessCell", {"binding": ("person", JOUEUR)}),
          ("PlayerFatigueIconCell", {"binding": ("person.Fatigue", 0)}),
          ("PlayerHappinessCellOnlyIcon", {"binding": ("person", JOUEUR)}),
          ("PlayerMoraleCellNoText", {"binding": ("person", JOUEUR), "team": ("person.Team", EQUIPE)})]
LIENS_BLOCS = {"player": ("person", JOUEUR), "person": ("person", JOUEUR), "team": ("person.Team", EQUIPE)}
OPTION_GURU = "fiche_fmguru"                # option (section FM Guru de la page Features additionnelles)
VERSION_GURU = "uipicker-guru-v12"
NOM_GURU_LIGNE = "UIPickerGuruLigne"
NOM_GURU_POLYGONE = "UIPickerGuruPolygone"
CLASSE_GURU_TABLEAU = "uipicker-guru-tableau"         # tableau d'attributs recopié (mode Large)
CLASSE_GURU_TABLEAU_FM = "uipicker-guru-tableau-fm"   # conteneur du modèle inclus de FM (Medium / Small)
NOM_LIGNE_LARGE = "UIPickerLignePolygone"    # Infos | polygone (mode Large)
OPTION_LARGE = "fiche_large_colonne"         # option (2026-10-30, le joueur) : à droite d'Infos en Large, polygone
LARGE_POUR_CONTRE = options.get(OPTION_LARGE) == "pour_contre"   # ou Pour / Contre + bouton (comme Medium)
# ... v2 (pc1 en jeu, le joueur : « trop zoomé ») : lignes Pour / Contre compactes = copie de la ligne de FM
# (LISTE_PC, déjà en pastilles) dans un modèle de FM cité par rien, plus petite ; polygone réglé comme en mode polygone
LISTE_PC = "data_display-string-list-item-pro-con"
LIGNE_PC_LARGE = "DebugNewsRelatedArticleRow"          # modèle de débogage de FM, cité par aucun modèle (scan 2026-10-30)
GUID_LIGNE_PC_LARGE = "9140bc0802a300740b73918db8c9f9af"
CLASSE_LIGNE_PC_LARGE = "uipicker-ligne-pc-large-v1"   # + empreinte de LISTE_PC (refaite quand elle change)
PASTILLE_PC_LARGE, LOGO_PC_LARGE = 22, 14              # px (ligne de FM du skin : 32 / 20)
TEXTE_PC_LARGE = "body-sm"                             # (FM : body-md)
POLYGONE_PC_DESSOUS = False  # 2026-11-05 (le joueur) : mode polygone, Pour / Contre sous le polygone (moitié basse) ;
                             # 2026-11-07 (le joueur) : retiré, polygone seul au milieu (Pour / Contre = pastilles du haut)
# 2026-11-05 (le joueur) : avec l'en-tête en grande tuile (option entete_vue, le polygone est en haut), en Large :
# Pour / Contre seuls, tout le temps (pas de bouton, pas de polygone) ; prend le pas sur fiche_large_colonne
LARGE_PC_SEULS = options.get("entete_vue") == "tuile"
VERSION_POLYGONE_LARGE = "uipicker-polygone-large-v8" + (f"-pcseul1-{VERSION_COLONNE}" if LARGE_PC_SEULS else
                                                         f"-pc2-{VERSION_COLONNE}" if LARGE_POUR_CONTRE else
                                                         f"-pcb1-{VERSION_COLONNE}" if POLYGONE_PC_DESSOUS else "")   # v7 : polygone par taille de texte ; v8 : zone fixe,
                                                         # rayon qui rapetisse   # v3 : tailles prévues des colonnes comme Guru ; v4 :
                                                         # largeur min de FM sortie de la colonne des attributs ;
                                                         # v5 : trait Infos | polygone pleine hauteur ; v6 :
                                                         # polygone 265 (attributs +30 pour la police Normale)
LIGNE_ATTRIBUT = "AttributesRow"             # ligne d'attribut de FM (modèle des listes du tableau d'attributs)
VERSION_LIGNE_ATTRIBUT = "uipicker-ligne-attribut-v1"
POSTES = "role_selector-large"               # colonne des postes de la fiche (bouton « Comparer » en haut à droite)
VERSION_COMPARER = "uipicker-comparer-v3"
VERSION_PASTILLE_NOTE = "uipicker-pastille-note-v1"
LIGNE_TRAITS = "PlayerTraitsRow12px"         # ligne d'une caractéristique (liste PlayerTraitsList de FM)
VERSION_LIGNE_TRAITS = "uipicker-ligne-traits-v1"   # en jeu : sans effet (gardé, sans danger)
LISTE_TRAITS = "PlayerTraitsFrameList"       # cadre Caractéristiques (titre + liste), modèle inclus dans Infos
VERSION_LISTE_TRAITS = "uipicker-liste-traits-v1"
HAUTEUR_LISTE_TRAITS = 44                    # px : 2 lignes de body-md
PASTILLE_NOTE_MAX = 60                      # px max de la pastille de note à l'entraînement (FM : 42 à 50, « 10,00 »
                                             # passait à la ligne)
CLASSE_MIN_ATTRIBUTS = "player-attributes-block-min-width"   # classe FM (min-width) de la colonne des attributs
CLASSE_SANS_MIN = "uipicker-sans-min-attributs"              # colonne à qui on l'a retirée (defaire la remet)   # v2 : ligne qui ne rétrécit plus (v1 en jeu : Infos
                                                         # écrasée, attributs pas serrés), tailles de Guru, bouton
                                                         # attributs <-> polygone de FM caché
CLASSE_CACHE_BOUTON_LARGE = "uipicker-cache-bouton-large"   # conteneur jamais affiché autour du bouton de FM
CLASSE_TABLEAU_LARGE = "uipicker-tableau-large"         # tableau d'attributs recopié en ligne (Large) ; + empreinte
CLASSE_TABLEAU_LARGE_FM = "uipicker-tableau-large-fm"   # conteneur du modèle inclus de FM (Medium / Small)


# ---------- 1. fiche joueur : Pour / Contre + entraînement rapide ----------
def pros_cons(t):
    col = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
    kids = t.children(col) if col is not None else []
    if col is not None and any(VERSION_COLONNE in (t.elem(r).get("m_Classes") or []) for r in t.walk(col)):
        return []
    redo = any(t.name(r).startswith("UIPicker") for r in kids)
    for r in kids:   # le polygone, ou une version précédente de la colonne : on refait tout
        t.remove(r)
    vis = visible_model(t)
    s = ajout_rapport(t)   # paramètre "report" : le rapport du joueur pour ton club
    if None in (col, vis, s):
        return ["colonne du polygone ou éléments introuvables (le jeu a changé ?), ignoré"]
    middle = first(s, lambda r: s.name(r) == "middle-column")

    cls = [c for c in t.elem(col).get("m_Classes") or []
           if c not in ("align-items-center", "justify-content-center", "align-items-stretch")
           and not c.startswith("uipicker-maxw-")]
    t.elem(col)["m_Classes"] = cls + ["align-items-stretch"]
    t.styles.style(t, col, LARGEUR_MAX(LARGEUR_COLONNE))
    msgs = ["colonne Pour / Contre refaite (nouvelle mise en forme)" if redo else "polygone retiré"]

    if POUR_CONTRE_A_LA_PLACE_DU_POLYGONE:
        # v22 (le joueur, 2026-11-07) : la zone porte Pour / Contre (rapport fait) OU le bloc « pas de rapport »
        # (phrase + bouton Observer joueur de FM) ; les copies Large (pc2 / pcseul) prennent les deux
        box = plain(t, col, None, ["flex-grow-class", "align-self-stretch", VERSION_COLONNE], NOM_POUR_CONTRE)
        t.elem(box)["m_RuleIndex"] = -1
        t.sd(box)["name_UxmlAttributeFlags"] = 1
        # v23 : rapport de l'adjoint (jeunes du centre de formation : HasScoutedInfo faux) = Pour / Contre aussi
        adj, autre = aiguillage_adjoint(t, vis, box, ["flex-grow-class", "align-self-stretch"])
        oui = make_visible(t, vis, autre, None, "report.HasScoutedInfo", "", ["flex-grow-class", "align-self-stretch"])
        msgs += sans_rapport(t, autre, vis)
        for cible in (adj, oui):
            mid = t.clone(middle, cible, src=s)
            no_styles(t, mid)   # sa règle intégrée vient de ScoutedProsAndCons (flex 1 0 0) : remplacée par les classes
            t.elem(mid)["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
            for part in t.children(mid):   # Pour et Contre : même place
                style_partie(t, part)
                t.styles.style(t, part, MOITIE)
        msgs.append("Pour / Contre du rapport à la place du polygone")
        if POLYGONE_POUR_CONTRE:
            msgs += bascule_polygone(t, col, box, vis)

    return msgs


def aiguillage_adjoint(t, vis, parent, classes):
    """comme la tuile Rapport de FM (CoachScoutReportTile_4x4) : d'abord report.UseCoachReportLayout (rapport de
    l'adjoint : tes joueurs, jeunes du centre de formation, où HasScoutedInfo peut être faux), puis seulement
    HasScoutedInfo ; renvoie (conteneur « adjoint », conteneur « sinon »)"""
    adj = make_visible(t, vis, parent, None, "report.UseCoachReportLayout", "", list(classes))
    autre = make_visible(t, vis, parent, None, "report.UseCoachReportLayout", "", list(classes))
    t.sd(autre)["InvertDirectBinding"], t.sd(autre)["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
    for r in (adj, autre):
        t.elem(r)["m_RuleIndex"] = -1
    return adj, autre


def sans_rapport(t, parent, vis, classes=("flex-grow-class", "align-self-stretch")):
    """bloc « pas encore de rapport » (le joueur, 2026-11-07), affiché seulement si report.HasScoutedInfo est faux
    (disparaît dès que le rapport est fait) : phrase de FM (report.NoScoutedInfoString, SIText de la tuile Rapport de
    supervision) + bouton « Observer joueur » de FM (PersonGradeOrScoutDescriptionCell : action ScoutPlayerSpeakTo
    du joueur), centrés dans la zone Pour / Contre"""
    st = src_tree(SANS_RAPPORT_TEXTE[0])
    sb = src_tree(SANS_RAPPORT_BOUTON[0])
    txt = st and first(st, lambda r: st.name(r) == SANS_RAPPORT_TEXTE[1])
    rm = sb and first(sb, lambda r: sb.name(r) == SANS_RAPPORT_BOUTON[1])
    if txt is None or rm is None:
        return ["bloc « pas de rapport » : phrase ou bouton de FM introuvable (le jeu a changé ?), ignoré"]
    bloc = make_visible(t, vis, parent, None, "report.HasScoutedInfo", "",
                        list(classes) + ["column-direction-normal", "align-items-center", "justify-content-center"])
    t.sd(bloc)["InvertDirectBinding"], t.sd(bloc)["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
    t.elem(bloc)["m_RuleIndex"] = -1
    t.styles.style(t, bloc, {"min-width": 0, "min-height": 0, "overflow": "hidden"})
    x = t.clone(txt, bloc, src=st)
    t.styles.copy_from(Styles(*nb.find_vta(SANS_RAPPORT_TEXTE[0])[::2]), t, x)
    t.sd(x)["name"], t.sd(x)["name_UxmlAttributeFlags"] = "", 0
    t.elem(x)["m_Classes"] = [c for c in t.elem(x).get("m_Classes") or [] if c != "sitext-hover-cursor"] \
        + ["margin-bottom-global-gap-regular"]
    b = t.clone(rm, bloc, src=sb)
    no_styles(t, b)
    t.sd(b)["name"], t.sd(b)["name_UxmlAttributeFlags"] = "", 0
    for m in t.sd(b)["Mappings"]:   # binding (la personne de la cellule) -> le joueur de la fiche
        if m["to"]["m_path"].startswith("binding."):
            m["to"]["m_path"] = CHEMIN_JOUEUR + m["to"]["m_path"][len("binding"):]
    for r in t.walk(b):
        if typ(t, r).endswith("SIButton"):
            t.elem(r)["m_Classes"] = ["align-self-center" if c == "align-self-flex-start" else c
                                      for c in t.elem(r).get("m_Classes") or []]
    return ["bloc « pas encore de rapport » (phrase + bouton Observer joueur de FM) tant qu'il n'y a pas de rapport"]


def en_variables(t, rid, variable):
    """transforme le conteneur rid en élément BindingVariables (données copiées de celui du rapport du recruteur)
    qui porte la seule variable donnée ; False si le modèle est introuvable"""
    s = src_tree(VARIABLES_SOURCE)
    m = s and first(s, lambda r: typ(s, r) == "SI.Bindable.BindingVariables")
    if m is None:
        return False
    e = t.elem(rid)
    old = e["m_SerializedData"]["rid"]
    data = copy.deepcopy(s.refs[s.elem(m)["m_SerializedData"]["rid"]])
    data["rid"] = t.new_rid()
    d = data["data"]
    d["uxmlAssetId"] = e["m_Id"]
    d["name"], d["name_UxmlAttributeFlags"] = "", 0
    d["ValueVariables"], d["ReferenceVariables"] = [copy.deepcopy(variable)], []
    d["ValueVariables_UxmlAttributeFlags"] = 1
    t.refs[data["rid"]] = data
    t.tt["references"]["RefIds"].append(data)
    e["m_FullTypeName"] = "SI.Bindable.BindingVariables"
    e["m_SerializedData"] = {"rid": data["rid"]}
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] != old]
    t.refs.pop(old, None)
    return True


def bascule_polygone(t, col, box, vis):
    """bouton en haut de la colonne (case du polygone de FM recopiée ; la colonne n'existe qu'en Medium / Small) :
    coché, le polygone de FM (recopié de la fiche d'origine) à la place de Pour / Contre. Colonne enveloppée dans
    un élément BindingVariables qui porte la variable du bouton : v8 à v10, variable ajoutée aux value-vars du
    composant de la fiche (bouton à droite du titre « Infos ») = jamais lue en jeu (console : rien construit), comme
    dans l'infobulle ; un élément BindingVariables (rapport du recruteur) marche, mais le bouton doit être dedans"""
    for g in [r for r in t.walk() if CLASSE_BOUTON_PC in (t.elem(r).get("m_Classes") or [])]:
        t.remove(g)            # v8 à v10 : bouton dans l'en-tête d'Infos
    for p in [p for r in t.walk() for p in t.elem(r).get("m_Properties") or [] if p["name"] == "value-vars"]:
        for v in VARIABLES_PC_ANCIENNES:
            p["value"] = p["value"].replace(v, "")
    o = ouvrir(GROS_BLOC, depart_original=True)
    src = o and o[3]
    pcol = src and first(src, lambda r: src.name(r) == "AttributeSpiderChartExpanded")
    case = src and first(src, lambda r: typ(src, r).endswith("SICheckBox")
                         and (src.sd(r).get("SelectionBinding") or {}).get("m_path") == "polygonselected")
    if None in (pcol, case):
        return ["bouton polygone / Pour-Contre : éléments introuvables (le jeu a changé ?), ignoré"]
    vp = plain(t, col, t.children(col).index(box), ["flex-grow-class", "align-self-stretch"])
    t.elem(vp)["m_RuleIndex"] = -1
    if not en_variables(t, vp, VARIABLE_POLYGONE_PC):
        t.remove(vp)
        return [f"BindingVariables de {VARIABLES_SOURCE} introuvable (le jeu a changé ?), bouton polygone ignoré"]
    # bouton en haut à droite d'Infos, contre le séparateur (demande du joueur) : il doit rester sous l'élément
    # BindingVariables, donc posé en absolute à gauche de la colonne (right 100 % + marge = moitié de l'écart de FM)
    ligne = plain(t, vp, None, ["row-direction-normal", "margin-right-global-gap-large"])
    t.elem(ligne)["m_RuleIndex"] = -1
    # v14 : remonté (top 0 = il bavait sur le trait sous « Infos » en Small et Large)
    t.styles.style(t, ligne, {"position": "absolute", "top": BOUTON_PC_HAUT, "right": {"unit": 2, "value": 100.0}})
    t.styles.style(t, col, {"overflow": "visible"})      # sinon le bouton, hors de la colonne, serait coupé
    b = t.clone(case, ligne, src=src)
    t.styles.copy_from(src.styles, t, b)
    t.sd(b)["SelectionBinding"]["m_path"] = POLYGONE_PC
    sans = plain(t, vp, None, ["flex-grow-class", "align-self-stretch"])
    t.elem(sans)["m_RuleIndex"] = -1
    move(t, box, sans)
    # MEDIUM_POLYGONE : inversé (polygone tant que la case n'est pas cochée ; bouton caché en Medium = polygone seul)
    t.to_visible(sans, vis, POLYGONE_PC, not MEDIUM_POLYGONE, "")
    avec = plain(t, vp, None, ["flex-grow-class", "align-self-stretch", "align-items-center",
                               "justify-content-center"])
    t.elem(avec)["m_RuleIndex"] = -1
    t.to_visible(avec, vis, POLYGONE_PC, MEDIUM_POLYGONE, "")
    # v11 en jeu : l'inversion ignorée (rien au départ, les deux après le clic) : drapeau « attribut posé » à 1,
    # comme Kinito le fait toujours
    for x in (sans, avec):
        t.sd(x)["InvertDirectBinding_UxmlAttributeFlags"] = 1
        # v15 (le joueur : au retour du polygone, Pour / Contre disparaissaient une fraction de seconde) : contenu
        # construit dès l'ouverture et seulement caché, au lieu d'être refait à chaque bascule
        t.sd(x)["AlwaysInstantiate"], t.sd(x)["AlwaysInstantiate_UxmlAttributeFlags"] = 1, 1
        t.styles.style(t, x, {"min-width": 0, "overflow": "hidden"})   # largeur gardée (colonne plus « hidden »)
    if MEDIUM_POLYGONE:
        polygone_cale(t, src, pcol, avec)
    else:
        polygone(t, src, pcol, avec)
    if not FICHE_SMALL:
        return ["bouton en haut de la colonne Pour / Contre (Medium / Small) : polygone à leur place"]
    # Small (le joueur, 2026-11-12) : Pour / Contre passent sous les attributs, le polygone reste seul, sans bouton
    hors = si_small(t, col, t.children(col).index(vp), False, ["flex-grow-class", "align-self-stretch"])
    move(t, vp, hors)
    seul = si_small(t, col, None, True, ["flex-grow-class", "align-self-stretch", "column-direction-normal"])
    t.styles.style(t, seul, {"min-width": 0, "overflow": "hidden"})
    # v17 (le joueur) : polygone dans la moitié haute, Projets / Personnes et Clubs préférés / Nationalités dessous
    haut = plain(t, seul, None, ["align-self-stretch", "align-items-center", "justify-content-center"])
    t.elem(haut)["m_RuleIndex"] = -1
    t.styles.style(t, haut, {**RESTE, "overflow": "hidden"})
    polygone(t, src, pcol, haut)
    msgs = ["bouton en haut de la colonne Pour / Contre (Medium) : polygone à leur place",
            "Small : polygone en haut de la colonne, sans bouton"]
    err = blocs_small(t, seul)
    return msgs + ([f"{err}, blocs sous le polygone ignorés"] if err else
                   ["Small : Projets (court puis long terme) sous le polygone"])


def sources_blocs(t):
    """(arbre du remapper, remapper, arbre du titre, titre, trait) pour les blocs de FM recopiés, ou None"""
    ns = src_tree(NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == NOTE_ENTRAINEMENT) if ns else None
    tt_titre, titre_fm = titre_traits(t)
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    if None in (note, titre_fm, div_model):
        return None
    return ns, ns.parent[note], tt_titre, titre_fm, div_model


def blocs_small(t, parent):
    """moitié basse de la colonne (Small) : contenus des tuiles de FM de l'onglet Personnel (BLOCS_SMALL), chacun
    sous un petit titre, calés dans la place (le joueur : pas de zone qui défile) ; message d'erreur ou None"""
    srcs = sources_blocs(t)
    if srcs is None:
        return "liaison ou titre introuvable"
    zone = plain(t, parent, None, ["align-self-stretch", "column-direction-normal"])
    t.elem(zone)["m_RuleIndex"] = -1
    # v19 (le joueur) : trait de Projets à la hauteur de celui d'Infos (sous Suspensions) : moitiés égales, remontée
    t.styles.style(t, zone, {**RESTE, "overflow": "hidden", "margin-top": REMONTEE_PROJETS})
    for modele, texte, params, en_bas in BLOCS_SMALL:
        if en_bas:   # Nationalités collées en bas de la colonne
            vide = plain(t, zone, None, ["flex-grow-class"])
            t.elem(vide)["m_RuleIndex"] = -1
        err = bloc_fm(t, zone, srcs, modele, texte, params)
        if err:
            return err
    return None


def bloc_fm(t, parent, srcs, modele, texte, params, garder=None):
    """contenu d'une tuile de FM sous un petit titre + trait (texte None : sans) ; ses paramètres -> données de la
    fiche (LIENS_BLOCS) ; garder(t, copie) retouche la copie ; message d'erreur ou None"""
    ns, remap, tt_titre, titre_fm, div_model = srcs
    bundle, _, stt = nb.find_vta(modele)
    if stt is None:
        return f"{modele} introuvable"
    s = Tree(stt)
    racine = s.children(s.tt["m_VisualTree"]["rid"])[0]
    params = params or [p.get("name") for p in s.sd(racine).get("Parameters") or []]
    bloc = plain(t, parent, None, ["align-self-stretch", "margin-bottom-global-gap-regular"])
    t.elem(bloc)["m_RuleIndex"] = -1
    if texte:
        titre_fixe(t, bloc, tt_titre, titre_fm, L(*texte))
        d = t.clone(div_model, bloc)
        t.sd(d)["name"] = ""
        t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-small"]
    rm = t.clone(remap, bloc, src=ns)   # BindingRemapper vidé : paramètres de la tuile -> fiche
    for k in list(t.children(rm)):
        t.remove(k)
    t.sd(rm)["name"] = ""
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = ["align-self-stretch"], -1
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": p, "to": {"m_path": LIENS_BLOCS[p][0]},
                             "type": {"id": LIENS_BLOCS[p][1]}} for p in params if p in LIENS_BLOCS]
    c = t.clone(racine, rm, src=s)
    copy_usings(t, s, racine)
    t.styles.copy_from(Styles(bundle, stt), t, c)
    for r in list(t.walk(c)):   # cadre de tuile retiré (son contenu gardé), hauteurs de tuile retirées
        e = t.elem(r)
        e["m_Classes"] = [k for k in e.get("m_Classes") or [] if k not in ("height-100-percent", "tile-content")]
    for r in [r for r in t.walk(c) if (t.elem(r).get("m_TemplateAlias") or "").startswith(("tile-", "micro-tile-"))]:
        p = t.parent[r]
        box = plain(t, p, t.children(p).index(r), ["align-self-stretch"])
        t.elem(box)["m_RuleIndex"] = -1
        for k in list(t.children(r)):
            move(t, k, box)
        t.remove(r)
    t.elem(c)["m_Classes"] = ["align-self-stretch"]
    if typ(t, c).endswith("TabGroup"):
        sans_onglets(t, rm, c)
    if garder:
        garder(t, c)
    return None


def sans_onglets(t, parent, groupe):
    """v19 (le joueur) : Projets sans boutons, Court terme puis Long terme l'un sous l'autre ; le texte de chaque
    bouton (traduit par FM) sert de petit titre au-dessus de sa liste"""
    textes = [r for r in t.walk(groupe) if typ(t, r).endswith("SIText")]
    contenu = next((r for r in t.walk(groupe) if typ(t, r).endswith("SwitchElement")), None)
    if contenu is None or len(textes) != len(t.children(contenu)):
        return
    box = plain(t, parent, None, ["align-self-stretch", "column-direction-normal"])
    t.elem(box)["m_RuleIndex"] = -1
    for txt, plan in zip(textes, list(t.children(contenu))):
        move(t, txt, box)
        t.sd(txt)["name"] = ""
        t.elem(txt)["m_Classes"] = ["body-sm", "global-text-secondary", "margin-top-global-gap-small"]
        t.elem(txt)["m_RuleIndex"] = -1
        move(t, plan, box)
    t.remove(groupe)


def titre_fixe(t, parent, tt_titre, titre_fm, texte):
    """petit titre comme « Caractéristiques » (TraitsTitleFrame de FM recopié), sans icône, texte fixe"""
    titre = t.clone(titre_fm, parent, src=tt_titre)
    t.sd(titre)["name"] = ""
    for k in list(t.walk(titre)):
        if k == titre or k not in t.refs:
            continue
        if t.name(k) == "TraitsIcon":
            t.remove(k)
            continue
        if typ(t, k).endswith("SIText"):
            xd = t.sd(k)
            tb = xd["TextBinding"]
            tb["m_kind"] = 0
            tb["m_direct"] = {"Path": {"m_path": ""}, "Nullable": 0}
            tb["m_visualFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                      "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
            xd.update(text=texte, text_UxmlAttributeFlags=1, DebugDisplay=texte)
        t.sd(k)["name"] = ""


def polygone(t, src, pcol, parent):
    """le polygone de FM (fiche d'origine src, colonne pcol) recopié sous parent, un peu plus petit"""
    for k in src.children(pcol):
        c = t.clone(k, parent, src=src)
        t.styles.copy_from(src.styles, t, c)
        copy_usings(t, src, k)
        for r in t.walk(c):               # plus petit : les étiquettes ne sont plus coupées sur les côtés
            if typ(t, r).endswith("FMSpiderChart"):
                t.sd(r)["SpiderChartRadiusPercentage"] = float(RAYON_POLYGONE_PC)


# 2026-11-14 (le joueur, MEDIUM_POLYGONE vu en jeu : « micro flash », un peu trop à gauche) : polygone sans flash comme
# l'en-tête (technique.md : cale fixe SANS liaison qui coupe, graphique INTERIEUR fois plus grand centré dedans, rayon
# en px, affiché une fois person.Age lu) ; décalé à droite (marge droite de FM gardée sur la colonne)
POLY_MEDIUM_CALE = (360, 360)      # px (largeur, hauteur) de la cale (étiquettes : ~±176 px du centre)
POLY_MEDIUM_RAYON_PX = 100.0       # px : rayon affiché (mesuré sur sa capture, ~le même qu'avant)
POLY_MEDIUM_DECALAGE = 8           # px vers la droite
POLY_MEDIUM_INTERIEUR = 2.0


def polygone_cale(t, src, pcol, parent):
    w, h = POLY_MEDIUM_CALE
    gw, gh = round(w * POLY_MEDIUM_INTERIEUR), round(h * POLY_MEDIUM_INTERIEUR)
    fixe = lambda a, b: {"width": a, "min-width": a, "max-width": a, "height": b, "min-height": b,  # noqa: E731
                         "max-height": b, "flex-grow": 0, "flex-shrink": 0}
    cale = plain(t, parent, None, ["column-direction-normal", "align-items-center", "justify-content-center"])
    t.elem(cale)["m_RuleIndex"] = -1
    t.styles.style(t, cale, {**fixe(w, h), "overflow": "hidden", "margin-left": 2 * POLY_MEDIUM_DECALAGE})
    s, vis = ni.visible_model()
    att = ni.new_visible(t, s, vis, cale, None, "", ni.make_binding(s.sd(vis)["Binding"], 4, ["person.Age"], 0),
                         ["column-direction-normal", "align-items-center", "justify-content-center"])
    t.elem(att)["m_RuleIndex"] = -1
    t.styles.style(t, att, fixe(gw, gh))
    polygone(t, src, pcol, att)
    for r in t.walk(att):
        if typ(t, r).endswith("FMSpiderChart"):
            t.sd(r)["SpiderChartRadiusPercentage"] = round(POLY_MEDIUM_RAYON_PX * 100.0 / min(gw, gh), 2)
            t.elem(r)["m_Classes"] = [k for k in t.elem(r)["m_Classes"]
                                      if k not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
            t.styles.style(t, r, fixe(gw, gh))


def si_small(t, parent, index, small, classes):
    """conteneur affiché seulement en Small (small) ou seulement hors Small ; SMALL_SEULEMENT = False : Medium + Small
    (même liaison que le bouton polygone de FM) au lieu de Small"""
    if SMALL_SEULEMENT:
        s, vis = ni.visible_model()   # BindIntToVisible : Small = mode > 1, hors Small = mode < 2
        b = ni.make_binding(s.sd(vis)["Binding"], 4 if small else 0, [MODE_AFFICHAGE], 1 if small else 2)
        v = ni.new_visible(t, s, vis, parent, index, "", b, list(classes))
    else:
        v = plain(t, parent, index, list(classes))
        polygon_visible(t, v, inverse=not small)
    t.elem(v)["m_RuleIndex"] = -1
    return v


def sous(t, root, pred):
    return next((r for r in t.walk(root) if pred(r)), None)


def pour_contre_bas(t):
    """Small : Pour | Contre du rapport sous le tableau d'attributs, côte à côte, chaque liste défile seule (molette)
    dans la place qui reste du bloc (ne bave pas)"""
    old = named(t, NOM_PC_BAS)
    if any(VERSION_PC_BAS in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    for r in old:
        t.remove(r)
    table = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == TABLEAU)
    s = ajout_rapport(t)
    vis = visible_model(t)
    ds = src_tree(DEFILEMENT_SOURCE)
    sv = ds and first(ds, lambda r: typ(ds, r).endswith("SIScrollView"))
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    middle = s and first(s, lambda r: s.name(r) == "middle-column")
    if None in (table, s, vis, sv, div_model, middle):
        return ["tableau d'attributs, Pour / Contre ou défilement introuvable (le jeu a changé ?), Pour / Contre "
                "sous les attributs ignorés"]
    parent = t.parent[table]
    reste = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0}
    t.styles.style(t, table, FIXE)    # le tableau garde sa taille, Pour / Contre prennent ce qui reste
    wrap = si_small(t, parent, t.children(parent).index(table) + 1, True, ["align-self-stretch", VERSION_PC_BAS])
    t.sd(wrap)["name"] = NOM_PC_BAS
    # le tableau grandit aussi (flex-grow-class de FM, gardée pour Medium / Large) : Pour / Contre prennent presque
    # toute la place libre
    t.styles.style(t, wrap, {**reste, "flex-grow": 1000})
    # v3 : rapport de l'adjoint (jeunes du centre de formation) = Pour / Contre aussi (aiguillage_adjoint)
    adj, autre = aiguillage_adjoint(t, vis, wrap, ["align-self-stretch", "column-direction-normal"])
    for r in (adj, autre):
        t.styles.style(t, r, reste)
    box = make_visible(t, vis, autre, None, "report.HasScoutedInfo", "", ["align-self-stretch"])
    t.styles.style(t, box, reste)
    sans = sans_rapport(t, autre, vis, ("align-self-stretch",))
    if len(t.children(autre)) > 1:
        t.styles.style(t, t.children(autre)[-1], reste)
    for cible in (adj, box):
        pc_bas_contenu(t, cible, div_model, middle, s, sv, ds, reste)
    return ["Small : Pour / Contre sous les attributs (deux colonnes qui défilent)" + (" (refait)" if old else "")] \
        + sans


def pc_bas_contenu(t, box, div_model, middle, s, sv, ds, reste):
    """Small : trait + Pour | Contre côte à côte (chaque liste dans un SIScrollView de FM) dans box"""
    d = t.clone(div_model, box)
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-regular"]
    t.styles.style(t, d, FIXE)
    mid = t.clone(middle, box, src=s)
    no_styles(t, mid)
    t.elem(mid)["m_Classes"] = ["row-direction-normal", "align-self-stretch"]
    t.styles.style(t, mid, reste)
    for k, part in enumerate(t.children(mid)):
        style_partie(t, part)
        t.elem(part)["m_Classes"] = ["margin-right-global-gap-large"] if k == 0 else []
        t.styles.style(t, part, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                 "min-height": 0, "overflow": "hidden"})
        liste = next((c for c in t.children(part) if typ(t, c).endswith("StreamedObjectList")), None)
        for c in t.children(part):
            if c != liste:
                t.styles.style(t, c, FIXE)
        if liste is not None:   # la liste dans un SIScrollView de FM, qui prend la hauteur qui reste
            v = t.clone(sv, part, t.children(part).index(liste), src=ds)
            for c in list(t.children(v)):
                t.remove(c)
            t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = "", 0
            t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = ["align-self-stretch"], -1
            t.styles.style(t, v, reste)
            move(t, liste, v)


def small_gauche_infos(t):
    """Small (le joueur, 2026-11-12) : légende Clé / Préférables en bas d'Infos (collée en bas, sous le bloc
    Entraînement) ; sous les postes à sa place : Suspensions (sorties d'Infos, qui débordait avec beaucoup de
    caractéristiques), éligibilité de FM (formé au club / au pays) et langues parlées"""
    old = named(t, NOM_SMALL_GAUCHE)
    if any(VERSION_SMALL_GAUCHE in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    col = first(t, lambda r: t.name(r) == NOM_COLONNE_GAUCHE)
    info = first(t, lambda r: t.name(r) == "InfoBlockFrame")
    for r in old:   # version d'avant : ce qui était caché « hors Small » remis en place, ajouts retirés
        kids = t.children(r)
        if CLASSE_SMALL_HORS in (t.elem(r).get("m_Classes") or []) or (   # (v1 : légende, sans la classe)
                t.parent[r] == col and any(t.elem(k).get("m_TemplateAlias") == "AttributesKey" for k in kids)):
            p = t.parent[r]
            for k in kids:
                move(t, k, p, t.children(p).index(r))
        t.remove(r)
    for r in [r for r in t.children(info) if t.elem(r).get("m_TemplateAlias") == "AttributesKey"] if info else []:
        t.remove(r)   # v2 : la légende recopiée de la v1 était ressortie dans Infos (en double)
    # v3 : Suspensions / éligibilité / langues de la v2 ressorties sous les postes (en double, tous modes)
    for r in list(t.children(col)) if col else []:
        if t.elem(r).get("m_TemplateAlias") not in ("role_selector-large", "AttributesKey") and \
                t.name(r) != NOM_SMALL_GAUCHE:
            t.remove(r)
    key = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "AttributesKey")
    bans = first(t, lambda r: t.name(r) == "PlayerReportBansBlock")
    srcs = sources_blocs(t)
    if None in (key, col, info, bans, srcs) or t.parent[key] != col:
        return ["légende, colonne des postes ou Infos introuvable, Small (légende / éligibilité) ignoré"]
    marque = ["align-self-stretch", VERSION_SMALL_GAUCHE]

    def cacher(elements):   # cachés en Small (même place)
        p = t.parent[elements[0]]
        h = si_small(t, p, t.children(p).index(elements[0]), False, marque + [CLASSE_SMALL_HORS])
        t.sd(h)["name"] = NOM_SMALL_GAUCHE
        for e in elements:
            move(t, e, h)
        return h

    # légende : cachée sous les postes en Small, recopiée en bas d'Infos
    hors = cacher([key])
    bas = si_small(t, info, None, True, marque)
    t.sd(bas)["name"] = NOM_SMALL_GAUCHE
    t.styles.style(t, bas, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "justify-content": "flex-end"})
    k = t.clone(key, bas)
    t.elem(k)["m_Classes"] = ["align-self-centre", "margin-top-global-gap-regular"]
    # sous les postes : Suspensions (recopiées ; cachées dans Infos avec leur trait), éligibilité, langues
    gauche = si_small(t, col, t.children(col).index(hors) + 1, True, marque + ["margin-top-global-gap-regular"])
    t.sd(gauche)["name"] = NOM_SMALL_GAUCHE
    sib = t.children(info)
    trait = sib[sib.index(bans) - 1] if sib.index(bans) > 0 else None
    b = t.clone(bans, gauche)
    t.sd(b)["name"] = ""
    t.elem(b)["m_Classes"] = ["align-self-stretch", "margin-bottom-global-gap-regular"]
    cacher([trait, bans] if trait is not None and (t.elem(trait).get("m_TemplateAlias") or "").startswith(
        "layout-divider") else [bans])
    modele, texte, params, _ = ELIGIBILITE
    err = bloc_fm(t, gauche, srcs, modele, texte, params) or \
        bloc_fm(t, gauche, srcs, LANGUES, None, None, garder=langues_seules)
    return [f"{err}, éligibilité / langues sous les postes ignorées" if err else
            "Small : légende en bas d'Infos ; Suspensions, éligibilité et langues sous les postes"]


def langues_seules(t, c):
    """tuile Nationalités de FM : seule la ligne « Langues : ... » est gardée (drapeaux et nationalités retirés : déjà
    dans l'en-tête de la fiche)"""
    for r in list(t.walk(c)):
        if r in t.refs and (t.name(r) == "nationalities-info-frame" or
                            (t.elem(r).get("m_TemplateAlias") or "").startswith("layout-divider")):
            t.remove(r)


def options_hors_small(t):
    """Small : les options d'entraînement de hors_defaut (sous les attributs) cachées, elles passent dans le bloc
    Entraînement d'Infos ; refait si hors_defaut a reposé ses options"""
    opts = named(t, NOM_OPTIONS_ENTRAINEMENT)
    holder = next((k for o in opts for k in t.children(o)
                   if {CLASSE_SI_POLYGONE, CLASSE_SI_PLACE} & set(t.elem(k).get("m_Classes") or [])), None)
    if holder is None:
        return []
    kids = t.children(holder)
    if any(CLASSE_OPTIONS_HORS_SMALL in (t.elem(k).get("m_Classes") or []) for k in kids):
        return []
    v = si_small(t, holder, 0, False, ["align-self-stretch", CLASSE_OPTIONS_HORS_SMALL])
    for k in kids:
        move(t, k, v)
    return ["Small : options d'entraînement sous les attributs cachées (dans le bloc Entraînement d'Infos)"]


def options_verticales(t, parent):
    """Rôles (avec / sans ballon), Priorité et Intensité de FM l'un sous l'autre (version téléphone du bloc 4x4 de
    FM recopiée, sans le terrain) ; message d'erreur ou None"""
    bundle, _, stt = nb.find_vta(OPTIONS_VERTICALES)
    s = Tree(stt) if stt is not None else None
    racine = s and s.children(s.tt["m_VisualTree"]["rid"])[0]
    if racine is None:
        return f"{OPTIONS_VERTICALES} introuvable"
    c = t.clone(racine, parent, src=s)
    copy_usings(t, s, racine)
    t.styles.copy_from(Styles(bundle, stt), t, c)
    switch = sous(t, c, lambda r: t.name(r) == "PhoneSwitch")
    phone = switch and sous(t, switch, lambda r: t.name(r) == "Phone")
    menus = phone and sous(t, phone, lambda r: t.name(r) == "Dropdowns")
    if menus is None:
        t.remove(c)
        return f"menus de {OPTIONS_VERTICALES} (version téléphone) introuvables"
    frame = t.parent[switch]
    move(t, menus, frame)
    t.remove(switch)
    t.sd(c)["name"] = ""
    t.elem(c)["m_Classes"] = ["align-self-stretch"]
    t.elem(frame)["m_Classes"] = ["align-self-stretch"]
    no_styles(t, frame)
    t.elem(menus)["m_Classes"] = ["align-self-stretch"]
    for k in t.children(menus):   # serrés : ça doit tenir dans la hauteur d'Infos
        t.elem(k)["m_Classes"] = ["align-items-start", "width-100-percent", "margin-top-global-gap-small"]
        # menus bridés à la largeur d'Infos (le joueur : un long rôle SLB débordait), le texte trop long est coupé
        for m in t.walk(k):
            if m != k and m in t.refs and not typ(t, m).endswith("SIText"):
                t.styles.style(t, m, LARGEUR_MAX({"unit": 2, "value": 100.0}))
    return None


def style_partie(t, part):
    """Pour ou Contre : titre au style de la colonne "Infos" (pas de bandeau), puis un trait comme sous "Infos" """
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    t.elem(part)["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
    head = t.children(part)[0]
    t.elem(head)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    text = t.children(head)[1]
    t.elem(text)["m_Classes"] = ["body-sm-strong"] + [c for c in t.elem(text).get("m_Classes") or []
                                                      if c.endswith("string-colour")]
    if div_model is not None:
        d = t.clone(div_model, part, 1)
        t.sd(d)["name"] = ""
        t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-large"]


def ajout_rapport(t):
    """paramètre "report" du bloc Pour / Contre (le rapport du joueur pour ton club) ajouté au BindingRemapper
    racine (celui qui relie human et player) ; renvoie None si un élément manque"""
    remap = None
    for r in t.tt["references"]["RefIds"]:
        maps = (r.get("data") or {}).get("Mappings")
        if isinstance(maps, list) and {"human", "player"} <= {m.get("from") for m in maps}:
            remap = r
    s = src_tree(POUR_CONTRE_SOURCE)
    if None in (remap, s):
        return None
    if not any(m.get("from") == "report" for m in remap["data"]["Mappings"]):
        exp = s.children(s.tt["m_VisualTree"]["rid"])[0]
        rep_type = next((p["type"]["id"] for p in s.sd(exp).get("Parameters") or [] if p.get("name") == "report"), 0)
        remap["data"]["Mappings"].append({"m_serialisedType": 0, "from": "report", "to": {"m_path": RAPPORT},
                                          "type": {"id": rep_type}})
    return s


# ---------- 1 bis. option « fiche FM Guru » (mode Large) ----------
def defaire_tableau(t):
    """tableau d'attributs recopié (v7) retiré, modèle inclus de FM sorti de son conteneur ; True si fait"""
    fait = False
    for x in [x for x in t.walk() if CLASSE_GURU_TABLEAU in (t.elem(x).get("m_Classes") or [])]:
        t.remove(x)
        fait = True
    for g in [x for x in t.walk() if CLASSE_GURU_TABLEAU_FM in (t.elem(x).get("m_Classes") or [])]:
        for k in t.children(g):
            move(t, k, t.parent[g], t.children(t.parent[g]).index(g))
        t.remove(g)
        fait = True
    postes = first(t, lambda r: t.name(r) == NOM_COLONNE_GAUCHE)
    if fait and postes is not None:
        t.styles.style(t, postes, {"flex-shrink": 1})
    return fait


def sans_guru(t):
    """option sur la version du skin : fiche FM Guru retirée sur place (Infos remise, Suspensions sorties de leur
    conteneur, Pour retirés, largeurs de FM), sans refaire tout le skin"""
    rows = named(t, NOM_GURU_LIGNE)
    bans = first(t, lambda r: t.name(r) == "PlayerReportBansBlock")
    g = t.parent.get(bans) if bans is not None else None
    wrapped = g is not None and CLASSE_SI_POLYGONE in (t.elem(g).get("m_Classes") or [])
    tableau = defaire_tableau(t)
    if not rows and not wrapped and not tableau:
        return []
    for row in rows:
        info = next((k for k in t.children(row) if t.name(k) == "InfoBlockFrame"), None)
        if info is not None:
            move(t, info, t.parent[row], t.children(t.parent[row]).index(row))
            t.styles.style(t, info, {"max-width": 312})   # largeur max de FM (v8 la réduit)
        t.remove(row)
    if wrapped:
        frame = t.parent[g]
        sib = t.children(frame)
        nxt = sib[sib.index(g) + 1] if sib.index(g) + 1 < len(sib) else None
        if nxt is not None and CLASSE_SI_POLYGONE in (t.elem(nxt).get("m_Classes") or []):
            t.remove(nxt)
        move(t, bans, frame, t.children(frame).index(g))
        t.remove(g)
    exp = first(t, lambda r: isinstance((t.sd(r).get("Settings") or {}).get("m_settings"), list))
    if exp is not None and len(t.sd(exp)["Settings"]["m_settings"]) == 7:
        sets = t.sd(exp)["Settings"]["m_settings"]
        sets[2]["PredefinedSize"], sets[4]["PredefinedSize"] = FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS
    return ["fiche FM Guru retirée (version du skin)"]


def mode_guru():
    return options.get(OPTION_GURU) == "guru"


def key_left(t):
    """fiche joueur : légende Clé / Préférables / Priorité en bas de la colonne de gauche (sous le terrain des
    postes), ce qui libère le bas de la colonne des attributs pour la ligne d'entraînement"""
    key = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "AttributesKey")
    roles = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "role_selector-large")
    if key is None or roles is None:
        return ["légende ou colonne des postes introuvable, ignoré"]
    p = t.parent[key]
    if t.name(p) == NOM_SMALL_GAUCHE:   # cachée en Small (small_gauche_infos) : déjà dans la colonne
        p = t.parent[p]
    if t.name(p) == NOM_COLONNE_GAUCHE:
        return []
    # la colonne des postes est un modèle inclus : on l'enveloppe (même place parmi les enfants du bloc)
    box = t.parent[roles]
    col = plain(t, box, t.children(box).index(roles), ["column-direction-normal", "align-self-stretch"],
                NOM_COLONNE_GAUCHE)
    move(t, roles, col)
    t.elem(roles)["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
    move(t, key, col)
    t.elem(key)["m_Classes"] = ["align-self-centre", "margin-top-global-gap-regular", "margin-bottom-global-gap-regular"]
    return ["légende sous le terrain des postes (colonne de gauche)"]


def largeur_postes(t):
    """colonne des postes bridée à la largeur prévue par FM (le joueur, 2026-11-12 : la fiche bougeait d'un joueur à
    l'autre ; FM ne fixe pas cette colonne, elle prend la largeur de son contenu, ex. des noms de rôles longs)"""
    col = first(t, lambda r: t.name(r) == NOM_COLONNE_GAUCHE)
    if col is None:
        return []
    e = t.elem(col)
    # v1.41 (le joueur : « gratte sur les postes comme Guru, sans toucher aux autres scaling ») : base 380, peut
    # descendre à LARGEUR_POSTES_LARGE (360) et rétrécit avant tout le reste (shrink fort) : en Large la place manque
    # toujours (attributs serrés) → 360 ; Medium / Small, assez de place → 380. Jamais plus large (jitter)
    mini = LARGEUR_POSTES_LARGE if POLYGONE_LARGE else LARGEUR_POSTES
    fixe = {**LARGEUR_MAX(LARGEUR_POSTES), "min-width": mini, "flex-basis": LARGEUR_POSTES,
            "flex-shrink": 50 if POLYGONE_LARGE else 1}
    if e.get("m_RuleIndex", -1) >= 0 and (PROPRIETES["min-width"][0], "", [(3, {"unit": 1, "value": float(
            mini)})]) in t.styles.values(e["m_RuleIndex"]):
        return []
    t.styles.style(t, col, fixe)
    return [f"colonne des postes bridée à {LARGEUR_POSTES} px (la fiche ne bouge plus d'un joueur à l'autre)"
            + (f", {mini} px quand la place manque (Large)" if mini != LARGEUR_POSTES else "")]


def cale_largeur(t, nom_colonne, nom_cale, largeur):
    """cale de hauteur 0 et min-width largeur en tête de la colonne : elle garde sa largeur même vide, pendant que FM
    la remplit en changeant de joueur (le joueur, 2026-11-12 : effet de chargement, Pour / Contre « tout petit quand ça
    flashe »). v1 dans un conteneur hors Small : sa liaison n'est pas encore lue pendant le chargement, donc cachée
    juste quand il faut ; v2 élément simple, tous modes (remplie, la colonne est déjà à sa largeur max : rien ne
    change hors chargement)"""
    col = first(t, lambda r: t.name(r) == nom_colonne)
    if col is None:
        return False
    old = named(t, nom_cale)
    if any(typ(t, r) == "UnityEngine.UIElements.VisualElement" for r in old):
        return False
    for r in old:
        t.remove(r)
    cale = plain(t, col, 0, [])
    t.elem(cale)["m_RuleIndex"] = -1
    t.sd(cale)["name"] = nom_cale
    t.styles.style(t, cale, {"min-width": largeur, "flex-shrink": 0, "flex-grow": 0})
    return True


def largeur_colonne_pc(t):
    """colonne Pour / Contre (ou polygone) toujours à LARGEUR_COLONNE (elle était étroite le temps du chargement)"""
    if not cale_largeur(t, "AttributeSpiderChartExpanded", NOM_CALE_PC, LARGEUR_COLONNE):
        return []
    return [f"colonne Pour / Contre fixée à {LARGEUR_COLONNE} px (plus d'effet de chargement)"]


def largeur_infos(t):
    """colonne Infos toujours à FM_LARGEUR_INFOS_MAX (le joueur : « une vue fixe qui ne bouge jamais »)"""
    if not cale_largeur(t, "InfoBlockFrame", NOM_CALE_INFOS, FM_LARGEUR_INFOS_MAX):
        return []
    return [f"colonne Infos fixée à {FM_LARGEUR_INFOS_MAX} px"]


def largeur_options(t):
    """menus d'entraînement sous les attributs (hors_defaut.py) à largeur fixe (le joueur, 2026-11-12 : la fiche
    bougeait d'un joueur de son club à l'autre ; FM taille chaque menu sur le texte choisi, ex. « Défenseur central à
    l'aise... » contre « Milieu axial », et la rangée élargissait tout le tableau) ; le texte trop long est coupé"""
    fait = []
    for o in named(t, NOM_OPTIONS_ENTRAINEMENT):
        for k in [r for r in t.walk(o) if t.name(r) in MENUS_OPTIONS]:
            e = t.elem(k)
            if e.get("m_RuleIndex", -1) >= 0 and (PROPRIETES["min-width"][0], "", [(3, {"unit": 1, "value": float(
                    LARGEUR_MENU_OPTIONS)})]) in t.styles.values(e["m_RuleIndex"]):
                continue
            t.styles.style(t, k, {**LARGEUR_MAX(LARGEUR_MENU_OPTIONS), "min-width": LARGEUR_MENU_OPTIONS,
                                  "flex-basis": LARGEUR_MENU_OPTIONS, "flex-grow": 0, "flex-shrink": 0})
            for m in t.walk(k):
                if m != k and m in t.refs and not typ(t, m).endswith("SIText"):
                    t.styles.style(t, m, LARGEUR_MAX({"unit": 2, "value": 100.0}))
            fait.append(k)
    return [f"menus d'entraînement sous les attributs à {LARGEUR_MENU_OPTIONS} px chacun (la fiche ne bouge plus "
            "d'un joueur à l'autre)"] if fait else []


def a_classe(t, r, c):
    return c in (t.elem(r).get("m_Classes") or [])


def defaire_polygone_large(t):
    """ligne Infos | polygone retirée (Infos remise à sa place), tableau recopié retiré, modèle inclus de FM sorti de
    son conteneur ; True si quelque chose était posé"""
    fait = False
    for x in [x for x in t.walk() if a_classe(t, x, CLASSE_TABLEAU_LARGE)]:
        t.remove(x)
        fait = True
    for g in [x for x in t.walk() if a_classe(t, x, CLASSE_TABLEAU_LARGE_FM) or a_classe(t, x, CLASSE_CACHE_BOUTON_LARGE)]:
        for k in t.children(g):
            move(t, k, t.parent[g], t.children(t.parent[g]).index(g))
        t.remove(g)
        fait = True
    for row in named(t, NOM_LIGNE_LARGE):
        info = next((k for k in t.children(row) if t.name(k) == "InfoBlockFrame"), None)
        if info is not None:
            move(t, info, t.parent[row], t.children(t.parent[row]).index(row))
        t.remove(row)
        fait = True
    for c in [x for x in t.walk() if a_classe(t, x, CLASSE_SANS_MIN)]:   # v4 : classe de largeur min remise
        t.elem(c)["m_Classes"] = [k for k in t.elem(c)["m_Classes"] if k != CLASSE_SANS_MIN] + [CLASSE_MIN_ATTRIBUTS]
        fait = True
    sets = reglages_colonnes(t)
    if fait and sets:
        sets[2]["PredefinedSize"], sets[4]["PredefinedSize"] = FM_LARGEUR_ATTRIBUTS, FM_LARGEUR_INFOS
    return fait


def reglages_colonnes(t):
    """réglages des 7 colonnes de l'ExpandableContentElement (postes, trait, attributs, trait, Infos, trait,
    polygone), ou None"""
    exp = first(t, lambda r: isinstance((t.sd(r).get("Settings") or {}).get("m_settings"), list))
    sets = t.sd(exp)["Settings"]["m_settings"] if exp is not None else None
    return sets if sets and len(sets) == 7 else None


def polygone_large(t):
    """v1.41 (le joueur : « arrange la vue de base en Large pour avoir le polygone, comme celle de Guru », « garde
    tout le contenu ») : en Large, FM cache la colonne du polygone (Pour / Contre du skin) ; Infos et le polygone
    passent côte à côte dans la colonne d'Infos (même nombre de colonnes pour l'ExpandableContentElement), comme
    fiche_fmguru. Rien de retiré : Infos garde tout (Suspensions, icônes, logos...).
    Largeurs sans liaison (pas de style par mode) : la ligne a pour largeur son contenu (Infos 312, + la partie
    polygone en Large seulement) et un max de INFOS_LARGE + POLYGONE_LARGE_LARGEUR : en Medium / Small (312) le max ne
    joue pas ; en Large, Infos (seule à rétrécir) descend à INFOS_LARGE.
    Tableau d'attributs : recopié en ligne pour le mode Large, sans « flex-no-shrink » (il rétrécit, comme Guru v7) ;
    le modèle inclus de FM reste pour Medium / Small. La copie porte l'empreinte du modèle : refaite quand il change
    (bloc d'entraînement Large, style médiatique)."""
    bundle, _, stt = nb.find_vta(TABLEAU)
    if stt is None:
        return [f"{TABLEAU} introuvable (le jeu a changé ?), polygone en Large ignoré"]
    empreinte = hashlib.md5(json.dumps(stt, sort_keys=True, default=str).encode()).hexdigest()[:8]
    marque = f"{CLASSE_TABLEAU_LARGE}-{empreinte}"
    rows = named(t, NOM_LIGNE_LARGE)
    if rows and all(a_classe(t, r, VERSION_POLYGONE_LARGE) for r in rows) \
            and any(a_classe(t, x, marque) for x in t.walk()):
        return []
    refait = defaire_polygone_large(t)
    o = ouvrir(GROS_BLOC, depart_original=True)
    src = o and o[3]
    chart = src and first(src, lambda r: typ(src, r).endswith("FMSpiderChart"))
    info = first(t, lambda r: t.name(r) == "InfoBlockFrame")
    # v5 (le joueur : trait manquant à côté du polygone) : un trait ENTRE les colonnes du bloc (pleine hauteur), pas
    # le 1er trouvé (v1 à v4 : un trait de 16 px de haut)
    exp = first(t, lambda r: isinstance((t.sd(r).get("Settings") or {}).get("m_settings"), list))
    vdiv = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-vertical"
                 and t.parent.get(r) == exp)
    tc = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == TABLEAU)
    sets = reglages_colonnes(t)
    if None in (chart, info, vdiv, tc, sets) or polygon_button(t) is None:
        return ["polygone, Infos ou tableau d'attributs introuvable (le jeu a changé ?), polygone en Large ignoré"]

    # Infos | polygone (la partie polygone n'existe qu'en Large : colonne du polygone de FM cachée)
    parent = t.parent[info]
    row = plain(t, parent, t.children(parent).index(info), ["row-direction-normal", "align-self-stretch",
                                                            VERSION_POLYGONE_LARGE], NOM_LIGNE_LARGE)
    t.elem(row)["m_RuleIndex"] = -1
    # v2 : ne rétrécit pas (v1 : elle rétrécissait avant les attributs, Infos écrasée) : ce sont les attributs
    t.styles.style(t, row, {"flex-grow": 0, "flex-shrink": 0, "min-width": 0,
                            "max-width": INFOS_LARGE + POLYGONE_LARGE_LARGEUR})
    move(t, info, row)
    # FM : flex 1 1 0 + max 312 ; dans une ligne qui prend la largeur de son contenu, base 312 (sinon 0)
    t.styles.style(t, info, {"flex-basis": FM_LARGEUR_INFOS_MAX, "flex-shrink": 1, "min-width": 0})
    droite = plain(t, row, None, ["row-direction-normal", "align-self-stretch"])
    t.elem(droite)["m_RuleIndex"] = -1
    t.styles.style(t, droite, {"flex-grow": 0, "flex-shrink": 0})
    polygon_visible(t, droite, inverse=True)
    # v7 (le joueur : Petit parfait ; Normal / Grand / Plus grand, Infos déborde) : une partie polygone par taille de
    # texte (settings.TextScaling), largeur fixe chacune ; la ligne garde son max (Petit) : Infos prend ce que le
    # polygone laisse
    s_vis, vis_m = ni.visible_model()
    if vis_m is None:
        return ["modèle de visibilité de FM introuvable (le jeu a changé ?), polygone en Large ignoré"]
    # option « pour_contre » (le joueur, 2026-10-30) : à la place du polygone, la colonne de Medium recopiée (élément
    # BindingVariables : bouton en haut à droite d'Infos, Pour / Contre, polygone au clic) ; posée par pros_cons
    pc = None
    if LARGE_POUR_CONTRE and not LARGE_PC_SEULS:
        pcol = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
        pc = pcol and next((r for r in t.walk(pcol) if typ(t, r) == "SI.Bindable.BindingVariables"), None)
    msg_pc = []
    if LARGE_POUR_CONTRE and not LARGE_PC_SEULS and pc is None:
        msg_pc = ["mode Large : colonne Pour / Contre introuvable (fonction coupée ?), polygone gardé"]
    # mode polygone (2026-11-05, le joueur) : Pour / Contre (bloc de Medium, sans bouton) sous le polygone ;
    # grande tuile : ce même bloc seul, sur toute la hauteur
    pcb = None
    if pc is None and (POLYGONE_PC_DESSOUS or LARGE_PC_SEULS):
        pcol = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
        pcb = pcol and next((r for r in t.walk(pcol) if t.name(r) == NOM_POUR_CONTRE), None)
        if pcb is None:
            msg_pc = ["mode Large : Pour / Contre introuvables (fonction coupée ?), polygone seul"]
    for op, valeur, largeur, rayon in TAILLES_TEXTE:
        b = ni.make_binding(s_vis.sd(vis_m)["Binding"], op, [TAILLE_TEXTE], valeur)
        taille = ni.new_visible(t, s_vis, vis_m, droite, None, "", b, ["row-direction-normal", "align-self-stretch"])
        t.elem(taille)["m_RuleIndex"] = -1
        t.styles.style(t, taille, {"flex-grow": 0, "flex-shrink": 0, "flex-basis": largeur, "min-width": largeur,
                                   "max-width": largeur, "overflow": "hidden"})
        d = t.clone(vdiv, taille)   # garde ses classes et sa règle (align-self stretch)
        t.sd(d)["name"] = ""
        col = plain(t, taille, None, ["column-direction-normal", "align-items-center", "justify-content-center",
                                      "flex-grow-class"])
        t.elem(col)["m_RuleIndex"] = -1
        t.styles.style(t, col, {"min-width": 0})
        if pc is not None:
            # le bouton est hors de la colonne (à gauche du trait, sur Infos) : rien de coupé
            t.styles.style(t, taille, {"overflow": "visible"})
            t.styles.style(t, col, {"overflow": "visible"})
            c = t.clone(pc, col)
            for r in t.walk(c):
                if t.name(r) == NOM_POUR_CONTRE:
                    t.sd(r)["name"] = ""   # un seul UIPickerPourContre (celui de Medium)
                if typ(t, r).endswith("FMSpiderChart"):   # comme le polygone seul (étiquettes 10 px, anneaux)
                    sd = t.sd(r)
                    sd["SpiderChartRadiusPercentage"] = float(rayon)
                    sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
                    sd["LabelsTemplate"]["m_AssetGUID"] = guru.GUID_ETIQUETTES
                if typ(t, r).endswith("StreamedObjectList"):   # lignes compactes (ligne_pc_large)
                    t.sd(r)["RowTemplate"]["m_AssetGUID"] = GUID_LIGNE_PC_LARGE
                if t.name(r) == "layout-divider-solid-horizontal" or (
                        t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal":
                    t.elem(r)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-small"]
            continue
        cible = col
        if pcb is not None and LARGE_PC_SEULS:
            # grande tuile : Pour puis Contre (lignes compactes) sur toute la hauteur, ni bouton ni polygone
            t.elem(col)["m_Classes"] = ["column-direction-normal", "align-items-stretch", "flex-grow-class"]
            bas = plain(t, col, None, ["align-self-stretch", "column-direction-normal", "align-items-stretch"])
            t.elem(bas)["m_RuleIndex"] = -1
            t.styles.style(t, bas, {**RESTE, "overflow": "hidden"})
            c = t.clone(pcb, bas)
            t.sd(c)["name"] = ""
            for r in t.walk(c):
                if typ(t, r).endswith("StreamedObjectList"):
                    t.sd(r)["RowTemplate"]["m_AssetGUID"] = GUID_LIGNE_PC_LARGE
                if t.name(r) == "layout-divider-solid-horizontal" or (
                        t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal":
                    t.elem(r)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-small"]
            continue
        if pcb is not None:
            # 2026-11-05 (le joueur) : polygone dans la moitié haute, Pour puis Contre (lignes compactes) dessous
            t.elem(col)["m_Classes"] = ["column-direction-normal", "align-items-stretch", "flex-grow-class"]
            cible = plain(t, col, None, ["align-self-stretch", "align-items-center", "justify-content-center"])
            t.elem(cible)["m_RuleIndex"] = -1
            t.styles.style(t, cible, {**RESTE, "overflow": "hidden"})
            bas = plain(t, col, None, ["align-self-stretch", "column-direction-normal", "align-items-stretch"])
            t.elem(bas)["m_RuleIndex"] = -1
            t.styles.style(t, bas, {**RESTE, "overflow": "hidden"})
            c = t.clone(pcb, bas)
            t.sd(c)["name"] = ""
            for r in t.walk(c):
                if typ(t, r).endswith("StreamedObjectList"):
                    t.sd(r)["RowTemplate"]["m_AssetGUID"] = GUID_LIGNE_PC_LARGE
                if t.name(r) == "layout-divider-solid-horizontal" or (
                        t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal":
                    t.elem(r)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-small"]
        poly = t.clone(chart, cible, src=src)   # polygone de la fiche d'origine, réglé comme la vue Guru
        t.styles.copy_from(src.styles, t, poly)
        copy_usings(t, src, chart)
        sd = t.sd(poly)
        sd["SpiderChartRadiusPercentage"] = float(rayon)
        sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
        sd["LabelsTemplate"]["m_AssetGUID"] = guru.GUID_ETIQUETTES

    # bouton de FM à côté d'« Infos » (Large : attributs <-> polygone) : caché, comme la vue Guru ; pas retiré (les
    # conditions polygon_visible copient sa liaison) : dans un conteneur affiché seulement hors Large, lui seulement
    # en Large = jamais
    tete = first(t, lambda r: t.name(r) == "InfoBlockHeaderFrame")
    for k in (list(t.children(tete)) if tete is not None else []):
        if t.find(lambda r: typ(t, r) == "SI.Bindable.SICheckBox", k):
            cache = plain(t, tete, t.children(tete).index(k), [CLASSE_CACHE_BOUTON_LARGE])
            t.elem(cache)["m_RuleIndex"] = -1
            move(t, k, cache)
            polygon_visible(t, cache)

    # tableau d'attributs : modèle de FM pour Medium / Small, copie qui rétrécit pour Large
    s, sst = Tree(stt), Styles(bundle, stt)
    holder = t.parent[tc]
    i = t.children(holder).index(tc)
    # flex-grow comme le modèle inclus (colonne : il remplit la hauteur)
    g = plain(t, holder, i, ["flex-grow-class", "align-self-stretch", CLASSE_TABLEAU_LARGE_FM])
    t.elem(g)["m_RuleIndex"] = -1
    # v4 (v3 en jeu : attributs toujours ~818 px) : la colonne des attributs de FM a la classe
    # player-attributes-block-min-width (min-width, AlwaysAppliedStyleSheet) : elle ne pouvait pas rétrécir.
    # Classe déplacée sur le conteneur Medium / Small (eux gardent leur largeur min), la colonne marquée pour defaire
    col_attr = holder
    while col_attr is not None and not a_classe(t, col_attr, CLASSE_MIN_ATTRIBUTS):
        col_attr = t.parent.get(col_attr)
    if col_attr is not None:
        t.elem(col_attr)["m_Classes"] = [k for k in t.elem(col_attr)["m_Classes"] if k != CLASSE_MIN_ATTRIBUTS] \
            + [CLASSE_SANS_MIN]
        t.elem(g)["m_Classes"].append(CLASSE_MIN_ATTRIBUTS)
    move(t, tc, g)
    polygon_visible(t, g)
    large = plain(t, holder, i + 1, ["flex-grow-class", "align-self-stretch", CLASSE_TABLEAU_LARGE, marque])
    t.elem(large)["m_RuleIndex"] = -1
    t.styles.style(t, large, {"min-width": 0, "overflow": "hidden"})
    polygon_visible(t, large, inverse=True)
    root = s.children(s.tt["m_VisualTree"]["rid"])[0]
    copie = t.clone(root, large, src=s)
    t.styles.copy_from(sst, t, copie)
    used = {s.elem(x).get("m_TemplateAlias") for x in s.walk(root)} - {None, ""}
    for u in s.tt.get("m_Usings") or []:
        if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
            t.tt["m_Usings"].append(dict(u))
    for x in t.walk(copie):
        cls = t.elem(x).get("m_Classes") or []
        if "flex-no-shrink-class" in cls or x == copie or t.name(x) in ("Outfielder", "Goalkeeper"):
            t.elem(x)["m_Classes"] = [c for c in cls if c != "flex-no-shrink-class"]
            t.styles.style(t, x, {"min-width": 0, "flex-shrink": 1, "overflow": "hidden"})
    # v3 (v2 en jeu : attributs toujours pas serrés, polygone hors de l'écran ; le joueur : « inspire-toi de Guru ») :
    # tailles prévues de FM comme fiche_fmguru (attributs 860 -> 585, Infos 295 -> 570 : même somme, donc mêmes
    # colonnes affichées dans chaque mode ; postes gardés à 380)
    sets[2]["PredefinedSize"] = float(LARGEUR_ATTRIBUTS_LARGE)
    sets[4]["PredefinedSize"] = float(FM_LARGEUR_ATTRIBUTS + FM_LARGEUR_INFOS - LARGEUR_ATTRIBUTS_LARGE)
    if pc is not None:
        return [f"mode Large : Pour / Contre à droite d'Infos, bouton pour le polygone (Infos {INFOS_LARGE} px, "
                f"colonne {POLYGONE_LARGE_LARGEUR} px), tableau d'attributs qui rétrécit" + (" (refait)" if refait else "")]
    if LARGE_PC_SEULS and pcb is not None:
        return [f"mode Large (en-tête grande tuile) : Pour / Contre seuls à droite d'Infos, sans bouton ni polygone, "
                "tableau d'attributs qui rétrécit" + (" (refait)" if refait else "")]
    return msg_pc + [f"mode Large : polygone à droite d'Infos (Infos {INFOS_LARGE} px, polygone {POLYGONE_LARGE_LARGEUR} px"
                     + (", Pour / Contre dessous" if pcb is not None else "") + "), "
                     "tableau d'attributs qui rétrécit" + (" (refait)" if refait else "")]


NOM_BOUTON_LARGE_SEUL = "UIPickerBoutonPolygoneLargeSeul-v1"
BOUTON_POLYGONE_MEDIUM = False   # 2026-11-05 (le joueur) : polygone dans l'en-tête en Medium (entete_fiche) -> bouton
                                 # de la colonne Pour / Contre caché en Medium (gardé dans la copie Large pour_contre)


def bouton_large_seul(t):
    """Medium : bouton du polygone (colonne Pour / Contre) dans un SIVisible « mode == 0 » : jamais vu en Medium
    (Pour / Contre restent), toujours là dans la copie Large (faite avant, option pour_contre)"""
    if BOUTON_POLYGONE_MEDIUM or named(t, NOM_BOUTON_LARGE_SEUL):
        return []
    pcol = first(t, lambda r: t.name(r) == "AttributeSpiderChartExpanded")
    vp = pcol and next((r for r in t.walk(pcol) if typ(t, r) == "SI.Bindable.BindingVariables"), None)
    ligne = vp and next((k for k in t.children(vp) if t.find(lambda r: typ(t, r) == "SI.Bindable.SICheckBox", k)),
                        None)
    s_vis, vis_m = ni.visible_model()
    if ligne is None or vis_m is None:
        return ["bouton du polygone (Medium) introuvable : laissé"]
    v = ni.new_visible(t, s_vis, vis_m, vp, t.children(vp).index(ligne), NOM_BOUTON_LARGE_SEUL,
                       ni.equal_binding(s_vis.sd(vis_m)["Binding"], MODE_AFFICHAGE, 0), [])
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.elem(v)["m_RuleIndex"] = -1
    move(t, ligne, v)
    return ["Medium : bouton du polygone caché (polygone dans l'en-tête)"]


def ligne_pc_large(t):
    """option Pour / Contre en Large (v2, le joueur : « trop zoomé ») : LIGNE_PC_LARGE (modèle de FM cité par rien)
    remplacé par une copie de la ligne Pour / Contre de FM (pastille du skin comprise) plus petite : pastille
    PASTILLE_PC_LARGE, logo LOGO_PC_LARGE, texte TEXTE_PC_LARGE. Lue seulement par la colonne Large"""
    bundle, _, stt = nb.find_vta(LISTE_PC)
    if stt is None:
        return [f"{LISTE_PC} introuvable (le jeu a changé ?), lignes compactes ignorées"]
    marque = f"{CLASSE_LIGNE_PC_LARGE}-" + hashlib.md5(json.dumps(stt, sort_keys=True, default=str)
                                                         .encode()).hexdigest()[:8]
    if any(a_classe(t, r, marque) for r in t.walk()):
        return []
    s = Tree(stt)
    s.styles = Styles(bundle, stt)
    racine = t.tt["m_VisualTree"]["rid"]
    expect = s.children(s.tt["m_VisualTree"]["rid"])[0]
    for k in list(t.children(racine)):
        t.remove(k)
    copie = t.clone(expect, racine, src=s)
    t.styles.copy_from(s.styles, t, copie)
    t.tt["m_Usings"] = [dict(u) for u in s.tt.get("m_Usings") or []]
    carre = lambda v: {k: v for k in ("width", "height", "min-width", "min-height", "max-width", "max-height")}  # noqa: E731
    for r in t.walk(copie):
        cls = t.elem(r).get("m_Classes") or []
        if t.name(r).startswith("UIPickerPourContreListe-"):
            t.styles.style(t, r, carre(PASTILLE_PC_LARGE))
        elif typ(t, r).endswith("SIImage"):
            t.styles.style(t, r, carre(LOGO_PC_LARGE))
        elif typ(t, r).endswith("SIText"):
            t.elem(r)["m_Classes"] = [TEXTE_PC_LARGE if c.startswith("body-") else c for c in cls]
    for r in t.children(copie)[:1]:
        t.elem(r)["m_Classes"] = (t.elem(r).get("m_Classes") or []) + [marque]
    return [f"ligne Pour / Contre compacte (mode Large) : pastille {PASTILLE_PC_LARGE} px, texte {TEXTE_PC_LARGE}"]


def ligne_attribut(t):
    """v1.41 (le joueur : « (tendance) » du gardien décale la valeur en Large, police Normale et plus) : dans la ligne
    d'attribut de FM (AttributesRow, lignes des tableaux d'attributs), le nom ne rétrécissait pas (pas de min-width 0) :
    la case de la valeur était écrasée et la valeur collée au nom. Nom : min-width 0 + rétrécit (son « … » de FM
    joue) ; case de la valeur : ne rétrécit plus. Rien ne change quand le nom tient. Le texte « (tendance) » vient du
    jeu (attribute.AttributeTypeInfo.Name, pas de nom court) : pas modifiable sans mod"""
    if any(a_classe(t, r, VERSION_LIGNE_ATTRIBUT) for r in t.walk()):
        return []
    fait = 0
    for rang in [r for r in t.walk() if t.name(r) in ("non-clickable-attributes_row", "clickable-attributes_row")]:
        kids = t.children(rang)
        if len(kids) != 2:
            continue
        nom, valeur = kids
        for x in [nom] + [r for r in t.walk(nom) if typ(t, r).endswith(("SIText", "SIButton"))
                          or (typ(t, r) == "UnityEngine.UIElements.VisualElement" and r != nom)]:
            t.styles.style(t, x, {"min-width": 0, "flex-shrink": 1})
        t.styles.style(t, nom, {"overflow": "hidden"})
        t.styles.style(t, valeur, {"flex-shrink": 0})
        t.elem(rang)["m_Classes"] = (t.elem(rang).get("m_Classes") or []) + [VERSION_LIGNE_ATTRIBUT]
        fait += 1
    if not fait:
        return ["lignes de AttributesRow introuvables (le jeu a changé ?), ignoré"]
    return ["ligne d'attribut : nom coupé (…) au lieu de décaler la valeur"]


def bouton_comparer(t):
    """le joueur (2026-11-01, Medium) : le bouton « Comparer » des postes touche le bord droit de la colonne (un peu
    mangé) → sa case (#SIVisible-IsFantasyDraftGame) décalée vers la gauche par une marge droite de FM.
    v2 (v1 en jeu : toujours coupé, au même endroit) : la vraie cause = #main-frame, classe de FM
    player-report-role-selector-roles-size-high-possession-ip (min-width 380, max 420, shrink 0) dans la colonne
    bridée à 380 (360 en Large) : la droite dépassait et était rognée → min-width 0 + rétrécit.
    v3 (v2 en jeu : entier mais 4-6 px trop à gauche, 3 modes) : marge retirée, bord droit = celui des rôles"""
    case = first(t, lambda r: t.name(r) == "SIVisible-IsFantasyDraftGame")
    cadre = first(t, lambda r: t.name(r) == "main-frame")
    if case is None or cadre is None:
        return ["bouton « Comparer » des postes introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(case).get("m_Classes") or []
    if VERSION_COMPARER in cls:
        return []
    cls = [c for c in cls if not c.startswith("uipicker-comparer-v") and c != "margin-right-global-gap-regular"]
    t.elem(case)["m_Classes"] = cls + [VERSION_COMPARER]
    t.styles.style(t, cadre, {"min-width": 0, "flex-shrink": 1})
    return ["bouton « Comparer » des postes entier, aligné sur les rôles"]


def pastille_note(t):
    """le joueur (2026-11-01) : note à l'entraînement « 10,00 » coupée sur 2 lignes. FM écrit toujours 2 décimales
    (pas réglable) et la classe de couleur posée par le SIStyleSetter (data_display-average_rating-default-default-
    rating-*, AlwaysAppliedStyleSheet) borne la pastille à 42-50 px → max-width PASTILLE_NOTE_MAX sur la pastille
    (et son parent : on ne sait pas lequel reçoit la classe). Largeur auto : seules les notes trop longues grandissent.
    Vaut partout où la note s'affiche (modèle inclus)"""
    pastille = first(t, lambda r: t.name(r) == "data_display-average_rating-default-default")
    if pastille is None:
        return ["pastille de la note à l'entraînement introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(pastille).get("m_Classes") or []
    if VERSION_PASTILLE_NOTE in cls:
        return []
    for r in (t.parent[pastille], pastille):
        t.styles.style(t, r, {"max-width": PASTILLE_NOTE_MAX})
    t.elem(pastille)["m_Classes"] = cls + [VERSION_PASTILLE_NOTE]
    return [f"pastille de la note à l'entraînement : jusqu'à {PASTILLE_NOTE_MAX} px (« 10,00 » sur une ligne)"]


def ligne_traits(t):
    """le joueur (2026-11-09, fiche Medium, jamais réglé avant) : UNE seule caractéristique dont le texte passe sur
    2 lignes n'a que la hauteur d'une ligne (texte rogné en haut et en bas). Ligne de FM (PlayerTraitsRow12px) :
    #TraitsRemapper en rangée, largeur = celle du texte sur une ligne puis rétrécie → hauteur mesurée sur une ligne.
    Remapper : flex-basis 0 + grandit + min-width 0 (largeur = la place restante, texte mesuré à cette largeur) ;
    texte : min-width 0. v36 de Guru (hauteur mini du cadre) était sans effet : la ligne elle-même est en cause"""
    rem = first(t, lambda r: t.name(r) == "TraitsRemapper")
    txt = first(t, lambda r: t.name(r) == "TraitsText")
    if rem is None or txt is None:
        return ["ligne des caractéristiques (PlayerTraitsRow12px) introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(rem).get("m_Classes") or []
    if VERSION_LIGNE_TRAITS in cls:
        return []
    t.styles.style(t, rem, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
    t.styles.style(t, txt, {"min-width": 0, "flex-shrink": 1})
    t.elem(rem)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-ligne-traits-v")] + [VERSION_LIGNE_TRAITS]
    return ["caractéristiques : texte sur 2 lignes à sa vraie hauteur"]


def liste_traits(t):
    """ligne-traits-v1 en jeu (2026-11-09, Large) : sans effet. La ligne (align-items center) est rognée au milieu =
    elle rétrécit à la hauteur que la liste de FM (StreamedObjectList Truncate) se donne : 1 ligne. Le joueur : « laisser
    un peu plus de place » → min-height HAUTEUR_LISTE_TRAITS sur #PlayerTraitsList elle-même (Guru v36 la mettait sur
    le cadre extérieur : sans effet). Une seule caractéristique courte : un peu de vide dessous"""
    liste = first(t, lambda r: t.name(r) == "PlayerTraitsList")
    if liste is None:
        return ["liste des caractéristiques (PlayerTraitsList) introuvable (le jeu a changé ?), ignoré"]
    cls = t.elem(liste).get("m_Classes") or []
    if VERSION_LISTE_TRAITS in cls:
        return []
    t.styles.style(t, liste, {"min-height": HAUTEUR_LISTE_TRAITS})
    t.elem(liste)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-liste-traits-v")] + [VERSION_LISTE_TRAITS]
    return [f"caractéristiques : liste haute de {HAUTEUR_LISTE_TRAITS} px au moins (2 lignes)"]


def recaler(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe (comme Kinito)"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])
    return r


def sources_entrainement():
    """modèles de FM recopiés pour le bloc d'entraînement (note, pouces, roue), ou un message d'erreur"""
    ns = src_tree(NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == NOTE_ENTRAINEMENT) if ns else None
    sb = src_tree(BOUTONS_SOURCE)
    boutons = {nom: first(sb, lambda r, nom=nom: sb.name(r) == nom and typ(sb, r) == "FM.UI.FMActionButton")
               for nom in POUCES} if sb else {}
    bundle_a, _, tta = nb.find_vta(ACTIONS_SOURCE)
    ta = Tree(tta) if tta is not None else None
    actions = first(ta, lambda r: ta.name(r) == ACTIONS_NOM and typ(ta, r).endswith("PluginContextMenuBindings")) \
        if ta else None
    if None in (note, actions) or None in boutons.values() or len(boutons) != len(POUCES):
        return "note, pouces ou menu Actions introuvable (le jeu a changé ?)"
    textes = [k for k in ta.children(actions) if typ(ta, k).endswith("SIText")]
    chevron = next((k for k in ta.children(actions) if typ(ta, k).endswith("VisualElement")), None)
    if [p.get("m_path") for p in ta.sd(actions).get("BindingPaths") or []] != ["selectedlist"] \
            or len(textes) != 1 or chevron is None:
        return f"menu « Actions » de FM ({ACTIONS_SOURCE}) inattendu (introuvable)"
    return {"ns": ns, "note": note, "sb": sb, "boutons": boutons, "ta": ta, "actions": actions,
            "styles_a": Styles(bundle_a, tta)}


def titre_traits(t):
    """(arbre, élément) du titre « Caractéristiques » de FM (TraitsTitleFrame) : dans la fiche jusqu'à la MAJ de FM du
    2026-11-12, depuis dans le modèle inclus PlayerTraitsFrameList"""
    titre = first(t, lambda r: t.name(r) == "TraitsTitleFrame")
    if titre is not None:
        return t, titre
    tl = src_tree(TRAITS_SOURCE)
    titre = first(tl, lambda r: tl.name(r) == "TraitsTitleFrame") if tl else None
    return (tl, titre) if titre is not None else (None, None)


def contenu_entrainement(t, parent, src, tt_titre, titre_fm, div_model, a_droite=False):
    """sous parent : trait, titre « Entraînement » avec le plot, puis la ligne note + pouces + roue « Actions »
    (a_droite : roue calée contre le bord droit, elle ne suit plus la largeur de la note / des pouces)"""
    d = t.clone(div_model, parent)   # trait comme entre les blocs d'Infos
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-regular"]
    # v6 : titre comme « Caractéristiques » (TraitsTitleFrame de FM recopié : icône + texte body-sm-strong), plot de FM
    titre = t.clone(titre_fm, parent, src=tt_titre)
    t.sd(titre)["name"] = ""
    for k in t.walk(titre):
        if k != titre and t.name(k) == "TraitsIcon":
            t.elem(k)["m_Classes"] = [c if c != ICONE_TRAITS else ICONE_TITRE for c in t.elem(k)["m_Classes"]]
        if typ(t, k).endswith("SIText"):
            xd = t.sd(k)
            tb = xd["TextBinding"]
            tb["m_kind"] = 0
            tb["m_direct"] = {"Path": {"m_path": ""}, "Nullable": 0}
            tb["m_visualFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                      "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
            texte = L("Entraînement", "Training")
            xd.update(text=texte, text_UxmlAttributeFlags=1, DebugDisplay=texte)
        if k != titre:
            t.sd(k)["name"] = ""
    ns, note = src["ns"], src["note"]
    row = plain(t, parent, None, ["row-direction-normal", "align-items-center", "align-self-stretch"])
    # v14 : sans style hérité (plain copie le 1er VisualElement du modèle, la colonne des postes bridée à 380 px :
    # la ligne devenait plus large qu'Infos et la roue en sortait)
    t.elem(row)["m_RuleIndex"] = -1
    rm = t.clone(ns.parent[note], row, src=ns)   # BindingRemapper binding -> person, avec la pastille
    t.elem(rm)["m_Classes"] = ["margin-right-global-gap-large"]
    t.styles.style(t, rm, FIXE)
    copy_usings(t, ns, ns.parent[note])

    # pouces : FMActionButton de FM (« player » fourni par un BindingRemapper player -> person) avec le gabarit icône
    # de Kinito (kinito_rapport_entrainement.GABARITS, posé par entrainement_individuel_equipes)
    pr = t.clone(ns.parent[note], row, src=ns)
    for k in list(t.children(pr)):
        t.remove(k)
    t.sd(pr)["name"] = ""
    t.sd(pr)["Mappings"] = [{"m_serialisedType": 0, "from": "player", "to": {"m_path": "person"},
                             "type": {"id": JOUEUR}}]
    t.elem(pr)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-right-global-gap-regular"]
    t.styles.style(t, pr, FIXE)
    for i, (nom, guid) in enumerate(POUCES.items()):
        b = recaler(t, t.clone(src["boutons"][nom], pr, src=src["sb"]))
        t.elem(b)["m_Classes"] = ["margin-right-global-gap-regular"] if i < len(POUCES) - 1 else []
        t.sd(b)["ActionsListWidget"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
        t.sd(b)["ActionsListWidget_UxmlAttributeFlags"] = 1

    if a_droite:   # v9 (le joueur) : espace extensible, la roue reste collée au séparateur de droite d'Infos
        esp = plain(t, row, None, [])
        t.elem(esp)["m_RuleIndex"] = -1
        t.styles.style(t, esp, {"flex-grow": 1})

    # roue : le menu « Actions » de l'écran Entraîn. individuel (comme la v31 de Kinito hors Large), sur ce joueur
    a = recaler(t, t.clone(src["actions"], row, src=src["ta"]))
    t.styles.copy_from(src["styles_a"], t, a)
    t.sd(a)["name"] = ""
    t.elem(a)["m_Classes"] = [c for c in t.elem(a).get("m_Classes") or [] if c != "flex-grow-class"]
    t.styles.style(t, a, FIXE)
    t.sd(a)["BindingPaths"] = [{"m_path": "person"}]
    x = next(k for k in t.children(a) if typ(t, k).endswith("SIText"))
    t.elem(x)["m_Classes"] = list(t.elem(x).get("m_Classes") or []) + ["hidden-item"]   # texte gardé pour FM
    ch = next(k for k in t.children(a) if k != x and typ(t, k).endswith("VisualElement"))
    i = recaler(t, t.clone_shallow(ch, a, t.children(a).index(x)))
    t.sd(i)["name"] = ""
    t.elem(i)["m_Classes"], t.elem(i)["m_RuleIndex"] = [ICONE_ROUE, "margin-right-global-gap-small"], -1


def infos_training_row(t):
    """v1.24 (le joueur) : la ligne d'entraînement passe en bas d'Infos (sous Suspensions) : note à l'entraînement,
    Féliciter / Critiquer en pouces (gabarits de Kinito, comme dans Entraîn. individuel), puis la roue « Actions » de
    l'écran Entraîn. individuel (rapport d'entraînement) pour ce joueur. Mêmes conditions que l'ancienne ligne :
    joueurs suivant l'entraînement de ton club, colonne du polygone affichée (Medium / Small)."""
    old = named(t, NOM_ENTRAINEMENT_RAPIDE)
    if any(VERSION_LIGNE in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    if polygon_button(t) is None:
        return ["bouton du polygone introuvable (le jeu a changé ?), ligne d'entraînement ignorée"]
    bans = first(t, lambda r: t.name(r) == "PlayerReportBansBlock")
    info = first(t, lambda r: t.name(r) == "InfoBlockFrame")
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    vis = visible_model(t)
    tt_titre, titre_fm = titre_traits(t)
    src = sources_entrainement()
    if None in (info, div_model, vis, titre_fm) or isinstance(src, str):
        return [(src if isinstance(src, str) else "colonne Infos introuvable") + ", ligne d'entraînement ignorée"]
    for r in old:   # ancienne version (sous les options d'entraînement, ou sous les Pour / Contre)
        t.remove(r)
    for r in named(t, NOM_TRAIT):
        t.remove(r)

    sous_info = bans
    if bans is not None and t.name(t.parent.get(bans)) == NOM_SMALL_GAUCHE:   # cachées en Small : place du conteneur
        sous_info = t.parent[bans]
    index = t.children(info).index(sous_info) + 1 if bans is not None and t.parent.get(sous_info) == info else None
    wrap = make_visible(t, vis, info, index, "person.PlayerTraining", NOM_ENTRAINEMENT_RAPIDE,
                        ["align-self-stretch", VERSION_LIGNE])
    wrap = make_visible(t, vis, wrap, None, CLUB_HUMAIN, "", ["align-self-stretch"])   # v7 : tes joueurs seulement
    if FICHE_SMALL and SMALL_SEULEMENT:   # v12 : Small seulement (Medium : sous les pieds, large_training)
        inner = si_small(t, wrap, None, True, ["column-direction-normal", "align-self-stretch"])
        # v13 / v15 (le joueur : « elle est utile », elle tient les menus dessous) : bloc bridé à la largeur d'Infos
        for r in (inner, wrap, t.parent[wrap]):
            t.styles.style(t, r, LARGEUR_MAX({"unit": 2, "value": 100.0}))
    else:
        inner = plain(t, wrap, None, ["column-direction-normal", "align-self-stretch"])
        polygon_visible(t, inner)   # affichée seulement quand la colonne du polygone est là (Medium / Small)
    contenu_entrainement(t, inner, src, tt_titre, titre_fm, div_model, a_droite=True)
    msgs = ["note à l'entraînement + pouces + roue « Actions » en bas d'Infos" + (" (déplacés)" if old else "")]
    if FICHE_SMALL:   # Small : Rôles / Priorité / Intensité dans le bloc, sous la note (ils quittent le bas des attributs)
        v = si_small(t, inner, None, True, ["align-self-stretch"])
        t.sd(v)["name"] = NOM_OPTIONS_INFOS
        err = options_verticales(t, v)
        msgs.append(f"{err}, options dans Infos ignorées" if err else "Small : Rôles / Priorité / Intensité dans le "
                    "bloc Entraînement d'Infos")
    return msgs


def large_training(t):
    """v1.25 (le joueur, validé en jeu le 2026-11-12) : mode Large, le même bloc dans le tableau d'attributs (modèle inclus
    AttributesTableTemplate) : sous les pieds (colonne Physique) pour un joueur de champ, sous Gardien pour un gardien.
    « Large seulement » = la liaison du bouton polygone de la fiche (visibilityMask de l'ExpandableContentElement,
    colonne 6 cachée) : le modèle ne la reçoit que si son BindingExpect la déclare (paramètre ajouté, type de
    « rolemask »). Vu en jeu : ça marche (Large seulement)."""
    old = named(t, NOM_ENTRAINEMENT_LARGE)
    if old and all(VERSION_LARGE in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    gros = src_tree(GROS_BLOC)
    bouton = polygon_button(gros) if gros else None
    tt_titre, titre_fm = titre_traits(gros) if gros else (None, None)
    attente = first(t, lambda r: typ(t, r).endswith("BindingExpect"))
    params = t.sd(attente).get("Parameters") if attente is not None else None
    masque = next((p for p in params or [] if p.get("name") == "rolemask"), None)
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    vis = visible_model(t)

    def liste(chemin):
        return first(t, lambda r: typ(t, r).endswith("StreamedObjectList")
                     and (t.binding(r) or "").lower() == chemin.lower())
    physique, gardien = liste("Person.AttributesPhysical"), liste("Person.AttributesGoalkeeping")
    src = sources_entrainement()
    if None in (bouton, titre_fm, masque, div_model, vis, physique, gardien) or isinstance(src, str):
        return [(src if isinstance(src, str) else "tableau d'attributs ou bouton du polygone introuvable")
                + ", bloc d'entraînement (Large) ignoré"]
    for r in old:
        t.remove(r)
    if not any(p.get("name") == MASQUE for p in params):
        p = copy.deepcopy(masque)
        p["name"] = MASQUE
        params.append(p)
    # colonne Physique du joueur de champ (sous les pieds, à la fin) ; colonne Gardien du gardien (sous la liste)
    for parent in (t.parent[t.parent[physique]], t.parent[gardien]):
        wrap = make_visible(t, vis, parent, None, "person.PlayerTraining", NOM_ENTRAINEMENT_LARGE,
                            ["align-self-stretch", VERSION_LARGE])
        wrap = make_visible(t, vis, wrap, None, CLUB_HUMAIN, "", ["align-self-stretch"])   # v2 : tes joueurs seulement
        if FICHE_SMALL and SMALL_SEULEMENT:
            # v5 (le joueur, 2026-11-12) : aussi en Medium (Infos trop serré, le bloc y était coupé) = hors Small ;
            # le bloc d'Infos n'est plus qu'en Small
            inner = si_small(t, wrap, None, False, ["column-direction-normal", "align-self-stretch"])
            contenu_entrainement(t, inner, src, tt_titre, titre_fm, div_model, a_droite=True)
            continue
        inner = plain(t, wrap, None, ["column-direction-normal", "align-self-stretch"])
        e = t.elem(inner)
        data = copy.deepcopy(gros.refs[gros.elem(bouton)["m_SerializedData"]["rid"]])   # SIVisible du bouton polygone
        data["rid"] = t.new_rid()
        data["data"]["uxmlAssetId"], data["data"]["name"] = e["m_Id"], ""
        args = data["data"]["Binding"]["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]
        args[-1] = 1   # inversé : affiché quand la colonne du polygone est CACHÉE (mode Large)
        old_sd = e["m_SerializedData"]["rid"]
        t.refs[data["rid"]] = data
        t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] != old_sd] + [data]
        t.refs.pop(old_sd, None)
        e["m_FullTypeName"], e["m_SerializedData"] = "SI.Bindable.SIVisible", {"rid": data["rid"]}
        contenu_entrainement(t, inner, src, tt_titre, titre_fm, div_model, a_droite=True)
    mode = "Large / Medium" if FICHE_SMALL and SMALL_SEULEMENT else "Large"
    return [f"bloc d'entraînement en mode {mode} : sous les pieds (joueur de champ), sous Gardien (gardien)"
            + (" (refait)" if old else "")]


def training_separator(t):
    """fiche joueur : trait horizontal entre les attributs et le groupe options d'entraînement + Féliciter /
    Critiquer. Posé dans le conteneur "s'il y a la place" des options : masqué avec elles en mode Défaut."""
    if named(t, NOM_SEPARATEUR):
        return []
    opts = named(t, NOM_OPTIONS_ENTRAINEMENT)
    holder = next((k for o in opts for k in t.children(o)
                   if {CLASSE_SI_POLYGONE, CLASSE_SI_PLACE} & set(t.elem(k).get("m_Classes") or [])), None)
    div_model = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal")
    if holder is None or div_model is None:
        return ["options d'entraînement (hors_defaut.py) ou trait introuvable, séparateur ignoré"]
    d = t.clone(div_model, holder, 0)
    t.sd(d)["name"] = NOM_SEPARATEUR
    t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-bottom-global-gap-large"]
    return ["séparateur au-dessus des options d'entraînement"]


def dynamics_logos(t):
    """fiche joueur, colonne Infos : logos Hiérarchie et Groupe social (ceux de l'onglet Personnel) à droite de
    Réputation, l'un sur l'autre. Recopie du BindingSetter de FM (isDataValid) + son switch : sans info (joueur
    d'un autre club...), la branche « pas de données » reste vide. Les textes sont retirés, seule l'image reste."""
    old = named(t, NOM_LOGOS)
    if any(VERSION_LOGOS in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    for row in old:   # version précédente : Réputation remise à sa place, puis on refait
        for k in [k for k in t.children(row) if t.name(k) == "PlayerReputationTextFrame"]:
            move(t, k, t.parent[row], t.children(t.parent[row]).index(row))
        t.remove(row)
    rep = first(t, lambda r: t.name(r) == "PlayerReputationTextFrame")
    tip = first(t, lambda r: typ(t, r) == "SI.Bindable.Tooltip" and len(t.children(r)) == 1
                and typ(t, t.children(r)[0]) == "SI.Bindable.SIText")
    if rep is None or (LOGOS_INFOBULLE and tip is None):
        return ["ligne Réputation ou modèle d'infobulle introuvable, logos ignorés"]
    sources = []
    for model, label in LOGOS_SOURCES:
        bundle, _, stt = nb.find_vta(model)
        s = Tree(stt) if stt is not None else None
        setter = first(s, lambda r: s.name(r) == "BindingDataSetter") if s else None
        if setter is None:
            return [f"{model} introuvable (le jeu a changé ?), logos ignorés"]
        sources.append((s, Styles(bundle, stt), setter, label))

    parent = t.parent[rep]
    row = plain(t, parent, t.children(parent).index(rep),
                ["row-direction-normal", "align-self-stretch", VERSION_LOGOS], NOM_LOGOS)
    t.elem(row)["m_RuleIndex"] = -1
    t.styles.style(t, row, {"align-items": "flex-end"})
    move(t, rep, row)
    t.styles.style(t, rep, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0})
    col = plain(t, row, None, ["column-direction-normal", "align-items-center", "margin-left-global-gap-small"])
    t.elem(col)["m_RuleIndex"] = -1
    # v5 : colonne en position absolue (ne compte plus dans la hauteur de la ligne : les 2 logos empilés sont plus
    # hauts que Réputation + valeur, la ligne grandissait et le trait du dessous descendait), ancrée en bas à droite
    t.styles.style(t, col, {**FIXE, "position": "absolute", "right": LOGOS_MARGE_DROITE, "bottom": LOGOS_BAS})   # v2 : au ras du bas de « Nationale »
    for i, (s, sst, setter, label) in enumerate(sources):
        new = t.clone(setter, col, src=s)
        t.sd(new)["name"] = ""
        t.styles.copy_from(sst, t, new)   # taille de l'image (24 px)
        for r in [r for r in t.walk(new) if typ(t, r) == "SI.Bindable.SIText"]:
            t.remove(r)
        img = next(r for r in t.walk(new) if typ(t, r) == "SI.Bindable.SIImage")
        frame = t.parent[img]
        t.elem(img)["m_Classes"] = []
        t.elem(frame)["m_Classes"] = ["row-direction-normal", "align-items-center"] \
            + (["margin-bottom-global-gap-small"] if i < len(sources) - 1 else [])
        if LOGOS_INFOBULLE:
            tt = t.clone(tip, frame)
            text = t.children(tt)[0]
            t.sd(text)["name"] = ""
            set_text_binding(t, text, {"m_kind": 1, "m_direct": {"Path": {"m_path": label}, "Nullable": 0},
                                       "m_visualFunction": {"m_target": {"m_guid": ""},
                                                            "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                            "m_outputs": {"m_variable": {"m_argumentBytes": []}}}})
    return ["logos Hiérarchie + Groupe social à droite de Réputation" + (" (refait)" if old else "")]


def sans_logos(t):
    """logos d'Infos retirés (copies d'Infos comprises), Réputation remise à sa place"""
    old = named(t, NOM_LOGOS)
    for row in old:
        for k in [k for k in t.children(row) if t.name(k) == "PlayerReputationTextFrame"]:
            move(t, k, t.parent[row], t.children(t.parent[row]).index(row))
            t.styles.style(t, k, {"flex-grow": 0})
        t.remove(row)
    return ["logos Hiérarchie + Groupe social retirés d'Infos (ils sont dans la tuile État d'esprit)"] if old else []


def etat_icones(t):
    """fiche joueur, colonne Infos : icônes des tableaux de joueurs (condition, forme, fatigue, état d'esprit, moral)
    en ligne en haut à droite, au niveau de Taille ; survol = infobulle de la cellule FM (essai, 2026-11-12)"""
    old = named(t, NOM_ICONES)
    if any(VERSION_ICONES in (t.elem(r).get("m_Classes") or []) for r in old):
        return []
    for r in old:
        t.remove(r)
    taille = first(t, lambda r: t.name(r) == "PersonHeightTextFrame")
    ns = src_tree(NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == NOTE_ENTRAINEMENT) if ns else None
    if taille is None or note is None:
        return ["ligne Taille ou modèle de liaison introuvable, icônes ignorées"]
    cellules = []
    for model, liens in ICONES:
        bundle, _, stt = nb.find_vta(model)
        if stt is None:
            return [f"{model} introuvable (le jeu a changé ?), icônes ignorées"]
        s = Tree(stt)
        cellules.append((s, Styles(bundle, stt), s.children(s.tt["m_VisualTree"]["rid"])[0], liens))
    cadre = t.parent[taille]   # #Frame : Taille, Personnalité, Réputation
    row = plain(t, cadre, 0, ["row-direction-normal", "align-items-center", VERSION_ICONES], NOM_ICONES)
    t.elem(row)["m_RuleIndex"] = -1
    # position absolue : ne pousse pas Taille vers le bas, ancrée en haut à droite (au niveau de « Taille »)
    t.styles.style(t, row, {**FIXE, "position": "absolute", "top": 0, "right": ICONES_MARGE_DROITE})
    for i, (s, sst, racine, liens) in enumerate(cellules):
        rm = t.clone(ns.parent[note], row, src=ns)   # BindingRemapper vidé : paramètres de la cellule -> fiche
        for k in list(t.children(rm)):
            t.remove(k)
        t.elem(rm)["m_Classes"] = ["column-direction-normal"]
        t.elem(rm)["m_RuleIndex"] = -1
        t.sd(rm)["name"] = ""
        t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": p, "to": {"m_path": chemin}, "type": {"id": ty}}
                                for p, (chemin, ty) in liens.items()]
        # v2 : chaque icône dans une case fixe, centrée (v1 en jeu : alignement et écarts inégaux, chaque cellule FM
        # gardait ses marges / hauteurs de tableau)
        w = ICONE_LARGEURS[i] if i < len(ICONE_LARGEURS) else ICONE_CASE
        t.styles.style(t, rm, {"width": w, "height": ICONE_CASE, "min-width": w, **FIXE,
                               "align-items": "center", "justify-content": "center"})
        c = t.clone(racine, rm, src=s)
        copy_usings(t, s, racine)
        t.styles.copy_from(sst, t, c)
        # classes de cellule de tableau (hauteur 36 px, marges, alignement en haut) retirées : juste l'icône
        for r in t.walk(c):
            cls = t.elem(r).get("m_Classes") or []
            t.elem(r)["m_Classes"] = [k for k in cls if not k.startswith(ICONE_CLASSES_RETIREES)]
    return ["icônes condition / forme / fatigue / état d'esprit / moral en haut à droite des Infos"
            + (" (refait)" if old else "")]


def sans_etat_icones(t):
    """ICONES_ETAT = False : rangée d'icônes d'Infos posée avant retirée"""
    old = named(t, NOM_ICONES)
    for r in old:
        t.remove(r)
    return ["icônes d'état des Infos retirées"] if old else []


def infos_largeur(t):
    """retire l'essai « colonne Infos plus étroite » (uipicker-infos-v1, max 280) : la largeur vaut pour tous les
    modes (le mode n'est pas lisible dans la fiche) et le joueur ne veut pas que Small change ; largeur de FM remise"""
    info = first(t, lambda r: t.name(r) == "InfoBlockFrame")
    cls = (t.elem(info).get("m_Classes") or []) if info is not None else []
    if not any(c.startswith("uipicker-infos-v") for c in cls):
        return []
    t.elem(info)["m_Classes"] = [c for c in cls if not c.startswith("uipicker-infos-v")]
    t.styles.style(t, info, {"max-width": FM_LARGEUR_INFOS_MAX})
    return ["colonne Infos : largeur de FM remise"]


NOM_TAILLE_CACHEE = "UIPickerTailleCachee"


def taille_infos(t):
    """2026-11-05 (le joueur) : avec l'en-tête en grande tuile (option entete_vue = tuile), la taille est sous le
    nom en haut -> « Taille » d'Infos cachée dans toutes les fiches (tous modes) ; remise si l'option revient à FM.
    Cachée par un élément SANS liaison (taille 0, coupé, hors du flux : rien de lié ne tient au chargement)"""
    cacher_ = options.get("entete_vue") == "tuile"
    boites = [r for r in t.walk() if t.name(r) == NOM_TAILLE_CACHEE]
    if not cacher_:
        for b in boites:
            par = t.parent[b]
            i = t.children(par).index(b)
            for j, k in enumerate(list(t.children(b))):
                move(t, k, par, i + j)
            t.remove(b)
        return ["taille remise dans Infos (en-tête de FM)"] if boites else []
    deja = {k for b in boites for k in t.walk(b)}
    tailles = [r for r in t.walk() if t.name(r) == "PersonHeightTextFrame" and r not in deja]
    for r in tailles:
        par = t.parent[r]
        b = plain(t, par, t.children(par).index(r), [], NOM_TAILLE_CACHEE)
        t.sd(b)["name_UxmlAttributeFlags"] = 1
        t.elem(b)["m_RuleIndex"] = -1
        t.styles.style(t, b, {"position": "absolute", "top": 0, "width": 0, "height": 0, "max-width": 0,
                              "max-height": 0, "overflow": "hidden"})
        move(t, r, b)
    return [f"taille cachée dans Infos ({len(tailles)}), elle est dans l'en-tête en grande tuile"] if tailles else []


def jobs():
    # 2026-11-12 : la vue FM Guru est un script à part (fiche_fmguru.py) qui prend le dessus : cette fonction est
    # désactivée quand elle est choisie (main) ; sans_guru nettoie encore une vue Guru d'avant (v1 à v12, ici)
    big = [fn for on, fn in ((True, sans_guru), (POUR_CONTRE_A_LA_PLACE_DU_POLYGONE, pros_cons), (ENTRAINEMENT_RAPIDE, infos_training_row),
                             (LEGENDE_A_GAUCHE, key_left), (LEGENDE_A_GAUCHE, largeur_postes), (True, largeur_options),
                             (POUR_CONTRE_A_LA_PLACE_DU_POLYGONE, largeur_colonne_pc), (True, largeur_infos),
                             (SEPARATEUR_ENTRAINEMENT, training_separator),
                             (LOGOS_DYNAMIQUE, dynamics_logos), (not LOGOS_DYNAMIQUE, sans_logos), (ICONES_ETAT, etat_icones), (not ICONES_ETAT, sans_etat_icones),
                             (True, infos_largeur), (FICHE_SMALL, pour_contre_bas),
                             (FICHE_SMALL and ENTRAINEMENT_RAPIDE, options_hors_small),
                             (FICHE_SMALL and LEGENDE_A_GAUCHE, small_gauche_infos)) if on]
    if POLYGONE_LARGE:
        big.append(polygone_large)   # en dernier ; recopie le tableau d'attributs : son job passe avant
    if POUR_CONTRE_A_LA_PLACE_DU_POLYGONE and POLYGONE_POUR_CONTRE:
        big.append(bouton_large_seul)   # après la copie Large (qui garde le bouton)
    big.append(taille_infos)   # en dernier : aussi dans les copies d'Infos (option entete_vue, 2026-11-05)
    # un seul passage par modèle : deux passages séparés repartiraient chacun de l'état d'origine
    return [(POSTES, bouton_comparer), (NOTE_ENTRAINEMENT, pastille_note), (LIGNE_TRAITS, ligne_traits),
            (LISTE_TRAITS, liste_traits)] \
        + ([(LIGNE_ATTRIBUT, ligne_attribut)] if POLYGONE_LARGE else []) \
        + ([(LIGNE_PC_LARGE, ligne_pc_large)]   # 2026-11-07 : aussi grande tuile (pcseul : lignes vides sans elle)
           if POLYGONE_LARGE and (LARGE_POUR_CONTRE or POLYGONE_PC_DESSOUS or LARGE_PC_SEULS) else []) \
        + ([(TABLEAU, large_training)] if ENTRAINEMENT_RAPIDE else []) \
        + ([(GROS_BLOC, lambda t: [m for fn in big for m in fn(t)])] if big else [])


def cmd_etat():
    for model in [GROS_BLOC]:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
            continue
        t = Tree(tt)
        have = [n for n in (NOM_POUR_CONTRE, NOM_ENTRAINEMENT_RAPIDE, NOM_LOGOS, NOM_ICONES) if named(t, n)]
        print(f"{model} : " + (", ".join(have) if have else "rien"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op in ("appliquer", "si-actif") and mode_guru():
        print(L("désactivée : pas compatible avec l'affichage fiche joueur de FM Guru (choisi dans Features "
                "additionnelles, il prend le dessus)",
                "disabled: not compatible with the FM Guru player profile display (chosen in Additional features, "
                "it takes over)"))
        return
    if op == "appliquer":
        appliquer_jobs(jobs(), MARKER)
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)   # ajouts retirés en remettant les modèles d'origine
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            appliquer_jobs(jobs(), MARKER)
        else:
            print("ajouts de la fiche joueur : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])