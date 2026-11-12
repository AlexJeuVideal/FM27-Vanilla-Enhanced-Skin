"""Couleurs de l'interface : barre du haut, son texte, barre secondaire, accent (bouton Continuer + violet interactif).

Chaque couleur est facultative (« fm » = celle de FM, le choix de base) :
- barre  : barre de navigation du haut. FM y peint la couleur du club (TitlebarBackgroundColour, dégradé SIGradient
           à 90 %, modèle PrimaryNavigationBarGradient) : les SIGradient deviennent des éléments simples à fond fixe.
- texte  : texte et icônes de cette barre. FM pose la classe nav-on-dark (texte clair) ou nav-on-light (texte foncé)
           selon le club (human.team.teamcontainer.IsDark, #NavThemeStyleSetter de PrimaryNavigationBar) : la classe
           est forcée. Sans texte choisi (« auto ») : blanc, sauf barre très claire (noir). Une couleur précise ajoute
           en plus des règles USS « .nav-on-dark .portal-text » etc. (AlwaysAppliedStyleSheet).
- barre2 : barre secondaire (sous la barre du haut) : dégradé de la couleur de ce qu'on regarde (ton club, un autre
           club, une compétition, une nation...) -> ta couleur partout (SecondaryNavigationBar).
- accent : variables USS violettes / roses de FM27 (onglets, interrupteurs, sélections, bouton Continuer) recolorées
           dans la teinte choisie, en gardant leurs nuances (ACCENT_REF = violet de base de FM).
- liseret : le trait fin (1 px, teinté aux couleurs de l'équipe) entre la barre du haut et la barre secondaire :
           #IsEmployedDivider d'OverviewTitleBar. « cache » = display: none (2026-11-12, demande du joueur) ; « fm » =
           affiché ; absent / « auto » = caché dès qu'une couleur (barre, texte, barre2, accent) est choisie, affiché
           sinon (skin installé sans toucher aux couleurs = trait de FM). (v2 cachait par erreur
           #PrimaryNavigationBarClubColours, le trait home / away à côté des flèches : gardé.)
Écran Tactiques (2026-10-30, demande du joueur : « une couleur pour chaque vert ») :
- tac_barre   : bandeau du haut (formation, Style, Mentalité, Intensité...) : dégradé écrit dans TacticalPlannerHeader
                (SIGradient, fonction 47578265, 2 ColorVisualArg #206658 -> #036150) ; seules ses 2 couleurs changent
                (modèle partagé : propriétaire tactiques_boutons, qui repart de l'original -> SUIVANTS le relance).
- tac_panneau : fond et cadres autour du terrain et des remplaçants : variable --pitch-tile-default-background +
                verts écrits en dur dans les règles « tactics » (#036150, cadres #32755D...), nuances gardées.
- tac_terrain : la pelouse (.tactics-collapsable-pitch-grass-colour, var(--colours-tactics-base-50) de FM).
Tuiles et tableau de score (2026-11-06, demande du joueur) :
- tuiles      : fond de toutes les tuiles / cartes du jeu : variables --layout-ui-tiles-interaction-surface-light-default
                et --layout-surfaces-cards-surface (FM : var(--colours-ui-soft) #1E2129) ; survol (…-light-hover, FM
                #2E3138) = la couleur choisie un peu plus claire (TUILES_SURVOL). « panneau » = comme le grand panneau
                des fiches (TUILES_PANNEAU_*, transparent : le fond de la page passe dessous). Aussi les cartes de
                l'en-tête de la fiche joueur (ENTETE_CARTE, v15).
- score_fond  : cases sombres du tableau de score de base en match (modèle Scoreboard qui contient #scorebar : logo
                de la compétition, temps, score, aller-retour ; FM #232735). Les tableaux sous licence (Premier
                League, EFL, Ligue des champions…) ne sont pas touchés. Texte foncé si la couleur est claire.
- score_bande : bande claire des noms d'équipes de ce tableau (FM #D2D2E4) ; noms en blanc si la couleur est foncée.
  Modèle du bundle du match (écrit aussi par match_haut, qui le remet d'origine en entier quand on le retire :
  SUIVANTS["match_haut"] relance ce script) ; appliquer repart de l'original du modèle.
Match (2026-11-07, demande du joueur : « en match c'est toujours les couleurs de base ») :
- match_boutons  : fond des boutons du haut à droite (Tactiques, Consignes, mentalité, Ajustements, Cons. du banc,
                   roue, ⋯) : règles .buttons-me-menu-controls-base* (FM : var(--layout-ui-tiles-light-background),
                   survol var(--midnight)) ; survol = un peu plus clair (TUILES_SURVOL) ; texte foncé si couleur claire.
                   Le bouton lecture (violet) suit l'accent.
- match_effectif : fond du bandeau de l'effectif en bas (titulaires + remplaçants) : règles .squad-overview-block /
                   .squad-overview-item (FM : var(--midnight), survol var(--colours-ui-strong)).
- commentaire    : barre de commentaire (« X se positionne sur la droite ») : MatchCommentaryBar (bundle du match),
                   aux couleurs du club par un SIStyleSetter (classes fm-club-primary-color / -secondary-color) :
                   classes retirées, fonction du setter vidée (elle posait la couleur du club en code, par-dessus),
                   fond choisi + texte blanc ou foncé (selon la couleur) en style intégré.
Postes (2026-11-09, demande du joueur) :
- poste_gb / poste_d / poste_dm (AL et MD) / poste_mc / poste_mo / poste_bt : couleur de chaque poste dans l'écran
  Tactiques (cases du terrain et du tableau) ; pas dans les thèmes complets (POSTES).

Menus et boutons (2026-11-08, demande du joueur) :
- menus   : menus déroulants, menus de la roue / des onglets et fenêtres (Préférences…) : MENUS_VARIABLES +
            règles MENUS_SELECTEURS (FM #2E3138). Traits séparateurs : ceux de FM.
- panneaux : tout ce qui a le fond des panneaux de FM (var(--midnight-alpha-65), #0A0F1E à 65 %) : panneaux des pages
             et du match, pop-ups ; voiles qui assombrissent l'écran : FM.
- fiche    : grande tuile du milieu de la fiche joueur seulement (FICHE_SELECTEURS).
- boutons : boutons d'action en dégradé, bouton Continuer / Messages et tout le violet / rose qui les suit : même
            travail que l'accent (nuances gardées), à sa place quand elle est choisie.

Fichiers : modèles du bundle gameworld (seul script à toucher ces 4 modèles : appliquer repart de l'original) et les
2 bundles de styles, partagés avec theme_fond (infobulles) : ecrire_styles() refait les deux à chaque fois.

Usage (jeu fermé) :
  couleurs_interface.py appliquer barre=#1D3B57 texte=auto barre2=#2B2F36 accent=#B145E3 liseret=cache|fm|auto
      tac_barre=#206658 tac_panneau=#03614F tac_terrain=#0C433A tuiles=#1E2129 score_fond=#232735
      score_bande=#D2D2E4 match_boutons=#2A2E3A match_effectif=#141A2A commentaire=#FFFFFF
      menus=#2E3138 boutons=#A300DB poste_gb=#3C3C5A poste_d poste_dm poste_mc poste_mo poste_bt [--dry-run]
      (#RRGGBBAA = avec opacité, ex. barre=#1D3B5780 = à 50 %)
      (clé absente = valeur précédente gardée ; « fm » = couleur de FM / trait affiché ; noms de couleurs :
      theme_fond.py liste)
  couleurs_interface.py retirer | etat | si-actif
  couleurs_interface.py essai-pelouse   (ESSAI : pelouse des Tactiques, voir ESSAI_PELOUSE)
"""
import colorsys
import copy
import json
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
import bouton_continuer  # noqa: E402  (clé « continuer » : couleur du bouton Continuer, ce script l'appelle)
import touche_club  # noqa: E402  (clés « touche » : couleur du club sur la barre unie, ce script l'appelle)
from attributs_tout_cocher import ouvrir, original  # noqa: E402  (modèle repris de la sauvegarde d'origine)
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

# =====================================================================================================
# RÉGLAGES MODIFIABLES
ACCENT_REF = "#B145E3"          # --colours-base-purple-base : la couleur d'accent de FM (choisir celle-ci = rien ne change)
CONTRASTE_MINI = 4.5            # accent : contraste gardé avec le texte (blanc / noir) de FM, sans dépasser FM ni ce seuil
TEXTE_SEUIL_NOIR = 0.75        # texte « auto » : noir si la barre est plus claire que ça (0 noir .. 1 blanc)
# variables d'accent recolorées (définies dans FigmaStyleVariables, AlwaysAppliedStyleSheet, TransferDeadlineDay)
VARIABLES_ACCENT = [
    "--colours-base-purple-soft", "--colours-base-purple-strong", "--colours-base-purple-base",
    "--colours-base-purple-deep", "--colours-base-purple-base-35", "--colours-base-purple-base-16",
    "--colours-base-purple-base-8", "--colours-base-purple-20", "--colours-base-purple-40",
    "--colours-base-purple-50", "--colours-base-purple-60",
    "--brand-theme-primary", "--brand-theme-primary-soft", "--brand-theme-primary-accent",
    "--brand-theme-primary-accent-soft", "--brand-theme-light", "--brand-theme-accent", "--brand-theme-primary-08",
    "--brand-theme-primary-16", "--brand-theme-primary-70", "--brand-theme-primary-0", "--brand-theme-accent-40",
    "--colours-brand-foundation-twilight", "--colours-brand-foundation-twilight-soft",
    "--colours-brand-foundation-twilight-base", "--colours-brand-foundation-twilight-base-0",
    "--colours-brand-foundation-twilight-strong", "--colours-brand-foundation-twilight-strong-0",
    "--colours-brand-foundation-horizon", "--colours-brand-foundation-horizon-soft",
    "--colours-brand-foundation-horizon-base-soft", "--colours-brand-foundation-horizon-base-20",
    "--colours-brand-foundation-horizon-base-8", "--colours-brand-foundation-cloud",
    "--colours-brand-tints-horizon-120", "--colours-brand-tints-horizon-alpha-8",
    "--colours-brand-tints-horizon-alpha-20", "--colours-brand-tints-horizon-alpha-30",
    "--horizon-alpha-8", "--horizon-alpha-16", "--horizon-alpha-35", "--highlight-colour-transparent",
    "--colours-brand-highlight-pink-base", "--colours-brand-fm25-lilac", "--colours-brand-fm25twlight-light",
    "--data-tables-background-selected", "--data-tables-background-focus-cell",
]
# (2026-11-11) --continue-button-default-* (rouge de base du bouton Continuer, aussi les jours de match / Confirmer la
# sélection) : plus recolorées (le joueur : les alertes toujours là, même avec un thème) ; la couleur du thème / du
# club sur le bouton = clé « continuer » (bouton_continuer.py), seulement quand il dit « Continuer »
# couleurs écrites en dur dans les règles (pas des variables) : recolorées si ce sont des violets d'accent (teinte
# entre ces bornes, mêmes valeurs que les variables ci-dessus)
TEINTES_DURES = (250, 300)
# variables ci-dessus recolorées seulement si leur couleur d'origine est dans cette famille (de 245° à 360°, puis
# jusqu'à 5°) : un thème spécial de FM qui les redéfinit dans une autre teinte (jaune du jour de clôture) est gardé
TEINTES_ACCENT = (245, 5)
# texte de la barre (couleur précise) : règles ajoutées, sous .nav-on-dark et .nav-on-light
TEXTE_COULEUR = ["portal-text", "global-text-primary", "global-text-secondary", "nd-flat-black"]
TEXTE_TEINTE = ["portal-image", "nd-flat-black", "ui-concepts-chevron-down_small", "ui-concepts-chevron-left_small",
                "ui-concepts-chevron-right_small", "#NavTabDropdownIndicator"]
# écran Tactiques : couleurs de FM (choisir celles-ci = rien ne change) ; les autres verts suivent leur nuance
TAC_BARRE_FM = "#20665A"        # haut du dégradé du bandeau (le bas, #036150, suit)
TAC_PANNEAU_FM = "#03614F"      # --pitch-tile-default-background
TAC_TERRAIN_FM = "#0C433A"      # --colours-tactics-base-50
# verts écrits en dur dans les règles dont un sélecteur contient « tactic » : recolorés comme le panneau
TAC_PANNEAU_DURS = ["#036150", "#03614F", "#32755D", "#0E4740",
                    "#1DA68F", "#188B78", "#126658", "#0C433A", "#072722", "#051A16"]   # (+ valeurs des variables)
# variables vertes des Tactiques (boutons Vue combinée / Avec le ballon..., ≪, onglets, cadres des remplaçants...) :
# recolorées comme le panneau (v2, 2026-10-30 : le joueur, « les boutons suivent pas la couleur »)
TAC_VARIABLES = ["--colours-tactics-base-00", "--colours-tactics-base-20", "--colours-tactics-base-40",
                 "--colours-tactics-base-50", "--colours-tactics-base-60", "--colours-tactics-base-80",
                 "--colours-feature-tactics-base-20", "--colours-feature-tactics-base-20-a16",
                 "--colours-feature-tactics-base-40", "--colours-feature-tactics-base-50",
                 "--colours-feature-tactics-base-60", "--colours-feature-tactics-base-80"]
TAC_TERRAIN_CLASSE = "tactics-collapsable-pitch-grass-colour"
# v16 (2026-11-09, le joueur : « quand je soulève un joueur, la surbrillance des autres qui peuvent jouer au poste se
# voit à peine ») : lignes surlignées pendant le glisser (FM #126658 à 50 %) = PAS recolorées comme le panneau (thème
# gris -> gris sur gris) : couleur du bouton Continuer (boutons / accent / violet de FM), éclaircie jusqu'à
# SURBRILLANCE_CONTRASTE avec le panneau. Jamais le vert de FM (le joueur : « PAS VERT »)
SURBRILLANCE_CLASSE = "tactics-row-highlight-highlighted"
SURBRILLANCE_ALPHA = 0.6
SURBRILLANCE_CONTRASTE = 2.5
# ESSAI (2026-10-31, Kiliwick : terrain qui reste gris avec Ardoise quoi qu'on choisisse) : quel élément fait vraiment
# la pelouse ? Commande essai-pelouse = styles seuls, chaque candidat dans une couleur vive (règle d'une seule classe ou
# variable) ; retour normal : toute autre écriture des couleurs (si-actif, app, choix 1)
ESSAI_PELOUSE = {"tactics-collapsable-pitch-grass-colour": "#FF0000",       # rouge : la pelouse visée jusqu'ici
                 "tactics-pitch-block": "#0040FF",                          # bleu
                 "tactics-collapsable-pitch-container": "#00E5FF",          # cyan
                 "frame-324-tactics-visualiser-pitch-default": "#FF8000",   # orange
                 "--pitch-tile-default-background": "#FFD000",              # jaune (= panneau)
                 "--colours-tactics-base-50": "#FF00FF"}                    # magenta
# tuiles : variables du fond des tuiles / cartes (valeur remplacée par la couleur choisie) et du survol
TUILES_VARIABLES = ["--layout-ui-tiles-interaction-surface-light-default", "--layout-surfaces-cards-surface"]
TUILES_VARIABLES_SURVOL = ["--layout-ui-tiles-interaction-surface-light-hover"]
TUILES_FM = "#1E2129"           # --colours-ui-soft (choisir celle-ci = comme FM)
# v15 (2026-11-09, le joueur : « brancher l'en-tête sur la couleur des tuiles ») : cartes de l'en-tête de la fiche
# joueur (entete_tuile v31, classe CL_CARTE) : règle « .classe { fond } » ajoutée à AlwaysAppliedStyleSheet
ENTETE_CARTE = "uipicker-entete-carte"
TUILES_SURVOL = 0.06            # survol : clarté (0..1) ajoutée à la couleur choisie (retirée si elle est très claire)
# tuiles=panneau (2026-11-07, demande du joueur : « comme la grande tuile du milieu ») : fond du grand panneau des fiches
# (.sicard-container-large = var(--midnight-alpha-65) de FM) : couleur + transparence, le fond de la page passe dessous
TUILES_PANNEAU = "panneau"
TUILES_PANNEAU_RGB, TUILES_PANNEAU_ALPHA = "#0A0F1E", 0.65
# tableau de score de base (match) : couleurs de FM dans ses styles intégrés, remplacées
SCORE_FOND_FM = "#232735"       # cases sombres (logo de la compétition, temps, score, aller-retour)
SCORE_BANDE_FM = "#D2D2E4"      # bande claire des noms d'équipes
SCORE_TEXTE_FONCE = "#232735"   # texte posé sur une case devenue claire (= texte des noms de FM)
SCORE_SEUIL_CLAIR = 0.6         # luminance (0 noir .. 1 blanc) au-dessus de laquelle le texte des cases passe en foncé
SCORE_SEUIL_FONCE = 0.45        # luminance sous laquelle les noms de la bande passent en blanc
# match : classes des règles USS dont le fond est remplacé (préfixe : toutes les positions et le survol)
MATCH_BOUTONS_CLASSES = ("buttons-me-menu-controls-base",)
MATCH_EFFECTIF_CLASSES = ("squad-overview-block", "squad-overview-item")
MATCH_SEUIL_CLAIR = 0.6         # luminance au-dessus de laquelle le texte (boutons, commentaire) passe en foncé
MATCH_TEXTE_FONCE = "#1A1C22"
# menus (2026-11-08, demande du joueur : « met les toutes dans le même settings ») : menus déroulants, menus de la roue /
# des onglets, fenêtres (Préférences, notifications) : variables du fond des fenêtres (FM : var(--colours-ui-strong)
# #2E3138) + fond des règles dont un sélecteur est exactement l'une de ces suites de classes (survol / sélection : FM)
MENUS_FM = "#2E3138"
MENUS_VARIABLES = ["--layout-surfaces-modules-modal", "--layout-surfaces-modal-surface"]
MENUS_SELECTEURS = [("si-dropdown", "virtualised-list__item"), ("si-dropdown", "virtualised-list__item--odd"),
                    ("cascading-menu__folder__entry",), ("floating-element",), ("dialog-card",),
                    ("setup_game_dialog",)]
# panneaux (2026-11-09, le joueur : « pour être 100 % custom », « tout ce qui regroupe ça ») : toutes les règles dont le
# fond est var(--midnight-alpha-65) de FM (#0A0F1E 65 %) : panneaux SICard grand / petit format (Messages, Infos,
# Classement du Portail, tableau de l'Effectif, panneaux du match… classes posées par le code de FM), pop-ups,
# report / tool containers. Sauf les voiles qui assombrissent l'écran (PANNEAUX_EXCLUS). tuiles=panneau suit.
PANNEAUX_VARIABLE = "--midnight-alpha-65"
PANNEAUX_EXCLUS = ("overlay", "--dimmed")
# v14 (2026-11-09, mod diag « fonds » sur le Portail : Messages = #0D0E11 75 %) : les grands panneaux des pages sont
# des « blocs » (.siblock-border, message-container-frame, cartes de rapport…) au fond var(--layout-modules-block-surface)
# (FM : var(--colours-alpha-dark-75)) : la variable elle-même prend la couleur des panneaux. v11 / v13 (tuiles non
# cliquables, cartes FigmaBaseCard) : fausses pistes, retirées
PANNEAUX_VARIABLES = ["--layout-modules-block-surface"]
# fiche (2026-11-09, le joueur : « la tuile du milieu de joueur… que la fiche joueur ») : fond propre du bloc des
# attributs de la fiche (FM : var(--layout-modules-block-surface)) ; classe utilisée seulement par
# PlayerAttributesLargeBlock (les variantes compactes mid / min servent aussi à l'infobulle : pas touchées)
FICHE_SELECTEURS = [("frames-player-attributes-full-block-size-max-rows",)]
# boutons (2026-11-08, le joueur : « partout où tu vois du violet, la couleur doit être liée au gros bouton en haut à
# droite ») : boutons d'action en dégradé, bouton Continuer / Messages ET tout le violet / rose qui les suit (liens,
# onglets, sélections, montants…) = tout ce que fait l'accent. Choisie, elle passe avant l'accent.
# postes (2026-11-09, le joueur : les couleurs des postes de l'écran Tactiques, une par poste) : clé -> (poste dans les
# variables de FM --colours-tactics-<poste>-foreground / -background, couleur de FM). Seules les règles des Tactiques
# (POSTES_PREFIXES) prennent la couleur choisie (en dur, à la place de var(...)) ; les autres usages de ces variables
# (calendrier, graphes…) gardent FM. Le fond « -background » (survol, case de fond) = la couleur assombrie (POSTES_FOND)
POSTES = {"poste_gb": ("goalkeeper", "#3C3C5A"), "poste_d": ("defender", "#02796F"),
          "poste_dm": ("defensive-midfield", "#0D7741"), "poste_mc": ("midfield", "#08397D"),
          "poste_mo": ("attacking-midfield", "#5F1084"), "poste_bt": ("striker", "#8D1363")}
POSTES_PREFIXES = ("tactics-visualiser-player", "data_display-tables-player_position")
POSTES_FOND = 0.55              # clarté du fond = clarté de la couleur choisie × ceci
# =====================================================================================================

MARKER =os.path.join(backup.BACKUP_DIR, "couleurs_interface.actif")
CLES = ("barre", "texte", "barre2", "accent", "liseret", "tac_barre", "tac_panneau", "tac_terrain",
        "tuiles", "score_fond", "score_bande", "match_boutons", "match_effectif", "commentaire", "menus", "boutons",
        "panneaux", "fiche", *POSTES, "continuer", "continuer_alerte", "continuer_traitement", "continuer_match",
        "touche", "touche_long", "touche_force")
# bouton Continuer en alerte / pendant le traitement / les jours de match (2026-11-11, le joueur) : couleur, None =
# celle de FM ; dans les thèmes de l'app (nuance de la couleur du bouton, page.html nuanceContinuer)
CONTINUER_EN_PLUS = {"continuer_alerte": "alerte", "continuer_traitement": "traitement", "continuer_match": "match"}
# touche de couleur du club sur une barre unie (2026-11-11, ESSAI, touche_club.py) : style (net / doux / halo / liseret
# / deux, None = aucune), longueur et force en % ; seulement si « barre » est choisie
TOUCHE = ("touche", "touche_long", "touche_force")
CONTINUER =("fm", "theme", "club")   # clé « continuer » : None = auto (theme si boutons / accent choisis, sinon fm)
COULEURS = CLES[:4]            # couleurs des barres (le trait entre les barres se cache dès qu'une est choisie)
TACTIQUES = ("tac_barre", "tac_panneau", "tac_terrain")
AUTRES = ("tuiles", "score_fond", "score_bande", "match_boutons", "match_effectif",
          "commentaire", "menus", "boutons", "panneaux", "fiche", *POSTES, "continuer",
          *CONTINUER_EN_PLUS)   # ne cachent pas le trait entre les barres non plus
MODELE_COMMENTAIRE = "MatchCommentaryBar"
COMMENTAIRE_REPERE = "CommentaryBar"
CLASSES_CLUB = ("fm-club-primary-color", "fm-club-secondary-color")   # posées par le SIStyleSetter (couleurs du club)
MARQUE_COMMENTAIRE = "uipicker-couleurs-commentaire-v2"
# v2 (2026-11-09, retour de Bat : barre blanche avec Minuit glacé) : la fonction du SIStyleSetter (couleur principale du
# club -> fond de l'enfant, en code) passait devant notre style intégré : vidée
GUID_FOND_CLUB = "76b11a74d053f6a469f7dd0da19d3c91"
MATCH = os.path.join(nb.AA, "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle")
MODELE_SCORE = "Scoreboard"     # 3 modèles de ce nom : celui de base est celui qui contient #scorebar
SCORE_REPERE = "scorebar"
MARQUE_SCORE = "uipicker-couleurs-score-v2"   # v2 : opacité
MODELE_TACTIQUES = "TacticalPlannerHeader"
FN_DEGRADE_TACTIQUES = "47578265f34902049a44904bda1f1db1"
MARQUE_TACTIQUES = "uipicker-couleurs-tactiques-v2"   # v2 : opacité
LISERET = "IsEmployedDivider"   # trait entre les 2 barres (OverviewTitleBar)
CACHE, AFFICHE = "cache", "fm"   # liseret None = auto (caché si une couleur est choisie)
sm.PROPRIETES.setdefault("display-mot-cle", (131081, 1))   # StylePropertyId Display ; mot-clé None = 6
AUCUN = 6
MARQUE = "uipicker-couleurs-v16"   # v16 (2026-11-11) : touche de couleur du club sur la barre unie (touche_club) ; v15 (2026-11-09) : tuiles = aussi les cartes de l'en-tête de la fiche ; v14 (2026-11-09) : panneaux = variable des blocs ; v13 : cartes ; v12 : fiche ; v11 (2026-11-09) : panneaux = aussi tuiles non cliquables ; v10 : panneaux ; v9 (2026-11-08) : menus / fenêtres, boutons d'action ; v8 (2026-11-07) : match (boutons du haut à droite, effectif, commentaire) ; v7 (2026-11-07) : opacité de chaque couleur (#RRGGBBAA) ; v6 (2026-11-07) : tuiles=panneau ; v5 (2026-11-06) : pelouse réparée, tuiles, tableau de score ; v4 : texte de la barre
#                                    d'avant-match (2026-10-30) ; marque() reconnaît toutes les versions
MODELE_BARRE = "PrimaryNavigationBarGradient"
MODELE_BARRE2 = "SecondaryNavigationBar"
MODELE_TEXTE = "PrimaryNavigationBar"
MODELE_SEPARATEUR = "OverviewTitleBar"
MODELE_AVANT_MATCH = "TeamSelectionTitleBar"   # barre de l'écran d'avant-match (même #NavThemeStyleSetter)
SOURCE_VE = "PrimaryNavigationBarClubColours"   # un VisualElement simple (#Employed) : données recopiées
FN_DEGRADE = "9f6121106098fd4478470df83d3e70ee"
THEME_SETTER = "NavThemeStyleSetter"
STYLES = [os.path.join(nb.AA, "ui-styles_assets_common.bundle"), os.path.join(nb.AA, "ui-styles_assets_default.bundle")]
FEUILLE_TEXTE = "AlwaysAppliedStyleSheet"
SPECIFICITE = 1000              # règles du texte : passent devant celles de FM (survol, onglet actif...)
COULEUR_ID, TEINTE_ID, FOND_ID = 65536, 196610, 458752
# niveaux de connaissance (2026-11-10, fonction recrutement\connaissance_couleurs, son marqueur) : FM colore le niveau
# (pays / régions de « Connaissance du monde », connaissance du recruteur…) par 10 classes (KnowledgeLevelDataCollection,
# valeur 0-100 : 5/10/15/20/25/30/45/60/80/100), dont 5 en blanc. Ici : une échelle rouge -> vert, règles ajoutées à
# AlwaysAppliedStyleSheet (spécificité SPECIFICITE : devant celles de FM, partagées avec d'autres classes)
CONNAISSANCE_MARKER = os.path.join(backup.BACKUP_DIR, "connaissance_couleurs.actif")
CONNAISSANCE = {
    "data_knowledge_level_0_basic": "#DC3B3B", "data_knowledge_level_1_average": "#EA5A2E",
    "data_knowledge_level_2_reasonable": "#F2792A", "data_knowledge_level_3_decent": "#F59E0B",
    "data_knowledge_level_4_good": "#FACC15", "data_knowledge_level_5_verygood": "#D4DA3A",
    "data_knowledge_level_6_superb": "#A3D635", "data_knowledge_level_7_outstanding": "#7BCB2E",
    "data_knowledge_level_8_exceptional": "#4ADE80", "data_knowledge_level_9_peerless": "#22C55E",
}
DRY_RUN = "--dry-run" in sys.argv


# ---------- couleurs ----------
def to_rgb(c):
    import theme_fond
    return theme_fond.to_rgb(c)


def alpha(c):
    """opacité (0..1) choisie dans l'app (#RRGGBBAA), 1 sinon"""
    import theme_fond
    return theme_fond.alpha(c)


def code(c):
    """couleur donnée -> "#RRGGBB", ou "#RRGGBBAA" si elle n'est pas opaque"""
    a = alpha(c)
    return hexa(to_rgb(c)) + ("%02X" % round(a * 255) if a < 1 else "")


def pct(a):
    return f" à {round(a * 100)} %" if a < 1 else ""


def hexa(rgb):
    return None if rgb is None else "#%02X%02X%02X" % tuple(rgb)[:3]


def luminance(rgb):
    return (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255


def recolorer(rgb, accent, ref=ACCENT_REF):
    """couleur de FM -> même nuance dans la teinte choisie (ref -> accent)"""
    h0, l0, s0 = colorsys.rgb_to_hls(*(v / 255 for v in to_rgb(ref)))
    ha, la, sa = colorsys.rgb_to_hls(*(v / 255 for v in accent))
    _, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    s2 = min(1.0, s * sa / s0) if s0 else sa
    l2 = l + (1 - l) * (la - l0) / (1 - l0) if la >= l0 else l * la / l0
    return _garde_contraste(rgb, ha, max(0.0, min(1.0, l2)), s2)


def _lum_rel(rgb):
    """luminance relative (WCAG)"""
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _garde_contraste(rgb, h, l, s):
    """même clarté HLS ≠ même luminosité (gris, jaune, bleu clair sont bien plus lumineux que le violet de FM) :
    la couleur garde au moins le contraste qu'avait celle de FM (plafonné à CONTRASTE_MINI) avec le texte blanc
    (couleur sombre de FM : fonds de boutons, bandeaux) ou noir (couleur claire : textes sur fond sombre)"""
    def vers(x):
        return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, x, s))
    y0 = _lum_rel(rgb)
    sombre = y0 < 0.179   # contraste avec le blanc meilleur qu'avec le noir
    def contraste(y):
        return 1.05 / (y + 0.05) if sombre else (y + 0.05) / 0.05
    cible = min(contraste(y0), CONTRASTE_MINI)
    if contraste(_lum_rel(vers(l))) >= cible:
        return vers(l)
    bas, haut = (0.0, l) if sombre else (l, 1.0)   # sombre : on assombrit ; clair : on éclaircit
    for _ in range(30):
        m = (bas + haut) / 2
        if (contraste(_lum_rel(vers(m))) >= cible) == sombre:
            bas = m
        else:
            haut = m
    return vers(bas if sombre else haut)


def config():
    """réglages enregistrés : {clé: "#RRGGBB" ou None (FM / auto)}"""
    try:
        m = json.load(open(MARKER, encoding="utf-8"))
    except Exception:
        m = {}
    return {k: m.get(k) for k in CLES}


def liseret_cache(cfg):
    """trait entre les barres caché ? choix explicite, sinon caché dès qu'une couleur est choisie"""
    if cfg["liseret"] in (CACHE, AFFICHE):
        return cfg["liseret"] == CACHE
    return any(cfg[k] for k in COULEURS)


def texte_voulu(cfg):
    """(classe forcée « clair » True / « foncé » False / None = FM, couleur des règles ajoutées ou None)"""
    if cfg["texte"]:
        rgb = to_rgb(cfg["texte"])
        return luminance(rgb) >= 0.5, (None if hexa(rgb) == "#FFFFFF" and alpha(cfg["texte"]) >= 1 else rgb)
    if cfg["barre"]:   # auto : blanc, sauf barre très claire
        return luminance(to_rgb(cfg["barre"])) < TEXTE_SEUIL_NOIR, None
    return None, None


# ---------- feuilles de style (partagées avec theme_fond) ----------
def _rgba(tt, rgb, a=1.0):
    tt.setdefault("colors", []).append({"r": rgb[0] / 255, "g": rgb[1] / 255, "b": rgb[2] / 255, "a": a})
    return len(tt["colors"]) - 1


def _rgb_de(c):
    return tuple(round(c[k] * 255) for k in "rgb")


def _famille_accent(rgb):
    """violet / rose / framboise de FM (pas le jaune du thème du jour de clôture du mercato, TransferDeadlineDay)"""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    return (h * 360 >= TEINTES_ACCENT[0] or h * 360 <= TEINTES_ACCENT[1]) and s > 0.15


def _accent_violet(rgb):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    return TEINTES_DURES[0] <= h * 360 <= TEINTES_DURES[1] and s > 0.3


def _infobulle(tt, rgb):
    import theme_fond
    hit = False
    for rule in tt.get("m_Rules") or []:
        if not any(len(cs["m_Selectors"]) == 1 and [(p["m_Type"], p["m_Value"]) for p in cs["m_Selectors"][0]["m_Parts"]]
                   == [(3, theme_fond.INFOBULLE_CLASSE)] for cs in rule["m_ComplexSelectors"]):
            continue
        for p in rule["m_Properties"]:
            if p["m_Id"] == FOND_ID:
                # 4e valeur = opacité choisie (theme_fond.colour2)
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb[:3], rgb[3] if len(rgb) > 3 else 1.0)}]
                hit = True
    return hit


def _accent(tt, accent, durs, a=1.0):
    """variables d'accent + violets écrits en dur ; renvoie le nombre de valeurs changées"""
    n = 0
    for rule in tt.get("m_Rules") or []:
        for p in rule["m_Properties"]:
            nom = p.get("m_Name") or p.get("m_CustomName") or ""
            var = nom in VARIABLES_ACCENT
            if nom.startswith("--") and not var:
                continue
            for v in p["m_Values"]:
                if v["m_ValueType"] != 4:
                    continue
                c = tt["colors"][v["valueIndex"]]
                rgb = _rgb_de(c)
                if (var and _famille_accent(rgb)) or rgb in durs:
                    v["valueIndex"] = _rgba(tt, recolorer(rgb, accent), c["a"] * a)   # opacité de FM × la choisie
                    n += 1
    return n


def _selecteurs(rule):
    return [[p["m_Value"] for s in cs["m_Selectors"] for p in s["m_Parts"]] for cs in rule["m_ComplexSelectors"]]


def _tactiques(tt, panneau, terrain, a_panneau=1.0, a_terrain=1.0):
    """écran Tactiques : panneau (variables + verts en dur des règles « tactic ») et pelouse ; renvoie le nombre changé.
    Panneau sans terrain choisi : pelouse fixée au vert de FM (elle lisait --colours-tactics-base-50, recolorée)"""
    n = 0
    durs = {to_rgb(c) for c in TAC_PANNEAU_DURS}
    if panneau and not terrain:
        terrain = to_rgb(TAC_TERRAIN_FM)
    for rule in tt.get("m_Rules") or []:
        sels = _selecteurs(rule)
        tactique = any("tactic" in str(v) for s in sels for v in s)
        pelouse = any(s == [TAC_TERRAIN_CLASSE] for s in sels)
        if sels == [[SURBRILLANCE_CLASSE]]:
            continue   # _surbrillance
        for p in rule["m_Properties"]:
            nom = p.get("m_Name") or p.get("m_CustomName") or ""
            if terrain and pelouse and p["m_Id"] == FOND_ID:
                # var(--colours-tactics-base-50) = 3 valeurs (fonction var, nombre d'arguments, nom) : TOUTE la valeur
                # est remplacée (2026-11-06 : seul le nom l'était -> var(#couleur) invalide, pelouse jamais changée,
                # Kiliwick / Lampardovic)
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, terrain, a_terrain)}]
                n += 1
                continue
            for v in p["m_Values"]:
                if panneau and v["m_ValueType"] == 4:
                    c = tt["colors"][v["valueIndex"]]
                    rgb = _rgb_de(c)
                    if (nom == "--pitch-tile-default-background" or nom in TAC_VARIABLES
                            or (tactique and not nom.startswith("--") and rgb in durs)):
                        v["valueIndex"] = _rgba(tt, recolorer(rgb, panneau, TAC_PANNEAU_FM), c["a"] * a_panneau)
                        n += 1
    return n


def fond_poste(rgb):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l * POSTES_FOND, s))


def _postes(tt, choix):
    """couleurs des postes (Tactiques) : choix = {poste FM: (rgb, opacité)} ; règles des Tactiques qui lisent
    var(--colours-tactics-<poste>-foreground / -background) -> la couleur en dur ; renvoie le nombre changé"""
    n = 0
    noms = {}
    for poste, (rgb, a) in choix.items():
        noms[f"--colours-tactics-{poste}-foreground"] = (rgb, a)
        noms[f"--colours-tactics-{poste}-background"] = (fond_poste(rgb), a)
    S = tt.get("strings") or []
    for rule in tt.get("m_Rules") or []:
        if not any(str(v).startswith(POSTES_PREFIXES) for s in _selecteurs(rule) for v in s):
            continue
        for p in rule["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] == 8 and v["valueIndex"] < len(S) and S[v["valueIndex"]] in noms:
                    rgb, a = noms[S[v["valueIndex"]]]
                    # var(...) = 3 valeurs (fonction, nombre d'arguments, nom) : toute la valeur remplacée
                    p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]
                    n += 1
                    break
    return n


def couleur_surbrillance(panneau, accent=None):
    """surbrillance des lignes au glisser (Tactiques) = couleur du bouton Continuer (en haut à droite) : `boutons`
    (sinon `accent`, sinon violet de FM ; le joueur, 2026-11-09 : « lie-la au bouton », « PAS VERT »), éclaircie (ou
    foncée sur panneau clair) tant que son contraste avec le panneau est sous SURBRILLANCE_CONTRASTE"""
    c = accent or to_rgb(ACCENT_REF)
    yp = _lum_rel(panneau)
    pas = 0.03 if yp < 0.179 else -0.03   # panneau sombre : plus clair ; panneau clair : plus foncé
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    while True:
        rgb = tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))
        y = _lum_rel(rgb)
        if (max(y, yp) + 0.05) / (min(y, yp) + 0.05) >= SURBRILLANCE_CONTRASTE or not 0 < l + pas < 1:
            return rgb
        l += pas


def _surbrillance(tt, rgb):
    n = 0
    for rule in tt.get("m_Rules") or []:
        if _selecteurs(rule) != [[SURBRILLANCE_CLASSE]]:
            continue
        for p in rule["m_Properties"]:
            if p["m_Id"] == FOND_ID:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, SURBRILLANCE_ALPHA)}]
                n += 1
    return n


def survol_tuiles(rgb):
    """couleur du survol des tuiles : la couleur choisie un peu plus claire (plus foncée si elle est déjà très claire)"""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in rgb))
    l = l + TUILES_SURVOL if l + TUILES_SURVOL <= 0.95 else l - TUILES_SURVOL
    return tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l, s))


def tuiles_voulues(cfg):
    """(rgb, alpha) du fond des tuiles, ou None (FM) ; « panneau » = fond du grand panneau (transparent)"""
    v = cfg.get("tuiles")
    if not v:
        return None
    if v == TUILES_PANNEAU:   # comme le grand panneau : sa couleur choisie, sinon celle de FM
        if cfg.get("panneaux"):
            return to_rgb(cfg["panneaux"]), alpha(cfg["panneaux"])
        return to_rgb(TUILES_PANNEAU_RGB), TUILES_PANNEAU_ALPHA
    return to_rgb(v), alpha(v)


def _tuiles(tt, rgb, alpha=1.0):
    """fond des tuiles / cartes (variables, valeur var(...) de FM remplacée par la couleur) ; renvoie le nombre"""
    n = 0
    survol = survol_tuiles(rgb)
    for rule in tt.get("m_Rules") or []:
        for p in rule["m_Properties"]:
            nom = p.get("m_Name") or p.get("m_CustomName") or ""
            c = rgb if nom in TUILES_VARIABLES else survol if nom in TUILES_VARIABLES_SURVOL else None
            if c is not None:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, c, alpha)}]
                n += 1
    return n


def _entete_cartes(tt, rgb, a=1.0):
    """« .ENTETE_CARTE { fond } » ajoutée à la fin de la feuille (spécificité SPECIFICITE : devant la règle d'une
    classe d'entete_tuile)"""
    idx = len(tt["m_Rules"])
    tt["m_Rules"].append({"m_ComplexSelectors": [{"m_Specificity": SPECIFICITE, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": ENTETE_CARTE, "m_Type": 3}], "m_PreviousRelationship": 0}]}],
        "line": -1, "m_Properties": [{"m_Id": FOND_ID, "m_CustomName": "", "m_Line": -1,
                                      "m_Values": [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]}]})


def _fonds_classes(tt, classes, rgb, a=1.0, texte=False):
    """match : fond des règles dont un sélecteur a une classe commençant par l'une de « classes » (le survol : un
    peu plus clair) ; texte : couleur du texte foncée dans les règles hors survol si la couleur est claire.
    Renvoie le nombre de règles changées"""
    n = 0
    survol = survol_tuiles(rgb)
    fonce = texte and luminance(rgb) >= MATCH_SEUIL_CLAIR
    regles = tt.get("m_Rules") or []

    def a_nous(cs):
        return any(isinstance(p["m_Value"], str) and p["m_Value"].startswith(classes)
                   for s in cs["m_Selectors"] for p in s["m_Parts"])

    for rule in list(regles):
        css = rule.get("m_ComplexSelectors") or []
        nous = [cs for cs in css if a_nous(cs)]
        if not nous:
            continue
        if len(nous) < len(css):
            # règle partagée avec d'autres éléments (boutons de l'iPhone, recherche du recrutement…) : nos sélecteurs
            # partent dans une copie ajoutée à la fin, l'originale garde les autres
            rule["m_ComplexSelectors"] = [cs for cs in css if not a_nous(cs)]
            rule = copy.deepcopy(rule)
            idx = len(regles)
            rule["m_ComplexSelectors"] = copy.deepcopy(nous)
            for cs in rule["m_ComplexSelectors"]:
                cs["ruleIndex"] = idx
            regles.append(rule)
        sels = _selecteurs(rule)
        if any(x in str(v) for s in sels for v in s for x in ("disabled", "active", "focus", "checked")):
            continue   # états (désactivé…) : couleurs de FM
        hover = any("hover" in str(v) for s in sels for v in s)
        fait = False
        for p in rule["m_Properties"]:
            if p["m_Id"] == FOND_ID:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, survol if hover else rgb, a)}]
                fait = True
        if fonce and not hover:
            props = [p for p in rule["m_Properties"] if p["m_Id"] == COULEUR_ID]
            if not props:
                props = [{"m_Id": COULEUR_ID, "m_CustomName": "", "m_Line": -1, "m_Values": []}]
                rule["m_Properties"].append(props[0])
            for p in props:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, to_rgb(MATCH_TEXTE_FONCE))}]
            fait = True
        n += fait
    return n


def _menus(tt, rgb, a=1.0):
    """menus / fenêtres : variables du fond des fenêtres + fond des règles de MENUS_SELECTEURS ; renvoie le nombre de
    valeurs changées"""
    n = 0
    for rule in tt.get("m_Rules") or []:
        for p in rule["m_Properties"]:
            if (p.get("m_Name") or p.get("m_CustomName") or "") in MENUS_VARIABLES:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]
                n += 1
    return n + _fonds_selecteurs(tt, MENUS_SELECTEURS, rgb, a)


def _panneaux(tt, rgb, a=1.0):
    """fond des règles dont le fond est var(PANNEAUX_VARIABLE), sauf voiles (PANNEAUX_EXCLUS) ; renvoie le nombre"""
    n = 0
    chaines = tt.get("strings") or []
    for rule in tt.get("m_Rules") or []:
        for p in rule["m_Properties"]:   # variables des blocs (définies dans :root)
            if (p.get("m_Name") or p.get("m_CustomName") or "") in PANNEAUX_VARIABLES:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]
                n += 1
        if any(x in str(v) for s in _selecteurs(rule) for v in s for x in PANNEAUX_EXCLUS):
            continue
        for p in rule["m_Properties"]:
            if p["m_Id"] == FOND_ID and any(v["m_ValueType"] == 8 and v["valueIndex"] < len(chaines)
                                            and chaines[v["valueIndex"]] == PANNEAUX_VARIABLE for v in p["m_Values"]):
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]
                n += 1
    return n


def _fonds_selecteurs(tt, selecteurs, rgb, a=1.0):
    """fond des règles dont un sélecteur est exactement l'une de ces suites de classes (règle partagée : nos sélecteurs
    dans une copie ajoutée à la fin, l'originale garde les autres) ; renvoie le nombre de valeurs changées"""
    n = 0
    regles = tt.get("m_Rules") or []
    cibles = set(selecteurs)

    def a_nous(cs):
        return tuple(p["m_Value"] for s in cs["m_Selectors"] for p in s["m_Parts"]) in cibles

    for rule in list(regles):
        css = rule.get("m_ComplexSelectors") or []
        nous = [cs for cs in css if a_nous(cs)]
        if not nous or not any(p["m_Id"] == FOND_ID for p in rule["m_Properties"]):
            continue
        if len(nous) < len(css):
            rule["m_ComplexSelectors"] = [cs for cs in css if not a_nous(cs)]
            rule = copy.deepcopy(rule)
            idx = len(regles)
            rule["m_ComplexSelectors"] = copy.deepcopy(nous)
            for cs in rule["m_ComplexSelectors"]:
                cs["ruleIndex"] = idx
            regles.append(rule)
        for p in rule["m_Properties"]:
            if p["m_Id"] == FOND_ID:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]
                n += 1
    return n


def _essai_pelouse(tt):
    """ESSAI_PELOUSE : fond des règles d'une seule classe / valeur des variables -> couleur vive ; renvoie le nombre"""
    n = 0
    for rule in tt.get("m_Rules") or []:
        sels = _selecteurs(rule)
        cible = next((ESSAI_PELOUSE[s[0]] for s in sels if len(s) == 1 and s[0] in ESSAI_PELOUSE), None)
        for p in rule["m_Properties"]:
            nom = p.get("m_Name") or p.get("m_CustomName") or ""
            c = ESSAI_PELOUSE.get(nom) if nom.startswith("--") else cible if p["m_Id"] == FOND_ID else None
            if c:
                p["m_Values"] = [{"m_ValueType": 4, "valueIndex": _rgba(tt, to_rgb(c))}]
                n += 1
    return n


def _partie(nom):
    return {"m_Value": nom[1:], "m_Type": 6} if nom.startswith("#") else {"m_Value": nom, "m_Type": 3}


def _texte(tt, rgb, a=1.0):
    """règles « .nav-on-dark .portal-text { color } » etc. ajoutées à la fin de la feuille"""
    for prop, cibles in ((COULEUR_ID, TEXTE_COULEUR), (TEINTE_ID, TEXTE_TEINTE)):
        idx = len(tt["m_Rules"])
        sels = [{"m_Specificity": SPECIFICITE, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": nav, "m_Type": 3}], "m_PreviousRelationship": 0},
            {"m_Parts": [_partie(c)], "m_PreviousRelationship": 2}]}
            for nav in ("nav-on-dark", "nav-on-light") for c in cibles]
        tt["m_Rules"].append({"m_ComplexSelectors": sels, "line": -1, "m_Properties": [
            {"m_Id": prop, "m_CustomName": "", "m_Line": -1,
             "m_Values": [{"m_ValueType": 4, "valueIndex": _rgba(tt, rgb, a)}]}]})


def _connaissance(tt):
    """une règle « .data_knowledge_level_N { color } » par niveau, ajoutée à la fin de la feuille"""
    for classe, c in CONNAISSANCE.items():
        idx = len(tt["m_Rules"])
        tt["m_Rules"].append({"m_ComplexSelectors": [{"m_Specificity": SPECIFICITE, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": classe, "m_Type": 3}], "m_PreviousRelationship": 0}]}], "line": -1,
            "m_Properties": [{"m_Id": COULEUR_ID, "m_CustomName": "", "m_Line": -1,
                              "m_Values": [{"m_ValueType": 4, "valueIndex": _rgba(tt, to_rgb(c))}]}]})
    return len(CONNAISSANCE)


def connaissance_active():
    return os.path.exists(CONNAISSANCE_MARKER)


def _infobulle_theme_fond():
    """fond des infobulles posé par theme_fond (son marqueur), ou None"""
    import theme_fond
    m = theme_fond.marker()
    if not m:
        return None
    c = m.get("infobulle") or theme_fond.INFOBULLE_DEFAUT
    if c is None:
        return None
    a = alpha(c)
    return to_rgb(c) + ((a,) if a < 1 else ())


def ecrire_styles(infobulle="marqueur", cfg=None, essai=False):
    """réécrit les 2 bundles de styles depuis leur original : infobulles (theme_fond) + accent + texte de la barre.
    Rien à poser -> bundles d'origine remis. essai : ESSAI_PELOUSE en plus."""
    if infobulle == "marqueur":
        infobulle = _infobulle_theme_fond()
    cfg = config() if cfg is None else cfg
    cle_accent = "boutons" if cfg.get("boutons") else "accent"   # boutons choisis : passent avant l'accent
    accent = to_rgb(cfg[cle_accent]) if cfg[cle_accent] else None
    texte = texte_voulu(cfg)[1]
    panneau = to_rgb(cfg["tac_panneau"]) if cfg.get("tac_panneau") else None
    terrain = to_rgb(cfg["tac_terrain"]) if cfg.get("tac_terrain") else None
    # opacités choisies (#RRGGBBAA, 1 = opaque)
    a_accent, a_texte = alpha(cfg[cle_accent]), alpha(cfg["texte"])
    a_panneau, a_terrain = alpha(cfg.get("tac_panneau")), alpha(cfg.get("tac_terrain"))
    tuiles, tuiles_alpha = tuiles_voulues(cfg) or (None, 1.0)
    # match : (clé, classes, texte foncé si couleur claire, nom dans le bilan)
    match = [(k, cls, txt, nom) for k, cls, txt, nom in (
        ("match_boutons", MATCH_BOUTONS_CLASSES, True, "boutons du match"),
        ("match_effectif", MATCH_EFFECTIF_CLASSES, False, "effectif du match")) if cfg.get(k)]
    menus = to_rgb(cfg["menus"]) if cfg.get("menus") else None
    a_menus = alpha(cfg.get("menus"))
    panneaux = to_rgb(cfg["panneaux"]) if cfg.get("panneaux") else None
    a_panneaux = alpha(cfg.get("panneaux"))
    fiche = to_rgb(cfg["fiche"]) if cfg.get("fiche") else None
    a_fiche = alpha(cfg.get("fiche"))
    postes = {POSTES[k][0]: (to_rgb(cfg[k]), alpha(cfg[k])) for k in POSTES if cfg.get(k)}
    connaissance = connaissance_active()
    if (infobulle is None and accent is None and texte is None and panneau is None and terrain is None
            and tuiles is None and not match and menus is None and panneaux is None and fiche is None
            and not postes and not essai and not connaissance):
        for path in STYLES:
            if os.path.exists(backup.backup_path(path)):
                if not DRY_RUN:
                    backup.restore(path)
                print(f"styles d'origine remis ({os.path.basename(path)})")
        return
    envs = {}
    for path in STYLES:
        src = backup.backup_path(path)
        envs[path] = UnityPy.load(src if os.path.exists(src) else path)   # repart de l'original
    feuilles = []
    for path, env in envs.items():
        for o in env.objects:
            if o.type.name != "MonoBehaviour":
                continue
            try:
                tt = o.read_typetree()
            except Exception:
                continue
            if "m_Rules" in tt:
                feuilles.append((path, o, tt))
    durs = set()   # valeurs d'origine des variables d'accent violettes
    if accent:
        for _, _, tt in feuilles:
            for rule in tt["m_Rules"]:
                for p in rule["m_Properties"]:
                    if (p.get("m_Name") or p.get("m_CustomName")) in VARIABLES_ACCENT:
                        for v in p["m_Values"]:
                            if v["m_ValueType"] == 4:
                                rgb = _rgb_de(tt["colors"][v["valueIndex"]])
                                if _accent_violet(rgb):
                                    durs.add(rgb)
    bilan = {p: [] for p in STYLES}
    for path, o, tt in feuilles:
        fait = []
        if infobulle is not None and _infobulle(tt, infobulle):
            fait.append("infobulles")
        if accent:
            n = _accent(tt, accent, durs, a_accent)
            if n:
                fait.append(f"{'boutons et violets' if cle_accent == 'boutons' else 'accent'} {n}")
        if menus:
            n = _menus(tt, menus, a_menus)
            if n:
                fait.append(f"menus {n}")
        if panneaux:
            n = _panneaux(tt, panneaux, a_panneaux)
            if n:
                fait.append(f"panneaux {n}")
        if fiche:
            n = _fonds_selecteurs(tt, FICHE_SELECTEURS, fiche, a_fiche)
            if n:
                fait.append(f"fiche joueur {n}")
        if texte is not None and tt.get("m_Name") == FEUILLE_TEXTE:
            _texte(tt, texte, a_texte)
            fait.append("texte de la barre")
        if panneau or terrain:
            n = _tactiques(tt, panneau, terrain, a_panneau, a_terrain)
            if n:
                fait.append(f"tactiques {n}")
        if panneau:
            n = _surbrillance(tt, couleur_surbrillance(panneau, accent))
            if n:
                fait.append(f"surbrillance au glisser {n}")
        if tuiles:
            n = _tuiles(tt, tuiles, tuiles_alpha)
            if n:
                fait.append(f"tuiles {n}")
            if tt.get("m_Name") == FEUILLE_TEXTE:
                _entete_cartes(tt, tuiles, tuiles_alpha)
                fait.append("cartes de l'en-tête")
        for k, cls, txt, nom in match:
            n = _fonds_classes(tt, cls, to_rgb(cfg[k]), alpha(cfg[k]), txt)
            if n:
                fait.append(f"{nom} {n}")
        if postes:   # après l'accent : la couleur choisie pour MO n'est pas recolorée
            n = _postes(tt, postes)
            if n:
                fait.append(f"postes {n}")
        if essai:
            n = _essai_pelouse(tt)
            if n:
                fait.append(f"ESSAI pelouse {n}")
        if connaissance and tt.get("m_Name") == FEUILLE_TEXTE:
            fait.append(f"niveaux de connaissance {_connaissance(tt)}")
        if fait:
            o.save_typetree(tt)
            bilan[path].append(f"{tt.get('m_Name')} ({', '.join(fait)})")
    for path, env in envs.items():
        nom = os.path.basename(path)
        if not bilan[path]:
            if os.path.exists(backup.backup_path(path)) and not DRY_RUN:
                backup.restore(path)
            print(f"{nom} : d'origine")
            continue
        data = env.file.save(packer="original")
        print(f"{nom} : " + " ; ".join(bilan[path]))
        if not DRY_RUN:
            backup.write_bundle(path, data)
    if infobulle is not None:
        print("infobulles : fond %s%s" % (hexa(infobulle), pct(infobulle[3] if len(infobulle) > 3 else 1.0)))
    if accent:
        print(("boutons d'action et tout le violet" if cle_accent == "boutons" else "accent")
              + f" : {hexa(accent)}{pct(a_accent)}")
    if texte is not None:
        print(f"texte de la barre : {hexa(texte)}{pct(a_texte)}")
    if panneau:
        print(f"tactiques, panneau : {hexa(panneau)}{pct(a_panneau)}")
    if terrain:
        print(f"tactiques, terrain : {hexa(terrain)}{pct(a_terrain)}")
    if tuiles:
        transp = (pct(tuiles_alpha) + " (comme le grand panneau)" if cfg.get("tuiles") == TUILES_PANNEAU
                  else pct(tuiles_alpha))
        print(f"tuiles : {hexa(tuiles)}{transp} (survol {hexa(survol_tuiles(tuiles))})")
    for k, _, txt, nom in match:
        rgb = to_rgb(cfg[k])
        print(f"{nom} : {hexa(rgb)}{pct(alpha(cfg[k]))} (survol {hexa(survol_tuiles(rgb))})"
              + (" (texte foncé)" if txt and luminance(rgb) >= MATCH_SEUIL_CLAIR else ""))
    if menus:
        print(f"menus et fenêtres : {hexa(menus)}{pct(a_menus)}")
    if panneaux:
        print(f"grands panneaux : {hexa(panneaux)}{pct(a_panneaux)}")
    if fiche:
        print(f"grande tuile de la fiche joueur : {hexa(fiche)}{pct(a_fiche)}")
    for poste, (rgb, a) in postes.items():
        print(f"poste {poste} : {hexa(rgb)}{pct(a)} (fond {hexa(fond_poste(rgb))})")


# ---------- tableau de score de base (bundle du match) ----------
sm.PROPRIETES.setdefault("color", (COULEUR_ID, 4))


def _modele_score():
    """(objet, typetree, Tree) du Scoreboard de base (celui qui contient #scorebar), ou None"""
    if not os.path.exists(MATCH):
        return None
    for o in nb.env_of(MATCH).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != MODELE_SCORE:
                continue
        except Exception:
            continue
        deja = nb._ecrits.get((MATCH, o.path_id))
        tt = copy.deepcopy(deja) if deja is not None else o.read_typetree()
        if "m_VisualTree" not in tt:
            continue
        t = sm.Tree(tt)
        if any(t.name(r) == SCORE_REPERE for r in t.walk()):
            return o, tt, t
    return None


def _marque_score(t):
    pref = MARQUE_SCORE.rsplit("-v", 1)[0] + "-v"
    return any(c.startswith(pref) for r in t.walk() for c in (t.elem(r).get("m_Classes") or []))


def _fond_inline(t, r):
    """couleur de fond (#RRGGBB) du style intégré de l'élément, ou None"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx is None or idx < 0:
        return None
    try:
        props = t.styles.values(idx)
    except ValueError:
        return None
    for pid, _, vals in props:
        if pid == FOND_ID and vals and vals[0][0] == 4:
            c = vals[0][1]
            return hexa(tuple(round(c[k] * 255) for k in "rgb"))
    return None


def _textes(t, r):
    """SIText / Label sous l'élément r (lui compris)"""
    return [k for k in t.walk(r) if (t.elem(k).get("m_FullTypeName") or "").endswith(("SIText", "Label"))]


def tableau_score(cfg):
    """cases sombres / bande des noms du tableau de score de base : repart de l'original du modèle, couleurs posées
    dans ses styles intégrés ; rien de choisi = modèle d'origine remis (s'il avait été touché)"""
    fond = to_rgb(cfg["score_fond"]) if cfg.get("score_fond") else None
    bande = to_rgb(cfg["score_bande"]) if cfg.get("score_bande") else None
    a_fond, a_bande = alpha(cfg.get("score_fond")), alpha(cfg.get("score_bande"))
    trouve = _modele_score()
    if trouve is None:
        print(f"{MODELE_SCORE} (tableau de score) : introuvable (le jeu a changé ?)")
        return
    obj, tt, t = trouve
    t.styles = sm.Styles(MATCH, tt)
    pose = _marque_score(t)
    if fond is None and bande is None and not pose:
        return   # d'origine et rien à faire
    orig = original(MATCH, obj)
    if orig is None:
        if pose:
            print(f"{MODELE_SCORE} : pas de sauvegarde d'origine, laissé tel quel")
            return
    else:
        feuille = original(MATCH, obj, orig["inlineSheet"]["m_PathID"])
        tt, t = orig, sm.Tree(orig)
        t.styles = sm.Styles(MATCH, tt)
        if feuille is not None:   # feuille d'origine aussi : les règles des passages précédents ne s'empilent pas
            t.styles.sh, t.styles.changed = feuille, True
    msgs = []
    if fond is not None or bande is not None:
        clair = fond is not None and luminance(fond) >= SCORE_SEUIL_CLAIR
        fonce = bande is not None and luminance(bande) < SCORE_SEUIL_FONCE
        n_fond = n_bande = 0
        for r in list(t.walk()):
            c = _fond_inline(t, r)
            if fond is not None and c == SCORE_FOND_FM:
                t.styles.style(t, r, {"background-color": tuple(v / 255 for v in fond) + (a_fond,)})
                n_fond += 1
                if clair:   # texte blanc de FM illisible sur une case claire (sauf petits textes violets)
                    for k in _textes(t, r):
                        if not any("ultra-violet" in x for x in (t.elem(k).get("m_Classes") or [])):
                            t.styles.style(t, k, {"color": tuple(v / 255 for v in to_rgb(SCORE_TEXTE_FONCE)) + (1.0,)})
            elif bande is not None and c == SCORE_BANDE_FM:
                t.styles.style(t, r, {"background-color": tuple(v / 255 for v in bande) + (a_bande,)})
                n_bande += 1
                if fonce:
                    for k in _textes(t, r):
                        t.styles.style(t, k, {"color": (1.0, 1.0, 1.0, 1.0)})
        if fond is not None:
            msgs.append(f"{n_fond} case(s) -> {hexa(fond)}{pct(a_fond)}" + (" (texte foncé)" if clair else ""))
        if bande is not None:
            msgs.append(f"{n_bande} bande(s) des noms -> {hexa(bande)}{pct(a_bande)}" + (" (noms en blanc)" if fonce else ""))
        if not n_fond and not n_bande:
            print(f"{MODELE_SCORE} : couleurs de FM introuvables (le jeu a changé ?), rien fait")
            return
        rid = next(r for r in t.walk() if t.name(r) == SCORE_REPERE)
        t.elem(rid)["m_Classes"] = list(t.elem(rid).get("m_Classes") or []) + [MARQUE_SCORE]
    else:
        msgs.append("remis d'origine")
    import score_disposition   # match_haut : disposition du tableau (repartie de l'original ici) reposée
    if score_disposition.actif():
        score_disposition.CFG_THEME = cfg   # couleur des cases (score_fond) de CE passage, pas l'ancienne sauvegarde
        msgs += score_disposition.disposer(t)
    t.finish()
    t.styles.save()
    for n in score_disposition.types_ref_manquants(obj, tt):   # fondus du tableau (SIGradient)
        msgs.append(f"type {n} déclaré dans le bundle")
    obj.save_typetree(tt)
    nb._ecrits[(MATCH, obj.path_id)] = tt
    nb._dirty.add(MATCH)
    print(f"{MODELE_SCORE} (tableau de score) : " + " ; ".join(msgs))


def _modele_commentaire():
    """(objet, typetree, Tree) de MatchCommentaryBar (celui qui contient #CommentaryBar), ou None"""
    if not os.path.exists(MATCH):
        return None
    for o in nb.env_of(MATCH).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != MODELE_COMMENTAIRE:
                continue
        except Exception:
            continue
        deja = nb._ecrits.get((MATCH, o.path_id))
        tt = copy.deepcopy(deja) if deja is not None else o.read_typetree()
        if "m_VisualTree" not in tt:
            continue
        t = sm.Tree(tt)
        if any(t.name(r) == COMMENTAIRE_REPERE for r in t.walk()):
            return o, tt, t
    return None


def _marque_commentaire(t):
    pref = MARQUE_COMMENTAIRE.rsplit("-v", 1)[0] + "-v"
    return any(c.startswith(pref) for r in t.walk() for c in (t.elem(r).get("m_Classes") or []))


def barre_commentaire(cfg):
    """barre de commentaire du match : repart de l'original du modèle ; couleur choisie = classes des couleurs du club
    retirées, fond + texte en style intégré ; rien de choisi = modèle d'origine remis (s'il avait été touché)"""
    fond = to_rgb(cfg["commentaire"]) if cfg.get("commentaire") else None
    trouve = _modele_commentaire()
    if trouve is None:
        print(f"{MODELE_COMMENTAIRE} (barre de commentaire) : introuvable (le jeu a changé ?)")
        return
    obj, tt, t = trouve
    pose = _marque_commentaire(t)
    if fond is None and not pose:
        return   # d'origine et rien à faire
    t.styles = sm.Styles(MATCH, tt)
    orig = original(MATCH, obj)
    if orig is None:   # bundle jamais sauvegardé : le modèle est celui de FM
        if pose:
            print(f"{MODELE_COMMENTAIRE} : pas de sauvegarde d'origine, laissé tel quel")
            return
    else:
        feuille = original(MATCH, obj, orig["inlineSheet"]["m_PathID"])
        tt, t = orig, sm.Tree(orig)
        t.styles = sm.Styles(MATCH, tt)
        if feuille is not None:   # feuille d'origine aussi : les règles des passages précédents ne s'empilent pas
            t.styles.sh, t.styles.changed = feuille, True
    if fond is not None:
        texte = to_rgb(MATCH_TEXTE_FONCE) if luminance(fond) >= MATCH_SEUIL_CLAIR else (255, 255, 255)
        n_fond = n_texte = 0
        for r in list(t.walk()):
            cls = list(t.elem(r).get("m_Classes") or [])
            if CLASSES_CLUB[0] in cls:
                t.styles.style(t, r, {"background-color": tuple(v / 255 for v in fond) + (alpha(cfg["commentaire"]),)})
                n_fond += 1
            if CLASSES_CLUB[1] in cls:
                t.styles.style(t, r, {"color": tuple(v / 255 for v in texte) + (1.0,)})
                n_texte += 1
            if any(c in cls for c in CLASSES_CLUB):
                t.elem(r)["m_Classes"] = [c for c in cls if c not in CLASSES_CLUB]
        if not n_fond:
            print(f"{MODELE_COMMENTAIRE} : classe {CLASSES_CLUB[0]} introuvable (le jeu a changé ?), rien fait")
            return
        n_fct = 0
        for r in t.walk():
            f = t.sd(r).get("BindFunction")
            if isinstance(f, dict) and (f.get("m_target") or {}).get("m_guid") == GUID_FOND_CLUB:
                f["m_target"]["m_guid"] = ""
                f["m_inputs"]["m_variable"]["m_argumentBytes"] = []
                n_fct += 1
        if not n_fct:
            print(f"{MODELE_COMMENTAIRE} : fonction des couleurs du club introuvable (le jeu a changé ?), rien fait")
            return
        rid = next(r for r in t.walk() if t.name(r) == COMMENTAIRE_REPERE)
        t.elem(rid)["m_Classes"] = list(t.elem(rid).get("m_Classes") or []) + [MARQUE_COMMENTAIRE]
        msg = f"fond {hexa(fond)}{pct(alpha(cfg['commentaire']))}, texte {hexa(texte)} ({n_fond} fond, {n_texte} texte)"
    else:
        msg = "remise d'origine"
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(MATCH)
    print(f"{MODELE_COMMENTAIRE} (barre de commentaire) : {msg}")


# ---------- modèles ----------
def _ve_source():
    t = ouvrir(SOURCE_VE)[3]
    rid = next(r for r in t.walk() if t.name(r) == "Employed")
    e = t.elem(rid)
    return e["m_FullTypeName"], copy.deepcopy(t.refs[e["m_SerializedData"]["rid"]])


def en_fond_fixe(t, rid, rgb, ve, a=1.0):
    """SIGradient -> élément simple (VisualElement) au fond fixe ; classes, style et enfants gardés"""
    e = t.elem(rid)
    typ, ref = ve
    sd = t.refs[e["m_SerializedData"]["rid"]]
    ancien = sd["data"]
    data = copy.deepcopy(ref["data"])
    for k in data:
        if k in ancien:
            data[k] = ancien[k]
    sd["type"] = copy.deepcopy(ref["type"])
    sd["data"] = data
    e["m_FullTypeName"] = typ
    t.styles.style(t, rid, {"background-color": tuple(v / 255 for v in rgb) + (a,)})
    e["m_Classes"] = list(e.get("m_Classes") or []) + [MARQUE]


def degrades(t):
    out = []
    for r in t.walk():
        f = t.sd(r).get("BindGradientFunc")
        if isinstance(f, dict) and f["m_target"]["m_guid"] == FN_DEGRADE:
            out.append(r)
    return out


def classe_texte(t, clair):
    """#NavThemeStyleSetter : la condition « club foncé » devient toujours vraie (texte clair) ou fausse"""
    rid = next((r for r in t.walk() if t.name(r) == THEME_SETTER), None)
    if rid is None:
        return False
    vf = t.sd(rid)["BindFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    p = ("const.True" if clair else "const.False").encode()
    args[0][1] = b"\x01" + _enc_varint(len(p)) + p
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.elem(rid)["m_Classes"] = list(t.elem(rid).get("m_Classes") or []) + [MARQUE]
    return True


def marque(t):
    pref = MARQUE.rsplit("-v", 1)[0] + "-v"
    return any(c.startswith(pref) for r in t.walk() for c in (t.elem(r).get("m_Classes") or []))


def cacher_liseret(t):
    """#IsEmployedDivider (trait entre la barre du haut et la barre secondaire) : display: none"""
    rid = next((r for r in t.walk() if t.name(r) == LISERET), None)
    if rid is None:
        return False
    t.styles.style(t, rid, {"display-mot-cle": AUCUN})
    t.elem(rid)["m_Classes"] = list(t.elem(rid).get("m_Classes") or []) + [MARQUE]
    return True


def _degrade_tactiques(t):
    """SIGradient du bandeau des tactiques (fonction 47578265), ou None"""
    for r in t.walk():
        f = t.sd(r).get("BindGradientFunc")
        if isinstance(f, dict) and f["m_target"]["m_guid"] == FN_DEGRADE_TACTIQUES:
            return r
    return None


def _couleurs_degrade(t, r):
    """[(r, g, b, a)] des ColorVisualArg du dégradé"""
    args = decode_args(t.sd(r)["BindGradientFunc"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    return [struct.unpack("<4f", bytes(a[1][:16])) for a in args if a[0].endswith(b"ColorVisualArg")]


def bandeau_tactiques(cfg):
    """dégradé du bandeau des Tactiques : ses 2 couleurs seulement, sur le modèle tel qu'il est (partagé avec
    tactiques_boutons / effectif_equipes) ; sans couleur choisie = celles de l'original remises"""
    actuel = ouvrir(MODELE_TACTIQUES)
    if actuel is None or actuel[2] is None:
        print(f"{MODELE_TACTIQUES} : introuvable (le jeu a changé ?)")
        return
    bundle, obj, tt, t = actuel
    r = _degrade_tactiques(t)
    if r is None:
        print(f"{MODELE_TACTIQUES} : dégradé du bandeau introuvable (le jeu a changé ?)")
        return
    classes = t.elem(r).get("m_Classes") or []
    pose = any(c.startswith(MARQUE_TACTIQUES.rsplit("-v", 1)[0]) for c in classes)
    if not cfg.get("tac_barre") and not pose:
        return   # d'origine et rien à faire
    orig = original(bundle, obj)
    if orig is not None:
        to = sm.Tree(orig)
        ro = _degrade_tactiques(to)
        fm = _couleurs_degrade(to, ro) if ro is not None else None
    else:
        fm = None
    if fm is None:
        if pose:
            print(f"{MODELE_TACTIQUES} : pas de sauvegarde d'origine, dégradé laissé tel quel")
            return
        fm = _couleurs_degrade(t, r)
    if cfg.get("tac_barre"):
        choisi, a = to_rgb(cfg["tac_barre"]), alpha(cfg["tac_barre"])
        cibles = [tuple(v / 255 for v in recolorer(tuple(round(x * 255) for x in c[:3]), choisi, TAC_BARRE_FM)) + (c[3] * a,)
                  for c in fm]
    else:
        cibles = fm
    vf = t.sd(r)["BindGradientFunc"]["m_inputs"]["m_variable"]
    args = decode_args(vf["m_argumentBytes"])
    i = 0
    for a in args:
        if a[0].endswith(b"ColorVisualArg") and i < len(cibles):
            a[1] = struct.pack("<4f", *cibles[i]) + bytes(a[1][16:])
            i += 1
    vf["m_argumentBytes"] = encode_args(args)
    autres = [c for c in classes if not c.startswith(MARQUE_TACTIQUES.rsplit("-v", 1)[0])]
    t.elem(r)["m_Classes"] = autres + ([MARQUE_TACTIQUES] if cfg.get("tac_barre") else [])
    obj.save_typetree(tt)
    nb._dirty.add(bundle)
    if cfg.get("tac_barre"):
        degrade = " -> ".join(hexa(tuple(round(x * 255) for x in c[:3])) for c in cibles)
        print(f"{MODELE_TACTIQUES} : bandeau des tactiques {degrade}{pct(alpha(cfg['tac_barre']))}")
    else:
        print(f"{MODELE_TACTIQUES} : bandeau des tactiques remis aux couleurs de FM")


def modeles(cfg):
    """les 5 modèles, repris de l'original puis modifiés selon cfg (ou laissés d'origine)"""
    clair = texte_voulu(cfg)[0]
    cache = True if liseret_cache(cfg) else None
    ve = None
    # barre de l'écran d'avant-match : fond toujours sombre (midnight-background-colour), texte selon le club -> clair
    avant_match = True if clair is not None else None
    for modele, voulu in ((MODELE_BARRE, cfg["barre"]), (MODELE_BARRE2, cfg["barre2"]), (MODELE_TEXTE, clair),
                          (MODELE_SEPARATEUR, cache), (MODELE_AVANT_MATCH, avant_match)):
        actuel = ouvrir(modele)
        if actuel is None or actuel[2] is None:
            print(f"{modele} : introuvable (le jeu a changé ?)")
            continue
        if voulu is None and not marque(actuel[3]):
            continue   # d'origine et rien à faire
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marque(t):
            print(f"{modele} : pas de sauvegarde d'origine propre, rien fait")
            continue
        if voulu is None:
            msg = "remis d'origine"
        elif modele in (MODELE_TEXTE, MODELE_AVANT_MATCH):
            if not classe_texte(t, voulu):
                print(f"{modele} : #{THEME_SETTER} introuvable (le jeu a changé ?)")
                continue
            msg = "texte " + ("clair" if voulu else "foncé")
        elif modele == MODELE_SEPARATEUR:
            if not cacher_liseret(t):
                print(f"{modele} : #{LISERET} introuvable (le jeu a changé ?)")
                continue
            msg = "trait entre les barres caché"
        else:
            ve = ve or _ve_source()
            rgb = to_rgb(voulu)
            ds = degrades(t)
            if not ds:
                print(f"{modele} : dégradés introuvables (le jeu a changé ?)")
                continue
            touche = None
            for r in ds:
                if modele == MODELE_BARRE:   # avant l'aplat : les couches sont des copies du dégradé de FM
                    touche = touche_club.poser(t, t.styles, r, cfg) or touche
                en_fond_fixe(t, r, rgb, ve, alpha(voulu))
            msg = f"{len(ds)} dégradé(s) -> {hexa(rgb)}{pct(alpha(voulu))}" + (f", {touche}" if touche else "")
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        print(f"{modele} : {msg}")
    bandeau_tactiques(cfg)
    tableau_score(cfg)
    barre_commentaire(cfg)
    mode, couleur = continuer_voulu(cfg)
    bouton_continuer.appliquer(mode, couleur, en_plus=continuer_en_plus(cfg))
    nb.save_all()


def continuer_en_plus(cfg):
    """bouton Continuer en alerte / traitement : {alerte / traitement: (r, g, b, a)} des couleurs choisies"""
    return {e: tuple(to_rgb(cfg[k])) + (alpha(cfg[k]),) for k, e in CONTINUER_EN_PLUS.items() if cfg.get(k)}


def continuer_voulu(cfg):
    """bouton Continuer : (mode, couleur) ; auto = couleur du thème (boutons, sinon accent) si choisie, sinon FM"""
    c = cfg.get("boutons") or cfg.get("accent")
    mode = cfg.get("continuer") or ("theme" if c else "fm")
    if mode == "theme" and not c:
        mode = "fm"
    return mode, (tuple(to_rgb(c)) + (alpha(c),) if mode == "theme" else None)


# ---------- commandes ----------
def lire_args(args, cfg):
    for a in args:
        if "=" not in a:
            sys.exit(f"argument pas compris : {a!r} (ex. barre=#1D3B57 texte=auto barre2=fm accent=rouge)")
        k, v = (x.strip() for x in a.split("=", 1))
        k = k.lower()
        if k not in CLES:
            sys.exit(f"réglage inconnu : {k!r} ({', '.join(CLES)})")
        if k == "liseret":
            v = v.lower()
            if v not in ("", "auto", "fm", "base", "affiche", CACHE):
                sys.exit(f"liseret : {v!r} pas compris (cache, fm = trait affiché, auto)")
            cfg[k] = CACHE if v == CACHE else None if v in ("", "auto") else AFFICHE
            continue
        if k == "continuer":
            v = v.lower()
            if v not in ("", "auto", *CONTINUER):
                sys.exit(f"continuer : {v!r} pas compris ({', '.join(CONTINUER)}, auto)")
            cfg[k] = v if v in CONTINUER else None
            continue
        if k == "touche":
            v = v.lower()
            if v not in ("", "aucune", "fm", *touche_club.STYLES):
                sys.exit(f"touche : {v!r} pas compris ({', '.join(touche_club.STYLES)}, aucune)")
            cfg[k] = v if v in touche_club.STYLES else None
            continue
        if k in ("touche_long", "touche_force"):
            if not v.isdigit():
                sys.exit(f"{k} : {v!r} pas compris (nombre, en %)")
            cfg[k] = int(v)
            continue
        if k == "tuiles" and v.lower() == TUILES_PANNEAU:
            cfg[k] = TUILES_PANNEAU
            continue
        cfg[k] = None if v.lower() in ("", "fm", "auto", "base") else code(v)   # #RRGGBBAA : opacité gardée
    return cfg


def cmd_appliquer(args):
    cfg = lire_args(args, config())
    if not any(cfg[k] for k in COULEURS + TACTIQUES + AUTRES) and cfg["liseret"] != CACHE:
        return cmd_retirer()   # rien à poser (trait affiché = FM)
    modeles(cfg)
    ecrire_styles(cfg=cfg)
    for k in COULEURS + TACTIQUES + AUTRES:
        print(f"{k} : {cfg[k] or ('auto' if k == 'texte' else 'FM')}")
    print("trait entre les barres :", "caché" if liseret_cache(cfg) else "affiché (FM)",
          "" if cfg["liseret"] else "(auto)")
    if cfg["touche"]:
        print("touche du club :", cfg["touche"], "" if cfg["barre"] else "(sans effet : barre de FM)")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump(dict(actif=True, **cfg), f)
    else:
        print("(essai à blanc : rien écrit)")


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    vide = dict.fromkeys(CLES)
    modeles(vide)
    ecrire_styles(cfg=vide)   # garde les infobulles de theme_fond s'il est activé


def cmd_etat():
    cfg = config()
    for k, titre in zip(COULEURS + TACTIQUES + AUTRES,
                        ("barre du haut", "texte de la barre", "barre secondaire", "accent", "tactiques : bandeau",
                         "tactiques : panneau", "tactiques : terrain", "tuiles", "tableau de score : cases",
                         "tableau de score : bande des noms", "match : boutons du haut à droite",
                         "match : bandeau de l'effectif", "match : barre de commentaire",
                         "menus et fenêtres", "boutons d'action", "grands panneaux", "grande tuile de la fiche joueur",
                         "poste GB", "poste D", "poste AL / MD", "poste MC", "poste MO", "poste BT",
                         "bouton Continuer (fm / theme / club, vide = auto)", "bouton Continuer en alerte",
                         "bouton Continuer pendant le traitement", "bouton Continuer les jours de match")):
        print(f"{titre} : {cfg[k] or ('auto' if k == 'texte' else 'couleur de FM')}")
    actif = os.path.exists(MARKER)
    print("trait entre les barres :", "caché" if actif and liseret_cache(cfg) else "affiché (FM)",
          "(auto)" if actif and not cfg["liseret"] else "")
    for modele in (MODELE_BARRE, MODELE_BARRE2, MODELE_TEXTE, MODELE_SEPARATEUR, MODELE_AVANT_MATCH):
        o = ouvrir(modele)
        print(f"{modele} : " + ("modifié" if o and marque(o[3]) else "d'origine"))
    s = _modele_score()
    print(f"{MODELE_SCORE} (tableau de score) : " + ("introuvable" if s is None else
                                                     "modifié" if _marque_score(s[2]) else "d'origine"))
    s = _modele_commentaire()
    print(f"{MODELE_COMMENTAIRE} (barre de commentaire) : " + ("introuvable" if s is None else
                                                               "modifié" if _marque_commentaire(s[2]) else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer(argv[1:])
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer([])
        else:
            print("couleurs de l'interface : non activées, rien à faire")
    elif op == "tableau-score":   # tests (124) : seulement le tableau de score (bundle du match), marqueur pas touché
        if os.path.exists(MARKER):
            tableau_score(config())
            nb.save_all()
        else:
            print("couleurs de l'interface : non activées, rien à faire")
    elif op == "essai-pelouse":   # styles seuls, couleurs enregistrées + ESSAI_PELOUSE ; marqueur pas touché
        ecrire_styles(cfg=config(), essai=True)
        print("ESSAI pelouse : rouge = grass-colour, bleu = tactics-pitch-block, cyan = pitch-container, "
              "orange = visualiser-pitch, jaune = --pitch-tile-default-background, magenta = --colours-tactics-base-50")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
