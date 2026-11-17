"""[AJOUT KINITO] Calendrier, onglet Rencontres : le programme des rencontres en vrai tableau FM, avec des vues personnalisables.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : « dans l'onglet programme de rencontre, vue perso + possibilité d'importer, comme ce
qu'on a fait pour recommandation […] c'était possible sur FM24 ». Choix de Kinito : la vue par défaut est celle de FM (a),
on ne crée pas d'objet nouveau dans le jeu (pas de b).

Relevé dans le jeu (2026-11-12, rien de deviné) :
- la liste du programme (CalendarFixturesListBlock #FixturesList) n'est PAS un tableau : une StreamedObjectList de lignes
  toutes faites (CalendarFixtureRow, puis _MaxRes / _StandardRes / _MinRes), le titre du mois DANS la ligne du 1er match du
  mois (SIVisible listelement.isfirstfixtureofthemonth) ; d'où « Modifier les colonnes » bloqué (relevé aussi par Alex) ;
- ses données, team.FixtureListElements (DynamicReference {fixture, index, isfirstfixtureofthemonth}, relevé sonde F7),
  sont celles du tableau des matchs de Portail > Vue d'ensemble (PortalAdaptiveContentBlock, un StreamedTable) ;
- la fabrique de colonnes de ce tableau, FixtureListElementTableFactory (ui-tablefactories), a 8 colonnes : tv, date,
  date-day, time, club, venue, result, comp ; sa vue PortalFixtureScheduleTableViewSettings en montre 7 ;
- une collection de vues = une liste de vues (objets du même bundle) ; les vues personnalisées sont des fichiers .json,
  rangés dans un dossier au NOM de la collection (code : StreamedTableViewSettingsCollection.CreateCustomViewFilePath) ;
- une seule collection de vues n'est citée par aucun bundle ni par le code : NationalPoolPlayerSearchShortlistView-
  Collection (e4593511…) ; ses vues servent à 7 autres collections : on ne touche qu'à SA liste, jamais à ses vues.

Ce que fait l'ajout (état v14 ; détail dans « AJOUTS KINITO - DETAILS.md », § 10) :
- bloc CalendarFixturesListBlock (bundle global), PARTAGÉ avec kinito_rencontres_boutons (26.2, propriétaire : il repart
  de l'original) : on part du modèle ACTUEL et on n'ajoute / retire que nos morceaux, par leur nom. L'en-tête et la liste
  de FM, intacts, dans un SIVisible montré en petit format (PETIT = usesmallview, variable du bloc de FM) ; à côté, hors
  petit format, un BindingVariables qui déclare V_VUE (selectedView : le modèle TableViewDropdown de FM lit CE nom en dur)
  et VUES_PRETES, et contient le menu des vues (#TableViewDropdown des capitaines, relié DELAI s après le tableau par un
  SIDelayEvent, comme 26.5 / 26.8) et le tableau : copie de celui du Portail (mêmes données) avec les réglages de la Base
  de données, notre collection, la sélection dans selectedfixturelistelement (l'aperçu à droite), SelectionMode 2 et une
  colonne de sélection à 0 px, le défilement jusqu'à team.NextFixtureListElement, le modèle de ligne LIGNE, AlternateRows
  0. Les variables du filtre sont à la racine du bloc ; dans le bandeau, le bouton « Filtre ⌄ » (SIFloatingPopupWidget,
  contenu = PANNEAU) et, pour un club IA, la rangée de ses équipes (ee.rangee d'Alex, boutons CELLULE_IA) avant le Filtre ;
- objets de FM cités par RIEN (données décompressées de tous les bundles ui-*, code du jeu, scripts du skin), réécrits
  depuis leur original, ce script seul propriétaire : LIGNE (titre du mois, lignes cachées par le filtre, zone des
  cellules de hauteur fixe), PANNEAU (le filtre), CELLULE (Spectateurs), CELLULE_DATE, CELLULE_IA, FABRIQUE_TABLEAU (copie
  de FABRIQUE + nos colonnes), la liste de COLLECTION (jamais ses vues), VUE_RENCONTRES (vue par défaut), VUE_FILTRE ;
- lus seulement, et remis d'origine si une ancienne version les avait changés (un ajout ne doit changer aucun autre
  écran) : FABRIQUE, FABRIQUE_COMPS, VUE_FILTRE_V6.
Ce qui change pour le joueur : un tableau FM au lieu de la liste (titre du mois, vues perso, filtre, colonnes), aussi
sur le programme d'un club IA ; en petit format, la liste de FM et les colonnes Stade / Spectateurs d'Alex restent.
Retirer remet la liste d'origine.
v15 (copie d'UI PICKER, demande d'Alex le 11/10) : le menu des vues n'est plus sous le nom de l'équipe mais dans
l'en-tête, à gauche du bouton Filtre ; V_VUE et VUES_PRETES passent du BindingVariables à la racine du bloc.
v16 (Kinito, 13/10) : un nom de vue long (« Kinito personnalisé ») élargissait le menu VERS LA DROITE et poussait
Filtre hors de l'écran. Mesuré (sonde, clic du 13/10 11:25) : la rangée d'équipes de 26.2 réserve 520 px pour ~200
utiles, la zone du Filtre (291 de large) se tassait et le menu + Filtre débordaient de 48 px à droite du bloc. Donc :
la zone du Filtre ne se tasse plus (flex-shrink 0 : c'est le vide de la rangée de 26.2 qui cède, le menu s'étend vers
la GAUCHE, Filtre reste au bord), et le menu est plafonné à LARGEUR_MAX_MENU (sm.LARGEUR_MAX d'Alex) : au-delà, le nom
se coupe en « … » (son texte, dans le modèle de FM GenericDisplayValuePairDropdownRow, a déjà content-no-wrap et
content-ellipsis). Seuls nos éléments changent (la zone et l'enveloppe du menu) : aucun modèle de FM n'est touché.

v18 (Kinito, 13/11, ESSAI) : « si je regarde le calendrier de l'année passée je ne peux pas filtrer ceux de l'an
passé ». Relevé dans le code du jeu : le menu « Saison » de FM (CalendarHeaderSeasonBlock) écrit Year / yearindex, que
team.FixtureListElements suit (contextes YearIndex, PreviousAmount, FutureAmount, FixturePadding) ; team.CurrentComps n'a
AUCUN contexte (la saison en cours seulement), et aucune propriété d'équipe, de club, de personne ni de compétition ne
donne « les compétitions d'une saison » (TeamReference / ClubReference / PersonReference / CompReference ::
GetContextsInternal). Une compétition de l'an passé absente cette saison (championnat quitté en montant) n'était donc ni
dans le panneau ni jamais cachée. La v18 ajoutait une section « Compétitions nationales » = Nation.DivisionList du pays
du championnat de l'équipe (copie dans les archives) : VUE EN JEU le 13/11 (Rodez, saison 2026/27), le titre s'affichait, AUCUNE ligne
(liste vide ici ; peut-être la variable « gender » que la page d'un pays déclare autour, pas prouvé), et la Coupe de
France pas encore commencée manquait aussi à la liste de la saison.
v19 (Kinito, 13/11, ESSAI, son choix : « masquer au clic ») : plus aucune liste de FM. Section « Compétitions masquées »
du panneau : « Masquer la compétition du match sélectionné » copie selectedfixturelistelement.Fixture.Competition (ce que
le bloc de FM passe à l'aperçu : selectedfixture) dans la 1re case libre de MASQUES cases (variables kinitofmasque1..N à la
racine) ; chaque case remplie s'affiche (nom) avec « Remettre » (copie const.NullRef, comme FM). Pour chaque case, à la
racine, la fonction de FM BindAndSetAOrBToDestinationUsingReferenceIsNullAsBool (079b54af, celle de ViewedFixtureTooltip :
« isClub ») calcule kinitofpleinN (case remplie) et kinitofidN (UniqueId de sa compétition, 0 si vide) SANS jamais lire
une référence vide (IsNullReference) ; dans chaque ligne, la comparaison d'entiers déjà utilisée pour Domicile
(c4a44b78, op 2 = égal) compare binding.fixture.Competition.UniqueId à kinitofidN : jamais un entier vide (GetInt de FM
plante sur une valeur vide : relevé dans son code). Une ligne est cachée si une case est remplie ET égale. Vaut pour toute
saison et toute compétition (coupe pas commencée, championnat quitté, coupe d'Europe d'il y a 3 ans). Textes écrits en
clair (comme ceux du skin d'Alex : FM n'a pas de « Masquer » à recopier). Aussi : le titre du mois passe AVANT les
enveloppes du filtre : un 1er match du mois caché (un amical) emportait le titre du mois avec lui. VUE EN JEU par Kinito
le 13/11 : « le reste fonctionne » ; un mois entièrement filtré garde son titre seul (juillet, tout en amicaux) : il
choisit de le garder ainsi.
v20 (Kinito, 13/11 : « n'utiliser que ce procédé pour filtrer », ses choix) : la liste à cases des compétitions de cette
saison est RETIRÉE (V_FCOMPS, V_PRET, la condition « comp », le tableau du panneau ; la vue VUE_FILTRE, plus utilisée,
est remise d'origine). Le bouton « Masquer cette compétition » passe dans le bandeau du calendrier, entre le menu des
vues et Filtre (« Vues - Masquer la compétition - Filtre ») : un seul bouton visible, celui de la 1re case libre (6
SIVisible, ET sur les cases d'avant remplies et la sienne vide), dans 6 enveloppes qui le cachent si la compétition du
match sélectionné est déjà masquée (kinitofidsel, UniqueId de la sélection ou 0, calculé comme les cases, comparé à
chaque kinitofidN). Le panneau Filtre : Réinitialiser (tout : cases vidées, Hors compétition, Domicile, Extérieur), les
compétitions masquées (nom + « Remettre », ou « Aucune… »), Hors compétition, Lieu. VUE EN JEU par Kinito le 13/11 :
« ça fonctionne ».
v21 (Kinito, 13/11 : « traduis cette feature dans toutes les langues du jeu ») : nos quatre textes (« Masquer cette
compétition », « Compétitions masquées », « Remettre », « Aucune… ») suivent la langue RÉGLÉE DANS FM, en direct :
recette 19 (comme 26.18, vue en jeu) : le conteneur de FM de tdd-messages-banner (bundle global, variable
current_language, languagesetting -> app.NativeSettings), puis un interrupteur de FM par langue (7980ef35 : texte ==
languagesetting.PropertyValue ; rang 1 = c'est elle) ; l'anglais sinon (anglais US, tchèque, thaï : le fichier de FM 27
n'a pas ces deux dernières). Un interrupteur de FM ne construit que la langue réglée. Les deux boutons sont recopiés
entiers dans chaque langue (le bouton de FM et son texte, comme en v20), les deux textes seuls. Traductions : TRADUCTIONS
(mots de FM recopiés du fichier des langues de FM 27 quand il les a, le reste par nous ; personne de langue maternelle ne
les a relus). Les autres textes du filtre (Filtre, Réinitialiser, Hors compétition, Lieu, Domicile, Extérieur, les vues,
les mois) étaient déjà ceux de FM, par leur n° de traduction : rien à faire. VUE EN JEU par Kinito le 14/11 : « ça
fonctionne ».
v22 (Kinito, 14/11 : « parfois le filtre bug un peu » : toutes les compétitions masquées sauf la Coupe de France, des
tours manquaient, revenus en faisant défiler, « comme un retard d'affichage ») : CAUSE (code du jeu, lu le 14/11) : le
tableau de FM ne construit que les lignes censées être à l'écran (DynamicSizeVirtualisationController) et place les
autres avec la hauteur MÉMORISÉE la dernière fois qu'il les a vues (SizeCache, mis à jour seulement par la ligne
affichée : VirtualisedElementSizeChanged). Une ligne masquée hors de l'écran garde donc pour lui ses 32 px d'avant au
lieu d'1 px : des matchs plus bas lui semblent hors de l'écran, jusqu'à ce que le défilement les lui fasse mesurer.
CORRECTIF : rebrancher le tableau après chaque changement du filtre. StreamedListView.BindToData pose l'état 8, que
StateChanged traite par Rebuild, qui VIDE le SizeCache (SetFallbackSize de la moyenne, Clear, ResetView). Le tableau est
donc dans un SIVisible de FM sur kinitofaffiche (V_AFFICHE, vrai au départ), en VisibilityType 1 (VisibilityFlag : il
garde sa place, rien ne saute à l'écran) ; caché, FM le débranche (SIVisible.ShowWidget -> BindChildren(faux) ->
DeferredContent.TeardownFromChildren), remontré il le rebranche (ResumeFromChildren). Chaque geste du filtre (Masquer,
Remettre, Réinitialiser, les trois cases) finit par « kinitofaffiche = faux » ; un SIVisible inversé sur la même variable
porte un SIDelayEvent de FM qui la remet à vrai DELAI_RECHARGE plus tard (rebranché à chaque fois qu'il se remontre,
comme la zone d'écriture de 26.6 v8). Conséquence : comme à l'ouverture, le tableau revient sur le prochain match
(ScrollToElementBinding + SetScrollToAsSelected), qui devient le match sélectionné.

Historique des versions (demandes, relevés en jeu, essais) : résumé dans « AJOUTS KINITO - DETAILS.md »,
§ 10 ; texte complet gardé par Kinito.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_vues.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_vues.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rencontres_vues.py etat
"""
import copy
import json
import os
import struct
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, _enc_varint, decode_args, encode_args  # noqa: E402
import elements  # noqa: E402  (copy_usings : les modèles inclus d'un morceau recopié)
import arbre as sm  # noqa: E402  (v13 : propriétés de style left / right / bottom)
import entrainement_equipes as ee  # noqa: E402  (v13 : rangée, bouton et événement d'Alex, sans les modifier, comme 26.2)

# v13 : identifiants lus dans le jeu (UnityEngine.UIElements.StyleSheets.StylePropertyId, UIElementsModule.dll)
sm.PROPRIETES.setdefault("left", (131089, 3))
sm.PROPRIETES.setdefault("right", (131103, 3))
sm.PROPRIETES.setdefault("bottom", (131080, 3))

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
DELAI = 0.5          # s : le menu des vues apparaît (et se relie) ce temps après le tableau (comme 26.5 / 26.8)
HAUTEUR_LIGNE = 32   # px : hauteur d'une ligne de match (mini, v4 ; Portail : 28 ; tableau des capitaines : 32)
MARGES_MOIS = (8, 4)  # px : au-dessus et au-dessous du nom du mois, dans le bandeau (v4 : 6 / 2)
CLASSE_MOIS = "heading-small-16px"   # v5 (Kinito : « augmenter la police des mois ») : 16 px, police de titre de FM ;
                                     # la liste de FM : body-sm-strong (12 px gras) ; plus grand : heading-regular-18px
LARGEURS = {"kinito-stade": (180, 90), "kinito-spectateurs": (90, 60)}   # px : largeur par défaut, minimum
ECART_MENU = 8       # px entre le menu des vues et le bouton Filtre (v15 ; 8 = écart FM entre deux boutons)
LARGEUR_MAX_MENU = 300   # px : largeur maximale du menu des vues (v16, choix de Kinito ; au-delà, le nom se coupe en « … »)
# v24 (Alex, 17/11) : FM du 2026-11-17, chaque colonne d'une vue a une part de la place libre (m_growWeight, 0 = ne
# grandit pas ; la vue du Portail : Club 1, le reste 0). Sans part, le tableau restait à sa largeur minimum (moitié du
# bloc, dates sur 2 lignes). Part de chaque colonne de la vue « Programme des rencontres » (absente = 0)
GRANDIT = {"club": 1.0, "kinito-stade": 1.0, "comp": 0.5, "kinito-date": 0.5}
# =====================================================================================================

VERSION = 24  # v24 (Alex, 17/11) : colonnes qui s'élargissent (GRANDIT, m_growWeight de FM) ;
              # v23 (Alex, 17/11) : MAJ de FM, liste = tableau de FM (#FixturesTable) caché comme l'ancienne liste,
              # titre du mois pris dans CalendarFixtureTableRowElement ; historique : voir la docstring ; v15 (Alex, 11/10) : menu des vues à gauche de Filtre, variables des
              # vues à la racine du bloc ; v16 (Kinito, 13/10) : le menu s'étend vers la gauche, plafonné ;
              # v17 (Alex, 20/10) : VisualElement nu cherché dans plusieurs modèles (MAJ de FM, SOURCES_ELEMENT) ;
              # v18 (Kinito, 13/11, essai) : « Compétitions nationales » dans le filtre (liste vide en jeu) ;
              # v19 (Kinito, 13/11, essai) : « Compétitions masquées » au clic, titre du mois hors du filtre ;
              # v20 (Kinito, 13/11) : « Masquer cette compétition » dans le bandeau, plus de liste à cases ;
              # v21 (Kinito, 13/11) : nos quatre textes dans la langue réglée dans FM (TRADUCTIONS) ;
              # v22 (Kinito, 14/11) : le tableau rebranché après chaque geste du filtre (des matchs manquaient)
COLONNE_SELECTION = "kinito-selection"   # v5 : notre colonne de sélection, 0 px, cellule vide (SelectionCellID)
SOURCE_SELECTION = ("PlayerPositionalRolesTableFactory", "selection-small")   # v8 : la colonne de sélection à 0 px de FM
GUID_CELLULE_SELECTION = "b08b21f21a0ebe24fb8168b6dd702eeb"   # sa cellule : RadioToggleCell (un bouton, AUCUN texte)
BLOC ="CalendarFixturesListBlock"                     # bundle global, PARTAGÉ avec 26.2 (kinito_rencontres_boutons)
CELLULE = "LiveTablePtsCell"                           # bundle gameworld, inutilisée : réécrite (Spectateurs)
GUID_CELLULE = "109c38ab9d4ae8e47b8966be700fca74"
FABRIQUE = "FixtureListElementTableFactory"
GUID_FABRIQUE = "1866d2cac42a10d44a6bfda2d752767c"
LIGNE = "BulletTextRow"                                # bundle gameworld, inutilisé : réécrit en modèle de ligne (v4)
GUID_LIGNE = "0a3d196bd3bbfb14bb0af4e91ffd3276"
TYPE_ELEMENT = 1986679663   # type du paramètre « listelement » de CalendarFixtureRow (un élément de FixtureListElements)
SOURCE_MOIS = ("CalendarFixtureRow", "ShowMonth", "Month")   # le titre du mois de la liste de FM
SOURCE_MOIS_FMMAJ = "CalendarFixtureTableRowElement"   # v23 : FM du 2026-11-17, même #ShowMonth > #Month (fixture.FixtureDate)
SOURCE_ELEMENT = ("CompetitionsLeagueTableStagesTile_Table_Row_Template", "list-layout-divider-solid-horizontal")
# v17 (Alex, 20/10) : retiré de ce modèle par la MAJ de FM du 2026-11-12 -> autres VisualElement nus de FM, dans l'ordre
# (classes et style remplacés à chaque copie : n'importe lequel convient)
SOURCES_ELEMENT = [SOURCE_ELEMENT, ("NonPlayerAttributesBlock", "divider"), ("GenericModalDialog", "layout-divider")]
CLASSE_TRAIT = "layout-divider-solid-horizontal"       # trait de FM : 1 px, toute la largeur, couleur du thème
COLLECTION = "NationalPoolPlayerSearchShortlistViewCollection"   # inutilisée : sa liste de vues est réécrite
GUID_COLLECTION = "e45935119858ada499c85d638823de63"
GUID_COLLECTION_CAPITAINES = "a0216e8d74ac92642ae8716ff6ebb02c"   # celle des morceaux recopiés du bloc des capitaines
VUE_DEFAUT = "PortalFixtureScheduleTableViewSettings"  # vue du tableau des matchs du Portail (lue, jamais modifiée)
SOURCE_NOMS_VUES = "PlayerSearchResultsViewCollection"           # nom / préfixe des vues personnalisées
SOURCE_REGLAGES = ("PersonSearchMainContentBlock", "playertable")
REGLAGES = ["ContextMenuData", "AllowColumnReordering", "AllowColumnResizing", "ViewDropdownName", "ScrollViewMode",
            "HorizontalScrollerVisibility"]
SOURCE_TABLEAU = "PortalAdaptiveContentBlock"           # son StreamedTable sur team.FixtureListElements
SOURCE_CAPITAINES = "SquadCaptainsBlock"                # InitFunction du tableau, menu des vues, déclaration de la vue
SOURCE_VARIABLES = ("PlayerRecommendationsMainBlock", "BindingVariables_FM")
SOURCE_VISIBLE = ("PersonSearchMainContentBlock", "position-view-visible")
SOURCE_DELAI = "GameCreationGameSummaryScreen"
SOURCE_JOUE = ("CalendarFixtureCard_MaxRes", "AttendanceVisible")
DONNEES = "team.FixtureListElements"
SELECTION = "selectedfixturelistelement"               # celle de la liste de FM : l'aperçu du match, à droite
MODE_SELECTION = 2      # comme la liste de FM : SI.UI.VirtualisedList.SelectionModes.ExactlyOne (0 = aucune sélection)
DEFILER = "team.NextFixtureListElement"                # celle de la liste de FM
TRAD_VUE = 34911        # « Programme des rencontres » (le titre du bloc)
TRAD_STADE = 18770      # « Stadium » (colonne d'Alex)
TRAD_SPECTATEURS = 43782   # « Attendance » (colonne d'Alex)
COLONNES_MENU = ["tv", "date", "date-day", "time", "club", "venue", "result", "comp", "kinito-stade",
                 "kinito-spectateurs"]
# v11 (10/10, Kinito : « ajouter dans Insérer colonne toutes les colonnes de cet écran », capture de « Modifier
# l'affichage » des rencontres de FM24). Chaque colonne = une colonne de FM recopiée telle quelle (même cellule), ses
# chemins réécrits vers une propriété du match que FM utilise déjà ailleurs (relevé du 10/10 dans les modèles :
# MatchReferee.Name et Weather.WeatherDescriptionString dans MatchPreviewCardHeader, NextMatchDaysText dans
# NextFixtureCell, TVRightsString dans CalendarFixtureRow_StandardRes, HomeTeam / AwayTeam partout, Result + ResultType
# avec la cellule résultat + icône de FM, MatchResultCellWithBorder). Titres : n° de traduction de FM, repérés par leur
# texte anglais de conception (DebugDisplay) : à vérifier en jeu. Pas de « Formation » ni de « Formation adverse »
# (aucune donnée de formation d'un match trouvée ; choix de Kinito : on les laisse), « Buteurs » plus tard (choix de
# Kinito : il faut fabriquer une cellule). Droits TV : FM n'a qu'un texte par match (pas un par équipe).
COLONNES_V11 = [   # (id, titre, (fabrique source, colonne source), {chemin de la source : chemin réécrit}, largeurs)
    # v12 : titres « Domicile » / « Extérieur » (25515 / 25516, déjà lus en jeu dans le panneau du filtre) ; en v11,
    # 11620 / 11627 (texte de conception « Home Team ») affichaient « team#1 » : des traductions à paramètre
    ("kinito-domicile", 25515, (FABRIQUE, "club"),                       # « Home » (Domicile)
     {"binding.fixture.TeamOpponent": "binding.fixture.HomeTeam"}, (180, 90)),
    ("kinito-exterieur", 25516, (FABRIQUE, "club"),                      # « Away » (Extérieur)
     {"binding.fixture.TeamOpponent": "binding.fixture.AwayTeam"}, (180, 90)),
    ("kinito-icone-resultat", 9824, ("PlayerTableFactory", "last-int-match-result-with-icon"),   # « Form »
     {"binding.LastInternationalForm.Result": "binding.fixture.Result",
      "binding.LastInternationalForm.ResultType": "binding.fixture.ResultType"}, (80, 60)),
    ("kinito-arbitre", 43798, (FABRIQUE, "time"),                        # « Referee »
     {"binding.fixture.KickoffTime": "binding.fixture.MatchReferee.Name"}, (150, 80)),
    ("kinito-meteo", 43797, (FABRIQUE, "time"),                          # « Weather »
     {"binding.fixture.KickoffTime": "binding.fixture.Weather.WeatherDescriptionString"}, (150, 80)),
    ("kinito-quand", 9795, (FABRIQUE, "time"),                           # « Days » (FM n'a pas de « When »)
     {"binding.fixture.KickoffTime": "binding.fixture.NextMatchDaysText"}, (110, 60)),
    ("kinito-droits-tv", 25780, (FABRIQUE, "time"),                      # « TV » (titre de la liste de FM)
     {"binding.fixture.KickoffTime": "binding.fixture.TVRightsString"}, (130, 60)),
]
COLONNES_MENU += [c[0] for c in COLONNES_V11]
# v12 (11/10, Kinito, après la v11 en jeu) : trois colonnes à nous, recopiées de colonnes de cette fabrique (titres et
# réglages propres : dans les vues recopiées du Portail, « tv » ne se montrait que sur une taille d'écran et « time »
# sautait faute de place, et ces réglages restent dans les vues perso de Kinito) ; (id, titre, colonne source,
# largeurs, cellule remplacée ou None)
CELLULE_DATE = "EventCell"                             # bundle gameworld, citée par rien : réécrite (la date)
GUID_CELLULE_DATE = "ffc4552057d5cb84d815930c04209a1f"
SOURCE_DATE = "DateCell_BreakpointDependent"           # cellule de FM : « [abbr_day] [date_short_month_year] » (14297)
TRAD_DATE_JOUR = 14297                                 # ou « [%date#1-long] » selon la taille d'écran : on garde 14297
COLONNES_V12 = [
    ("kinito-date", 43356, "date-day", (120, 90), GUID_CELLULE_DATE),   # « Date » ; « Dim 15 nov. 2026 »
    ("kinito-heure", 25781, "time", (60, 45), None),   # « Time » de l'en-tête de la liste de FM (CalendarFixture-
                                                       # ListHeader_MaxRes) ; 43367 s'affiche « Temps » : à vérifier en jeu
    ("kinito-tv", 43366, "tv", (40, 30), None),        # l'icône TV de FM (TVCell, binding.Fixture.IsOnTV)
]
# v12 : le menu « Insérer colonne » (Kinito, 11/10 : une seule date, avec le jour ; l'icône TV ; sans Forme, Jours ni
# Arbitre — FM ne garde l'arbitre que sur le prochain match une fois désigné : MatchPreviewCardHeader, MatchPreviewTile_*)
COLONNES_MENU = ["kinito-date", "kinito-heure", "club", "kinito-domicile", "kinito-exterieur", "kinito-tv", "venue",
                 "result", "kinito-spectateurs", "kinito-stade", "comp", "kinito-meteo"]
# v12 (Kinito, 11/10 : « notre tableau rencontre doit être indépendant des autres tableaux, il ne doit pas impacter un
# autre écran ») : NOTRE fabrique. FixtureListElementTableFactory sert aussi au Portail (PortalAdaptiveContentBlock) et à
# la préparation de pré-saison (PreseasonTrainingPreparationBlock) : elle est remise d'origine et seulement lue ; sa copie,
# plus nos colonnes, va dans la seule fabrique du jeu citée par rien (fabriques_libres.py : données décompressées de tous
# les bundles ui-*, code du jeu, scripts du skin ; même script C# que FixtureListElementTableFactory)
FABRIQUE_TABLEAU = "AgentTableFactory"
GUID_FABRIQUE_TABLEAU = "81ee9a75c22f24c4888512efef3a98cf"
# v12 : le bloc (CalendarFixturesListBlock) sert aussi au programme d'un AUTRE club (FixturesAIClubTool) et au profil de
# club dans la fiche de match (ClubProfileInMatchCard, NationalTeamContainerProfileInMatchCard : forcesmallview vrai) ;
# nos morceaux (tableau, menu des vues, bouton Filtre) ne se montraient que pour une équipe du club du joueur, hors petit
# format (v13 : pour toute équipe, hors petit format) ; ailleurs, la liste de FM, intacte. usesmallview = forcesmallview
# OU app.GridBreakpointIsSmall (calcul du bloc)
V_HUMAIN = "kinitofhumain"           # vrai : l'équipe affichée est une équipe du club du joueur (variable de la racine)
EQUIPES_HUMAIN = "human.Club.Teams"  # les équipes du club du joueur (celle des boutons 26.2)
PETIT = "usesmallview"               # variable du bloc de FM
NOM_MONTRE = "UIPickerKinito-rencontres-vues-montre"   # notre partie de #Fixtures (préfixe « -rencontres-vues »)
NOM_ZONE_FILTRE = "UIPickerKinito-rencontres-vues-filtre-zone"   # le bouton Filtre, dans l'en-tête
# v13 (Kinito, 11/10 : « appliquer notre tableau aux programmes de rencontre des clubs IA », « un bouton sur leur écran
# qui mène au programme de leur équipe jeune, réserve, première, comme nous ») : nos morceaux pour toute équipe hors
# petit format (v12 : club du joueur seulement), et une rangée de boutons d'équipes pour un club IA
CELLULE_IA = "LiveTablePositionCell"                   # bundle gameworld, citée par rien (modeles_libres.py, 11/10) :
GUID_CELLULE_IA = "2bcbc4ad56ffaca4da932cd4480701c8"   # réécrite en bouton d'équipe IA (seul propriétaire)
OUTIL_IA = "bf02c4f9c08fa3f458d42f8f5251a633"          # FixturesAIClubTool : le programme d'un autre club
OUTIL_HUMAIN = "cc93f9746a2f0204d8d5a7bcb3fb316f"      # CalendarToolFixturesTab (pour relire l'événement de FM)
PARAMS_IA = [("human", "human"), ("calendartab", "const.Two"), ("team", "row")]   # ceux de FM (flèches ^ v du bloc)
VAR_FLECHE = "previoussibling"                         # l'équipe que vise la flèche ^ de FM (relecture de l'événement)
EQUIPES_IA = {"liste": "team.Club.Teams", "largeur": 520, "hauteur": 32, "descendre": 2, "marge": 24}   # = 26.2
NOM_EQUIPES_IA = f"UIPickerKinito-rencontres-vues-equipes-ia-v{VERSION}"   # préfixe « -rencontres-vues » : retirer_bloc
NOM_CELLULE_IA = f"UIPickerKinito-rencontres-bouton-ia-v{VERSION}"
# v12 : la vue « Programme des rencontres », à nous (l'ordre de FM24, Stade en plus à la fin)
VUE_RENCONTRES = "SquadHierarchyPlayersTable"          # ui-tableviews, citée par rien (vues_libres.py) : réécrite
GUID_VUE_RENCONTRES = "1e8c7ed1ec1daad4bb61aa6cd384596a"
COLONNES_VUE = ["kinito-date", "kinito-heure", "club", "kinito-tv", "venue", "result", "kinito-spectateurs", "comp",
                "kinito-stade"]
V_VUE = "selectedView"   # la vue choisie, déclarée par nous : CE nom, que le modèle TableViewDropdown de FM lit en dur
                         # (v1 : « kinitovuerencontres », menu et tableau restés vides en jeu)
VUES_PRETES = "kinitovuesprete"
PREFIXE = "UIPickerKinito"
NOM_CACHE = f"{PREFIXE}-rencontres-liste-fm"           # l'en-tête et la liste de FM, cachés (gardés intacts)
NOM_VUES = f"{PREFIXE}-rencontres-vues-v{VERSION}"     # nos morceaux
NOM_ENTETE = f"{PREFIXE}-rencontres-entete"
NOM_MENU = f"{PREFIXE}-rencontres-menu"
NOM_TABLEAU = f"{PREFIXE}-rencontres-tableau"
NOM_DELAI = f"{PREFIXE}-rencontres-delai"
NOM_JOUE = f"{PREFIXE}-spectateurs-si-joue"
NOM_LIGNE = f"{PREFIXE}-rencontres-ligne"              # v4 : le modèle de ligne réécrit
NOM_MOIS = f"{PREFIXE}-rencontres-mois"
NOM_CELLULES = f"{PREFIXE}-rencontres-cellules"
REPERE = f"UIPickerKinito-rencontres-v{VERSION}"       # debug_name posé sur la collection, la fabrique et la cellule
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_rencontres_vues.actif")

# ----- v6 / v7 : LE FILTRE (Kinito, 10/10 : « rangé comme FM24 », Lieu en plus, « Hors compétition » = les amicaux ;
# v7 : « mettre de base tous les filtres actifs ») -----
# Chaque case : cochée = « afficher ça » ; tout est coché au départ, décocher cache. Aucun filtre côté moteur
# (InteropEventIDs : rien pour les matchs) : tout se fait dans la ligne.
V_FHC, V_FDOM, V_FEXT = "kinitofhc", "kinitofdom", "kinitofext"   # cases Hors compétition, Domicile, Extérieur
VARS_FILTRE = [V_FHC, V_FDOM, V_FEXT]   # v7 : vraies (cochées) au départ
# v7 à v19 : la liste à cases des compétitions de cette saison (team.CurrentComps copiée dans kinitofcomps, kinitofpret,
# condition « comp » de la ligne) ; v20 : retirée (Kinito : « n'utiliser que ce procédé », le masquage)
L_DOM = "kinitoxdomicile"   # calculé dans chaque ligne
# v19 : les compétitions masquées au clic (toute saison) : MASQUES cases à la racine du bloc (préfixe « kinitof » : retirées
# avec les autres), et pour chacune « remplie » et l'UniqueId de sa compétition (0 si vide), calculés sans lire de vide
MASQUES = 6
V_MASQUE = [f"kinitofmasque{k}" for k in range(1, MASQUES + 1)]   # la compétition masquée (référence, vide au départ)
V_PLEIN = [f"kinitofplein{k}" for k in range(1, MASQUES + 1)]     # vrai : la case est remplie
V_ID = [f"kinitofid{k}" for k in range(1, MASQUES + 1)]           # UniqueId de sa compétition, 0 si vide
L_EGAL = [f"kinitoxegal{k}" for k in range(1, MASQUES + 1)]       # dans chaque ligne : la compétition du match = la case
SELECTION_COMP = "selectedfixturelistelement.Fixture.Competition"   # le match sélectionné (comme selectedfixture de FM)
ID_COMP = "binding.fixture.Competition.UniqueId"
# v20 : la compétition du match sélectionné est-elle déjà masquée ? (UniqueId de la sélection, 0 sans sélection, calculé
# comme les cases ; une égalité par case) : le bouton du bandeau se cache alors
V_IDSEL = "kinitofidsel"
V_SELEGAL = [f"kinitofselegal{k}" for k in range(1, MASQUES + 1)]
# v22 : le tableau rebranché après chaque geste du filtre (voir la docstring) : faux = débranché, un SIDelayEvent de FM le
# remet à vrai DELAI_RECHARGE secondes plus tard
V_AFFICHE = "kinitofaffiche"
DELAI_RECHARGE = 0.05
VISIBILITE_PLACE = 1   # SI.Bindable.VisibilityChangeType.VisibilityFlag (0 DisplayStyle, 2 Fade) : caché, garde sa place
NOM_RECHARGE = f"{PREFIXE}-rencontres-vues-recharge-v{VERSION}"   # préfixe « -rencontres-vues » : retiré par retirer_bloc
NOM_RECHARGE_DELAI = f"{PREFIXE}-rencontres-vues-recharge-delai"


def recharger():
    """v22 : le dernier événement de chaque geste du filtre (le tableau se débranche, puis se rebranche)"""
    return copier("const.False", V_AFFICHE)
TEXTE_TITRE_MASQUES = "Compétitions masquées"
TEXTE_MASQUER = "Masquer cette compétition"   # v20 : son texte (v19 : « Masquer la compétition du match sélectionné »)
TEXTE_REMETTRE = "Remettre"
TEXTE_AUCUNE = "Aucune. Sélectionne un match, puis « Masquer cette compétition »."
# v21 : la langue du jeu (recette 19, comme 26.18 kinito_fenetre_but, vue en jeu) : le conteneur de FM de
# tdd-messages-banner (bundle global) lit le réglage de langue ; son interrupteur compare un texte à
# languagesetting.PropertyValue (rang 1 = c'est elle, rang 0 = la suite)
SOURCE_LANGUE = "tdd-messages-banner"
FONCTION_LANGUE = "7980ef35a33c35e43940a2b7add470dd"
LANGUE_DEFAUT = "english"
LANGUES_JEU = ("english", "english (us)", "french", "german", "italian", "spanish", "spanish (latam)", "portuguese",
               "portuguese (bra)", "dutch", "danish", "norwegian", "swedish", "polish", "czech", "russian", "turkish",
               "greek", "indonesian", "japanese", "korean", "chinese", "chinese (traditional)", "thai", "arabic")
#               (les valeurs du réglage natif current_language, lues dans game_plugin.dll : 26.13 v24, v95)
MEMES = {"english (us)": "english", "spanish (latam)": "spanish", "portuguese (bra)": "portuguese",
         "czech": "english", "thai": "english", "chinese (traditional)": "chinese"}   # comme 26.13 v95 : absentes du
#        fichier de langues de FM 27 (tchèque, thaï, chinois traditionnel) ou partielles (espagnol d'Amérique latine)
# Nos quatre textes dans chaque langue du fichier de FM 27. Mots de FM recopiés de ce fichier (languages.fmf, lu par
# chantier-cartes-jeunes\outils\mots_fm_ids.mjs) : le verbe « masquer » de « Hide details » / « Hide loans »
# (0x100a6a0c, 0x1008825e), « Show » (0x10048d00, « Afficher »), « Hidden » (0x10053f07), « Competition »
# (0x100a28cb), « None » (0x10038553, « Aucune ») ; le reste par nous (FM n'a ni « Hide competition » ni « Unhide »),
# au vouvoiement quand FM vouvoie (allemand, turc, grec…) ; le français reste celui de Kinito. « ​ » : l'espace
# sans largeur que FM met dans ses textes japonais et chinois (où la ligne peut se couper).
TRADUCTIONS = {
    "masquer": {
        "english": "Hide this competition", "french": TEXTE_MASQUER, "german": "Diesen Wettbewerb ausblenden",
        "italian": "Nascondi questa competizione", "spanish": "Ocultar esta competición",
        "portuguese": "Ocultar esta competição", "dutch": "Deze competitie verbergen", "danish": "Skjul denne turnering",
        "norwegian": "Skjul denne turneringen", "swedish": "Dölj denna tävling", "polish": "Ukryj te rozgrywki",
        "russian": "Скрыть этот турнир", "turkish": "Bu turnuvayı gizle",
        "greek": "Απόκρυψη αυτής της διοργάνωσης", "indonesian": "Sembunyikan kompetisi ini",
        "japanese": "この大会を非表示", "korean": "이 대회 숨기기", "chinese": "隐藏此赛事", "arabic": "إخفاء هذه البطولة"},
    "titre_masques": {
        "english": "Hidden competitions", "french": TEXTE_TITRE_MASQUES, "german": "Ausgeblendete Wettbewerbe",
        "italian": "Competizioni nascoste", "spanish": "Competiciones ocultas", "portuguese": "Competições ocultas",
        "dutch": "Verborgen competities", "danish": "Skjulte turneringer", "norwegian": "Skjulte turneringer",
        "swedish": "Dolda tävlingar", "polish": "Ukryte rozgrywki", "russian": "Скрытые турниры",
        "turkish": "Gizlenen turnuvalar", "greek": "Κρυφές διοργανώσεις", "indonesian": "Kompetisi tersembunyi",
        "japanese": "非表示の大会", "korean": "숨긴 대회", "chinese": "已隐藏的赛事", "arabic": "البطولات المخفية"},
    "remettre": {
        "english": "Show", "french": TEXTE_REMETTRE, "german": "Einblenden", "italian": "Mostra", "spanish": "Mostrar",
        "portuguese": "Mostrar", "dutch": "Weergeven", "danish": "Vis", "norwegian": "Vis", "swedish": "Visa",
        "polish": "Pokaż", "russian": "Показать", "turkish": "Göster", "greek": "Εμφάνιση", "indonesian": "Tampilkan",
        "japanese": "再表示", "korean": "다시 표시", "chinese": "重新显示", "arabic": "إظهار"},
    "aucune": {
        "english": "None. Select a match, then “Hide this competition”.",
        "french": TEXTE_AUCUNE,
        "german": "Keine. Wählen Sie ein Spiel aus, dann „Diesen Wettbewerb ausblenden“.",
        "italian": "Nessuna. Seleziona una partita, poi «Nascondi questa competizione».",
        "spanish": "Ninguna. Selecciona un partido y luego «Ocultar esta competición».",
        "portuguese": "Nenhuma. Seleccione um jogo e depois «Ocultar esta competição».",
        "dutch": "Geen. Selecteer een wedstrijd en daarna “Deze competitie verbergen”.",
        "danish": "Ingen. Vælg en kamp og derefter »Skjul denne turnering«.",
        "norwegian": "Ingen. Velg en kamp og deretter «Skjul denne turneringen».",
        "swedish": "Inga. Välj en match och sedan ”Dölj denna tävling”.",
        "polish": "Brak. Wybierz mecz, a następnie „Ukryj te rozgrywki”.",
        "russian": "Нет. Выберите матч, затем «Скрыть этот турнир».",
        "turkish": "Yok. Bir maç seçin, ardından “Bu turnuvayı gizle”.",
        "greek": "Καμία. Επιλέξτε έναν αγώνα και μετά «Απόκρυψη αυτής της διοργάνωσης».",
        "indonesian": "Tidak ada. Pilih sebuah pertandingan, lalu “Sembunyikan kompetisi ini”.",
        "japanese": "なし。​試合を​選んでから​「この大会を非表示」を​押してください。",
        "korean": "없음. 경기를 선택한 후 '이 대회 숨기기'를 누르십시오.",
        "chinese": "无。​请选择​一场比赛，​然后点击​“隐藏此赛事”。",
        "arabic": "لا شيء. حدد مباراة، ثم «إخفاء هذه البطولة»."},
}


def texte_langue(cle, langue):
    """v21 : notre texte cle dans une langue du réglage de FM (LANGUES_JEU)"""
    return TRADUCTIONS[cle][MEMES.get(langue, langue)]


def _slug(langue):
    return "".join(c if c.isalnum() else "-" for c in langue).strip("-").replace("--", "-")
AMICAL = "binding.fixture.Competition.IsFriendly"
DOMICILE = ("binding.fixture.awayteam.UniqueId", "binding.fixture.TeamOpponent.UniqueId")   # le test de FM
# (NextFixtureCell : l'équipe qui se déplace = l'adversaire -> on joue à domicile), sans dépendre de la langue
CONDITIONS = [   # la ligne est cachée si UNE de ces conditions (ET de ses vrai/faux, (chemin, inversé)) est vraie
    ("amical", [(AMICAL, 0), (V_FHC, 1)]),                  # un amical, Hors compétition décoché
    ("domicile", [(L_DOM, 0), (V_FDOM, 1)]),                # à domicile, Domicile décoché
    ("exterieur", [(L_DOM, 1), (V_FEXT, 1)]),               # à l'extérieur, Extérieur décoché
] + [(f"masque{k + 1}", [(V_PLEIN[k], 0), (L_EGAL[k], 0)]) for k in range(MASQUES)]   # v19 : case remplie et égale
PANNEAU = "ClubSupportersConfidenceRow"   # gameworld, inutilisé : réécrit en contenu du panneau du filtre
GUID_PANNEAU = "b6ef021c86228fa40bc3cd737041d17c"
VUE_FILTRE = "SquadHierarchyManagerTable"   # v12 : ui-tableviews, citée par rien (vues_libres.py) : réécrite
GUID_VUE_FILTRE = "ea9a748b7dec7c64091df48551642985"
VUE_FILTRE_V6 = "ClubRivalriesTable"   # v6 à v11 : réécrite par ERREUR (FM la cite : ClubInfoReportBlock, tableaux
GUID_VUE_FILTRE_V6 = "c3b852c207c70e645adcad0eaaab3727"   # des rivaux) ; remise d'origine par appliquer et retirer
GUID_VUE_PORTAIL = "3a280eff0041cbd42a02cf328d097b1a"   # la vue de l'InitFunction du tableau du Portail (recopié)
FABRIQUE_COMPS = "ScoutingCompetitionTableFactory"   # fabrique de FM pour des lignes de compétitions (paramètre binding
GUID_FABRIQUE_COMPS = "971e4349f999b504dbbeb2f81e50bf32"   # de type compétition), lue seulement
COLONNE_COMP_FM = "competition"   # sa colonne logo + nom + pays (CompetitionWithLocationCell), lue seulement
# v12 (Kinito, 11/10 : « colonne de FM ») : la colonne de FM. v7 à v11 : « kinito-nom » (nom seul), AJOUTÉE à cette
# fabrique, qui sert aussi au recrutement (CustomPortalScoutingCompetitionCalendarNewsBlock) : remise d'origine
COLONNE_FILTRE = COLONNE_COMP_FM
SOURCE_WIDGET = "TacticsPlayerSelectionTableBlock"   # le bouton « Filtre ⌄ » des Tactiques (SIFloatingPopupWidget)
SOURCE_CASE = "inputs-switch-checkbox-default"     # la case à cocher de FM (SICheckBox)
SOURCE_OPTIONS = "TacticsPitchViewOptions"         # un libellé (SIText) et un bouton (SIButton) de FM
SOURCE_CALCUL = ("GoOnHolidayWidget", "BindingSetter")
FONCTIONS = {   # une fonction de FM recopiée de ce modèle, arguments réécrits
    "contient": ("ControllerRemapSettingsRow", "53435a45561e1754cba90ac41c45e5a7"),   # BindListContainsValueToDestination
    "aorb": ("LiveCupDrawButtons", "c4a44b7871191264db60b54fb75c714a"),   # BindAndSetAorBToDestinationOnIntComparison
    # v19 : BindAndSetAOrBToDestinationUsingReferenceIsNullAsBool (ValidateReference, PrimaryBinding, FallbackBinding,
    # Destination, ForceUpdate) : Primary, ou Fallback si la référence est vide ou n'existe pas (IsNullReference, jamais
    # de lecture d'une valeur vide) ; dans ViewedFixtureTooltip : Event.team.Club, const.true, const.false, isClub
    "nul": ("ViewedFixtureTooltip", "079b54afdf49eb242aba84c36407187b"),
}
# v12 : le SIVisible de FM dont la liaison est BindMultipleBooleanArgsToVisible (Show(vrai / faux), dans les deux sens) ;
# v6 à v11 : BindMultipleBooleanArgsToUSSClass (678bbaf2), dont la branche « faux » ne fait rien (classe jamais retirée)
SOURCE_VISIBLE_FN = ("PortalMessagesToolActionBar", "DividerVisible", "c829483f851514241b3346cd5118791b")
OU = 1   # SI.VisualScripting.VisibleFunctions+LogicOperator : And = 0, Or = 1 (relevé dans SI.Bindable.dll)
TEXTES = {   # un texte de FM recopié de ce modèle (n° de traduction ; anglais de FM entre parenthèses)
    "reinitialiser": ("ContractNegotiationTool", 5581),            # (Reset)
    "competitions": ("CompetitionsTile_2x1", 24516),               # (Competitions)
    "horscomp": ("CompCellNoBorderNonCompetitiveString", 34988),   # (Non Competitive)
    "lieu": ("UpcomingMatchBlock", 9818),                          # (Venue)
    "domicile": ("ArrangeFriendlyCompactBlock", 25515),            # (Home) : lieu d'un amical à organiser
    "exterieur": ("ArrangeFriendlyCompactBlock", 25516),           # (Away)
}
# v13 : 52 px, la hauteur que FM donne à la colonne « competition » (logo + nom + pays, deux lignes : ScoutingCompetition-
# Table de CustomPortalScoutingCompetitionCalendarNewsBlock) ; v7 à v12 : 32 px (le pays était coupé)
HAUTEUR_LIGNE_PANNEAU, LARGEUR_PANNEAU = 52, 280   # px
NOM_MASQUES = f"{PREFIXE}-rencontres-panneau-masques-v{VERSION}"   # v19 : la section des compétitions masquées
NOM_MASQUER = f"{PREFIXE}-rencontres-vues-masquer"   # v20 : le bouton du bandeau (préfixe « -rencontres-vues » :
                                                     # retiré par retirer_bloc, comme la zone du Filtre où il est)
NOM_FILTRE = f"{PREFIXE}-rencontres-vues-filtre"        # le bouton : préfixe « -rencontres-vues », retiré par retirer_bloc
NOM_ESPACE = f"{PREFIXE}-rencontres-vues-filtre-espace"
NOM_PANNEAU = f"{PREFIXE}-rencontres-panneau"
NOM_CALCUL = f"{PREFIXE}-rencontres-filtre-calcul-v{VERSION}"
NOM_INIT = f"{PREFIXE}-rencontres-vues-filtre-init"   # v7 : les calculs de départ (préfixe retiré par retirer_bloc)
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")


# ---------- petits outils ----------
def _texte(x):
    x = x.encode()
    return bytes([1, 1, len(x)]) + x


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _chemin(chemin):
    return b"\x01" + _enc_varint(len(chemin)) + chemin.encode()


def copier(source, destination):
    """contenu d'un événement « copier la valeur de <source> dans <destination> » (217,15,225,87)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])


def liste(contenus):
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def evenements_ok():
    """le format écrit ici = celui de FM, refait à l'octet près (copie de ClubNationInfoTabButton)"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return liste([copier("rowindex", "selected-tab")]) == attendu


def _parent_id(t, rid):
    p = t.parent[rid]
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(rid)["m_ParentId"])


def _nommer(t, rid, nom):
    t.sd(rid)["name"], t.sd(rid)["name_UxmlAttributeFlags"] = nom, 1


def _vider(t, rid):
    for k in list(t.children(rid)):
        t.remove(k)


def _deplacer(t, rid, parent, index=None):
    ancien = t.parent[rid]
    t.elem(ancien)["m_Children"] = [k for k in t.elem(ancien)["m_Children"] if k["rid"] != rid]
    enfants = t.elem(parent)["m_Children"]
    enfants.insert(len(enfants) if index is None else index, {"rid": rid})
    t.elem(rid)["m_Parent"] = {"rid": parent}
    t.parent[rid] = parent
    _parent_id(t, rid)


def _poser(d, cle, valeur):
    d[cle] = valeur
    d[cle + "_UxmlAttributeFlags"] = 1


def _remplacer_octets(x, avant, apres):
    """remplace une suite d'octets de même longueur dans toutes les listes m_argumentBytes d'une donnée"""
    assert len(avant) == len(apres)
    n = 0
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "m_argumentBytes" and isinstance(v, list):
                b = bytes(v)
                if avant in b:
                    x[k] = list(b.replace(avant, apres))
                    n += b.count(avant)
            else:
                n += _remplacer_octets(v, avant, apres)
    elif isinstance(x, list):
        for v in x:
            n += _remplacer_octets(v, avant, apres)
    return n


def mono(env, nom):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == nom:
                return o
        except Exception:
            continue
    return None


def guid_de(bundle, path_id):
    """le GUID (clé du catalogue) d'un objet d'un bundle"""
    for o in nb.env_of(bundle).objects:
        if o.type.name == "AssetBundle":
            for k, v in o.read_typetree()["m_Container"]:
                if v["asset"]["m_PathID"] == path_id:
                    return k
    return None


# ---------- les morceaux de FM ----------
class Sources:
    def __init__(self):
        def ouvre(m):
            o = ouvrir(m, depart_original=True)
            return o and o[3]
        self.tp = ouvre(SOURCE_TABLEAU)
        self.tableau = self.tp and first(self.tp, lambda r: typ(self.tp, r) == "StreamedTable" and (
            ((self.tp.sd(r).get("Binding") or {}).get("m_direct") or {}).get("Path") or {}).get("m_path") == DONNEES)
        self.tc = ouvre(SOURCE_CAPITAINES)
        self.menu = self.tc and first(self.tc, lambda r: self.tc.name(r) == "TableViewDropdown")
        self.tableau_cap = self.tc and first(self.tc, lambda r: self.tc.name(r) == "FilteredPlayersTable")
        self.ligne = self.tc and first(self.tc, lambda r: self.tc.name(r) == "Left" and typ(self.tc, r) == "VisualElement")
        self.decl_vue = None
        if self.tc:
            racine = self.tc.children(self.tc.tt["m_VisualTree"]["rid"])[0]
            for c in self.tc.sd(racine).get("m_components") or []:
                ref = self.tc.refs[c["rid"]]
                if "BindingVariablesComponent" in ref["type"]["class"]:
                    self.decl_vue = next((copy.deepcopy(v) for v in ref["data"].get("ReferenceVariables") or []
                                          if v.get("m_name") == "selectedView"), None)
        self.tg = ouvre(SOURCE_VARIABLES[0])
        self.variables = self.tg and first(self.tg, lambda r: self.tg.name(r) == SOURCE_VARIABLES[1]
                                           and typ(self.tg, r) == "BindingVariables")
        self.tv = ouvre(SOURCE_VISIBLE[0])
        self.visible = self.tv and first(self.tv, lambda r: self.tv.name(r) == SOURCE_VISIBLE[1]
                                         and typ(self.tv, r) == "SIVisible")
        self.reglages = None
        if self.tv:
            r = first(self.tv, lambda r: typ(self.tv, r) == "StreamedTable" and self.tv.sd(r).get("name") == SOURCE_REGLAGES[1])
            if r is not None and all(k in self.tv.sd(r) for k in REGLAGES):
                d = self.tv.sd(r)
                self.reglages = {}
                for k in REGLAGES:
                    self.reglages[k] = copy.deepcopy(d[k])
                    self.reglages[k + "_UxmlAttributeFlags"] = d.get(k + "_UxmlAttributeFlags", 1)
        self.td = ouvre(SOURCE_DELAI)
        self.delai = self.td and first(self.td, lambda r: self.td.elem(r).get("m_FullTypeName") == "FM.UI.SIDelayEvent"
                                       and not self.td.children(r))
        self.tj = ouvre(SOURCE_JOUE[0])
        self.joue = self.tj and first(self.tj, lambda r: self.tj.name(r) == SOURCE_JOUE[1] and typ(self.tj, r) == "SIVisible")
        # v4 : le titre du mois de la liste de FM (#ShowMonth > #Month), un VisualElement nu de FM
        for modele in (SOURCE_MOIS[0], SOURCE_MOIS_FMMAJ):   # v23 : FM du 2026-11-17 sans CalendarFixtureRow
            self.tr = ouvre(modele)
            self.mois = self.tr and first(self.tr, lambda r: self.tr.name(r) == SOURCE_MOIS[1]
                                          and typ(self.tr, r) == "SIVisible")
            texte = self.mois is not None and self.tr.children(self.mois)
            if not (texte and len(texte) == 1 and self.tr.name(texte[0]) == SOURCE_MOIS[2]
                    and typ(self.tr, texte[0]) == "SIText"):
                self.mois = None
            if self.mois is not None:
                break
        self.tl, self.element = None, None
        for modele, nom in SOURCES_ELEMENT:   # v17
            tl = ouvre(modele)
            el = tl and first(tl, lambda r, tl=tl, nom=nom: tl.name(r) == nom
                              and typ(tl, r) == "VisualElement" and not tl.children(r))
            if el is not None:
                self.tl, self.element = tl, el
                break
        # v6 : les morceaux du filtre
        self.tw = ouvre(SOURCE_WIDGET)
        self.widget = self.tw and first(self.tw, lambda r: typ(self.tw, r) == "SIFloatingPopupWidget")
        if self.widget is not None and [typ(self.tw, k) for k in self.tw.children(self.widget)] != ["SIText", "VisualElement"]:
            self.widget = None
        self.tk = ouvre(SOURCE_CASE)
        self.case = self.tk and first(self.tk, lambda r: typ(self.tk, r) == "SICheckBox")
        self.to = ouvre(SOURCE_OPTIONS)
        self.libelle = self.to and first(self.to, lambda r: typ(self.to, r) == "SIText")
        self.bouton = self.to and first(self.to, lambda r: typ(self.to, r) == "SIButton")
        self.tcalc = ouvre(SOURCE_CALCUL[0])
        self.calcul = self.tcalc and first(self.tcalc, lambda r: typ(self.tcalc, r) == SOURCE_CALCUL[1])
        self.fn = {cle: _fonction_source(m, g) for cle, (m, g) in FONCTIONS.items()}
        # v12 : la liaison (Binding, m_kind 2) d'un SIVisible de FM sur BindMultipleBooleanArgsToVisible
        self.vis_fn = None
        tvf = ouvre(SOURCE_VISIBLE_FN[0])
        if tvf:
            for r in tvf.walk():
                b = tvf.sd(r).get("Binding") if typ(tvf, r) == "SIVisible" and tvf.name(r) == SOURCE_VISIBLE_FN[1] else None
                if isinstance(b, dict) and b.get("m_kind") == 2 and _fn_guid(b.get("m_visualFunction")) == SOURCE_VISIBLE_FN[2]:
                    self.vis_fn = copy.deepcopy(b)
                    break
        # v12 : la cellule de date de FM (son BindingExpect, recopié dans CELLULE_DATE)
        self.tdate = ouvre(SOURCE_DATE)
        enfants = self.tdate and self.tdate.children(self.tdate.tt["m_VisualTree"]["rid"])
        self.date_be = enfants[0] if enfants and len(enfants) == 1 and typ(self.tdate, enfants[0]) == "BindingExpect" else None
        self.textes = {cle: _texte_source(m, n) for cle, (m, n) in TEXTES.items()}
        # v13 : la rangée de boutons d'équipes d'Alex (comme 26.2) et le bouton de FM qu'elle recopie
        self.mx = ee.Morceaux()
        ob = ouvrir(ee.BOUTON_SOURCE)
        self.bouton_equipe = ob and ob[3]
        # v21 : la langue du jeu (le conteneur de FM qui la lit, et son interrupteur « texte == langue »)
        self.tlg = ouvre(SOURCE_LANGUE)
        self.langue_env = self.langue_sw = None
        if self.tlg:
            tg = self.tlg
            self.langue_env = first(tg, lambda r: typ(tg, r) == "ComponentElement" and any(
                "languagesetting" in json.dumps((tg.refs.get(c["rid"]) or {}).get("data") or {})
                for c in tg.sd(r).get("m_components") or []))
            self.langue_sw = first(tg, lambda r: typ(tg, r) == "BindableSwitchElement" and _fn_guid(
                (tg.sd(r).get("Binding") or {}).get("m_visualFunction")) == FONCTION_LANGUE)
            if self.langue_env is not None:
                donnees = json.dumps([(tg.refs.get(c["rid"]) or {}).get("data")
                                      for c in tg.sd(self.langue_env).get("m_components") or []])
                if "current_language" not in donnees or "app.NativeSettings" not in donnees:
                    self.langue_env = None
            if self.langue_sw is not None:
                f = tg.sd(self.langue_sw)["Binding"]["m_visualFunction"]
                mots = [x for x in decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                        if bytes(x[0]).endswith(b"StringVisualArg")]
                if len(mots) != 1 or bytes(mots[0][1]) != bytes([1, 7]) + b"english":
                    self.langue_sw = None

    def manque(self):
        noms = {"tableau du Portail": self.tableau, "menu des vues des capitaines": self.menu,
                "tableau des capitaines": self.tableau_cap, "rangée #Left des capitaines": self.ligne,
                "déclaration selectedView": self.decl_vue, "BindingVariables de FM": self.variables,
                "SIVisible de FM": self.visible, "réglages de la Base de données": self.reglages,
                "SIDelayEvent de FM": self.delai, "#AttendanceVisible de FM": self.joue,
                "titre du mois de la liste de FM": self.mois, "VisualElement nu de FM": self.element,
                "bouton Filtre des Tactiques": self.widget, "case à cocher de FM": self.case,
                "libellé de FM": self.libelle, "bouton de FM": self.bouton, "BindingSetter de FM": self.calcul,
                "SIVisible à vrai/faux multiples de FM": self.vis_fn, f"cellule {SOURCE_DATE}": self.date_be}
        noms.update({f"fonction {k} de FM": v for k, v in self.fn.items()})
        noms.update({f"texte {k} de FM": v for k, v in self.textes.items()})
        noms.update({"rangée d'équipes d'Alex": self.mx if self.mx.ok() else None,
                     "bouton d'équipe de FM": self.bouton_equipe})   # v13
        noms.update({"conteneur de langue de FM (tdd-messages-banner)": self.langue_env,   # v21
                     "interrupteur de langue de FM (tdd-messages-banner)": self.langue_sw})
        out = [n for n, v in noms.items() if v is None]
        if any(MEMES.get(lg, lg) not in TRADUCTIONS[c] for c in TRADUCTIONS for lg in LANGUES_JEU) \
                or any(texte_langue("masquer", lg) not in texte_langue("aucune", lg) for lg in LANGUES_JEU):
            out.append("traductions incomplètes (v21)")
        if not evenements_ok():
            out.append("format des événements")
        if not ee._verifier_evenement() or not evenement_ia_ok():   # v13
            out.append("format de l'événement « programme d'un club IA »")
        return out


def _corps(e):
    """le contenu d'un événement (sans l'enveloppe de liste : 5 octets, longueur, … , 0 final)"""
    e = bytes(e)
    n = struct.unpack_from("<i", e, 5)[0]
    return e[9:9 + n]


def evenement_ia_ok():
    """v13 : l'événement écrit pour un bouton d'équipe IA = la branche « équipe IA » de l'événement des flèches ^ v de FM
    (bloc d'origine), refaite à l'octet près ; FM range ses deux branches sans le type d'action (4 octets), que porte un
    événement seul (celui de 26.2, validé en jeu, l'a aussi)"""
    o = ouvrir(BLOC, depart_original=True)
    if not o:
        return False
    nous = _corps(ee.evenement_ecran(OUTIL_IA, [(n, VAR_FLECHE if n == "team" else c) for n, c in PARAMS_IA]))
    humain = _corps(ee.evenement_ecran(OUTIL_HUMAIN, [("calendartab", "const.Two"), ("team", VAR_FLECHE)]))
    for r in o[3].tt["references"]["RefIds"]:
        ev = ((r or {}).get("data") or {}).get("Events")
        b = bytes(ev.get("m_bytes") or []) if isinstance(ev, dict) else b""
        if OUTIL_IA.encode() in b and nous[4:] in b and humain[4:] in b and nous[:4] == humain[:4]:
            return True
    return False


# ---------- le bloc (partagé avec 26.2 : nos morceaux seulement) ----------
def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(f"{PREFIXE}-rencontres-")]


def bloc_a_jour(t):
    noms = {t.name(r) for r in t.walk()}
    return {NOM_CACHE, NOM_VUES, NOM_TABLEAU, NOM_MENU, NOM_DELAI, NOM_FILTRE, NOM_INIT, NOM_MONTRE, NOM_ZONE_FILTRE,
            NOM_EQUIPES_IA,   # v13 : la rangée IA (nom versionné : un bloc v12 n'est pas à jour)
            f"{NOM_MASQUER}-bouton-1-langue-v{VERSION}",   # v21 : le bouton du bandeau dans la langue du jeu
            NOM_RECHARGE, NOM_RECHARGE_DELAI} <= noms   # v22 : le tableau rebranché après chaque geste du filtre


def _visible(t, src, parent, chemin, inverse, nom, index=None, toujours=0):
    v = t.clone(src.visible, parent, index, src=src.tv)
    _vider(t, v)
    _parent_id(t, v)
    _nommer(t, v, nom)
    sd = t.sd(v)
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    _poser(sd, "InvertDirectBinding", 1 if inverse else 0)
    _poser(sd, "AlwaysInstantiate", toujours)
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    return v


def _visible_fn(t, src, parent, termes, operateur, nom, index=None, toujours=0, classes=()):
    """v12 : un SIVisible de FM sur BindMultipleBooleanArgsToVisible (montre si les termes (chemin, inversé) combinés
    par l'opérateur, ET = 0 / OU = 1, sont vrais ; Show(vrai / faux) : montre ET cache) ; le SIVisible, ou un texte
    d'erreur"""
    v = t.clone(src.visible, parent, index, src=src.tv)
    _vider(t, v)
    _parent_id(t, v)
    _nommer(t, v, nom)
    sd = t.sd(v)
    b = copy.deepcopy(src.vis_fn)
    if not _args(b["m_visualFunction"], [ARG_BOOLEENS, ARG_LOGIQUE], [_booleens(termes), struct.pack("<i", operateur)]):
        return "fonction « vrai/faux multiples vers visible » de FM : arguments inattendus"
    sd["Binding"] = b
    sd["Binding_UxmlAttributeFlags"] = 1
    _poser(sd, "InvertDirectBinding", 0)
    _poser(sd, "AlwaysInstantiate", toujours)
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = list(classes), -1
    return v


def construire_bloc(t, src):
    fixtures = first(t, lambda r: t.name(r) == "Fixtures" and typ(t, r) == "VisualElement")
    liste_fm = first(t, lambda r: t.name(r) == "FixturesList" and typ(t, r) == "StreamedObjectList")
    if liste_fm is None:   # v23 : FM du 2026-11-17, la liste est devenue un tableau de FM (#FixturesTable), seul enfant
        liste_fm = first(t, lambda r: t.name(r) == "FixturesTable" and typ(t, r) == "StreamedTable")
    if fixtures is None or liste_fm is None or t.parent.get(liste_fm) != fixtures:
        return ["liste du programme (#Fixtures > #FixturesList / #FixturesTable) introuvable"]
    enfants = t.children(fixtures)
    if enfants == [liste_fm]:
        entete_fm = None   # v23 : le tableau de FM a son en-tête de colonnes
    elif len(enfants) != 2 or enfants[1] != liste_fm or typ(t, enfants[0]) != "BindableSwitchElement":
        return ["contenu de #Fixtures inattendu (en-tête + liste attendus)"]
    else:
        entete_fm = enfants[0]
    # 1. l'en-tête et la liste de FM, intacts : montrés quand NOS morceaux ne le sont pas : v13, en petit format (fiche
    # de club dans un match, petite fenêtre) ; v12 : aussi pour le programme d'un autre club ; v1 à v11 : toujours cachés
    cache = _visible_fn(t, src, fixtures, [(PETIT, 0)], 0, NOM_CACHE, index=0, classes=["base-template-grow"])
    if isinstance(cache, str):
        return [cache]
    t.styles.style(t, cache, {"flex-direction": "column"})
    if entete_fm is not None:
        _deplacer(t, entete_fm, cache)
    _deplacer(t, liste_fm, cache)
    # 2. nos morceaux : dans un SIVisible montré hors petit format (jamais instancié ailleurs) : v13, pour toute équipe
    # (Kinito : « appliquer notre tableau aux programmes des clubs IA ») ; v12 : équipe du club du joueur seulement ;
    # puis un BindingVariables de FM (la vue choisie, VUES_PRETES)
    montre = _visible_fn(t, src, fixtures, [(PETIT, 1)], 0, NOM_MONTRE, classes=["base-template-grow"])
    if isinstance(montre, str):
        return [montre]
    t.styles.style(t, montre, {"flex-direction": "column"})
    bv = t.clone(src.variables, montre, src=src.tg)
    _vider(t, bv)
    _parent_id(t, bv)
    _nommer(t, bv, NOM_VUES)
    t.elem(bv)["m_Classes"], t.elem(bv)["m_RuleIndex"] = ["base-template-grow"], -1
    d = t.sd(bv)
    # v15 : la vue choisie et VUES_PRETES déclarées à la racine du bloc (vues du menu, maintenant dans l'en-tête, et du
    # tableau) : voir plus bas ; ce BindingVariables n'en déclare plus
    _poser(d, "ReferenceVariables", [])
    _poser(d, "ValueVariables", [])
    # 2a. la rangée du menu des vues (au-dessus du tableau)
    rangee = t.clone(src.ligne, bv, src=src.tc)
    _vider(t, rangee)
    _parent_id(t, rangee)
    _nommer(t, rangee, NOM_ENTETE)
    t.elem(rangee)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-regular"]
    t.elem(rangee)["m_RuleIndex"] = -1
    env = _visible(t, src, rangee, VUES_PRETES, False, f"{PREFIXE}-rencontres-menu-pret", toujours=1)
    menu = t.clone(src.menu, env, src=src.tc)
    t.styles.copy_from(src.tc.styles, t, menu)
    elements.copy_usings(t, src.tc, src.menu)
    _parent_id(t, menu)
    _nommer(t, menu, NOM_MENU)
    t.elem(menu)["m_Classes"] = []
    n = 0
    for c in t.closure(menu):
        n += _remplacer_octets(t.refs[c].get("data") or {}, GUID_COLLECTION_CAPITAINES.encode(), GUID_COLLECTION.encode())
    if n != 1:
        return [f"menu des vues : {n} référence(s) à la collection remplacée(s) (1 attendue)"]
    # 2b. le tableau (copie de celui du Portail) avec les réglages de la Base de données
    tab = t.clone(src.tableau, bv, src=src.tp)
    t.styles.copy_from(src.tp.styles, t, tab)
    _parent_id(t, tab)
    _nommer(t, tab, NOM_TABLEAU)
    t.elem(tab)["m_Classes"] = ["base-template-grow", "margin-bottom-global-gap-extra-large"]
    sd = t.sd(tab)
    if (sd.get("FactoryAsset") or {}).get("m_AssetGUID") != GUID_FABRIQUE:
        return ["tableau du Portail : fabrique inattendue"]
    sd["FactoryAsset"]["m_AssetGUID"] = GUID_FABRIQUE_TABLEAU   # v12 : notre fabrique (copie de celle de FM + nos colonnes)
    sd.update(copy.deepcopy(src.reglages))
    init = copy.deepcopy(src.tc.sd(src.tableau_cap)["InitFunction"])
    args = decode_args(init["m_inputs"]["m_variable"]["m_argumentBytes"])
    guids = [a for a in args if GUID_COLLECTION_CAPITAINES.encode() in bytes(a[1])]
    vues = [a for a in args if bytes(a[1]) == _chemin("selectedView")]
    if len(guids) != 1 or len(vues) != 1:
        return ["InitFunction du tableau des capitaines : arguments inattendus"]
    guids[0][1] = bytes(guids[0][1]).replace(GUID_COLLECTION_CAPITAINES.encode(), GUID_COLLECTION.encode())
    vues[0][1] = _chemin(V_VUE)
    init["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    _poser(sd, "InitFunction", init)
    _poser(sd, "SelectedItemsBinding", {"m_path": SELECTION})
    _poser(sd, "SelectionMode", MODE_SELECTION)        # v3 : le tableau du Portail n'accepte aucune sélection (0)
    _poser(sd, "SelectionCellID", COLONNE_SELECTION)   # v5 : notre colonne de sélection à 0 px, pas le rond de FM
    _poser(sd, "ScrollToElementBinding", {"m_path": DEFILER})
    _poser(sd, "SetScrollToAsSelected", 1)             # v3 : le prochain match, sélectionné à l'ouverture (liste de FM)
    # v4 : notre modèle de ligne (bandeau du mois + zone des cellules) ; lignes de hauteur variable, comme TeamSquadBlock
    _poser(sd, "RowElementAsset", {"m_AssetGUID": GUID_LIGNE, "m_SubObjectName": "", "m_SubObjectType": ""})
    _poser(sd, "DynamicElements", 1)
    _poser(sd, "FixedElementSize", 0.0)
    _poser(sd, "EstimatedElementSize", float(HAUTEUR_LIGNE))
    _poser(sd, "DisableSorting", 1)   # les colonnes de la fabrique n'ont pas de tri
    # v12 : pas de zébrage (réglage par défaut de FM ; le tableau du Portail recopié le met à 1). Une ligne cachée garde
    # 1 px (construire_ligne) : zébrée, la ligne impaire y laissait un trait (--data-tables-background-odd, blanc 6 %)
    _poser(sd, "AlternateRows", 0)
    # v22 : le tableau dans un SIVisible de FM sur V_AFFICHE (caché : FM le débranche ; remontré : il le rebranche, et le
    # tableau oublie les hauteurs qu'il avait mémorisées), en VisibilityFlag (il garde sa place) ; puis, montrée quand
    # V_AFFICHE est faux, la zone dont le SIDelayEvent de FM le remet à vrai
    rech = _visible(t, src, bv, V_AFFICHE, False, NOM_RECHARGE, index=t.children(bv).index(tab), toujours=1)
    t.elem(rech)["m_Classes"] = ["base-template-grow"]
    t.styles.style(t, rech, {"flex-direction": "column"})
    dr = t.sd(rech)
    if "VisibilityType" not in dr or dr.get("AlwaysBindChildren"):
        return ["SIVisible de FM : VisibilityType absent ou AlwaysBindChildren allumé (inattendu)"]
    _poser(dr, "VisibilityType", VISIBILITE_PLACE)
    _deplacer(t, tab, rech)
    zone = _visible(t, src, bv, V_AFFICHE, True, NOM_RECHARGE_DELAI)
    t.styles.style(t, zone, {"position": "absolute", "width": 0, "height": 0})
    mr = t.clone(src.delai, zone, src=src.td)
    _parent_id(t, mr)
    _nommer(t, mr, NOM_RECHARGE_DELAI + "-minuteur")
    t.elem(mr)["m_Classes"], t.elem(mr)["m_RuleIndex"] = [], -1
    t.styles.style(t, mr, {"position": "absolute", "width": 0, "height": 0})
    _poser(t.sd(mr), "m_duration", float(DELAI_RECHARGE))
    _poser(t.sd(mr), "TransitionEvents", {"m_bytes": liste([copier("const.True", V_AFFICHE)])})
    # 2c. le délai : VUES_PRETES passe à vrai, le menu des vues se relie après le tableau
    dl = t.clone(src.delai, bv, src=src.td)
    _parent_id(t, dl)
    _nommer(t, dl, NOM_DELAI)
    t.elem(dl)["m_Classes"], t.elem(dl)["m_RuleIndex"] = [], -1
    t.styles.style(t, dl, {"position": "absolute", "width": 0, "height": 0})
    dd = t.sd(dl)
    _poser(dd, "m_duration", float(DELAI))
    _poser(dd, "TransitionEvents", {"m_bytes": liste([copier("const.True", VUES_PRETES)])})
    pb = (filtre_bloc(t, src) or equipes_ia(t, src) or menu_a_cote_du_filtre(t, src, env, rangee)   # v6 ; v13 ; v15
          or masquer_dans_le_bandeau(t, src))   # v20
    if pb:
        return [pb]
    return [f"bouton « Filtre » dans l'en-tête, variables du filtre à la racine du bloc",
            f"tableau FM à la place de la liste ({DONNEES}, fabrique des matchs, vues de {COLLECTION}), menu des vues "
            f"relié {DELAI} s après, pour toute équipe hors petit format ; en-tête et liste de FM intacts, montrés en "
            f"petit format (fiche de club dans un match)",
            f"boutons des équipes d'un club IA ({EQUIPES_IA['liste']}, clic = son programme) à côté de ceux de 26.2"]


def menu_a_cote_du_filtre(t, src, env, rangee):
    """v15 (demande d'Alex, 11/10) : le menu des vues (« 👁 Programme des rencontres ⌄ ») passe de sous le nom de
    l'équipe à l'en-tête, juste à gauche du bouton Filtre ; sa rangée (vide) est retirée. Le menu et le tableau ne sont
    plus dans le même BindingVariables : la vue choisie (V_VUE, nom lu en dur par TableViewDropdown) et VUES_PRETES
    sont déclarées à la racine du bloc (comme les variables du filtre ; aucune variable de ce nom à l'origine).
    None ou un texte d'erreur"""
    filtre = first(t, lambda r: t.name(r) == NOM_FILTRE)
    zone = filtre is not None and t.parent.get(filtre)
    if not zone or t.name(zone) != NOM_ZONE_FILTRE:
        return "bouton Filtre introuvable dans sa zone (inattendu)"
    _deplacer(t, env, zone, t.children(zone).index(filtre))
    # v16 : plafonné (au-delà, le texte de FM se coupe en « … ») ; la zone ne se tasse plus : le menu s'étend vers la
    # gauche, dans le vide de la rangée d'équipes de 26.2, et Filtre reste au bord droit
    t.styles.style(t, env, {"align-self": "center", "margin-right": ECART_MENU, **sm.LARGEUR_MAX(LARGEUR_MAX_MENU)})
    t.styles.style(t, zone, {"flex-shrink": 0})
    t.remove(rangee)
    d = _composant_racine(t)
    decl = copy.deepcopy(src.decl_vue)
    decl["m_name"] = V_VUE
    d.setdefault("ReferenceVariables", []).append(decl)
    d.setdefault("ValueVariables", []).append({"m_name": VUES_PRETES, "m_scopeValue": {"m_serializedData": "Bool|0|"}})
    d["ValueVariables_UxmlAttributeFlags"] = d["ReferenceVariables_UxmlAttributeFlags"] = 1
    return None


def masquer_dans_le_bandeau(t, src):
    """v20 (Kinito, 13/11 : « Vues - Masquer la compétition - Filtre ») : le bouton « Masquer cette compétition » dans la
    zone du Filtre, juste avant lui (donc après le menu des vues). Un seul bouton visible : MASQUES SIVisible (ET : les
    cases d'avant remplies, la sienne vide), chacun copie la compétition du match sélectionné dans SA case ; le tout dans
    MASQUES enveloppes (OU : case vide, ou pas la compétition sélectionnée) qui le cachent si elle est déjà masquée. Plus
    rien quand les cases sont pleines. SIVisible de FM sans AlwaysInstantiate. None ou un texte d'erreur"""
    filtre = first(t, lambda r: t.name(r) == NOM_FILTRE)
    zone = filtre is not None and t.parent.get(filtre)
    if not zone or t.name(zone) != NOM_ZONE_FILTRE:
        return "bouton Filtre introuvable dans sa zone (inattendu)"
    grp = t.clone(src.element, zone, t.children(zone).index(filtre), src=src.tl)
    _parent_id(t, grp)
    _nommer(t, grp, NOM_MASQUER)
    t.elem(grp)["m_Classes"], t.elem(grp)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    t.styles.style(t, grp, {"align-self": "center", "flex-shrink": 0, "margin-right": ECART_MENU})
    parent = grp
    for j in range(MASQUES):
        w = _visible_fn(t, src, parent, [(V_PLEIN[j], 1), (V_SELEGAL[j], 1)], OU, f"{NOM_MASQUER}-deja-{j + 1}")
        if isinstance(w, str):
            return w
        t.styles.style(t, w, {"flex-direction": "row", "align-items": "center"})
        parent = w
    for k in range(MASQUES):
        v = _visible_fn(t, src, parent, [(V_PLEIN[i], 0) for i in range(k)] + [(V_PLEIN[k], 1)], 0,
                        f"{NOM_MASQUER}-case-{k + 1}")
        if isinstance(v, str):
            return v
        # v21 : le bouton dans la langue du jeu
        _bouton_langue(t, src, v, f"{NOM_MASQUER}-bouton-{k + 1}", "masquer",
                       [copier(SELECTION_COMP, V_MASQUE[k]), recharger()])   # v22 : puis le tableau rebranché
    return None


def equipes_ia(t, src):
    """v13 : dans le bandeau (celui des boutons de 26.2), une rangée de boutons d'équipes pour une équipe qui n'est pas du
    club du joueur, hors petit format : la rangée d'Alex (entrainement_equipes.rangee, comme 26.2) dans un SIVisible de FM
    (NON V_HUMAIN et NON PETIT), sur team.Club.Teams, boutons = CELLULE_IA ; None ou un texte d'erreur"""
    bandeau = first(t, lambda r: any(t.elem(k).get("m_TemplateAlias") == "QuickFlick" for k in t.children(r)))
    if bandeau is None:
        return "bandeau du programme (flèches QuickFlick) introuvable"
    # v14 : juste AVANT la zone du bouton Filtre (qui s'étire et pousse Filtre au bout), donc juste après la rangée de
    # 26.2, comme sur le programme du club du joueur ; en v13, à la fin du bandeau : relevé en jeu (capture du 11/10,
    # Laval MFC U19), Filtre restait au milieu, collé à gauche des boutons
    filtre = first(t, lambda r: t.name(r) == NOM_ZONE_FILTRE)
    if filtre is None or t.parent.get(filtre) != bandeau:
        return "zone du bouton Filtre introuvable dans le bandeau (inattendu)"
    zone = _visible_fn(t, src, bandeau, [(V_HUMAIN, 1), (PETIT, 1)], 0, NOM_EQUIPES_IA,
                       index=t.children(bandeau).index(filtre))
    if isinstance(zone, str):
        return zone
    # la place de la rangée de 26.2 (la même : portée par le SIVisible, comme le SIVisible « même club » de 26.2)
    t.styles.style(t, zone, {"height": EQUIPES_IA["hauteur"], "margin-left": EQUIPES_IA["marge"],
                             "top": EQUIPES_IA["descendre"], "width": EQUIPES_IA["largeur"], "flex-shrink": 1,
                             "min-width": 0})
    c = ee.rangee(t, src.mx, zone, None, EQUIPES_IA)
    # comme la rangée « même club » de 26.2 : le BindingRemapper ne donne que l'équipe affichée et prend toute la place
    sd = t.sd(c)
    sd["Mappings"] = [m for m in sd["Mappings"] if m.get("from") == ee.PARAM_EQUIPE]
    t.elem(c)["m_RuleIndex"] = -1
    t.styles.style(t, c, {"flex-grow": 1})
    for r in t.walk(c):
        if t.name(r).startswith(ee.PREFIXE):
            t.sd(r)["name"] = f"{PREFIXE}-rencontres-equipes-ia-remap" if r == c else f"{PREFIXE}-rencontres-equipes-ia-liste"
    listes = [r for r in t.walk(c) if t.sd(r).get("RowTemplate")]
    if len(sd["Mappings"]) != 1 or len(listes) != 1:
        return "rangée des équipes d'Alex : contenu inattendu"
    t.sd(listes[0])["RowTemplate"]["m_AssetGUID"] = GUID_CELLULE_IA
    return None


def retirer_bloc(o):
    """retire nos morceaux, remet l'en-tête et la liste de FM à leur place, et les règles de style devenues inutiles"""
    bundle, obj, tt, t = o
    for r in [r for r in marques(t) if t.name(r).startswith(f"{PREFIXE}-rencontres-vues")]:
        if r in t.refs:   # v12 : nos morceaux s'emboîtent (zone du filtre > bouton) : déjà parti avec son parent
            t.remove(r)
    retirer_variables_filtre(t)   # v6
    cache = first(t, lambda r: t.name(r) == NOM_CACHE)
    if cache is not None:
        p = t.parent[cache]
        i = t.children(p).index(cache)
        for k, enfant in enumerate(list(t.children(cache))):
            _deplacer(t, enfant, p, i + k)
        t.remove(cache)
    # le modèle inclus TableViewDropdown : retiré s'il n'est plus utilisé et que l'original ne l'avait pas
    orig = hp.original(bundle, obj)
    alias_orig = {u.get("alias") for u in (orig or {}).get("m_Usings") or []}
    utilises = {t.elem(r).get("m_TemplateAlias") for r in t.walk()}
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") in alias_orig or u.get("alias") in utilises]
    feuille = orig and hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is None:
        return
    n0 = len(feuille["m_Rules"])
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    if not any(i >= n0 for i in utilisees):
        t.styles.sh, t.styles.changed = feuille, True
        return
    regles = t.styles.sh["m_Rules"]
    garder = list(range(n0)) + [i for i in range(n0, len(regles)) if i in utilisees]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    _tables_sans_valeurs_inutiles(t.styles.sh, feuille)
    t.styles.changed = True


TABLES_VALEURS = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}   # comme arbre.py


def _tables_sans_valeurs_inutiles(sh, feuille):
    """après le retrait des règles : les valeurs ajoutées en fin de table (au-delà de l'original) qu'aucune règle
    n'utilise plus sont retirées (ex. « absolute » du délai) — la feuille redevient identique à ce qu'elle était"""
    utilisees = {}
    for regle in sh["m_Rules"]:
        for p in regle["m_Properties"]:
            for v in p["m_Values"]:
                table = TABLES_VALEURS.get(v["m_ValueType"])
                if table:
                    utilisees.setdefault(table, set()).add(v["valueIndex"])
    for table in set(TABLES_VALEURS.values()):
        valeurs = sh.get(table)
        if not isinstance(valeurs, list):
            continue
        n0 = len(feuille.get(table) or [])
        while len(valeurs) > n0 and (len(valeurs) - 1) not in utilisees.get(table, set()):
            valeurs.pop()


# ---------- la cellule des spectateurs (LiveTablePtsCell, seul propriétaire) ----------
def cellule_a_jour(t):
    return any(t.name(r) == NOM_JOUE for r in t.walk())


def construire_cellule(t, src):
    be = first(t, lambda r: typ(t, r) == "BindingExpect")
    texte = first(t, lambda r: typ(t, r) == "SIText")
    if be is None or texte is None:
        return "cellule : BindingExpect ou texte introuvable"
    params = t.sd(be).get("Parameters") or []
    if len(params) != 1 or params[0].get("name") != "binding":
        return "cellule : paramètre « binding » inattendu"
    params[0]["type"]["id"] = 1718188148   # FixtureReference, comme VenueCell / FixtureResultCell
    tb = t.sd(texte).get("TextBinding") or {}
    if (((tb.get("m_direct") or {}).get("Path") or {}).get("m_path")) != "binding.LeaguePoints":
        return "cellule : texte inattendu"
    tb["m_direct"]["Path"]["m_path"] = "binding.Attendance"
    t.elem(texte)["m_Classes"] = ["body-sm", "global-text-primary"]
    parent = t.parent[texte]
    v = t.clone(src.joue, parent, t.children(parent).index(texte), src=src.tj)
    _vider(t, v)
    _parent_id(t, v)
    _nommer(t, v, NOM_JOUE)
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    t.sd(v)["Binding"]["m_direct"]["Path"]["m_path"] = "binding.HasResult"
    _deplacer(t, texte, v)
    return None


# ---------- v12 : la cellule de la date (EventCell, seul propriétaire) ----------
NOM_DATE = f"{PREFIXE}-rencontres-date"


def cellule_date_a_jour(t):
    return any(t.name(r) == NOM_DATE for r in t.walk())


def construire_cellule_date(t, src):
    """le contenu de la cellule de FM DateCell_BreakpointDependent (BindingExpect, paramètre « value » ; date valide /
    « - »), sans son choix selon la taille d'écran : son texte « [abbr_day] [date_short_month_year] » (TRAD_DATE_JOUR)
    toujours, celui en « [%date#1-long] » retiré"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    be = t.clone(src.date_be, racine, src=src.tdate)
    t.styles.copy_from(src.tdate.styles, t, be)
    _parent_id(t, be)
    _nommer(t, be, NOM_DATE)
    t.tt["m_Usings"] = []
    elements.copy_usings(t, src.tdate, src.date_be)
    visibles = [r for r in t.walk() if typ(t, r) == "SIVisible"]
    garde = []
    for v in visibles:
        textes = [k for k in t.children(v) if typ(t, k) == "SIText"]
        tb = (t.sd(textes[0]).get("TextBinding") or {}) if len(textes) == 1 else {}
        args = decode_args(((tb.get("m_visualFunction") or {}).get("m_inputs") or {}).get("m_variable", {})
                           .get("m_argumentBytes") or [])
        trad = next((struct.unpack("<i", bytes(a[1])[:4])[0] for a in args if b"TranslationID" in bytes(a[0])), None)
        garde.append((v, textes, trad))
    if sorted(tr for _, _, tr in garde) != sorted([9807, TRAD_DATE_JOUR]):
        return f"cellule {SOURCE_DATE} : textes inattendus ({[tr for _, _, tr in garde]})"
    for v, textes, trad in garde:
        if trad == TRAD_DATE_JOUR:
            p = t.parent[v]
            _deplacer(t, textes[0], p, t.children(p).index(v))
        t.remove(v)
    return None


# ---------- v13 : le bouton d'équipe d'un club IA (CELLULE_IA, seul propriétaire) ----------
def cellule_ia_a_jour(t):
    return any(t.name(r) == NOM_CELLULE_IA for r in t.walk())


def cellule_ia_modifiee(t):
    return any(t.name(r).startswith(PREFIXE) for r in t.walk())


def construire_cellule_ia(t, src):
    """le bouton d'équipe de la rangée d'Alex (ee.construire_bouton, comme la cellule de 26.2 : nom et équipe affichée
    surlignée) ; clic = le programme de cette équipe (FixturesAIClubTool, paramètres de FM) ; textes non cliquables
    (26.2 v4 : sinon une petite fenêtre vide au clic)"""
    msgs = ee.construire_bouton(t, src.bouton_equipe)
    if any("introuvable" in m for m in msgs):
        return f"bouton d'équipe : {msgs[0]}"
    c = t.children(t.tt["m_VisualTree"]["rid"])[0]
    t.sd(c)["name"] = NOM_CELLULE_IA
    ev = ee.evenement_ecran(OUTIL_IA, PARAMS_IA)
    boutons = [r for r in t.walk(c) if typ(t, r) == "SIButton"]
    if not boutons:
        return "bouton d'équipe : boutons du modèle FM introuvables"
    for r in boutons:
        t.sd(r)["Events"]["m_bytes"] = list(ev)
    for r in t.walk(c):
        if typ(t, r) == "SIText":
            t.sd(r)["pickingMode"], t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1, 1
    # les modèles inclus de la cellule de FM qui ne servent plus (ArrowStateIcon)
    utilises = {t.elem(r).get("m_TemplateAlias") for r in t.walk()}
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") in utilises]
    return None


# ---------- v12 : les vues (ui-tableviews, seul propriétaire de chacune) ----------
def vue_colonnes(tt):
    return [c.get("m_columnID") for c in (tt.get("m_tableView") or {}).get("m_tableConfig") or []]


def vue_modifiee(objet):
    """la vue diffère de son original sauvegardé (une de nos versions)"""
    orig = hp.original(VUES, objet)
    return orig is not None and objet.read_typetree() != orig


def construire_vue(tt, squelette, modele_colonne, colonnes):
    """la vue : la vue du Portail comme squelette (aucune condition ni attente de liaison), nos colonnes, chacune avec
    les réglages de la colonne « date » du Portail, sur toutes les tailles d'écran et sans priorité (jamais sautée)"""
    tt["m_tableView"] = copy.deepcopy(squelette)
    config = []
    for col in colonnes:
        e = copy.deepcopy(modele_colonne)
        e["m_columnID"] = col
        e["m_columnMetadata"]["m_priority"] = 0
        e["m_columnMetadata"]["m_applicableBreakpoints"] = -1
        if "m_growWeight" in e["m_columnMetadata"]:   # v24 : FM du 2026-11-17 (0 = la colonne ne s'élargit pas)
            e["m_columnMetadata"]["m_growWeight"] = float(GRANDIT.get(col, 0.0))
        config.append(e)
    tt["m_tableView"]["m_tableConfig"] = config


def vue_a_jour(tt):
    """v24 : nos colonnes, et leur part de la place libre (m_growWeight) si FM l'a"""
    cfg = (tt.get("m_tableView") or {}).get("m_tableConfig") or []
    return vue_colonnes(tt) == COLONNES_VUE and all(
        (c.get("m_columnMetadata") or {}).get("m_growWeight", GRANDIT.get(c["m_columnID"], 0.0))
        == GRANDIT.get(c["m_columnID"], 0.0) for c in cfg)


# ---------- le modèle de ligne (BulletTextRow, seul propriétaire, v4) ----------
def ligne_a_jour(t):
    """v6 : le calcul du filtre en plus (une ligne v4 / v5 a le bandeau mais pas le filtre : ANCIENNE version)"""
    noms = {t.name(r) for r in t.walk()}
    return {NOM_LIGNE, NOM_CALCUL} <= noms and bool(t.tt.get("m_ContentContainerId"))


def ligne_modifiee(t):
    """notre modèle de ligne, même incomplet (pour le retirer)"""
    return any(t.name(r).startswith(f"{PREFIXE}-rencontres-") for r in t.walk())


def construire_ligne(t, src):
    """BulletTextRow réécrit : son BindingExpect (paramètre binding = un élément de team.FixtureListElements), en
    colonne > le bandeau du mois (SIVisible sur binding.isfirstfixtureofthemonth > trait de FM + texte du mois de FM)
    puis la zone des cellules, déclarée conteneur de contenu (le tableau y range les cellules : StreamedTable.OnMakeItem)"""
    racine = t.tt["m_VisualTree"]["rid"]
    enfants = t.children(racine)
    if len(enfants) != 1 or typ(t, enfants[0]) != "BindingExpect":
        return "modèle de ligne : contenu inattendu (un BindingExpect attendu)"
    be = enfants[0]
    params = t.sd(be).get("Parameters") or []
    if len(params) != 1:
        return "modèle de ligne : paramètre inattendu"
    _vider(t, be)
    params[0]["name"], params[0]["type"] = "binding", {"id": TYPE_ELEMENT}
    _nommer(t, be, NOM_LIGNE)
    t.elem(be)["m_Classes"], t.elem(be)["m_RuleIndex"] = ["flex-grow-class"], -1
    # v10 : hauteur mini 1 px. Relevé dans le code du jeu (DynamicSizeVirtualisationController.VirtualisedElement-
    # SizeChanged) : la hauteur d'une ligne n'est enregistrée que si elle dépasse float.Epsilon ; une ligne cachée à 0 px
    # garde donc sa hauteur d'avant dans le tableau, ses calculs de position se décalent, et quand elle réapparaît (même
    # hauteur qu'enregistrée) rien n'est recalculé : en jeu, décocher puis recocher une compétition vidait le tableau
    # jusqu'au prochain changement d'équipe (qui reconstruit tout). À 1 px, chaque changement est enregistré.
    t.styles.style(t, be, {"flex-direction": "column", "min-height": 1})
    # 1. le bandeau du mois (seulement sur le 1er match du mois) ; v19 : AVANT le filtre, hors de ses enveloppes (jusqu'à
    # la v18, il était dans la plus intérieure : un 1er match du mois caché, un amical par exemple, emportait le titre
    # du mois avec lui ; relevé par Kinito le 13/11, « août 2026 » absent)
    mois = t.clone(src.mois, be, src=src.tr)
    t.styles.copy_from(src.tr.styles, t, mois)
    _parent_id(t, mois)
    _nommer(t, mois, NOM_MOIS)
    t.sd(mois)["Binding"]["m_direct"]["Path"]["m_path"] = "binding.isfirstfixtureofthemonth"
    texte = t.children(mois)[0]
    f = t.sd(texte)["TextBinding"]["m_visualFunction"]
    n = _remplacer_args(f, _chemin("fixture.FixtureDate"), _chemin("binding.fixture.FixtureDate"))
    if n != 1:
        return f"texte du mois : {n} chemin(s) de date remplacé(s) (1 attendu)"
    haut, bas = MARGES_MOIS
    t.styles.style(t, texte, {"margin-top": haut, "margin-bottom": bas})
    classes = t.elem(texte).get("m_Classes") or []
    if "body-sm-strong" not in classes:
        return "texte du mois : classe body-sm-strong de FM introuvable"
    t.elem(texte)["m_Classes"] = [CLASSE_MOIS if c == "body-sm-strong" else c for c in classes]   # v5 : plus grand
    trait = t.clone(src.element, mois, 0, src=src.tl)
    _parent_id(t, trait)
    _nommer(t, trait, f"{PREFIXE}-rencontres-trait")
    t.elem(trait)["m_Classes"], t.elem(trait)["m_RuleIndex"] = [CLASSE_TRAIT], -1
    # 0. v6 : le filtre (calcul, et les enveloppes qui cachent la ligne), après le bandeau du mois ; les cellules vont dans
    # la plus intérieure
    contenu = _filtre_ligne(t, src, be)
    if isinstance(contenu, str):
        return contenu
    # 2. la zone des cellules : en ligne, hauteur FIXE d'une ligne de match (v9 ; jusqu'à la v8 une hauteur mini : en jeu,
    # la 1re ligne et toutes ses cellules faisaient 8 388 670 px, le plafond du moteur de mise en page, avec ou sans
    # flex-grow (v7) et avec ou sans cellule texte dans la colonne de sélection (v8) : une cellule grandissait sans
    # fin dans une ligne qui prend la hauteur de son contenu. Hauteur fixe + débordement coupé : aucune cellule ne
    # peut plus agrandir la ligne, qui fait bandeau du mois + HAUTEUR_LIGNE)
    cellules = t.clone(src.element, contenu, src=src.tl)
    _parent_id(t, cellules)
    _nommer(t, cellules, NOM_CELLULES)
    t.elem(cellules)["m_Classes"], t.elem(cellules)["m_RuleIndex"] = ["row-direction-normal"], -1
    t.styles.style(t, cellules, {"height": HAUTEUR_LIGNE, "min-height": HAUTEUR_LIGNE, "flex-shrink": 0,
                                 "overflow": "hidden"})
    t.tt["m_ContentContainerId"] = t.elem(cellules)["m_Id"]
    t.tt["m_Usings"] = []   # plus aucun modèle inclus (la puce de BulletTextRow est partie)
    return None


def _remplacer_args(f, avant, apres):
    """remplace une suite d'octets (longueur libre) dans les arguments d'une fonction visuelle, argument par argument"""
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    n = 0
    for a in args:
        b = bytes(a[1])
        if avant in b:
            n += b.count(avant)
            a[1] = b.replace(avant, apres)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return n


# ---------- la fabrique (ui-tablefactories, partagé : cette fabrique seulement) ----------
def fabrique_a_jour(tt):
    cols = {c["m_id"]: c for c in tt.get("m_rowData") or []}
    ids = {"kinito-stade", "kinito-spectateurs", COLONNE_SELECTION} | {c[0] for c in COLONNES_V11 + COLONNES_V12}
    return (ids <= set(cols)
            and cols[COLONNE_SELECTION]["m_uxmlRef"]["m_AssetGUID"] == GUID_CELLULE_SELECTION   # v8
            and all(cols[c[0]]["m_translationID"]["GameID"] == c[1] for c in COLONNES_V11 + COLONNES_V12))   # v12


def fabrique_modifiee(tt):
    """nos colonnes, quelle que soit la version (pour retirer une ancienne version aussi)"""
    return any(str(c.get("m_id", "")).startswith("kinito-") for c in tt.get("m_rowData") or [])


def colonnes_v11(tt, autres):
    """v11 : les colonnes de COLONNES_V11, recopiées de leur colonne source (de cette fabrique ou d'une autre fabrique
    de FM, lue seulement : autres = {fabrique: {id: colonne}}), chemins réécrits ; (liste, None) ou (None, message)"""
    cols = {c["m_id"]: c for c in tt["m_rowData"]}
    nouvelles = []
    for cid, titre, (fab, src), chemins, (larg, mini) in COLONNES_V11:
        source = (cols if fab == FABRIQUE else autres.get(fab) or {}).get(src)
        if source is None:
            return None, f"colonne « {src} » de {fab} introuvable"
        c = copy.deepcopy(source)
        faits = 0
        for v in c["m_valueBindings"]:
            if v["to"]["m_path"] in chemins:
                v["to"]["m_path"] = chemins[v["to"]["m_path"]]
                faits += 1
        if faits != len(chemins):
            return None, f"colonne « {src} » de {fab} : chemins inattendus"
        c["m_id"], c["m_translationID"] = cid, {"GameID": titre}
        c["m_defaultWidth"], c["m_minimumWidth"] = float(larg), float(mini)
        nouvelles.append(c)
    return nouvelles, None


def colonnes_v12(cols):
    """v12 : les colonnes de COLONNES_V12, recopiées d'une colonne de FM de cette fabrique (cols : ses colonnes
    d'origine), titre et largeurs à nous, cellule remplacée pour la date ; (liste, None) ou (None, message)"""
    nouvelles = []
    for cid, titre, src, (larg, mini), cellule in COLONNES_V12:
        if src not in cols:
            return None, f"colonne « {src} » de {FABRIQUE} introuvable"
        c = copy.deepcopy(cols[src])
        c["m_id"], c["m_translationID"] = cid, {"GameID": titre}
        c["m_defaultWidth"], c["m_minimumWidth"] = float(larg), float(mini)
        if cellule:
            c["m_uxmlRef"] = {"m_AssetGUID": cellule, "m_SubObjectName": "", "m_SubObjectType": ""}
        nouvelles.append(c)
    return nouvelles, None


def construire_fabrique(tt, colonne_selection, autres):
    cols = {c["m_id"]: c for c in tt["m_rowData"]}
    if not {"time", "result"} <= set(cols) or any(c.startswith("kinito-") for c in cols):
        return "fabrique : colonnes « time » / « result » introuvables, ou déjà des colonnes Kinito"
    stade = copy.deepcopy(cols["time"])   # WhiteTextCell, binding <- un texte
    stade["m_id"], stade["m_translationID"] = "kinito-stade", {"GameID": TRAD_STADE}
    stade["m_defaultWidth"], stade["m_minimumWidth"] = map(float, LARGEURS["kinito-stade"])
    if len(stade["m_valueBindings"]) != 1:
        return "fabrique : colonne « time » inattendue"
    stade["m_valueBindings"][0]["to"]["m_path"] = "binding.fixture.Stadium.Name"
    spect = copy.deepcopy(cols["result"])  # binding <- binding.Fixture (FixtureReference)
    spect["m_id"], spect["m_translationID"] = "kinito-spectateurs", {"GameID": TRAD_SPECTATEURS}
    spect["m_defaultWidth"], spect["m_minimumWidth"] = map(float, LARGEURS["kinito-spectateurs"])
    spect["m_uxmlRef"] = {"m_AssetGUID": GUID_CELLULE, "m_SubObjectName": "", "m_SubObjectType": ""}
    # v5 : la colonne de sélection, invisible (0 px, pas d'élargissement automatique, pas de titre) ; v8 : copie de la
    # colonne de sélection à 0 px de FM (RadioToggleCell, sans texte). En v5-v7 elle avait la cellule TEXTE de « time »
    # (WhiteTextCell) : en jeu, la ligne et toutes ses cellules faisaient 8 388 670 px de haut (relevé du 10/10, 22 h 50,
    # journal des clics), un texte dans une colonne de 0 px. La v4, sans cette colonne, avait des lignes normales.
    sel = copy.deepcopy(colonne_selection)
    if sel["m_uxmlRef"]["m_AssetGUID"] != GUID_CELLULE_SELECTION or len(sel["m_valueBindings"]) != 1:
        return f"fabrique : colonne {SOURCE_SELECTION[1]} de {SOURCE_SELECTION[0]} inattendue"
    sel["m_id"], sel["m_translationID"] = COLONNE_SELECTION, {"GameID": 0}
    sel["m_defaultWidth"] = sel["m_minimumWidth"] = 0.0
    sel["m_allowWidthAutoResizing"] = 0
    sel["m_valueBindings"][0]["to"]["m_path"] = "const.EmptyString"
    nouvelles, pb = colonnes_v11(tt, autres)   # v11 (avant d'ajouter les nôtres : les sources sont les colonnes de FM)
    if pb:
        return f"fabrique : {pb}"
    v12, pb = colonnes_v12(cols)
    if pb:
        return f"fabrique : {pb}"
    tt["m_rowData"] += [stade, spect, sel] + nouvelles + v12
    return None


# ---------- la collection (ui-tableviews, partagé : cette collection seulement) ----------
def collection_a_jour(tt):
    return any(e.get("debug_name") == REPERE for e in tt.get("m_tableViewSettings") or [])


def collection_modifiee(tt):
    """notre liste de vues, quelle que soit sa version (pour retirer une ancienne version aussi)"""
    return any(str(e.get("debug_name") or "").startswith("UIPickerKinito-rencontres-v")
               for e in tt.get("m_tableViewSettings") or [])


def construire_collection(tt, src_noms, pid_vue, titres, type_entree):
    tt["m_customViewDisplayName"] = copy.deepcopy(src_noms["m_customViewDisplayName"])
    tt["m_customViewNamePrefix"] = copy.deepcopy(src_noms["m_customViewNamePrefix"])
    vide = {"m_FileID": 0, "m_PathID": 0}
    tt["m_tableViewSettings"] = [{"debug_name": REPERE, "name": "Fixtures", "ChildList": [], "Disable": 0,
                                  "AddSpacerBefore": 0, "DisplayValue": {"GameID": TRAD_VUE},
                                  "PropertyValue": {"m_FileID": 0, "m_PathID": pid_vue}, "Requirement": dict(vide)}]
    refs = []
    for i, col in enumerate(COLONNES_MENU):
        refs.append({"rid": i + 1, "type": copy.deepcopy(type_entree),
                     "data": {"debug_name": "", "name": col, "ChildList": [], "Disable": 0, "AddSpacerBefore": 0,
                              "DisplayValue": {"GameID": titres[col]}, "PropertyValue": col, "Requirement": dict(vide)}})
    tt["references"] = {"version": 2, "RefIds": refs}
    tt["m_contextMenuData"] = [{"debug_name": REPERE, "name": "Fixtures", "ChildList": [{"rid": r["rid"]} for r in refs],
                                "Disable": 0, "AddSpacerBefore": 0, "DisplayValue": {"GameID": TRAD_VUE},
                                "PropertyValue": "kinito-rencontres", "Requirement": dict(vide)}]


# ---------- v6 : le filtre ----------
ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON = "BindingPath]", "BooleanVisualArg", "ComparisonOperator]"
ARG_TEXTE, ARG_BOOLEENS, ARG_LOGIQUE = "StringVisualArg", "BooleanArg]", "LogicOperator]"


def _fn_guid(f):
    return ((f.get("m_target") or {}).get("m_guid")) if isinstance(f, dict) else None


def _fonction_source(modele, guid):
    """une fonction de FM (copie), prise sur un élément du modèle qui l'utilise (BindFunction seul ou en liste)"""
    o = ouvrir(modele, depart_original=True)
    if not o:
        return None
    t = o[3]
    for r in t.walk():
        fs = t.sd(r).get("BindFunction")
        for f in fs if isinstance(fs, list) else [fs]:
            if _fn_guid(f) == guid:
                return copy.deepcopy(f)
    return None


def _texte_source(modele, numero):
    """le TextBinding (copie) d'un texte de FM qui affiche la traduction n° numero"""
    o = ouvrir(modele, depart_original=True)
    if not o:
        return None
    t = o[3]
    for r in t.refs.values():   # toutes les données du modèle : un texte peut être porté par une surcharge d'instance
        tb = ((r or {}).get("data") or {}).get("TextBinding")
        if not str(((r or {}).get("type") or {}).get("class", "")).startswith("SIText"):
            continue
        if not isinstance(tb, dict) or tb.get("m_kind") != 2:
            continue
        for a in decode_args(tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]):
            b = bytes(a[1])
            if b"TranslationID" in bytes(a[0]) and len(b) >= 4 and struct.unpack("<i", b[:4])[0] == numero:
                return copy.deepcopy(tb)
    return None


def _args(f, attendu, valeurs):
    """réécrit les arguments d'une fonction recopiée ; attendu = fin du nom de type de chaque argument, dans l'ordre de
    FM ; valeurs = octets (None : garder ceux de FM). Faux si les arguments ne sont pas ceux attendus."""
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != len(attendu) or any(not bytes(a[0]).endswith(s.encode()) for a, s in zip(args, attendu)):
        return False
    for a, v in zip(args, valeurs):
        if v is not None:
            a[1] = v
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return True


def _booleens(cond):
    """une liste de BooleanArg (format relevé sur StoreNoItemsSelector) : nombre, puis (chemin, inversé) par élément"""
    return _enc_varint(len(cond)) + b"".join(b"\x01" + _enc_varint(len(p)) + p.encode() + bytes([inv]) for p, inv in cond)


def _filtre_ligne(t, src, parent):
    """dans la ligne de match : un BindingSetter de FM qui calcule L_DOM (match à domicile) et L_EGAL (v19 : la
    compétition du match = la case k ; v20 : plus de L_DANS / L_ENCOURS, la liste à cases est retirée), puis une
    enveloppe par condition de CONDITIONS, cachée si la condition est vraie (v12 : un SIVisible de FM, qui montre et
    cache) ; renvoie la plus intérieure (les cellules y vont), ou un texte d'erreur"""
    calc = t.clone(src.calcul, parent, src=src.tcalc)
    _vider(t, calc)
    _parent_id(t, calc)
    _nommer(t, calc, NOM_CALCUL)
    # v7 : AUCUN flex-grow (en v6, calcul et enveloppes « grandis pour remplir » dans une ligne qui prend la hauteur
    # de son contenu : relevé en jeu, la 1re ligne faisait 8 388 670 px)
    t.elem(calc)["m_Classes"], t.elem(calc)["m_RuleIndex"] = [], -1
    t.styles.style(t, calc, {"flex-direction": "column"})
    fns = []
    for cle, attendu, valeurs in (
            ("aorb", [ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
             [_chemin("const.True"), _chemin("const.False"), _chemin(L_DOM), None, struct.pack("<i", 2),
              _chemin(DOMICILE[0]), _chemin(DOMICILE[1])]),) + tuple(
            # v19 : la compétition du match = la case k ? Deux entiers jamais vides : l'UniqueId de la compétition du
            # match, et V_ID[k], que la racine met à 0 quand la case est vide (op 2 = égal, comme Domicile)
            ("aorb", [ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
             [_chemin("const.True"), _chemin("const.False"), _chemin(L_EGAL[k]), None, struct.pack("<i", 2),
              _chemin(ID_COMP), _chemin(V_ID[k])]) for k in range(MASQUES)):
        f = copy.deepcopy(src.fn[cle])
        if not _args(f, attendu, valeurs):
            return f"fonction « {cle} » de FM : arguments inattendus"
        fns.append(f)
    sd = t.sd(calc)
    _poser(sd, "ValueVariables", [{"m_name": n, "m_scopeValue": {"m_serializedData": "Bool|0|"}}
                                  for n in (L_DOM, *L_EGAL)])   # v19 : une égalité par case ; v20 : sans la liste
    _poser(sd, "ReferenceVariables", [])
    _poser(sd, "BindFunction", fns)
    contenu = calc
    for nom, cond in CONDITIONS:
        # v12 : un SIVisible de FM (montré ou caché, display, par sa liaison) ; montré si UNE des conditions de cache
        # manque : Ou sur les conditions inversées. v6 à v11 : une enveloppe + un SIStyleSetter sur
        # BindMultipleBooleanArgsToUSSClass, qui pose la classe mais ne l'enlève jamais (en jeu : recocher ne remettait
        # pas les matchs)
        # AlwaysInstantiate : le contenu existe dès la création de la ligne (la zone des cellules, conteneur de contenu
        # du modèle, y est : le tableau y range les cellules à OnMakeItem) ; v7 : pas de flex-grow
        w = _visible_fn(t, src, contenu, [(p, 1 - inv) for p, inv in cond], OU, f"{PREFIXE}-rencontres-filtre-{nom}",
                        toujours=1)
        if isinstance(w, str):
            return w
        t.styles.style(t, w, {"flex-direction": "column"})
        contenu = w
    return contenu


def _composant_racine(t):
    """les données du BindingSetterComponent de la racine du bloc (ses variables sont vues de tout le bloc), ou None"""
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    for c in t.sd(racine).get("m_components") or []:
        ref = t.refs[c["rid"]]
        if str(ref["type"]["class"]).startswith("BindingSetterComponent"):
            return ref["data"]
    return None


def retirer_variables_filtre(t):
    d = _composant_racine(t)
    if d is None:
        return
    for cle in ("ValueVariables", "ReferenceVariables"):
        d[cle] = [v for v in d.get(cle) or [] if not str(v.get("m_name", "")).startswith("kinitof")
                  and v.get("m_name") not in (V_VUE, VUES_PRETES)]   # v15 : celles des vues aussi


def filtre_bloc(t, src):
    """le bloc : les variables du filtre à sa racine (vues de l'en-tête, du panneau et des lignes du tableau), et le
    bouton « Filtre ⌄ » de FM au bout de la rangée de l'en-tête (celle des boutons d'équipes, 26.2), poussé à droite"""
    d = _composant_racine(t)
    if d is None:
        return "racine du bloc : BindingSetterComponent introuvable"
    retirer_variables_filtre(t)
    d.setdefault("ValueVariables", []).extend([{"m_name": n, "m_scopeValue": {"m_serializedData": "Bool|1|"}}
                                               for n in VARS_FILTRE]   # v7 : cochées au départ
                                              # v12 : faux au départ (la liste de FM d'abord, jamais nos morceaux sur un
                                              # écran qui n'est pas le nôtre)
                                              + [{"m_name": V_HUMAIN, "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
                                              # v19 : case remplie (faux) et UniqueId de sa compétition (0) ; « Int|0| » :
                                              # le format de FM (FilterListID de NationSiteContentBlock) ; v20 : la
                                              # sélection déjà masquée (une égalité par case) et son UniqueId
                                              + [{"m_name": n, "m_scopeValue": {"m_serializedData": "Bool|0|"}}
                                                 for n in V_PLEIN + V_SELEGAL]
                                              + [{"m_name": n, "m_scopeValue": {"m_serializedData": "Int|0|"}}
                                                 for n in V_ID + [V_IDSEL]]
                                              # v22 : le tableau branché (vrai au départ)
                                              + [{"m_name": V_AFFICHE, "m_scopeValue": {"m_serializedData": "Bool|1|"}}])
    d.setdefault("ReferenceVariables", []).extend([{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": n}
                                                   for n in V_MASQUE])   # v19 : les cases, vides au départ
    d["ValueVariables_UxmlAttributeFlags"] = d["ReferenceVariables_UxmlAttributeFlags"] = 1
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    entete = next((k for k in t.children(racine) if typ(t, k) == "VisualElement"
                   and "row-direction-normal" in (t.elem(k).get("m_Classes") or [])), None)
    if entete is None:
        return "rangée de l'en-tête du bloc introuvable"
    # v12 : l'espaceur et le bouton dans un SIVisible (mêmes conditions que notre tableau) : ailleurs, l'en-tête de FM ;
    # v13 : hors petit format, pour toute équipe
    zone = _visible_fn(t, src, entete, [(PETIT, 1)], 0, NOM_ZONE_FILTRE, classes=["flex-grow-class", "row-direction-normal"])
    if isinstance(zone, str):
        return zone
    t.styles.style(t, zone, {"align-items": "center"})
    espace = t.clone(src.element, zone, src=src.tl)
    _parent_id(t, espace)
    _nommer(t, espace, NOM_ESPACE)
    t.elem(espace)["m_Classes"], t.elem(espace)["m_RuleIndex"] = ["flex-grow-class"], -1
    w = t.clone(src.widget, zone, src=src.tw)
    t.styles.copy_from(src.tw.styles, t, w)
    _parent_id(t, w)
    _nommer(t, w, NOM_FILTRE)
    _poser(t.sd(w), "ContentTemplate", {"m_AssetGUID": GUID_PANNEAU, "m_SubObjectName": "", "m_SubObjectType": ""})
    t.styles.style(t, w, {"align-self": "center", "flex-shrink": 0})
    # les calculs de départ (v7 à v19 : aussi la copie de la liste à cases, retirée en v20)
    init = t.clone(src.calcul, entete, src=src.tcalc)
    _vider(t, init)
    _parent_id(t, init)
    _nommer(t, init, NOM_INIT)
    t.elem(init)["m_Classes"], t.elem(init)["m_RuleIndex"] = [], -1
    t.styles.style(t, init, {"position": "absolute", "width": 0, "height": 0})
    fns = []
    # v12 : V_HUMAIN = l'équipe affichée (team, paramètre du bloc) est dans les équipes du club du joueur (v13 : choisit
    # la rangée d'équipes, celle de 26.2 ou celle d'un club IA)
    f = copy.deepcopy(src.fn["contient"])
    if not _args(f, [ARG_BOOL, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_CHEMIN],
                 [b"\x00", _chemin(EQUIPES_HUMAIN), _chemin("team"), None, _chemin(V_HUMAIN)]):
        return "fonction « contient » de FM : arguments inattendus"
    fns.append(f)
    # v19 : pour chaque case de masquage, sans jamais lire une référence vide (fonction de FM sur IsNullReference) :
    # V_PLEIN = la case est remplie, V_ID = l'UniqueId de sa compétition, 0 si elle est vide
    for k in range(MASQUES):
        for primaire, secours, dest in (("const.True", "const.False", V_PLEIN[k]),
                                        (f"{V_MASQUE[k]}.UniqueId", "const.Zero", V_ID[k])):
            f = copy.deepcopy(src.fn["nul"])
            if not _args(f, [ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL],
                         [_chemin(V_MASQUE[k]), _chemin(primaire), _chemin(secours), _chemin(dest), None]):
                return "fonction « référence vide » de FM : arguments inattendus"
            fns.append(f)
    # v20 : l'UniqueId de la compétition du match sélectionné (0 sans sélection, même fonction de FM), puis, pour chaque
    # case, est-ce la même ? (deux entiers jamais vides, op 2 = égal) : le bouton du bandeau se cache si elle est masquée
    f = copy.deepcopy(src.fn["nul"])
    if not _args(f, [ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL],
                 [_chemin(SELECTION_COMP), _chemin(f"{SELECTION_COMP}.UniqueId"), _chemin("const.Zero"),
                  _chemin(V_IDSEL), None]):
        return "fonction « référence vide » de FM : arguments inattendus"
    fns.append(f)
    for k in range(MASQUES):
        f = copy.deepcopy(src.fn["aorb"])
        if not _args(f, [ARG_CHEMIN, ARG_CHEMIN, ARG_CHEMIN, ARG_BOOL, ARG_COMPARAISON, ARG_CHEMIN, ARG_CHEMIN],
                     [_chemin("const.True"), _chemin("const.False"), _chemin(V_SELEGAL[k]), None, struct.pack("<i", 2),
                      _chemin(V_IDSEL), _chemin(V_ID[k])]):
            return "fonction « A ou B » de FM : arguments inattendus"
        fns.append(f)
    sd = t.sd(init)
    _poser(sd, "ValueVariables", [])
    _poser(sd, "ReferenceVariables", [])
    _poser(sd, "BindFunction", fns)
    return None


# ---------- v6 : le panneau du filtre (ClubSupportersConfidenceRow, seul propriétaire) ----------
def panneau_a_jour(t):
    return any(t.name(r) == NOM_MASQUES for r in t.walk())   # v7 : nom versionné (v20 : la section des masquées)


def panneau_modifie(t):
    return any(t.name(r).startswith(f"{PREFIXE}-rencontres-") for r in t.walk())


def _libelle(t, src, parent, cle, classes, nom):
    x = t.clone(src.libelle, parent, src=src.to)
    _parent_id(t, x)
    _nommer(t, x, nom)
    t.elem(x)["m_Classes"], t.elem(x)["m_RuleIndex"] = list(classes), -1
    _poser(t.sd(x), "TextBinding", copy.deepcopy(src.textes[cle]))
    return x


def _case(t, src, parent, var, cle):
    """une rangée : la case à cocher de FM sur var (cochée = vrai) et son libellé"""
    r = t.clone(src.element, parent, src=src.tl)
    _parent_id(t, r)
    _nommer(t, r, f"{PREFIXE}-rencontres-panneau-{cle}")
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    t.styles.style(t, r, {"margin-top": 6})
    c = t.clone(src.case, r, src=src.tk)
    t.styles.copy_from(src.tk.styles, t, c)
    _parent_id(t, c)
    _nommer(t, c, f"{PREFIXE}-rencontres-panneau-{cle}-case")
    d = t.sd(c)
    _poser(d, "SelectionBinding", {"m_path": var})
    _poser(d, "CheckedEvents", {"m_bytes": liste([copier("const.True", var), recharger()])})   # v22 : puis le tableau
    _poser(d, "UncheckedEvents", {"m_bytes": liste([copier("const.False", var), recharger()])})   # rebranché
    _libelle(t, src, r, cle, ["body-md", "global-text-primary", "padding-left-global-padding-regular"],
             f"{PREFIXE}-rencontres-panneau-{cle}-texte")


def _trait(t, src, parent, cle):
    """v7 : le trait de FM (CLASSE_TRAIT, celui du bandeau du mois) entre deux sections du panneau"""
    x = t.clone(src.element, parent, src=src.tl)
    _parent_id(t, x)
    _nommer(t, x, f"{PREFIXE}-rencontres-panneau-trait-{cle}")
    t.elem(x)["m_Classes"], t.elem(x)["m_RuleIndex"] = [CLASSE_TRAIT], -1
    t.styles.style(t, x, {"margin-top": 4, "margin-bottom": 10})


def _texte_fixe(t, r, s):
    """v19 : un texte écrit tel quel (comme les textes du skin d'Alex et kinito_pays_formation : TextBinding m_kind 0,
    le champ « text » d'Unity)"""
    sd = t.sd(r)
    tb = copy.deepcopy(sd.get("TextBinding") or {})
    tb["m_kind"] = 0
    tb.setdefault("m_direct", {}).setdefault("Path", {})["m_path"] = ""
    tb["m_visualFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                              "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    _poser(sd, "TextBinding", tb)
    sd["text"], sd["text_UxmlAttributeFlags"] = s, 1
    sd["DebugDisplay"], sd["DebugDisplay_UxmlAttributeFlags"] = s, 1


def _texte_chemin(t, r, chemin):
    """v19 : un texte lu sur un chemin (TextBinding m_kind 1, comme le nom de l'équipe dans l'en-tête de ce bloc)"""
    sd = t.sd(r)
    tb = copy.deepcopy(sd.get("TextBinding") or {})
    tb["m_kind"] = 1
    tb.setdefault("m_direct", {}).setdefault("Path", {})["m_path"] = chemin
    tb["m_visualFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                              "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    _poser(sd, "TextBinding", tb)


def _libelle_fixe(t, src, parent, texte, classes, nom):
    x = t.clone(src.libelle, parent, src=src.to)
    _parent_id(t, x)
    _nommer(t, x, nom)
    t.elem(x)["m_Classes"], t.elem(x)["m_RuleIndex"] = list(classes), -1
    _texte_fixe(t, x, texte)
    return x


def _bouton(t, src, parent, nom, texte, evenements):
    """v19 : le bouton de FM de Réinitialiser (TacticsPitchViewOptions), avec un texte écrit tel quel"""
    b = t.clone(src.bouton, parent, src=src.to)
    t.styles.copy_from(src.to.styles, t, b)
    _vider(t, b)
    _parent_id(t, b)
    _nommer(t, b, nom)
    _poser(t.sd(b), "Events", {"m_bytes": liste(evenements)})
    _libelle_fixe(t, src, b, texte, ["body-md", "global-text-primary"], nom + "-texte")
    return b


def selon_langue(t, src, parent, nom, cle, faire, css, css_sw=None, index=None):
    """v21, recette 19 (26.18) : sous parent, le conteneur de FM qui lit la langue du jeu (tdd-messages-banner, ses
    composants seuls), puis un interrupteur de FM par langue dont notre texte cle diffère de l'anglais (rang 1 = c'est
    elle, rang 0 = la suite) ; l'anglais au bout. faire(par, texte, suffixe) pose le contenu d'une langue (suffixe : ""
    pour l'anglais, « -german »…). Un interrupteur de FM ne construit que l'enfant montré : le jeu ne construit que la
    langue réglée. Renvoie le conteneur"""
    tg = src.tlg
    env = t.clone(src.langue_env, parent, index, src=tg)
    _parent_id(t, env)
    for k in list(t.children(env)):
        if not (t.elem(k).get("m_FullTypeName") or "").endswith("Component"):
            t.remove(k)
    t.styles.copy_from(tg.styles, t, env)
    _nommer(t, env, f"{nom}-langue-v{VERSION}")
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    t.styles.style(t, env, css)
    defaut = texte_langue(cle, LANGUE_DEFAUT)
    autres = [(lg, texte_langue(cle, lg)) for lg in LANGUES_JEU if texte_langue(cle, lg) != defaut]
    css_sw = css_sw or {"flex-direction": css.get("flex-direction", "column")}

    def suite(par, i):
        if i == len(autres):
            faire(par, defaut, "")
            return
        lg, texte = autres[i]
        sw = t.clone(src.langue_sw, par, src=tg)
        _parent_id(t, sw)
        _vider(t, sw)
        t.styles.copy_from(tg.styles, t, sw)
        _nommer(t, sw, f"{nom}-langue-{_slug(lg)}")
        t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = [], -1
        f = t.sd(sw)["Binding"]["m_visualFunction"]
        a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        mots = [x for x in a if bytes(x[0]).endswith(b"StringVisualArg")]
        mots[0][1] = b"\x01" + _enc_varint(len(lg.encode())) + lg.encode()
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
        t.styles.style(t, sw, css_sw)
        suite(sw, i + 1)                    # rang 0 : pas cette langue
        faire(sw, texte, f"-{_slug(lg)}")   # rang 1 : c'est elle

    suite(env, 0)
    return env


def _libelle_langue(t, src, parent, cle, classes, nom, css=None):
    """v21 : un texte à nous (TRADUCTIONS[cle]) dans la langue du jeu"""
    return selon_langue(t, src, parent, nom, cle,
                        lambda par, texte, s: _libelle_fixe(t, src, par, texte, classes, nom + s),
                        dict(css or {}, **{"flex-direction": "column"}))


def _bouton_langue(t, src, parent, nom, cle, evenements, css=None):
    """v21 : le bouton de _bouton recopié entier dans chaque langue (comme en v20 : le bouton de FM et son texte)"""
    return selon_langue(t, src, parent, nom, cle,
                        lambda par, texte, s: _bouton(t, src, par, nom + s, texte, evenements),
                        dict(css or {}, **{"flex-direction": "column"}),
                        {"flex-direction": "column", "flex-shrink": 0})


def _section_masques(t, src, be):
    """v19 : COMPÉTITIONS MASQUÉES ; v20 : sans bouton « Masquer » (il est dans le bandeau). Une ligne par case remplie
    (SIVisible sur la case, sans AlwaysInstantiate : le nom n'est lu que si elle est remplie) : son nom et « Remettre »
    (la vide) ; « Aucune… » si toutes sont vides (ET sur les V_PLEIN inversés). None, ou un texte d'erreur"""
    sec = t.clone(src.element, be, src=src.tl)
    _parent_id(t, sec)
    _nommer(t, sec, NOM_MASQUES)
    t.elem(sec)["m_Classes"], t.elem(sec)["m_RuleIndex"] = [], -1
    t.styles.style(t, sec, {"flex-direction": "column", "flex-shrink": 0})
    _trait(t, src, sec, "masques")
    # v21 : nos textes dans la langue du jeu (_libelle_langue, _bouton_langue)
    _libelle_langue(t, src, sec, "titre_masques", ["heading-small-12px", "global-text-primary"],
                    f"{PREFIXE}-rencontres-panneau-titre-masques")
    aucune = _visible_fn(t, src, sec, [(p, 1) for p in V_PLEIN], 0, f"{PREFIXE}-rencontres-panneau-masques-aucune")
    if isinstance(aucune, str):
        return aucune
    t.styles.style(t, aucune, {"margin-top": 6})
    _libelle_langue(t, src, aucune, "aucune", ["body-md", "global-text-primary"],
                    f"{PREFIXE}-rencontres-panneau-masques-aucune-texte")
    for k in range(MASQUES):
        base = f"{PREFIXE}-rencontres-panneau-masque-{k + 1}"
        plein = _visible(t, src, sec, V_MASQUE[k], False, base + "-pleine")
        t.elem(plein)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, plein, {"margin-top": 6})
        nom = t.clone(src.libelle, plein, src=src.to)
        _parent_id(t, nom)
        _nommer(t, nom, base + "-nom")
        t.elem(nom)["m_Classes"], t.elem(nom)["m_RuleIndex"] = ["body-md", "global-text-primary", "flex-grow-class"], -1
        _texte_chemin(t, nom, f"{V_MASQUE[k]}.Name")
        _bouton_langue(t, src, plein, base + "-remettre", "remettre",
                       [copier("const.NullRef", V_MASQUE[k]), recharger()],   # v22 : puis le tableau rebranché
                       {"flex-shrink": 0, "margin-left": 8})
    return None


def construire_panneau(t, src):
    """le contenu du panneau (v20) : Réinitialiser (tout), COMPÉTITIONS MASQUÉES (nom + Remettre), Hors compétition,
    LIEU, Domicile, Extérieur ; v7 à v19 : aussi le tableau de FM à cases sur team.CurrentComps, retiré en v20"""
    enfants = t.children(t.tt["m_VisualTree"]["rid"])
    if len(enfants) != 1 or typ(t, enfants[0]) != "BindingExpect":
        return "panneau : contenu inattendu (un BindingExpect attendu)"
    be = enfants[0]
    _vider(t, be)
    _poser(t.sd(be), "Parameters", [])
    _nommer(t, be, NOM_PANNEAU)
    t.elem(be)["m_Classes"], t.elem(be)["m_RuleIndex"] = [], -1
    t.styles.style(t, be, {"flex-direction": "column", "min-width": LARGEUR_PANNEAU, "margin-left": 12,
                           "margin-right": 12, "margin-top": 12, "margin-bottom": 12})
    # Réinitialiser : v7, recoche tout (v6 copiait const.NullRef dans la liste : crash en jeu, « Unable to cast
    # NullReference to IList » ; FM ne vide jamais ainsi une liste à cases, et le jeu n'a pas d'événement « tout décocher »)
    b = t.clone(src.bouton, be, src=src.to)
    t.styles.copy_from(src.to.styles, t, b)
    _vider(t, b)
    _parent_id(t, b)
    _nommer(t, b, f"{PREFIXE}-rencontres-panneau-reinitialiser")
    # v19 : vide aussi les cases de masquage (const.NullRef, comme FM ; ce qui les lit tolère une référence vide : la
    # fonction IsNullReference de FM et les SIVisible ; v6 plantait parce qu'un TABLEAU lisait la liste vidée) ; v20 :
    # plus de liste à cases à recocher
    _poser(t.sd(b), "Events", {"m_bytes": liste([copier("const.True", v) for v in VARS_FILTRE]
                                                + [copier("const.NullRef", v) for v in V_MASQUE]
                                                + [recharger()])})   # v22 : puis le tableau rebranché
    t.styles.style(t, b, {"align-self": "flex-start", "margin-bottom": 10})
    _libelle(t, src, b, "reinitialiser", ["body-md", "global-text-primary"], f"{PREFIXE}-rencontres-panneau-reinitialiser-texte")
    # v20 : COMPÉTITIONS MASQUÉES (trait de FM et titre au-dessus, comme les sections du filtre de FM24), puis Hors
    # compétition (les amicaux), puis LIEU
    pb = _section_masques(t, src, be)
    if pb:
        return pb
    _case(t, src, be, V_FHC, "horscomp")
    _trait(t, src, be, "lieu")
    _libelle(t, src, be, "lieu", ["heading-small-12px", "global-text-primary"], f"{PREFIXE}-rencontres-panneau-titre-lieu")
    _case(t, src, be, V_FDOM, "domicile")
    _case(t, src, be, V_FEXT, "exterieur")
    t.tt["m_Usings"] = []
    return None


# ---------- v7 à v11 : la fabrique des compétitions de FM (une colonne y était AJOUTÉE) ; v12 : remise d'origine ----------
def fabrique_comps_modifiee(tt):
    return any(str(c.get("m_id", "")).startswith("kinito-") for c in tt.get("m_rowData") or [])


# ---------- v6 : la vue du tableau du panneau ; v12 : VUE_FILTRE (citée par rien), une seule colonne, celle de FM ----------
def vue_filtre_a_jour(tt):
    return vue_colonnes(tt) == [COLONNE_FILTRE]


# ---------- v12 : notre fabrique (FABRIQUE_TABLEAU, seul propriétaire) ----------
GARDER_FABRIQUE = ("m_GameObject", "m_Enabled", "m_Script", "m_Name")   # ce qui reste à l'objet réécrit


def fabrique_tableau(t_libre, t_fm):
    """le contenu de la fabrique de FM (son original), sous l'identité de la fabrique libre"""
    tt = {k: copy.deepcopy(v) for k, v in t_fm.items() if k not in GARDER_FABRIQUE}
    tt.update({k: copy.deepcopy(t_libre[k]) for k in GARDER_FABRIQUE if k in t_libre})
    return tt


# ---------- commandes ----------
def etat_actuel():
    """tous les objets que ce script réécrit ou remet d'origine (None : introuvable)"""
    env_f, env_v = nb.env_of(FABRIQUES), nb.env_of(VUES)
    return {
        "bloc": ouvrir(BLOC), "cellule": ouvrir(CELLULE), "ligne": ouvrir(LIGNE), "panneau": ouvrir(PANNEAU),
        "date": ouvrir(CELLULE_DATE),                                       # v12
        "cellule_ia": ouvrir(CELLULE_IA),                                   # v13
        "fab": mono(env_f, FABRIQUE),                                       # FM : lue ; v12 : remise d'origine
        "fab_tab": mono(env_f, FABRIQUE_TABLEAU),                           # v12 : la nôtre
        "fab_comps": mono(env_f, FABRIQUE_COMPS),                           # FM : lue ; v12 : remise d'origine
        "col": mono(env_v, COLLECTION), "vue_filtre": mono(env_v, VUE_FILTRE),
        "vue_v6": mono(env_v, VUE_FILTRE_V6),                               # FM : remise d'origine (erreur de la v6)
        "vue_rencontres": mono(env_v, VUE_RENCONTRES),                      # v12
        "env_v": env_v,
    }


def _modifie_fm(o):
    """les objets de FM que ce script ne doit plus toucher (v12) et qu'une ancienne version a modifiés"""
    out = []
    if o["fab"] is not None and fabrique_modifiee(o["fab"].read_typetree()):
        out.append((o["fab"], FABRIQUES, FABRIQUE))
    if o["fab_comps"] is not None and fabrique_comps_modifiee(o["fab_comps"].read_typetree()):
        out.append((o["fab_comps"], FABRIQUES, FABRIQUE_COMPS))
    if o["vue_v6"] is not None and vue_modifiee(o["vue_v6"]):
        out.append((o["vue_v6"], VUES, VUE_FILTRE_V6))
    # v20 : la vue du tableau à cases (réécrite de la v12 à la v19, citée par rien) n'est plus utilisée : d'origine
    if o["vue_filtre"] is not None and vue_modifiee(o["vue_filtre"]):
        out.append((o["vue_filtre"], VUES, VUE_FILTRE))
    return out


def a_jour():
    o = etat_actuel()
    if any(v is None for v in o.values()):
        return False
    return (bloc_a_jour(o["bloc"][3]) and cellule_a_jour(o["cellule"][3]) and ligne_a_jour(o["ligne"][3])
            and panneau_a_jour(o["panneau"][3]) and cellule_date_a_jour(o["date"][3])
            and cellule_ia_a_jour(o["cellule_ia"][3])
            and fabrique_a_jour(o["fab_tab"].read_typetree()) and collection_a_jour(o["col"].read_typetree())
            and vue_a_jour(o["vue_rencontres"].read_typetree())
            and not _modifie_fm(o))


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def _depuis_original(nom, test, construire, src):
    """un modèle dont on est seul propriétaire, repris de son original puis construit ; (o, None) ou (None, message)"""
    o = ouvrir(nom, depart_original=True)
    if test(o[3]):
        return None, f"pas de sauvegarde d'origine propre de {nom}"
    pb = construire(o[3], src)
    return (None, pb) if pb else (o, None)


def _remettre(objet, bundle, nom):
    """un objet de FM remis à son original sauvegardé ; faux s'il n'y en a pas"""
    orig = hp.original(bundle, objet)
    if orig is None:
        print(f"[Kinito] Rencontres (vues) : {nom} : pas de sauvegarde d'origine, rien fait")
        return False
    objet.save_typetree(orig)
    nb._dirty.add(bundle)
    print(f"[Kinito] Rencontres (vues) : {nom} : remise d'origine (le reste du bundle n'est pas touché)")
    return True


def cmd_appliquer():
    o = etat_actuel()
    manquants = [k for k, v in o.items() if v is None]
    if manquants:
        print("[Kinito] Rencontres (vues) : objets du jeu introuvables (" + ", ".join(manquants) + ") (mise à jour de "
              "FM ?), ignoré")
        return
    if a_jour():
        print("[Kinito] Rencontres (vues) : déjà appliqué")
    else:
        src = Sources()
        manque = src.manque()
        if manque:
            print("[Kinito] Rencontres (vues) : morceaux de FM introuvables (" + ", ".join(manque) + "), rien enregistré")
            return
        # garde-fous : les objets réécrits sont bien ceux qu'on croit (GUID du catalogue)
        attendus = [(o["cellule"][0], o["cellule"][1].path_id, GUID_CELLULE, CELLULE),
                    (o["ligne"][0], o["ligne"][1].path_id, GUID_LIGNE, LIGNE),
                    (o["panneau"][0], o["panneau"][1].path_id, GUID_PANNEAU, PANNEAU),
                    (o["date"][0], o["date"][1].path_id, GUID_CELLULE_DATE, CELLULE_DATE),
                    (o["cellule_ia"][0], o["cellule_ia"][1].path_id, GUID_CELLULE_IA, CELLULE_IA),   # v13
                    (VUES, o["col"].path_id, GUID_COLLECTION, COLLECTION),
                    (VUES, o["vue_filtre"].path_id, GUID_VUE_FILTRE, VUE_FILTRE),
                    (VUES, o["vue_v6"].path_id, GUID_VUE_FILTRE_V6, VUE_FILTRE_V6),
                    (VUES, o["vue_rencontres"].path_id, GUID_VUE_RENCONTRES, VUE_RENCONTRES),
                    (FABRIQUES, o["fab"].path_id, GUID_FABRIQUE, FABRIQUE),
                    (FABRIQUES, o["fab_tab"].path_id, GUID_FABRIQUE_TABLEAU, FABRIQUE_TABLEAU),
                    (FABRIQUES, o["fab_comps"].path_id, GUID_FABRIQUE_COMPS, FABRIQUE_COMPS)]
        faux = [nom for bundle, pid, g, nom in attendus if guid_de(bundle, pid) != g]
        if faux:
            print(f"[Kinito] Rencontres (vues) : GUID changé ({', '.join(faux)}), rien enregistré")
            return
        tf_fm = hp.original(FABRIQUES, o["fab"]) or o["fab"].read_typetree()
        tf_libre = hp.original(FABRIQUES, o["fab_tab"])
        if tf_libre is None or tf_libre.get("m_Script") != tf_fm.get("m_Script") or "m_rowData" not in tf_libre:
            print(f"[Kinito] Rencontres (vues) : {FABRIQUE_TABLEAU} : pas d'original, ou pas du même type que "
                  f"{FABRIQUE}, rien enregistré")
            return
        vue_portail = mono(o["env_v"], VUE_DEFAUT)
        noms = mono(o["env_v"], SOURCE_NOMS_VUES)
        if vue_portail is None or noms is None:
            print("[Kinito] Rencontres (vues) : vue du Portail ou recherche de joueurs introuvable, rien enregistré")
            return
        tp = vue_portail.read_typetree()
        modele_colonne = next((c for c in tp["m_tableView"]["m_tableConfig"] if c.get("m_columnID") == "date"), None)
        tn = noms.read_typetree()
        # le type des entrées de colonnes (PropertyValue = un texte), pas celui des vues (PropertyValue = un objet)
        type_entree = next((r["type"] for r in tn["references"]["RefIds"]
                            if r["type"]["class"] == "SIDropdownElement`1[[System.String, mscorlib]]"), None)
        if type_entree is None or not tn.get("m_customViewDisplayName", {}).get("GameID") or modele_colonne is None:
            print("[Kinito] Rencontres (vues) : format des menus de colonnes ou des vues inattendu, rien enregistré")
            return
        # 1. le bloc : le modèle actuel (partagé avec 26.2), sans une ancienne version de nos morceaux
        retirer_bloc(o["bloc"])
        msgs = construire_bloc(o["bloc"][3], src)
        if any("introuvable" in m or "inattendu" in m or "attendue" in m for m in msgs):
            print(f"[Kinito] Rencontres (vues) : {BLOC} : {msgs[0]}, rien enregistré")
            return
        # 2. les modèles dont on est seul propriétaire, depuis leurs originaux
        repris = []
        for nom, test, construire in ((CELLULE, cellule_a_jour, construire_cellule),
                                      (LIGNE, ligne_a_jour, construire_ligne),
                                      (PANNEAU, panneau_modifie, construire_panneau),
                                      (CELLULE_DATE, cellule_date_a_jour, construire_cellule_date),   # v12
                                      (CELLULE_IA, cellule_ia_modifiee, construire_cellule_ia)):   # v13
            om, pb = _depuis_original(nom, test, construire, src)
            if pb:
                print(f"[Kinito] Rencontres (vues) : {nom} : {pb}, rien enregistré")
                return
            repris.append(om)
        # 3. notre fabrique (v12) : le contenu de celle de FM (son original) + nos colonnes ; v8 : la colonne de
        # sélection à 0 px de FM comme modèle
        fr = mono(nb.env_of(FABRIQUES), SOURCE_SELECTION[0])
        colonne_selection = next((c for c in (fr.read_typetree()["m_rowData"] if fr is not None else [])
                                  if c["m_id"] == SOURCE_SELECTION[1]), None)
        if colonne_selection is None:
            print(f"[Kinito] Rencontres (vues) : colonne {SOURCE_SELECTION[1]} de {SOURCE_SELECTION[0]} introuvable, "
                  "rien enregistré")
            return
        tf = fabrique_tableau(tf_libre, tf_fm)
        autres = {}   # v11 : les colonnes des autres fabriques de FM qui servent de modèle (lues seulement)
        for nom_fab in {f for _, _, (f, _), _, _ in COLONNES_V11 if f != FABRIQUE}:
            ff = mono(nb.env_of(FABRIQUES), nom_fab)
            if ff is not None:
                autres[nom_fab] = {c["m_id"]: c for c in ff.read_typetree()["m_rowData"]}
        pb = construire_fabrique(tf, colonne_selection, autres)
        if pb:
            print(f"[Kinito] Rencontres (vues) : {pb}, rien enregistré")
            return
        titres = {c["m_id"]: c["m_translationID"]["GameID"] for c in tf["m_rowData"]}
        if not set(COLONNES_MENU) | set(COLONNES_VUE) <= set(titres):
            print("[Kinito] Rencontres (vues) : colonnes de la fabrique inattendues, rien enregistré")
            return
        # 4. la collection (vue par défaut : la nôtre) et nos deux vues, depuis leurs originaux
        tc = hp.original(VUES, o["col"]) or o["col"].read_typetree()
        construire_collection(tc, tn, o["vue_rencontres"].path_id, titres, type_entree)
        tvr = hp.original(VUES, o["vue_rencontres"])
        if tvr is None:
            print(f"[Kinito] Rencontres (vues) : pas d'original de {VUE_RENCONTRES}, rien enregistré")
            return
        construire_vue(tvr, tp["m_tableView"], modele_colonne, COLONNES_VUE)
        # v20 : plus de vue du tableau à cases (VUE_FILTRE) : remise d'origine plus bas (_modifie_fm)
        for m in msgs:
            print(f"[Kinito] Rencontres (vues) : {BLOC} : {m}")
        print(f"[Kinito] Rencontres (vues) : {CELLULE} : spectateurs si le match est joué (binding.HasResult > "
              "binding.Attendance)")
        print(f"[Kinito] Rencontres (vues) : {LIGNE} : modèle de ligne (filtre par SIVisible, bandeau du mois au 1er "
              "match du mois, zone des cellules)")
        print(f"[Kinito] Rencontres (vues) : {PANNEAU} : panneau du filtre (Réinitialiser, {MASQUES} compétitions "
              "masquées au plus, hors compétition, lieu)")
        print(f"[Kinito] Rencontres (vues) : {CELLULE_DATE} : la date avec le jour (texte {TRAD_DATE_JOUR} de "
              f"{SOURCE_DATE})")
        print(f"[Kinito] Rencontres (vues) : {CELLULE_IA} : bouton d'équipe d'un club IA (clic = son programme)")
        print(f"[Kinito] Rencontres (vues) : {FABRIQUE_TABLEAU} : notre fabrique ({FABRIQUE} recopiée + nos colonnes, "
              f"{len(tf['m_rowData'])} colonnes)")
        print(f"[Kinito] Rencontres (vues) : {COLLECTION} : vue « Programme des rencontres » ({VUE_RENCONTRES}), vues "
              f"personnalisées, menu « Insérer colonne » ({len(COLONNES_MENU)} colonnes)")
        print(f"[Kinito] Rencontres (vues) : {VUE_RENCONTRES} : {', '.join(COLONNES_VUE)}")
        enregistrer(*o["bloc"])
        for om in repris:
            enregistrer(*om)
        o["fab_tab"].save_typetree(tf)
        nb._dirty.add(FABRIQUES)
        o["col"].save_typetree(tc)
        o["vue_rencontres"].save_typetree(tvr)
        nb._dirty.add(VUES)
        for objet, bundle, nom in _modifie_fm(o):   # v12 : ce que les anciennes versions avaient touché chez FM
            _remettre(objet, bundle, nom)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    o = etat_actuel()
    bloc = o["bloc"]
    if bloc is not None and (marques(bloc[3]) or first(bloc[3], lambda r: bloc[3].name(r) == NOM_CACHE) is not None):
        retirer_bloc(bloc)
        enregistrer(*bloc)
        print(f"{BLOC} : nos morceaux retirés, en-tête et liste de FM remis (le reste du bloc n'est pas touché)")
        fait = True
    for om, nom, test in ((o["cellule"], CELLULE, cellule_a_jour), (o["ligne"], LIGNE, ligne_modifiee),
                          (o["panneau"], PANNEAU, panneau_modifie),
                          (o["date"], CELLULE_DATE, cellule_date_a_jour),
                          (o["cellule_ia"], CELLULE_IA, cellule_ia_modifiee)):   # seuls propriétaires
        if om is None or not test(om[3]):
            continue
        bundle, obj, tt, t = om
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{nom} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        else:
            obj.save_typetree(orig)
            sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
            if sheet is not None:
                t.styles.sh, t.styles.changed = sheet, True
                t.styles.save()
            nb._dirty.add(bundle)
            fait = True
            print(f"{nom} : remise d'origine")
    for objet, bundle, test, nom in (
            (o["fab"], FABRIQUES, lambda x: fabrique_modifiee(x.read_typetree()), FABRIQUE),
            (o["fab_tab"], FABRIQUES, lambda x: fabrique_modifiee(x.read_typetree()), FABRIQUE_TABLEAU),
            (o["fab_comps"], FABRIQUES, lambda x: fabrique_comps_modifiee(x.read_typetree()), FABRIQUE_COMPS),
            (o["col"], VUES, lambda x: collection_modifiee(x.read_typetree()), COLLECTION),
            (o["vue_filtre"], VUES, vue_modifiee, VUE_FILTRE),
            (o["vue_v6"], VUES, vue_modifiee, VUE_FILTRE_V6),
            (o["vue_rencontres"], VUES, vue_modifiee, VUE_RENCONTRES)):
        if objet is not None and test(objet):
            orig = hp.original(bundle, objet)
            if orig is None:
                print(f"{nom} : pas de sauvegarde d'origine, rien fait")
            else:
                objet.save_typetree(orig)
                nb._dirty.add(bundle)
                fait = True
                print(f"{nom} : remise d'origine (le reste du bundle n'est pas touché)")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    o = etat_actuel()

    def dire(nom, objet, a_jour_, modifie, texte):
        print(f"{nom} : " + ("introuvable" if objet is None else f"{texte} (à jour)" if a_jour_(objet)
                            else "ANCIENNE version" if modifie(objet) else "d'origine"))

    bloc = o["bloc"]
    print(f"{BLOC} : " + ("introuvable" if bloc is None else f"tableau à la place de la liste (à jour, v{VERSION})"
                          if bloc_a_jour(bloc[3]) else "ANCIENNE version" if marques(bloc[3]) else "liste d'origine"))
    dire(CELLULE, o["cellule"], lambda x: cellule_a_jour(x[3]), lambda x: False, "spectateurs")
    dire(LIGNE, o["ligne"], lambda x: ligne_a_jour(x[3]), lambda x: ligne_modifiee(x[3]), "modèle de ligne")
    dire(PANNEAU, o["panneau"], lambda x: panneau_a_jour(x[3]), lambda x: panneau_modifie(x[3]), "panneau du filtre")
    dire(CELLULE_DATE, o["date"], lambda x: cellule_date_a_jour(x[3]), lambda x: False, "date avec le jour")
    dire(CELLULE_IA, o["cellule_ia"], lambda x: cellule_ia_a_jour(x[3]), lambda x: cellule_ia_modifiee(x[3]),
         "bouton d'équipe d'un club IA")
    dire(FABRIQUE_TABLEAU, o["fab_tab"], lambda x: fabrique_a_jour(x.read_typetree()),
         lambda x: fabrique_modifiee(x.read_typetree()), "notre fabrique")
    dire(COLLECTION, o["col"], lambda x: collection_a_jour(x.read_typetree()),
         lambda x: collection_modifiee(x.read_typetree()), f"vues des rencontres v{VERSION}")
    dire(VUE_RENCONTRES, o["vue_rencontres"], lambda x: vue_a_jour(x.read_typetree()), vue_modifiee,
         "vue « Programme des rencontres »")
    o_vf = o["vue_filtre"]   # v20 : plus utilisée (la liste à cases est retirée), attendue d'origine
    print(f"{VUE_FILTRE} (plus utilisée depuis la v20) : " + ("introuvable" if o_vf is None else
                                                               "MODIFIÉE par une ancienne version" if vue_modifiee(o_vf)
                                                               else "d'origine"))
    for objet, nom, modifie in ((o["fab"], FABRIQUE, lambda x: fabrique_modifiee(x.read_typetree())),
                                (o["fab_comps"], FABRIQUE_COMPS, lambda x: fabrique_comps_modifiee(x.read_typetree())),
                                (o["vue_v6"], VUE_FILTRE_V6, vue_modifiee)):
        print(f"{nom} (FM, jamais modifié en v12) : " + ("introuvable" if objet is None else
                                                          "MODIFIÉ par une ancienne version" if modifie(objet)
                                                          else "d'origine"))
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
            print("[Kinito] Rencontres (vues) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
