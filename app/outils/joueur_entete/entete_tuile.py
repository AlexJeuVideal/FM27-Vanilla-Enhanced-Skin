"""En-tête de la fiche joueur en « grande tuile » (2026-11-05, concept du joueur) : vue au choix (option
`entete_vue`), appelée par entete_fiche (seul écrivain du bundle des en-têtes).

Une seule tuile (fond, bord, coins ronds), largeurs FIXES (rien ne s'adapte, rien ne bave), de gauche à droite :
photo | identité (nom + n°, poste, taille, drapeaux de statut, Actions) | grille 2 colonnes (Nation + sélections /
Âge / Valeur | Club + temps de jeu / Salaire + contrat) | polygone (pas en Small) | Statut de transfert +
Éligibilité (tuiles 2x1 de FM, sans leur cadre) | Progression (tuile 2x1 de FM ; pas dans la plus petite largeur) |
Niveau actuel / Potentiel (bloc de FM : étoiles chez nous, rapport du recruteur sinon).

Dans PlayerReportHeader (modèle touché par ce seul script) : chaque bannière de FM (max / mid / min, choisies par
FM selon la largeur de la fenêtre ; pas celle du téléphone) est cachée et notre tuile, aux largeurs de cette
taille (TAILLES), prend sa place ; la photo de FM est cachée (recopiée dans la tuile). Chaque passage repart du
modèle d'origine (sauvegarde) : option « fm » = modèle d'origine remis.
Éléments repris par contenu (chemins de données, noms FM) dans la bannière max (déjà retouchée par entete_fiche :
2e nationalité comprise).
"""
import copy
import os

from arbre import Tree, Styles, named, PROPRIETES, no_styles  # noqa: F401
from elements import first, typ, plain, copy_usings, move
import notes_au_lieu_des_libelles as nb
from langue import texte as L
import options

OPTION = "entete_vue"
MODELE = "PlayerReportHeader"
PREFIXE = "UIPickerEnteteTuile"
# v2 : v1 vue en jeu = rien d'affiché : les aiguillages de FM (UseStandard / UseSmall) choisissent leur enfant PAR
# POSITION ; bannière cachée + tuile côte à côte décalaient les enfants -> les deux dans un seul conteneur (Place),
# à la place exacte de la bannière
# v3 (le joueur, v2 vue en jeu : « j'aime beaucoup ») : Progression retirée ; tuile sur toute la largeur (dépassait
# en Large, trop courte en Medium / Small) : blocs en parts fixes (POIDS) ; grille en 2 rangées (traits alignés,
# trait du milieu à la hauteur de celui Statut / Éligibilité) ; bords alignés sur la fiche ; dégradé du club
# v4 (le joueur, v3 vue en Large : « rend bien mieux ») : statut étroit, Statut de prêt au lieu d'Éligibilité,
# grille Âge | Nation / Salaire | Valeur, marge avant chaque trait
# v5 : polygone dans une cale fixe sans liaison (il s'affichait en très grand pendant le chargement)
# v6 : une seule ligne de sélections (A, ou jeunes avant AGE_JEUNE ans), le détail au survol (infobulle de FM)
# v7 : la ligne unique de sélections en Large seulement (Medium / Small : les deux côte à côte)
# v8 : nationalités en 3 lettres en Large
# v9 : bannière / photo de FM cachées sans liaison (le grand polygone Medium flashait au chargement) ; nom court du
# club en Large
# v10 : colonne âge / salaire plus large, nation / valeur plus étroite
# v11 : polygone affiché seulement une fois les données du joueur lues (flash à l'ouverture)
# v12 : rayon du polygone 44 -> 17 % (flash au changement de joueur : image sans étiquettes, rayon entier)
# v13 : paire Âge | Nation en 2 versions (Large / Medium + Small) : plus de place pour la nation en Medium
# v14 (le joueur : « augmente la taille du polygone » Large et Medium, « égalise quelques tailles entre les cases »
# en Large) : cale du polygone et tuile plus grandes, rayon par bannière ; âge / nation / club à peu près égaux en
# Large, statut un peu plus étroit
# v15 (le joueur, v14 vue : « medium tu peux largement grossir encore, large un peu ») : rayon 20 -> 24 % (max),
# 18,3 -> 27 % (mid) ; la cale avait encore beaucoup de place autour des étiquettes
# v16 (le joueur : étoiles du niveau un peu coupées en Large) : cale max 250 -> 224 px de large (étiquettes ~190 px,
# rayon inchangé : % du petit côté = la hauteur)
# v17 (le joueur, Small : « pourquoi c'est en 3 lettres ? ») : la bannière de FM27 a sa propre nation en 3 lettres
# (primarytext nation.threelettername), trouvée en premier quand UIPickerNationalites manque -> Medium / Small
# prennent la nation en nom complet (nation.Name)
# v18 (le joueur, Large + Medium : polygone encore plus grand, étiquettes à ~3-4 mm du bord de la tuile ; Large :
# niveau / potentiel un peu à gauche, pris sur Dispo. transfert / prêt) : mesuré sur sa capture Large (×1,17 écran) :
# étiquettes à ~29 px du bord haut / bas -> rayon + ~16 px (Large) / + ~10 px (Medium), cale + 2 × ce gain (même
# marge autour des étiquettes qu'en v15 : pas de flash) ; la cale dépasse la zone en hauteur (coupée par la zone,
# les étiquettes restent dedans) ; parts statut / niveau propres au Large (`poids` de TAILLES)
# v19 (le joueur, v18 vue : polygone parfait mais le flash revient) : 32 % de la cale agrandie = rayon trop grand pour
# la marge des étiquettes (~33-36 px au lieu de ~37 : FM le réduit -> saut). Rayon = celui que FM garde avec les
# étiquettes (moitié de la hauteur - ~38 px) : max 31 % (62,6 px), mid 29 % (53,4 px) ; même taille à l'écran
# v20 (le joueur, v19 vue : flash plus petit mais encore léger) : marge ~38 px pas assez ; v15 (pas de flash) avait
# ~44 px en Large -> max 28 % (56,6 px, marge 44), mid 27 % (49,7 px, marge 42)
# v21 (le joueur, v20 vue : léger flash encore, Large + Medium ; « tu avais réussi parfaitement avant ») : le rayon
# n'était pas seul en cause -> cale + rayon du polygone remis comme en v16 (validée sans flash) : max 224 × 170 à 24 %,
# mid 226 × 164 à 27 % ; le reste de v17 / v18 gardé (nations, parts statut / niveau du Large)
# v22 (le joueur : « la taille actuelle, sans flash ») : cale visible de v18 gardée (elle coupe), mais le graphique
# y est INTERIEUR fois plus grand, centré (déborde des 4 côtés, coupé) : les étiquettes y tiennent toujours, FM ne
# réduit plus le rayon -> même taille au chargement et à l'affichage. Rayon donné en px (`rayon_px`), converti en %
# du petit côté du graphique ; px = taille finale de v20, mesurée sur les vidéos du joueur (10 im/s, 1re image après
# le changement de joueur = flash : polygone +2 % en Large, +5 % en Medium, étiquettes +7 % / +4 %) : 55,5 / 47,5 px
# v23 : px mesurés sur les vidéos (v22 : px estimés)
# v24 (2026-11-07, le joueur, maquette « B » choisie) : chaque info dans sa carte (fond, bord, coins ronds, écart
# entre les cartes) au lieu des traits : [Âge / Contrat] [Nation / Valeur (bord vert)] [Club] [Dispo. transfert /
# Dispo. prêt] [Niveau / Potentiel] [polygone] ; polygone TOUT À DROITE, et aussi en Small (vide à droite)
# v25 (le joueur, v24 vue : « j'adore ») : nom du club coupé net -> « … » + nom complet au survol (bloc club de FM
# déplié dans tous les modes, chaîne rétrécissable, DisplayTooltipWhenElided sur le texte de la cellule) ; plus de bord
# vert autour de la valeur ; contenu des cartes centré ; cartes un peu plus discrètes ; plus de cadre autour de
# l'en-tête (seul le trait du bas reste) ; polygone un peu plus petit (rayon -10 %, plus d'air)
# v26 (le joueur : salaire et temps de jeu pas centrés) : leur bloc de FM sans largeur 100 % ni calage à gauche
# v27 (le joueur : « tu mets la progression en haut à droite ») : tuile Progression de FM (sans son cadre) à la place
# du polygone, dans sa carte tout à droite, tous les modes (le polygone reste dans le code : PROGRESSION = False)
# v28 : Progression en Small seulement (mode > 1), polygone en Large / Medium
# v30 : carte Progression habillée (titre, tendance, courbe dans un bandeau sombre)
# v31 (2026-11-09, le joueur : « brancher l'en-tête sur la couleur des tuiles ») : fond des cartes plus en style
# intégré (il passait devant tout) mais par la classe CL_CARTE (règle de la feuille du modèle, même couleur) ;
# couleurs_interface (tuiles) pose une règle plus forte sur cette classe
# v32 (2026-11-09, le joueur, Large : « fais de la place pour le nom ») : Dispo. transfert | Dispo. prêt côte à côte
# au-dessus de Niveau / Potentiel, dans une seule colonne ; la place gagnée va à l'identité
# v33 : rapport de supervision trop haut pour la carte Niveau (Large) : Niveau 1.15 / Dispo. 0.85 de la hauteur,
# marges réduites ; titre du rapport caché en Large (etoiles_rapport v2)
# v34 (le joueur : « Indisponible » sur 2 lignes) : valeurs Dispo. sur une ligne, « … » + infobulle (Large)
# v35 (Heyti, 2026-11-12 : sélections U20 affichées pour un jeune déjà sélectionné en A) : Large, ligne unique = A
# aussi avant AGE_JEUNE ans dès que InternationalDebutNationalTeamContainer n'est pas nul
# v36 (2026-11-15, le joueur) : Dispo. transfert / prêt centrés dans leur carte (cadre de FM en align-items-start)
# v37 : Large, titres Dispo. sur une ligne (body-xs) : les deux cartes à la même hauteur
# v38 (2026-11-18, le joueur : bas de l'en-tête mangé depuis FM du 2026-11-17) : FM fixe la hauteur du conteneur
# (.report-player-full-header-max-type-player, height 180 px) < notre tuile (Large 188 + 2 x 6) : hauteur du conteneur
# en auto (style intégré) -> il suit la tuile et pousse la fiche
# v39 (le joueur, v38 vue : Medium OK ; Large poussé = bas de la fiche qui défile) : tuile Large ramenée à 180 px
# (haut 172, marges 4) -> ne pousse plus rien en Large ; hauteur auto gardée (Medium 192)
# v40 : Medium aussi à 180 px (172 + 2 x 4) : la fiche tremblait (barre de défilement en boucle)
# v41 : Small aussi à 180 px (152 + 2 x 14) : les 3 tailles = hauteur de FM
# v42 (2026-11-19, le joueur : clic sur les étoiles = rapport vide) : bloc Niveau / Potentiel dans un remapper
# player / team / human (scout_lie), tous les styles
# v43 (2026-11-19, le joueur) : trait fin sous l'en-tête retiré (trait_bas) ; option entete_couleur_club
VERSION = 44   # v44 : trait du bas de notre tuile transparent
CONTENEUR = "report-player-full-header-max"   # élément de FM qui porte la classe à hauteur fixe
AUTO = (1, 2)                                  # mot-clé Auto (style intégré)
CL_CARTE = "uipicker-entete-carte"     # classe fixe (sans version) : couleurs_interface.ENTETE_CARTE la vise
CL_LIGNE = "uipicker-gomez-ligne-v1"   # rangée de la tuile identité (gomez) : ses cellules de FM recentrées
CELLULES_FM = ("cell-medium", "cell-button")   # cellules de FM (pays, sélections) : hauteur fixe + align-self-start
COURBE_FOND = (0.0, 0.0, 0.0, 0.22)
PROGRESSION = True
# v29 (le joueur : la 2x1 « écrit juste une phrase ») : la 2x2 a la courbe (FMLineChart) + la tendance
MODELE_PROGRESSION = "TrainingProgressReportTile_2x2"
# gom30 (2026-11-19, le joueur) : Small, tuile Efficacité tactique de FM à droite de Progression (en-tête gomez)
MODELE_EFFICACITE = "TacticalEffectivenessTile_2x2"
EFFICACITE_LARGEUR = 480     # px de la carte (gom30 : 260 ; gom31 : 2 colonnes)
MODELE_EFFICACITE_TABLEAU = "TacticalEffectivenessTileTable"   # gom31 : lignes du tableau de FM à droite
# gom32 (2026-11-19, le joueur) : joueur hors club (Small) : cartes Agent + Attentes au lieu de Progression / Efficacité
AGENT_HORS_CLUB = options.get("entete_style") == "gomez"
CHEMIN_CLUB = "person.Team.IsHuman"          # joueur de ton club (comme hors_defaut)
MODELE_AGENT = "PlayerAgentReportTile_2x2"   # nom de l'agent + phrase (player -> player.Agent)
BOUTON_AGENT_SOURCE, BOUTON_AGENT = "TransferRoomInMainBlock", "ask-agent-availability-button"
ACTION_AGENT = 1999843434                    # ActionId de FM « Demander à l'agent (disponibilité) »
MODELE_INFO_TRANSFERT = "TransferInfo"       # valeur + demande salariale attendues (rapport de recrutement)
TYPE_RAPPORT = 1315196500
MODELE_DEMANDES = "PlayerInfoInterestExpectations"   # liste des demandes de l'agent (Person.PlayerAgentDemands)
CHEMIN_DEMANDES = "person.PlayerAgentDemands"        # gom37 : pas nul = l'agent a répondu (sinon : rapport)
TYPE_EFFICACITE, TYPE_TACTIQUE = 842556533, 2003981122
EFFICACITE_PART_TABLEAU = 1.3   # part de largeur du tableau (la 2x2 : 1)
EFFICACITE_LIGNES = ("tactical-understanding", "player-ability", "player-buyin", "match-info")
EFFICACITE_HAUT_LIGNE = 30      # px par ligne du tableau (FM : row-height-large)
EFFICACITE_ECART = 20           # gom38 : px entre la colonne gauche et le tableau (gom31 : 10)
INTERIEUR = 2.0                             # graphique = cale × INTERIEUR (v22)
# 2026-11-14 (option fiche_medium_colonne, demande de hunfair) : en Medium, carte Pour / Contre en pastilles (comme
# l'infobulle : cadres POUR | CONTRE) à la place du polygone, qui passe à droite d'Infos (fiche_joueur_plus)
MEDIUM_PC = options.get("fiche_medium_colonne") == "polygone"
# 2026-11-15 (option fiche_large_tuile) : en Large, entete = polygone (base) ; pastilles = carte Pour / Contre comme
# Medium ; dessous = rien (polygone + Pour / Contre à droite d'Infos, fiche_joueur_plus)
LARGE_TUILE = options.get("fiche_large_tuile")
# carte de droite par mode (0 Large, 1 Medium) : "pc", "poly" ou None
DROITE = {0: {"pastilles": "pc", "dessous": None}.get(LARGE_TUILE, "poly"), 1: "pc" if MEDIUM_PC else "poly"}
PC_RAPPORT = "Person.PlayerReportForContextTeam"     # comme le bandeau de l'en-tête de FM (entete_fiche)
PC_GUID_PASTILLE = "1d9ea6f83e853594c9a3339ba036281b"   # ProConRow = pastille de l'en-tête (entete_fiche, 28 px)
PC_RANGEES = 3                                       # rangées de pastilles max par cadre (le reste est caché)
PC_PAR_RANGEE = 4                                    # v2 (le joueur, v1 vue en jeu : « limite à 12 ») : 4 × 3 = 12 max
# pc2 (2026-11-19, le joueur : fond des cadres Pour / Contre « ressort beaucoup trop », doit suivre chaque thème) :
# voile noir transparent (assombrit la couleur de la tuile, quelle qu'elle soit) au lieu du blanc 6 % de l'infobulle
PC_CADRE_FOND = (0.0, 0.0, 0.0, 0.11)   # pc3 (le joueur : « réduis l'ombre de moitié ») : 0,22 -> 0,11
# 2026-11-19 (le joueur, maquette « A » choisie) : option entete_style = numero : grand numéro du maillot derrière la
# photo, nom plus gros, trait doré à gauche, valeur encadrée en or ; la carte de droite reste celle des options
# (polygone / Pour / Contre / rien / Progression)
STYLE_NUMERO = options.get("entete_style") == "numero"
# 2026-11-19 (le joueur, maquette « format Gómez » du haut : « des tuiles qui regroupent les infos, pas plein de
# petites ») : entete_style = gomez : 3 tuiles = identité (n° en contour, photo, lignes nom / poste / nation / Valeur /
# Contrat) | club (club, Dispo. transfert, Dispo. prêt, Niveau / Potentiel) | carte de droite des options ; fond des
# tuiles = CL_CARTE (couleur des tuiles du skin), sans bord
STYLE_GOMEZ = options.get("entete_style") == "gomez"
EFFICACITE_SMALL = STYLE_GOMEZ   # gom30 : tuile Efficacité tactique à droite de Progression (Small)
# 2026-11-19 (le joueur) : option entete_couleur_club : « non » = plus de dégradé du club derrière l'en-tête
COULEUR_CLUB = options.get("entete_couleur_club") != "non"
GOMEZ_POIDS = (2.3, 1.0)    # parts de la largeur : identité, club (la carte de droite garde sa largeur fixe) ;
                            # gom6 : club 1.25 -> 1.0
GOMEZ_LIGNE = 2             # px sous chaque ligne (gom7 : 3 -> 6 ; gom10 : 4 ; gom12 : 2)
# gom12 (le joueur : Large pas réglé) : 32 + 4 × 24 + marges = ~183 px > 172 de la tuile Large -> elle grandissait
# (cale en hauteur auto) et poussait la fiche ; lignes plus basses, réparties dans la hauteur (space-around) :
# serrées en Large, aérées en Medium / Small (+ ENTETE_PLUS)
GOMEZ_HAUT_LIGNE, GOMEZ_HAUT_NOM = 24, 28   # px, hauteur des lignes de la tuile identité (gom13 : 22 -> 24 : la
                                            # valeur (pastille 24 px) était coupée en bas)
GOMEZ_HAUT_LIGNE_MS, GOMEZ_HAUT_NOM_MS = 26, 28   # gom61 : 27 / 30 -> 26 / 28 (place rendue) ; gom60 : Medium / Small (bas des textes coupé) ; Large : 24 / 28
GOMEZ_MARGE = 16            # px, marges intérieures gauche / droite des tuiles (gom7 : 12 -> 16)
GOMEZ_LIBELLE = 112         # px, colonne des libellés de la tuile club (gom3)
MEDIAS_CHEMIN = "person.MediaDescription"   # description des médias (gom4)
# gom5 (le joueur : « bloque le numéro et la photo à un endroit fixe », « enlève le n° à droite du nom », « un maillot
# à la couleur du club derrière le numéro, la couleur du maillot du club ») : cadre fixe = maillot de FM (KitShirt :
# image du kit recolorée, paramètre kit = person.Team.Kit, type 1616315467 ; sans player = pas son n°) + notre n° centré
# gom6 (le joueur, gom5 vu : « le kit a pas marché », maillot vide + petit n° du modèle en haut à gauche) : FM dessine
# ses maillots depuis Team.KitHome (TacticsPositionFilledMedium), pas Team.Kit ; texte du n° du modèle retiré
MAILLOT_MODELE, MAILLOT_KIT, TYPE_KIT = "KitShirt", "person.Team.KitHome", 1616315467
# gom6 (le joueur, Medium : « réduis la tuile transfert, élargis Pour / Contre ») : carte Pour / Contre plus large de
# GOMEZ_PC_PLUS px, 6 pastilles par rangée (au lieu de PC_PAR_RANGEE)
GOMEZ_PC_PLUS, GOMEZ_PC_PAR_RANGEE = 150, 6
# gom27 (le joueur, Large : « réduis légèrement la carte du joueur, un peu plus de largeur au Pour / Contre ») : carte
# Pour / Contre du Large + GOMEZ_PC_PLUS_LARGE px, pris sur les tuiles identité / club (parts GOMEZ_POIDS)
GOMEZ_PC_PLUS_LARGE = 80
# pc4 (le joueur : « en moyen et petit, grossis les vignettes Pour / Contre, il y a la place ») : carte du Medium (aussi
# vue en Small) = liste de pastilles × PC_ECHELLE_MEDIUM, PC_PAR_RANGEE_GROS par rangée (5 × 30 × 1,3 = 195 px < cadre)
PC_ECHELLE_MEDIUM, PC_PAR_RANGEE_GROS = 1.3, 5
GOMEZ_NIVEAU_DECALE = 30   # gom29 : px de cale avant Niveau / Potentiel en Large (80 ; gom43, le joueur : avec un
                           # rapport, « Ligue 1 McDonal… », « Not s… » coupés à gauche -> 30)
GOMEZ_CLUB_LARGE = 130   # gom28 : px de base de la tuile club en Large (club ≈ 130 + sa part du reste : ~530 px)
MAILLOT = {"report-player-banner-max": dict(w=112, h=112, police=54),
           "report-player-banner-mid": dict(w=104, h=104, police=50),
           "report-player-banner-min": dict(w=92, h=92, police=44)}
MAILLOT_NUMERO, MAILLOT_CONTOUR = (1.0, 1.0, 1.0, 0.96), (0.0, 0.0, 0.0, 0.85)
MAILLOT_PETIT = dict(w=50, h=50, police=24)      # gom15 : maillot du coin de la photo (Large) ; plus utilisé (gom16)
PHOTO_RAPPORT = 0.8                              # gom17 : largeur / hauteur de la photo de FM (capture Medium 118 × 148)
# gom17 (le joueur : « les pays sont décalés dans tous les sens ») : décalage à droite du bloc pays de FM (drapeau,
# dans son modèle : pas modifiable) mesuré sur les captures (~6 px Medium / Small, ~11 px Large) -> marge négative
# Large, Medium / Small ; gom23 (le joueur : « les pays toujours bouffés ») : -11 en Large poussait le 1er drapeau
# hors du bord de la colonne (coupé, un trait) -> -6 comme en Medium, ligne des pays sans coupe
PAYS_DECALAGE = {True: -4, False: -6}
# gom20 (le joueur, gom19 vu en Large : « à droite de la photo toujours n'importe comment ») : mesuré sur sa capture
# (1 px capture ~ 1 px jeu) : pays 4 px et sélections 5 px plus bas que le texte d'en face -> remontés (Large seul)
LARGE_REMONTE = {"nat": -4, "caps": -5}
# gom22 (le joueur, gom21 vu : « pourquoi le nom si haut, tu mets de l'espace pour mettre de l'espace », modèle =
# bloc serré centré) : lignes centrées dans la tuile, écart fixe entre elles par affichage (Large serré ; Medium /
# Small = la place libre / 5, comme le space-around validé « niquel »)
GOMEZ_ECART_LARGE = 2
GOMEZ_ECART_LARGE_2C = 2   # gom25 : écart entre 2 lignes des colonnes du Large (modèle du joueur : lignes serrées)
# gom9 : maillot de dos dessiné (formes + dégradé du club) ; KitShirt (MAILLOT_MODELE / MAILLOT_KIT) plus utilisé
MAILLOT_DEGRADE = 0                              # GradientDirection TopToBottom (sans AlphaTweak : couleur pleine)
MAILLOT_COL = (0.0, 0.0, 0.0, 0.25)              # ourlet du bas (sombre) ; gom11 : col = 2e couleur du kit
MAILLOT_SANS_CLUB = (0.45, 0.47, 0.50, 1.0)      # gris si le dégradé de FM manque
MAILLOT_OMBRES = False                           # gom48 : coupées (« rendu moche »)
MAILLOT_FONDU = 12                               # gom46 : 3 ; gom48 : 12 (couleur quasi pleine)
MAILLOT_ECHELLE = 0.95                           # gom48 : 0,8 ; gom53 (le joueur : « il paraît vraiment petit ») : 0,95
MAILLOT_DESCENTE = 0.08                          # gom50 : mesuré, ~9 px plus haut que le centre de la photo
MAILLOT_NUMERO_TAILLE = 0.83                     # gom48 : 0,7 ; gom53 : suit le maillot (0,7 × 0,95 / 0,8)
NUMERO_BADGE = "data_display-player-report-header-squad-number"   # petit n° de FM à droite du nom
# 2026-11-19 ESSAI (le joueur : « grandir l'en-tête pour que le bas descende », vide en bas de la fiche) : tuile plus
# haute de N px (UIPICKER_ESSAI_ENTETE_PLUS, 124 seulement ; 0 = 180 px de FM). Risque connu : v38 (Large poussé =
# bas qui défile), v40 (Medium 192 = fiche qui tremble chez un ami) ; le vide dépend de la résolution
# 2026-11-19 (le joueur, Medium validé : « mets le fix pour que la fiche remplisse bien en bas sur TOUT ce qu'on avait
# déjà fait ») : de base dans les 3 styles de la grande tuile (cartes, numero, gomez) ; la variable garde le réglage
# d'essai (0 = 180 px de FM partout)
try:
    ENTETE_PLUS = max(0, int(os.environ.get("UIPICKER_ESSAI_ENTETE_PLUS") or 40))
except ValueError:
    ENTETE_PLUS = 40
# 2026-11-19 (le joueur : « en Moyen augmente légèrement pour bien compléter le vide en bas ») : captures +40 = ~44 px
# de vide en Medium, ~25 en Small -> Medium + 30 de plus, Small inchangé ; px en plus par affichage (1 Medium, 2 Small)
# gom60 (le joueur : « en petit ça bouffe le bas des textes, étends un peu le conteneur au global ») : +10 px en Medium
# et Small (avec des lignes gomez plus hautes : GOMEZ_HAUT_LIGNE_MS / GOMEZ_HAUT_NOM_MS)
ENTETE_PLUS_GLOBAL = 0   # gom61 (le joueur, gom60 vu : « tu m'as fait bug les tuiles en bas, trop grand ») : 10 -> 0
ENTETE_PLUS_MODE = ({1: ENTETE_PLUS + 30 + ENTETE_PLUS_GLOBAL, 2: ENTETE_PLUS + ENTETE_PLUS_GLOBAL}
                    if ENTETE_PLUS else {})
# gom35 (le joueur) : Medium / Small, joueur hors club (fiche plus courte, ~65 px de vide en Small) : + N px en plus
ENTETE_PLUS_HORS_CLUB = 0   # gom36 : retiré (le vide vient de hors_defaut : même hauteur de fiche à la place)
OR = (0.95, 0.71, 0.11, 1.0)
OR_BORD = (0.95, 0.71, 0.11, 0.75)
# num3 (le joueur, num2 vu : « même couleur que le club on voit mal ») : remplissage sombre + contour or, à côté de la
# photo (plus dessous : le 7 de 37 était caché)
NUMERO_COULEUR = (0.0, 0.0, 0.0, 0.30)
NUMERO_CONTOUR, NUMERO_CONTOUR_COULEUR = 2.0, (0.95, 0.71, 0.11, 0.95)
# num3 (le joueur : « tente C », halo) : FM n'a pas de dégradé rond (GradientDirection, global-metadata : 0 TopToBottom,
# 1 LeftToRight, 2-7 EndColour<coin>, 8 TopRightToBottomLeftWithAlphaTweak, 9 TopLefttToBottomRightWithAlphaTweak,
# 10 PersonReportHeader…, 11 TopToBottomWithAlphaTweak, 12 …ClubButton, 13 RightToLeft) -> 2 moitiés : gauche 8
# (fort en haut à droite), droite 9 (fort en haut à gauche) = le plus fort en haut au milieu
HALO = (8, 9)
# num4 (le joueur, num3 vu : « chelou de fou », cases en taches jaunes, petits titres illisibles) : couleur du club à
# pleine force -> fond de la case (les 2 moitiés ensemble) en opacité réduite
FONDU_OPACITE = 0.2
NUMERO_CHEMIN = "person.SquadNumberBlankIfInvalid"   # vide sans numéro (comme les listes de FM)
NUMERO_TRAIT = 3                                     # px, trait doré à gauche de la tuile
# par bannière : taille du numéro, décalage de la photo vers la droite (le numéro dépasse à gauche), taille du nom
NUMERO = {"report-player-banner-max": dict(police=88, nom=24),
          "report-player-banner-mid": dict(police=80, nom=22),
          "report-player-banner-min": dict(police=66, nom=21)}   # nom de FM : 20 px (fm-universe-20px)
NOM = f"{PREFIXE}-v{VERSION}" + ("-mpc7" if MEDIUM_PC else "") \
    + {"pastilles": "-lpc3", "dessous": "-lrien1"}.get(LARGE_TUILE, "") + ("-num4" if STYLE_NUMERO else "") + ("-gom72pc4" if STYLE_GOMEZ else "") \
    + (f"-hmode{ENTETE_PLUS}m{ENTETE_PLUS + 30}" if ENTETE_PLUS else "") \
    + ("" if COULEUR_CLUB else "-sanscoul2")   # + N px Small, N + 30 Medium ; option entete_couleur_club
# num2 : cases fondues (dégradé du club au fond), plus de traits ; num3 : halo (HALO), numéro à côté de la photo
# mpc v3 : titres calés en haut ; v4 : pastilles centrées ; v5 : bouton Observer sans rapport
NOM_CACHE = PREFIXE + "Cache"          # SIVisible jamais vrai : bannière / photo de FM gardées, cachées
NOM_PLACE = PREFIXE + "Place"          # conteneur [bannière cachée, tuile] = un seul enfant de l'aiguillage
SOURCE = "report-player-banner-max"
MODE = "settings.AdaptiveScalingLevelIndex"
JOUEUR, EQUIPE = 1145176065, 1145176088

# par bannière de FM remplacée (taille de fenêtre) : polygone (largeur, hauteur en px ; None = pas), hauteur de la
# tuile, écart de part et d'autre des traits
TAILLES = {
    # v25 : rayons -10 % (le joueur : « que ça respire un poil plus » ; plus petit = plus de marge, pas de flash)
    # v39 (le joueur : en Large, v38 poussait la fiche = bas qui défile) : 172 + 2 x 4 = 180 = hauteur de FM
    "report-player-banner-max": dict(poly=(256, 202), haut=172, marge_haut=4, ecart=12, rayon_px=50.0,
                                     # v32 : statut + niveau en une colonne, le reste à l'identité (nom)
                                     poids=dict(statut_niveau=1.75, ident=2.65)),
    # v40 (ami du joueur : fiche qui tremble en Medium / Small) : 180 + 2 x 6 = 192 > 180 de FM -> poussait la fiche,
    # barre de défilement qui apparaît / disparaît à chaque image ; 172 + 2 x 4 = 180 comme le Large
    "report-player-banner-mid": dict(poly=(246, 184), haut=172, marge_haut=4, ecart=10, rayon_px=43.0),
    # v24 : polygone aussi ici (le joueur) ; rayon à la même marge d'étiquettes que le Large (~28 px haut / bas)
    # v41 (ami du joueur : tremble aussi en Small) : 152 + 2 x 6 = 164 -> conteneur auto rétréci sous les 180 de FM ;
    # 152 + 2 x 14 = 180 : même hauteur que FM, tuile inchangée
    "report-player-banner-min": dict(poly=(224, 150), haut=152, marge_haut=14, ecart=8, rayon_px=35.0),
}
# v24 : cartes (maquette B) : fond / bord d'une carte, coins ; v25 : un peu plus discrètes, plus de bord vert
CARTE_FOND, CARTE_BORD = (1.0, 1.0, 1.0, 0.03), (1.0, 1.0, 1.0, 0.07)
CARTE_RAYON = 8
CARTE_BORD_VALEUR = CARTE_BORD
CELLULE_CLUB = "text-cell-medium-strong"   # cellule du nom du club (texte #primary-text, « … » déjà là)
# v14 : rayon (% du petit côté de la cale) par bannière ; mesuré en jeu (v13, 210 × 150 à 17 %) : FM garde ~37 px de
# marge en largeur et en hauteur autour des étiquettes -> cale agrandie de 2 × le gain de rayon dans les deux sens,
# pour que FM ne réduise pas le rayon (sinon le flash revient)
# parts de la largeur de la tuile (flex-basis 0 : la même pour tous les joueurs, rien ne dépend du contenu ;
# en Small le polygone n'est pas là, les autres se partagent sa part)
# v4 : statut bien plus étroit, la place va à la nation (sélections jeunes coupées en v3)
# v10 (le joueur : salaire / fin de contrat coupés en Large) : âge / salaire 1.3 -> 1.75, nation / valeur 1.9 -> 1.45
# v13 : la paire Âge | Nation a sa part (paire), partagée selon le mode (POIDS_PAIRE : Large / Medium + Small) ;
# un peu plus large qu'avant (3.2 -> 3.5) pour les noms complets du Medium
# v14 (le joueur : égaliser les cases en Large) : âge ≈ nation ≈ club ; statut 1.1 -> 0.9 (la place du polygone)
POIDS = dict(ident=2.0, paire=3.6, club=1.75, poly=2.0, statut=0.9, niveau=1.5)
POIDS_PAIRE = {"large": (1.85, 1.75), "autres": (1.4, 2.1)}   # (âge / salaire, nation / valeur)
MARGE_HAUT = 6                              # px au-dessus / au-dessous de la tuile
MARGE_COTES = 28                            # px à gauche / à droite (bords de la fiche dessous)
# dégradé de l'en-tête de FM recopié en fond de la tuile : False (v3) = le dégradé d'origine de l'en-tête (autour de
# tout) teinte déjà la tuile (vu en jeu, club rouge) ; True le doublerait
DEGRADE_CLUB = False
DIRECTION_DEGRADE = 11                      # TopToBottomWithAlphaTweak (celle de l'en-tête de FM)
AGE_JEUNE = 21                              # moins de ... ans : sélections jeunes au lieu des sélections A (v6)
POLYGONE_MARGE = 10                        # px de part et d'autre de la cale du polygone (v5)
# v12 (vidéo du joueur, flash à chaque changement de joueur) : une image sans étiquettes, où FM prend le rayon demandé
# en entier (44 % : gros polygone), puis les étiquettes reviennent et FM le réduit ~2,7 fois pour qu'elles tiennent ;
# rayon demandé = celui que FM garde avec les étiquettes -> même taille sur les deux images
POLYGONE_RAYON = 17.0                     # % (FM : 34,8 ; étiquettes 10 px de la vue Guru)
FOND, BORD = (1.0, 1.0, 1.0, 0.045), (1.0, 1.0, 1.0, 0.12)
TRAIT = (1.0, 1.0, 1.0, 0.10)               # traits fins de la grille et entre les blocs
RAYON, MARGE = 12, (10, 14)                 # coins ; marges intérieures (haut / bas, gauche / droite)
CELLULE = (6, 10)                           # marges intérieures d'une case de la grille (haut / bas, côtés)
# v4 : Statut de transfert / Statut de prêt = les 2 cadres (repérés par leur titre) de cette tuile de FM
CLUB = "PlayerReportHeaderMaxTeamSection"   # bloc club de FM (recopié en Large avec le nom court, v9)
STATUT = "PlayerTransferStatusTile_2x2"
STATUT_CADRES = ["transfer-status-text", "loan-status-text"]

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "max-height": (131094, 3),
               "padding-top": (131101, 3), "padding-bottom": (131098, 3), "padding-left": (131099, 3),
               "padding-right": (131100, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "margin-top": (131093, 3), "align-self": (131074, 7), "align-items": (131073, 7),
               "justify-content": (131088, 7), "flex-direction": (131083, 7),
               "border-top-color": (458763, 4), "border-bottom-color": (458758, 4),
               "border-left-color": (458761, 4), "border-right-color": (458762, 4),
               "border-top-left-radius": (458764, 3), "border-top-right-radius": (458765, 3),
               "border-bottom-left-radius": (458759, 3), "border-bottom-right-radius": (458760, 3),
               "position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
               "font-size": (65537, 3), "text-overflow": (196609, 7), "white-space": (65552, 7),
               "color": (65536, 4), "-unity-text-align": (65546, 7),
               "text-outline-color": (65549, 4), "text-outline-width": (65550, 2), "opacity": (458767, 2),
               "bottom": (131080, 3), "right": (131103, 3)}.items():
    PROPRIETES.setdefault(_k, _v)


def vue():
    # 2026-11-07 (le joueur) : mode FM Guru = en-tête de FM (retouché), jamais la grande tuile
    if options.get("fiche_fmguru") == "guru":
        return "fm"
    return options.get(OPTION)


# ---------- recherche dans la bannière source ----------
def _surcharges(s, r):
    """texte des données surchargées d'un modèle inclus (chemins des liaisons par fonction décodés)"""
    out = []
    for o in s.elem(r).get("m_SerializedDataOverride") or []:
        d = (s.refs.get(o["m_SerializedData"]["rid"]) or {}).get("data") or {}
        out.append(str(d))
        tb = d.get("TextBinding")
        if isinstance(tb, dict) and tb.get("m_kind") == 2:
            out.append(nb.describe(tb))
    return " ".join(out)


def _alias(s, r):
    return s.elem(r).get("m_TemplateAlias") or ""


def pieces(s):
    """éléments de la bannière max à recopier (dict nom -> rid), ou None si l'un manque"""
    nom_txt = first(s, lambda r: "person.Name" in str(s.sd(r).get("TextBinding") or ""))
    poste = first(s, lambda r: "PositionCombinedStringLong" in _surcharges(s, r))
    flags = first(s, lambda r: s.name(r) == "PlayerStatusFlagsForTeamVisible")
    def _nation(r, court):
        if not typ(s, r).endswith("BindingRemapper"):
            return False
        maps = s.sd(r).get("Mappings") or []
        if not any(m.get("to", {}).get("m_path", "").lower() == "person.nation" for m in maps):
            return False
        trois = any(m.get("from") == "primarytext" and "threelettername" in m.get("to", {}).get("m_path", "").lower()
                    for m in maps)
        return trois == court
    # v17 : nom complet d'abord (la bannière de FM27 a aussi une nation en 3 lettres)
    nat3 = first(s, lambda r: _nation(r, True))   # Large, si la ligne d'entete_fiche manque
    nat = first(s, lambda r: s.name(r) == "UIPickerNationalites") or first(s, lambda r: _nation(r, False)) or nat3
    caps = first(s, lambda r: {"StandardTextTooltip", "text-cell-button-medium"}
                 <= {_alias(s, k) for k in s.children(r)})
    age = first(s, lambda r: _alias(s, r) == "data_display-cell-standard-regular" and "Person.Age" in _surcharges(s, r))
    club = first(s, lambda r: _alias(s, r) == "PlayerReportHeaderMaxTeamSection")
    valeur = first(s, lambda r: typ(s, r).endswith("BindingRemapper")
                   and any(m.get("from") == "TransferValueRange" for m in s.sd(r).get("Mappings") or []))
    contrat = first(s, lambda r: typ(s, r).endswith("BindableSwitchElement")
                    and "person.fullcontract.IsValid" in str(s.sd(r).get("Binding") or ""))
    scout = first(s, lambda r: _alias(s, r) == "PlayerReportHeaderScoutSection")
    actions = first(s, lambda r: s.name(r) == "FrameActions")
    setter = first(s, lambda r: typ(s, r).endswith("BindingSetter"))
    p = dict(nom=nom_txt is not None and s.parent[nom_txt], poste=poste is not None and s.parent[poste],
             flags=flags is not None and s.parent[flags], nat=nat, caps=caps, age=age, club=club, valeur=valeur,
             contrat=contrat, scout=scout is not None and s.parent[scout], actions=actions, setter=setter)
    manque = [k for k, v in p.items() if v is None or v is False]
    p["nat3"] = nat3
    return p, manque


# ---------- petits outils ----------
def boite(t, parent, css, classes=(), nom=""):
    classes = list(classes)
    if css and css.pop("_carte", False):   # v31 : carte (habille) -> fond par la classe CL_CARTE
        classes.append(CL_CARTE)
    fondu = bool(css) and css.pop("_fondu", False)
    b = plain(t, parent, None, classes, nom)
    t.elem(b)["m_RuleIndex"] = -1
    if nom:
        t.sd(b)["name_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, b, css)
    if fondu and _FONDU.get(id(t)) is not None:
        degrade_fondu(t, b, _FONDU[id(t)])
    return b


_FONDU = {}   # id(arbre) -> SIGradient de l'en-tête de FM (entete_style numero), posé par construire


def maillot_numero(t, src, nom_txt, parent, dm, degrade, e, place=None):
    """cadre fixe (dm w × h) = maillot de dos plat aux couleurs du club + n° centré comme sur un vrai maillot ;
    gom9 (le joueur, maillot du jeu (KitShirt) « moche de ouf » -> « un maillot de dos tout simple », « couleur du
    club », « le numéro bien centré vraiment comme un maillot irl ») : formes (épaules + manches, corps, col) remplies
    du dégradé du club de l'en-tête de FM (SIGradient, déjà vu marcher) ; messages"""
    w, h = dm["w"], dm["h"]
    cadre = boite(t, parent, {"width": w, "min-width": w, "max-width": w, "height": h, "min-height": h,
                              "max-height": h, "flex-shrink": 0, "flex-grow": 0, "align-self": "center",
                              "margin-right": e, "overflow": "hidden", **(place or {})}, [])
    msgs = []

    from hierarchie_pyramide import path_arg

    def forme(x, y, fw, fh, r, couleur, px=False):
        """rectangle absolu (en 120e du cadre, ou en px si px) aux coins arrondis r ; couleur = chemin d'une couleur
        du kit (dégradé de FM repointé dessus, gom11) ou couleur fixe (r, g, b, a)"""
        css = ({"position": "absolute", "left": x, "top": y, "width": fw, "height": fh} if px else
               {"position": "absolute", "left": round(x * w / 120), "top": round(y * h / 120),
                "width": round(fw * w / 120), "height": round(fh * h / 120),
                **{f"border-{c}-radius": round(r * w / 120) for c in ("top-left", "top-right", "bottom-left",
                                                                       "bottom-right")}})
        if not isinstance(couleur, str) or degrade is None:
            css["background-color"] = couleur if not isinstance(couleur, str) else MAILLOT_SANS_CLUB
            return boite(t, cadre, css, [])
        if px:
            # gom46 (le joueur, gom45 vu : « rend super chelou », rayé) : un dégradé de FM par bande = rayures (chacun
            # va de la couleur au sombre) -> fenêtre (overflow hidden) sur UN dégradé MAILLOT_FONDU fois plus haut que
            # le maillot, calé sur le cadre : couleur continue, légère ombre vers le bas
            fen = boite(t, cadre, {**css, "overflow": "hidden"}, [])
            g = t.clone_shallow(degrade, fen)
            sd = t.sd(g)
            sd["name"] = ""
            sd["GradientDirection"] = MAILLOT_DEGRADE
            sd["BindGradientFunc"] = path_arg(sd["BindGradientFunc"], couleur)
            t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
            t.styles.style(t, g, {"position": "absolute", "left": -x, "top": -y, "width": w,
                                  "height": round(h * MAILLOT_FONDU), "flex-shrink": 0})
            return fen
        g = t.clone_shallow(degrade, cadre)
        sd = t.sd(g)
        sd["name"] = ""
        sd["GradientDirection"] = MAILLOT_DEGRADE
        sd["BindGradientFunc"] = path_arg(sd["BindGradientFunc"], couleur)
        t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
        t.styles.style(t, g, css)
        return g

    if degrade is None:
        msgs.append("maillot : dégradé de FM introuvable, maillot gris")
    k1, k2 = MAILLOT_KIT + ".BackgroundColour", MAILLOT_KIT + ".ForegroundColour"
    # gom11 (le joueur : maquette 2 « classique », 2e couleur = celle du kit, « link au kit : si le joueur change, ça
    # change ») : manches, bouts de manches (2e couleur), corps, ourlet sombre, col (2e couleur) ; repère 120 × 120
    # gom44 (le joueur : son maillot PNG, « rouge et vert exprès ») : maillot_dos.png découpé (rouge = couleur 1 du
    # kit, vert = couleur 2) ; gom47 : lignes 1 px + bords anti-crénelés ; gom48 : MAILLOT_ECHELLE, couleur pleine
    # gom50 (le joueur : « mal positionné », « on voit pas bien les chiffres, réfère-toi aux couleurs des kits »,
    # « pas de blanc ») : maillot collé à droite du cadre (vers la photo), descendu de MAILLOT_DESCENTE ; n° dans un
    # SIStyleSetter (comme #shirt-badge de TacticalTweakPlayerRow) : couleur = KitHome.NumberColour
    import maillot_dos
    hm = round(h * MAILLOT_ECHELLE)
    lm, zones, voiles = maillot_dos.decoupe(hm)
    # gom53 : même centre vertical qu'en gom51 (0,8 : 0,1 h + descente + 0,4 h) ; à 0,95 le bas dépasse le cadre de
    # quelques px -> cadre en overflow visible (mise en page inchangée)
    dx, dy = w - lm - 2, round(h * (0.5 + MAILLOT_DESCENTE) - hm / 2)
    t.styles.style(t, cadre, {"overflow": "visible"})
    chemins = {"1": k1, "2": k2}
    for k, op, rs in zones:   # gom47 : bords anti-crénelés = mêmes couleurs, opacité < 1
        for x, y, fw, fh in rs:
            f = forme(dx + x, dy + y, fw, fh, 0, chemins[k], px=True)
            if op < 1:
                t.styles.style(t, f, {"opacity": op})
    for couleur, rs in (voiles if MAILLOT_OMBRES else []):
        for x, y, fw, fh in rs:
            forme(dx + x, dy + y, fw, fh, 0, couleur, px=True)
    # n° : centré sur le corps (PNG : corps ~ 24-76 % en largeur), un peu au-dessus du milieu
    zone = {"position": "absolute", "left": dx + round(0.24 * lm), "top": dy + round(0.22 * hm),
            "width": round(0.52 * lm), "height": round(0.5 * hm)}
    hote, coul = cadre, None
    setter = numero_kit_setter(t, cadre, zone)
    if setter is not None:
        hote, coul = setter, "fm-club-primary-color"
    else:
        msgs.append("maillot : SIStyleSetter de FM introuvable, n° en blanc")
    num = numero(t, src, nom_txt, hote, dict(police=round(dm["police"] * MAILLOT_NUMERO_TAILLE)))
    css = {"-unity-text-align": "middle-center", "margin-right": 0, "text-outline-width": 0}
    if coul:
        t.elem(num)["m_Classes"] = [c for c in t.elem(num).get("m_Classes") or [] if not c.startswith("fm-club-")] \
            + [coul]
        en = t.elem(num)   # couleur fixe de numero() retirée : le style intégré passerait devant la classe
        vals = t.styles.values(en["m_RuleIndex"]) if en.get("m_RuleIndex", -1) >= 0 else []
        reste = [p for p in vals if p[0] not in (PROPRIETES["color"][0], PROPRIETES["text-outline-color"][0])]
        en["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
        css.update({"flex-grow": 1, "align-self": "stretch"})
    else:
        css.update(zone, color=MAILLOT_NUMERO)
    t.styles.style(t, num, css)
    return msgs


MAILLOT_SETTER_SOURCE = ("TacticalTweakPlayerRow", "shirt-badge")   # SIStyleSetter de FM (couleurs du kit)


def numero_kit_setter(t, parent, css):
    """gom50 : SIStyleSetter (copie de #shirt-badge, sans sa fonction) : couleur 1 = KitHome.NumberColour, couleur 2
    = KitHome.NumberOutlineColour ; les textes de classe fm-club-primary-color dedans prennent la couleur 1"""
    s = Src(MAILLOT_SETTER_SOURCE[0])
    r = s.s and first(s.s, lambda r: s.s.name(r) == MAILLOT_SETTER_SOURCE[1]
                      and (s.s.elem(r).get("m_FullTypeName") or "").endswith("SIStyleSetter"))
    if r is None:
        return None
    st = s.clone(t, r, parent)
    for k in list(t.children(st)):
        t.remove(k)
    sd = t.sd(st)
    sd["name"] = ""
    sd["BindFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                          "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    sd["PrimaryColorDataLink"] = {"m_path": MAILLOT_KIT + ".NumberColour"}
    sd["SecondaryColorDataLink"] = {"m_path": MAILLOT_KIT + ".NumberOutlineColour"}
    t.elem(st)["m_Classes"], t.elem(st)["m_RuleIndex"] = ["column-direction-normal"], -1
    t.styles.style(t, st, {**css, "align-items": "stretch", "justify-content": "center"})
    return st


def numero(t, src, nom_txt, parent, dn):
    """n° du maillot en grand (copie du texte du nom, chemin NUMERO_CHEMIN), remplissage sombre + contour or"""
    num = src.clone(t, nom_txt, parent)
    sd = t.sd(num)
    sd["name"] = ""
    sd["DebugDisplay"] = "37"
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = NUMERO_CHEMIN
    t.elem(num)["m_Classes"] = [k for k in t.elem(num).get("m_Classes") or []
                                if k not in ("content-ellipsis", "flex-grow-class", "align-self-stretch",
                                             "margin-right-global-gap-regular")]
    t.styles.style(t, num, {"font-size": dn["police"], "color": NUMERO_COULEUR,
                            "text-outline-width": NUMERO_CONTOUR, "text-outline-color": NUMERO_CONTOUR_COULEUR,
                            "-unity-text-align": "middle-right", "white-space": "nowrap", "flex-shrink": 0,
                            "margin-top": 0, "margin-bottom": 0, "margin-right": 6})
    return num


def degrade_fondu(t, carte, degrade):
    """case fondue : dégradé du club de l'en-tête de FM (même fonction de couleur) recopié au fond de la carte (1er
    enfant, absolu, dessiné sous le contenu) ; num3 : halo = 2 moitiés en diagonale (HALO)"""
    cent = {"unit": 2, "value": 100.0}
    fond = boite(t, carte, {"position": "absolute", "left": 0, "top": 0, "width": cent, "height": cent,
                            "flex-direction": "row", "opacity": FONDU_OPACITE}, [])
    move(t, fond, carte, 0)
    for i, sens in enumerate(HALO):
        g = t.clone_shallow(degrade, fond)
        t.sd(g)["name"] = ""
        t.sd(g)["GradientDirection"] = sens
        t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
        coins = ("top-left", "bottom-left") if i == 0 else ("top-right", "bottom-right")
        t.styles.style(t, g, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "height": cent,
                              **{f"border-{c}-radius": CARTE_RAYON for c in coins}})


def trait_vertical(t, parent):
    boite(t, parent, {"width": 1, "min-width": 1, "flex-shrink": 0, "align-self": "stretch",
                      "background-color": TRAIT})


def bloc(t, parent, largeur, classes=("column-direction-normal",), css=None):
    """bloc de largeur fixe (ne grandit pas, ne rétrécit pas, coupe ce qui dépasse)"""
    return boite(t, parent, {"width": largeur, "min-width": largeur, "max-width": largeur, "flex-shrink": 0,
                             "flex-grow": 0, "overflow": "hidden", **(css or {})}, classes)


class Src:
    """sous-arbre d'un autre modèle, recopié avec ses styles et ses modèles inclus"""
    def __init__(self, modele):
        bundle, _, tt = nb.find_vta(modele)
        self.s = Tree(tt) if tt is not None else None
        self.styles = Styles(bundle, tt) if tt is not None else None

    def clone(self, t, r, parent, index=None):
        c = t.clone(r, parent, index, src=self.s)
        copy_usings(t, self.s, r)
        t.styles.copy_from(self.styles, t, c)
        return c


def titre(t, txt_src, txt_rid, parent, fr, en):
    """petit titre fixe (style du titre « Rapport de supervision » de FM : body-xs-strong, gris)"""
    c = t.clone(txt_rid, parent, src=txt_src.s)
    no_styles(t, c)
    sd = t.sd(c)
    sd["name"] = ""
    sd["text"], sd["text_UxmlAttributeFlags"] = L(fr, en), 1
    sd["DebugDisplay"] = sd["text"]
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    t.elem(c)["m_Classes"] = ["body-xs-strong", "global-text-secondary", "content-ellipsis",
                              "margin-bottom-global-gap-small"]
    return c


def remapper(t, modele_rm, parent, liens, classes=()):
    rm = t.clone_shallow(modele_rm, parent)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": k, "to": {"m_path": p}, "type": {"id": ty}}
                            for k, (p, ty) in liens.items()]
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = list(classes), -1
    return rm


def tuile_fm(t, parent, modele_rm, modele, liens, tous=False):
    """contenu d'une tuile de FM (son cadre retiré), paramètres -> données de l'en-tête ; message ou None ;
    tous : tous les liens (tuile dont les paramètres sont dans un BindingExpectComponent, pas sur la racine)"""
    src = Src(modele)
    if src.s is None:
        return f"{modele} introuvable"
    s = src.s
    racine = s.children(s.tt["m_VisualTree"]["rid"])[0]
    noms = [p.get("name") for p in s.sd(racine).get("Parameters") or []]
    rm = remapper(t, modele_rm, parent, {k: v for k, v in liens.items() if tous or k in noms}, ["align-self-stretch"])
    c = src.clone(t, racine, rm)
    for r in list(t.walk(c)):
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
    return None


def scout_lie(t, src, p, parent, rm_model):
    """bloc Niveau / Potentiel (scout) de FM recopié, dans un remapper player / team / human (2026-11-19, le joueur :
    clic sur les étoiles = rapport vide : le bouton de FM ouvre le rapport avec ces variables, absentes de notre copie)"""
    rm = remapper(t, rm_model, parent, {"player": ("person", JOUEUR), "team": ("person.Team", EQUIPE),
                                        "human": ("game.GameCurrentManager", JOUEUR)},
                  ["column-direction-normal", "align-items-center", "justify-content-center"])
    return src.clone(t, p["scout"], rm)


def si_club(t, s_vis, vis, bv, parent, club, chemin=None):
    """gom32 : conteneur affiché seulement pour un joueur de ton club (club=True, person.Team.IsHuman, comme
    hors_defaut) ou seulement pour les autres (club=False : inversé ; sans club = autres) ; chemin : autre condition"""
    import notes_installations as ni
    # gom70 / gom71 (BindingSetter « équipes du club contient person.Team » autour des cartes) RETIRÉS : l'enveloppe
    # tassait / décalait Progression, Efficacité et Recrutement chez tous les joueurs (vu en jeu, v2.08). Structure
    # d'avant remise ; joueur libre = si_libre (à côté, rien autour)
    b = copy.deepcopy(bv)
    b["m_kind"] = 1
    b["m_direct"] = {"Path": {"m_path": chemin or CHEMIN_CLUB}, "Nullable": 0}
    v = ni.new_visible(t, s_vis, vis, parent, None, "", b, ["column-direction-normal", "align-items-stretch"])
    sd = t.sd(v)
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = (0 if club else 1), 1
    t.elem(v)["m_RuleIndex"] = -1
    t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "min-width": 0, "overflow": "hidden",
                          "align-self": "stretch"})
    return v


def si_hors(t, s_vis, vis, bv, parent):
    """gom72 : conteneurs « hors club » : autre club (person.Team.IsHuman faux, gom32 tel quel) + joueur LIBRE
    (person.Team nul : liaison directe sur l'objet, inversée, comme CityOfBirthVisible de FM = « visible si pas nul »).
    Le contenu est posé dans les deux ; un seul est visible (club / autre club / libre s'excluent)"""
    autres = si_club(t, s_vis, vis, bv, parent, False)
    libre = si_club(t, s_vis, vis, bv, parent, False, chemin="person.Team")
    return [autres, libre]


def agent_hors_club(t, dans, rm_model, txt, msgs):
    """gom32 : carte Agent (joueur hors club) : titre, tuile agent de FM (nom + phrase), bouton de FM « Demander à
    l'agent » (FMActionButton ActionId ACTION_AGENT, comme la Transfer Room) sur le joueur affiché"""
    ts_, tr_ = txt
    if tr_ is not None:
        titre(t, ts_, tr_, dans, "Recrutement", "Recruitment")   # gom67 (le joueur : « rename la tuile ») : Agent
    # gom39 (le joueur : « fais respirer la tuile agent, que ça remplisse, tout bien centré ») : sous le titre, nom /
    # type d'agent / bouton centrés et répartis sur la hauteur
    corps = boite(t, dans, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "justify-content": "space-evenly",
                            "align-items": "center", "overflow": "hidden"}, ["column-direction-normal"])
    dans = corps
    m = tuile_fm(t, dans, rm_model, MODELE_AGENT, {"player": ("person", JOUEUR)})
    if m:
        msgs.append(m)
    # agent2 (le joueur : « 2 boutons interroger dans la tuile en petit en haut ») : la tuile de FM recopiée porte
    # déjà le bouton de bouton_tuile_agent (v14, posé dans le modèle) -> cette copie retirée, notre bouton gardé
    for r in [r for r in t.walk(corps) if (t.name(r) or "").startswith(PREFIXE + "BoutonAgent")]:
        if r in t.refs:
            t.remove(r)
    for r in t.walk(corps):
        el = t.elem(r)
        if t.name(r) == "Frame":
            el["m_Classes"] = [k for k in el.get("m_Classes") or [] if k != "align-items-start"] + ["align-items-center"]
        if (el.get("m_FullTypeName") or "").endswith("SIText"):
            t.styles.style(t, r, {"-unity-text-align": "middle-center"})
    src = Src(BOUTON_AGENT_SOURCE)
    btn = src.s and first(src.s, lambda r: src.s.name(r) == BOUTON_AGENT
                          and (src.s.elem(r).get("m_FullTypeName") or "").endswith("FMActionButton"))
    if btn is None:
        msgs.append("bouton « Demander à l'agent » de FM introuvable (le jeu a changé ?)")
        return
    zb = boite(t, dans, {"flex-shrink": 0}, ["row-direction-normal", "justify-content-center"])
    msgs += boutons_icones(t, zb, "person")   # gom67 : 3 icônes (agent, offre, shortlist)


def trait_bas(t, garder):
    """2026-11-19 (le joueur : « un fin séparateur sous l'en-tête, enlève-le ») : bordure du bas 1 px de
    .entity-background-header (FM, AlwaysAppliedStyleSheet / SIStyles) sur le remapper de l'en-tête : 0 en style
    intégré (vue tuile) ; garder=True : style intégré retiré (FM)"""
    r = first(t, lambda r: "entity-background-header" in (t.elem(r).get("m_Classes") or []))
    if r is None:
        return
    e = t.elem(r)
    pid = PROPRIETES["border-bottom-width"][0]
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    reste = [p for p in old if p[0] != pid]
    if garder:
        if len(reste) != len(old):
            e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    else:
        t.styles.style(t, r, {"border-bottom-width": 0})


FOND_SANS_CLUB = "UIPickerFondSansClub"   # pas PREFIXE : remettre_fm ne doit pas l'effacer avec son contenu


def couleur_club(t, degrade, garder):
    """option entete_couleur_club : dégradé du club de l'en-tête de FM gardé (style d'origine) ou caché ;
    sanscoul2 (le joueur, v43 vu : en-tête ENTIER disparu) : #PlayerReportHeaderGradient CONTIENT tout l'en-tête
    (2 317 éléments) -> opacité 0 cachait tout. « non » = contenu sorti dans un conteneur à sa mise en page
    (FOND_SANS_CLUB, copie de sa règle), dégradé vide gardé dedans (modèle des maillots), invisible ; « oui » = remis"""
    e = t.elem(degrade)
    sans_op = lambda vals: [p for p in vals if p[0] != PROPRIETES["opacity"][0]]
    par = t.parent.get(degrade)
    if par is not None and t.name(par) == FOND_SANS_CLUB:   # défaire : dégradé remis à la place du conteneur
        haut = t.parent[par]
        i = t.children(haut).index(par)
        move(t, degrade, haut, i)
        for k in list(t.children(par)):
            move(t, k, degrade)
        e["m_RuleIndex"] = t.elem(par).get("m_RuleIndex", -1)
        t.remove(par)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    reste = sans_op(old)
    if len(reste) != len(old):   # opacité 0 de sanscoul1 retirée
        e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    if garder:
        return
    haut = t.parent[degrade]
    fond = plain(t, haut, t.children(haut).index(degrade), list(e.get("m_Classes") or []), FOND_SANS_CLUB)
    t.elem(fond)["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    for k in list(t.children(degrade)):
        move(t, k, fond)
    move(t, degrade, fond, 0)
    e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    t.styles.style(t, degrade, {"opacity": 0.0, "position": "absolute", "width": 0, "height": 0})


MODELE_TUILE_AGENT = "PlayerAgentReportTile_2x2"
NOM_BOUTON_TUILE_AGENT = PREFIXE + "BoutonAgent-v11"   # v9 : 3 icônes ; v10 : cases + pastille grisée   # v2 : libellé court ; v3 : 145 px ; v4 : selon le texte ;
                                                      # v5 : texte dans le bouton de FM
# agent3 (le joueur : « change la phrase, mets juste interroger agent, pour toutes les langues ») : le FMActionButton
# écrit seul « Interroger agent sur disponibilité… » (aucun champ texte) -> son texte rendu transparent (règle
# « .CL_BOUTON_AGENT * { color: transparent } », spécificité 1000), largeur fixe, notre texte par-dessus (sans clic)
CL_BOUTON_AGENT = "uipicker-agent-libelle-v2"
CL_LIBELLE_AGENT = "uipicker-agent-texte-v1"   # gom61 : notre texte, blanc malgré la règle transparente
# 170 VU « un petit peu trop long » ; v4 (le joueur : « fais réagir le bouton à la largeur du texte, pour les autres
# langues ») : largeur = BOUTON_AGENT_PX par caractère (× 2 pour les idéogrammes / hangul) + BOUTON_AGENT_BASE
# (icône + marges du bouton de FM)
BOUTON_AGENT_PX, BOUTON_AGENT_BASE, BOUTON_AGENT_ICONE = 7, 36, 16


def largeur_texte_bouton(texte):
    larges = sum(1 for ch in texte if ord(ch) >= 0x1100)   # hangul, kana, CJK : pleine chasse
    return BOUTON_AGENT_BASE + BOUTON_AGENT_PX * (len(texte) + larges)
TEXTE_SOURCE = ("PlayerReportHeaderScoutSection", "ScoutReport")   # SIText de FM recopié pour nos textes fixes


def regle_bouton_agent(t, racine):
    """feuille intégrée attachée à la racine + règle « .CL_BOUTON_AGENT * » : textes du bouton de FM transparents"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(racine).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    sh = t.styles.sh
    if any(p.get("m_Value") == CL_BOUTON_AGENT for r in sh["m_Rules"] for cs in r.get("m_ComplexSelectors") or []
           for s in cs["m_Selectors"] for p in s["m_Parts"]):
        return
    idx = t.styles.add_rule([(PROPRIETES["color"][0], "", [(4, (0.0, 0.0, 0.0, 0.0))])])
    sh["m_Rules"][idx]["m_ComplexSelectors"] = [
        {"m_Specificity": 1000, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": CL_BOUTON_AGENT, "m_Type": 3}], "m_PreviousRelationship": 0},
            {"m_Parts": [{"m_Value": "*", "m_Type": 1}], "m_PreviousRelationship": 2}]}]   # 1 = *, 2 = descendant
    # gom61 (le joueur, gom57 vu : bouton orange vide) : notre texte est DANS le bouton -> « * » le rendait transparent
    # aussi (sur son élément texte interne) ; règle plus forte « .CL_LIBELLE_AGENT, .CL_LIBELLE_AGENT * » en blanc
    idx = t.styles.add_rule([(PROPRIETES["color"][0], "", [(4, (1.0, 1.0, 1.0, 1.0))])])
    sh["m_Rules"][idx]["m_ComplexSelectors"] = [
        {"m_Specificity": 2000, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": CL_LIBELLE_AGENT, "m_Type": 3}], "m_PreviousRelationship": 0}]},
        {"m_Specificity": 2000, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": CL_LIBELLE_AGENT, "m_Type": 3}], "m_PreviousRelationship": 0},
            {"m_Parts": [{"m_Value": "*", "m_Type": 1}], "m_PreviousRelationship": 2}]}]


def libelle_agent(t, zb, b):
    """bouton de FM b (dans la boîte zb) : libellé de FM caché, « Interroger agent » par-dessus ; message ou None"""
    src = Src(TEXTE_SOURCE[0])
    txt = src.s and first(src.s, lambda r: (src.s.elem(r).get("m_FullTypeName") or "").endswith("SIText")
                          and src.s.name(r) == TEXTE_SOURCE[1])
    if txt is None:
        return "texte de FM introuvable : libellé du bouton de l'agent gardé"
    regle_bouton_agent(t, t.children(t.tt["m_VisualTree"]["rid"])[0])
    t.elem(b)["m_Classes"] = [k for k in t.elem(b).get("m_Classes") or [] if not k.startswith("margin-")] \
        + [CL_BOUTON_AGENT]   # sans marge : notre texte (100 % de zb) reste centré sur le bouton
    libelle = L("Interroger agent", "Ask agent")
    w = largeur_texte_bouton(libelle)
    t.styles.style(t, b, {"width": w, "min-width": w, "max-width": w, "overflow": "hidden", "flex-shrink": 0})
    # gom57 (le joueur, joueur prêté : « Interroger agent » seul, FM avait caché son bouton) : texte mis DANS le
    # bouton -> gom61 vu : jamais affiché (le FMActionButton ne montre pas les enfants posés dans l'UXML)
    # gom65 : texte de nouveau par-dessus, frère du bouton dans zb ; zb sans largeur propre (= taille du bouton) et
    # overflow hidden : bouton caché par FM (display none) -> zb à 0 -> notre texte caché avec lui
    # gom66 (gom65 vu : texte décalé à droite, coupé : zb sans largeur fixe) : largeur w comme avant gom57 ; hauteur
    # = celle du bouton (bouton caché -> 0 -> texte coupé par overflow hidden)
    t.styles.style(t, zb, {"width": w, "min-width": w, "max-width": w, "overflow": "hidden", "flex-shrink": 0,
                           "flex-grow": 0, "align-self": "center"})
    c = t.clone(txt, zb, src=src.s)
    no_styles(t, c)
    sd = t.sd(c)
    sd["name"] = ""
    sd["text"], sd["text_UxmlAttributeFlags"] = libelle, 1
    sd["DebugDisplay"] = sd["text"]
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # Ignore : le clic va au bouton dessous
    t.elem(c)["m_Classes"] = ["body-s-strong", CL_LIBELLE_AGENT]
    t.styles.style(t, c, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                          "height": {"unit": 2, "value": 100.0}, "-unity-text-align": "middle-center",
                          "color": (1.0, 1.0, 1.0, 1.0), "margin-top": 0, "margin-bottom": 0,
                          "padding-left": BOUTON_AGENT_ICONE})   # v4 : centré à droite de l'icône de FM
    return None


# gom67 (le joueur : « dans la case agent, juste des logos, plus de phrase : 1 discussion agent, 1 pour faire une
# offre, 1 ajouter shortlist ») : 3 FMActionButton de FM (icône de l'action, libellé caché par la règle transparente,
# coupé par la largeur), infobulle à nous ; (modèle source, nom du bouton, ActionId, infobulle fr, en)
# gom68 (le joueur, gom67 vu : shortlist = liste déroulante de FM, « dégueulasse ») : bouton simple (ShowOnlyFirstButton,
# 1re liste) ; « les boutons indisponibles restent, grisés, pas cliquables ; un truc sombre par-dessus, pour tous les
# thèmes » : chaque bouton dans une case fixe ; dessous, une pastille sombre translucide avec l'icône de FM estompée
# (visible quand FM retire son bouton, action indisponible) ; (…, icône de la pastille)
BOUTONS_ICONES = (
    ("TransferRoomInMainBlock", "ask-agent-availability-button", ACTION_AGENT, "Interroger agent", "Ask agent",
     "ui-concepts-speech-bubble_small"),
    ("RecruitmentAgentOffersFrame", "make-offer-button", 1933656696, "Faire une offre", "Make an offer",
     "game-concepts-money-in-cash-up_small"),
    ("RecruitmentAgentOffersFrame", "add-to-shortlist-button", 1097488485, "Ajouter à la shortlist",
     "Add to shortlist", "game-concepts-shortlist_small"),
)
# gom69 (le joueur, gom68 vu : shortlist « toujours bouffée », FM garde sa liste déroulante) : ces boutons-là
# habillés : bouton de FM invisible (opacité 0, garde le clic et sa liste), par-dessus (sans clic) un bouton primaire
# du thème de FM (classe buttons-button-primary-default) avec l'icône ; le tout dans une boîte haute comme le bouton
# de FM (bouton retiré -> boîte à 0 -> habillage caché, pastille grisée visible)
BOUTONS_HABILLES = {1097488485}
CL_BOUTON_PRIMAIRE = "buttons-button-primary-default"
BOUTON_ICONE_PX, BOUTON_ICONE_HAUT, BOUTON_ICONE_ECART = 34, 28, 8


def _textes_a_traduire():   # jamais appelée : repère pour notes_claude\traductions_relever.py (textes en variables)
    return (L("Interroger agent", "Ask agent"), L("Faire une offre", "Make an offer"),
            L("Ajouter à la shortlist", "Add to shortlist"), L("Recrutement", "Recruitment"))
BOUTON_GRISE_FOND, BOUTON_GRISE_ICONE = (0.0, 0.0, 0.0, 0.35), 0.35   # pastille sombre ; opacité de son icône


def boutons_icones(t, zb, chemin):
    """les 3 boutons-icônes de BOUTONS_ICONES dans la boîte zb (en ligne), sur le joueur chemin ; messages"""
    msgs = []
    regle_bouton_agent(t, t.children(t.tt["m_VisualTree"]["rid"])[0])
    t.styles.style(t, zb, {"flex-shrink": 0, "align-self": "center", "justify-content": "center"})
    sources = {}
    w, h = BOUTON_ICONE_PX, BOUTON_ICONE_HAUT
    rayon = 4
    coins = {k: rayon for k in ("border-top-left-radius", "border-top-right-radius", "border-bottom-left-radius",
                                "border-bottom-right-radius")}
    for i, (modele, nom, action, fr, en, icone) in enumerate(BOUTONS_ICONES):
        if modele not in sources:
            sources[modele] = Src(modele)
        src = sources[modele]
        btn = src.s and first(src.s, lambda r: src.s.name(r) == nom
                              and (src.s.elem(r).get("m_FullTypeName") or "").endswith("FMActionButton"))
        if btn is None:
            msgs.append(f"bouton « {fr} » de FM introuvable (le jeu a changé ?)")
            continue
        case = boite(t, zb, {"width": w, "min-width": w, "max-width": w, "height": h, "min-height": h,
                             "max-height": h, "flex-shrink": 0, "margin-left": BOUTON_ICONE_ECART if i else 0},
                     ["column-direction-normal", "justify-content-center", "align-items-center"])
        # pastille « indisponible » (dessous : cachée par le bouton de FM quand il est là)
        pg = boite(t, case, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                             "height": {"unit": 2, "value": 100.0}, "background-color": BOUTON_GRISE_FOND, **coins},
                   ["row-direction-normal", "justify-content-center", "align-items-center"])
        ic = boite(t, pg, {"flex-shrink": 0, "opacity": BOUTON_GRISE_ICONE}, [icone])
        t.sd(ic)["pickingMode"], t.sd(ic)["pickingMode_UxmlAttributeFlags"] = 1, 1
        t.sd(pg)["tooltip"], t.sd(pg)["tooltip_UxmlAttributeFlags"] = L(fr, en), 1
        habille_ = action in BOUTONS_HABILLES
        dans_b = case
        if habille_:
            dans_b = boite(t, case, {"width": w, "min-width": w, "max-width": w, "overflow": "hidden",
                                     "flex-shrink": 0}, ["column-direction-normal"])
        b = src.clone(t, btn, dans_b)
        sd = t.sd(b)
        sd["name"] = ""
        sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": chemin}, 1
        sd["ActionId"], sd["ActionId_UxmlAttributeFlags"] = action, 1
        sd["StyleAsPrimaryButton"], sd["StyleAsPrimaryButton_UxmlAttributeFlags"] = 1, 1
        sd["ShowOnlyFirstButton"], sd["ShowOnlyFirstButton_UxmlAttributeFlags"] = 1, 1   # gom68 : pas de liste
        sd["tooltip"], sd["tooltip_UxmlAttributeFlags"] = L(fr, en), 1
        t.elem(b)["m_Classes"] = [k for k in t.elem(b).get("m_Classes") or []
                                  if not k.startswith(("margin-", "padding-"))] + [CL_BOUTON_AGENT]
        t.styles.style(t, b, {"width": w, "min-width": w, "max-width": w, "overflow": "hidden", "flex-shrink": 0})
        if habille_:
            t.styles.style(t, b, {"opacity": 0.0})
            hb = boite(t, dans_b, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                                   "height": {"unit": 2, "value": 100.0}, "padding-left": 0, "padding-right": 0,
                                   "margin-left": 0, "margin-right": 0, "margin-top": 0, "margin-bottom": 0},
                       [CL_BOUTON_PRIMAIRE, "row-direction-normal", "justify-content-center", "align-items-center"])
            ih = boite(t, hb, {"flex-shrink": 0}, [icone])
            for x in (hb, ih):
                t.sd(x)["pickingMode"], t.sd(x)["pickingMode_UxmlAttributeFlags"] = 1, 1   # le clic va à FM
    return msgs


def bouton_tuile_agent(t):
    """2026-11-19 (le joueur : « en Large en bas à droite, une tuile que pour ici, avec un bouton parler à l'agent ») :
    tuile Agent 2x2 de FM (posée par fiche_ordre_tuiles en Large, joueur hors club) : nom / type centrés + bouton de
    FM « Demander à l'agent » (comme la carte Agent de l'en-tête) sur le joueur de la tuile"""
    if named(t, NOM_BOUTON_TUILE_AGENT):
        return []
    for r in [r for r in t.walk() if (t.name(r) or "").startswith(PREFIXE + "BoutonAgent")]:   # ancienne version
        if r in t.refs:
            t.remove(r)
    frame = first(t, lambda r: t.name(r) == "Frame")
    src = Src(BOUTON_AGENT_SOURCE)
    btn = src.s and first(src.s, lambda r: src.s.name(r) == BOUTON_AGENT
                          and (src.s.elem(r).get("m_FullTypeName") or "").endswith("FMActionButton"))
    if frame is None or btn is None:
        return ["tuile Agent : cadre ou bouton de FM introuvable (le jeu a changé ?), pas de bouton"]
    par = t.parent[frame]
    t.elem(frame)["m_Classes"] = [k for k in t.elem(frame).get("m_Classes") or [] if k != "align-items-start"] \
        + ["align-items-center"]
    t.styles.style(t, par, {"justify-content": "space-evenly", "align-items": "center"})
    zb = boite(t, par, {"flex-shrink": 0}, ["row-direction-normal", "justify-content-center"], NOM_BOUTON_TUILE_AGENT)
    t.sd(zb)["name_UxmlAttributeFlags"] = 1
    m = boutons_icones(t, zb, "player")   # gom67 : 3 icônes (agent, offre, shortlist)
    return ["tuile Agent : boutons agent / offre / shortlist"] + m


def attentes_hors_club(t, dans, rm_model, txt, msgs, sv):
    """gom32 : carte Attentes (joueur hors club) : valeur de transfert + demande salariale attendues du rapport de
    recrutement (TransferInfo de FM) ; dessous, les demandes de l'agent une fois contacté (liste de
    PlayerInfoInterestExpectations : Person.PlayerAgentDemands), comme le rapport des messages"""
    ts_, tr_ = txt
    if tr_ is not None:
        titre(t, ts_, tr_, dans, "Attentes", "Expectations")
    # gom33 (le joueur, gom32 vu : réponse de l'agent coupée tout en bas) : demandes / réponse de l'agent EN PREMIER
    # (ne rétrécit pas), rapport de recrutement dessous (coupé s'il n'y a plus de place)
    src = Src(MODELE_DEMANDES)
    cadre = src.s and first(src.s, lambda r: src.s.name(r) == "Frame_KnownExpectations")
    rmd = cadre is not None and next((k for k in src.s.walk(cadre) if k != cadre and (
        src.s.elem(k).get("m_FullTypeName") or "").endswith("BindingRemapper")), None)
    s_vis, vis, bv = sv
    if rmd:
        # gom37 (le joueur : phrases de l'agent l'une sur l'autre) : lignes à hauteur variable (DynamicElements de
        # la liste de FM) ; affichées seulement quand l'agent a répondu (CHEMIN_DEMANDES pas nul), à la place du
        # rapport
        # gom41 (vu : Attentes vide, les 2 conditions cachées : FM ne lit pas un objet comme un booléen) : sans
        # condition, demandes en haut (hauteur variable), rapport dessous
        zd = boite(t, dans, {"flex-shrink": 0, "min-height": 0, "margin-bottom": 4},
                   ["column-direction-normal", "align-items-stretch"])
        c = src.clone(t, rmd, zd)
        for r in t.walk(c):   # liste de FM : marges du bas retirées (place comptée)
            el = t.elem(r)
            if el.get("m_Classes"):
                el["m_Classes"] = [k for k in el["m_Classes"] if not k.startswith(("margin-bottom", "item_padding"))]
            if (el.get("m_FullTypeName") or "").endswith("StreamedObjectList"):
                t.sd(r)["DynamicElements"], t.sd(r)["DynamicElements_UxmlAttributeFlags"] = 1, 1
    else:
        msgs.append("demandes de l'agent (PlayerInfoInterestExpectations) introuvables (le jeu a changé ?)")
    # gom42 (le joueur : « remets ce qu'il y avait avant », « c'est bien mieux ») : ordre de gom32 = rapport
    # (Transfer Information) en haut, demandes de l'agent dessous (hauteur variable gardée, coupées s'il manque de
    # la place)
    zr = boite(t, dans, {"flex-shrink": 0, "min-height": 0}, ["column-direction-normal", "align-items-stretch"])
    if rmd:
        move(t, zr, dans, t.children(dans).index(zd))
        t.styles.style(t, zd, {"flex-shrink": 1, "flex-grow": 1, "overflow": "hidden", "margin-bottom": 0,
                               "margin-top": 6})
    m = tuile_fm(t, zr, rm_model, MODELE_INFO_TRANSFERT,
                 {"player": ("person", JOUEUR), "human": ("game.GameCurrentManager", JOUEUR),
                  "report": (PC_RAPPORT, TYPE_RAPPORT)}, tous=True)
    if m:
        msgs.append(m)


def habiller_progression(t, carte_p, txt):
    """v30 (le joueur : « la mini courbe, mais plus belle, pas juste dans le vide ») : titre « Progression » en haut
    de la carte, tendance (icône + phrase de FM) dessous, courbe dans un bandeau sombre aux coins ronds qui prend le
    reste de la hauteur"""
    ts, tr = txt
    if tr is not None:
        c = titre(t, ts, tr, carte_p, "Progression", "Progression")
        move(t, c, carte_p, 0)
    courbe = first(t, lambda r: t.name(r) == "data_display-graphs-tile-line_chart"
                   and r in set(t.walk(carte_p)))
    if courbe is None:
        return "Progression : courbe introuvable (pas de bandeau)"
    t.styles.style(t, courbe, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "margin-top": 6,
                               "background-color": COURBE_FOND, "padding-top": 4, "padding-bottom": 4,
                               "padding-left": 6, "padding-right": 6,
                               **{f"border-{c}-radius": 6 for c in ("top-left", "top-right", "bottom-left",
                                                                    "bottom-right")}})
    # les conteneurs entre la carte et la courbe prennent toute la hauteur (la courbe s'étire)
    r = t.parent[courbe]
    while r is not None and r != carte_p:
        t.styles.style(t, r, {"flex-grow": 1, "min-height": 0})
        r = t.parent.get(r)


def centrer(t, top):
    """v26 : contenu de FM centré dans sa carte : plus de largeur 100 % ni de calage à gauche, conteneurs centrés"""
    retire = {"width-100-percent", "align-items-start", "align-self-start", "content-left-align"}
    for r in t.walk(top):
        e = t.elem(r)
        if e.get("m_Classes") is None or typ(t, r).endswith(("Component", "SIText")):
            if e.get("m_Classes"):
                e["m_Classes"] = [k for k in e["m_Classes"] if k not in retire]
            continue
        e["m_Classes"] = [k for k in e["m_Classes"] if k not in retire]
        if "align-items-center" not in e["m_Classes"]:
            e["m_Classes"].append("align-items-center")
    return top


def club_retrecissable(t, top):
    """v25 : bloc club déplié sous top : chaque niveau rétrécit (max 100 %, min 0, sans flex-no-shrink) sauf le
    logo, pour que la cellule du nom (max 100 %, « … » de FM) soit bornée par la carte ; infobulle du nom complet
    quand il est coupé (DisplayTooltipWhenElided du texte de la cellule, par surcharge du modèle inclus) ;
    message ou None"""
    cent = {"unit": 2, "value": 100.0}
    for r in list(t.walk(top)):
        alias = t.elem(r).get("m_TemplateAlias") or ""
        if "Icon" in alias:
            continue
        e = t.elem(r)
        if e.get("m_Classes") is not None:
            e["m_Classes"] = [k for k in e["m_Classes"] if k != "flex-no-shrink-class"]
        if typ(t, r).endswith(("BindingRemapperComponent", "BindingSetterComponent")):
            continue
        t.styles.style(t, r, {"max-width": cent, "min-width": 0, "flex-shrink": 1})
    cell = Src(CELLULE_CLUB)
    txt = cell.s and first(cell.s, lambda r: cell.s.name(r) == "primary-text")
    if txt is None:
        return f"{CELLULE_CLUB} : texte introuvable (pas d'infobulle du nom du club)"
    ident = cell.s.sd(txt)["uxmlAssetId"]
    for inst in [r for r in t.walk(top) if t.elem(r).get("m_TemplateAlias") == CELLULE_CLUB]:
        ovs = t.elem(inst).setdefault("m_SerializedDataOverride", [])
        o = next((o for o in ovs if o["m_ElementId"] == ident), None)
        if o is None:
            ref = copy.deepcopy(cell.s.refs[cell.s.elem(txt)["m_SerializedData"]["rid"]])
            ref["rid"] = t.new_rid()
            t.refs[ref["rid"]] = ref
            t.tt["references"]["RefIds"].append(ref)
            ovs.append({"m_ElementId": ident, "m_ElementIdsPath": [ident], "m_SerializedData": {"rid": ref["rid"]}})
            d = ref["data"]
        else:
            d = t.refs[o["m_SerializedData"]["rid"]]["data"]
        for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
            d[k], d[k + "_UxmlAttributeFlags"] = 1, 1
    return None


def regle_cartes(t, racine):
    """v31 : « .CL_CARTE { background-color: CARTE_FOND } » dans la feuille intégrée du modèle (une fois), feuille
    rattachée à la racine de la tuile (comme salle_trophees.barre_au_survol) ; spécificité d'une classe (10) :
    la règle de couleurs_interface (tuiles) passe devant"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(racine).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    sh = t.styles.sh
    if any(p.get("m_Value") == CL_CARTE for r in sh["m_Rules"] for cs in r.get("m_ComplexSelectors") or []
           for s in cs["m_Selectors"] for p in s["m_Parts"]):
        return
    idx = t.styles.add_rule([(PROPRIETES["background-color"][0], "", [(4, CARTE_FOND)])])
    sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 10, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": [{"m_Value": CL_CARTE, "m_Type": 3}], "m_PreviousRelationship": 0}]}]


# ---------- la tuile ----------
def construire(t, parent, index, dims, src, p, txt, photo, haut_src, poly_src, rm_model, s_vis, vis, degrade):
    """v3 : la tuile prend toute la largeur ; blocs en parts fixes de la largeur (POIDS : même place pour tous les
    joueurs, rien ne dépend du contenu) ; grille en 2 rangées (traits alignés) ; barre aux couleurs du club"""
    import notes_installations as ni
    v, h = MARGE
    # le setter de la bannière (variables hasContract / teamtodisplay lues par le bloc du club)
    # (élément d'un autre modèle : recopié avec ses enfants, puis vidé ; clone_shallow ne lit que t)
    racine = t.clone(p["setter"], parent, index, src=src.s)
    for k in list(t.children(racine)):
        t.remove(k)
    t.sd(racine)["name"], t.sd(racine)["name_UxmlAttributeFlags"] = NOM, 1
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = ["align-self-stretch"], -1
    regle_cartes(t, racine)
    # v25 (le joueur) : plus de cadre (fond, bords, coins) : seul le trait du bas sépare l'en-tête de la fiche
    haut_css = {"height": dims["haut"], "min-height": dims["haut"], "max-height": dims["haut"]}
    if ENTETE_PLUS:   # hauteur auto entre haut (Large) et haut + le plus grand ajout (cales liées au mode, plus bas)
        haut_css = {"min-height": dims["haut"], "max-height": dims["haut"] + max(ENTETE_PLUS_MODE.values())
                    + (ENTETE_PLUS_HORS_CLUB if STYLE_GOMEZ else 0)}
    carte = boite(t, racine, {
        "flex-direction": "row", "align-items": "stretch", **haut_css, "flex-shrink": 0, "flex-grow": 1,
        "overflow": "hidden",
        # v44 (le joueur, v43 vu : « barre toujours là ») : c'était CE trait (v25), pas celui de FM -> transparent
        # (1 px gardé : hauteur de 180 px pile, anti-tremblement v40 / v41)
        "border-bottom-width": 1, "border-bottom-color": (0.0, 0.0, 0.0, 0.0),
        "padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
        "margin-top": dims.get("marge_haut", MARGE_HAUT), "margin-bottom": dims.get("marge_haut", MARGE_HAUT),
        "margin-left": MARGE_COTES,
        "margin-right": MARGE_COTES,
        **({"border-left-width": NUMERO_TRAIT, "border-left-color": OR} if STYLE_NUMERO else {})},
        ["align-self-stretch"])
    if ENTETE_PLUS:
        # cale sans largeur, haute de haut + ENTETE_PLUS (moins marges intérieures et trait du bas), seulement en
        # Medium / Small (mode > 0) : la tuile grandit, les cartes (étirées) suivent ; Large : rien, tuile à haut
        # une cale par affichage (Medium +70, Small +40) ; gom18 : aiguillage (pas de SIVisible : au chargement toutes
        # les cales étaient là -> en-tête au plus haut puis qui se rétracte)
        mince = {"width": 0, "min-width": 0, "flex-shrink": 0}
        vc = aiguillage_mode(t, src, p, carte, mince, mince)
        for m, plus in ENTETE_PLUS_MODE.items():
            cale_h = dims["haut"] + plus - 2 * v - 1
            boite(t, vc[m], {**mince, "height": cale_h, "min-height": cale_h})
        if ENTETE_PLUS_HORS_CLUB and STYLE_GOMEZ:
            # gom35 (le joueur : joueur hors club, vide en bas de la fiche en Medium / Small, fiche plus courte ;
            # PAS en Large) : 2e cale plus haute de ENTETE_PLUS_HORS_CLUB px, seulement pour un joueur hors club
            for m, plus in ENTETE_PLUS_MODE.items():
                cale_h = dims["haut"] + plus + ENTETE_PLUS_HORS_CLUB - 2 * v - 1
                hors = si_club(t, s_vis, vis, s_vis.sd(vis)["Binding"], vc[m], False)
                t.styles.style(t, hors, {**mince, "flex-grow": 0})
                boite(t, hors, {**mince, "height": cale_h, "min-height": cale_h})
    # touche de couleur du club (le joueur : « pas une couleur entière », « du haut vers le bas, comme la tuile de
    # base du jeu ») : le dégradé de l'en-tête d'origine recopié (même fonction de couleurs, GradientDirection 11 =
    # TopToBottomWithAlphaTweak, ordre de l'énumération lu dans global-metadata), en fond de toute la tuile,
    # derrière le contenu (1er enfant, position absolue)
    if degrade is not None and DEGRADE_CLUB:
        g = t.clone_shallow(degrade, carte, 0)
        t.sd(g)["name"] = ""
        t.sd(g)["GradientDirection"] = DIRECTION_DEGRADE
        t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = [], -1
        t.styles.style(t, g, {"position": "absolute", "left": 0, "top": 0, "width": {"unit": 2, "value": 100.0},
                              "height": {"unit": 2, "value": 100.0},
                              **{f"border-{c}-radius": RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                        "bottom-right")}})
    e = dims["ecart"]
    msgs = []
    if STYLE_NUMERO:
        _FONDU[id(t)] = degrade
        if degrade is None:
            msgs.append("en-tête : dégradé du club introuvable, cases sans fond")
    POIDS = {**globals()["POIDS"], **dims.get("poids", {})}   # v18 : parts propres à une bannière

    def sep(dans=None):
        """v24 : écart entre deux cartes (plus de trait)"""
        dans = carte if dans is None else dans
        boite(t, dans, {"width": e, "min-width": e, "max-width": e, "flex-shrink": 0})

    def habille(css, bord=CARTE_BORD, padding=True):
        """v24 : style d'une carte (fond, bord, coins ronds, marges intérieures) ; entete_style numero : case fondue
        (dégradé du club de FM au fond, ni bord ni trait ; le joueur : « effet case, mais fondu, pas de séparateur »)"""
        cv_, ch_ = CELLULE
        if STYLE_GOMEZ:   # tuile : fond CL_CARTE, coins ronds, sans bord
            css.update({"_carte": True, **{f"border-{c}-radius": CARTE_RAYON for c in (
                "top-left", "top-right", "bottom-left", "bottom-right")}})
            if padding:
                css.update({"padding-top": cv_ + 2, "padding-bottom": cv_ + 2, "padding-left": GOMEZ_MARGE,
                            "padding-right": GOMEZ_MARGE})
            return css
        if STYLE_NUMERO:
            css.update({"_fondu": True, "overflow": "hidden",
                        **{f"border-{c}-radius": CARTE_RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                        "bottom-right")}})
            if padding:
                css.update({"padding-top": cv_, "padding-bottom": cv_, "padding-left": ch_, "padding-right": ch_})
            return css
        css.update({"_carte": True,   # v31 : fond CARTE_FOND par la classe (regle_cartes)
                    **{f"border-{c}-width": 1 for c in ("top", "bottom", "left", "right")},
                    **{f"border-{c}-color": bord for c in ("top", "bottom", "left", "right")},
                    **{f"border-{c}-radius": CARTE_RAYON for c in ("top-left", "top-right", "bottom-left",
                                                                    "bottom-right")}})
        if padding:
            css.update({"padding-top": cv_, "padding-bottom": cv_, "padding-left": ch_, "padding-right": ch_})
        return css

    def part(dans, poids, classes, css=None):
        """bloc qui prend poids parts de la largeur (flex-basis 0 : ne dépend pas du contenu, coupe le surplus)"""
        return boite(t, dans, {"flex-grow": poids, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                               "overflow": "hidden", **(css or {})}, classes)

    if STYLE_GOMEZ:
        msgs += tuiles_gomez(t, carte, dims, src, p, txt, photo, haut_src, rm_model, s_vis, vis, habille, sep, part,
                             degrade)
        msgs += zone_droite(t, carte, dims, poly_src, rm_model, s_vis, vis, txt, habille, sep)
        return msgs
    # photo ; entete_style numero : grand numéro du maillot derrière (dessiné AVANT la photo = dessous), photo décalée
    nom_txt = first(src.s, lambda r: r in set(src.s.walk(p["nom"]))
                    and "person.Name" in str(src.s.sd(r).get("TextBinding") or ""))
    if STYLE_NUMERO and nom_txt is not None:
        dn = dims["numero"]
        zph = boite(t, carte, {"flex-shrink": 0, "align-self": "stretch", "margin-right": e},
                    ["row-direction-normal", "align-items-center"])
        numero(t, src, nom_txt, zph, dn)
        ph = t.clone(photo, zph)
        t.styles.style(t, ph, {"flex-shrink": 0, "align-self": "center"})
    else:
        if STYLE_NUMERO:
            msgs.append("en-tête grand numéro : nom introuvable, numéro pas posé")
        ph = t.clone(photo, carte)
        t.styles.style(t, ph, {"flex-shrink": 0, "align-self": "center", "margin-right": e})
    t.sd(ph)["name"] = ""
    t.elem(ph)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    if ENTETE_PLUS:   # tuile en hauteur auto : photo bornée à la hauteur Large (avant : coupée par la tuile, pareil)
        ph_max = dims["haut"] - 2 * MARGE[0] - 1
        t.styles.style(t, ph, {"max-height": ph_max, "overflow": "hidden"})
    # identité
    ident = part(carte, POIDS["ident"], ["column-direction-normal", "justify-content-center"])
    for k in ("nom", "poste"):
        c = src.clone(t, p[k], ident)
        t.styles.style(t, c, {"flex-shrink": 0, "margin-bottom": 4})
        if k == "nom" and STYLE_NUMERO:   # nom plus gros
            for r in t.walk(c):
                if "person.Name" in str(t.sd(r).get("TextBinding") or ""):
                    t.styles.style(t, r, {"font-size": dims["numero"]["nom"]})
    if haut_src:
        hs, hr = haut_src
        c = t.clone(hr, ident, src=hs)
        t.styles.copy_from(hs.styles, t, c)
        copy_usings(t, hs, hr)
        t.sd(c)["name"] = ""
        t.elem(c)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"]
        kids = t.children(c)
        if kids:
            t.elem(kids[0])["m_Classes"] = ["global-text-secondary", "body-sm", "margin-right-global-gap-small"]
    ligne = boite(t, ident, {"flex-shrink": 0}, ["row-direction-normal", "align-items-center"])
    a = src.clone(t, p["actions"], ligne)
    t.sd(a)["name"] = ""
    f = src.clone(t, p["flags"], ligne)
    t.elem(f)["m_Classes"] = ["margin-left-global-gap-regular"]
    sep()
    # grille (v3, le joueur) : 3 carrés côte à côte, séparés par des traits : [Nation + sélections / Âge],
    # [Contrat + temps de jeu / Valeur], [Club seul, toute la hauteur : un joueur prêté a 2 clubs (parent + prêt)] ;
    # trait du milieu des 2 premiers carrés à la même hauteur (et à celle du trait Statut / Éligibilité)
    cv, ch = CELLULE

    def carre(poids, avec_trait):
        if avec_trait:
            sep()
        return part(carte, poids, ["column-direction-normal", "align-self-stretch"])

    def moitie(c, haut_, bord=CARTE_BORD):
        # v24 : une carte (moitié haute ou basse d'une colonne), écart e entre les deux
        css = habille({"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden",
                       "justify-content": "center"}, bord)
        css["margin-bottom" if haut_ else "margin-top"] = e // 2
        return boite(t, c, css, ["column-direction-normal", "align-items-center"])   # v25 : centré

    # v4 (le joueur) : en haut Âge | Nation, en bas Salaire (contrat + temps de jeu) | Valeur
    # v13 (le joueur : en Medium, sélections jeunes et 3e pays coupés) : 2 versions de la paire Âge | Nation, chacune
    # avec ses parts (POIDS_PAIRE) : Large (mode == 0 : 3 lettres, une ligne de sélections) et Medium / Small
    # (mode > 0 : noms complets, sélections A et jeunes côte à côte) ; la paire garde la même part de la tuile
    b = s_vis.sd(vis)["Binding"]
    court = None   # v8 : nationalités en 3 lettres (ligne posée par entete_fiche, nations_courtes_large)
    for r in src.s.walk():
        if src.s.name(r) == "UIPickerNationsCourtesLarge-v1" and src.s.children(r):
            court = src.s.children(r)[0]
            break
    if court is None:
        court = p.get("nat3")   # v17 : nation en 3 lettres de la bannière de FM27
    paire = part(carte, POIDS["paire"], ["row-direction-normal", "align-self-stretch"])
    for large, liaison in ((True, ni.equal_binding(b, MODE, 0)), (False, ni.make_binding(b, 4, [MODE], 0))):
        p_age, p_nat = POIDS_PAIRE["large" if large else "autres"]
        zone = ni.new_visible(t, s_vis, vis, paire, None, "", liaison, ["row-direction-normal"])
        t.styles.style(t, zone, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                 "align-self": "stretch", "overflow": "hidden"})
        c1 = part(zone, p_age, ["column-direction-normal", "align-self-stretch"])
        src.clone(t, p["age"], moitie(c1, True))
        centrer(t, src.clone(t, p["contrat"], moitie(c1, False)))   # v26 : salaire / temps de jeu centrés
        sep(zone)
        c2 = part(zone, p_nat, ["column-direction-normal", "align-self-stretch"])
        h1 = moitie(c2, True)
        n = src.clone(t, court if (large and court is not None) else p["nat"], h1)
        t.sd(n)["name"] = ""
        k = src.clone(t, p["caps"], h1)
        t.elem(k)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        cellules = [x for x in t.children(k) if (t.elem(x).get("m_TemplateAlias") or "") == "text-cell-button-medium"]
        if not large:   # sélections A et jeunes côte à côte
            for x in cellules:
                t.elem(x)["m_Classes"] = ["margin-right-global-gap-regular"]
        elif len(cellules) == 2:
            # Large (v6) : une seule ligne : sélections A, ou jeunes avant AGE_JEUNE ans ; tout le détail (A +
            # jeunes) reste dans l'infobulle de FM au survol (InternationalCapsAndGoalsStringIncludingYouth)
            # v35 : A aussi avant AGE_JEUNE ans dès qu'il a joué en A
            ni.selections_une_ligne(t, s_vis, vis, k, cellules, b, AGE_JEUNE)
        src.clone(t, p["valeur"], moitie(c2, False, CARTE_BORD_VALEUR))
    c3 = carre(POIDS["club"], True)
    bc = boite(t, c3, habille({"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "overflow": "hidden",
                               "justify-content": "center"}),
               ["column-direction-normal", "align-items-center"])
    # v9 (le joueur : nom du club mordu en Large) : en Large, contenu du bloc club de FM recopié avec le nom court
    # (primarytext team.Name -> club.ShortName dans ses remappers) ; Medium / Small : nom complet
    # v25 (le joueur : nom coupé net quand il est long) : bloc de FM déplié dans TOUS les modes pour que toute la
    # chaîne rétrécisse (max 100 %, min 0) jusqu'à la cellule du nom (« … » de FM) ; nom complet au survol
    clubs = Src(CLUB)
    cr = clubs.s and clubs.s.children(clubs.s.tt["m_VisualTree"]["rid"])
    cr = cr and clubs.s.children(cr[0])
    if cr:
        for court, liaison in ((True, ni.equal_binding(b, MODE, 0)), (False, ni.make_binding(b, 4, [MODE], 0))):
            nl = ni.new_visible(t, s_vis, vis, bc, None, "", liaison)
            c = clubs.clone(t, cr[0], nl)
            if court:
                for r in t.walk(c):
                    for prop in t.elem(r).get("m_Properties") or []:
                        if prop.get("name") == "mappings" and isinstance(prop.get("value"), str):
                            prop["value"] = prop["value"].replace("primarytext:team.Name:",
                                                                  "primarytext:club.ShortName:")
            msg = club_retrecissable(t, nl)
            if msg:
                msgs.append(msg)
    else:
        src.clone(t, p["club"], bc)
    st = Src(STATUT)

    def statut_cadre(h, nom_titre):
        titre_fm = st.s and first(st.s, lambda r: st.s.name(r) == nom_titre)
        if titre_fm is None:
            msgs.append(f"{STATUT} : {nom_titre} introuvable")
            return
        rm = remapper(t, rm_model, h, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
        c = st.clone(t, st.s.parent[titre_fm], rm)
        t.sd(c)["name"] = ""
        # v36 (2026-11-15, le joueur : « dispo transfert mal aligné dans sa case ») : cadre de FM en align-items-start
        # -> titre et valeur centrés dans la carte
        t.elem(c)["m_Classes"] = ["column-direction-normal", "align-items-center", "justify-content-center"]
        t.styles.style(t, c, {"margin-bottom": 0})   # FM : 8 px dessous (texte remonté)
        return c

    def statut_court(c):
        """v34 (le joueur : « Indisponible » coupé en 2 lignes en Large) : valeur sur une ligne, « … » si elle ne tient
        pas (FM n'a pas de diminutif traduit), texte complet au survol (DisplayTooltipWhenElided)"""
        cent = {"unit": 2, "value": 100.0}
        for r in t.walk(c):
            if not t.name(r).endswith("-value-text") and not t.name(r).endswith("-style-setter"):
                continue
            t.styles.style(t, r, {"max-width": cent, "min-width": 0, "flex-shrink": 1, "overflow": "hidden"})
            if typ(t, r).endswith("SIText"):
                t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis"})
                for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                    t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1

    if "statut_niveau" in POIDS:
        # v32 (le joueur, Large : « fais de la place pour le nom ») : une colonne, en haut Dispo. transfert | Dispo.
        # prêt côte à côte, en bas Niveau / Potentiel ; la place gagnée va à l'identité
        sep()
        col = part(carte, POIDS["statut_niveau"], ["column-direction-normal", "align-self-stretch"])
        # v33 (rapport de supervision qui débordait) : Niveau un peu plus haut que les Dispo., marges du haut / bas
        # réduites dans les cartes
        haut_ = boite(t, col, {"flex-grow": 0.85, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                               "margin-bottom": e // 2}, ["row-direction-normal", "align-self-stretch"])
        for i, nom_titre in enumerate(STATUT_CADRES):
            if i:
                sep(haut_)
            hc = boite(t, haut_, {**habille({"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                             "overflow": "hidden", "justify-content": "center"}),
                                  "padding-top": 3, "padding-bottom": 3},
                       ["column-direction-normal", "align-items-center"])
            c = statut_cadre(hc, nom_titre)
            if c is not None:
                statut_court(c)
                # v37 (le joueur, Large : « Dispo. transfert » sur 2 lignes, plus haut que « Dispo. prêt ») : titre sur
                # une ligne, un cran plus petit (body-xs), « … » + texte complet au survol s'il ne tient pas
                for r in t.walk(c):
                    if t.name(r) == nom_titre and typ(t, r).endswith("SIText"):
                        t.elem(r)["m_Classes"] = ["body-xs" if k == "body-sm" else k
                                                  for k in t.elem(r).get("m_Classes") or []]
                        t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis",
                                              "max-width": {"unit": 2, "value": 100.0}, "overflow": "hidden"})
                        for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                            t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1
        nv = boite(t, col, {**habille({"flex-grow": 1.15, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                       "overflow": "hidden", "margin-top": e // 2}),
                            "padding-top": 2, "padding-bottom": 2},
                   ["column-direction-normal", "justify-content-center", "align-items-center"])
        scout_lie(t, src, p, nv, rm_model)
    else:
        # statut de transfert / prêt l'un sous l'autre, puis niveau à côté (Medium / Small)
        # v4 (le joueur) : colonne étroite, Statut de transfert / Statut de prêt (cadres de la tuile 2x2 de FM, titres
        # traduits par FM compris) ; Éligibilité retirée
        sep()
        col = part(carte, POIDS["statut"], ["column-direction-normal", "align-self-stretch"])
        for i, nom_titre in enumerate(STATUT_CADRES):
            statut_cadre(moitie(col, i == 0), nom_titre)
        # niveau actuel / potentiel (bloc de FM)
        sep()
        nv = part(carte, POIDS["niveau"], ["column-direction-normal", "justify-content-center", "align-items-center"],
                  habille({}))
        scout_lie(t, src, p, nv, rm_model)
    msgs += zone_droite(t, carte, dims, poly_src, rm_model, s_vis, vis, txt, habille, sep)
    return msgs


def zone_droite(t, carte, dims, poly_src, rm_model, s_vis, vis, txt, habille, sep):
    """carte de droite (polygone / Pour / Contre / Progression en Small, selon les options) ; messages"""
    import notes_installations as ni
    e = dims["ecart"]
    msgs = []
    # polygone : v24 tout à droite, dans sa carte, dans tous les modes (Small compris)
    if dims["poly"] and poly_src:
        w, hh = dims["poly"]
        # v5 (le joueur : polygone « en très grand une demi-seconde » à l'ouverture) : rien de lié ne tient pendant
        # le chargement d'une fiche (fonctions.md, cale de la fiche 2026-11-12) -> zone de largeur fixe et cale
        # w × hh SANS liaison, qui coupe ce qui dépasse, autour du polygone
        large = w + e + 2 * POLYGONE_MARGE
        zcss = {"width": large, "min-width": large, "max-width": large, "flex-grow": 0, "flex-shrink": 0,
                "align-self": "stretch", "overflow": "hidden"}
        bv = s_vis.sd(vis)["Binding"]
        # v28 (le joueur : « la progression fallait la mettre que sur la vue en petite ») : Progression en Small
        # (mode > 1), polygone en Large / Medium (mode < 2)
        if PROGRESSION:
            zp = ni.new_visible(t, s_vis, vis, carte, None, "", ni.make_binding(bv, 4, [MODE], 1),
                                ["row-direction-normal"])
            t.styles.style(t, zp, dict(zcss))
            sep(zp)
            # gom36 (le joueur, Doué : réponse de l'agent plus haute -> en-tête plus haut, fiche décalée, vide en bas) :
            # avec gomez, contenu des cartes de droite du Small en absolu (comme la tuile club) : il ne peut plus
            # agrandir l'en-tête (180 px pile, comme tes joueurs)
            hors_flux_c = ({"position": "absolute", "left": e, "right": 0, "top": 0, "bottom": 0}
                           if AGENT_HORS_CLUB else {})
            cpp = boite(t, zp, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                        "overflow": "hidden", **hors_flux_c}),
                        ["column-direction-normal", "align-items-stretch", "justify-content-center"])
            # gom32 (le joueur : joueur hors club = Progression / Efficacité vides) : joueur de ton club = Progression
            # (et Efficacité) ; sinon Agent (nom + bouton « Demander à l'agent ») et Attentes (valeur / salaire du
            # rapport, demandes de l'agent une fois contacté)
            if AGENT_HORS_CLUB:
                cpp_club = si_club(t, s_vis, vis, bv, cpp, True)
                for i_h, h_ in enumerate(si_hors(t, s_vis, vis, bv, cpp)):
                    agent_hors_club(t, h_, rm_model, txt, msgs if i_h == 0 else [])
            else:
                cpp_club = cpp
            m = tuile_fm(t, cpp_club, rm_model, MODELE_PROGRESSION,
                         {"person": ("person", JOUEUR), "team": ("person.Team", EQUIPE)})
            if m:
                msgs.append(m)
            else:
                m = habiller_progression(t, cpp_club, txt)
                if m:
                    msgs.append(m)
            if EFFICACITE_SMALL:
                # gom30 (le joueur, Small : « réduis la carte joueur, à droite de Progression une tuile Efficacité
                # tactique, plus de contenu ») : tuile de FM (team -> person.Team, player -> person : section joueur
                # avec / sans ballon) ; la carte joueur (flex) rétrécit d'autant
                ze = ni.new_visible(t, s_vis, vis, carte, None, "", ni.make_binding(bv, 4, [MODE], 1),
                                    ["row-direction-normal"])
                le = EFFICACITE_LARGEUR + e
                t.styles.style(t, ze, {**zcss, "width": le, "min-width": le, "max-width": le})
                sep(ze)
                cpe = boite(t, ze, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                            "overflow": "hidden", **hors_flux_c}),
                            ["column-direction-normal", "align-items-stretch", "justify-content-flex-start"])
                if AGENT_HORS_CLUB:
                    for i_h, h_ in enumerate(si_hors(t, s_vis, vis, bv, cpe)):
                        attentes_hors_club(t, h_, rm_model, txt, msgs if i_h == 0 else [], (s_vis, vis, bv))
                    cpe = si_club(t, s_vis, vis, bv, cpe, True)
                ts_, tr_ = txt
                if tr_ is not None:
                    titre(t, ts_, tr_, cpe, "Efficacité tactique", "Tactical Effectiveness")
                # gom31 (le joueur : « arrange-la mieux, remplis, trouve du contenu ») : 2 colonnes = tuile 2x2
                # (tactique, jauge globale, poste joué) | lignes du tableau de FM (compréhension tactique, capacité du
                # joueur, adhésion, match) sans en-tête, lignes compactes
                rang = boite(t, cpe, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "align-self": "stretch",
                                      "overflow": "hidden"}, ["row-direction-normal", "align-items-center"])
                # gom64 (le joueur : « que ça tienne dans le même rectangle que les infos à droite, bien aligné ») :
                # colonne gauche haute pile comme les 4 lignes du tableau, centrée comme lui ; dedans, 1er élément en
                # haut, dernier en bas (space-between)
                hg = len(EFFICACITE_LIGNES) * EFFICACITE_HAUT_LIGNE
                ge = boite(t, rang, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                     "overflow": "hidden", "margin-right": 10, "height": hg, "min-height": hg,
                                     "max-height": hg}, ["column-direction-normal"])
                de = boite(t, rang, {"flex-grow": EFFICACITE_PART_TABLEAU, "flex-shrink": 1, "flex-basis": 0,
                                     "min-width": 0, "overflow": "hidden", "justify-content": "center"},
                           ["column-direction-normal"])
                m = tuile_fm(t, ge, rm_model, MODELE_EFFICACITE,
                             {"team": ("person.Team", EQUIPE), "player": ("person", JOUEUR)}, tous=True)
                if m:
                    msgs.append(m)
                else:
                    # gom38 (le joueur : « le côté gauche, fais-le respirer ») : tactique / jauge / poste joué
                    # répartis sur la hauteur (colonne de la 2x2 de FM en space-around), plus d'écart avec le tableau
                    # gom40 (gom38 sans effet : les conteneurs au-dessus gardaient la hauteur du contenu) : toute la
                    # chaîne jusqu'à ge étirée en hauteur ; la section joueur ne s'étire plus (elle prenait le reste)
                    for r in list(t.walk(ge)):
                        cls = t.elem(r).get("m_Classes") or []
                        if "padding-right-global-padding-none" in cls and "flex-grow-class" in cls:
                            t.styles.style(t, r, {"justify-content": "space-between", "flex-grow": 1,
                                                  "min-height": 0, "padding-top": 0, "padding-bottom": 0})
                            p_ = t.parent.get(r)
                            while p_ is not None and p_ != ge:
                                t.styles.style(t, p_, {"flex-grow": 1, "min-height": 0, "align-self": "stretch"})
                                p_ = t.parent.get(p_)
                        if t.name(r) == "player-section":
                            t.styles.style(t, r, {"flex-grow": 0})
                    t.styles.style(t, ge, {"margin-right": EFFICACITE_ECART})
                # gom34 (le joueur : lignes vides, « pas link au joueur ») : efficacité DU JOUEUR, comme les cellules
                # de l'écran Tactiques (TacticsTEGaugeWrapperCell : team.TacticalEffectivenessForPlayer, joueur lu
                # dans le contexte) : player / person posés dans un remapper au-dessus
                ctx = remapper(t, rm_model, de, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
                m = tuile_fm(t, ctx, rm_model, MODELE_EFFICACITE_TABLEAU,
                             {"effectiveness": ("person.Team.TacticalEffectivenessForPlayer", TYPE_EFFICACITE),
                              "tactic": ("person.Team.Tactic", TYPE_TACTIQUE), "showheader": ("const.false", 0),
                              "player": ("person", JOUEUR)})
                if m:
                    msgs.append(m)
                else:
                    h = EFFICACITE_HAUT_LIGNE
                    for r in t.walk(de):
                        if t.name(r) in EFFICACITE_LIGNES:
                            t.styles.style(t, r, {"height": h, "min-height": h, "max-height": h})
                    for r in [r for r in t.walk(de) if t.name(r) == "header" or (
                            t.elem(r).get("m_TemplateAlias") or "") == "layout-divider-solid-horizontal"]:
                        t.remove(r)
            # options fiche_medium_colonne / fiche_large_tuile : Pour / Contre, polygone ou rien selon le mode
            def selon(quoi):
                modes = [m for m in (0, 1) if DROITE[m] == quoi]
                if not modes:
                    return None
                b = ni.make_binding(bv, 0, [MODE], 2) if len(modes) == 2 else ni.equal_binding(bv, MODE, modes[0])
                return ni.new_visible(t, s_vis, vis, carte, None, "", b, ["row-direction-normal"])
            # gom12 (le joueur, Large : tuile club écrasée) : avec gomez, une carte Pour / Contre PAR affichage, plus
            # large (GOMEZ_PC_PLUS) en Medium seulement
            modes_pc = [m for m in (0, 1) if DROITE[m] == "pc"]
            groupes = [[m] for m in modes_pc] if STYLE_GOMEZ else ([modes_pc] if modes_pc else [])
            for g in groupes:
                bpc = ni.make_binding(bv, 0, [MODE], 2) if len(g) == 2 else ni.equal_binding(bv, MODE, g[0])
                zpc = ni.new_visible(t, s_vis, vis, carte, None, "", bpc, ["row-direction-normal"])
                zc_pc = dict(zcss)
                if STYLE_GOMEZ and g in ([1], [0]):
                    lp = zc_pc["width"] + (GOMEZ_PC_PLUS if g == [1] else GOMEZ_PC_PLUS_LARGE)
                    zc_pc.update({"width": lp, "min-width": lp, "max-width": lp})
                t.styles.style(t, zpc, zc_pc)
                sep(zpc)
                msgs += carte_pour_contre(t, zpc, habille,
                                          PC_ECHELLE_MEDIUM if STYLE_GOMEZ and g == [1] else 1.0)
            if DROITE != {0: "poly", 1: "poly"}:
                zone = selon("poly")
                if zone is None:
                    return msgs
            else:
                zone = ni.new_visible(t, s_vis, vis, carte, None, "", ni.make_binding(bv, 0, [MODE], 2),
                                      ["row-direction-normal"])
            t.styles.style(t, zone, zcss)
        else:
            zone = boite(t, carte, zcss, ["row-direction-normal"])
        sep(zone)
        cp = boite(t, zone, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                     "overflow": "hidden"}, padding=False),
                   ["column-direction-normal", "align-items-center", "justify-content-center"])
        # ESSAI ENTETE_PLUS : cale du polygone (plus haute que la tuile Large) hors du calcul de hauteur (absolue,
        # centrée : top 50 % - moitié de sa hauteur), sinon la tuile Large grandirait jusqu'à elle
        hors_flux = {"position": "absolute", "left": POLYGONE_MARGE, "top": {"unit": 2, "value": 50.0},
                     "margin-top": -(hh // 2)} if ENTETE_PLUS else {}
        pb = boite(t, cp, {"width": w, "min-width": w, "max-width": w, "height": hh, "min-height": hh,
                           "max-height": hh, "flex-grow": 0, "flex-shrink": 0, "overflow": "hidden",
                           "align-self": "center", **hors_flux},
                   ["column-direction-normal", "align-items-center", "justify-content-center"])
        # v11 (le joueur : flash encore, Large et Medium) : graphique dans un SIVisible lié aux données du joueur
        # (person.Age > 0) : caché tant que la fiche n'est pas chargée (un conteneur lié reste caché tant que sa
        # liaison n'est pas lue), il n'apparaît qu'avec les vraies notes
        # v22 : graphique plus grand que la cale (gw × gh), centré dans la cale qui coupe ; rayon en px
        if "rayon_px" in dims:
            gw, gh = round(w * INTERIEUR), round(hh * INTERIEUR)
            rayon = round(dims["rayon_px"] * 100.0 / min(gw, gh), 2)
        else:
            gw, gh, rayon = w, hh, dims.get("rayon", POLYGONE_RAYON)
        fixe = lambda a, b: {"width": a, "min-width": a, "max-width": a, "height": b, "min-height": b,
                             "max-height": b, "flex-grow": 0, "flex-shrink": 0}
        attente = ni.new_visible(t, s_vis, vis, pb, None, "", ni.make_binding(s_vis.sd(vis)["Binding"], 4,
                                                                             ["person.Age"], 0))
        t.styles.style(t, attente, fixe(gw, gh))
        rm = remapper(t, rm_model, attente, {"player": ("person", JOUEUR)})
        t.styles.style(t, rm, fixe(gw, gh))
        ps, pr = poly_src
        import fiche_fmguru as guru
        poly = t.clone(pr, rm, src=ps)
        t.styles.copy_from(ps.styles, t, poly)
        copy_usings(t, ps, pr)
        sd = t.sd(poly)
        sd["SpiderChartRadiusPercentage"] = rayon
        sd["NumberOfInnerRings"] = guru.ANNEAUX_POLYGONE
        sd["LabelsTemplate"]["m_AssetGUID"] = guru.GUID_ETIQUETTES
        t.elem(poly)["m_Classes"] = [x for x in t.elem(poly)["m_Classes"]
                                     if x not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
        t.styles.style(t, poly, fixe(gw, gh))
    return msgs


def aiguillage_mode(t, src, p, parent, css=None, enfant_css=None, classes=()):
    """gom18 (le joueur : « pourquoi ça bouge dans tous les sens ») : les versions par affichage en SIVisible sont TOUTES
    montrées le temps que la fiche charge (doubles photos / noms / cales : l'en-tête sautait) -> aiguillage de FM
    (BindableSwitchElement, copie de celui du contrat, sans ses enfants) sur settings.AdaptiveScalingLevelIndex :
    enfants Large / Medium / Small, FM ne construit que celui de l'affichage (enfant choisi par position ; si FM lit le
    mode comme un booléen, Small prend l'enfant Medium : sans gravité). Renvoie les 3 conteneurs"""
    sw = t.clone(p["contrat"], parent, src=src.s)
    for k in list(t.children(sw)):
        t.remove(k)
    sd = t.sd(sw)
    sd["name"] = ""
    b = copy.deepcopy(sd["Binding"])
    b["m_kind"] = 1
    b["m_direct"]["Path"]["m_path"] = MODE
    sd["Binding"] = b
    if "AlwaysInstantiate" in sd:
        sd["AlwaysInstantiate"] = 0
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
    if css:
        t.styles.style(t, sw, dict(css))
    return [boite(t, sw, dict(enfant_css or {}), list(classes)) for _ in range(3)]


def regle_lignes(t, racine):
    """gom19 (le joueur : « des lignes bouffées, sélections, les pays, aligne avec l'autre côté ») : les cellules de FM
    (nation-cell / text-cell-button : .cell-medium = hauteur fixe, align-self-start) étaient calées en haut d'un cadre
    plus haut que la rangée -> texte plus bas que celui d'en face et coupé en bas. Règle
    « .CL_LIGNE .cell-medium / .cell-button » (spécificité 20 > 10 de FM) : hauteur auto, centrée, sans marges"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(racine).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    sh = t.styles.sh
    if any(p.get("m_Value") == CL_LIGNE for r in sh["m_Rules"] for cs in r.get("m_ComplexSelectors") or []
           for s in cs["m_Selectors"] for p in s["m_Parts"]):
        return
    zero = [(PROPRIETES[k][0], "", [(3, 0)]) for k in ("margin-top", "margin-bottom", "padding-top", "padding-bottom",
                                                      "min-height")]
    idx = t.styles.add_rule([(PROPRIETES["height"][0], "", [(1, 2)]),   # height: auto (mot-clé 2)
                             (PROPRIETES["align-self"][0], "", [(7, "center")])] + zero)
    sh["m_Rules"][idx]["m_ComplexSelectors"] = [
        {"m_Specificity": 20, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": CL_LIGNE, "m_Type": 3}], "m_PreviousRelationship": 0},
            {"m_Parts": [{"m_Value": c, "m_Type": 3}], "m_PreviousRelationship": 2}]}   # 2 = descendant
        for c in CELLULES_FM]


def tuiles_gomez(t, carte, dims, src, p, txt, photo, haut_src, rm_model, s_vis, vis, habille, sep, part,
                 degrade=None):
    """entete_style gomez : tuile identité | tuile club (la carte de droite est ajoutée ensuite) ; messages"""
    import notes_installations as ni
    msgs = []
    e = dims["ecart"]
    b = s_vis.sd(vis)["Binding"]
    modes = ((True, ni.equal_binding(b, MODE, 0)), (False, ni.make_binding(b, 4, [MODE], 0)))
    ts, tr = txt

    def ligne(dans, bas=0, haut=GOMEZ_HAUT_LIGNE_MS):   # gom60 : Medium / Small ; le Large passe sa hauteur (lg)
        # gom10 (le joueur : « trop d'espace un peu n'importe comment ») : toutes les lignes à la même hauteur
        return boite(t, dans, {"flex-shrink": 0, "margin-bottom": bas, "min-width": 0, "overflow": "hidden",
                               "height": haut, "min-height": haut, "max-height": haut},
                     ["row-direction-normal", "align-items-center", CL_LIGNE])

    def sans_marges(c):
        """gom17 (le joueur : « aligne bien », écarts inégaux) : marges haut / bas de FM retirées d'une copie (elles
        décalaient le texte dans des lignes de même hauteur)"""
        for r in t.walk(c):
            el = t.elem(r)
            if el.get("m_Classes"):
                el["m_Classes"] = [k for k in el["m_Classes"]
                                   if not k.startswith(("margin-bottom", "margin-top", "padding-top", "padding-bottom",
                                                        "margin-vertical", "padding-vertical"))]
        t.styles.style(t, c, {"margin-top": 0, "margin-bottom": 0})
        return c

    def pousse(dans):   # vide qui pousse la suite à droite
        boite(t, dans, {"flex-grow": 1, "flex-shrink": 1, "min-width": 4})

    def libelle(dans, fr):
        c = titre(t, ts, tr, dans, fr, fr)   # essai pas validé : FR seul
        t.elem(c)["m_Classes"] = [k for k in t.elem(c)["m_Classes"] if k != "margin-bottom-global-gap-small"]
        t.styles.style(t, c, {"flex-shrink": 0, "margin-right": 8})

    # ---- tuile identité : n° | photo | lignes
    t1 = part(carte, GOMEZ_POIDS[0], ["row-direction-normal", "align-self-stretch", "align-items-center"],
              habille({}))
    regle_lignes(t, t1)
    nom_txt = first(src.s, lambda r: r in set(src.s.walk(p["nom"]))
                    and "person.Name" in str(src.s.sd(r).get("TextBinding") or ""))
    # gom15 (le joueur, maquette L1 pour le Large) : grand maillot à côté de la photo en Medium / Small seulement ; en
    # Large, petit maillot dans le coin bas-gauche de la photo (posé avec la photo, plus bas)
    if nom_txt is not None:   # gom18 : aiguillage (Large vide)
        vm = aiguillage_mode(t, src, p, t1, {"flex-shrink": 0, "align-self": "center"}, {"flex-shrink": 0},
                             ["row-direction-normal"])
        for zm in vm[1:]:
            m = maillot_numero(t, src, nom_txt, zm, dims["maillot"], degrade, e)
        msgs += m
    # gom13 (le joueur : « toujours le souci en Large ») : la photo de FM (~165 px de haut en Large) + marges de la tuile
    # dépassait la tuile Large (172) -> en-tête plus haut, fiche poussée hors écran ; photo dans un cadre de hauteur
    # fixe qui tient dans la tuile (haut sans ENTETE_PLUS - marges), coupé en bas (le buste)
    # gom14 (le joueur : « tu as bouffé les photos sur toutes les en-têtes, sépare grand et les 2 autres ») : cadre
    # fixe en Large seulement (mode 0) ; Medium / Small (mode > 0) : photo à sa taille, comme avant
    cv_ = CELLULE[0] + 2
    ph_h = dims["haut"] - 2 * MARGE[0] - 1 - 2 * cv_
    vp = aiguillage_mode(t, src, p, t1, {"flex-shrink": 0, "align-self": "center", "margin-right": e},
                         {"flex-shrink": 0}, ["column-direction-normal", "align-items-center"])
    for i, zv in enumerate(vp):
        large = i == 0
        css = {"flex-shrink": 0}
        if large:   # cadre DANS le SIVisible (styles sur un SIVisible parfois ignorés, technique.md)
            css.update({"height": ph_h, "min-height": ph_h, "max-height": ph_h, "overflow": "hidden"})
        zb = boite(t, zv, css, ["column-direction-normal", "align-items-center"])
        ph = t.clone(photo, zb)
        t.sd(ph)["name"] = ""
        t.elem(ph)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
        t.styles.style(t, ph, {"flex-shrink": 0})
        if large:
            # gom17 (le joueur : « en grand l'image toujours complètement bouffée ») : photo de FM (taille par sa classe
            # thumbnails-alt-person-picture-player-report) réduite à la hauteur du cadre, proportions gardées
            pw = round(ph_h * PHOTO_RAPPORT)
            for r in t.walk(ph):
                if t.elem(r).get("m_TemplateAlias") == "PersonPicture":
                    t.styles.style(t, r, {"width": pw, "min-width": pw, "max-width": pw, "height": ph_h,
                                          "min-height": ph_h, "max-height": ph_h})
        # gom16 (le joueur, gom15 vu : « enlève le maillot en Large ») : plus de petit maillot sur la photo ; le n°
        # revient à droite du nom en Large (ligne du nom, plus bas)
    # gom25 (le joueur, gom24 vu en Large : « ça n'a pas bougé », modèle = 2 colonnes serrées centrées chacune) :
    # aiguillage : Large = 2 colonnes indépendantes (gomez_large) ; Medium / Small = les lignes validées
    vcol = aiguillage_mode(t, src, p, t1, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                           "align-self": "stretch", "flex-direction": "column"},
                           {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "overflow": "hidden",
                            "justify-content": "space-evenly"}, ["column-direction-normal"])
    # gom63 (le joueur, gom62 vu : « un peu trop d'espace en bas ») : place libre réelle répartie à parts égales
    # (haut, entre les lignes, bas) au lieu d'écarts calculés ; les lignes alignées (gom62) ne débordent plus
    # gom61 (le joueur : « remonte un peu le texte pour pas que ça bouffe ») : lignes collées en haut (avant : centrées)
    # et écarts plus petits (libre / 6) -> la dernière ligne garde de la place en bas
    col = vcol[1]
    lignes_h = 2 * GOMEZ_HAUT_NOM_MS + 3 * GOMEZ_HAUT_LIGNE_MS   # gom60 : lignes du Medium / Small

    def espace():   # gom22 : écart entre 2 lignes, par affichage
        ve = aiguillage_mode(t, src, p, col, {"flex-shrink": 0}, {"flex-shrink": 0})
        for m, z in enumerate(ve):
            if m == 0:
                g = GOMEZ_ECART_LARGE
            else:
                libre = dims["haut"] + ENTETE_PLUS_MODE.get(m, 0) - 2 * MARGE[0] - 1 - 2 * cv_ - lignes_h
                g = GOMEZ_ECART_LARGE   # gom63 : le reste en space-evenly (avant : max(2, libre // 6))
            t.styles.style(t, z, {"height": g, "min-height": g, "max-height": g})

    # nom + statut | Actions
    r1 = ligne(col, 0, GOMEZ_HAUT_NOM_MS)   # gom13 : marges 0 partout (space-around répartit pareil entre les lignes)
    # gom16 : nom par affichage : Large = avec le petit n° de FM à droite (pas de maillot) ; Medium / Small = sans
    # (n° sur le maillot)
    vn = aiguillage_mode(t, src, p, r1, {"flex-shrink": 1, "min-width": 0}, {"flex-shrink": 1, "min-width": 0},
                         ["row-direction-normal", "align-items-center"])
    for i, zn in enumerate(vn):
        large = i == 0
        c = sans_marges(src.clone(t, p["nom"], zn))
        t.styles.style(t, c, {"flex-shrink": 1, "min-width": 0})
        if not large:
            for r in [r for r in t.walk(c) if t.elem(r).get("m_TemplateAlias") == NUMERO_BADGE]:
                if r in t.refs:
                    t.remove(r)
        for r in t.walk(c):
            if "person.Name" in str(t.sd(r).get("TextBinding") or ""):
                t.styles.style(t, r, {"font-size": dims["numero"]["nom"]})
    f = src.clone(t, p["flags"], r1)
    t.elem(f)["m_Classes"] = ["margin-left-global-gap-regular"]
    # gom57 (le joueur : « le statut joueur pas bien aligné au nom », badge Int / Vac / Obs plus haut) : drapeaux de
    # FM centrés dans la ligne du nom, sans leurs marges haut / bas
    sans_marges(f)
    t.styles.style(t, f, {"align-self": "center", "justify-content": "center"})
    pousse(r1)
    a = src.clone(t, p["actions"], r1)
    t.sd(a)["name"] = ""
    t.styles.style(t, a, {"flex-shrink": 0})
    # gom3 (le joueur : « trop d'espace, mal rangé ») : sous le nom, 2 colonnes : gauche = poste · taille / nation(s) /
    # sélections ; droite (calée à droite) = âge / salaire + fin / valeur
    # gom7 (le joueur : « giga chelou, mal aligné », taille « poussée par le poste ») : vraies lignes gauche | droite
    # (poste | âge, nation | salaire, sélections | valeur, médias) ; taille retirée (dans Infos, fiche_joueur_plus)
    # gom58 (le joueur, Medium / Small : « nom, poste, âge, dessous pays et sélections ; à droite sous Actions la
    # description médias à la place de l'âge ») : poste | médias, âge | temps de jeu, nation | salaire, sélections |
    # valeur (Large inchangé : ses 2 colonnes plus bas)
    espace()
    r2 = ligne(col)
    c = sans_marges(src.clone(t, p["poste"], r2))
    t.styles.style(t, c, {"flex-shrink": 1, "min-width": 0, "margin-right": 8, "align-self": "center"})
    pousse(r2)
    mds = []
    if nom_txt is not None:   # médias, à droite (aiguillage : Large vide)
        vmd = aiguillage_mode(t, src, p, r2, {"flex-shrink": 1, "min-width": 0}, {"flex-shrink": 1, "min-width": 0},
                              ["row-direction-normal", "align-items-center", "justify-content-flex-end"])
        for zmd in vmd[1:]:
            md = src.clone(t, nom_txt, zmd)
            sd = t.sd(md)
            sd["name"], sd["DebugDisplay"] = "", "Buteur polyvalent"
            sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = MEDIAS_CHEMIN
            for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                sd[k], sd[k + "_UxmlAttributeFlags"] = 1, 1
            t.elem(md)["m_Classes"] = ["body-sm", "global-text-secondary", "content-ellipsis"]
            t.styles.style(t, md, {"white-space": "nowrap", "text-overflow": "ellipsis", "overflow": "hidden",
                                   "flex-shrink": 1, "min-width": 0, "margin-top": 0, "margin-bottom": 0,
                                   "margin-right": 0, "-unity-text-align": "middle-right"})
            mds.append(md)
    espace()
    r2b = ligne(col)
    c = sans_marges(src.clone(t, p["age"], r2b))
    t.styles.style(t, c, {"flex-shrink": 0, "margin-right": 8})
    pousse(r2b)
    tj = sans_marges(contrat_part(t, src, p, r2b, 1))   # temps de jeu, en face de l'âge
    # gom59 (le joueur : « même police que Important Player sur la description médias ») : classes de texte du temps
    # de jeu de FM recopiées sur les médias (taille / graisse / couleur), sans ses classes de mise en page
    tx = tj is not None and first(t, lambda r: r in set(t.walk(tj)) and typ(t, r).endswith("SIText"))
    if tx:
        mise_en_page = ("margin", "padding", "flex", "align", "justify", "row-", "column-", "width", "height")
        police = [k for k in t.elem(tx).get("m_Classes") or [] if not k.startswith(mise_en_page)]
        for md in mds:
            t.elem(md)["m_Classes"] = police + ["content-ellipsis"]
    # nation(s) + sélections (Large : 3 lettres, une ligne de sélections ; Medium / Small : noms complets)
    court = None
    for r in src.s.walk():
        if src.s.name(r) == "UIPickerNationsCourtesLarge-v1" and src.s.children(r):
            court = src.s.children(r)[0]
            break
    if court is None:
        court = p.get("nat3")
    # gom10 (le joueur : « le temps de jeu sous l'âge ») : nation(s) | temps de jeu, sélections | salaire, médias |
    # valeur
    espace()
    r3 = ligne(col)
    espace()
    r3b = ligne(col, 0, GOMEZ_HAUT_NOM_MS)   # gom58 : sélections | valeur (ligne de la valeur haute, gom16)
    t.styles.style(t, r3b, {"overflow": "visible"})
    # gom61 (le joueur, Medium / Small : nation ~4 px et sélections ~7 px plus bas que le salaire / la valeur en face,
    # « fais comme à droite pour pas que ça bouge partout ») : plus d'aiguillage par affichage (ces lignes ne sont
    # montrées qu'en Medium / Small, le Large a ses colonnes, plus bas) : copies posées directement dans la ligne,
    # sans marges haut / bas, comme le salaire et la valeur
    t.styles.style(t, r3, {"overflow": "visible"})   # gom23 : drapeaux jamais coupés
    n = src.clone(t, p["nat"], r3)
    t.sd(n)["name"] = ""
    sans_marges(n)
    t.styles.style(t, n, {"flex-shrink": 0, "margin-left": PAYS_DECALAGE[False], "padding-left": 0,
                          "align-self": "center"})
    # gom13 (le joueur : « les pays sont mal alignés ») : marges à gauche de FM retirées (décalage sous le poste)
    for r in t.walk(n):
        el = t.elem(r)
        if el.get("m_Classes"):
            el["m_Classes"] = [("align-items-center" if k == "align-items-start" else k) for k in el["m_Classes"]
                               if not k.startswith(("margin-left", "padding-left", "padding-horizontal",
                                                    "margin-horizontal"))]   # gom19 : centré dans la rangée
    pousse(r3)
    k = sans_marges(src.clone(t, p["caps"], r3b))
    t.elem(k)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, k, {"flex-shrink": 1, "min-width": 0, "align-self": "center"})
    for i, x in enumerate(c for c in t.children(k)
                          if (t.elem(c).get("m_TemplateAlias") or "") == "text-cell-button-medium"):
        t.elem(x)["m_Classes"] = ["margin-left-global-gap-regular"] if i else []
    pousse(r3b)
    # gom4 (le joueur : « sous les sélections, la description des médias ») : texte de FM (Person.MediaDescription,
    # comme PersonPersonalBlock), copie du texte du nom reliée à ce chemin
    sans_marges(contrat_part(t, src, p, r3, 0))    # gom58 : salaire + fin, en face de la nation
    # gom16 (le joueur : « le prix bouffé en haut ») : ligne de la valeur plus haute (28), rien coupé
    c = sans_marges(src.clone(t, p["valeur"], r3b))   # gom58 : valeur, en face des sélections
    t.styles.style(t, c, {"flex-shrink": 0})
    for k in t.children(col):   # gom25 : Small = mêmes lignes que Medium
        t.clone(k, vcol[2])
    # gom25 : Large = 2 colonnes, chacune centrée en hauteur, lignes serrées
    L = boite(t, vcol[0], {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch"},
              ["row-direction-normal"])
    gauche = boite(t, L, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden",
                          "justify-content": "center", "padding-left": 6}, ["column-direction-normal"])
    droite = boite(t, L, {"flex-shrink": 0, "justify-content": "center", "align-items": "flex-end",
                          "margin-left": 12}, ["column-direction-normal"])

    def lg(dans, h=GOMEZ_HAUT_LIGNE, dernier=False, a_droite=False):
        r = ligne(dans, 0 if dernier else GOMEZ_ECART_LARGE_2C, h)
        t.styles.style(t, r, {"overflow": "visible"})
        if a_droite:
            t.styles.style(t, r, {"justify-content": "flex-end"})
        return r

    r = lg(gauche, GOMEZ_HAUT_NOM)
    c = sans_marges(src.clone(t, p["nom"], r))
    t.styles.style(t, c, {"flex-shrink": 1, "min-width": 0})
    for x in t.walk(c):
        if "person.Name" in str(t.sd(x).get("TextBinding") or ""):
            t.styles.style(t, x, {"font-size": dims["numero"]["nom"]})
    f = src.clone(t, p["flags"], r)
    t.elem(f)["m_Classes"] = ["margin-left-global-gap-regular"]
    sans_marges(f)   # gom57 : badge de statut centré sur le nom (Large aussi)
    t.styles.style(t, f, {"align-self": "center", "justify-content": "center"})
    r = lg(gauche)
    c = sans_marges(src.clone(t, p["poste"], r))
    t.styles.style(t, c, {"flex-shrink": 1, "min-width": 0, "align-self": "center"})
    # gom60 (le joueur, Large : « prénom, poste, âge, puis pays et après le pays les sélections sur la même ligne,
    # comme ça ça fit à tout le skin ») : âge à gauche sous le poste ; pays + sélections sur une ligne ; à droite,
    # médias à la place de l'âge (comme Medium / Small)
    r = lg(gauche)
    t.styles.style(t, sans_marges(src.clone(t, p["age"], r)), {"flex-shrink": 0})
    r = lg(gauche, dernier=True)
    n = src.clone(t, court if court is not None else p["nat"], r)
    t.sd(n)["name"] = ""
    sans_marges(n)
    t.styles.style(t, n, {"flex-shrink": 0, "margin-left": PAYS_DECALAGE[True], "padding-left": 0})
    for x in t.walk(n):
        el = t.elem(x)
        if el.get("m_Classes"):
            el["m_Classes"] = [("align-items-center" if k == "align-items-start" else k) for k in el["m_Classes"]
                               if not k.startswith(("margin-left", "padding-left", "padding-horizontal",
                                                    "margin-horizontal"))]
    k = sans_marges(src.clone(t, p["caps"], r))   # gom60 : sélections juste après le pays, même ligne
    t.elem(k)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, k, {"flex-shrink": 1, "min-width": 0, "margin-left": 12, "overflow": "hidden"})
    cellules = [x for x in t.children(k) if (t.elem(x).get("m_TemplateAlias") or "") == "text-cell-button-medium"]
    if len(cellules) == 2:
        ni.selections_une_ligne(t, s_vis, vis, k, cellules, b, AGE_JEUNE)
    r = lg(droite, GOMEZ_HAUT_NOM, a_droite=True)
    a = src.clone(t, p["actions"], r)
    t.sd(a)["name"] = ""
    t.styles.style(t, a, {"flex-shrink": 0})
    r_md = lg(droite, a_droite=True)   # gom60 : médias à la place de l'âge
    tj = sans_marges(contrat_part(t, src, p, lg(droite, a_droite=True), 1))
    sans_marges(contrat_part(t, src, p, lg(droite, a_droite=True), 0))
    if nom_txt is not None:
        md = src.clone(t, nom_txt, r_md)
        sd = t.sd(md)
        sd["name"], sd["DebugDisplay"] = "", "Buteur polyvalent"
        sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = MEDIAS_CHEMIN
        for kk in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
            sd[kk], sd[kk + "_UxmlAttributeFlags"] = 1, 1
        tx = first(t, lambda x: x in set(t.walk(tj)) and typ(t, x).endswith("SIText"))
        mise_en_page = ("margin", "padding", "flex", "align", "justify", "row-", "column-", "width", "height")
        t.elem(md)["m_Classes"] = ([kk for kk in t.elem(tx).get("m_Classes") or [] if not kk.startswith(mise_en_page)]
                                   if tx else ["body-sm", "global-text-secondary"]) + ["content-ellipsis"]
        t.styles.style(t, md, {"white-space": "nowrap", "text-overflow": "ellipsis", "overflow": "hidden",
                               "flex-shrink": 1, "min-width": 0, "margin-top": 0, "margin-bottom": 0,
                               "margin-right": 0, "-unity-text-align": "middle-right", "max-width": 260})
    r = lg(droite, GOMEZ_HAUT_NOM, dernier=True, a_droite=True)
    t.styles.style(t, sans_marges(src.clone(t, p["valeur"], r)), {"flex-shrink": 0})
    # gom2 (le joueur, gom1 vu : tuile qui déborde en haut / en bas) : valeur | salaire + fin sur UNE ligne, sans
    # libellés ; le temps de jeu part dans la tuile club
    sep()
    # ---- tuile club : club | Dispo. transfert | Dispo. prêt | Niveau / Potentiel
    # gom3 (le joueur : « CATA le rangement ») : gauche = club puis lignes libellé (largeur fixe) | valeur ; droite =
    # Niveau / Potentiel
    # gom28 (le joueur, gom27 vu : Large, tuile club coupée « Non d... », « Ligue 1 McDonal... ») : en Large seulement,
    # la tuile a une base de GOMEZ_CLUB_LARGE px (cale dans l'aiguillage de FM, enfant Large) + sa part ; contenu posé
    # en absolu (il ne compte pas dans la base) : Medium / Small = base 0, comme avant
    coque = boite(t, carte, habille({"flex-grow": GOMEZ_POIDS[1], "flex-shrink": 1, "min-width": 0,
                                     "overflow": "hidden"}, padding=False), ["row-direction-normal",
                                                                            "align-self-stretch"])
    vcale = aiguillage_mode(t, src, p, coque, {"flex-shrink": 0, "min-width": 0}, {"min-width": 0})
    boite(t, vcale[0], {"width": GOMEZ_CLUB_LARGE, "min-width": GOMEZ_CLUB_LARGE, "height": 0, "flex-shrink": 0})
    marges_t2 = {k: v for k, v in habille({}).items() if k.startswith("padding")}
    t2 = boite(t, coque, {"position": "absolute", "left": 0, "right": 0, "top": 0, "bottom": 0, **marges_t2},
               ["row-direction-normal", "align-items-center"])
    # gom17 (le joueur : « en petit mets niveau et pot plus centré, trop d'espace ») : la colonne de gauche prend sa
    # largeur, Niveau / Potentiel centrés dans le reste
    # gom26 (le joueur, Large : tuile club « trop resserrée sur elle-même ») : club / Dispo. transfert / Dispo. prêt
    # répartis sur toute la hauteur (space-around, comme les lignes de l'identité) au lieu d'un bloc centré
    g2 = boite(t, t2, {"flex-grow": 0, "flex-shrink": 1, "min-width": 0, "overflow": "hidden", "align-self": "stretch",
                       "justify-content": "space-around"}, ["column-direction-normal"])
    bc = boite(t, g2, {"flex-shrink": 0, "min-width": 0, "overflow": "hidden", "margin-bottom": 0},
               ["column-direction-normal"])
    clubs = Src(CLUB)
    cr = clubs.s and clubs.s.children(clubs.s.tt["m_VisualTree"]["rid"])
    cr = cr and clubs.s.children(cr[0])
    if cr:
        vcl = aiguillage_mode(t, src, p, bc, {"flex-shrink": 0, "min-width": 0}, {"min-width": 0},
                              ["column-direction-normal"])
        for i, nl in enumerate(vcl):
            court_ = i == 0
            c = clubs.clone(t, cr[0], nl)
            if court_:
                for r in t.walk(c):
                    for prop in t.elem(r).get("m_Properties") or []:
                        if prop.get("name") == "mappings" and isinstance(prop.get("value"), str):
                            prop["value"] = prop["value"].replace("primarytext:team.Name:",
                                                                  "primarytext:club.ShortName:")
            m = club_retrecissable(t, nl)
            if m:
                msgs.append(m)
    else:
        src.clone(t, p["club"], bc)
    # temps de jeu (2e ligne du bloc contrat de FM)
    lib = {"width": GOMEZ_LIBELLE, "min-width": GOMEZ_LIBELLE, "max-width": GOMEZ_LIBELLE, "flex-shrink": 0,
           "white-space": "nowrap", "text-overflow": "ellipsis", "overflow": "hidden", "margin-bottom": 0}
    # gom10 : temps de jeu parti dans la tuile identité (sous l'âge)
    # Dispo. transfert / Dispo. prêt : cadre de FM en ligne (titre à la largeur des libellés, valeur à côté)
    st = Src(STATUT)
    for i, nom_titre in enumerate(STATUT_CADRES):
        titre_fm = st.s and first(st.s, lambda r: st.s.name(r) == nom_titre)
        if titre_fm is None:
            msgs.append(f"{STATUT} : {nom_titre} introuvable")
            continue
        rm = remapper(t, rm_model, g2, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
        t.styles.style(t, rm, {"flex-shrink": 0, "margin-bottom": GOMEZ_LIGNE if i == 0 else 0})
        c = st.clone(t, st.s.parent[titre_fm], rm)
        t.sd(c)["name"] = ""
        t.elem(c)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, c, {"margin-bottom": 0, "flex-direction": "row", "align-items": "center", "min-width": 0})
        for r in t.walk(c):
            if t.name(r) == nom_titre:
                t.styles.style(t, r, lib)
            elif typ(t, r).endswith("SIText") or t.name(r).endswith("-style-setter"):
                t.styles.style(t, r, {"white-space": "nowrap", "text-overflow": "ellipsis", "overflow": "hidden",
                                      "min-width": 0, "flex-shrink": 1})
            if typ(t, r).endswith("SIText"):
                for k in ("DisplayTooltipWhenElided", "displayTooltipWhenElided"):
                    t.sd(r)[k], t.sd(r)[k + "_UxmlAttributeFlags"] = 1, 1
    # gom29 (le joueur, Large : « Niveau / Potentiel trop vers le centre ») : en Large seulement, cale de
    # GOMEZ_NIVEAU_DECALE px avant eux (aiguillage, enfant Large) : leur zone centrée commence plus à droite
    vniv = aiguillage_mode(t, src, p, t2, {"flex-shrink": 0, "min-width": 0}, {"min-width": 0})
    boite(t, vniv[0], {"width": GOMEZ_NIVEAU_DECALE, "min-width": GOMEZ_NIVEAU_DECALE, "height": 0,
                       "flex-shrink": 0})
    nv = boite(t, t2, {"flex-shrink": 0, "flex-grow": 1, "margin-left": 12, "justify-content": "center"},
               ["column-direction-normal", "align-items-center"])
    scout_lie(t, src, p, nv, rm_model)
    return msgs   # la carte de droite pose son propre écart (zone_droite)


def contrat_part(t, src, p, dans, garder):
    """copie du bloc contrat de FM (aiguillage : 0 = « - » sans contrat, 1 = [salaire + fin, temps de jeu]) avec
    une seule des 2 lignes : garder 0 = salaire + fin, 1 = temps de jeu"""
    c = src.clone(t, p["contrat"], dans)
    for r in t.walk(c):
        el = t.elem(r)
        if el.get("m_Classes"):
            el["m_Classes"] = [k for k in el["m_Classes"] if k not in ("width-100-percent", "align-items-start",
                                                                      "content-left-align", "flex-grow-class")]
    t.styles.style(t, c, {"flex-shrink": 0})
    kids = t.children(c)
    lignes = t.children(kids[1]) if len(kids) == 2 else []
    if len(lignes) == 2:
        t.remove(lignes[1 - garder])
        t.elem(lignes[garder])["m_Classes"] = [k for k in t.elem(lignes[garder]).get("m_Classes") or []
                                               if k != "margin-bottom-global-gap-regular"]
    return c


def carte_pour_contre(t, parent, habille, echelle=1.0):
    """Medium (option fiche_medium_colonne = polygone) : carte à la place du polygone, comme l'infobulle du joueur
    (pastilles_pour_contre.contenu) : cadres POUR | CONTRE côte à côte, titres traduits de FM, pastilles de l'en-tête
    (ProConRow, couleur selon la note, texte au survol) ; rangées en trop cachées"""
    import pastilles_pour_contre as ppc
    from hierarchie_pyramide import path_arg
    lst = ppc.src_tree(ppc.LISTE_SOURCE)
    liste = lst and first(lst, lambda r: lst.name(r) == ppc.LISTE and typ(lst, r).endswith("WrappedObjectList"))
    ttr = ppc.src_tree(ppc.TITRES_SOURCE)
    titres = ttr and [first(ttr, lambda r, n=n: ttr.name(r) == n) for n, _ in ppc.LISTES]
    if liste is None or not titres or None in titres:
        return ["carte Pour / Contre (Medium) : liste ou titres de FM introuvables (le jeu a changé ?), ignorée"]
    # v5 (2026-11-15, le joueur : « un bouton Observer comme là où il y a tout l'espace ») : comme la colonne de la
    # fiche (fiche_joueur_plus) : rapport de l'adjoint OU rapport fait = pastilles, sinon phrase de FM + Observer joueur
    import fiche_joueur_plus as fjp
    from arbre import make_visible
    tour = boite(t, parent, habille({"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                                     "overflow": "hidden"}, padding=False),
                 ["column-direction-normal", "align-items-stretch"])
    cl = ["flex-grow-class", "align-self-stretch"]
    adj, autre = fjp.aiguillage_adjoint(t, parent, tour, cl, rapport=PC_RAPPORT)
    oui = make_visible(t, parent, autre, None, PC_RAPPORT + ".HasScoutedInfo", "", list(cl))
    t.elem(oui)["m_RuleIndex"] = -1
    msgs = fjp.sans_rapport(t, autre, parent, rapport=PC_RAPPORT)
    for cible in (adj, oui):
        pastilles_pour_contre(t, cible, liste, lst, titres, ttr, ppc, path_arg, echelle)
    return msgs + ["carte Pour / Contre en pastilles à la place du polygone, Observer sans rapport"]


def pastilles_pour_contre(t, parent, liste, lst, titres, ttr, ppc, path_arg, echelle=1.0):
    pas = ppc.PASTILLE_BANDEAU + 2   # pastille + marges 1 px
    cp = boite(t, parent, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-self": "stretch",
                           "overflow": "hidden", "padding-top": 6, "padding-bottom": 6, "padding-left": 6,
                           "padding-right": 6},
               ["row-direction-normal", "align-items-stretch"])
    for i, (titre_src, (_, chemin)) in enumerate(zip(titres, ppc.LISTES)):
        cadre = boite(t, cp, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden",
                              "background-color": PC_CADRE_FOND, "border-radius": ppc.CADRE_ARRONDI, "padding": 3,
                              # v3 (le joueur) : titres toujours en haut, à la même hauteur (pas selon le nombre)
                              "justify-content": "flex-start", "padding-top": 6, **({"margin-left": 6} if i else {})},
                      ["column-direction-normal", "align-items-center"])
        ti = t.clone(titre_src, cadre, src=ttr)
        no_styles(t, ti)
        t.sd(ti)["name"] = ""
        t.elem(ti)["m_Classes"] = ["body-sm-strong", "global-text-primary"]
        t.styles.style(t, ti, {"margin-bottom": 2, "flex-shrink": 0})
        # v4 (le joueur) : pastilles centrées en hauteur dans la place sous le titre (titre, lui, reste en haut)
        zone = boite(t, cadre, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0,
                                "overflow": "hidden", "align-self": "stretch", "justify-content": "center"},
                     ["column-direction-normal", "align-items-center"])
        w = t.clone(liste, zone, src=lst)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": PC_GUID_PASTILLE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], PC_RAPPORT + chemin[len("report"):])
        sd["ItemParamName"] = "procon"
        sd["ItemUssClassName"] = "flex-no-shrink-class"   # sinon les pastilles rétrécissent et se chevauchent
        t.elem(w)["m_Classes"] = []
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "justify-content": "center",
                              "align-self": "center",
                              "max-width": (PC_PAR_RANGEE_GROS if echelle != 1.0 else
                                            GOMEZ_PC_PAR_RANGEE if STYLE_GOMEZ else PC_PAR_RANGEE) * pas,
                              "min-height": pas, "max-height": PC_RANGEES * pas,
                              "overflow": "hidden", "flex-shrink": 0})
        if echelle != 1.0:   # pc4 : liste agrandie (scale USS de FM, id 327681 : x, y), centrée sur elle-même
            e = t.elem(w)
            vieux = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
            e["m_RuleIndex"] = t.styles.add_rule([v for v in vieux if v[0] != 327681]
                                                 + [(327681, "", [(2, float(echelle)), (2, float(echelle))])])


# ---------- étoiles Niveau / Potentiel sous la note du rapport (joueur hors club) ----------
# 2026-11-07 (le joueur, avant v1.66) : sur la fiche d'un joueur hors club, la carte Niveau / Potentiel ne montrait que
# la note A/B/C : dans PlayerReportHeaderScoutSection, l'aiguillage report.UseCoachReportLayout montre SOIT la note
# (#ScoutReport, recruteur) SOIT les étoiles (#AbilityStarRange, entraîneur = nos joueurs). Le bloc des étoiles de FM
# est recopié sous la note, dans la branche « rapport connu » (report.HasScoutedInfo) : rien avant supervision. Note +
# étoiles centrées. Vue « tuile » seulement (cartes de hauteur fixe : ça tient ; la bannière de FM n'est pas touchée)
MODELE_RAPPORT = "PlayerReportHeaderScoutSection"
PREFIXE_ETOILES = PREFIXE + "Etoiles"
NOM_ETOILES = f"{PREFIXE_ETOILES}-v6"   # v4 (2026-11-13, le joueur, capture Large : « Rapport de supervision » pas
                                        # centré au-dessus de la note) : titre align-self-start de FM -> centré
                                        # v5 (2026-11-15, le joueur : « Potentiel pas centré ») : aussi les titres
                                        # Niveau / Potentiel du bloc d'étoiles de FM (tes joueurs : rapport adjoint)
NOM_TITRE_RAPPORT = PREFIXE_ETOILES + "Titre"   # aiguillage du titre d'origine (Medium / Small) ; + « Large » : petit
TITRE_RAPPORT_LARGE = 10                        # px, titre du rapport en Large (v3)
ETOILES_ECART = 6   # px entre la note et les étoiles
# 2026-11-19 (le joueur, format Gómez : « augmente la hauteur entre rapport et les étoiles, on a plein de place ») :
# 16 px avec entete_style = gomez (tuile club plus haute que la carte Niveau des cartes)
if STYLE_GOMEZ:
    ETOILES_ECART = 16
    NOM_ETOILES += "-g1"


def etoiles_rapport(t):
    """job d'entete_fiche sur PlayerReportHeaderScoutSection"""
    a_nous = [r for r in t.walk() if t.name(r).startswith(PREFIXE_ETOILES)]
    if (vue() == "tuile" and named(t, NOM_ETOILES)) or (vue() != "tuile" and not a_nous):
        return []
    for r in a_nous:   # v2 : le titre du rapport ressorti de son aiguillage
        if r in t.refs and t.name(r) == NOM_TITRE_RAPPORT:
            par = t.parent[r]
            i = t.children(par).index(r)
            for j, k in enumerate(list(t.children(r))):
                move(t, k, par, i + j)
    for r in a_nous:
        if r in t.refs:
            t.remove(r)
    frame = first(t, lambda r: t.name(r) == "Frame")
    if frame is not None:   # FM : marge à droite du cadre (décalait le centre)
        cl = t.elem(frame).get("m_Classes") or []
        if vue() == "tuile":
            t.elem(frame)["m_Classes"] = [c for c in cl if c != "margin-right-global-gap-regular"]
        elif "margin-right-global-gap-regular" not in cl:
            t.elem(frame)["m_Classes"] = cl + ["margin-right-global-gap-regular"]
    titre_fm = first(t, lambda r: t.name(r) == "ScoutReport" and typ(t, r).endswith("SIText"))
    avant, apres = ("align-self-start", "align-self-center-class") if vue() == "tuile" else \
        ("align-self-center-class", "align-self-start")
    if titre_fm is not None:   # v4 : centré en vue tuile, à gauche (FM) sinon
        t.elem(titre_fm)["m_Classes"] = [apres if c == avant else c for c in t.elem(titre_fm).get("m_Classes") or []]
    # v5 : titres Niveau / Potentiel du bloc d'étoiles de FM (rapport de l'adjoint) : centrés en vue tuile
    ab = first(t, lambda r: t.name(r) == "AbilityStarRange")
    for r in (list(t.walk(ab)) if ab is not None else []):
        if t.name(r) in ("CurrentAbilityText", "PotentialAbilityText"):
            t.elem(r)["m_Classes"] = [apres if c == avant else c for c in t.elem(r).get("m_Classes") or []]
    has = first(t, lambda r: t.name(r) == "HasReport")
    kids = has is not None and t.children(has)
    if vue() != "tuile":
        if kids and len(kids) > 1:
            t.elem(kids[1])["m_Classes"] = []   # classes d'origine (aucune)
        return ["étoiles sous la note du rapport retirées (vue de FM)"]
    etoiles = first(t, lambda r: t.name(r) == "AbilityStarRange")
    if etoiles is None or not kids or len(kids) < 2:
        return ["étoiles ou rapport connu introuvables : étoiles non posées"]
    connu = kids[1]   # aiguillage HasScoutedInfo : 0 = pas supervisé, 1 = rapport
    t.elem(connu)["m_Classes"] = ["column-direction-normal", "align-items-center"]
    boite_ = boite(t, connu, {"margin-top": ETOILES_ECART, "flex-shrink": 0},
                   ["column-direction-normal", "align-items-center"], NOM_ETOILES)
    c = t.clone(etoiles, boite_)
    t.sd(c)["name"] = ""
    dedans = set(t.closure(c))
    # v6 (2026-11-19, le joueur : clic sur ces étoiles = rapport vide) : elles viennent de la branche entraîneur (tes
    # joueurs) et ouvraient le rapport de l'entraîneur, vide pour un joueur hors club -> même clic que la note du
    # recruteur (bouton de FM dont l'évènement passe isonmainscreen : rapport de recrutement)
    bouton_scout = first(t, lambda r: r not in dedans and typ(t, r).endswith("SIButton")
                         and b"isonmainscreen" in bytes((t.sd(r).get("Events") or {}).get("m_bytes") or []))
    if bouton_scout is not None:
        for r in dedans:
            if typ(t, r).endswith("SIButton"):
                t.sd(r)["Events"] = copy.deepcopy(t.sd(bouton_scout)["Events"])
    pot = first(t, lambda r: r in dedans and t.name(r) == "PotentialAbility")
    if pot is not None:   # dernière colonne : pas de marge à droite (centre juste)
        t.elem(pot)["m_Classes"] = [k for k in t.elem(pot).get("m_Classes") or []
                                    if k != "margin-right-global-gap-regular"]
    # v4 (le joueur : « centre le niveau et le potentiel pile au-dessus des étoiles ») : étiquettes centrées
    for r in dedans:
        if t.name(r) in ("CurrentAbilityText", "PotentialAbilityText"):
            t.elem(r)["m_Classes"] = ["align-self-center-class" if k == "align-self-start" else k
                                      for k in t.elem(r).get("m_Classes") or []]
    # v2 (le joueur, Large v32 : carte Niveau en demi-hauteur, rapport qui déborde) : titre « Rapport de supervision »
    # d'origine en Medium / Small (mode > 0) ; v3 (le joueur : « il doit apparaître, juste plus petit ») : en Large
    # (mode == 0) une copie du titre en petit
    msgs = ["rapport de supervision : étoiles Niveau / Potentiel sous la note (vue tuile)"]
    import notes_installations as ni
    titre = first(t, lambda r: t.name(r) == "ScoutReport" and typ(t, r).endswith("SIText"))
    s_vis, vis = ni.visible_model()
    if titre is not None and vis is not None:
        par = t.parent[titre]
        sv = ni.new_visible(t, s_vis, vis, par, t.children(par).index(titre), NOM_TITRE_RAPPORT,
                            ni.make_binding(s_vis.sd(vis)["Binding"], 4, [MODE], 0))
        move(t, titre, sv)
        sl = ni.new_visible(t, s_vis, vis, par, t.children(par).index(sv) + 1, NOM_TITRE_RAPPORT + "Large",
                            ni.equal_binding(s_vis.sd(vis)["Binding"], MODE, 0))
        petit = t.clone(titre, sl)
        t.sd(petit)["name"] = ""
        t.styles.style(t, petit, {"font-size": TITRE_RAPPORT_LARGE, "margin-top": 0, "margin-bottom": 1})
    else:
        msgs.append("rapport de supervision : titre introuvable, gardé en Large")
    return msgs


def hauteur_auto(t, oui):
    """v38 : hauteur du conteneur de FM en auto (oui) ou rendue à la règle de FM (non)"""
    c = first(t, lambda r: t.name(r) == CONTENEUR)
    if c is None:
        return False
    e = t.elem(c)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    reste = [p for p in old if not (p[0] == 131087 and p[2] == [AUTO])]
    if oui:
        e["m_RuleIndex"] = t.styles.add_rule(reste + [(131087, "", [AUTO])])
    elif len(reste) != len(old):
        e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
    return True


def remettre_fm(t):
    """nos tuiles retirées, bannières / photo de FM remises à leur place"""
    hauteur_auto(t, False)
    for c in [r for r in t.walk() if t.name(r) == NOM_CACHE]:
        par = t.parent[c]
        i = t.children(par).index(c)
        for j, k in enumerate(list(t.children(c))):
            move(t, k, par, i + j)
        t.remove(c)
    for c in [r for r in t.walk() if t.name(r) == NOM_PLACE]:   # v2 : contenu ressorti à la place du conteneur
        par = t.parent[c]
        i = t.children(par).index(c)
        for j, k in enumerate(list(t.children(c))):
            move(t, k, par, i + j)
        t.remove(c)
    for r in [r for r in t.walk() if t.name(r).startswith(PREFIXE)]:
        if r in t.refs:
            t.remove(r)


def job(t):
    """job d'entete_fiche sur PlayerReportHeader"""
    a_nous = [r for r in t.walk() if t.name(r).startswith(PREFIXE)]
    if vue() != "tuile":
        if not a_nous:
            return []
        remettre_fm(t)
        g = first(t, lambda r: typ(t, r).endswith("SIGradient"))
        if g is not None:
            couleur_club(t, g, True)   # option entete_couleur_club : sans effet sur l'en-tête de FM
        trait_bas(t, True)
        return ["en-tête de FM remis (vue grande tuile retirée)"]
    if named(t, NOM):
        return []
    if a_nous:   # ancienne version : FM remis, puis refait
        remettre_fm(t)
    import notes_installations as ni
    from moteur_photos import ouvrir
    src = Src(SOURCE)
    if src.s is None:
        return [f"{SOURCE} introuvable : grande tuile non posée"]
    p, manque = pieces(src.s)
    if manque:
        return [f"en-tête grande tuile : {', '.join(manque)} introuvable(s) dans la bannière, ignoré"]
    txt = Src("PlayerReportHeaderScoutSection")
    txt_rid = txt.s and first(txt.s, lambda r: typ(txt.s, r).endswith("SIText") and txt.s.name(r) == "ScoutReport")
    photo = first(t, lambda r: t.name(r) == "PersonPictureFrame")
    rm_model = first(t, lambda r: typ(t, r).endswith("BindingRemapper"))
    degrade = first(t, lambda r: typ(t, r).endswith("SIGradient"))   # dégradé du club de l'en-tête d'origine
    if degrade is not None:   # option entete_couleur_club (2026-11-19) : « non » = dégradé caché (opacité 0)
        couleur_club(t, degrade, COULEUR_CLUB)
    trait_bas(t, False)
    o = ouvrir("PlayerAttributesLargeBlock", depart_original=True)
    fa = o and o[3]
    haut = fa and first(fa, lambda r: fa.name(r) == "PersonHeightTextFrame")
    chart = fa and first(fa, lambda r: typ(fa, r).endswith("FMSpiderChart"))
    s_vis, vis = ni.visible_model()
    if None in (txt_rid, photo, rm_model, vis):
        return ["en-tête grande tuile : titre, photo ou modèles introuvables, ignoré"]
    def cacher(r):
        """v9 : élément SANS liaison (taille 0, hors du flux, coupe tout) : v1-v8 = SIVisible « mode == 99 », qui
        laissait voir la bannière de FM pendant le chargement de la fiche (liaison pas encore lue), avec le grand
        polygone de l'en-tête Medium (le joueur : « le polygone flashe trop gros avant »)"""
        par = t.parent[r]
        c = boite(t, par, {"position": "absolute", "left": 0, "top": 0, "width": 0, "height": 0,
                           "max-width": 0, "max-height": 0, "overflow": "hidden"}, [], NOM_CACHE)
        move(t, c, par, t.children(par).index(r))
        move(t, r, c)
        return c

    msgs = []
    bannieres = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") in TAILLES
                 and t.name(t.parent[r]) != "PhoneSwitch"]
    for r in bannieres:
        dims = {**TAILLES[t.elem(r)["m_TemplateAlias"]], "numero": NUMERO[t.elem(r)["m_TemplateAlias"]],
                "maillot": MAILLOT[t.elem(r)["m_TemplateAlias"]]}
        # ESSAI ENTETE_PLUS : ⚠ la bannière (max / mid / min) suit la LARGEUR de la fenêtre, pas l'affichage Large /
        # Medium / Small (« max » aussi en Medium chez le joueur) -> la hauteur en plus suit l'affichage (construire :
        # cale liée au mode, Medium / Small seulement ; le joueur : « large on avait déjà fait un truc parfait »)
        haut_ = t.parent[r]
        place = plain(t, haut_, t.children(haut_).index(r), ["align-self-stretch"], NOM_PLACE)
        t.sd(place)["name_UxmlAttributeFlags"] = 1
        t.elem(place)["m_RuleIndex"] = -1
        move(t, r, place)
        cacher(r)
        msgs += construire(t, place, None, dims, src, p, (txt, txt_rid), photo,
                           (fa, haut) if haut is not None else None, (fa, chart) if chart is not None else None,
                           rm_model, s_vis, vis, degrade)
    cacher(photo)
    if not hauteur_auto(t, True):
        msgs.append(f"en-tête grande tuile : {CONTENEUR} introuvable, hauteur de FM gardée (bas coupé)")
    # pas de photo de FM recopiée en double : les tuiles ont la leur
    return list(dict.fromkeys(msgs)) + [f"en-tête en grande tuile ({len(bannieres)} tailles de fenêtre)"]
