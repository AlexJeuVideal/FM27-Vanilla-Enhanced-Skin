"""[AJOUT KINITO] 26.20 — la bande du haut de la fiche joueur, À NOUS, en 1080p et affichage « Large » (06/11/2026).

Demande de Kinito (capture de S. Faye) : seulement en 1080p et en Large (Préférences de FM, « Affichage des
informations »), dans les quatre tailles du texte ; les autres tailles de fenêtre et d'affichage ne changent pas.
De gauche à droite :
  joueur (photo, nom, poste, taille, Actions) | nation (drapeau + 3 lettres, à côté la 2e ; sélections) au-dessus de
  l'âge (date de naissance) et du lieu de naissance | clubs (club parent / en prêt à) | réputation au-dessus du prix,
  puis temps de jeu, salaire et date de fin | Dispo. transfert au-dessus de Dispo. prêt | polygone | rapport de
  supervision (la note ; Niveau / Potentiel en étoiles quand il y a un rapport).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie « Ajouts Kinito » du menu.

v5 (Kinito, 06/11 : « ma fiche joueur doit être construite entièrement indépendante de celle d'Alex, et désactive la
sienne si la mienne est activée (pour le 1080p) » ; v1 à v4 étaient posées DANS la grande tuile d'Alex) :
- NOTRE bande, construite depuis les modèles D'ORIGINE de FM (sauvegardes de l'app : bannière 1080p
  report-player-banner-max, bloc du rapport, cellule de nation, tuile des statuts, bloc des clubs, Personnel, en-tête),
  avec notre code seulement : rien n'est importé de la tuile d'Alex (joueur_entete\\entete_tuile.py) ; ses réglages de
  départ (couleurs, marges, hauteur) sont recopiés ici et ne bougent plus quand il change les siens. Seul le moteur
  commun de l'app (lecture / écriture des fichiers) est le sien.
- Posée dans PlayerReportHeader, à la place 1080p de FM : l'aiguillage UseStandard (app.GridBreakpointIsStandard,
  faux = 1080p) choisit son enfant PAR POSITION ; à l'enfant 0, un conteneur à nous [SIVisible « mode > 0 » (Moyen,
  Petit) avec ce qui y était, tel quel : la tuile d'Alex ou la bannière de FM | SIVisible « mode == 0 » (Large) avec
  notre bande, une par taille du texte (SIVisible sur settings.TextScaling, par tranches)]. L'enfant 1 (autre taille
  de fenêtre) et UseSmall ne sont pas touchés.
- S'il refait sa tuile (autre version), son outil la refait DANS notre « sinon » (il cherche la bannière de FM où
  qu'elle soit, et ne touche qu'à ses propres noms) : notre bande reste.
- La photo de FM (hors de l'aiguillage, à gauche de la bannière) : la tuile d'Alex la cache partout (sa cachette) ; sans
  elle (en-tête de FM), elle serait à côté de notre bande, qui a la sienne -> cachée en 1080p Large seulement : la
  photo de FM dans un SIVisible « mode > 0 », et en Large deux doublures sous des copies des aiguillages de FM (rien en
  1080p, la photo aux autres tailles de fenêtre). Si ensuite sa tuile cache la photo, ce script repasse et retire nos
  doublures.

Comment (mesuré le 06/11/2026, lecture seule ; détail : chantier-entete-large\\ETUDE, sections 2 et 6) :
- LE DRAPEAU (mesuré dans le code du jeu) : FM n'affiche que le logo de la nation (nation_logo_<n°> : l'écusson
  de la fédé) ; les drapeaux (nation_flag_<n°>, AddrData\\flag-*) ne sont demandés par aucun écran, et la fonction
  d'image de FM n'a pas de cas pour eux. Ici : la fonction visuelle de FM StaticStringTacticalAnimation, citée par
  RIEN (bundles, scènes, code, autres fonctions, scripts), est réécrite avec le graphe de BindSIImage de FM
  (donnée -> AsString -> SetImageOrHide) et un Concat de FM glissé dedans : « nation_flag_ » + n° du pays. Même
  recette qu'Alex pour l'amical (club_amical, UIPickerDifference). L'image : celle de NationFlag_Medium (24 x 15),
  avec cette fonction et les arguments de BindSIText (clé vide + chemin). Si la fonction ne peut pas être posée, on
  garde le logo de FM (le message le dit).
- Lieu de naissance : le bloc de FM de Personnel > Vue d'ensemble (PersonPersonalBlock, PlaceOfBirthInfoBlock :
  « Dakar, Sénégal ») sous un titre à nous ; 2e nationalité : 1er élément de person.SecondaryNationalityList.
- Rapport : le bloc de FM (PlayerReportHeaderScoutSection), la note par son libellé court (gradinginfo.ShortGradeString,
  comme Kinito l'a vu en v3) ; chez un joueur d'un autre club, les étoiles du rapport sous la note.

ÉTAPE 2 (bloc v1, 06/11/2026, nuit) : le GRAND BLOC de la fiche (PlayerAttributesLargeBlock), à nous en 1080p Large.
Il n'existe que dans la composition « Large » de la Vue d'ensemble (point de rupture de la bannière « max ») : dans le
bloc, seul l'affichage est testé (settings.AdaptiveScalingLevelIndex). Notre bloc est rangé dans PlayerAttributesTile,
modèle de FM cité par RIEN, refait depuis son original à chaque passage ; dans le grand bloc, deux SIVisible sans
style autour de l'élément de FM qui porte tout (ExpandableContentElement) : [« mode > 0 » : lui, tel qu'Alex l'a
fait | « mode == 0 » : notre modèle inclus]. Les fonctions d'Alex ne voient jamais notre bloc (vérifié : elles
refont le leur par-dessus, résultat identique à « Alex seul »). Ce qu'il contient, recopié des modèles D'ORIGINE :
  postes (role_selector-large sans le poste écrit sous « Postes ») + légende | notes (AttributesTableTemplate :
  chaque colonne à sa largeur, mesurée dans les 20 langues, pieds écartés, Entraînement sous les pieds pour tes
  joueurs) | Infos (Personnalité + Rapports médias dans une place fixe pour le cas le plus long ; Caractéristiques et
  Suspensions qui défilent chacune dans sa moitié ; plus de taille ni de réputation, elles sont dans la bande) |
  Pour / Contre (une moitié chacun, qui défile). Postes et Pour / Contre ont la même largeur (au moins 210 px).
BLOC v2 (07/11/2026, la v1 vue en jeu par Kinito) : les 3 colonnes de notes à la MÊME largeur, réglée sur l'intitulé le
plus long en français et en anglais avec juste un petit écart (son choix : les autres langues coupent leurs intitulés
trop longs ; chez les gardiens, les deux « (tendance) » sont coupés) ; la place gagnée va à la colonne du terrain, qui
prend tout le reste et au moins les deux boutons Avec / Sans le ballon entiers ; Pour / Contre garde sa largeur v1.

BLOC v3 (07/11/2026, maquette 47 choisie par Kinito, « le bloc d'abord ») : postes (largeur fixe) | notes (comme la v2,
SANS l'Entraînement : il montera dans la bande, étape suivante) | une colonne qui prend le reste : en haut, deux moitiés
[Personnalité, Rapports avec les médias (à la ligne, jamais coupés), Projets (court terme / long terme, titres de FM
avec leur nombre, chaque projet sur une ligne avec « … ») | Taille, Réputation (le format de FM : titre au-dessus,
valeur dessous), Caractéristiques] ; dessous, le polygone des attributs (celui de la bande, cale fixe). Projets et
Caractéristiques défilent dans leur place. Les projets : la liste de FM (person.ShortTermPlanList, comme l'écran
Personnel ; elle demande l'équipe, que le grand bloc reçoit), élément par élément (la fonction de FM « élément n d'une
liste », comme la 2e nationalité de la bande) : la ligne de projet de FM (PlayerPlansRow) sert aussi à Personnel, on
n'y touche pas. Plus de Pour / Contre ni de Suspensions dans le bloc (la 47 les met dans la bande : étape suivante).

À VOIR EN JEU (bloc v3) : dans les 4 tailles du texte, un joueur de champ et un gardien : la colonne de droite (deux
moitiés, polygone dessous), la personnalité et les rapports médias à la ligne, les projets (court / long terme, leur
nombre, « Aucun projet », un projet long coupé avec « … » et sa phrase entière au survol), la taille et la réputation,
les caractéristiques ; 1080p Moyen / Petit et les autres tailles de fenêtre inchangés.

Usage : python kinito_entete_large.py appliquer|retirer|etat|si-actif [--dry-run]
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
from arbre import Tree, Styles, no_styles, PROPRIETES  # noqa: E402
from elements import first, typ, move, copy_usings, plain, types_ref_manquants  # noqa: E402
from langue import SUFFIXE, texte as L  # noqa: E402  (titre fixe fr / en : changer de langue change le nom posé)
import notes_installations as ni  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402

VERSION = 15  # v15 (Kinito, 08/11 : « ce qui concerne le contrat avec le contrat, son départ avec le départ », pour
#   TES joueurs) : dans la colonne des boutons, « Interroger l'agent sur l'intérêt suscité » à la place de « Discuter
#   d'un nouveau contrat avec l'agent » ; dans la case du contrat, à droite du salaire et de la date de fin, deux
#   boutons-icônes (_icones_contrat) : « Discuter d'un nouveau contrat avec l'agent » (bulle) et « Proposer nouveau
#   contrat » (contrat), mêmes règles (grisés quand FM ne donne pas l'action) ;
#   v14 (v13 vue en jeu, capture 52 et une vidéo) : le bouton grisé n'a plus le look grisé pendant que FM
#   charge le joueur (_bouton_gris : son gris vient seulement du SIEnabled person.IsPlayer) ;
#   v13 (v12 vue en jeu, captures 46-51 et une vidéo) : les boutons d'action avec NOTRE gabarit (sans icône,
#   une seule infobulle : le texte entier, puis l'explication de FM ; GABARIT_BOUTON) ; « Proposer un contrat » du
#   joueur libre = PersonApproachToSign ; l'infobulle du libellé fixe seulement sur le bouton grisé ;
#   v12 (v11 vue en jeu, captures 41-45 : Geubbels, Bonello libre, Mbappé) : les 4 premières colonnes de
#   la MÊME largeur (les boutons bien plus étroits : « … » si le texte ne tient pas, le texte entier au survol) ; la
#   date de fin de contrat SOUS « Fin de contrat », aussi grosse que le salaire ; un bouton d'action que FM retire
#   (action déjà faite, pas d'agent…) reste à sa place, GRISÉ (_bouton_gris) ; les boutons sous team = human.Team
#   comme FM (« Proposer un contrat » au joueur libre) ; un joueur que tu as prêté a TES boutons (son contrat est
#   chez toi : person.FullContract.MainTeam.IsHuman) ;
#   v11 (v10 vue en jeu, captures 34-40, option « polygone » choisie) : le POLYGONE DES ATTRIBUTS DANS LA
#   BANDE POUR DE BON (l'option disparaît) ; nouvel ordre : contrat (statut, salaire, fin de contrat ; cliquable comme
#   la bannière de FM) | valeur | dispos | boutons d'action de FM (selon le joueur : à toi, d'un autre club, libre) |
#   polygone des attributs | entraînement (tes joueurs) ou polygone de stats ; la valeur soulignée à la largeur de son
#   texte ; les 4 menus d'entraînement de la même largeur, la note et les pouces à côté du mot « Entraînement » ;
#   v10 (v9 vue en jeu, captures 32-33) : le polygone de stats du bout en étiquettes 10 px sur toute la
#   case (compétition et pouce par-dessus, dans les coins), et sans « flash » au changement de joueur (le graphique
#   deux fois plus grand dans une cale qui coupe : la technique d'Alex, voir _polygone_2x) ; option de l'app
#   entete_large_disposition : « polygone », le polygone des attributs dans la bande et le rapport dans le bloc ;
#   v9 (v8 vue en jeu, captures 30-31) : la bande sur TOUTE la largeur, sans photo ni étoiles (la carte
#   du joueur est entière dans le bloc, voir carte_bas47) ;
#   v6 (07/11) : la bande et la carte de la MAQUETTE 47 (voir « v6 » plus bas) ; v7 (v6 vue en jeu,
#   capture 28) : la carte en DEUX morceaux (le jeu coupe l'en-tête à son bord bas), la bande tient dans l'en-tête,
#   les chiffres en grand comme la maquette, la valeur sans cadre, le message sans rapport, le bout centré ;
#   v8 (v7 vue en jeu, capture 29) : le haut de la carte FERMÉ (bords et coins du bas, il finit au bord de l'en-tête :
#   le jeu coupe aussi la zone du bloc, 10 px plus bas, rien ne peut passer entre les deux) ; les étoiles calées sous
#   leur titre ; les intitulés des menus d'entraînement sur une ligne, « … » s'ils sont coupés ;
#   v2 (06/11, v1 vue en jeu par Kinito : « c'est bien mieux », drapeau affiché) : clubs APRÈS la nation /
#   l'âge ; 2e nationalité à côté de la 1re ; fin de contrat SOUS le salaire (3 lignes) ; Dispo. transfert / prêt sur
#   une ligne ; v3 : 1080p seulement, temps de jeu au-dessus du salaire, 3 lettres pour les deux nations, réputation,
#   étoiles du rapport, polygone au plus grand ; v4 : réputation au-dessus du prix, prix plus large ;
#   v5 : indépendante de la tuile d'Alex (voir l'en-tête)
VERSION_FN = 1   # la fonction du drapeau a son numéro à elle (vue en jeu en v1 : inchangée)
# v10 (08/11, captures 32-33) : une option de l'app d'Alex (entete_large_disposition) mettait au choix le rapport ou le
# polygone des attributs dans la bande ; v11 (captures 34-40, Kinito : « polygone en haut, fixe ») : l'option est
# retirée, le polygone est dans la bande et le rapport en bas de la colonne de droite du bloc, toujours
PREFIXE = "UIPickerKinitoEnteteLarge"
NOM_PLACE = f"{PREFIXE}Place"              # notre conteneur, enfant 0 de l'aiguillage UseStandard (place 1080p)
NOM_AUTRES = f"{PREFIXE}Autres"            # SIVisible « mode > 0 » : ce qui était à cette place, tel quel
NOM_LARGE = f"{PREFIXE}-v{VERSION}{SUFFIXE}"   # SIVisible « mode == 0 » : notre bande
NOM_PHOTO = f"{PREFIXE}Photo"              # autour de la photo de FM, quand rien d'autre ne la cache
NOM_PHOTO_FM = f"{PREFIXE}PhotoFM"         # SIVisible « mode > 0 » qui garde la photo de FM
ANCIENNE_RACINE = "UIPickerEnteteTuile-v"  # v1-v4 : nos morceaux étaient sous la racine de la tuile d'Alex
CACHE_ALEX = "UIPickerEnteteTuileCache"    # sa cachette (photo de FM cachée par sa tuile) : lue, jamais touchée
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_entete_large.actif")
MODELE = "PlayerReportHeader"
BANNIERE = "report-player-banner-max"      # la bannière de FM en 1080p (mesuré sur les captures de Kinito)
PHOTO = "PersonPictureFrame"
AIGUILLAGES = {"UseStandard": "app.GridBreakpointIsStandard", "UseSmall": "app.GridBreakpointIsSmall"}
MODE = "settings.AdaptiveScalingLevelIndex"   # Large 0, Moyen 1, Petit 2
TAILLE_TEXTE = "settings.TextScaling"      # Petit 85, Normal 100, Grand 110, Plus grand 120
OP_INF, OP_EGAL, OP_SUP = 0, 2, 4          # opérateurs des comparaisons de FM (BindIntToVisible)
TYPE_NATION = 1145176074                   # type de « nation » (cellules de nation de FM)
JOUEUR, EQUIPE = 1145176065, 1145176088    # types « personne » / « équipe » des remappers de FM

# la carte : réglages de départ recopiés de la grande tuile d'Alex (v19-v23, 06/11/2026), à nous depuis la v5
HAUT, ECART = 188, 12                      # hauteur de la carte (bannière 1080p) ; écart de part et d'autre des traits
FOND, BORD = (1.0, 1.0, 1.0, 0.045), (1.0, 1.0, 1.0, 0.12)
TRAIT = (1.0, 1.0, 1.0, 0.10)              # traits fins entre les blocs et dans les colonnes
RAYON, MARGE_COTES_INT = 12, 14            # coins ; marge intérieure à gauche / à droite
MARGE_HAUT, MARGE_COTES = 6, 28            # px au-dessus / au-dessous de la carte ; à gauche / à droite (bords de la fiche)
CELLULE = (6, 10)                          # marges intérieures d'une case (haut / bas, droite)
AGE_JEUNE = 21                             # moins de ... ans : sélections jeunes au lieu des sélections A
CLUB = "PlayerReportHeaderMaxTeamSection"  # bloc club de FM (nom court du club)
STATUT = "PlayerTransferStatusTile_2x2"    # tuile de FM : Dispo. transfert / Dispo. prêt (repérés par leur titre)
STATUT_CADRES = ["transfer-status-text", "loan-status-text"]
ANNEAUX = 4                                # anneaux intérieurs du polygone (FM : 1), comme celui de la fiche
GUID_ETIQUETTES = "a5645e1771c2b1549b0dfcd072c95560"   # SpiderChartColourGradedLabel_10px : étiquettes 10 px

# par taille du texte (tranches, pour qu'aucune valeur ne reste sans carte) : parts de la largeur de la carte
# (flex-basis 0 : rien ne dépend du contenu) et RAYON du polygone (px) demandé à FM, calculé avec SA formule
# (FMSpiderChart : UpdateLabelFitRadius / ValidateLayout, lus dans le code du jeu : rayon dessiné = min(demandé,
# max(rayon où les étiquettes tiennent dans la cale, demandé / 2))) et sa police (ABC Social, étiquettes 10 px en gras,
# 2 lignes en haut et en bas) : le plus grand qui tient en français et en anglais dans la cale (outils\mesure.py
# polygone 290 174) ; demandé pile, FM ne le réduit pas (pas de « flash »).
# v2 : mesuré sur la capture de Kinito (texte Plus grand, 1920 de large : ~120 px par part) ; v4 (pastille du prix
# coupée en Plus grand : « 284M € - 351M € » = 146 unités en 16,8 px gras, + icône et cadre) : le prix gagne
TAILLES_TEXTE = [
    ("petit", None, 95, dict(club=1.55, ident=2.0, nation=1.6, prix=1.85, statut=0.9, niveau=1.85), 54.0),
    ("normal", 95, 105, dict(club=1.6, ident=1.9, nation=1.6, prix=1.95, statut=0.95, niveau=1.75), 50.0),
    ("grand", 105, 115, dict(club=1.6, ident=1.85, nation=1.6, prix=2.05, statut=1.05, niveau=1.6), 47.5),
    ("plus-grand", 115, None, dict(club=1.5, ident=1.75, nation=1.6, prix=2.2, statut=1.15, niveau=1.55), 45.0),
]
POLYGONE_L = 290       # px de large de la cale du polygone ; hauteur = celle du contenu de la carte
PADDING_V = 6          # px en haut / en bas dans la carte
POLYGONE_MARGE_K = 4   # px de part et d'autre de la cale
V_NAT2 = "kinitonat2"   # variable de référence : la 2e nationalité (1er élément de SecondaryNationalityList)
LISTE_NAT2 = "person.SecondaryNationalityList"
SOURCE_ELEMENT = ("TransferBlockMainFrame", "firstItem")   # BindListItemUsingIndexToDestination de FM (26.13 v36)
CL_DATE = ["body-regular-14px-regular", "global-text-secondary", "content-no-wrap", "content-ellipsis"]
CHEMIN_DATE = "person.fullcontract.EndDateDescription"
CELLULE_CONTRAT = "text-cell-button-medium-secondary-text"   # v11 : la cellule du contrat de la bannière de FM
TITRE_LIEU = ("Lieu de naissance :", "Place of birth:")
NOTE_LONGUE, NOTE_COURTE = "gradinginfo.GradeString", "gradinginfo.ShortGradeString"

# propriétés de style écrites par ce script (numéros de la feuille de style de Unity, ceux de la tuile d'Alex)
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
               "right": (131103, 3)}.items():   # v10 (right : entre position et top, ordre de Unity)
    PROPRIETES.setdefault(_k, _v)

# ---------- le drapeau : une fonction visuelle de FM inutilisée, réécrite ----------
FONCTIONS = os.path.join(nb.AA, "ui-visualfunctions_assets_all.bundle")
FN_CIBLE = "df9cb9de795c5e84e8f746caa22d20cc"   # StaticStringTacticalAnimation (citée par rien, 06/11/2026)
NOM_CIBLE = "StaticStringTacticalAnimation"
FN_MODELE = "BindSIImage"                       # son graphe recopié : donnée -> AsString -> SetImageOrHide
FN_CONCAT = "BindManagerIconFromSettingsByName"  # un graphe de FM qui a un nœud TextFunctions_Concat (recopié)
NOM_FN = f"UIPickerKinitoDrapeau-v{VERSION_FN}"
DEBUT_DRAPEAU = "nation_flag_"                  # GraphicsUtils.ResolveResourceID, ResourceType.Flag (15)
SOURCE_DRAPEAU = "NationFlag_Medium"            # l'image de FM (son SIImage et sa boîte)
CL_DRAPEAU = "nation-flag-medium-24px"          # règle de FM : 24 x 15 px (26.19 v5) = proportions des drapeaux 128 x 80
CL_TEXTE_LIEU = ["body-regular-14px-regular", "global-text-primary", "content-no-wrap", "content-ellipsis"]
SOURCE_ARGS = ("PlayerReportHeaderScoutSection", "ScoutReport")   # un SIText à BindSIText : (clé, chemin)
SOURCE_TEXTE_NATION = "nation-cell-medium-bold"  # le texte du nom de la nation (primary-text)
SOURCE_LIEU = "PersonPersonalBlock"             # Personnel > Vue d'ensemble : PlaceOfBirthInfoBlock, CityOfBirthVisible
CHEMIN_UNIQUE = "nation.UniqueId"


def _objets(bundle):
    """{guid: objet} des assets du bundle (sa table m_Container), ou None (comme club_amical d'Alex)"""
    if not os.path.exists(bundle):
        return None
    env = nb.env_of(bundle)
    par_pid = {o.path_id: o for o in env.objects}
    for o in env.objects:
        if o.type.name == "AssetBundle":
            return {k.lower(): par_pid.get(v["asset"]["m_PathID"]) for k, v in o.read_typetree()["m_Container"]}
    return None


def _par_nom(fns, nom):
    for o in fns.values():
        if o is None or o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == nom:
                return o.read_typetree()
        except Exception:
            continue
    return None


def _noeuds(g, classe):
    return [r for r in g["references"]["RefIds"] if r["type"]["class"] == classe]


def _id_neuf():
    return {"m_idBytes": list(os.urandom(16))}


ZERO = {"m_idBytes": [0] * 16}


def graphe_drapeau(modele, g_concat, cible):
    """typetree de cible refait avec le graphe de modele (BindSIImage) et un Concat (« nation_flag_ » + texte) entre
    AsString et SetImageOrHide ; None si un graphe n'a pas la forme attendue"""
    g = copy.deepcopy(modele)
    a = _noeuds(g, "TypedValueVisualFunctionLibrary_AsString")
    inv = [r for r in _noeuds(g, "InvokeNode") if r["data"].get("m_name") == "SetImageOrHide"]
    att = _noeuds(g, "VisualBindings_Wait")
    cc = _noeuds(g_concat, "TextFunctions_Concat")
    if len(a) != 1 or len(inv) != 1 or len(att) != 1 or len(cc) != 1:
        return None
    a, inv, att = a[0]["data"], inv[0]["data"], att[0]["data"]
    image = next((s for s in inv["m_inputDataSockets"] if s["m_name"] == "ImageID"), None)
    # la forme mesurée : Wait (fin) -> SetImageOrHide ; AsString -> son ImageID
    if image is None or image["m_sourceID"] != a["m_dataOutString"]["m_id"] \
            or att["m_asyncOutComplete"]["m_destinationID"] != inv["m_inputExecSocket"]["m_id"]:
        return None
    c = copy.deepcopy(cc[0])
    c["rid"] = max(r["rid"] for r in g["references"]["RefIds"]) + 1
    d = c["data"]
    d["m_id"] = _id_neuf()
    for k in ("m_execInExecInput", "m_execOutExecOutput", "m_dataInText", "m_dataInText1", "m_dataOutString"):
        d[k]["m_id"] = _id_neuf()
    d["m_parentID"] = copy.deepcopy(a["m_parentID"])
    d["m_position"] = {"x": (a["m_position"]["x"] + inv["m_position"]["x"]) / 2, "y": a["m_position"]["y"] - 80}
    d["m_dataInText"]["m_sourceID"] = copy.deepcopy(ZERO)
    d["m_dataInText"]["m_defaultSocketValue"] = {"m_value": DEBUT_DRAPEAU}
    d["m_dataInText1"]["m_sourceID"] = copy.deepcopy(a["m_dataOutString"]["m_id"])
    d["m_execOutExecOutput"]["m_destinationID"] = copy.deepcopy(inv["m_inputExecSocket"]["m_id"])
    att["m_asyncOutComplete"]["m_destinationID"] = copy.deepcopy(d["m_execInExecInput"]["m_id"])
    image["m_sourceID"] = copy.deepcopy(d["m_dataOutString"]["m_id"])
    g["m_nodes"].append({"rid": c["rid"]})
    g["references"]["RefIds"].append(c)
    # identité de la cible gardée (son m_id), nom = notre repère ; tout ce qui est rattaché au m_id du modèle (nœuds,
    # entrées, sorties, variables) l'est à celui de la cible (Alex, club_amical v14 : entrées oubliées -> plantage)
    ancien, nouveau = modele["m_id"]["m_idBytes"], cible["m_id"]["m_idBytes"]

    def rattacher(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "m_parentID" and isinstance(v, dict) and v.get("m_idBytes") == ancien:
                    x[k] = {"m_idBytes": list(nouveau)}
                else:
                    rattacher(v)
        elif isinstance(x, list):
            for v in x:
                rattacher(v)
    rattacher(g)
    for k in ("m_GameObject", "m_Enabled", "m_Script", "m_id"):
        g[k] = copy.deepcopy(cible[k])
    g["m_Name"] = g["m_name"] = NOM_FN
    return g


def poser_drapeau():
    """(ok, messages) : la fonction du drapeau posée (ou déjà là) ; ok faux = on garde le logo de FM"""
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None:
        return False, ["fonction de FM à réécrire introuvable (mise à jour de FM ?) : logo de la nation gardé"]
    actuel = obj.read_typetree()
    if actuel.get("m_Name") == NOM_FN:
        return True, []
    if str(actuel.get("m_Name", "")).startswith("UIPicker") and not str(actuel["m_Name"]).startswith(
            "UIPickerKinitoDrapeau"):
        return False, [f"{NOM_CIBLE} déjà réécrite par une autre fonction ({actuel['m_Name']}) : logo gardé"]
    cible = hp.original(FONCTIONS, obj) or actuel
    modele, concat = _par_nom(fns, FN_MODELE), _par_nom(fns, FN_CONCAT)
    if cible.get("m_Name") != NOM_CIBLE or modele is None or concat is None or cible["m_Script"] != modele["m_Script"]:
        return False, [f"fonctions de FM {NOM_CIBLE} / {FN_MODELE} / {FN_CONCAT} introuvables : logo gardé"]
    g = graphe_drapeau(modele, concat, cible)
    if g is None:
        return False, [f"graphe de {FN_MODELE} ou {FN_CONCAT} inattendu : logo gardé"]
    for n in types_ref_manquants(obj, g):
        print(f"{NOM_FN} : type {n} déclaré dans le bundle (recopié)")
    obj.save_typetree(g)
    nb._dirty.add(FONCTIONS)
    return True, [f"fonction de FM inutilisée {NOM_CIBLE} réécrite : « {DEBUT_DRAPEAU} » + n° du pays -> image"]


def retirer_drapeau():
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    if obj is None or not str(obj.read_typetree().get("m_Name", "")).startswith("UIPickerKinitoDrapeau"):
        return []
    orig = hp.original(FONCTIONS, obj)
    if orig is None:
        return [f"{NOM_CIBLE} : pas de sauvegarde d'origine, laissée (vérification des fichiers Steam)"]
    obj.save_typetree(orig)
    nb._dirty.add(FONCTIONS)
    return [f"{NOM_CIBLE} : remise d'origine"]


def drapeau_a_jour():
    fns = _objets(FONCTIONS)
    obj = fns and fns.get(FN_CIBLE)
    return obj is not None and obj.read_typetree().get("m_Name") == NOM_FN


# ---------- petits outils (à nous) ----------
class Src:
    """un modèle de FM D'ORIGINE (sauvegarde de l'app, feuille de style d'origine comprise) : jamais ce qu'un autre
    script en a fait dans le jeu ; recopié avec ses styles et ses modèles inclus"""
    def __init__(self, modele):
        o = hp.ouvrir(modele, depart_original=True)
        self.s = o[3] if o is not None else None
        self.styles = self.s.styles if self.s is not None else None

    def clone(self, t, r, parent, index=None):
        c = t.clone(r, parent, index, src=self.s)
        copy_usings(t, self.s, r)
        t.styles.copy_from(self.styles, t, c)
        return c


def boite(t, parent, css, classes=(), nom=""):
    b = plain(t, parent, None, list(classes), nom)
    t.elem(b)["m_RuleIndex"] = -1
    if nom:
        t.sd(b)["name_UxmlAttributeFlags"] = 1
    if css:
        t.styles.style(t, b, css)
    return b


def trait_vertical(t, parent):
    boite(t, parent, {"width": 1, "min-width": 1, "flex-shrink": 0, "align-self": "stretch",
                      "background-color": TRAIT})


def remapper(t, modele_rm, parent, liens, classes=()):
    rm = t.clone_shallow(modele_rm, parent)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": k, "to": {"m_path": p}, "type": {"id": ty}}
                            for k, (p, ty) in liens.items()]
    t.elem(rm)["m_Classes"], t.elem(rm)["m_RuleIndex"] = list(classes), -1
    return rm


def titre(t, k, parent, fr, en):
    """petit titre fixe (style du titre « Rapport de supervision » de FM : body-xs-strong, gris)"""
    c = t.clone(k.txt_rid, parent, src=k.txt.s)
    no_styles(t, c)
    sd = t.sd(c)
    sd["name"] = ""
    sd["text"], sd["text_UxmlAttributeFlags"] = L(fr, en), 1
    sd["DebugDisplay"] = sd["text"]
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    t.elem(c)["m_Classes"] = ["body-xs-strong", "global-text-secondary", "content-ellipsis"]
    return c


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
    """morceaux de la bannière 1080p de FM (d'origine) à recopier, repérés par contenu : (dict nom -> rid, manquants)"""
    nom_txt = first(s, lambda r: "person.Name" in str(s.sd(r).get("TextBinding") or ""))
    poste = first(s, lambda r: "PositionCombinedStringLong" in _surcharges(s, r))
    flags = first(s, lambda r: s.name(r) == "PlayerStatusFlagsForTeamVisible")
    caps = first(s, lambda r: {"StandardTextTooltip", "text-cell-button-medium"}
                 <= {_alias(s, k) for k in s.children(r)})
    age = first(s, lambda r: _alias(s, r) == "data_display-cell-standard-regular" and "Person.Age" in _surcharges(s, r))
    club = first(s, lambda r: _alias(s, r) == CLUB)
    valeur = first(s, lambda r: typ(s, r).endswith("BindingRemapper")
                   and any(m.get("from") == "TransferValueRange" for m in s.sd(r).get("Mappings") or []))
    contrat = first(s, lambda r: typ(s, r).endswith("BindableSwitchElement")
                    and "person.fullcontract.IsValid" in str(s.sd(r).get("Binding") or ""))
    actions = first(s, lambda r: s.name(r) == "FrameActions")
    setter = first(s, lambda r: typ(s, r).endswith("BindingSetter"))
    p = dict(nom=nom_txt is not None and s.parent[nom_txt], poste=poste is not None and s.parent[poste],
             flags=flags is not None and s.parent[flags], caps=caps, age=age, club=club, valeur=valeur,
             contrat=contrat, actions=actions, setter=setter)
    return p, [f"bannière : {k}" for k, v in p.items() if v is None or v is False]


def _chemin_direct(t, r):
    b = t.sd(r).get("Binding") if r in t.refs else None
    return ((b or {}).get("m_direct") or {}).get("Path", {}).get("m_path", "") if isinstance(b, dict) else ""


def aiguillage(t, nom):
    """l'aiguillage de FM (UseStandard / UseSmall) par son nom ET son chemin (nos copies n'ont pas de nom)"""
    return first(t, lambda r: typ(t, r).endswith("BindableSwitchElement") and t.name(r) == nom
                 and _chemin_direct(t, r) == AIGUILLAGES[nom])


def ancetres(t, r):
    noms = []
    while r in t.parent:
        r = t.parent[r]
        noms.append(t.name(r) or "")
    return noms


# ---------- la carte « Large » ----------
class Sources:
    """morceaux de FM nécessaires, pris dans les modèles d'origine (repérés par contenu)"""
    def __init__(self, t, avec_drapeau):
        self.src = Src(BANNIERE)
        self.p, self.manque = pieces(self.src.s) if self.src.s is not None else ({}, [BANNIERE])
        self.txt = Src(SOURCE_ARGS[0])
        s = self.txt.s
        self.txt_rid = s and first(s, lambda r: typ(s, r).endswith("SIText") and s.name(r) == SOURCE_ARGS[1])
        self.entete = Src(MODELE)
        e = self.entete.s
        self.photo = e and first(e, lambda r: e.name(r) == PHOTO)
        # modèles pris dans le jeu (clone_shallow : même modèle) : ce sont des éléments de FM qu'on ne modifie pas
        self.rm_model = first(t, lambda r: typ(t, r).endswith("BindingRemapper"))
        self.sw_std, self.sw_petit = aiguillage(t, "UseStandard"), aiguillage(t, "UseSmall")
        o = hp.ouvrir("PlayerAttributesLargeBlock", depart_original=True)
        self.fa = o and o[3]
        fa = self.fa
        self.haut = fa and first(fa, lambda r: fa.name(r) == "PersonHeightTextFrame")
        self.reputation = fa and first(fa, lambda r: fa.name(r) == "PlayerReputationTextFrame")
        self.chart = fa and first(fa, lambda r: typ(fa, r).endswith("FMSpiderChart"))
        self.s_vis, self.vis = ni.visible_model()
        # drapeau : la boîte de l'image de FM (nation-flag-medium-24px) et son SIImage
        self.fl = Src(SOURCE_DRAPEAU)
        f = self.fl.s
        img = f and first(f, lambda r: typ(f, r).endswith("SIImage") and f.name(r) == "NationFlag")
        self.boite_drapeau = img is not None and f.parent[img]
        self.avec_drapeau = avec_drapeau
        self.liaison_drapeau = None
        if img is not None and self.txt_rid is not None:
            tb = copy.deepcopy(s.sd(self.txt_rid).get("TextBinding") or {})
            vf = tb.get("m_visualFunction") or {}
            args = ni.decode_args((vf.get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or [])
            if len(args) == 2 and args[0][0].endswith(b"BindingKeyVisualArg") \
                    and args[1][0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                b = copy.deepcopy(f.sd(img)["Binding"])
                b["m_visualFunction"]["m_target"] = {"m_guid": FN_CIBLE}
                b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = \
                    ni.make_binding(tb, OP_EGAL, [CHEMIN_UNIQUE])["m_visualFunction"]["m_inputs"]["m_variable"][
                        "m_argumentBytes"]
                self.liaison_drapeau = b
        # nom de la nation (le texte de la cellule de FM, en gras)
        self.nt = Src(SOURCE_TEXTE_NATION)
        n = self.nt.s
        self.texte_nation = n and first(n, lambda r: typ(n, r).endswith("SIText"))
        # lieu de naissance (Personnel > Vue d'ensemble)
        self.lieu = Src(SOURCE_LIEU)
        li = self.lieu.s
        self.bloc_lieu = li and first(li, lambda r: li.name(r) == "PlaceOfBirthInfoBlock")
        self.vis_direct = li and first(li, lambda r: li.name(r) == "CityOfBirthVisible")
        self.clubs = Src(CLUB)
        self.statut = Src(STATUT)
        # la fonction de FM « élément n d'une liste » (2e nationalité) et un texte de FM pour la date de fin
        self.fn_element = fonction_element()
        ss = self.src.s
        contrat = self.p.get("contrat")
        self.texte_date = ss is not None and contrat and next(
            (r for r in ss.walk(contrat) if typ(ss, r).endswith("SIText") and ss.name(r) == "DashedString"), None)
        self._sources_47()

    def _sources_47(self):
        """v6 (maquette 47) : les morceaux de FM d'origine de la nouvelle bande"""
        st = self.statut.s
        tt = st and first(st, lambda r: st.name(r) == STATUT_CADRES[0])
        rep = tt is not None and next((x for x in st.children(st.parent[tt]) if x != tt and typ(st, x).endswith("SIText")),
                                      None)
        self.cl_reponse = list(st.elem(rep).get("m_Classes") or []) if rep else None   # « Non déf. » (gras)
        s = self.txt.s   # le BindingRemapper du rapport de FM (report -> PlayerReportForContextTeam, team -> human.team)
        self.rm_rapport = s and first(s, lambda r: typ(s, r).endswith("BindingRemapper") and any(
            m.get("from") == "report" for m in s.sd(r).get("Mappings") or []))
        self.pc = Src("ScoutedProsAndCons")   # titres « Pour » / « Contre » (pouce + mot)
        pc = self.pc.s
        self.pc_tetes = []
        for nom in ("pros", "cons"):
            x = pc and first(pc, lambda r, nom=nom: pc.name(r) == nom)
            self.pc_tetes.append(pc.children(x)[0] if x is not None and pc.children(x) else None)
        self.pc_ligne = Src("data_display-string-list-item-pro-con")   # l'icône de FM d'un Pour / Contre
        pl = self.pc_ligne.s
        self.pc_icone = pl and first(pl, lambda r: typ(pl, r).endswith("SIImage")
                                     and "0043cf8d" in _liaison(pl, r, "Binding"))
        # v9 (Kinito, 07/11 : « les icônes d'Alex pour le rapport procons ») : la liste de FM qui montre un modèle par
        # élément (WrappedObjectList, celle qu'Alex prend pour ses pastilles), et sa pastille, si elle est dans le jeu
        self.liste_src = Src("TeamMeetingBlock")
        ls = self.liste_src.s
        self.liste_pc = ls and first(ls, lambda r: ls.name(r) == "Players" and typ(ls, r).endswith("WrappedObjectList"))
        self.pastille_alex = pastille_alex()
        self.bulle_src = Src("role_selector-large")   # une infobulle de FM (StandardTextTooltip) avec son texte
        bs = self.bulle_src.s
        self.bulle = bs and first(bs, lambda r: _alias(bs, r) == "StandardTextTooltip" and any(
            isinstance(((bs.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}).get("TextBinding"), dict)
            for ov in bs.elem(r).get("m_SerializedDataOverride") or []))
        self.traits = Src("PlayerTraitsFrameList")   # titre « Entraînement » (le titre des Caractéristiques)
        self.titre_traits = _premier(self.traits.s, lambda r: self.traits.s.name(r) == "TraitsTitleFrame")
        self.note = Src("IndividualTrainingPlayerHeaderContent")   # la note à l'entraînement
        n = self.note.s
        cell = _premier(n, lambda r: _alias(n, r) == "PlayerTrainingRatingCell")
        self.note_rm = n.parent[cell] if cell is not None else None
        self.boutons = Src("PlayerReportDevelopmentProgressReportBlock")   # Féliciter / Critiquer
        sb = self.boutons.s
        self.pouces = {nom: _premier(sb, lambda r, nom=nom: sb.name(r) == nom and typ(sb, r) == "FM.UI.FMActionButton")
                       for nom in POUCES}
        self.gabarits = all(_gabarit_kinito(cle, modele) for cle, modele, _ in POUCES.values())
        self.opts = Src("PlayerIndividualTrainingOptionsBlock_4x4")   # les 4 menus d'entraînement
        self.perf = Src("PlayerPerformanceDataTile_8x4")   # le polygone de stats de FM
        pf = self.perf.s
        self.perf_rm = pf and first(pf, lambda r: typ(pf, r).endswith("BindingRemapper") and any(
            m.get("from") == "polygonobservation" for m in pf.sd(r).get("Mappings") or []))
        vis = [r for r in (pf.walk(self.perf_rm) if self.perf_rm is not None else [])
               if typ(pf, r).endswith("SIVisible") and "PerformanceReasonValue" in _liaison(pf, r, "Binding")]
        self.perf_ok = vis[0] if len(vis) >= 1 else None
        self.perf_ko = vis[1] if len(vis) >= 2 else None
        self.perf_titre = self.perf_ok is not None and next(
            (r for r in pf.walk(self.perf_ok) if typ(pf, r).endswith("SIText")
             and "Competition.Name" in _liaison(pf, r, "TextBinding")), None)
        self.perf_switch = self.perf_ok is not None and next(
            (r for r in pf.walk(self.perf_ok) if typ(pf, r).endswith("BindableSwitchElement")
             and "DataPointList" in _liaison(pf, r, "Binding")), None)
        self.perf_rm_valeur = self.perf_ok is not None and next(
            (r for r in pf.walk(self.perf_ok) if typ(pf, r).endswith("BindingRemapper") and any(
                m.get("from") == "performanceValue" for m in pf.sd(r).get("Mappings") or [])), None)
        self.pfd = Src("PerformanceFeedbackDisplay")
        pd = self.pfd.s
        self.pfd_vis = pd and first(pd, lambda r: pd.name(r) == "HasPerformanceValue")
        # v11 : la cellule du contrat de FM (son bouton et son trait de soulignement) et son clic dans la bannière
        self.cellule = Src(CELLULE_CONTRAT)
        ce = self.cellule.s
        self.cellule_bouton = ce and first(ce, lambda r: typ(ce, r).endswith("SIButton") and ce.name(r) == "CellButton")
        self.clic_contrat = None
        ss = self.src.s
        inst = ss and first(ss, lambda r: _alias(ss, r) == CELLULE_CONTRAT)
        for ov in (ss.elem(inst).get("m_SerializedDataOverride") or []) if inst is not None else []:
            ev = ((ss.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}).get("Events")
            if isinstance(ev, dict) and ev.get("m_bytes"):
                self.clic_contrat = copy.deepcopy(ev)
        # v12 : le SIEnabled du bouton d'action de FM (son opacité des boutons grisés), pour nos boutons grisés
        self.actif_src = Src("GenericActionButtonWidget")
        ga = self.actif_src.s
        self.actif = ga and first(ga, lambda r: typ(ga, r).endswith("SIEnabled")
                                  and "item.Disabled" in _liaison(ga, r, "Binding"))
        # v13 : les morceaux du gabarit des boutons d'action de FM, pour le nôtre (construire_gabarit)
        self.g_liste = Src("ActionsListWidget")
        self.g_donnees = Src("GenericActionButtonDataWidget")
        self.gab = morceaux_gabarit(self.g_liste.s, ga, self.g_donnees.s)

    def manquants(self):
        m = list(self.manque)
        for nom, v in (("fonction élément d'une liste", self.fn_element), ("texte de la date", self.texte_date),
                       ("titre", self.txt_rid), ("photo", self.photo), ("remapper", self.rm_model),
                       ("aiguillage UseStandard", self.sw_std), ("aiguillage UseSmall", self.sw_petit),
                       ("SIVisible", self.vis), ("image du drapeau", self.boite_drapeau),
                       ("texte de la nation", self.texte_nation), ("lieu de naissance", self.bloc_lieu),
                       ("SIVisible direct", self.vis_direct), ("clubs", self.clubs.s), ("statuts", self.statut.s),
                       ("réputation", self.reputation), ("taille", self.haut), ("polygone", self.chart),
                       # v6 (maquette 47)
                       ("remapper du rapport", self.rm_rapport), ("titre Pour", self.pc_tetes[0]),
                       ("titre Contre", self.pc_tetes[1]), ("icône Pour / Contre", self.pc_icone),
                       ("infobulle de FM", self.bulle), ("titre des caractéristiques", self.titre_traits),
                       ("note à l'entraînement", self.note_rm), ("menus d'entraînement", self.opts.s),
                       ("tuile des données de la prestation", self.perf_rm), ("prestation : avec données",
                                                                              self.perf_ok),
                       ("prestation : sans données", self.perf_ko), ("prestation : titre", self.perf_titre),
                       ("prestation : polygone", self.perf_switch), ("prestation : appréciation",
                                                                     self.perf_rm_valeur),
                       ("appréciation de FM", self.pfd_vis),
                       # v11
                       ("cellule du contrat de FM", self.cellule_bouton), ("clic du contrat de FM", self.clic_contrat),
                       # v12
                       ("SIEnabled du bouton d'action de FM", self.actif)):
            if v is None or v is False:
                m.append(nom)
        for nom, v in self.gab.items():   # v13
            if v is None or v is False:
                m.append(f"gabarit des boutons d'action de FM : {nom}")
        m += [f"bouton {x}" for x, v in self.pouces.items() if v is None]
        if self.avec_drapeau and self.liaison_drapeau is None:
            m.append("liaison du drapeau")
        return m


def fonction_element():
    """la fonction de FM « élément n d'une liste » (BindListItemUsingIndexToDestination, 21ee6b43), celle de
    TransferBlockMainFrame qui met le 1er élément dans firstItem, recopiée avec ses arguments (comme 26.13 v36,
    vue en jeu) ; None si introuvable"""
    o = hp.ouvrir(SOURCE_ELEMENT[0], depart_original=True)
    if o is None:
        return None
    tm = o[3]
    for r in tm.walk():
        fs = tm.sd(r).get("BindFunction") if r in tm.refs else None
        for f in fs if isinstance(fs, list) else []:
            if (f.get("m_target") or {}).get("m_guid", "").startswith("21ee6b43"):
                args = ni.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
                if len(chemins) == 2 and bytes(chemins[1][1]).endswith(SOURCE_ELEMENT[1].encode()) \
                        and sum(1 for a in args if bytes(a[0]).endswith(b"Int32VisualArg")) == 1:
                    return copy.deepcopy(f)
    return None


def _chemin_arg(c):
    b = c.encode()
    return bytes([1, len(b)]) + b   # (longueur < 128 : un octet)


def element_de_liste(fn, liste, index, destination):
    f = copy.deepcopy(fn)
    args = ni.decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
    chemins[0][1], chemins[1][1] = _chemin_arg(liste), _chemin_arg(destination)
    next(a for a in args if bytes(a[0]).endswith(b"Int32VisualArg"))[1] = struct.pack("<i", index)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
    return f


def visible(t, k, parent, index, nom, liaison, css=None):
    v = ni.new_visible(t, k.s_vis, k.vis, parent, index, nom, liaison, ["column-direction-normal"])
    if nom:
        t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, v, {"align-self": "stretch", "flex-shrink": 0, **(css or {})})
    return v


def visible_direct(t, k, parent, chemin):
    """SIVisible de FM « visible si <chemin> n'est pas nul » (CityOfBirthVisible recopié, sans enfants)"""
    v = t.clone(k.vis_direct, parent, src=k.lieu.s)
    for c in list(t.children(v)):
        t.remove(c)
    no_styles(t, v)
    sd = t.sd(v)
    sd["name"] = ""
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    t.elem(v)["m_Classes"] = []
    return v


def ligne_nation(t, k, parent, chemin, texte="nation.Name", css=None):
    """[drapeau] Nom du pays (nation = chemin ; texte : nom complet, ou ThreeLetterName) ; le drapeau par notre
    fonction, sinon le logo de FM"""
    rm = remapper(t, k.rm_model, parent, {"nation": (chemin, TYPE_NATION)},
                  ["row-direction-normal", "align-items-center"])
    t.styles.style(t, rm, {"flex-shrink": 1, "min-width": 0, **(css or {})})
    b = k.fl.clone(t, k.boite_drapeau, rm)
    t.sd(b)["name"] = ""
    t.elem(b)["m_Classes"] = [CL_DRAPEAU]   # la boîte de FM porte « small-16px » : 24 x 15 (proportions du drapeau)
    t.styles.style(t, b, {"flex-shrink": 0, "margin-right": 6})
    if k.avec_drapeau and k.liaison_drapeau is not None:
        for r in t.walk(b):
            if typ(t, r).endswith("SIImage"):
                t.sd(r)["Binding"] = copy.deepcopy(k.liaison_drapeau)
                t.sd(r)["name"] = ""
    tx = k.nt.clone(t, k.texte_nation, rm)
    sd = t.sd(tx)
    sd["name"] = ""
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = texte
    sd["TextBinding_UxmlAttributeFlags"] = 1
    t.elem(tx)["m_Classes"] = list(dict.fromkeys(list(t.elem(tx).get("m_Classes") or [])
                                                 + ["content-no-wrap", "content-ellipsis"]))
    t.styles.style(t, tx, {"flex-shrink": 1, "min-width": 0})
    return rm


def _liaison(t, r, cle):
    """une liaison de FM lue en texte : le JSON, plus les octets de ses arguments décodés (les chemins d'une
    fonction de FM y sont écrits en octets, json.dumps ne les montre pas)"""
    b = t.sd(r).get(cle) if r in t.refs else None
    if not isinstance(b, dict):
        return ""
    o = ((b.get("m_visualFunction") or {}).get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or []
    return json.dumps(b) + bytes(o).decode("latin-1")


def seul(t, s, rid, parent, index=None):
    """un élément de FM recopié SEUL (sans enfants ni styles), sans nom"""
    r = t.clone(rid, parent, index, src=s)
    for c in list(t.children(r)):
        t.remove(c)
    no_styles(t, r)
    t.sd(r)["name"] = ""
    t.elem(r)["m_Classes"] = []
    return r


def nation_secondaire(t, k, parent):
    """v2 (Kinito) : à côté de la 1re nationalité, la 2e (seulement elle s'il y en a plus) : drapeau + 3 lettres. Un
    BindingSetter de FM (celui de la bannière, vidé) déclare V_NAT2 (référence sans type, comme 26.13 v36) et y met
    le 1er élément de SecondaryNationalityList ; visible seulement s'il y en a une"""
    s = seul(t, k.src.s, k.p["setter"], parent)
    sd = t.sd(s)
    sd["ValueVariables"], sd["ValueVariables_UxmlAttributeFlags"] = [], 1
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": V_NAT2}]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"] = [element_de_liste(k.fn_element, LISTE_NAT2, 0, V_NAT2)]
    sd["BindFunction_UxmlAttributeFlags"] = 1
    t.elem(s)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, s, {"flex-shrink": 0, "margin-left": 10})
    v = visible_direct(t, k, s, V_NAT2)
    t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    ligne_nation(t, k, v, V_NAT2, "nation.ThreeLetterName", {"flex-shrink": 0})
    return s


def contrat_3_lignes(t, k, c):
    """v2 (Kinito : « on ne voit pas la date ») : la cellule de FM écrit salaire et date côte à côte (date coupée) ;
    sa date est vidée (texte fixe vide, la surcharge de FM sur EndDateDescription) et la date passe dessous, dans un
    texte de FM à nous (DashedString recopié) ; v3 : le temps de jeu en 1er : 3 lignes. Message si la forme a changé"""
    inst = next((r for r in t.walk(c) if t.elem(r).get("m_TemplateAlias") == "text-cell-button-medium-secondary-text"),
                None)
    if inst is None:
        return ["cellule salaire / date de fin introuvable : date laissée à côté du salaire"]
    vide = 0
    for ov in t.elem(inst).get("m_SerializedDataOverride") or []:
        d = (t.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}
        tb = d.get("TextBinding") or {}
        if "EndDateDescription" in str((tb.get("m_direct") or {}).get("Path")):
            d["TextBinding"] = copy.deepcopy(tb)
            d["TextBinding"]["m_kind"] = 0
            d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            d["text"], d["text_UxmlAttributeFlags"] = "", 1
            vide += 1
    if vide != 1:
        return [f"date de fin dans la cellule du salaire : {vide} surcharge(s) au lieu de 1 (introuvable)"]
    t.elem(inst)["m_Classes"] = []   # (FM : margin-bottom-global-gap-regular ; 3 lignes à faire tenir)
    par = t.parent[inst]
    d = seul(t, k.src.s, k.texte_date, par, t.children(par).index(inst) + 1)
    sd = t.sd(d)
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = CHEMIN_DATE
    sd["TextBinding_UxmlAttributeFlags"] = 1
    t.elem(d)["m_Classes"] = list(CL_DATE)
    t.styles.style(t, d, {"margin-top": 1, "margin-bottom": 2, "flex-shrink": 0})
    tj = next((x for x in t.children(par) if typ(t, x).endswith("BindingRemapper")), None)
    if tj is None:
        return ["temps de jeu (cellule de FM) introuvable : laissé sous la date"]
    move(t, tj, par, 0)
    t.styles.style(t, tj, {"margin-bottom": 2, "flex-shrink": 0})
    return []


def reputation(t, k, parent):
    """v3 (Kinito) : la réputation avec le prix (v4 : au-dessus) : le cadre de FM (PlayerReputationTextFrame de
    PlayerAttributesLargeBlock, titre traduit par FM) sur une ligne"""
    c = t.clone(k.reputation, parent, src=k.fa)
    t.styles.copy_from(k.fa.styles, t, c)
    t.sd(c)["name"] = ""
    t.elem(c)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, c, {"flex-shrink": 0, "margin-bottom": 6, "align-self": "stretch", "overflow": "hidden"})
    kids = t.children(c)
    for i, x in enumerate(kids):
        cl = [y for y in t.elem(x).get("m_Classes") or [] if not y.startswith("margin-bottom")]
        t.elem(x)["m_Classes"] = cl + (["margin-right-global-gap-small"] if i == 0 else []) + \
            ["content-no-wrap", "content-ellipsis"]
        t.styles.style(t, x, {"flex-shrink": 0 if i == 0 else 1, "min-width": 0})
    return c


def _remplacer_chemin(x, avant, apres):
    """chemin de donnée avant -> apres dans une donnée sérialisée ; nombre de remplacements"""
    n = 0
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "m_path" and v == avant:
                x[k] = apres
                n += 1
            else:
                n += _remplacer_chemin(v, avant, apres)
    elif isinstance(x, list):
        for v in x:
            n += _remplacer_chemin(v, avant, apres)
    return n


def rapport(t, k, parent):
    """le bloc de FM (PlayerReportHeaderScoutSection d'origine) recopié ; la note par son libellé court (FM :
    gradinginfo.ShortGradeString ; la phrase longue ne tient pas) ; son aiguillage « disposition de l'entraîneur »
    (report.UseCoachReportLayout : tes joueurs -> les étoiles ; les autres -> la note du rapport) garde les étoiles
    pour tes joueurs ; v3 (Kinito) : pour les autres, la note PUIS, s'il y a un rapport (report.HasScoutedInfo), les
    étoiles (celles du rapport du recruteur : ScoutedCurrent / PotentialAbility)"""
    s = k.txt.s
    racine = s.children(s.tt["m_VisualTree"]["rid"])
    if not racine:
        return [f"{SOURCE_ARGS[0]} : forme inattendue (introuvable)"]
    rm = remapper(t, k.rm_model, parent, {"team": ("localteam", EQUIPE)}, ["column-direction-normal"])
    c = k.txt.clone(t, racine[0], rm)
    sw = next((r for r in t.walk(c) if typ(t, r).endswith("BindableSwitchElement")
               and "UseCoachReportLayout" in json.dumps(t.sd(r).get("Binding") or {})), None)
    kids = t.children(sw) if sw is not None else []
    if len(kids) != 2:
        return [f"{SOURCE_ARGS[0]} : aiguillage du rapport introuvable"]
    eclaireur, etoiles = kids
    msgs = []
    if sum(_remplacer_chemin(t.refs[r], NOTE_LONGUE, NOTE_COURTE) for r in t.closure(eclaireur)) != 1:
        msgs.append(f"libellé de la note du rapport ({NOTE_LONGUE}) pas trouvé une seule fois : à vérifier")
    col = boite(t, sw, {}, ["column-direction-normal", "align-items-start"])
    move(t, col, sw, 0)
    move(t, eclaireur, col)
    v = visible_direct(t, k, col, "report.HasScoutedInfo")
    t.elem(v)["m_Classes"] = ["column-direction-normal", "align-items-start"]
    t.styles.style(t, v, {"margin-top": 8})
    e2 = t.clone(etoiles, v)
    t.sd(e2)["name"] = ""
    return msgs


def construire_large(t, parent, parts, rayon_px, k):
    """notre carte (fond, bord, coins, hauteur fixe) ; parts de la largeur et rayon du polygone : TAILLES_TEXTE"""
    src, p = k.src, k.p
    b = k.s_vis.sd(k.vis)["Binding"]
    msgs = []
    v, h = PADDING_V, MARGE_COTES_INT
    carte = boite(t, parent, {
        "flex-direction": "row", "align-items": "stretch", "height": HAUT, "min-height": HAUT, "max-height": HAUT,
        "flex-shrink": 0, "flex-grow": 1, "overflow": "hidden", "background-color": FOND,
        **{f"border-{c}-width": 1 for c in ("top", "bottom", "left", "right")},
        **{f"border-{c}-color": BORD for c in ("top", "bottom", "left", "right")},
        **{f"border-{c}-radius": RAYON for c in ("top-left", "top-right", "bottom-left", "bottom-right")},
        "padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
        "margin-top": MARGE_HAUT, "margin-bottom": MARGE_HAUT, "margin-left": MARGE_COTES,
        "margin-right": MARGE_COTES}, ["align-self-stretch"])
    e = ECART
    cv, ch = CELLULE

    def sep(dans=None):
        dans = carte if dans is None else dans
        boite(t, dans, {"width": e, "min-width": e, "flex-shrink": 0})
        trait_vertical(t, dans)
        boite(t, dans, {"width": e, "min-width": e, "flex-shrink": 0})

    def part(dans, poids, classes, css=None):
        return boite(t, dans, {"flex-grow": poids, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                               "overflow": "hidden", **(css or {})}, classes)

    def colonne(poids):
        return part(carte, poids, ["column-direction-normal", "align-self-stretch"])

    def moitie(c, haut_):
        css = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden",
               "padding-top": cv, "padding-bottom": cv, "padding-right": ch, "justify-content": "center"}
        if haut_:
            css.update({"border-bottom-width": 1, "border-bottom-color": TRAIT})
        return boite(t, c, css, ["column-direction-normal", "align-items-start"])

    def bloc_clubs():
        """clubs (club parent / en prêt à) : le contenu du bloc club de FM, nom court du club (primarytext team.Name
        -> club.ShortName dans ses remappers ; idée de la tuile d'Alex v9, vue par Kinito)"""
        c0 = colonne(parts["club"])
        bc = boite(t, c0, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "overflow": "hidden",
                           "justify-content": "center", "padding-top": cv, "padding-bottom": cv,
                           "padding-right": ch}, ["column-direction-normal", "align-items-start"])
        cs = k.clubs.s
        cr = cs.children(cs.tt["m_VisualTree"]["rid"])
        cr = cr and cs.children(cr[0])
        if cr:
            c = k.clubs.clone(t, cr[0], bc)
            for r in t.walk(c):
                for prop in t.elem(r).get("m_Properties") or []:
                    if prop.get("name") == "mappings" and isinstance(prop.get("value"), str):
                        prop["value"] = prop["value"].replace("primarytext:team.Name:", "primarytext:club.ShortName:")
        else:
            src.clone(t, p["club"], bc)

    # 1. le joueur : photo + identité
    ph = k.entete.clone(t, k.photo, carte)
    t.sd(ph)["name"] = ""
    t.elem(ph)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    t.styles.style(t, ph, {"flex-shrink": 0, "align-self": "center", "margin-right": e})
    ident = part(carte, parts["ident"], ["column-direction-normal", "justify-content-center"])
    for nom in ("nom", "poste"):
        c = src.clone(t, p[nom], ident)
        t.styles.style(t, c, {"flex-shrink": 0, "margin-bottom": 4})
    c = t.clone(k.haut, ident, src=k.fa)
    t.styles.copy_from(k.fa.styles, t, c)
    copy_usings(t, k.fa, k.haut)
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
    # 2. nation (drapeau + 3 lettres, puis à côté la 2e ; sélections) / âge, date et lieu de naissance
    c3 = colonne(parts["nation"])
    hn = moitie(c3, True)
    rang = boite(t, hn, {"flex-shrink": 0, "align-self": "stretch", "overflow": "hidden", "margin-bottom": 2},
                 ["row-direction-normal", "align-items-center"])
    ligne_nation(t, k, rang, "person.nation", "nation.ThreeLetterName")
    nation_secondaire(t, k, rang)
    cap = src.clone(t, p["caps"], hn)
    t.elem(cap)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    cellules = [x for x in t.children(cap) if (t.elem(x).get("m_TemplateAlias") or "") == "text-cell-button-medium"]
    if len(cellules) == 2:   # une seule ligne : sélections A, ou jeunes avant AGE_JEUNE ans (le détail : infobulle)
        for x, li in ((cellules[0], ni.make_binding(b, OP_SUP, ["person.Age"], AGE_JEUNE - 1)),
                      (cellules[1], ni.make_binding(b, OP_INF, ["person.Age"], AGE_JEUNE))):
            s2 = ni.new_visible(t, k.s_vis, k.vis, cap, t.children(cap).index(x), "", li)
            move(t, x, s2)
            t.elem(x)["m_Classes"] = []
    hb = moitie(c3, False)
    src.clone(t, p["age"], hb)
    ti = titre(t, k, hb, *TITRE_LIEU)
    t.styles.style(t, ti, {"margin-top": 4, "margin-bottom": 1, "flex-shrink": 0})
    # le bloc de FM (Personnel) : calé à droite, centré, à la ligne, police tifo-p ; ici sur une ligne, calé à gauche,
    # dans la police du contrat (« Dakar, Sénégal » : la virgule est dans le texte de la ville, padding de FM gardé)
    lieu = k.lieu.clone(t, k.bloc_lieu, hb)
    t.sd(lieu)["name"] = ""
    t.elem(lieu)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, lieu, {"flex-shrink": 0, "align-self": "stretch", "overflow": "hidden"})
    for r in t.walk(lieu):
        if typ(t, r).endswith("SIText"):
            garde = [x for x in t.elem(r).get("m_Classes") or [] if x.startswith("padding-right")]
            t.elem(r)["m_Classes"] = CL_TEXTE_LIEU + garde
            t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0})
        elif r != lieu and typ(t, r).endswith("SIVisible"):
            t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0})
    sep()
    # 3. clubs
    bloc_clubs()
    sep()
    # 4. réputation et prix / temps de jeu, salaire, date de fin
    c4 = colonne(parts["prix"])
    hp_ = moitie(c4, True)
    reputation(t, k, hp_)
    src.clone(t, p["valeur"], hp_)
    msgs += contrat_3_lignes(t, k, src.clone(t, p["contrat"], moitie(c4, False)))
    sep()
    # 5. Dispo. transfert / Dispo. prêt (les deux cadres de la tuile de FM) ; textes sans retour à la ligne
    c5 = colonne(parts["statut"])
    st = k.statut
    for i, nom_titre in enumerate(STATUT_CADRES):
        hh = moitie(c5, i == 0)
        titre_fm = first(st.s, lambda r: st.s.name(r) == nom_titre)
        if titre_fm is None:
            msgs.append(f"{STATUT} : {nom_titre} introuvable")
            continue
        rm = remapper(t, k.rm_model, hh, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
        c = st.clone(t, st.s.parent[titre_fm], rm)
        t.sd(c)["name"] = ""
        for r in t.walk(c):
            if typ(t, r).endswith("SIText"):
                t.elem(r)["m_Classes"] = list(dict.fromkeys(list(t.elem(r).get("m_Classes") or [])
                                                            + ["content-no-wrap", "content-ellipsis"]))
                t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})
    # 6. polygone : cale fixe sans liaison (rien de lié ne tient pendant le chargement d'une fiche), polygone dans un
    # SIVisible lié aux données du joueur (person.Age > 0 : caché tant qu'elles ne sont pas lues) ; cale = toute la
    # hauteur du contenu de la carte, 290 de large ; rayon demandé = celui où les étiquettes tiennent (TAILLES_TEXTE)
    w, hh = POLYGONE_L, HAUT - 2 * PADDING_V - 2
    zone = boite(t, carte, {}, ["row-direction-normal"])
    large = w + 2 * e + 1 + 2 * POLYGONE_MARGE_K
    t.styles.style(t, zone, {"width": large, "min-width": large, "max-width": large, "flex-grow": 0,
                             "flex-shrink": 0, "align-self": "stretch", "overflow": "hidden"})
    sep(zone)
    pb = boite(t, zone, {"width": w, "min-width": w, "max-width": w, "height": hh, "min-height": hh,
                         "max-height": hh, "flex-grow": 0, "flex-shrink": 0, "overflow": "hidden",
                         "align-self": "center", "margin-left": POLYGONE_MARGE_K},
               ["column-direction-normal", "align-items-center", "justify-content-center"])
    attente = ni.new_visible(t, k.s_vis, k.vis, pb, None, "", ni.make_binding(b, OP_SUP, ["person.Age"], 0))
    t.styles.style(t, attente, {"width": w, "height": hh, "flex-grow": 0, "flex-shrink": 0})
    rm = remapper(t, k.rm_model, attente, {"player": ("person", JOUEUR)})
    t.styles.style(t, rm, {"width": w, "height": hh, "flex-grow": 0, "flex-shrink": 0})
    poly = t.clone(k.chart, rm, src=k.fa)
    t.styles.copy_from(k.fa.styles, t, poly)
    copy_usings(t, k.fa, k.chart)
    sd = t.sd(poly)
    # FM : rayon de base = pourcentage × le plus petit côté de la cale
    sd["SpiderChartRadiusPercentage"] = round(100.0 * rayon_px / min(w, hh), 2)
    sd["NumberOfInnerRings"] = ANNEAUX
    sd["LabelsTemplate"]["m_AssetGUID"] = GUID_ETIQUETTES
    t.elem(poly)["m_Classes"] = [x for x in t.elem(poly)["m_Classes"]
                                 if x not in ("justify-content-end", "flex-grow-class", "align-self-stretch")]
    t.styles.style(t, poly, {"width": w, "min-width": w, "max-width": w, "height": hh, "min-height": hh,
                             "max-height": hh, "flex-grow": 0, "flex-shrink": 0})
    # 7. rapport de supervision (note ; Niveau actuel / Potentiel : bloc de FM)
    sep()
    nv = part(carte, parts["niveau"], ["column-direction-normal", "justify-content-center", "align-items-start"])
    msgs += rapport(t, k, nv)
    return msgs


# ---------- v6 (07/11/2026) : la bande et la carte de la MAQUETTE 47 ----------
# Kinito : « fais comme sur la maquette, d'un seul tenant », « tout d'un coup ». Mesuré sur ses captures (texte Normal et
# Plus grand) : la bande va de y 104 à 312 et le bloc finit à y 879 à l'écran, quelle que soit la taille du texte ; la
# carte de la bande fait HAUT = 188 de FM pour 209 px d'écran : 1,111 px d'écran par px de FM. La carte du joueur est
# posée dans la bande (position absolue) et DESCEND jusqu'au bas du bloc : 698 de FM (y 104 -> 879) ; le bloc (dessiné
# après la bande) lui laisse sa place vide. Si quelque chose au-dessus de la bande coupe ce qui dépasse, on ne verra
# que son haut (à regarder en jeu). — v7 : VU EN JEU (capture 28) : le jeu coupe l'en-tête à son bord bas ; la carte
# est maintenant en deux morceaux (carte_haut47 ici, carte_bas47 dans le bloc), CARTE_H n'est plus utilisé. — v9
# (capture 30) : la carte entière dans le bloc, la bande sur toute la largeur (carte_haut47 retiré).
CARTE_L = 270
# les trois cases de la bande (maquette 47 : 750 / 492 / 300 de large) ; v9 : la bande gagne la place de la photo
# (282) : 213 aux chiffres (« Espoir aux portes de … » était coupé, capture 31), 100 au bout (les menus d'entraînement)
# v11 (Kinito, 08/11, captures 34-40 : « contrat - valeur - dispo - nouveaux boutons - polygone attributs - polygone
# stats ou entraînement ») : poids = largeurs voulues en px de FM (flex-basis 0 : la place se partage au prorata du
# poids, marges intérieures en plus). Mesuré sur la capture 37 (1,1407 px d'écran par px de FM) : la bande fait 1626 de
# large, il reste 1546 aux trois cases (marges, bords, deux traits de 25). Chiffres : 775 de contenu (+ 85 de marges
# et de traits courts) : contrat 175 (« Indésirable dans l'équipe » 167), valeur 180 (« 3,9M € - 8,2M € » en grand
# 174), dispos 130 (« Indisponible » 126), boutons 290 (« Discuter d'un nouveau contrat avec l'agent » ~250 + icône
# et marges du bouton de FM) ; polygone 335 (rayon 49 + étiquettes ~112 de chaque côté) ; bout 352 (les deux menus
# d'entraînement de MENU_L, 328)
POIDS_47 = dict(chiffres=860, avis=335, bout=352)
# v12 (Kinito, 08/11, captures 41-45 : « les 4 premières colonnes de la même largeur, la colonne des boutons bien
# réduite ») : quatre colonnes de 214 de large chacune, marges comprises. La zone fait 856 (860 moins les 3 traits) ;
# une colonne a une base nulle, plus ses marges (10 à droite ; 14 à gauche, sauf la 1re) : 10 + 24 × 3 = 82 ; il
# reste 774 à partager : 204 à la 1re (sans marge à gauche), 190 aux autres → 214 chacune
POIDS_CHIFFRES = dict(contrat=204, valeur=190, dispo=190, boutons=190)
CHEMIN_SALAIRE = "person.FullContract.Wage.DisplayValue"            # (bannière de FM, cellule du contrat)
CHEMIN_STATUT = "person.FullContract.AgreedPlayingTime.DisplayValue"  # « Joueur important »
CHEMIN_DESCRIPTION = "Person.MediaDescription"                       # « Défenseur central prometteur »
GRADE_COACH = "person.ClubCoachReport.ScoutedGradeInfo"               # la note du rapport du préparateur
# Pour / Contre SANS les pastilles d'Alex (icône de FM et phrase, _lignes_pc) : PC_MAX lignes au plus chacun (bloc
# v16 : 8 ; v19 : 16, Barry en a 12 ; avec ses pastilles, plus de limite : _phrases_liste) ; variables kinitopc<p|c><n>
PC_MAX, V_PC = 16, "kinitopc"
ECART_PC = 10    # bloc v17 : entre la moitié Pour et la moitié Contre
LISTES_PC = (("p", "report.ScoutedProConsList.ProsList", "report.ScoutedProConsList.ProsCount"),
             ("c", "report.ScoutedProConsList.ConsList", "report.ScoutedProConsList.ConsCount"))
TEXTE_LIBRE = ("Joueur libre de tout contrat : pas de données de prestation.", "Free agent: no performance data.")
TITRE_PREPARATEUR = ("Rapport du préparateur", "Coach Report")   # texte de FM 27 (0x100ad0e8)
# v10 : le polygone de stats prend toute la hauteur de sa case : la bande (HAUT_BANDE 182) moins ses marges intérieures
# (2 × 6) et ses bords (2 × 1) = 168, moins 2 de marge. Rayon, par taille du texte (une bande par taille) : les
# étiquettes 10 px de deux lignes en haut et en bas (18 de haut au texte Normal, mesurées sur la capture 33, × la taille
# du texte), à 8 du polygone (LabelDistanceFromChart du polygone de stats de FM), 6 de marge : 83 - 8 - 18 × taille
# - 6. Sur les côtés (case de ~345 de large), il reste ~110 par étiquette. Les coins du haut (compétition à gauche sur
# TITRE_STATS_L, pouce à droite) restent libres : les étiquettes en biais du haut sont à ~35 du haut, sous les deux
# lignes de la compétition (~30)
STATS_H = 166
RAYONS_STATS = {"petit": 53.0, "normal": 51.0, "grand": 49.0, "plus-grand": 47.0}
TITRE_STATS_L = 110
# v10, option « polygone » (v11 : toujours) : le polygone des attributs dans la case du milieu (v11 : ~335 de large ;
# il en faut ~224 : rayon 49 + 10 + « Vision du jeu 12 » 53 de chaque côté), STATS_H de haut ; ses
# étiquettes à 10 du polygone : 83 - 10 - 18 × taille - 6
RAYONS_BANDE = {"petit": 51.0, "normal": 49.0, "grand": 47.0, "plus-grand": 45.0}
# v7 (capture 28, mesuré) : le jeu COUPE l'en-tête à son bord bas (188 de FM, y 313 à l'écran : fond, bande et carte
# coupés à la même ligne ; aucune règle de l'en-tête ni des feuilles de FM ne coupe, c'est le conteneur créé par le
# code du jeu). La bande (marge 6 + 188 + marge 6) perdait sa bordure du bas : elle fait maintenant HAUT_BANDE. La
# carte du joueur ne peut pas traverser : deux morceaux raccordés, le haut (la photo) ici, coupé par ce bord ; le bas
# (nom -> club) dans la tuile du bloc (carte_bas47), qui remonte de JOINTURE au-dessus du bloc (y 313 -> 336 = 20,1).
# v8 (v7 vue en jeu, capture 29, mesuré) : le jeu coupe AUSSI la zone du bloc, à y 322 (le nom est à la place que lui
# donne un haut de carte à y 313 : le bas remontait bien, il est coupé). Entre y 312 (bas de l'en-tête) et y 322, 10 px
# n'appartiennent ni à l'en-tête ni au bloc : rien ne peut y être dessiné. Deux cartes fermées, l'une sur l'autre : le
# haut finit au bord de l'en-tête (bords et coins du bas), le bas commence à la ligne de coupe du bloc (bords et coins
# du haut), 10 px plus bas.
HAUT_BANDE = HAUT - MARGE_HAUT       # 182 : la bande, sous sa marge du haut, finit au bord de l'en-tête
JOINTURE = 12                        # de FM entre la ligne où le jeu coupe la zone du bloc et le haut du bloc
#                                      (capture 29 : y 322 -> 336 = 14 px = 12,3 de FM ; 12 : le bord reste visible)
DECALE_ETOILES = 6                   # les étoiles de FM sont centrées dans une case à marge intérieure de 4 : la 1re
#                                      était 7 px (6 de FM) à droite de son titre (capture 29, Niveau actuel et Potentiel)
CL_LAB = ["body-sm", "global-text-secondary", "content-no-wrap", "content-ellipsis"]       # titres (comme FM)
CL_VAL = ["heading-xl", "global-text-primary", "content-no-wrap", "content-ellipsis"]      # réponses en grand (22)
CL_STAT = ["heading-xsmall-14px", "global-text-primary", "content-no-wrap", "content-ellipsis"]   # statut (gras 14)
TRAIT_CHIFFRE = (1.0, 1.0, 1.0, 0.45)   # le petit trait clair au-dessus de chaque chiffre (maquette 47)
TEXTE_SANS_RAPPORT = (("Pas encore de rapport de supervision", "No scouting report yet"),
                      ("Observe-le : ses points forts et ses points faibles s'afficheront ici.",
                       "Scout him: his strengths and weaknesses will show here."))
TITRE_PRESTATION = ("Données de la prestation", "Performance Data")
for _k, _v in {"height-kw": (131087, 1), "bottom": (131080, 3)}.items():   # height: auto (mot-clé 2) ; bottom
    PROPRIETES.setdefault(_k, _v)


def _chemins_args(binding, remplace):
    """une liaison à fonction recopiée, ses chemins de donnée remplacés (ancien -> nouveau) ; (liaison, nombre)"""
    b = copy.deepcopy(binding)
    args = ni.decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    n = 0
    for a in args:
        if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]"):
            v = bytes(a[1])
            if len(v) >= 2 and v[0] == 1 and v[2:2 + v[1]].decode(errors="replace") in remplace:
                a[1] = _chemin_arg(remplace[v[2:2 + v[1]].decode()])
                n += 1
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = ni.encode_args(args)
    return b, n


def texte_direct(t, k, parent, chemin, classes, css=None):
    """un texte de FM (celui du nom de la nation) lié directement à chemin"""
    tx = k.nt.clone(t, k.texte_nation, parent)
    no_styles(t, tx)
    sd = t.sd(tx)
    sd["name"] = ""
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["TextBinding_UxmlAttributeFlags"] = 1
    sd["DebugDisplay"] = ""
    t.elem(tx)["m_Classes"] = list(classes)
    t.styles.style(t, tx, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}, **(css or {})})
    return tx


def visible_bool(t, k, parent, chemin, inverse=False):
    """SIVisible de FM « visible si <chemin> est vrai » (ou faux) ; seulement sur un booléen de FM (jamais sur une
    variable remplie par une fonction : plantage du bloc v3)"""
    v = visible_direct(t, k, parent, chemin)
    t.sd(v)["InvertDirectBinding"], t.sd(v)["InvertDirectBinding_UxmlAttributeFlags"] = (1 if inverse else 0), 1
    return v


def bulle(t, k, parent, liaison=None, chemin=None):
    """l'infobulle de FM (StandardTextTooltip, qui couvre son parent) : son texte = la liaison donnée (recopiée), ou
    le chemin donné (liaison directe) ; (infobulle, nombre de textes changés)"""
    b = k.bulle_src.clone(t, k.bulle, parent)
    n = 0
    for ov in t.elem(b).get("m_SerializedDataOverride") or []:
        d = (t.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}
        if isinstance(d.get("TextBinding"), dict):
            if liaison is not None:
                d["TextBinding"] = copy.deepcopy(liaison)
            else:
                d["TextBinding"] = copy.deepcopy(d["TextBinding"])
                d["TextBinding"]["m_kind"] = 1
                d["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
            d["TextBinding_UxmlAttributeFlags"] = 1
            d["DebugDisplay"] = ""
            n += 1
    return b, n


def _colonne47(t, parent, poids, centre=False):
    return boite(t, parent, {"flex-grow": poids, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden",
                             "justify-content": "center"},
                 ["column-direction-normal", "align-items-center" if centre else "align-items-start",
                  "align-self-stretch"])


def _sep47(t, parent):
    boite(t, parent, {"width": ECART, "min-width": ECART, "flex-shrink": 0})
    trait_vertical(t, parent)
    boite(t, parent, {"width": ECART, "min-width": ECART, "flex-shrink": 0})


def _bloc_clubs47(t, k, parent):
    """le contenu du bloc club de FM (club parent / en prêt à), nom court du club (comme la v5)"""
    cs = k.clubs.s
    cr = cs.children(cs.tt["m_VisualTree"]["rid"])
    cr = cr and cs.children(cr[0])
    if not cr:
        k.src.clone(t, k.p["club"], parent)
        return [f"{CLUB} : forme inattendue, le bloc club de FM tel quel"]
    c = k.clubs.clone(t, cr[0], parent)
    for r in t.walk(c):
        for prop in t.elem(r).get("m_Properties") or []:
            if prop.get("name") == "mappings" and isinstance(prop.get("value"), str):
                prop["value"] = prop["value"].replace("primarytext:team.Name:", "primarytext:club.ShortName:")
    # v10 (bloc v15, capture 32 : carte VIDE pour un joueur prêté) : le bloc de FM est une ligne à la largeur de son
    # contenu (align-items-center), centrée dans la carte ; ses deux clubs côte à côte (v14) ont chacun une base nulle
    # (flex-basis 0, pour être égaux) : sans largeur donnée, la ligne du prêt mesurait 0 + l'icône, les clubs 0 de
    # large, leurs textes une lettre par ligne, et la carte (centrée verticalement) poussait tout son contenu hors de
    # la vue. La ligne prend la largeur de la carte, l'aiguillage aussi ; un joueur non prêté reste centré
    t.styles.style(t, c, {"align-self": "stretch", "min-width": 0})
    sw = next((r for r in t.walk(c) if t.name(r) == "IsAtTeam" and typ(t, r).endswith("BindableSwitchElement")),
              None)
    if sw is None:
        return [f"{CLUB} : aiguillage club / prêt (IsAtTeam) introuvable"]
    t.styles.style(t, sw, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "align-items": "center"})
    return _pret_cote_a_cote(t, c)


def _pret_cote_a_cote(t, c):
    """v9 (capture 31, « on avait dit l'un à côté de l'autre ») : un joueur prêté, le club parent et le club où il est
    prêté CÔTE À CÔTE, chacun en colonne (son titre, son écusson, son nom), l'icône « prêts » de FM entre les deux.
    Dans le bloc de FM (LoanTrialClub) : [écusson | titre + nom] (club parent) puis [écusson | titre + nom] (prêt à),
    l'un sous l'autre ; leurs liaisons et leurs remappers ne changent pas, seuls les éléments bougent dans leur cadre"""
    pret = next((r for r in t.walk(c) if t.name(r) == "LoanTrialClub"), None)
    parts = t.children(pret) if pret is not None else []
    if len(parts) != 2:
        return [f"{CLUB} : bloc du prêt (LoanTrialClub) introuvable"]
    t.elem(pret)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    t.styles.style(t, pret, {"align-self": "stretch"})
    msgs = []
    for part in parts:
        ecusson = next((x for x in t.walk(part) if (t.elem(x).get("m_TemplateAlias") or "") == "TeamIcon48px"), None)
        titre_c = next((x for x in t.walk(part) if typ(t, x).endswith("SIText")
                        and "global-text-secondary" in (t.elem(x).get("m_Classes") or [])), None)
        if ecusson is None or titre_c is None:
            msgs.append(f"{CLUB} : écusson ou titre d'un club du prêt introuvable")
            continue
        haut = ecusson if t.parent[ecusson] == part else t.parent[ecusson]   # l'écusson, ou son remapper
        move(t, titre_c, part, t.children(part).index(haut))
        t.elem(titre_c)["m_Classes"] = ["global-text-secondary", "body-sm", "content-no-wrap", "content-ellipsis"]
        t.styles.style(t, titre_c, {"margin-bottom": 2, "max-width": {"unit": 2, "value": 100.0}})
        t.elem(part)["m_Classes"] = ["column-direction-normal", "align-items-center"]
        t.styles.style(t, part, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                 "overflow": "hidden"})
        # ce qui était à droite de l'écusson (le nom, et la colonne vide du titre parti) : centré dessous
        for x in t.children(part):
            if x not in (titre_c, haut) and x in t.refs and not typ(t, x).endswith("Component"):
                t.elem(x)["m_Classes"] = [y for y in t.elem(x).get("m_Classes") or []
                                          if not y.startswith(("margin-left", "margin-bottom"))]
                t.styles.style(t, x, {"align-items": "center", "max-width": {"unit": 2, "value": 100.0},
                                      "min-width": 0})
                for y in t.walk(x):
                    if y != x and y in t.refs and not typ(t, y).endswith("Component"):
                        t.elem(y)["m_Classes"] = [z for z in t.elem(y).get("m_Classes") or []
                                                  if z != "margin-bottom-global-gap-regular"]
                        if "row-direction-normal" in t.elem(y)["m_Classes"]:   # la ligne du nom (club parent)
                            t.styles.style(t, y, {"justify-content": "center"})
    ico = boite(t, pret, {"width": ICONE_PRET_T, "height": ICONE_PRET_T, "min-width": ICONE_PRET_T,
                          "flex-shrink": 0, "margin-left": 6, "margin-right": 6}, [ICONE_PRET])
    move(t, ico, pret, 1)
    return msgs


def _cadre_carte(t, parent, css, coins, bords, nom):
    """le fond, les bords et les coins de la carte du joueur (seulement les bords et coins donnés)"""
    return boite(t, parent, {
        "position": "absolute", "width": CARTE_L, "min-width": CARTE_L, "max-width": CARTE_L,
        "background-color": FOND, **{f"border-{c}-width": 1 for c in bords},
        **{f"border-{c}-color": BORD for c in bords}, **{f"border-{c}-radius": RAYON for c in coins},
        "padding-left": MARGE_COTES_INT, "padding-right": MARGE_COTES_INT, "overflow": "hidden", **css},
        ["column-direction-normal", "align-items-center"], nom)


def _centre_entre(t, ligne, milieu, droite=()):
    """v9 : milieu CENTRÉ sur la largeur de la ligne, ce qui va à sa droite (numéro, statut) sans le décaler : deux
    cales de même poids de part et d'autre (flex 1, base 0), la cale de droite porte les éléments de droite"""
    gauche = boite(t, ligne, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0}, [])
    move(t, gauche, ligne, 0)
    move(t, milieu, ligne, 1)
    d = boite(t, ligne, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden"},
              ["row-direction-normal", "align-items-center"])
    for x in droite:
        move(t, x, d)
    return d


def carte_bas47(t, k, parent, taille):
    """la carte du joueur, dans la tuile du bloc, à gauche (la place laissée par le bloc). v9 (bloc v14, capture 30 :
    « l'espace entre la photo et le bloc d'en dessous doit disparaître ») : la carte ENTIÈRE, photo comprise, de la
    ligne où le jeu coupe la zone du bloc (JOINTURE au-dessus du bloc) jusqu'en bas ; la bande prend toute la largeur
    au-dessus. Photo ; nom (numéro à côté) ; description des médias ; niveau et potentiel ; Actions (statut à côté) ;
    nation et sélections ; âge et lieu de naissance ; club(s). k = les sources de la BANDE ; le bloc reçoit person et
    team, pas localteam : un remapper localteam -> person.Team (bloc v21 ; avant : -> team), puis le BindingSetter de la bannière (hasContract,
    teamtodisplay). taille = la taille du texte (TAILLES_BLOC), pour la hauteur de la photo"""
    carte = _cadre_carte(t, parent, {"left": 0, "top": -JOINTURE, "bottom": 0, "padding-top": 12,
                                     "padding-bottom": 12},
                         ("top-left", "top-right", "bottom-left", "bottom-right"), ("top", "bottom", "left", "right"),
                         f"{PREFIXE}CarteBas")
    # bloc v21 (Kinito, capture 55 : Santiago Simón, de Toluca, montré « Rodez AF, Ligue 1 », son club à lui) : le club
    # de la carte est celui que choisit le BindingSetter de la bannière de FM (teamtodisplay = BindAndSetAorBTo-
    # DestinationOnCondition : localteam.IsNation ? person.Team : localteam ; lu dans ses octets, Invert 0). Ici
    # localteam était l'équipe que reçoit le bloc : TON équipe quand la fiche est ouverte depuis chez toi (liste de
    # suivi, recherche…). localteam = person.Team, le club où il joue : le club de la carte, et ses pastilles d'état
    # (PlayerStatusFlagsForTeamVisible, qui lisent aussi localteam) pour ce club ; le numéro l'était déjà (v9)
    rm = remapper(t, k.rm_model, carte, {"localteam": ("person.Team", EQUIPE)},
                  ["column-direction-normal", "align-self-stretch"])
    t.styles.style(t, rm, {"flex-grow": 1, "min-height": 0})
    st = seul(t, k.src.s, k.p["setter"], rm)
    t.elem(st)["m_Classes"] = ["column-direction-normal", "align-items-center", "align-self-stretch"]
    # v9 : resserré (capture 30, « ça fait horrible ») : tout au milieu, ÉCART_CARTE entre les morceaux, au lieu
    # d'étaler le contenu sur toute la hauteur
    t.styles.style(t, st, {"flex-grow": 1, "min-height": 0, "justify-content": "center"})
    return _contenu_carte(t, k, st, taille)


ECART_CARTE = 8                    # v9 : entre deux morceaux de la carte
PHOTO_H = dict(petit=138, normal=130, grand=120, **{"plus-grand": 110})   # v9 : hauteur de la photo (FM : 138)
PHOTO_L, PHOTO_H_FM = 108, 138     # la photo de FM (thumbnails-alt-person-picture-player-report) : 108 x 138
COULEUR_DESCRIPTION = (0.945, 0.835, 0.561, 1.0)   # la description des médias, en or (maquette 47 : #f1d58f)
ICONE_PRET = "game-concepts-loans_small"         # v9 : l'icône « prêts » de FM (globe et flèches), choix de Kinito
ICONE_PRET_T = 24
for _k, _v in {"color": (65536, 4), "flex-wrap": (131086, 7)}.items():   # (flex-wrap : numéro d'Alex, pastilles)
    PROPRIETES.setdefault(_k, _v)


def _contenu_carte(t, k, parent, taille):
    """photo ; nom, description des médias ; niveau et potentiel ; Actions et statut ; nation et sélections ; âge et
    lieu de naissance ; club(s)"""
    src, p = k.src, k.p
    b = k.s_vis.sd(k.vis)["Binding"]
    n = [0]

    def groupe(css=None):
        g = boite(t, parent, {"flex-shrink": 0, "align-self": "stretch", "overflow": "hidden",
                              "margin-top": ECART_CARTE if n[0] else 0, **(css or {})},
                  ["column-direction-normal", "align-items-center"])
        n[0] += 1
        return g
    msgs = []
    # la photo (celle de l'en-tête de FM), à sa hauteur pour la taille du texte ; si la carte manque de place, c'est
    # elle qui cède (coupée en bas, jamais le club)
    h = PHOTO_H[taille]
    g = groupe({"flex-shrink": 1, "min-height": 70, "justify-content": "flex-start"})
    ph = k.entete.clone(t, k.photo, g)
    t.sd(ph)["name"] = ""
    t.elem(ph)["m_Classes"] = ["row-direction-normal", "align-items-start", "justify-content-center"]
    t.styles.style(t, ph, {"flex-shrink": 0, "padding-left": 0, "padding-right": 0, "align-self": "center"})
    images = [r for r in t.walk(ph) if (t.elem(r).get("m_TemplateAlias") or "") == "PersonPicture"]
    if len(images) != 1:
        msgs.append(f"photo du joueur : {len(images)} images au lieu d'une (introuvable)")
    for r in images:
        t.styles.style(t, r, {"width": round(PHOTO_L * h / PHOTO_H_FM), "height": h, "flex-shrink": 0})
    # le nom, CENTRÉ sur la largeur de la carte, le numéro à sa droite (v9, capture 30 : il était calé à gauche) ; le
    # numéro de FM prend les couleurs et le texte de l'équipe reçue (« team » de la tuile, pas celle où il joue : il
    # restait vide pour un joueur prêté, capture 31) -> son équipe actuelle, person.Team
    g = groupe()
    c = src.clone(t, p["nom"], g)
    t.styles.style(t, c, {"flex-shrink": 0, "align-self": "stretch", "margin-bottom": 2})
    nom = next((x for x in t.children(c) if typ(t, x).endswith("SIText")), None)
    if nom is None:
        msgs.append("nom du joueur (SIText) introuvable")
    else:
        t.elem(nom)["m_Classes"] = [x for x in t.elem(nom).get("m_Classes") or []
                                    if x != "margin-right-global-gap-regular"]
        t.styles.style(t, nom, {"flex-shrink": 1, "min-width": 0})
        d = _centre_entre(t, c, nom, [x for x in t.children(c) if x != nom])
        t.styles.style(t, d, {"padding-left": 8})
    numero = 0
    for r in t.walk(c):
        if typ(t, r).endswith("BindingRemapper"):
            for m in t.sd(r).get("Mappings") or []:
                if m.get("from") == "team" and (m.get("to") or {}).get("m_path") == "localteam":
                    m["to"]["m_path"] = "person.Team"
                    numero += 1
    if numero != 1:
        msgs.append(f"numéro du joueur : {numero} liens d'équipe au lieu d'un (introuvable)")
    # la description des médias mise en évidence (maquette 47 : en or, en gras, plus grande), à la ligne si longue
    texte_direct(t, k, g, CHEMIN_DESCRIPTION, ["heading-md", "content-center-align", "content-wrap"],
                 {"color": COULEUR_DESCRIPTION, "align-self": "stretch"})
    # v9 : niveau actuel et potentiel SOUS le nom et la description (capture 30, ils étaient dans la bande)
    msgs += _etoiles_carte(t, k, groupe())
    g = groupe()   # Actions CENTRÉ sur la largeur de la carte, le statut à sa droite (v9, capture 30)
    ligne = boite(t, g, {"flex-shrink": 0, "align-self": "stretch"}, ["row-direction-normal", "align-items-center"])
    a = src.clone(t, p["actions"], ligne)
    t.sd(a)["name"] = ""
    t.styles.style(t, a, {"flex-shrink": 0})
    f = src.clone(t, p["flags"], ligne)
    t.elem(f)["m_Classes"] = ["margin-left-global-gap-regular"]
    _centre_entre(t, ligne, a, [f])
    g = groupe()   # nation (drapeau + 3 lettres, la 2e à côté), sélections (une ligne, jeunes avant AGE_JEUNE ans)
    rang = boite(t, g, {"flex-shrink": 0, "overflow": "hidden", "margin-bottom": 2},
                 ["row-direction-normal", "align-items-center", "justify-content-center"])
    ligne_nation(t, k, rang, "person.nation", "nation.ThreeLetterName")
    nation_secondaire(t, k, rang)
    cap = src.clone(t, p["caps"], g)
    t.elem(cap)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    cellules = [x for x in t.children(cap) if (t.elem(x).get("m_TemplateAlias") or "") == "text-cell-button-medium"]
    if len(cellules) == 2:
        for x, li in ((cellules[0], ni.make_binding(b, OP_SUP, ["person.Age"], AGE_JEUNE - 1)),
                      (cellules[1], ni.make_binding(b, OP_INF, ["person.Age"], AGE_JEUNE))):
            s2 = ni.new_visible(t, k.s_vis, k.vis, cap, t.children(cap).index(x), "", li)
            move(t, x, s2)
            t.elem(x)["m_Classes"] = []
    g = groupe()   # âge (date de naissance), lieu de naissance
    src.clone(t, p["age"], g)
    ti = titre(t, k, g, *TITRE_LIEU)
    t.styles.style(t, ti, {"margin-top": 2, "margin-bottom": 1, "flex-shrink": 0})
    lieu = k.lieu.clone(t, k.bloc_lieu, g)
    t.sd(lieu)["name"] = ""
    t.elem(lieu)["m_Classes"] = ["row-direction-normal", "align-items-center", "justify-content-center"]
    t.styles.style(t, lieu, {"flex-shrink": 0, "align-self": "stretch", "overflow": "hidden"})
    for r in t.walk(lieu):
        if typ(t, r).endswith("SIText"):
            garde = [x for x in t.elem(r).get("m_Classes") or [] if x.startswith("padding-right")]
            t.elem(r)["m_Classes"] = CL_TEXTE_LIEU + garde
            t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0})
        elif r != lieu and typ(t, r).endswith("SIVisible"):
            t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0})
    g = groupe()   # le club (club parent / en prêt à)
    msgs += _bloc_clubs47(t, k, g)
    return msgs


def _etoiles_carte(t, k, parent):
    """v9 : niveau actuel et potentiel dans la carte. La partie « rapport » de l'en-tête de FM recopiée (elle se
    donne seule team = human.team et report = person.PlayerReportForContextTeam : l'équipe reçue n'y change rien),
    gardée sur son aiguillage report.UseCoachReportLayout : tes joueurs = les étoiles du rapport du préparateur ;
    les autres = les étoiles du rapport de supervision s'il y en a un (report.HasScoutedInfo), rien sinon. La 1re
    étoile sous le début de son titre (v8, DECALE_ETOILES)"""
    s = k.txt.s
    racine = s.children(s.tt["m_VisualTree"]["rid"])
    if not racine:
        return [f"{SOURCE_ARGS[0]} : forme inattendue (introuvable)"]
    c = k.txt.clone(t, racine[0], parent)
    t.sd(c)["name"] = ""
    sw = next((r for r in t.walk(c) if typ(t, r).endswith("BindableSwitchElement")
               and "UseCoachReportLayout" in json.dumps(t.sd(r).get("Binding") or {})), None)
    kids = t.children(sw) if sw is not None else []
    if len(kids) != 2:
        t.remove(c)
        return [f"{SOURCE_ARGS[0]} : aiguillage du rapport introuvable (étoiles de la carte)"]
    eclaireur, etoiles = kids
    v = visible_direct(t, k, sw, "report.HasScoutedInfo")
    move(t, v, sw, 0)
    t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.clone(etoiles, v)
    t.remove(eclaireur)
    msgs = []
    cases = [r for r in t.walk(c) if (t.elem(r).get("m_TemplateAlias") or "").endswith("AbilityStarRangeCell")]
    if len(cases) != 4:
        msgs.append(f"étoiles de la carte : {len(cases)} cases au lieu de 4 (introuvable)")
    # bloc v17 (Kinito, 08/11, capture 41 : « Niveau actuel centré sur la largeur des étoiles, pareil pour
    # Potentiel ») : les étoiles et leur titre centrés dans leur colonne (la colonne a la largeur des étoiles, la case
    # de FM a la même marge de chaque côté) ; jusqu'au bloc v16, la 1re étoile sous le début du titre (DECALE_ETOILES)
    for r in cases:
        t.styles.style(t, r, {"align-self": "center", "margin-left": 0})
    titres = [r for r in t.walk(c) if t.name(r) in ("CurrentAbilityText", "PotentialAbilityText")]
    if len(titres) != len(cases):   # un titre par case d'étoiles (deux dispositions du rapport de FM : 4 et 4)
        msgs.append(f"étoiles de la carte : {len(titres)} titres pour {len(cases)} cases (introuvable)")
    for r in titres:
        t.styles.style(t, r, {"align-self": "center"})
    # les deux colonnes (Niveau actuel, Potentiel) : 16 entre elles, rien après la 2e (le groupe reste centré)
    for r in t.walk(c):
        if t.name(r) == "CurrentAbility":
            t.styles.style(t, r, {"margin-right": 16, "align-items": "center"})
        elif t.name(r) == "PotentialAbility":
            t.styles.style(t, r, {"margin-right": 0, "align-items": "center"})
    return msgs


def manquants_carte(k):
    """les morceaux de la bande dont le bas de la carte a besoin (dans la tuile du bloc)"""
    m = [f"carte du joueur : {x}" for x in k.manque]
    for nom, v in (("remapper", k.rm_model), ("BindingSetter de la bannière", k.p.get("setter")),
                   ("texte de la nation", k.texte_nation), ("image du drapeau", k.boite_drapeau),
                   ("lieu de naissance", k.bloc_lieu), ("clubs", k.clubs.s), ("titre", k.txt_rid),
                   ("fonction élément d'une liste", k.fn_element), ("SIVisible", k.vis),
                   ("photo", k.photo), ("rapport (étoiles)", k.txt.s)):
        if v is None or v is False:
            m.append(f"carte du joueur : {nom}")
    return m


def _titre_chiffre(t, k, parent, fr, en):
    ti = titre(t, k, parent, fr, en)
    t.elem(ti)["m_Classes"] = list(CL_LAB)
    t.styles.style(t, ti, {"flex-shrink": 0, "max-width": {"unit": 2, "value": 100.0}, "margin-bottom": 1})
    return ti


def _classes_texte(t, r, classes):
    t.elem(r)["m_Classes"] = list(classes)
    t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})


def chiffres47(t, k, parent):
    """(v7, maquette 47) des colonnes séparées par un trait court ; dans chacune, en haut : un petit trait clair, le
    titre (gris, comme ceux de FM), la réponse en GRAND (22, heading-xl). v11 (Kinito, 08/11, captures 34-40) :
    Salaire (le statut en gras au-dessus, la FIN DE CONTRAT dessous, v12 : sa date en grand sous son titre ; le tout
    CLIQUABLE comme la cellule du contrat de la bannière de FM) | Valeur (sans cadre, soulignée au survol à la largeur de son texte, le clic de FM) | Dispo.
    transfert / Dispo. prêt | boutons d'action de FM (boutons47). v15 : pour tes joueurs, deux boutons-icônes à
    droite du salaire et de la date de fin (_icones_contrat)"""
    src, p, st = k.src, k.p, k.statut
    msgs = []
    zone = _colonne47(t, parent, POIDS_47["chiffres"])
    t.elem(zone)["m_Classes"] = ["row-direction-normal", "align-items-stretch", "align-self-stretch"]

    def col(nom, premier=False, tete=True):
        if not premier:   # le trait entre deux colonnes (court, comme la maquette)
            boite(t, zone, {"width": 1, "min-width": 1, "flex-shrink": 0, "align-self": "stretch",
                            "background-color": TRAIT, "margin-top": 34, "margin-bottom": 22})
        c = _colonne47(t, zone, POIDS_CHIFFRES[nom])
        t.styles.style(t, c, {"justify-content": "flex-start" if tete else "center", "padding-top": 30 if tete else 0,
                              "padding-right": CELLULE[1], "padding-left": 0 if premier else 14})
        if tete:
            boite(t, c, {"width": 36, "min-width": 36, "height": 3, "min-height": 3, "flex-shrink": 0,
                         "background-color": TRAIT_CHIFFRE, "margin-bottom": 11,
                         **{f"border-{x}-radius": 2 for x in ("top-left", "top-right", "bottom-left",
                                                              "bottom-right")}})
        return c
    # 1. le contrat : « Salaire », puis le bouton de la cellule du contrat de FM (text-cell-button-medium-secondary-text,
    #    son clic recopié de la bannière : il ouvre la fenêtre du contrat) avec dedans le statut (« Joueur important »)
    #    en gras, le salaire en grand et la fin de contrat ; « - » sans contrat
    c1 = col("contrat", premier=True)
    _titre_chiffre(t, k, c1, "Salaire", "Wage")
    sw = seul(t, src.s, p["contrat"], c1)
    t.elem(sw)["m_Classes"] = ["align-self-stretch"]
    tiret = src.clone(t, k.texte_date, sw)
    no_styles(t, tiret)
    _classes_texte(t, tiret, CL_VAL)
    # v15 : une ligne [le contrat | (tes joueurs) ses deux boutons-icônes, calés à droite de la case]
    boite_s = boite(t, sw, {}, ["row-direction-normal", "align-self-stretch"])
    msgs += _bouton_contrat(t, k, boite_s)
    boite(t, boite_s, {"flex-grow": 1, "flex-shrink": 1, "min-width": ECART_ICONES})
    msgs += _icones_contrat(t, k, boite_s)
    # 2. valeur : le bouton de FM (son clic et son infobulle), sans son icône ; cell-medium (le soulignement de FM au
    #    survol) MAIS sa hauteur de 16 (qui coupait le texte, capture 28) et tout fond retirés. v11 (capture 38 : « la
    #    ligne de soulignement déborde ») : le trait de FM (.cell-text-underline : absolu, 100 % de la largeur du
    #    bouton) suivait le bouton, étiré sur toute la colonne ; le bouton prend maintenant la largeur de son texte
    c2 = col("valeur")
    _titre_chiffre(t, k, c2, "Valeur", "Value")
    v = src.clone(t, p["valeur"], c2)
    t.elem(v)["m_Classes"] = ["align-self-stretch"]
    bouton = next((r for r in t.walk(v) if typ(t, r).endswith("SIButton")), None)
    if bouton is None:
        msgs.append("valeur : bouton de FM introuvable")
    else:
        for r in list(t.walk(bouton)):
            if r != bouton and t.name(r) == "game-concepts-transfer-value_small":
                t.remove(r)
        no_styles(t, bouton)
        t.elem(bouton)["m_Classes"] = ["cell-medium", "row-direction-normal", "align-items-center"]
        t.styles.style(t, bouton, {"height-kw": 2, "min-height": 0, "background-color": (0.0, 0.0, 0.0, 0.0),
                                   **{f"border-{x}-width": 0 for x in ("top", "bottom", "left", "right")},
                                   **{f"padding-{x}": 0 for x in ("top", "bottom", "left", "right")},
                                   "flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0},
                                   "align-self": "flex-start"})
        tx = next((r for r in t.children(bouton) if typ(t, r).endswith("SIText")), None)
        if tx is None:
            msgs.append("valeur : texte de FM introuvable")
        else:
            no_styles(t, tx)
            _classes_texte(t, tx, CL_VAL)
        boite(t, bouton, {}, ["cell-text-underline"])
    # 3. dispos : les deux cadres de la tuile de FM (titre, puis la réponse, ici en grand), l'un sous l'autre
    c3 = col("dispo")
    for i, nom_titre in enumerate(STATUT_CADRES):
        titre_fm = first(st.s, lambda r: st.s.name(r) == nom_titre)
        if titre_fm is None:
            msgs.append(f"{STATUT} : {nom_titre} introuvable")
            continue
        rm = remapper(t, k.rm_model, c3, {"player": ("person", JOUEUR)}, ["align-self-stretch"])
        t.styles.style(t, rm, {"margin-top": 8 if i else 0, "flex-shrink": 0})
        c = st.clone(t, st.s.parent[titre_fm], rm)
        t.sd(c)["name"] = ""
        for r in t.walk(c):
            if typ(t, r).endswith("SIText"):
                cl = list(t.elem(r).get("m_Classes") or [])
                cl = ["heading-xl" if x == "heading-xsmall-14px" else x for x in cl]
                _classes_texte(t, r, dict.fromkeys(cl + ["content-no-wrap", "content-ellipsis"]))
    # 4. les boutons d'action de FM, centrés en hauteur (ni trait clair ni titre)
    c4 = col("boutons", tete=False)
    msgs += boutons47(t, k, c4)
    return msgs


def _bouton_contrat(t, k, parent):
    """v11 (Kinito, 08/11 : « on remet la date de fin de contrat avec le contrat ; on rend le contrat cliquable comme
    sur la fiche de base du jeu ») : le bouton de la cellule du contrat de FM (text-cell-button-medium-secondary-text,
    SIButton « CellButton » et son trait de soulignement), avec le CLIC de la bannière (ses événements, surchargés
    dans la bannière : la fenêtre du contrat de FM, avec person) ; dedans, à la place de ses deux textes : le statut
    en gras, le salaire en grand, puis « Fin de contrat » et la date. Il prend la largeur de son texte le plus long
    (le trait aussi) ; sa hauteur de cellule (cell-medium) et son fond retirés, comme la valeur"""
    msgs = []
    b = k.cellule.clone(t, k.cellule_bouton, parent)
    t.sd(b)["name"] = ""
    t.sd(b)["Events"], t.sd(b)["Events_UxmlAttributeFlags"] = copy.deepcopy(k.clic_contrat), 1
    for x in list(t.children(b)):
        if typ(t, x).endswith("SIText"):
            t.remove(x)
    no_styles(t, b)
    t.elem(b)["m_Classes"] = ["cell-medium", "cell-button", "column-direction-normal", "align-items-start"]
    t.styles.style(t, b, {"height-kw": 2, "min-height": 0, "background-color": (0.0, 0.0, 0.0, 0.0),
                          **{f"border-{x}-width": 0 for x in ("top", "bottom", "left", "right")},
                          **{f"padding-{x}": 0 for x in ("top", "bottom", "left", "right")},
                          "flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0},
                          "align-self": "flex-start"})
    if not any(t.name(x) == "Underline" for x in t.children(b)):
        msgs.append("contrat : trait de soulignement de FM introuvable")
    texte_direct(t, k, b, CHEMIN_STATUT, CL_STAT)
    texte_direct(t, k, b, CHEMIN_SALAIRE, CL_VAL)
    # v12 (Kinito, 08/11, capture 41 : « la date en dessous de Fin de contrat plutôt qu'à côté, aussi grosse que le
    # salaire ; garder Fin de contrat tel quel ») : le titre, puis la date en grand (CL_VAL, comme le salaire)
    ti = _titre_chiffre(t, k, b, "Fin de contrat", "Contract Expires")
    t.styles.style(t, ti, {"flex-shrink": 0, "margin-top": 4})
    texte_direct(t, k, b, CHEMIN_DATE, CL_VAL)
    return msgs


def _fantome(t, r):
    """un texte recopié à l'identique, invisible (couleur transparente) et sans souris : il ne sert qu'à prendre la
    même hauteur que son jumeau du contrat"""
    t.styles.style(t, r, {"color": (0.0, 0.0, 0.0, 0.0)})
    _sans_clic(t, r)
    return r


def _icones_contrat(t, k, parent):
    """v15 (Kinito, 08/11 : pour TES joueurs, à droite du salaire une icône « Discuter d'un nouveau contrat », en
    dessous, à droite de la fin du contrat, une icône contrat « pour lui proposer un nouveau contrat » ; seulement en
    icône, grisées quand ce n'est pas possible) : une colonne de ICONE_B de large, sous team = human.Team (comme
    boutons47), visible si le contrat est chez toi (CONTRAT_HUMAIN). Pour être en face du salaire et de la date À
    TOUTES LES TAILLES DU TEXTE, la colonne reprend les textes du contrat à l'identique, invisibles (_fantome : statut,
    salaire, « Fin de contrat », date, mêmes liaisons et mêmes classes, donc mêmes hauteurs) ; chaque icône est centrée
    sur la ligne du salaire ou de la date (une place absolue qui couvre la ligne). Chaque case d'icône : le bouton
    d'action de FM avec SON gabarit d'icône (GABARITS_ICONES), et dessous le même bouton-icône grisé
    (_bouton_gris_icone), que le bouton de FM pousse hors de la case quand il est là"""
    msgs = []
    rm = remapper(t, k.rm_model, parent, {"team": ("human.Team", EQUIPE)}, ["column-direction-normal"])
    t.styles.style(t, rm, {"flex-shrink": 0, "align-self": "stretch"})
    g = visible_bool(t, k, rm, CONTRAT_HUMAIN)
    t.elem(g)["m_Classes"] = ["column-direction-normal"]
    t.styles.style(t, g, {"width": ICONE_B, "min-width": ICONE_B, "max-width": ICONE_B, "flex-shrink": 0,
                          "flex-grow": 1})
    _fantome(t, texte_direct(t, k, g, CHEMIN_STATUT, CL_STAT))
    for i, (cle, _nom, numero, fr, en) in enumerate(ACTIONS_CONTRAT):
        if i:
            ti = _titre_chiffre(t, k, g, "Fin de contrat", "Contract Expires")
            t.styles.style(t, ti, {"flex-shrink": 0, "margin-top": 4})
            _fantome(t, ti)
        ligne = boite(t, g, {"flex-shrink": 0, "align-self": "stretch"}, ["column-direction-normal"])
        _fantome(t, texte_direct(t, k, ligne, (CHEMIN_SALAIRE, CHEMIN_DATE)[i], CL_VAL))
        place = boite(t, ligne, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0},
                      ["column-direction-normal", "align-items-center", "justify-content-center"])
        _sans_clic(t, place)
        case = boite(t, place, _carre(ICONE_B, overflow="hidden"), ["column-direction-normal"])
        bt = k.boutons.clone(t, k.pouces["PraisePlayerButton"], case)
        t.sd(bt)["name"] = ""
        _regler_bouton_action(t, bt, numero, GABARITS_ICONES[cle][1])
        _w, n = _bouton_gris_icone(t, k, case, fr, en, GABARITS_ICONES[cle][2])
        if n != 1:
            msgs.append(f"infobulle d'un bouton-icône : {n} textes au lieu de 1 (introuvable)")
    return msgs


# v11 (Kinito, 08/11, captures 39-40 : les actions du menu « Actions » de FM, en boutons dans la bande, « toujours
# visibles mais grisés quand pas dispo ») : le bouton d'action de FM (FM.UI.FMActionButton, celui de Féliciter :
# FM y fabrique en jeu le bouton de l'action, son icône, son texte TRADUIT et son infobulle, grisé si l'action n'est
# pas possible, un menu si l'action a des choix : la durée de la période d'essai), avec le numéro de l'action
# (FM.GamePlugin.ActionID, lu dans les métadonnées du jeu le 08/11/2026 : PraisePlayerTrainingDevelopment
# 1800548932 = Féliciter, PlayerQuickScoutClub 943026793 = « Observer joueur », comme dans les modèles de FM).
# Le numéro est choisi par le NOM de l'action (le texte affiché vient du jeu : il dira en jeu si c'est la bonne)
# v12 : chaque action avec son LIBELLÉ DE FM (fichier des langues du jeu, français / anglais, identifiant entre
# parenthèses ; vus en jeu sur les captures 41-45 pour les quatre de Geubbels et Bonello) : il sert au bouton grisé
# (quand FM retire l'action) et à l'infobulle qui montre le texte entier (le bouton de FM coupe le sien par « … »)
ACTIONS_47 = {
    # v15 (Kinito, 08/11 : pour tes joueurs, le contrat avec le contrat, le départ avec le départ) : « Interroger
    # l'agent sur l'intérêt suscité » (« Ask Agent About Market Interest » : AskPlayerAgentAboutGenerateMarketInterest,
    # lu dans les métadonnées du jeu, choisi par son nom anglais) à la place de « Discuter d'un nouveau contrat avec
    # l'agent », qui passe en icône dans la case du contrat (ACTIONS_CONTRAT)
    "a_toi": (("AskPlayerAgentAboutGenerateMarketInterest", 1449750636,
               "Interroger l'agent sur l'intérêt suscité", "Ask Agent About Market Interest"),       # (100a29d7)
              ("PersonAskIntermediariesToOfferPlayerToClubs", 1517175660,
               "Engager un intermédiaire pour vendre le joueur", "Hire An Intermediary To Sell Player"),  # (100920ce)
              ("PersonOfferToClubs", 1164992875,
               "Proposer via TransferRoom", "Offer via TransferRoom")),                                # (100aa008)
    "autre": (("PersonAskPlayerAgentAboutClientAvailability", 1999843434,
               "Interroger agent sur disponibilité", "Ask Agent About Availability"),                 # (100a29de)
              ("PersonOfferTrialToPlayer", 1749513580,
               "Proposer période d'essai", "Offer Trial"),                                            # (1003b690)
              ("PersonMakeOfferForPlayer", 1933656696,
               "Faire une offre", "Make An Offer")),                                                 # (1003b68f)
    "libre": (("PersonAskPlayerAgentAboutClientAvailability", 1999843434,
               "Interroger agent sur disponibilité", "Ask Agent About Availability"),
              ("PersonOfferTrialToPlayer", 1749513580,
               "Proposer période d'essai", "Offer Trial"),
              # v13 (Kinito, capture 51 : « Proposer un contrat » grisé chez Stavrevski, alors que le menu Actions de
              # FM le propose) : l'action « Approach To Sign » (son libellé anglais) est PersonApproachToSign ;
              # PersonOfferContract (v12) est celle du bloc Contrat de FM pour TES joueurs et le staff
              ("PersonApproachToSign", 1749837424,
               "Proposer un contrat", "Approach To Sign")),                                          # (1003b692)
}
# v12 (Kinito : « un joueur que j'ai prêté m'appartient toujours ») : « à toi » = son CONTRAT est chez toi
# (person.FullContract.MainTeam.IsHuman), dans la branche « a un contrat » ; v11 prenait person.Team.IsHuman (le club
# où il joue : un prêté chez un autre avait les boutons d'un autre club). Un joueur prêté CHEZ toi a les boutons d'un
# autre club (son contrat est ailleurs : tu peux lui faire une offre)
CONTRAT_HUMAIN = "person.FullContract.MainTeam.IsHuman"
# v12 : les boutons sous team = human.Team, comme le bloc Contrat de FM (PersonContractBlockNew, qui pose ces mêmes
# boutons) : l'action se résout pour TON équipe (v11 sans : « Proposer un contrat » n'est pas venu chez le joueur libre)
BOUTON_H = 32        # hauteur d'un bouton secondaire de FM (--interaction-global-height-md = 32) : la case ne bouge pas
ECART_BOUTONS = 6
# v12 (Kinito : « les boutons disparaissent quand je les utilise : qu'ils restent visibles, grisés, non cliquables ») :
# FM CACHE un bouton d'action quand il ne donne pas l'action (ses modèles de liste d'actions : SIVisible sur
# « action »), il ne le grise jamais. Sous le bouton de FM, dans la même case (BOUTON_H, qui coupe), notre bouton grisé
# (_bouton_gris) : le bouton de FM, là, prend les 32 du haut et le pousse dessous, hors de la case ; caché, il ne
# prend plus de place et le bouton grisé remonte. GRIS_H < BOUTON_H : poussé par un bouton de FM d'au moins
# BOUTON_H - (BOUTON_H - GRIS_H) = GRIS_H de haut, il est tout entier hors de la case
GRIS_H = 30
OBS_L = 116          # « Observer joueur » : la largeur de son bouton de FM (110 mesurés, capture 43), fixe
# v13 (Kinito, captures 46-51 : « l'infobulle s'ouvre 2 fois », « enlever l'icône de discussion / de transfert ») : le
# bouton d'action de FM est fabriqué par FM avec SON gabarit (ActionsListWidget -> GenericActionButtonWidget ->
# GenericActionButtonDataWidget) : une icône (item.MenuIconID) et SON infobulle (item.Hint : une explication longue, ou
# la raison du gris), en plus de la nôtre (v12, posée sur la case). Nos boutons prennent NOTRE gabarit, comme les pouces
# de 26.14 (vus en jeu) : ce gabarit de FM recopié À PLAT dans un modèle de FM cité par RIEN (modeles_libres.py, puis
# guid_partout.py sur TOUS les bundles, scènes comprises, le 08/11 : seul l'index de son propre bundle le cite ; ni le
# code du jeu, ni un script du skin), refait à chaque passage depuis son ORIGINAL, remis d'origine au retrait. Ses deux
# branches (bouton simple | menu, pour les durées de la période d'essai), SANS icône, et UNE infobulle : le texte
# entier de l'action (item.Text), puis l'explication de FM dessous quand il en donne une (item.Hint)
GABARIT_BOUTON = "MatchTacticalFocusSmallRow"
GUID_GABARIT = "02d477df259e13e40b258ff273727164"
NOM_GABARIT = f"{PREFIXE}Bouton-v{VERSION}{SUFFIXE}"
# v15 (Kinito, 08/11 : « à côté du contrat du joueur une icône Discuter d'un nouveau contrat, et en dessous une icône
# contrat pour lui proposer un nouveau contrat ; seulement en icône, avec la même règle de grisé ; dans la case du
# salaire, à droite du salaire et de la fin du contrat ; que pour nos joueurs ») : deux boutons d'action de FM en
# icône. Chacun a SON gabarit (l'icône est FIXE, choisie ici, et grisée avec le bouton quand FM le grise : elle est
# dans le SIEnabled item.Disabled du gabarit ; l'icône de FM, item.MenuIconID, arrive une image après le reste, comme
# la loupe d'« Observer joueur », et on ne sait pas laquelle FM donne à chaque action), rangé dans un modèle de FM
# cité par RIEN, du même bundle que GABARIT_BOUTON (modeles_libres.py, puis guid_partout.py sur TOUS les bundles,
# scènes comprises, le 08/11 : seul l'index de son propre bundle les cite ; aucun script du skin ni de l'app d'Alex)
# ; l'icône : celles de FM (sa table des icônes d'action, IconIDDataCollection : la bulle et le contrat en cours)
GABARITS_ICONES = {
    "discuter": ("EditSessionContinentRow", "1282389cc1d106345941228ede38e222", "ui-concepts-speech-bubble_small"),
    "contrat": ("EditSessionGender", "0953f75f9900adb41a63c10d91d02e90",
                "game-concepts-contract-negotiated-ongoing_small"),
}
# (gabarit, nom de l'action, numéro, libellé de FM fr / en) ; numéros lus dans les métadonnées du jeu (le bloc Contrat
# de FM, PersonContractBlockNew, pose ces deux-là pour tes joueurs) ; libellés : fichier des langues du jeu
ACTIONS_CONTRAT = (("discuter", "PersonAskAgentAboutClientContractRenewal", 1882353528,
                    "Discuter d'un nouveau contrat avec l'agent", "Discuss New Contract With Agent"),   # (100a29d9)
                   ("contrat", "PersonOfferContract", 2000111204,
                    "Proposer nouveau contrat", "Offer New Contract"))                                 # (100491c9)
ICONE_B = 28         # un bouton-icône : carré de 28 (le salaire et la date font ~26 de haut au texte Normal)
ICONE_T = 16         # l'icône de FM (_small : 16 x 16, comme dans ses boutons)
ECART_ICONES = 8     # au moins, entre le contrat et ses icônes (calées à droite de la case)


def nom_icone(cle):
    return f"{PREFIXE}Icone{cle.capitalize()}-v{VERSION}{SUFFIXE}"


def _regler_bouton_action(t, bt, numero=None, gabarit=""):
    """un bouton d'action de FM (FMActionButton) à la largeur de sa case (GrowToWidth : FM coupe son texte par
    « … »), le 1er choix, person ; numero : son action (sinon celle qu'il a) ; gabarit : le GUID de son gabarit
    (ActionsListWidget ; vide : celui de FM)"""
    sd = t.sd(bt)
    reglages = [("RecordsBinding", {"m_path": "person"}), ("ShowOnlyFirstButton", 1), ("GrowToWidth", 1),
                ("ActionsListWidget", {"m_AssetGUID": gabarit, "m_SubObjectName": "", "m_SubObjectType": ""})]
    if numero is not None:
        reglages.append(("ActionId", numero))
    for cle_sd, val in reglages:
        sd[cle_sd], sd[cle_sd + "_UxmlAttributeFlags"] = copy.deepcopy(val), 1
    no_styles(t, bt)
    t.elem(bt)["m_Classes"] = []
    t.styles.style(t, bt, {"align-self": "stretch", "flex-shrink": 0, "min-width": 0, "overflow": "hidden",
                           "max-width": {"unit": 2, "value": 100.0}})


def _sans_clic(t, r):
    """pickingMode Ignore : la souris passe à travers (vers la boîte qui porte l'infobulle)"""
    t.sd(r)["pickingMode"], t.sd(r)["pickingMode_UxmlAttributeFlags"] = 1, 1


def _bouton_gris(t, k, parent, fr, en):
    """v12 : le bouton d'une action que FM ne donne pas, GRISÉ et sans clic, avec le libellé de FM : le bouton
    secondaire de FM (buttons-button-secondary-default) DÉSACTIVÉ (son état :disabled de FM : bordure et texte
    grisés, sans survol), dans le SIEnabled de FM (celui du bouton d'action : son opacité des boutons grisés), désactivé
    lui aussi (person.IsPlayer, inversé). GRIS_H de haut, sous le bouton de FM de la même case (voir GRIS_H). v13 :
    dans une boîte qui porte l'infobulle au libellé entier (bulle_texte ; la v12 la posait sur toute la case, et
    elle s'ouvrait AUSSI au survol du bouton de FM, en plus de la sienne) ; le bouton grisé laisse passer la souris
    jusqu'à elle. Poussée hors de la case quand FM montre son bouton, elle n'y prend plus la souris (la case coupe).
    v14 (Kinito, capture 52 et vidéos : « Observer joueur » fait toujours le flash) : la vidéo du 08/11, image par
    image : quand FM remplit la fiche EN PLACE au changement de joueur, son bouton disparaît 2 à 3 images (~70-100 ms),
    le temps que FM redonne l'action ; notre bouton grisé se voyait à sa place, d'où blanc -> gris -> blanc. Le
    bouton n'est plus désactivé par lui-même (enabledSelf) : son gris (:disabled de FM) vient SEULEMENT du SIEnabled
    person.IsPlayer inversé, comme son opacité. Joueur chargé : IsPlayer vrai, gris comme avant. Pendant le chargement
    (le joueur pas encore lu par FM), IsPlayer n'est pas vrai : le bouton a le look normal, celui du bouton de FM qui
    arrive (déduit, pas vu : si FM garde la valeur du joueur d'avant, il reste gris ces images-là, comme avant)"""
    w = boite(t, parent, {"height": GRIS_H, "min-height": GRIS_H, "max-height": GRIS_H, "flex-shrink": 0,
                          "margin-top": BOUTON_H - GRIS_H, "align-self": "stretch", "min-width": 0},
              ["column-direction-normal"])
    en_ = _actif_gris(t, k, w)
    b = boite(t, en_, {"height": GRIS_H, "min-height": GRIS_H, "max-height": GRIS_H, "flex-shrink": 0, "min-width": 0,
                       "align-self": "stretch"},
              ["buttons-button-secondary-default", "row-direction-normal", "align-items-center"])
    tx = titre(t, k, b, fr, en)
    t.elem(tx)["m_Classes"] = ["content-no-wrap", "content-ellipsis"]   # police et couleur : celles du bouton
    t.styles.style(t, tx, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})
    for x in (en_, b, tx):
        _sans_clic(t, x)
    _b, n = bulle_texte(t, k, w, fr, en)
    return w, n


def _actif_gris(t, k, w):
    """la boîte w PREND la souris (pickingMode Position, posé : la boîte de base de la tuile laisse passer la souris) ;
    dedans, le SIEnabled de FM (celui du bouton d'action : son opacité des boutons grisés), désactivé par
    person.IsPlayer inversé (v14 : rien d'autre ne le grise) ; rend le SIEnabled"""
    t.sd(w)["pickingMode"], t.sd(w)["pickingMode_UxmlAttributeFlags"] = 0, 1
    en_ = seul(t, k.actif_src.s, k.actif, w)
    sd = t.sd(en_)
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = "person.IsPlayer"
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
    sd["IgnoreDisabledOpacity"], sd["IgnoreDisabledOpacity_UxmlAttributeFlags"] = 0, 1
    t.elem(en_)["m_Classes"] = ["column-direction-normal"]
    t.styles.style(t, en_, {"flex-grow": 1, "align-self": "stretch", "min-width": 0})
    return en_


def _carre(cote, **css):
    return {"width": cote, "min-width": cote, "max-width": cote, "height": cote, "min-height": cote,
            "max-height": cote, "flex-shrink": 0, **css}


def _icone(t, parent, classe, k=None):
    """une icône de FM (sa classe d'image), ICONE_T de côté, sans souris ; k donné (dans un gabarit, qui n'a pas
    d'élément simple à recopier) : l'élément de la ligne du bouton d'action de FM, vidé de ses classes et styles"""
    if k is None:
        ic = boite(t, parent, _carre(ICONE_T), [classe])
    else:
        ic = _gab_copie(t, k.g_donnees, k.gab["ligne"], parent)
        t.elem(ic)["m_Classes"], t.elem(ic)["m_RuleIndex"] = [classe], -1
        t.styles.style(t, ic, _carre(ICONE_T))
    _sans_clic(t, ic)
    return ic


def _bouton_gris_icone(t, k, parent, fr, en, classe):
    """v15 : le bouton-icône d'une action que FM ne donne pas : comme _bouton_gris (le bouton secondaire de FM dans le
    SIEnabled grisé, l'infobulle au libellé de FM), carré de ICONE_B avec l'icône au milieu. Sous le bouton de FM de
    la même case : celui-ci, montré, fait ICONE_B de haut (son gabarit le fixe) et le pousse hors de la case"""
    w = boite(t, parent, _carre(ICONE_B), ["column-direction-normal"])
    en_ = _actif_gris(t, k, w)
    b = boite(t, en_, _carre(ICONE_B, **{f"padding-{x}": 0 for x in ("top", "bottom", "left", "right")}),
              ["buttons-button-secondary-default", "row-direction-normal", "align-items-center",
               "justify-content-center"])
    _icone(t, b, classe)
    for x in (en_, b):
        _sans_clic(t, x)
    _b, n = bulle_texte(t, k, w, fr, en)
    return w, n


# ---------- v13 : notre gabarit de bouton d'action (modèle de FM cité par rien, à nous seuls) ----------
def _gab_copie(t, src, rid, parent, nom=None):
    """un élément d'un modèle de FM d'origine, SANS ses enfants, ses classes et ses règles de style gardées (comme les
    gabarits de 26.14 : copier_el)"""
    r = t.clone(rid, parent, src=src.s)
    for x in list(t.children(r)):
        t.remove(x)
    t.styles.copy_from(src.styles, t, r)
    if nom is not None:
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
    return r


def _gab_contenu(t, k, parent, chevron):
    """dans le bouton (ou le menu) du gabarit : le texte de l'action de FM (sa ligne et son texte, « … » s'il est trop
    long ; SANS l'icône de FM), le chevron du menu, et UNE infobulle : le texte entier (item.Text), puis l'explication
    de FM s'il en donne une (item.Hint, son SIVisible de FM). Rien de la bulle de FM (TooltipVisible : item.Hint seul)"""
    g, sd_, sb = k.gab, k.g_donnees, k.actif_src
    ligne = _gab_copie(t, sd_, g["ligne"], parent)
    t.styles.style(t, ligne, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
    tx = _gab_copie(t, sd_, g["texte"], ligne)
    t.styles.style(t, tx, {"flex-shrink": 1, "min-width": 0})
    if chevron:
        _gab_copie(t, sb, g["chevron"], parent)
    _gab_bulle(t, k, parent)


def _gab_icone(t, k, parent, classe):
    """v15 : dans le bouton (ou le menu) d'un gabarit d'icône : carré de ICONE_B, l'icône fixe au milieu (dans le
    SIEnabled item.Disabled : grisée avec le bouton), et la même infobulle que les boutons à texte"""
    t.styles.style(t, parent, _carre(ICONE_B, **{f"padding-{x}": 0 for x in ("top", "bottom", "left", "right")},
                                     **{"flex-grow": 0, "justify-content": "center", "align-items": "center"}))
    _icone(t, parent, classe, k)
    _gab_bulle(t, k, parent)


def _gab_bulle(t, k, parent):
    """l'infobulle du gabarit : le texte entier (item.Text), puis l'explication de FM s'il en donne une (item.Hint)"""
    g, sd_ = k.gab, k.g_donnees
    bu = _gab_copie(t, sd_, g["bulle"], parent)
    lab = _gab_copie(t, sd_, g["bulle_texte"], bu)
    lab_sd = t.sd(lab)
    lab_sd["TextBinding"] = copy.deepcopy(lab_sd["TextBinding"])
    lab_sd["TextBinding"]["m_direct"]["Path"]["m_path"] = "item.Text"
    lab_sd["DebugDisplay"] = "item.Text"
    vis = _gab_copie(t, sd_, g["bulle_vis"], bu)
    t.elem(vis)["m_Classes"] = []
    expl = _gab_copie(t, sd_, g["bulle_texte"], vis)
    t.elem(expl)["m_Classes"] = ["body-sm", "global-text-secondary", "content-wrap"]
    t.styles.style(t, expl, {"margin-top": 4})


def construire_gabarit(t, k, icone=None, cle=None):
    """réécrit le modèle t (GABARIT_BOUTON, cité par rien) en gabarit de nos boutons d'action : le gabarit de FM
    recopié À PLAT (ActionsListWidget : ses paramètres, ActionValid, FirstRemapper -> item ; GenericActionButtonWidget :
    grow-to-width, SIEnabled item.Disabled, l'aiguillage item.ChildList [bouton simple | menu], leurs styles, le
    SIButton et ses événements, le SIDropdown et ses événements), le contenu de GenericActionButtonDataWidget remplacé
    par _gab_contenu (sans icône, une infobulle). v15 : icone (sa classe) et cle donnés, un gabarit d'ICÔNE
    (GABARITS_ICONES[cle]) : le bouton et le menu en carré, l'icône fixe au milieu (_gab_icone)"""
    g, sl, sb = k.gab, k.g_liste, k.actif_src
    racine = t.tt["m_VisualTree"]["rid"]
    for x in list(t.children(racine)):
        t.remove(x)
    att = _gab_copie(t, sl, g["attente_liste"], racine, NOM_GABARIT if icone is None else nom_icone(cle))
    val = _gab_copie(t, sl, g["valide"], att)
    prem = _gab_copie(t, sl, g["premier"], val)
    attb = _gab_copie(t, sb, g["attente_bouton"], prem)
    larg = _gab_copie(t, sb, g["largeur"], attb)
    act = _gab_copie(t, sb, g["actif"], larg)
    choix = _gab_copie(t, sb, g["choix"], act)
    st = _gab_copie(t, sb, g["style_simple"], choix)
    bt = _gab_copie(t, sb, g["bouton"], st)
    _gab_copie(t, sb, g["degrade"], bt)
    if icone is None:
        _gab_contenu(t, k, bt, chevron=False)
    else:
        _gab_icone(t, k, bt, icone)
    mv = _gab_copie(t, sb, g["menu_variables"], choix)
    ms = _gab_copie(t, sb, g["menu_style"], mv)
    mn = _gab_copie(t, sb, g["menu"], ms)
    if icone is None:
        _gab_contenu(t, k, mn, chevron=True)
        return [f"{GABARIT_BOUTON} : notre gabarit de bouton d'action (v{VERSION})"]
    _gab_icone(t, k, mn, icone)
    return [f"{GABARITS_ICONES[cle][0]} : notre gabarit de bouton-icône « {cle} » (v{VERSION})"]


def morceaux_gabarit(sl, sb, sd):
    """les morceaux des trois modèles de FM du bouton d'action (d'origine), repérés par nom, type et liaison :
    sl ActionsListWidget, sb GenericActionButtonWidget, sd GenericActionButtonDataWidget ; None si introuvable"""
    def racine(s):
        return s.tt["m_VisualTree"]["rid"] if s is not None else None

    def enfant(s, r, fin):
        if s is None or r is None:
            return None
        return next((x for x in s.children(r) if typ(s, x).endswith(fin)), None)

    def nomme(s, nom, fin):
        return s and _premier(s, lambda r: s.name(r) == nom and typ(s, r).endswith(fin))

    g = {"attente_liste": enfant(sl, racine(sl), "BindingExpect"),
         "valide": nomme(sl, "ActionValid", "SIVisible"),
         "premier": nomme(sl, "FirstRemapper", "BindingSetter"),
         "attente_bouton": enfant(sb, racine(sb), "BindingExpect")}
    g["largeur"] = enfant(sb, g["attente_bouton"], "SIStyleSetter")      # grow-to-width -> flex-grow-class
    g["actif"] = enfant(sb, g["largeur"], "SIEnabled")                    # item.Disabled
    g["choix"] = enfant(sb, g["actif"], "BindableSwitchElement")          # item.ChildList : [simple | menu]
    g["style_simple"] = nomme(sb, "SimpleButton", "SIStyleSetter")
    g["bouton"] = enfant(sb, g["style_simple"], "SIButton")
    g["degrade"] = enfant(sb, g["bouton"], "SIGradient")
    g["menu_variables"] = nomme(sb, "DropdownButton", "BindingVariables")
    g["menu_style"] = enfant(sb, g["menu_variables"], "SIStyleSetter")
    g["menu"] = enfant(sb, g["menu_style"], "SIDropdown")
    g["chevron"] = nomme(sb, "ui-concepts-chevron-down_small", "VisualElement")
    att_d = enfant(sd, racine(sd), "BindingExpect")
    g["ligne"] = enfant(sd, att_d, "VisualElement")
    g["texte"] = sd and _premier(sd, lambda r: typ(sd, r).endswith("SIText") and _chemin_direct_texte(sd, r) == "item.Text")
    g["bulle_vis"] = nomme(sd, "TooltipVisible", "SIVisible")
    g["bulle"] = sd and _premier(sd, lambda r: typ(sd, r).endswith(".Tooltip"))
    g["bulle_texte"] = enfant(sd, g["bulle"], "SIText")
    # la forme attendue (lue le 08/11) : l'aiguillage a deux branches, le texte de la ligne est item.Text, celui de la
    # bulle item.Hint
    if g["choix"] is not None and [x for x in sb.children(g["choix"])] != [g["style_simple"], g["menu_variables"]]:
        g["choix"] = None
    if g["texte"] is not None and sd.parent.get(g["texte"]) != g["ligne"]:
        g["texte"] = None
    if g["bulle_texte"] is not None and _chemin_direct_texte(sd, g["bulle_texte"]) != "item.Hint":
        g["bulle_texte"] = None
    return g


def _chemin_direct_texte(s, r):
    b = (s.sd(r) or {}).get("TextBinding") or {}
    return ((b.get("m_direct") or {}).get("Path") or {}).get("m_path", "") if b.get("m_kind") == 1 else ""


def gabarit_a_jour(modele=GABARIT_BOUTON, nom=NOM_GABARIT):
    o = hp.ouvrir(modele)
    return o is not None and any(o[3].name(x) == nom for x in o[3].children(o[3].tt["m_VisualTree"]["rid"]))


def icones_a_jour():
    """v15 : les deux gabarits de boutons-icônes, à cette version, dans le jeu"""
    return all(gabarit_a_jour(modele, nom_icone(cle)) for cle, (modele, _g, _i) in GABARITS_ICONES.items())


def retirer_gabarit():
    """nos gabarits (boutons d'action, et v15 : boutons-icônes) remis d'origine"""
    msgs = []
    for modele in [GABARIT_BOUTON] + [m for m, _g, _i in GABARITS_ICONES.values()]:
        o = ouvrir_modele(modele)
        if o is None or not any((o[3].name(x) or "").startswith(PREFIXE) for x in o[3].walk()):
            continue
        orig = ouvrir_modele(modele, original=True)
        if orig is None:
            msgs.append(f"{modele} : pas de sauvegarde d'origine, laissé")
            continue
        enregistrer(*orig, modele=modele)
        msgs.append(f"{modele} : remis d'origine")
    return msgs


def bulle_texte(t, k, parent, fr, en):
    """v12 : l'infobulle de FM (StandardTextTooltip) avec un TEXTE FIXE, posée à plat dans parent (comme dans le
    bouton des favoris de FM, BookmarkButton) : elle s'ouvre au survol de parent, ses enfants compris (le bouton de FM
    dedans garde son clic) ; ni couverture ni place prise"""
    b, n = bulle(t, k, parent, chemin="")
    t.elem(b)["m_Classes"] = []
    for ov in t.elem(b).get("m_SerializedDataOverride") or []:
        d = (t.refs.get(ov["m_SerializedData"]["rid"]) or {}).get("data") or {}
        if isinstance(d.get("TextBinding"), dict):
            d["TextBinding"]["m_kind"] = 0
            d["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            d["text"], d["text_UxmlAttributeFlags"] = L(fr, en), 1
            d["DebugDisplay"] = d["text"]
    return b, n


def boutons47(t, k, parent):
    """trois boutons d'action de FM l'un sous l'autre, tous de la largeur de la case (GrowToWidth), chacun dans une
    case de hauteur fixe (FM refait le contenu d'un bouton d'action à chaque changement de joueur : vide un instant,
    il ferait sauter les autres). Sans contrat : libre ; contrat chez toi : a_toi ; sinon : autre. v12 : sous
    team = human.Team (comme le bloc Contrat de FM) ; dans chaque case, sous le bouton de FM, le même bouton GRISÉ
    (quand FM retire l'action). v13 : le bouton de FM avec NOTRE gabarit (GABARIT_BOUTON : sans icône, une seule
    infobulle) ; l'infobulle du libellé fixe seulement sur le bouton grisé"""
    msgs = []
    rm = remapper(t, k.rm_model, parent, {"team": ("human.Team", EQUIPE)},
                  ["column-direction-normal", "align-self-stretch"])
    sw = seul(t, k.src.s, k.p["contrat"], rm)   # person.fullcontract.IsValid : [faux | vrai]
    t.elem(sw)["m_Classes"] = ["align-self-stretch"]
    groupes = {"libre": boite(t, sw, {}, ["column-direction-normal", "align-self-stretch"])}
    avec = boite(t, sw, {}, ["column-direction-normal", "align-self-stretch"])
    for cle, inverse in (("a_toi", False), ("autre", True)):
        g = visible_bool(t, k, avec, CONTRAT_HUMAIN, inverse=inverse)
        t.elem(g)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
        groupes[cle] = g
    for cle, g in groupes.items():
        for i, (_nom, numero, fr, en) in enumerate(ACTIONS_47[cle]):
            case = boite(t, g, {"height": BOUTON_H, "min-height": BOUTON_H, "max-height": BOUTON_H, "flex-shrink": 0,
                                "overflow": "hidden", "margin-top": ECART_BOUTONS if i else 0},
                         ["column-direction-normal", "align-self-stretch"])
            bt = k.boutons.clone(t, k.pouces["PraisePlayerButton"], case)
            t.sd(bt)["name"] = ""
            _regler_bouton_action(t, bt, numero, GUID_GABARIT)
            _w, n = _bouton_gris(t, k, case, fr, en)
            if n != 1:
                msgs.append(f"infobulle d'un bouton d'action : {n} textes au lieu de 1 (introuvable)")
    return msgs


# v9 (Kinito, 07/11) : les Pour / Contre avec les PASTILLES D'ALEX (comme FM24 : rond coloré selon la note, logo blanc,
# la phrase au survol). Sa fonction entete_fiche (moteur commun\pastilles_pour_contre.py, v15) réécrit ProConRow, une
# cellule de FM que le jeu n'utilise pas, en pastille de 28 px (logo 18), paramètre « procon » ; il la montre par une
# WrappedObjectList (celle de TeamMeetingBlock) sur report.ScoutedProConsList.ProsList / ConsList. On fait pareil : la
# liste de FM d'origine, sa pastille par son GUID, rien de chez lui n'est touché. Sa pastille absente du jeu (sa
# fonction pas passée) : nos icônes de FM d'avant (_icones_pc).
GUID_PASTILLE_ALEX = "1d9ea6f83e853594c9a3339ba036281b"   # ProConRow (cellule de FM inutilisée, réécrite par Alex)
NOM_PASTILLE_ALEX = "UIPickerPastilleBandeau-v"             # son nom quand Alex l'a réécrite (v15 au 07/11)
PASTILLE_ALEX_PAS = 28 + 2                                  # sa pastille (PASTILLE_BANDEAU) et ses marges de 1
PASTILLE_ALEX_RANGS = 2                                     # deux rangées au plus par liste (comme ses infobulles)


def pastille_alex():
    """vrai si ProConRow, dans le jeu tel qu'il est, est la pastille d'Alex"""
    try:
        _b, _o, tt = nb.find_vta("ProConRow")
    except Exception:
        return False
    if not tt:
        return False
    s = Tree(tt)
    return any((s.name(r) or "").startswith(NOM_PASTILLE_ALEX) for r in s.walk())


def _pastilles_alex(t, k, parent, chemin, colonne=False):
    """une liste de FM (WrappedObjectList) qui montre la pastille d'Alex pour chaque élément de chemin ; colonne : les
    pastilles l'une sous l'autre (bloc v16 : chacune en face de sa phrase), toutes"""
    w = k.liste_src.clone(t, k.liste_pc, parent)
    no_styles(t, w)
    sd = t.sd(w)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_PASTILLE_ALEX, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = hp.path_arg(sd["VisualFuncBinding"], chemin)
    sd["ItemParamName"] = "procon"
    sd["ItemUssClassName"] = "flex-no-shrink-class"   # (Alex : sinon les pastilles rétrécissent et se chevauchent)
    t.elem(w)["m_Classes"] = []
    if colonne:
        t.styles.style(t, w, {"flex-direction": "column", "flex-wrap": "nowrap", "flex-shrink": 0,
                              "width": PASTILLE_ALEX_PAS, "min-width": PASTILLE_ALEX_PAS,
                              "max-width": PASTILLE_ALEX_PAS, "align-self": "flex-start"})
        return []
    t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "overflow": "hidden",
                          "align-self": "stretch", "min-height": PASTILLE_ALEX_PAS,
                          "max-height": PASTILLE_ALEX_RANGS * PASTILLE_ALEX_PAS, "flex-shrink": 0})
    return []


def _phrases_liste(t, k, parent, chemin):
    """bloc v19 (Kinito, capture 52, Barry : « il manque des phrases dans le rapport : toutes celles où je dois
    défiler ») : les phrases étaient PC_MAX lignes fixes (8) ; les pastilles d'Alex, une liste de FM, montrent TOUS les
    points (Barry : 12 Pour, mesurés sur la capture : la barre de défilement et le pas de 30). Ici la même liste de FM
    (WrappedObjectList, celle des pastilles), l'une sous l'autre, chaque point par NOTRE modèle de ligne
    (GABARIT_PHRASE : PASTILLE_ALEX_PAS de haut, en face de sa pastille, la phrase avec « … », l'infobulle avec la
    phrase entière) : autant de phrases que de pastilles"""
    w = k.liste_src.clone(t, k.liste_pc, parent)
    no_styles(t, w)
    sd = t.sd(w)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_PHRASE, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = hp.path_arg(sd["VisualFuncBinding"], chemin)
    sd["ItemParamName"] = PARAM_PHRASE
    sd["ItemUssClassName"] = "flex-no-shrink-class"
    t.elem(w)["m_Classes"] = []
    t.styles.style(t, w, {"flex-direction": "column", "flex-wrap": "nowrap", "flex-grow": 1, "flex-shrink": 1,
                          "flex-basis": 0, "min-width": 0, "align-self": "flex-start"})
    return []


def _lignes_pc(t, k, parent, cle, liste, nombre, icone):
    """bloc v16 (Kinito, 08/11 : « on remet les phrases du procons », écrites à côté) : une ligne par Pour (ou Contre),
    PASTILLE_ALEX_PAS de haut (la hauteur d'une pastille d'Alex : en face de la sienne), sa PHRASE (« … » si elle est
    longue, entière dans l'infobulle de FM qui couvre la ligne) ; icone : l'icône de FM devant (sans la pastille
    d'Alex). Le n-ième par la fonction de FM « élément n », montré par le NOMBRE (jamais un SIVisible sur la
    variable : plantage du bloc v3) ; la phrase liée directement à la variable (comme les projets du bloc)"""
    b = k.s_vis.sd(k.vis)["Binding"]
    s = seul(t, k.src.s, k.p["setter"], parent)
    sd = t.sd(s)
    noms = [f"{V_PC}{cle}{i}" for i in range(PC_MAX)]
    sd["ValueVariables"], sd["ValueVariables_UxmlAttributeFlags"] = [], 1
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": n} for n in noms]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"] = [element_de_liste(k.fn_element, liste, i, n) for i, n in enumerate(noms)]
    sd["BindFunction_UxmlAttributeFlags"] = 1
    t.elem(s)["m_Classes"] = ["column-direction-normal"]
    t.styles.style(t, s, {"flex-shrink": 1, "flex-grow": 1, "min-width": 0, "align-self": "flex-start"})
    msgs = []
    for i, n in enumerate(noms):
        v = ni.new_visible(t, k.s_vis, k.vis, s, None, "", ni.make_binding(b, OP_SUP, [nombre], i))
        t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, v, {"flex-shrink": 0, "height": PASTILLE_ALEX_PAS, "min-height": PASTILLE_ALEX_PAS,
                              "max-height": PASTILLE_ALEX_PAS, "min-width": 0, "align-self": "stretch"})
        if icone:
            ic = k.pc_ligne.clone(t, k.pc_icone, v)
            t.sd(ic)["name"] = ""
            t.styles.style(t, ic, {"flex-shrink": 0, "margin-right": 6})
            lia, nb_ = _chemins_args(t.sd(ic)["Binding"], {"binding.ProConsID": f"{n}.ProConsID",
                                                            "binding.IsPro": f"{n}.IsPro"})
            t.sd(ic)["Binding"] = lia
            if nb_ != 2:
                msgs.append(f"icône Pour / Contre : {nb_} chemins remplacés au lieu de 2 (introuvable)")
        texte_direct(t, k, v, f"{n}.ProConsLongString", ["body-sm", "global-text-primary", "content-no-wrap",
                                                          "content-ellipsis"])
        _b, nbb = bulle(t, k, v, chemin=f"{n}.ProConsLongString")
        if nbb != 1:
            msgs.append(f"infobulle Pour / Contre : {nbb} textes au lieu de 1 (introuvable)")
    return msgs


def avis47(t, k, parent, taille="normal"):
    """la case du milieu de la bande : le polygone des attributs (v10 option « polygone », v11 pour de bon ; le rapport
    est en bas de la colonne de droite du bloc, _rapport_bloc)"""
    col = _colonne47(t, parent, POIDS_47["avis"], centre=True)
    _polygone_2x(t, k, col, STATS_H, RAYONS_BANDE[taille],
                 lambda dans: remapper(t, k.rm_model, dans, {"player": ("person", JOUEUR)}),
                 lambda dans: _cloner_fa(t, k, k.chart, dans))
    return []


def _cloner_fa(t, k, r, parent):
    """un morceau du grand bloc de FM d'origine (k.fa), avec ses styles et ses modèles inclus"""
    c = t.clone(r, parent, src=k.fa)
    t.styles.copy_from(k.fa.styles, t, c)
    copy_usings(t, k.fa, r)
    return c


def _rapport47(t, k, col, kb):
    """en haut, centrés : le titre du rapport sur deux lignes et sa note (« Rapport du préparateur » et la note du
    préparateur pour tes joueurs) ; dessous, Pour | Contre en icônes. (Niveau actuel et Potentiel : dans la carte
    depuis la v9). Dans col (la case de la bande, ou v15 option « polygone », le bas de la colonne de droite du bloc :
    il y faut localteam)"""
    msgs = []
    haut = boite(t, col, {"flex-shrink": 0, "margin-bottom": 8},
                 ["row-direction-normal", "align-items-center", "justify-content-center", "align-self-stretch"])
    s = k.txt.s
    racine = s.children(s.tt["m_VisualTree"]["rid"])
    if not racine:
        return [f"{SOURCE_ARGS[0]} : forme inattendue (introuvable)"]
    rm = remapper(t, k.rm_model, haut, {"team": ("localteam", EQUIPE)}, ["row-direction-normal"])
    c = k.txt.clone(t, racine[0], rm)
    sw = next((r for r in t.walk(c) if typ(t, r).endswith("BindableSwitchElement")
               and "UseCoachReportLayout" in json.dumps(t.sd(r).get("Binding") or {})), None)
    kids = t.children(sw) if sw is not None else []
    if len(kids) != 2:
        return [f"{SOURCE_ARGS[0]} : aiguillage du rapport introuvable"]
    eclaireur, etoiles = kids
    if sum(_remplacer_chemin(t.refs[r], NOTE_LONGUE, NOTE_COURTE) for r in t.closure(eclaireur)) != 1:
        msgs.append(f"libellé de la note du rapport ({NOTE_LONGUE}) pas trouvé une seule fois : à vérifier")
    # le titre du rapport : sans rapport, AU-DESSUS de « Observer joueur » (maquette 47) ; avec, sur deux lignes, sa
    # note juste à côté. v7 : le conteneur et le texte portent tous deux le nom « ScoutReport » (la v6 trouvait le
    # conteneur et ne faisait rien) : le texte est le SIText enfant du cadre « Frame »
    cadre = _par_nom_dans(t, eclaireur, "Frame")
    kids = t.children(cadre) if cadre is not None else []
    titre_r = next((r for r in kids if typ(t, r).endswith("SIText")), None)
    a_rapport = next((r for r in kids if typ(t, r).endswith("BindableSwitchElement")), None)
    if titre_r is None or a_rapport is None:
        msgs.append("titre du rapport de FM (Frame > SIText, HasReport) introuvable")
    else:
        t.elem(cadre)["m_Classes"] = ["column-direction-normal", "align-items-center"]
        dessus = visible_bool(t, k, cadre, "report.HasScoutedInfo", inverse=True)
        move(t, dessus, cadre, 0)
        move(t, titre_r, dessus)
        t.elem(titre_r)["m_Classes"] = ["body-xs-strong", "global-text-secondary", "content-no-wrap"]
        t.styles.style(t, titre_r, {"margin-bottom": 4, "flex-shrink": 0})
        # bloc v16 (Kinito, 08/11 : « le bouton Rapport de supervision a le même problème qu'avaient les polygones »)
        # : « Observer joueur » est un bouton d'action de FM (FMActionButton, PlayerQuickScoutClub), que FM refait à
        # chaque changement de joueur, vide un instant ; sa rangée (ou la note, s'il y a un rapport) a maintenant une
        # hauteur fixe, celle d'un bouton de FM : rien ne bouge autour de lui
        rang = boite(t, cadre, {"height": BOUTON_H, "min-height": BOUTON_H, "max-height": BOUTON_H, "flex-shrink": 0},
                     ["row-direction-normal", "align-items-center"])
        av = visible_direct(t, k, rang, "report.HasScoutedInfo")
        t2 = t.clone(titre_r, av)
        t.sd(t2)["name"] = ""
        t.elem(t2)["m_Classes"] = ["body-xs-strong", "global-text-secondary"]
        t.styles.style(t, t2, {"max-width": 78, "margin-right": 8, "flex-shrink": 0})
        move(t, a_rapport, rang)
        # bloc v17 (Kinito, 08/11 : « Observer joueur fait toujours le flash au changement de joueur ») : la hauteur
        # fixe de la v16 ne tenait pas sa LARGEUR : à sa taille de contenu, refait par FM à chaque joueur (son icône,
        # puis son texte), le bouton changeait de taille sous les yeux. Sa case a maintenant une largeur fixe (OBS_L)
        # et le bouton de FM la remplit (GrowToWidth) ; dessous, « Observer joueur » grisé (_bouton_gris), qui prend sa
        # place quand FM ne donne pas l'action
        uns = _par_nom_dans(t, a_rapport, "UnScouted")
        btns = [r for r in t.walk(uns) if typ(t, r) == "FM.UI.FMActionButton"] if uns is not None else []
        if len(btns) != 2:
            msgs.append(f"« Observer joueur » de FM (UnScouted : {len(btns)} boutons au lieu de 2) introuvable")
        else:
            t.elem(uns)["m_Classes"] = ["column-direction-normal"]
            t.styles.style(t, uns, {"width": OBS_L, "min-width": OBS_L, "max-width": OBS_L, "height": BOUTON_H,
                                    "min-height": BOUTON_H, "max-height": BOUTON_H, "overflow": "hidden",
                                    "flex-grow": 0, "flex-shrink": 0})
            for x in t.children(uns):   # l'aiguillage de FM team.IsClub (club | sélection)
                t.styles.style(t, x, {"align-self": "stretch", "flex-shrink": 0})
            # bloc v19 (vidéo du 08/11 : quand FM refait toute la fiche, son bouton arrive SANS sa loupe, et la loupe
            # une image plus tard : le texte se décale) : NOTRE gabarit de bouton (celui de la bande, sans icône), s'il
            # est dans le jeu ; sinon celui de FM
            for bt in btns:
                _regler_bouton_action(t, bt, gabarit=getattr(k, "gab_observer", ""))
            _bouton_gris(t, k, uns, "Observer joueur", "Scout Player")
    # autres joueurs : la note du rapport. v9 (capture 30) : leurs étoiles (niveau, potentiel) sont dans la carte
    ligne_e = boite(t, sw, {}, ["row-direction-normal", "align-items-center"])
    move(t, ligne_e, sw, 0)
    move(t, eclaireur, ligne_e)
    # tes joueurs : « Rapport du préparateur » et sa note (la note du rapport recopiée, sur le rapport du préparateur),
    # puis les étoiles de FM
    ligne_c = boite(t, sw, {}, ["row-direction-normal", "align-items-center"])
    move(t, ligne_c, sw, 1)
    tc = titre(t, k, ligne_c, *TITRE_PREPARATEUR)
    t.styles.style(t, tc, {"max-width": 78, "margin-right": 8, "flex-shrink": 0})
    t.elem(tc)["m_Classes"] = ["body-xs-strong", "global-text-secondary"]
    note = _par_nom_dans(t, eclaireur, "PlayerRecommendationCell-Unpacked")
    if note is None:
        msgs.append("note du rapport (PlayerRecommendationCell-Unpacked) introuvable")
    else:
        nc = t.clone(note, ligne_c)
        if sum(_remplacer_chemin(t.refs[r], "report.OverallReportGradeInfo", GRADE_COACH)
               for r in t.closure(nc)) != 1:
            msgs.append("note du préparateur : chemin de la note pas trouvé une seule fois (introuvable)")
    # v9 (capture 30) : les étoiles (niveau, potentiel) quittent la bande pour la carte (_etoiles_carte) ; v8 les y
    # calait sous leur titre (DECALE_ETOILES), la carte le fait
    t.remove(etoiles)
    # bloc v16 : Pour PUIS Contre (bloc v17 : côte à côte), chacun sous son titre de FM (pouce et mot, caché s'il est vide),
    # chaque point avec sa phrase (_listes_pc), dans une liste qui défile (la place qui reste sous le titre) ; sans
    # Pour NI Contre (pas de rapport) : notre message (maquette 47), posé par-dessus la liste vide, sans prendre la
    # souris. Par les NOMBRES : (Pour = 0 : (Contre = 0 : message))
    b = k.s_vis.sd(k.vis)["Binding"]
    bas = boite(t, col, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0}, ["column-direction-normal",
                                                                             "align-self-stretch"])
    rmr = seul(t, k.txt.s, k.rm_rapport, bas)
    t.elem(rmr)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    t.styles.style(t, rmr, {"flex-grow": 1, "min-height": 0})
    msgs += _listes_pc(t, k, kb, rmr)
    n_pour, n_contre = LISTES_PC[0][2], LISTES_PC[1][2]
    plein = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}
    sans_pour = visible(t, k, rmr, None, "", ni.equal_binding(b, n_pour, 0), plein)
    rien = visible(t, k, sans_pour, None, "", ni.equal_binding(b, n_contre, 0), plein)
    t.elem(rien)["m_Classes"] = ["column-direction-normal", "align-items-center"]
    for x in (sans_pour, rien):
        _sans_souris(t, x)
    _titre_et_texte(t, k, rien, *TEXTE_SANS_RAPPORT)
    return msgs


def _listes_pc(t, k, kb, parent):
    """bloc v16 : Pour, puis Contre (bloc v17 : côte à côte), dans un SIScrollView de FM (kb : sources du bloc) qui
    prend la place qui reste ;
    chacun : son titre de FM (pouce et mot), puis ses lignes [pastilles d'Alex en colonne | phrases] (la pastille et la
    ligne ont la même hauteur, PASTILLE_ALEX_PAS : chaque phrase en face de sa pastille), ou sans les pastilles d'Alex
    des lignes [icône de FM, phrase]. Une partie sans point est cachée (son NOMBRE)"""
    msgs = [] if k.pastille_alex and k.liste_pc else ["pastille d'Alex (ProConRow) pas dans le jeu : icônes de FM"]
    b = k.s_vis.sd(k.vis)["Binding"]
    # bloc v17 (Kinito, 08/11, capture 41 : « séparer en 2 : Pour à gauche, Contre à droite ») : deux moitiés égales
    # (base nulle) côte à côte ; une liste vide laisse sa moitié vide (l'autre ne bouge pas)
    contenu = boite(t, parent, {"flex-shrink": 0}, ["row-direction-normal", "align-items-start", "align-self-stretch"])
    for j, ((cle, liste, nombre), tete) in enumerate(zip(LISTES_PC, k.pc_tetes)):
        moitie = boite(t, contenu, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                                    "margin-left": ECART_PC if j else 0}, ["column-direction-normal"])
        partie = visible(t, k, moitie, None, "", ni.make_binding(b, OP_SUP, [nombre], 0), {"flex-shrink": 0})
        t.elem(partie)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
        h = k.pc.clone(t, tete, partie)
        t.sd(h)["name"] = ""
        t.elem(h)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"]
        for x in t.walk(h):
            if typ(t, x).endswith("SIText"):
                t.elem(x)["m_Classes"] = ["body-sm-strong"] + [c for c in t.elem(x).get("m_Classes") or []
                                                               if c.endswith("string-colour")]
        corps = boite(t, partie, {"flex-shrink": 0}, ["row-direction-normal", "align-items-start",
                                                       "align-self-stretch"])
        if k.pastille_alex and k.liste_pc:
            msgs += _pastilles_alex(t, k, corps, liste, colonne=True)
            boite(t, corps, {"width": 6, "min-width": 6, "flex-shrink": 0}, [])
            # bloc v19 : les phrases dans une liste de FM, autant que de pastilles (_phrases_liste)
            msgs += _phrases_liste(t, k, corps, liste)
        else:
            msgs += _lignes_pc(t, k, corps, cle, liste, nombre, icone=True)
    _dans_defilement(t, kb, parent, t.children(parent).index(contenu), [contenu])
    return msgs


def _titre_et_texte(t, k, parent, titre_fr_en, texte_fr_en):
    """un titre en gras et un texte, centrés, à la ligne s'il le faut (textes à nous)"""
    for i, (fr, en) in enumerate((titre_fr_en, texte_fr_en)):
        x = titre(t, k, parent, fr, en)
        t.elem(x)["m_Classes"] = (["body-sm-strong", "global-text-primary"] if i == 0 else
                                  ["body-sm", "global-text-secondary"]) + ["content-center-align", "content-wrap"]
        t.styles.style(t, x, {"align-self": "stretch", "flex-shrink": 0, "margin-top": 6 if i == 0 else 3})

# v11 (Kinito, 08/11, capture 37 : « les 4 doivent avoir la même taille TOUT le temps, la taille actuelle du rôle ALB
# sur le screen de Geubbels ») : mesuré sur la capture 37, le menu « Rôle ALB » va de x 1490 à 1673 (184 px d'écran,
# 1,1407 px par px de FM) : 161 de FM ; écart entre deux menus : 6 (capture : 8 px)
MENU_L = 161


def _entrainement47(t, k, parent):
    """tes joueurs : titre « Entraînement », la note, Féliciter / Critiquer ; dessous les 4 menus de FM (rôle avec /
    sans le ballon, domaine additionnel, intensité : le bloc de FM des options d'entraînement, sans son terrain).
    v11 : la note et les pouces juste après le mot (« Entraînement 8,89 pouce pouce », choix de Kinito) ; les 4 menus
    de MENU_L chacun, quel que soit leur texte (« … » s'il est coupé)"""
    msgs = []
    tete = boite(t, parent, {"flex-shrink": 0, "margin-bottom": 6},
                 ["row-direction-normal", "align-items-center", "align-self-stretch"])
    ti = k.traits.clone(t, k.titre_traits, tete)
    t.sd(ti)["name"] = ""
    for x in t.walk(ti):
        if x != ti and t.name(x) == "TraitsIcon":
            t.elem(x)["m_Classes"] = [c if c != "game-concepts-game-concepts-traits" else
                                      "game-concepts-training-general_small" for c in t.elem(x)["m_Classes"]]
        if typ(t, x).endswith("SIText"):
            sd = t.sd(x)
            sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
            sd["TextBinding"]["m_kind"] = 0
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            sd["text"], sd["text_UxmlAttributeFlags"] = L("Entraînement", "Training"), 1
            sd["DebugDisplay"] = sd["text"]
        if x != ti:
            t.sd(x)["name"] = ""
    rm = k.note.clone(t, k.note_rm, tete)
    t.styles.style(t, rm, {"flex-shrink": 0, "margin-left": 8, "margin-right": 6})
    pr = remapper(t, k.rm_model, tete, {"player": ("person", JOUEUR)}, ["row-direction-normal", "align-items-center"])
    t.styles.style(t, pr, {"flex-shrink": 0})
    for i, (nom, (_cle, _modele, guid)) in enumerate(POUCES.items()):
        bt = k.boutons.clone(t, k.pouces[nom], pr)
        t.elem(bt)["m_Classes"] = ["margin-left-global-gap-small"] if i else []
        if k.gabarits:   # le pouce vert / rouge de l'ajout Kinito 26.14 s'il est dans le jeu (comme le bloc v2)
            t.sd(bt)["ActionsListWidget"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
            t.sd(bt)["ActionsListWidget_UxmlAttributeFlags"] = 1
    # les 4 menus de FM (version écran, sans le terrain), deux par ligne
    o = k.opts.s
    racine = o.children(o.tt["m_VisualTree"]["rid"])[0]
    # le bloc de FM attend person, team et positionmask ; l'en-tête n'a que person : team = l'équipe du joueur (comme
    # la fiche Small d'Alex), positionmask (lu seulement par le petit terrain de FM, retiré) = sa meilleure position
    rmo = remapper(t, k.rm_model, parent, {"team": ("person.Team", EQUIPE),
                                           "positionmask": ("person.BestPositionMask", 0)},
                   ["column-direction-normal", "align-self-stretch"])
    c = k.opts.clone(t, racine, rmo)
    t.sd(c)["name"] = ""
    t.elem(c)["m_Classes"] = ["align-self-stretch"]
    sw = _par_nom_dans(t, c, "PhoneSwitch")
    menus = sw is not None and next((x for x in t.walk(t.children(sw)[0]) if t.name(x) == "Dropdowns"), None)
    if not menus:
        t.remove(c)
        return ["menus d'entraînement de FM (Dropdowns) introuvables"]
    cadre = t.parent[sw]
    move(t, menus, cadre)
    t.remove(sw)
    no_styles(t, cadre)
    t.elem(cadre)["m_Classes"] = ["align-self-stretch"]
    no_styles(t, menus)
    t.elem(menus)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    # 1re ligne : « positions » (rôle avec / sans le ballon) côte à côte ; 2e : domaine additionnel et intensité
    enfants = list(t.children(menus))
    if len(enfants) != 3:
        return msgs + [f"menus d'entraînement de FM : {len(enfants)} parties au lieu de 3 (introuvable)"]
    positions, focus, intensite = enfants
    ligne2 = boite(t, menus, {"flex-shrink": 0, "margin-top": 4}, ["row-direction-normal", "align-self-stretch"])
    move(t, focus, ligne2)
    move(t, intensite, ligne2)
    no_styles(t, positions)
    t.elem(positions)["m_Classes"] = ["row-direction-normal", "align-self-stretch"]
    for x in list(t.children(positions)) + [focus, intensite]:
        no_styles(t, x)
        # v11 : MENU_L de large, fixe ; le menu (le modèle inclus de FM, et le ContextShortcutsElement qui entoure le
        # 1er) étiré sur toute cette largeur : ils prenaient la largeur de leur texte (capture 37 : 161 / 64 / 69 / 161)
        t.elem(x)["m_Classes"] = ["column-direction-normal"]
        t.styles.style(t, x, {"width": MENU_L, "min-width": MENU_L, "max-width": MENU_L, "flex-grow": 0,
                              "flex-shrink": 0, "align-items": "stretch", "margin-right": 6})
        for m in t.walk(x):
            if m != x and m in t.refs and not typ(t, m).endswith("SIText"):
                t.styles.style(t, m, {"max-width": {"unit": 2, "value": 100.0}, "min-width": 0,
                                      "align-self": "stretch", "flex-shrink": 0})
            elif m != x and "tifo-ph" in (t.elem(m).get("m_Classes") or []):
                # v8 (capture 29) : l'intitulé sur UNE ligne, « … » s'il est coupé ; « Priorité de l'entraînement
                # individuel » passait sur deux lignes et descendait son menu sous celui de l'intensité. tifo-ph
                # (= body-sm, gris) vient APRÈS content-ellipsis dans les feuilles de FM et le remettait à la ligne :
                # remplacé par les classes de nos titres (body-sm vient avant)
                t.elem(m)["m_Classes"] = list(CL_LAB)
                t.styles.style(t, m, {"max-width": {"unit": 2, "value": 100.0}, "min-width": 0, "flex-shrink": 1})
    return msgs


def _stats47(t, k, parent, taille="normal"):
    """les autres joueurs : le polygone de stats de FM (player.AnalysisVisualisations.DefaultObservation, sa tuile
    « Données de la prestation ») : compétition et période, l'appréciation réduite à sa pastille (la phrase au
    survol), le polygone ; pas assez de données : le texte de FM"""
    msgs = []
    rmj = remapper(t, k.rm_model, parent, {"player": ("person", JOUEUR)},
                   ["column-direction-normal", "align-self-stretch"])
    rmp = seul(t, k.perf.s, k.perf_rm, rmj)
    t.elem(rmp)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    ok = seul(t, k.perf.s, k.perf_ok, rmp)
    t.elem(ok)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    # v10 (capture 33 : « le polygone des stats en haut n'est pas beau ») : il faisait ~18 de rayon sous la ligne de la
    # compétition, ses étiquettes de FM en 14 px coupées (« Passes … », « PdA-Dlj… »). Il prend maintenant TOUTE la case
    # (STATS_H), en étiquettes 10 px (le modèle de FM du polygone des attributs : mêmes liaisons, valeur et nom de la
    # stat), au rayon RAYONS_STATS de la taille du texte, sans flash (graphique deux fois plus grand dans la cale, _polygone_2x) ; la
    # compétition (sur deux lignes au plus, à gauche) et le pouce (à droite) sont posés PAR-DESSUS, dans les coins du
    # haut, où le polygone ne va pas
    zone = _cale_2x(t, ok, STATS_H)
    poly = k.perf.clone(t, k.perf_switch, zone)   # aiguillage de FM : texte de FM sans données | polygone
    t.sd(poly)["name"] = ""
    t.elem(poly)["m_Classes"] = ["justify-content-center", "align-items-center"]
    t.styles.style(t, poly, _taille_2x(STATS_H))
    graphes = [x for x in t.walk(poly) if typ(t, x).endswith("FMSpiderChart")]
    if len(graphes) != 1:
        msgs.append(f"polygone de stats : {len(graphes)} graphiques au lieu d'un (introuvable)")
    for x in graphes:
        _regler_polygone_2x(t, x, STATS_H, RAYONS_STATS[taille])
    tete = boite(t, ok, {"position": "absolute", "left": 0, "top": 0, "right": 0, "flex-shrink": 0},
                 ["row-direction-normal", "align-items-start"])
    _sans_souris(t, tete)
    ti = k.perf.clone(t, k.perf_titre, tete)
    t.sd(ti)["name"] = ""
    t.elem(ti)["m_Classes"] = ["body-sm-strong", "global-text-primary", "content-wrap"]
    t.styles.style(t, ti, {"flex-shrink": 1, "min-width": 0, "max-width": TITRE_STATS_L})
    boite(t, tete, {"flex-grow": 1}, [])
    rv = seul(t, k.perf.s, k.perf_rm_valeur, tete)   # performanceValue -> polygonobservation.PerformanceReasonValue
    pv = k.pfd.clone(t, k.pfd_vis, rv)
    lab = _par_nom_dans(t, pv, "Label")
    pouce = _par_nom_dans(t, pv, "ThumbsUp")
    if lab is None or pouce is None:
        msgs.append("appréciation de FM (ThumbsUp / Label) introuvable")
    else:
        liaison = copy.deepcopy(t.sd(lab).get("TextBinding"))
        conteneur = t.parent[pouce]
        t.remove(lab)
        _b, nb_ = bulle(t, k, conteneur, liaison)
        if nb_ != 1:
            msgs.append(f"infobulle de l'appréciation : {nb_} textes au lieu de 1 (introuvable)")
    ko = k.perf.clone(t, k.perf_ko, rmp)
    t.sd(ko)["name"] = ""
    for x in list(t.children(ko)):   # le trait de la tuile de FM sous le texte : pas dans la bande
        if (t.elem(x).get("m_TemplateAlias") or "").startswith("layout-divider"):
            t.remove(x)
    # v7 (maquette 47) : pas assez de données : « Données de la prestation », puis le texte de FM, centrés
    no_styles(t, ko)
    t.elem(ko)["m_Classes"] = ["column-direction-normal", "align-items-center", "align-self-stretch"]
    t.styles.style(t, ko, {"flex-grow": 1, "justify-content": "center"})
    for r in (rmj, rmp):
        t.styles.style(t, r, {"flex-grow": 1})
    texte_fm = next((x for x in t.children(ko) if typ(t, x).endswith("SIText")), None)
    if texte_fm is None:
        msgs.append("prestation : texte de FM « pas assez d'analyses » introuvable")
    else:
        no_styles(t, texte_fm)
        t.elem(texte_fm)["m_Classes"] = ["body-sm", "global-text-secondary", "content-center-align", "content-wrap"]
        t.styles.style(t, texte_fm, {"align-self": "stretch", "flex-shrink": 0, "margin-top": 3})
        tp = titre(t, k, ko, *TITRE_PRESTATION)
        move(t, tp, ko, 0)
        t.elem(tp)["m_Classes"] = ["body-sm-strong", "global-text-primary", "content-center-align", "content-wrap"]
        t.styles.style(t, tp, {"align-self": "stretch", "flex-shrink": 0})
    return msgs


def bout47(t, k, parent, taille="normal"):
    """le bout de la bande : sans contrat (libre) un texte à nous ; tes joueurs l'entraînement ; les autres le polygone
    de stats (ou le texte de FM s'il n'y a pas assez de données)"""
    col = _colonne47(t, parent, POIDS_47["bout"])
    t.styles.style(t, col, {"justify-content": "flex-start"} if False else {})
    sw = seul(t, k.src.s, k.p["contrat"], col)   # person.fullcontract.IsValid : [faux | vrai]
    t.elem(sw)["m_Classes"] = ["align-self-stretch"]
    t.styles.style(t, sw, {"flex-grow": 1})
    lib = boite(t, sw, {"flex-grow": 1, "justify-content": "center"},   # v7 : titre et texte, centrés
                ["column-direction-normal", "align-items-center", "align-self-stretch"])
    _titre_et_texte(t, k, lib, TITRE_PRESTATION, TEXTE_LIBRE)
    avec = boite(t, sw, {"flex-grow": 1}, ["column-direction-normal", "align-self-stretch"])
    a_nous = visible_bool(t, k, avec, CLUB_HUMAIN)
    t.elem(a_nous)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    msgs = _entrainement47(t, k, a_nous)
    autres = visible_bool(t, k, avec, CLUB_HUMAIN, inverse=True)
    t.elem(autres)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    msgs += _stats47(t, k, autres, taille)
    return msgs


def construire_47(t, parent, k, taille="normal"):
    """la bande : chiffres | avis | bout. v9 (capture 30 : « solidifier le bandeau en haut complètement ») : sur TOUTE la
    largeur, la carte du joueur (photo comprise) est entière dans le bloc, dessous. taille : la taille du texte de
    cette bande (TAILLES_TEXTE), pour le rayon des polygones (v10)"""
    msgs = []
    v, h = PADDING_V, MARGE_COTES_INT
    carte = boite(t, parent, {
        "flex-direction": "row", "align-items": "stretch", "height": HAUT_BANDE, "min-height": HAUT_BANDE,
        "max-height": HAUT_BANDE,
        "flex-shrink": 0, "flex-grow": 1, "overflow": "hidden", "background-color": FOND,
        **{f"border-{c}-width": 1 for c in ("top", "bottom", "left", "right")},
        **{f"border-{c}-color": BORD for c in ("top", "bottom", "left", "right")},
        **{f"border-{c}-radius": RAYON for c in ("top-left", "top-right", "bottom-left", "bottom-right")},
        "padding-top": v, "padding-bottom": v, "padding-left": h, "padding-right": h,
        "margin-top": MARGE_HAUT, "margin-bottom": 0, "margin-left": MARGE_COTES,
        "margin-right": MARGE_COTES}, ["align-self-stretch"])
    msgs += chiffres47(t, k, carte)
    _sep47(t, carte)
    msgs += avis47(t, k, carte, taille)
    _sep47(t, carte)
    msgs += bout47(t, k, carte, taille)
    return msgs


# ---------- pose / retrait dans l'en-tête de FM ----------
def place_1080p(t):
    """l'aiguillage UseStandard de FM (1080p = son enfant 0), s'il a sa forme (2 enfants), sinon None"""
    sw = aiguillage(t, "UseStandard")
    return sw if sw is not None and len(t.children(sw)) == 2 else None


def photo_ok(t):
    """la photo de FM est cachée par UNE seule chose : la cachette de la tuile d'Alex, ou notre SIVisible"""
    ph = first(t, lambda r: t.name(r) == PHOTO)
    if ph is None:
        return False
    anc = ancetres(t, ph)
    return (CACHE_ALEX in anc) != (NOM_PHOTO in anc)


def anciens(t):
    """v1-v4 : nos morceaux sous la racine de la tuile d'Alex"""
    return [k for r in t.walk() if (t.name(r) or "").startswith(ANCIENNE_RACINE)
            for k in t.children(r) if (t.name(k) or "").startswith(PREFIXE)]


def a_jour(t):
    sw = place_1080p(t)
    if sw is None or anciens(t):
        return False
    pl = t.children(sw)[0]
    return t.name(pl) == NOM_PLACE and any(t.name(x) == NOM_LARGE for x in t.children(pl)) and photo_ok(t)


def _regles_par_ref(t):
    return {r["rid"]: (r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}


def _deballer(t, r, garde):
    """r remplacé par les enfants de son enfant nommé garde (remis à la place de r, dans l'ordre), puis enlevé"""
    par = t.parent[r]
    i = t.children(par).index(r)
    g = next((x for x in t.children(r) if t.name(x) == garde), None)
    for j, x in enumerate(list(t.children(g)) if g is not None else []):
        move(t, x, par, i + j)
    t.remove(r)


def retirer_tout(t):
    """nos morceaux enlevés (v1-v4 dans la tuile d'Alex, v5 dans l'en-tête), ce qu'ils gardaient remis à sa place ;
    numéros de règle de TOUTES les références enlevées (éléments, et aussi composants : BindingRemapperComponent…
    que t.walk ne parcourt pas ; v1 du 06/11 : 36 règles restaient après un retrait)"""
    avant = _regles_par_ref(t)
    notes = _usings_notes(t)
    for r in [r for r in t.walk() if (t.name(r) or "").startswith(ANCIENNE_RACINE)]:
        for k in [k for k in t.children(r) if (t.name(k) or "").startswith(PREFIXE)]:
            if t.name(k) == NOM_AUTRES:
                _deballer_dans(t, k)
            else:
                t.remove(k)
    for nom, garde in ((NOM_PLACE, NOM_AUTRES), (NOM_PHOTO, NOM_PHOTO_FM)):
        for r in [r for r in t.walk() if t.name(r) == nom]:
            if r in t.refs:
                _deballer(t, r, garde)
    _usings_orphelins(t, (notes | USINGS_ANCIENS) - _alias_utilises(t))
    reste = {r["rid"] for r in t.tt["references"]["RefIds"] if r}
    return {ri for rid, ri in avant.items() if rid not in reste}


def _alias_utilises(t):
    return {t.elem(r).get("m_TemplateAlias") for r in t.walk()} - {None, ""}


# v6 : les modèles inclus que la pose ajoute à l'en-tête sont NOTÉS en classes sur notre racine (NOM_LARGE) : le
# retrait n'enlève que ceux-là (s'ils ne servent plus), jamais un modèle qu'Alex ou FM déclarait déjà, même inutilisé.
# Les bandes v3-v5 ne notaient rien : leurs 3 orphelins connus (USINGS_ANCIENS, absents de l'en-tête d'Alex seul et de
# celui de FM) sont enlevés aussi quand plus rien ne s'en sert.
MARQUE_USING = "kinito-modele-inclus--"
USINGS_ANCIENS = {"ScoutedCurrentAbilityStarRangeCell", "ScoutedPotentialAbilityStarRangeCell",
                  "scaling-icons-grades-medium-filled"}


def _usings_notes(t):
    return {c[len(MARQUE_USING):] for r in t.walk() for c in t.elem(r).get("m_Classes") or []
            if c.startswith(MARQUE_USING)}


def _usings_orphelins(t, disparus):
    """v6 : les modèles inclus notés par la pose (et les orphelins des anciennes bandes) que plus rien n'utilise,
    enlevés de la liste, sauf ceux que l'en-tête de FM d'origine déclare : le retrait rend l'en-tête à l'identique"""
    if not disparus:
        return
    o = hp.ouvrir(MODELE, depart_original=True)
    origine = {u.get("alias") for u in (o[3].tt.get("m_Usings") or [])} if o is not None else None
    if origine is None:   # l'origine illisible : on ne touche à rien
        return
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") not in disparus
                        or u.get("alias") in origine]


def _deballer_dans(t, k):
    """v1-v4 : le SIVisible « Autres » remplacé par ses enfants (la carte d'Alex), puis enlevé"""
    par = t.parent[k]
    i = t.children(par).index(k)
    for j, x in enumerate(list(t.children(k))):
        move(t, x, par, i + j)
    t.remove(k)


def poser(t, k, sw):
    """à l'enfant 0 de UseStandard : [ce qui y était, en Moyen / Petit | notre bande en Large, par taille du texte]"""
    b = k.s_vis.sd(k.vis)["Binding"]
    declares = {u.get("alias") for u in t.tt.get("m_Usings") or []}
    ancien = t.children(sw)[0]
    place = boite(t, sw, {}, ["align-self-stretch"], NOM_PLACE)
    move(t, place, sw, 0)
    autres = visible(t, k, place, 0, NOM_AUTRES, ni.make_binding(b, OP_SUP, [MODE], 0))
    move(t, ancien, autres)
    large = visible(t, k, place, 1, NOM_LARGE, ni.equal_binding(b, MODE, 0))
    # le BindingSetter de la bannière (variables hasContract / teamtodisplay lues par le bloc du club), vidé
    racine = t.clone(k.p["setter"], large, src=k.src.s)
    for x in list(t.children(racine)):
        t.remove(x)
    t.sd(racine)["name"] = ""
    t.elem(racine)["m_Classes"], t.elem(racine)["m_RuleIndex"] = ["align-self-stretch"], -1
    msgs = []
    for _nom, bas, haut, parts, rayon_px in TAILLES_TEXTE:
        dans = racine
        if bas is not None:   # « >= bas » = « > bas − 1 »
            dans = visible(t, k, dans, None, "", ni.make_binding(b, OP_SUP, [TAILLE_TEXTE], bas - 1))
        if haut is not None:
            dans = visible(t, k, dans, None, "", ni.make_binding(b, OP_INF, [TAILLE_TEXTE], haut))
        msgs += construire_47(t, dans, k, _nom)   # v6 : la maquette 47 (avant : construire_large)
    # v6 : un modèle inclus que la pose a déclaré sans s'en servir (le trait de la tuile de prestation de FM, retiré)
    # n'est pas gardé : le retrait ne saurait pas qu'il vient de nous
    servis = _alias_utilises(t)
    t.tt["m_Usings"] = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") in declares or u.get("alias") in servis]
    # (v8, essayé puis défait : noter AUSSI les modèles déjà déclarés dont notre bande se sert fait enlever, au
    # retrait, des modèles qu'Alex laisse déclarés sans s'en servir — sa fonction n'en retire jamais ; mesuré :
    # situation 3 de scenarios_bande6.py. Seuls ceux que la pose AJOUTE sont à nous)
    ajoutes = [u.get("alias") for u in t.tt["m_Usings"] if u.get("alias") not in declares]
    t.elem(large)["m_Classes"] = list(t.elem(large).get("m_Classes") or []) + [MARQUE_USING + a for a in ajoutes]
    return msgs


def poser_photo(t, k):
    """la photo de FM cachée en 1080p Large seulement, quand rien d'autre ne la cache (la tuile d'Alex la cache
    partout) : [SIVisible mode > 0 : la photo | SIVisible mode == 0 : UseSmall'[UseStandard'[rien, doublure],
    doublure]] (copies des aiguillages de FM : 1080p = enfants 0)"""
    ph = first(t, lambda r: t.name(r) == PHOTO)
    if ph is None:
        return [f"photo de FM ({PHOTO}) introuvable"]
    if CACHE_ALEX in ancetres(t, ph):
        return []
    par = t.parent[ph]
    i = t.children(par).index(ph)
    b = k.s_vis.sd(k.vis)["Binding"]
    w = boite(t, par, {"flex-shrink": 0}, ["column-direction-normal", "align-self-end"], NOM_PHOTO)
    move(t, w, par, i)
    fm = visible(t, k, w, 0, NOM_PHOTO_FM, ni.make_binding(b, OP_SUP, [MODE], 0))
    move(t, ph, fm)
    lg = visible(t, k, w, 1, "", ni.equal_binding(b, MODE, 0))

    def aig(modele, dans):
        a = t.clone_shallow(modele, dans)
        t.sd(a)["name"] = ""
        t.elem(a)["m_Classes"], t.elem(a)["m_RuleIndex"] = [], -1
        return a
    petit = aig(k.sw_petit, lg)
    std = aig(k.sw_std, petit)
    boite(t, std, {"width": 0, "height": 0, "flex-shrink": 0})   # 1080p : rien
    for dans in (std, petit):
        c = t.clone(ph, dans)
        t.sd(c)["name"] = ""
    return []


def retirer_regles(t, enlever):
    """les règles de la feuille (numéros dans enlever) que plus rien n'utilise, et les valeurs qu'elles avaient ajoutées
    en fin de table (recette de 26.14 / 26.15 / 26.17 / 26.19)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for rg in t.styles.sh["m_Rules"]:
        for cs in rg.get("m_ComplexSelectors") or []:
            cs["ruleIndex"] = nouvel.get(cs.get("ruleIndex"), cs.get("ruleIndex"))
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for rg in t.styles.sh["m_Rules"]:
        for pr in rg["m_Properties"]:
            for v in pr["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    t.styles.changed = True


def ouvrir_entete():
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        return None
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    return bundle, obj, tt, t


def enregistrer(bundle, obj, tt, t, modele=MODELE):
    t.finish()
    t.styles.save()
    for n in types_ref_manquants(obj, tt):
        print(f"{modele} : type {n} déclaré dans le bundle (recopié)")
    obj.save_typetree(tt)
    # bloc v19 : relu tel quel par la suite du MÊME passage (comme les jobs d'Alex, elements.py) ; sans cela, la tuile
    # ne voyait pas le gabarit des boutons que la bande venait de poser (read_typetree rend l'ancien) et ne le prenait
    # qu'au passage suivant (vu au banc : le 2e passage refaisait le bloc)
    nb._ecrits[(bundle, obj.path_id)] = tt
    nb._dirty.add(bundle)


def _marquer():
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


# ---------- étape 2 : le grand bloc de la fiche (PlayerAttributesLargeBlock), à nous en 1080p Large ----------
# Le bloc n'existe que dans la composition « Large » de la Vue d'ensemble (PlayerReportOverviewComposition-Large et
# -Large-FMC, point de rupture 3 = celui de la bannière « max » de l'en-tête, mesuré le 06/11/2026) : dans le bloc,
# seul l'affichage reste à tester (settings.AdaptiveScalingLevelIndex == 0, déjà lu dans ce bloc par les ajouts d'Alex
# vus en jeu, comme settings.TextScaling).
# NOTRE BLOC est rangé dans un modèle de FM cité par RIEN (PlayerAttributesTile : guid_partout.py, tous les bundles,
# scènes comprises ; ni dans le code du jeu, ni dans un script du skin), refait à chaque passage depuis son ORIGINAL :
# aucun script d'Alex ne le voit, ses fonctions qui cherchent dans le grand bloc (par nom, modèle inclus ou type) ne
# trouvent que les siens. Dans le grand bloc, on ne pose que deux SIVisible (sans style intégré : ses fonctions qui
# recopient « le 1er SIVisible » ou « le 1er VisualElement » du modèle n'en héritent rien) autour de l'élément de FM qui
# porte tout le bloc (ExpandableContentElement) : [« mode > 0 » : lui, tel qu'Alex l'a fait | « mode == 0 » : notre
# modèle, inclus].
VERSION_BLOC = 21    # v21 (Kinito, capture 55 : un joueur de Toluca montré au club de Kinito, Rodez) : le club de la
#                      carte (et ses pastilles d'état) pris sur person.Team, le club où il joue (carte_bas47) ;
#                      v20 (Kinito, captures 53-54, texte Normal et Petit : « réduire la colonne du terrain, donner ce
#                      que tu réduis à la colonne de droite ») : la colonne des postes à LISTE_ROLES (340) au lieu de
#                      380 ; la colonne de droite (Personnalité, Taille, Pour / Contre) prend les 40 de plus ;
#                      v19 (v18 vue en jeu, capture 52 et une vidéo) : les phrases des Pour / Contre dans une liste de
#                      FM, autant que de pastilles (elles s'arrêtaient à 8 : Barry en a 12), par notre modèle de ligne
#                      (GABARIT_PHRASE) ; « Observer joueur » avec notre gabarit de bouton (sans la loupe, qui arrivait
#                      une image après le texte) ;
#                      v18 (v17 vue en jeu, captures 46-51) : « Observer joueur » grisé avec son infobulle sur lui
#                      seul (comme les boutons de la bande v13) ;
#                      v17 (v16 vue en jeu, captures 41-45) : Pour à GAUCHE, Contre à DROITE (deux moitiés) ;
#                      « Niveau actuel » et « Potentiel » centrés au-dessus de leurs étoiles ; « Observer joueur »
#                      dans une case de largeur ET de hauteur fixes (il ne change plus de taille au changement de
#                      joueur), grisé à sa place quand FM ne le donne pas (_bouton_gris) ;
#                      v16 (v15 vue en jeu, captures 34-40) : le rapport en bas de la colonne de droite POUR DE BON
#                      (plus d'option), ses Pour / Contre l'un sous l'autre, chaque point avec sa PHRASE à côté
#                      de sa pastille (« … » si elle est longue, entière au survol ; la liste défile) ; le bouton
#                      « Observer joueur » dans une case de hauteur fixe (il ne fait plus sauter le reste) ;
#                      v15 (v14 vue en jeu, captures 32-33) : la carte d'un joueur PRÊTÉ n'est plus vide (le bloc club
#                      prend la largeur de la carte, voir _bloc_clubs47) ; le polygone sans « flash » au changement de
#                      joueur (technique d'Alex, _polygone_2x, RAYONS_BLOC) ; option « polygone » : le rapport à sa place ;
#                      v1 : vu en jeu le 07/11 (capture 8, Plus grand) ; v2 : 3 colonnes de notes égales réglées sur le
#                      français et l'anglais, la place gagnée à la colonne du terrain (boutons Avec / Sans le ballon
#                      entiers), Pour / Contre à sa largeur de la v1 ; v3 : la maquette 47 (voir l'en-tête) — FAISAIT
#                      PLANTER LE JEU à l'ouverture d'une fiche (SIVisible lié à la variable d'un projet) ; v4 : la v3
#                      corrigée (chaque projet montré par le nombre de projets, voir _projets), vue en jeu sans
#                      plantage (captures 17-19 : infobulle et défilement des projets marchent) ; v5 : la personnalité
#                      ne prend plus que sa hauteur (les projets remontent), titres des projets plus petits, 1er
#                      projet collé à son titre ; v6 (v5 vue en jeu, captures 20-21) : chaque partie des projets est
#                      un seul cadre (titre puis projets) ; Personnalité / Rapports médias et Court / Long terme avec
#                      les marges de Taille / Réputation (CADRES_INFOS) ; v7 (v6 vue en jeu, capture 22) : la marge
#                      écrite par FM sous les titres des projets (12 / 8 px) retirée ; v8 (v7 vue en jeu, captures
#                      23-25) : la liste des rôles prend la place qui reste et défile (elle poussait le bloc), la
#                      carte remplit la case du bloc (son haut ne bouge plus d'un joueur à l'autre) ; v9 : le
#                      polygone prend la largeur de sa colonne (FM règle sa taille), rayon demandé 83 / 79 / 76 / 74 ;
#                      v10 (v9 vue en jeu, captures 26-27) : colonnes de notes du gardien à la largeur du joueur ;
#                      v11 (bande v6 de la maquette 47) : le bloc laisse à gauche la place de la carte du joueur
#                      (CARTE_L + ECART), ses conteneurs pleine largeur ne prennent pas la souris (la carte dessous) ;
#                      v12 (bande v7) : le BAS de la carte du joueur (nom -> club) est dans le bloc, à gauche, et
#                      remonte de JOINTURE au-dessus du bloc pour rejoindre le bord de l'en-tête ; v13 (v12 vue en
#                      jeu, capture 29 : le jeu coupe la zone du bloc 10 px sous l'en-tête) : ce bas est une carte
#                      fermée qui commence à cette ligne de coupe ; v14 (bande v9, captures 30-31) : la carte
#                      ENTIÈRE (photo, nom centré, description en or, niveau et potentiel, Actions centré, prêt côte
#                      à côte avec l'icône « prêts », numéro de son équipe actuelle) et le cadre du bloc remontent
#                      tous deux jusqu'à la ligne de coupe
BLOC = "PlayerAttributesLargeBlock"
TUILE = "PlayerAttributesTile"
GUID_TUILE = "13118d2063ae6a449aac5938bb7d92de"
PREFIXE_BLOC = "UIPickerKinitoFicheLarge"
NOM_BLOC_AUTRES = f"{PREFIXE_BLOC}Autres"
NOM_BLOC_LARGE = f"{PREFIXE_BLOC}-v{VERSION_BLOC}{SUFFIXE}"
NOM_TUILE = f"{PREFIXE_BLOC}Tuile-v{VERSION_BLOC}{SUFFIXE}"
# bloc v19 : notre modèle de LIGNE des phrases Pour / Contre (_phrases_liste), réécrit dans un modèle de FM cité par
# RIEN, comme le gabarit des boutons (même bundle) : modeles_libres.py, puis guid_partout.py sur TOUS les bundles,
# scènes comprises, le 08/11 (seul l'index de son propre bundle le cite) ; aucun script du skin ni de l'app d'Alex.
# Refait à chaque passage depuis son ORIGINAL, remis d'origine au retrait. Une ligne : la ligne et le texte de FM (ceux
# du gabarit des boutons d'action), PASTILLE_ALEX_PAS de haut, la phrase « … », et l'infobulle de FM (Tooltip à plat,
# pas de modèle inclus : StandardTextTooltip est dans un autre bundle) avec la phrase entière. PARAM_PHRASE : le nom
# que la liste donne à chaque point (celui des pastilles d'Alex)
GABARIT_PHRASE = "CodeOfConductCard"
GUID_PHRASE = "5a25843f47f14b4498ad9b55ac7e475c"
NOM_PHRASE = f"{PREFIXE_BLOC}Phrase-v{VERSION_BLOC}{SUFFIXE}"
PARAM_PHRASE = "procon"
CHEMIN_PHRASE = f"{PARAM_PHRASE}.ProConsLongString"
RAPPORT_EQUIPE ="Person.PlayerReportForContextTeam"   # « report » : le rapport du joueur pour ton club
CLUB_HUMAIN = "person.Team.IsHuman"                    # bloc Entraînement : joueurs de ton club seulement
ENTRAINEMENT = "person.PlayerTraining"
ICONE_TRAITS, ICONE_ENTRAINEMENT = "game-concepts-game-concepts-traits", "game-concepts-training-general_small"
ICONE_ROUE = "ui-concepts-cog_small"
# pouces : boutons de FM (PlayerReportDevelopmentProgressReportBlock) ; leur gabarit icône = celui de l'ajout Kinito
# 26.14 (pouce vert / rouge) s'il est dans le jeu, sinon celui de FM
POUCES = {"PraisePlayerButton": ("feliciter", "TransferOfferResponseActionButton", "57e3e0d6ec1bc9047958da07d0f0f9da"),
          "WarnPlayerButton": ("critiquer", "TablePaginationEllipseMarker", "3d654263b1bd0b94a959cfd0c3010f49")}
DEBUT_GABARIT = "UIPickerKinito-rapport-entr-gabarit-"
INFOS_L = 200        # px de la colonne Infos (mesuré : « Modèle de professionnalisme » sur 1 ligne jusqu'en Grand)
COTE_MIN = 210       # px au moins pour les colonnes du terrain et de Pour / Contre (le terrain de FM : 200)
# v2 : la liste des rôles de FM (Sélec. 45 + Niveau 75 + Rôle 200, mesuré sur la capture 8) ENTIÈRE dans la colonne du
# terrain (+ ses marges 2 × 8) : un nom trop long est alors coupé par sa case (« … »), et FM montre le nom entier en
# infobulle au survol (vu par Kinito dans la même liste ailleurs) ; rognée par la colonne (v1), ni « … » ni infobulle
LISTE_ROLES = 340
# Par taille du texte (v2, choix de Kinito du 07/11 sur sa capture 8) :
# - les 3 colonnes de notes à la MÊME largeur, celle de l'intitulé le plus long en FRANÇAIS et en ANGLAIS (ailleurs, un
#   intitulé plus long finit par « … » : son choix, pour laisser la place au terrain) + 85 px : marge gauche 16,6, flèche
#   24, petit écart 4, case de la note 28, marge droite 12 (mesurés sur la capture : 1,143 px d'écran par px de FM) ;
#   ligne « Note (gardien de but) » : intitulé + « 10 /10 » + 29. Mesuré avec les polices du jeu (outils\mesure.py, qui
#   dépasse le rendu d'environ 5 % : marge en plus). Joueur de champ : « Qualités phys. nat. » ou « Note (gardien de
#   but) » ; gardien (ses colonnes égales aussi) : « Sorties dans la surface », les deux « (tendance) » coupés (son choix)
# - Pour / Contre : sa largeur de la v1 (le reste de la ligne partagé avec le terrain : 1372 px - tableau v1, / 2) ;
# - colonne du terrain : tout le reste, et au moins les deux boutons Avec / Sans le ballon entiers en français et en
#   anglais (textes + marges des boutons 4 × 10,5 + bords 16) ;
# - place fixe Personnalité + Rapports médias : le cas le plus long en français et en anglais sur 200 px (« Modèle de
#   professionnalisme », trois rapports médias), titres compris, + 6.
# v10 (Kinito, captures 26-27 : « pour un gardien, la même taille de colonne que pour un joueur ; pas grave si ça coupe
# des notes : ça change trop la fiche quand je passe de l'un à l'autre ») : le gardien prend les largeurs du joueur de
# champ (avant : 204 / 225 / 239 / 253) ; ses intitulés trop longs finissent par « … »
TAILLES_BLOC = [
    ("petit", None, 95, dict(champ=(181,) * 3, gardien=(181,) * 3), 90, dict(pc=323, terrain=220)),
    ("normal", 95, 105, dict(champ=(198,) * 3, gardien=(198,) * 3), 104, dict(pc=285, terrain=249)),
    ("grand", 105, 115, dict(champ=(211,) * 3, gardien=(211,) * 3), 132, dict(pc=259, terrain=268)),
    ("plus-grand", 115, None, dict(champ=(227,) * 3, gardien=(227,) * 3), 142, dict(pc=232, terrain=287)),
]
# v3 (maquette 47) : par taille du texte, le rayon du polygone des attributs (px) dans sa cale POLY_L x POLY_H en bas de
# la colonne de droite : le plus grand où les étiquettes tiennent en français (outils\mesure.py polygone 280 230 :
# 66,4 / 56,5 / 50,0 / 43,5 ; l'anglais tient plus large ; mesure.py dépasse le rendu du jeu d'environ 5 %). La cale :
# la colonne la plus étroite (gardien, texte Plus grand, une fois la carte de gauche posée) fait ~281 px.
# v9 (Kinito : « que le polygone s'adapte à la taille de son bloc ») : la cale prend TOUTE la largeur de la colonne
# (plus 280 px) et garde POLY_H de haut ; le rayon demandé est celui où les étiquettes tiennent EN HAUTEUR
# (mesure.py polygone 380 230 : 83,2 / 79,3 / 76,8 / 74,2, « Arrêts sur la ligne, hauteur » : au-delà de ~380 de large,
# c'est la hauteur qui limite). Si la colonne est plus étroite, FM réduit lui-même le rayon pour que les étiquettes
# tiennent (sa formule : min(demandé, max(rayon où elles tiennent, demandé / 2))) : à voir en jeu (un rétrécissement
# visible à l'ouverture d'une fiche serait la raison de revenir à une cale calibrée).
# v15 (capture 33, texte Normal : « les polygones semblent se redimensionner pour revenir à la même taille ») : c'était
# le rétrécissement annoncé ci-dessus. Mesuré sur la capture (1,14 px d'écran par px de FM ; tableau de notes 3 × 198 :
# texte Normal) : FM dessinait 67,5 au lieu des 79 demandés, la colonne fait 339 de large. Le graphique est maintenant
# deux fois plus grand dans la cale (_polygone_2x) : FM ne réduit plus, il faut donner LE rayon où les étiquettes
# tiennent dans la cale visible. Normal : 67,5, la taille que tu vois aujourd'hui (20 de FM au-dessus et au-dessous des
# étiquettes). Les autres tailles, avec les étiquettes mesurées sur la même capture (deux lignes : 18 de haut ;
# « Jeu aérien 13 » : 46 de large ; « Vision du jeu 12 » : 53 ; × la taille du texte) et la colonne de chaque taille
# (339 - 3 × l'écart de largeur des colonnes de notes : 390 / 339 / 300 / 252) : la même marge en haut et en bas, au
# moins 12 sur les côtés. Plus grand : la colonne (252) limite, « Jeu aérien » contre le bord
# RAYONS_BLOC = {"petit": 72.0, "normal": 67.5, "grand": 65.5, "plus-grand": 45.0}   (jusqu'au bloc v15)
# avant (v9 à v14) : 83 / 79 / 76 / 74, rayons DEMANDÉS, que FM réduisait (le saut au changement de joueur)
POLY_L, POLY_H = 280, 230   # POLY_L : plus utilisé depuis la v9 (cale à la largeur de la colonne)
# px de la colonne des postes (v3 : fixe, 380). Bloc v20 (Kinito, captures 53-54 : « réduire la colonne du terrain, et
# donner ce que tu réduis à la colonne de droite ») : au plus étroit qui garde la liste des rôles ENTIÈRE (LISTE_ROLES :
# ses colonnes fixes de FM, Sélec. 45 + Niveau 75 + Rôle 200, et ses marges ; plus étroite, FM la rogne sans « … », vu en
# v1). Le reste de la colonne tient dedans à toutes les tailles du texte : le terrain de FM (200), les boutons Avec /
# Sans le ballon (TAILLES_BLOC « terrain » : 287 au plus, texte Plus grand), « Postes » et « Comparer »
POSTES_L = LISTE_ROLES
PROJETS_MAX = 5      # projets montés par liste (ses lectures FM 27 : 3 au plus, 143 fichiers) ; FM écrit leur nombre
V_PROJET = "kinitoprojet"   # variables de référence : kinitoprojet<c|l><n> = n-ième projet à court / long terme
PLANS = "PlayerPlansTile_4x4"   # la tuile Projets de FM : ses titres « Court terme (n) » / « Long terme (n) »
LISTES_PROJETS = (("c", "Short-term", "Player.ShortTermPlanList", "Player.ShortTermPlanListCount"),
                  ("l", "Long-term", "Player.LongTermPlanList", "Player.LongTermPlanListCount"))
ECART_COLONNES = 12  # marge de FM à droite des deux premières colonnes de notes (margin-right-global-gap-large)
MOITIE = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden"}
for _k, _v in {"min-width": (131097, 3), "min-height": (131096, 3), "max-width": (131095, 3), "flex-grow": (131084, 2),
               "flex-shrink": (131085, 2), "flex-basis": (131081, 3), "overflow": (131090, 7)}.items():
    PROPRIETES.setdefault(_k, _v)


def racine_de(s):
    return s.children(s.tt["m_VisualTree"]["rid"])[0]


def _premier(s, pred):
    return s and first(s, pred)


def _par_nom_dans(t, root, nom):
    return next((r for r in t.walk(root) if t.name(r) == nom), None)


class SourcesBloc:
    """morceaux de FM du grand bloc, pris dans les modèles D'ORIGINE (jamais ce qu'Alex en a fait)"""
    def __init__(self):
        self.bloc = Src(BLOC)
        b = self.bloc.s
        self.titre_infos = _premier(b, lambda r: b.name(r) == "InfoTitleText")
        self.perso = _premier(b, lambda r: b.name(r) == "PersonalityVisibleForActualPlayer")
        self.trait_h = _premier(b, lambda r: _alias(b, r) == "layout-divider-solid-horizontal")
        self.trait_v = _premier(b, lambda r: _alias(b, r) == "layout-divider-solid-vertical")
        self.carte = _premier(b, lambda r: typ(b, r).endswith("ExpandableContentElement"))
        self.postes = Src("role_selector-large")
        self.cle = Src("AttributesKey")
        self.tableau = Src("AttributesTableTemplate")
        self.pieds = Src("PlayerReportFootednessBlock")
        p = self.pieds.s
        self.remapper = _premier(p, lambda r: typ(p, r).endswith("BindingRemapper"))
        self.traits = Src("PlayerTraitsFrameList")
        self.bans = Src("PlayerReportBansBlock")
        self.pc = Src("ScoutedProsAndCons")
        c = self.pc.s
        self.milieu = _premier(c, lambda r: c.name(r) == "middle-column")
        attente = c and racine_de(c)
        self.type_rapport = next((q["type"]["id"] for q in (c.sd(attente).get("Parameters") or [])
                                  if q.get("name") == "report"), None) if c else None
        self.defil = Src("PlayerRecommendationsMainBlock")
        d = self.defil.s
        self.scroll = _premier(d, lambda r: typ(d, r).endswith("SIScrollView"))
        # titre « Rapports avec les médias » de FM (Personnel) : le texte juste avant la valeur Person.MediaHandling
        self.perso_bloc = Src(SOURCE_LIEU)
        pp = self.perso_bloc.s
        self.titre_medias = None
        for r in (pp.walk() if pp else []):
            kids = pp.children(r)
            for i, x in enumerate(kids):
                if i and (pp.binding(x, "TextBinding") or "").lower() == "person.mediahandling" \
                        and pp.sd(kids[i - 1]).get("TextBinding"):
                    self.titre_medias = copy.deepcopy(pp.sd(kids[i - 1])["TextBinding"])
        # bloc Entraînement : note (IndividualTrainingPlayerHeaderContent), pouces, roue « Actions »
        self.note = Src("IndividualTrainingPlayerHeaderContent")
        n = self.note.s
        cell = _premier(n, lambda r: _alias(n, r) == "PlayerTrainingRatingCell")
        self.note_rm = cell is not None and n.parent[cell]
        self.boutons = Src("PlayerReportDevelopmentProgressReportBlock")
        sb = self.boutons.s
        self.pouces = {nom: _premier(sb, lambda r, nom=nom: sb.name(r) == nom and typ(sb, r) == "FM.UI.FMActionButton")
                       for nom in POUCES}
        self.gabarits = all(_gabarit_kinito(cle, modele) for cle, modele, _ in POUCES.values())
        self.roue = Src("TeamIndividualTrainingBlock")
        a = self.roue.s
        self.actions = _premier(a, lambda r: a.name(r) == "ActionsDropdown" and typ(a, r).endswith(
            "PluginContextMenuBindings"))
        self.titre_traits = _premier(self.traits.s, lambda r: self.traits.s.name(r) == "TraitsTitleFrame")
        self.s_vis, self.vis = ni.visible_model()
        # v3 : taille, réputation et polygone (le grand bloc d'origine, comme la bande) ; titres des projets (la tuile
        # Projets de FM, sa disposition « VisiblePlans » : body-md-strong) ; le BindingSetter de la bannière et la
        # fonction de FM « élément n d'une liste » (comme la 2e nationalité de la bande)
        self.haut = _premier(b, lambda r: b.name(r) == "PersonHeightTextFrame")
        self.reputation = _premier(b, lambda r: b.name(r) == "PlayerReputationTextFrame")
        self.chart = _premier(b, lambda r: typ(b, r).endswith("FMSpiderChart"))
        self.plans = Src(PLANS)
        pl = self.plans.s
        self.titres_projets = {}
        for cle, nom, _liste, _nombre in LISTES_PROJETS:
            x = _premier(pl, lambda r, nom=nom: typ(pl, r).endswith("SIText") and pl.sd(r).get("DebugDisplay") == nom
                         and "body-md-strong" in (pl.elem(r).get("m_Classes") or []))
            self.titres_projets[cle] = pl.parent[x] if x is not None else None
        self.banniere = Src(BANNIERE)
        bs = self.banniere.s
        self.setter = pieces(bs)[0].get("setter") if bs is not None else None
        self.fn_element = fonction_element()
        # un texte de valeur de FM (la personnalité : body-md, lien direct) et son titre (traduit par FM), recopiés
        # pour les projets et le titre « Projets »
        self.texte_valeur = _premier(b, lambda r: typ(b, r).endswith("SIText")
                                     and (b.binding(r, "TextBinding") or "").lower() == "person.personality")
        self.titre_perso = _premier(b, lambda r: b.name(r) == "PlayerPersonalityTitleText")

    def manquants(self):
        """v3 : seulement ce que le bloc v3 utilise"""
        m = []
        for nom, v in (("bloc d'origine", self.bloc.s), ("titre Infos", self.titre_infos),
                       ("personnalité", self.perso), ("traits", self.trait_h), ("traits verticaux", self.trait_v),
                       ("carte du bloc", self.carte), ("postes", self.postes.s), ("légende", self.cle.s),
                       ("tableau", self.tableau.s), ("pieds", self.pieds.s), ("remapper", self.remapper),
                       ("caractéristiques", self.traits.s), ("titre caractéristiques", self.titre_traits),
                       ("défilement", self.scroll), ("titre rapports médias", self.titre_medias),
                       ("SIVisible", self.vis), ("taille", self.haut), ("réputation", self.reputation),
                       ("polygone", self.chart), ("tuile Projets", self.plans.s),
                       ("titre Court terme", self.titres_projets.get("c")),
                       ("titre Long terme", self.titres_projets.get("l")),
                       ("BindingSetter de la bannière", self.setter),
                       ("fonction élément d'une liste", self.fn_element),
                       ("texte de la personnalité", self.texte_valeur), ("titre de la personnalité", self.titre_perso)):
            if v is None or v is False:
                m.append(nom)
        return m


def _gabarit_kinito(cle, modele):
    """le gabarit icône de l'ajout Kinito 26.14 (pouce) est-il dans le jeu ? (le modèle réécrit porte son nom)"""
    o = hp.ouvrir(modele)
    return o is not None and any(o[3].name(r).startswith(DEBUT_GABARIT + cle) for r in o[3].walk())


def _vide(t, s, modele, parent, classes, css=None, nom=""):
    """une boîte vide (copie d'un VisualElement de FM, sans enfants ni style) : la 1re de la tuile, ensuite boite()"""
    b = t.clone(modele, parent, src=s)
    for c in list(t.children(b)):
        t.remove(c)
    t.elem(b)["m_SerializedDataOverride"] = []
    no_styles(t, b)
    t.sd(b)["name"] = nom
    t.sd(b)["name_UxmlAttributeFlags"] = 1 if nom else 0
    t.elem(b)["m_Classes"] = list(classes)
    if css:
        t.styles.style(t, b, css)
    return b


def _trait(t, k, parent, vertical=False):
    d = k.bloc.clone(t, k.trait_v if vertical else k.trait_h, parent)
    t.sd(d)["name"] = ""
    t.elem(d)["m_Classes"] = (["margin-horizontal-global-gap-large", "align-self-stretch"] if vertical
                              else ["align-self-stretch", "margin-vertical-global-gap-regular"])
    no_styles(t, d)
    t.styles.style(t, d, {"flex-shrink": 0})
    return d


def _dans_defilement(t, k, parent, index, enfants):
    """un SIScrollView de FM (vide) à la place index de parent, qui prend la hauteur qui reste ; enfants déplacés dedans"""
    v = t.clone(k.scroll, parent, index, src=k.defil.s)
    for c in list(t.children(v)):
        t.remove(c)
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = "", 0
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = ["align-self-stretch"], -1
    t.styles.style(t, v, MOITIE)
    for c in enfants:
        move(t, c, v)
    return v


def _visible_direct(t, k, parent, chemin, inverse=False):
    """SIVisible de FM « visible si <chemin> est vrai / non nul » (celui de la personnalité recopié, vidé)"""
    v = k.bloc.clone(t, k.perso, parent)
    for c in list(t.children(v)):
        t.remove(c)
    no_styles(t, v)
    sd = t.sd(v)
    sd["name"] = ""
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = (1 if inverse else 0), 1
    t.elem(v)["m_Classes"] = ["align-self-stretch"]
    return v


def _colonne_postes(t, k, ligne, mini, base=None):
    """toute la place qui reste dans la ligne (v2), ou « base » px (v3 : la colonne de droite prend le reste) ; au moins
    « mini » (les boutons Avec / Sans le ballon entiers) et la liste des rôles entière"""
    plus_petit = max(COTE_MIN, mini, LISTE_ROLES)
    col = boite(t, ligne, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": plus_petit,
                           "overflow": "hidden"} if base is None else
                {"flex-grow": 0, "flex-shrink": 0, "flex-basis": max(base, plus_petit), "min-width": plus_petit,
                 "overflow": "hidden"}, ["column-direction-normal", "align-self-stretch"])
    p = k.postes.s
    r = k.postes.clone(t, racine_de(p), col)
    for x in [x for x in t.walk(r) if t.name(x) == "player-pos-button-frame"]:
        t.remove(x)   # le poste écrit sous « Postes » (Kinito : « ça fait pas beau », il descend tout le bloc)
    mf = _par_nom_dans(t, r, "main-frame")
    if mf is not None:   # sa classe de FM le fixe à 380 px au moins : il prend la largeur de la colonne
        t.styles.style(t, mf, {"min-width": 0, "max-width": {"unit": 2, "value": 100.0}, "flex-shrink": 1})
    if base is not None:
        # v8 (Kinito, captures 23-25 : « switcher de joueur fait changer l'emplacement de la fiche, JAMAIS ») : la liste
        # des rôles de FM (RoleTable : hauteur au plus 228, sinon celle de ses lignes) poussait le bloc (4 rôles : haut
        # du bloc à y 357 ; 5 : 337 ; 6 : il déborde sur les tuiles). Toute la chaîne jusqu'à la liste (et jusqu'à celle
        # du mode « Comparer ») prend la place qui RESTE (base 0, au plus 0 de hauteur propre) : sa hauteur ne compte
        # plus dans celle du bloc, et au-delà de la place, la liste de FM défile
        t.styles.style(t, r, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden"})
        for nom in ("RoleTable", "comparison-players-list-table"):
            x = _par_nom_dans(t, r, nom)
            while x is not None and x != r:
                t.styles.style(t, x, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0})
                x = t.parent.get(x)
    cle = k.cle.clone(t, racine_de(k.cle.s), col)
    t.elem(cle)["m_Classes"] = (t.elem(cle).get("m_Classes") or []) + ["align-self-centre",
                                                                         "margin-top-global-gap-regular"]
    return col


def _pieds_ecartes(t, k, instance):
    """le bloc des pieds de FM (modèle inclus) remplacé par sa copie, pied gauche / pied droit répartis sur la largeur"""
    par = t.parent[instance]
    i = t.children(par).index(instance)
    r = k.pieds.clone(t, racine_de(k.pieds.s), par, i)
    t.remove(instance)
    cadre = _par_nom_dans(t, r, "FootednessFrame")
    if cadre is not None:
        t.elem(cadre)["m_Classes"] = ["row-direction-normal", "justify-content-space-evenly", "align-self-stretch"]
        for x in t.children(cadre):
            t.elem(x)["m_Classes"] = []
    t.elem(r)["m_Classes"] = ["align-self-stretch"]
    return r


def _entrainement(t, k, parent):
    """sous parent (tes joueurs suivant l'entraînement) : trait, titre « Entraînement », note + pouces + roue « Actions »"""
    w = _visible_direct(t, k, parent, ENTRAINEMENT)
    w = _visible_direct(t, k, w, CLUB_HUMAIN)
    t.elem(w)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    _trait(t, k, w)
    titre = k.traits.clone(t, k.titre_traits, w)
    t.sd(titre)["name"] = ""
    for x in t.walk(titre):
        if x != titre and t.name(x) == "TraitsIcon":
            t.elem(x)["m_Classes"] = [c if c != ICONE_TRAITS else ICONE_ENTRAINEMENT for c in t.elem(x)["m_Classes"]]
        if typ(t, x).endswith("SIText"):
            sd = t.sd(x)
            sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
            sd["TextBinding"]["m_kind"] = 0
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            sd["text"], sd["text_UxmlAttributeFlags"] = L("Entraînement", "Training"), 1
            sd["DebugDisplay"] = sd["text"]
        if x != titre:
            t.sd(x)["name"] = ""
    ligne = boite(t, w, {}, ["row-direction-normal", "align-items-center", "align-self-stretch"])
    rm = k.note.clone(t, k.note_rm, ligne)   # BindingRemapper binding -> person, avec la pastille de la note
    t.elem(rm)["m_Classes"] = ["margin-right-global-gap-large"]
    t.styles.style(t, rm, {"flex-shrink": 0})
    # pouces : boutons de FM, « player » fourni par un BindingRemapper player -> person
    pr = k.note.clone(t, k.note_rm, ligne)
    for x in list(t.children(pr)):
        t.remove(x)
    no_styles(t, pr)
    t.sd(pr)["name"] = ""
    t.sd(pr)["Mappings"] = [{"m_serialisedType": 0, "from": "player", "to": {"m_path": "person"},
                             "type": {"id": JOUEUR}}]
    t.elem(pr)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-right-global-gap-regular"]
    t.styles.style(t, pr, {"flex-shrink": 0})
    for i, (nom, (cle, _modele, guid)) in enumerate(POUCES.items()):
        b = k.boutons.clone(t, k.pouces[nom], pr)
        t.elem(b)["m_Classes"] = ["margin-right-global-gap-regular"] if i < len(POUCES) - 1 else []
        if k.gabarits:
            t.sd(b)["ActionsListWidget"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
            t.sd(b)["ActionsListWidget_UxmlAttributeFlags"] = 1
    boite(t, ligne, {"flex-grow": 1}, [])   # espace : la roue calée à droite
    a = k.roue.clone(t, k.actions, ligne)
    t.sd(a)["name"] = ""
    t.elem(a)["m_Classes"] = [c for c in t.elem(a).get("m_Classes") or [] if c != "flex-grow-class"]
    t.styles.style(t, a, {"flex-shrink": 0})
    t.sd(a)["BindingPaths"] = [{"m_path": "person"}]
    x = next((c for c in t.children(a) if typ(t, c).endswith("SIText")), None)
    if x is not None:   # le texte « Actions » gardé pour FM, caché ; l'engrenage de FM devant le chevron
        t.elem(x)["m_Classes"] = list(t.elem(x).get("m_Classes") or []) + ["hidden-item"]
        ch = next((c for c in t.children(a) if c != x and typ(t, c).endswith("VisualElement")), None)
        if ch is not None:
            i = t.clone_shallow(ch, a, t.children(a).index(x))
            t.sd(i)["name"] = ""
            t.elem(i)["m_Classes"], t.elem(i)["m_RuleIndex"] = [ICONE_ROUE, "margin-right-global-gap-small"], -1
    return w


def _tableau(t, k, ligne, largeurs, entrainement=True):
    """tableau d'attributs de FM recopié : chaque colonne à sa largeur (largeurs[champ|gardien]), le conteneur prend la
    largeur de la disposition affichée ; pieds écartés ; bloc Entraînement sous les pieds (gardien : sous Gardien),
    sauf en v3 (entrainement=False : il monte dans la bande)"""
    cont = boite(t, ligne, {"flex-grow": 0, "flex-shrink": 1, "min-width": 0, "overflow": "hidden"},
                 ["column-direction-normal", "align-self-stretch"])
    r = k.tableau.clone(t, racine_de(k.tableau.s), cont)
    sw = next((x for x in t.walk(r) if typ(t, x).endswith("BindableSwitchElement")
               and t.binding(x) == "person.IsGoalkeeper"), None)
    if sw is None:
        return ["tableau d'attributs : aiguillage joueur / gardien introuvable"]
    for nom_disp, disp in zip(("champ", "gardien"), t.children(sw)):
        # la largeur de la disposition, écrite (le conteneur la prend) ; au plus celle du conteneur : s'il manque de la
        # place (le terrain et Pour / Contre gardent COTE_MIN), les colonnes rétrécissent ensemble
        cols = t.children(disp)
        total = sum(largeurs[nom_disp]) + ECART_COLONNES * (len(cols) - 1)
        t.styles.style(t, disp, {"flex-grow": 0, "width": total, "max-width": {"unit": 2, "value": 100.0}})
        for c, w in zip(cols, largeurs[nom_disp]):
            t.styles.style(t, c, {"flex-grow": 0, "flex-shrink": 1, "flex-basis": w, "min-width": 0})
    for x in [x for x in t.walk(r) if _alias(t, x) == "PlayerReportFootednessBlock"]:
        _pieds_ecartes(t, k, x)

    def liste(chemin):
        return next((x for x in t.walk(r) if typ(t, x).endswith("StreamedObjectList")
                     and (t.binding(x) or "").lower() == chemin.lower()), None)
    physique, gardien = liste("Person.AttributesPhysical"), liste("Person.AttributesGoalkeeping")
    if physique is None or gardien is None:
        return ["tableau d'attributs : listes Physique / Gardien introuvables"]
    if entrainement:
        _entrainement(t, k, t.parent[t.parent[physique]])
        _entrainement(t, k, t.parent[gardien])
    return []


def _infos(t, k, ligne, haut_perso):
    col = boite(t, ligne, {"width": INFOS_L, "min-width": INFOS_L, "flex-shrink": 0},
                ["column-direction-normal", "align-self-stretch"])
    ti = k.bloc.clone(t, k.titre_infos, col)
    t.elem(ti)["m_Classes"] = (t.elem(ti).get("m_Classes") or []) + ["align-self-start"]
    _trait(t, k, col)
    # Personnalité + Rapports avec les médias : place FIXE, celle du cas le plus long (Kinito, 06/11)
    zone = boite(t, col, {"height": haut_perso, "min-height": haut_perso, "flex-shrink": 0, "overflow": "hidden"},
                 ["column-direction-normal", "align-self-stretch"])
    v = k.bloc.clone(t, k.perso, zone)
    cadre = t.children(v)[0]
    t.elem(cadre)["m_Classes"] = (t.elem(cadre).get("m_Classes") or []) + ["margin-bottom-global-gap-small"]
    m = t.clone(cadre, v)
    for x in t.walk(m):
        sd = t.sd(x)
        if sd.get("name"):
            sd["name"] = sd["name"].replace("Personality", "MediaHandling")
        tb = sd.get("TextBinding")
        if not isinstance(tb, dict):
            continue
        if tb.get("m_kind") == 1 and (tb["m_direct"]["Path"]["m_path"] or "").lower().endswith("personality"):
            tb["m_direct"]["Path"]["m_path"] = tb["m_direct"]["Path"]["m_path"][:-len("Personality")] + "MediaHandling"
            sd["DebugDisplay"] = "Media-friendly"
        else:
            sd["TextBinding"] = copy.deepcopy(k.titre_medias)
            sd["DebugDisplay"] = "Media Handling Style"
    t.elem(m)["m_Classes"] = [c for c in t.elem(m).get("m_Classes") or [] if not c.startswith("margin-bottom")]
    _trait(t, k, col)
    # Caractéristiques, puis Suspensions : moitié chacune de ce qui reste, la liste défile dans sa place (titres fixes)
    for src_bloc, titre_nom in ((k.traits, "TraitsTitleFrame"), (k.bans, "BansTitleFrame")):
        place = boite(t, col, MOITIE, ["column-direction-normal", "align-self-stretch"])
        r = src_bloc.clone(t, racine_de(src_bloc.s), place)
        t.styles.style(t, r, MOITIE)
        haut = r
        kids = t.children(r)
        if len(kids) == 1 and not typ(t, kids[0]).endswith("BindableSwitchElement"):   # Caractéristiques : un cadre
            haut = kids[0]
            t.styles.style(t, haut, MOITIE)
        titre = next((x for x in t.children(haut) if t.name(x) == titre_nom), None)
        reste = [x for x in t.children(haut) if x != titre]
        if titre is None or not reste:
            return [f"Infos : {titre_nom} introuvable"]
        t.styles.style(t, titre, {"flex-shrink": 0})
        _dans_defilement(t, k, haut, t.children(haut).index(reste[0]), reste)
        if src_bloc is k.traits:
            _trait(t, k, col)
    return []


def _pour_contre(t, k, ligne, largeur):
    """à sa largeur de la v1 (v2 : la place gagnée sur les notes va au terrain, pas ici)"""
    col = boite(t, ligne, {"flex-grow": 0, "flex-shrink": 1, "flex-basis": largeur, "min-width": COTE_MIN,
                           "overflow": "hidden"}, ["column-direction-normal", "align-self-stretch"])
    rm = t.clone(k.remapper, col, src=k.pieds.s)
    for x in list(t.children(rm)):
        t.remove(x)
    no_styles(t, rm)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "report", "to": {"m_path": RAPPORT_EQUIPE},
                             "type": {"id": k.type_rapport}}]
    t.elem(rm)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    t.styles.style(t, rm, MOITIE)
    v = _visible_direct(t, k, rm, "report.HasScoutedInfo")
    t.styles.style(t, v, MOITIE)
    mid = k.pc.clone(t, k.milieu, v)
    no_styles(t, mid)
    t.elem(mid)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    t.styles.style(t, mid, MOITIE)
    for i, part in enumerate(t.children(mid)):   # Pour, puis Contre : une moitié chacun, la liste défile
        t.elem(part)["m_Classes"] = ["column-direction-normal", "align-self-stretch"] + (
            ["margin-top-global-gap-large"] if i else [])
        t.styles.style(t, part, MOITIE)
        tete = t.children(part)[0]
        t.elem(tete)["m_Classes"] = ["row-direction-normal", "align-items-center"]
        t.styles.style(t, tete, {"flex-shrink": 0})
        txt = next((x for x in t.children(tete) if typ(t, x).endswith("SIText")), None)
        if txt is not None:
            t.elem(txt)["m_Classes"] = ["body-sm-strong"] + [c for c in t.elem(txt).get("m_Classes") or []
                                                              if c.endswith("string-colour")]
        d = k.bloc.clone(t, k.trait_h, part, 1)
        t.sd(d)["name"] = ""
        t.elem(d)["m_Classes"] = ["align-self-stretch", "margin-vertical-global-gap-regular"]
        no_styles(t, d)
        t.styles.style(t, d, {"flex-shrink": 0})
        liste = next((x for x in t.children(part) if typ(t, x).endswith("StreamedObjectList")), None)
        if liste is not None:
            _dans_defilement(t, k, part, t.children(part).index(liste), [liste])
    return col


# ---------- bloc v3 (maquette 47) : la colonne de droite ----------
DEMI = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0, "overflow": "hidden"}
# v6 : les classes des cadres « titre au-dessus, valeur dessous » (Kinito trouve les marges de Taille / Réputation
# justes) : le 1er d'une paire (marge dessous), le 2e (sans marge). Personnalité / Rapports médias, Taille / Réputation,
# Court terme / Long terme les prennent toutes.
CADRES_INFOS = (["column-direction-normal", "align-items-start", "margin-bottom-global-gap-small",
                 "margin-bottom-global-gap-regular"],
                ["column-direction-normal", "align-items-start"])


def _remap(t, k, parent, liens, classes=()):
    """un BindingRemapper de FM (celui du bloc des pieds, vidé) : liens = {de: (chemin, type)}"""
    rm = t.clone(k.remapper, parent, src=k.pieds.s)
    for x in list(t.children(rm)):
        t.remove(x)
    no_styles(t, rm)
    t.sd(rm)["name"] = ""
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": a, "to": {"m_path": p}, "type": {"id": ty}}
                            for a, (p, ty) in liens.items()]
    t.elem(rm)["m_Classes"] = list(classes)
    return rm


def _titre_fixe(t, k, parent, fr, en):
    """un titre de FM (celui de la personnalité : body-sm, gris) avec un texte fixe fr / en"""
    x = k.bloc.clone(t, k.titre_perso, parent)
    sd = t.sd(x)
    sd["name"] = ""
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    sd["text"], sd["text_UxmlAttributeFlags"] = L(fr, en), 1
    sd["DebugDisplay"] = sd["text"]
    return x


def _texte_lie(t, k, parent, chemin, classes):
    """un texte de valeur de FM (celui de la personnalité) lié à chemin"""
    x = k.bloc.clone(t, k.texte_valeur, parent)
    no_styles(t, x)
    sd = t.sd(x)
    sd["name"] = ""
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["TextBinding_UxmlAttributeFlags"] = 1
    sd["DebugDisplay"] = ""
    t.elem(x)["m_Classes"] = list(classes)
    t.styles.style(t, x, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})
    return x


def _a_la_ligne(t, r):
    """les textes sous r écrits sur plusieurs lignes s'il le faut (jamais coupés)"""
    for x in t.walk(r):
        if typ(t, x).endswith("SIText"):
            t.elem(x)["m_Classes"] = [c for c in t.elem(x).get("m_Classes") or []
                                      if c not in ("content-no-wrap", "content-ellipsis")]
            t.styles.style(t, x, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})


def _perso_medias(t, k, parent):
    """Personnalité, puis Rapports avec les médias (comme la v2), à la ligne s'il le faut (Kinito : jamais coupés)"""
    # v5 (mesuré sur ses captures 17-19) : la place libre de la moitié était PARTAGÉE à parts égales entre ce bloc et
    # les projets (fiche de Nzinga-Pambani 21 px plus haute : « Projets » 11 px plus bas) : le SIVisible de FM s'étire
    # (aucune règle de FM sur lui : ça vient du type) ; rangé dans une boîte qui ne prend que sa hauteur, il ne peut plus
    boite_perso = boite(t, parent, {"flex-grow": 0, "flex-shrink": 0}, ["column-direction-normal", "align-self-stretch"])
    v = k.bloc.clone(t, k.perso, boite_perso)
    t.elem(v)["m_Classes"] = ["column-direction-normal", "align-self-stretch"]
    t.styles.style(t, v, {"flex-shrink": 0})
    deja = any(typ(t, x).endswith("SIText") and (t.binding(x, "TextBinding") or "").lower().endswith("mediahandling")
               for x in t.walk(v))
    if not deja:
        cadre = t.children(v)[0]
        m = t.clone(cadre, v)
        for x in t.walk(m):
            sd = t.sd(x)
            if sd.get("name"):
                sd["name"] = sd["name"].replace("Personality", "MediaHandling")
            tb = sd.get("TextBinding")
            if not isinstance(tb, dict):
                continue
            if tb.get("m_kind") == 1 and (tb["m_direct"]["Path"]["m_path"] or "").lower().endswith("personality"):
                tb["m_direct"]["Path"]["m_path"] = tb["m_direct"]["Path"]["m_path"][:-len("Personality")] + \
                    "MediaHandling"
                sd["DebugDisplay"] = "Media-friendly"
            else:
                sd["TextBinding"] = copy.deepcopy(k.titre_medias)
                sd["DebugDisplay"] = "Media Handling Style"
        t.elem(m)["m_Classes"] = [c for c in t.elem(m).get("m_Classes") or [] if not c.startswith("margin-bottom")]
    # v6 (Kinito, capture 20 : « la marge entre Équilibré et Rapports médias, harmonise : la taille et la réputation, ça
    # paraît mieux ») : les deux cadres prennent EXACTEMENT les classes des cadres Taille / Réputation (CADRES_INFOS)
    for i, x in enumerate(t.children(v)):
        t.elem(x)["m_Classes"] = list(CADRES_INFOS[min(i, 1)])
        t.styles.style(t, x, {"align-self": "stretch", "flex-shrink": 0, "flex-grow": 0})
    t.styles.style(t, v, {"flex-grow": 0, "flex-shrink": 0})
    _a_la_ligne(t, v)
    return v


def _projets(t, k, parent):
    """« Projets », puis court et long terme : le titre de FM (« Court terme (n) ») et chaque projet sur UNE ligne
    (« … », la phrase entière au survol : réglage par défaut des textes de FM, comme la liste des rôles) ; le n-ième
    projet par la fonction de FM « élément n d'une liste » (la ligne de projet de FM sert aussi à Personnel : on n'y
    touche pas) ; quand il n'y en a aucun, la liste de FM a une seule ligne, « Aucun projet ». Le tout défile dans sa
    place."""
    # v3 (07/11, son jeu a PLANTÉ à l'ouverture d'une fiche, Player.log : NullReferenceException dans
    # SIVisible -> BindableWidgetUtils.EvaluateAsBoolean, juste après le SetBinding de la fonction « élément n ») : un
    # SIVisible lié DIRECTEMENT à la variable d'un projet fait planter le jeu. Chaque ligne n >= 1 est montrée par le
    # NOMBRE de projets (« nombre > n », la comparaison de FM, comme sa tuile Projets) ; la 1re toujours (sans projet,
    # la liste de FM a une ligne « Aucun projet »). Plus aucun SIVisible sur une variable de projet.
    b = k.s_vis.sd(k.vis)["Binding"]
    x = _titre_fixe(t, k, parent, "Projets", "Plans")
    t.styles.style(t, x, {"flex-shrink": 0})
    rm = _remap(t, k, parent, {"player": ("person", JOUEUR)}, ["column-direction-normal", "align-self-stretch"])
    t.styles.style(t, rm, MOITIE)
    col = boite(t, rm, {"flex-shrink": 0}, ["column-direction-normal", "align-self-stretch"])
    for j, (cle, _nom, liste, nombre) in enumerate(LISTES_PROJETS):
        # v6 (Kinito, capture 20 : encore trop d'espace entre « Court terme » et « Aucun projet », mais pas entre
        # « Aucun projet » et « Long terme ») : le seul élément placé ENTRE le titre et le 1er projet était le
        # BindingSetter qui porte les variables ; chaque partie EST maintenant ce BindingSetter, avec dedans son titre
        # puis ses projets, et il prend les marges des cadres Taille / Réputation (CADRES_INFOS)
        s = seul(t, k.banniere.s, k.setter, col)
        sd = t.sd(s)
        tete = k.plans.clone(t, k.titres_projets[cle], s)
        t.sd(tete)["name"] = ""
        t.elem(tete)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"]
        # v7 (capture 22 : la v6 n'avait rien changé) : la ligne de titre de la tuile de FM porte une marge ÉCRITE dessous
        # (12 px sous « Court terme », 8 sous « Long terme » : outils\regles_projets.py), qui passait avant notre classe ;
        # sans elle, la marge est celle des titres de FM (margin-bottom-global-gap-small, comme Taille, Personnalité)
        no_styles(t, tete)
        t.styles.style(t, tete, {"flex-shrink": 0})
        # v5 : les titres à la taille de celui des Caractéristiques (body-sm-strong au lieu de body-md-strong)
        for x in t.walk(tete):
            if typ(t, x).endswith("SIText"):
                t.elem(x)["m_Classes"] = ["body-sm-strong" if c == "body-md-strong" else c
                                          for c in t.elem(x).get("m_Classes") or []]
        noms = [f"{V_PROJET}{cle}{i}" for i in range(PROJETS_MAX)]
        sd["ValueVariables"], sd["ValueVariables_UxmlAttributeFlags"] = [], 1
        sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": n} for n in noms]
        sd["ReferenceVariables_UxmlAttributeFlags"] = 1
        sd["BindFunction"] = [element_de_liste(k.fn_element, liste, i, n) for i, n in enumerate(noms)]
        sd["BindFunction_UxmlAttributeFlags"] = 1
        t.elem(s)["m_Classes"] = list(CADRES_INFOS[min(j, 1)]) + ["align-self-stretch"]
        t.styles.style(t, s, {"flex-shrink": 0})
        for i, n in enumerate(noms):
            dans = s if i == 0 else visible(t, k, s, None, "", ni.make_binding(b, OP_SUP, [nombre], i))
            # v5 : le 1er projet collé à son titre (plus de marge au-dessus), les suivants espacés comme avant
            _texte_lie(t, k, dans, f"{n}.Name", ["body-sm", "global-text-primary", "content-no-wrap",
                                                  "content-ellipsis", "align-self-stretch"]
                       + (["margin-top-global-gap-small"] if i else []))
    _dans_defilement(t, k, rm, 0, [col])
    return []


def _liste_qui_defile(t, k, parent, src_bloc, titre_nom):
    """un bloc de FM (Caractéristiques) : son titre fixe, sa liste qui défile dans la place qui reste (comme la v2)"""
    place = boite(t, parent, MOITIE, ["column-direction-normal", "align-self-stretch"])
    r = src_bloc.clone(t, racine_de(src_bloc.s), place)
    t.styles.style(t, r, MOITIE)
    haut = r
    kids = t.children(r)
    if len(kids) == 1 and not typ(t, kids[0]).endswith("BindableSwitchElement"):
        haut = kids[0]
        t.styles.style(t, haut, MOITIE)
    titre_ = next((x for x in t.children(haut) if t.name(x) == titre_nom), None)
    reste = [x for x in t.children(haut) if x != titre_]
    if titre_ is None or not reste:
        return [f"colonne de droite : {titre_nom} introuvable"]
    t.styles.style(t, titre_, {"flex-shrink": 0})
    _dans_defilement(t, k, haut, t.children(haut).index(reste[0]), reste)
    return []


def _taille_reputation(t, k, parent):
    """Taille, puis Réputation : les cadres de FM (titre au-dessus, valeur dessous, comme la Personnalité), avec les
    marges des deux cadres de la personnalité, pour que les lignes s'alignent d'une moitié à l'autre"""
    for i, rid in enumerate((k.haut, k.reputation)):
        c = k.bloc.clone(t, rid, parent)
        t.sd(c)["name"] = ""
        t.elem(c)["m_Classes"] = list(CADRES_INFOS[i])
        t.styles.style(t, c, {"flex-shrink": 0, "align-self": "stretch"})
        _a_la_ligne(t, c)


PLEIN, DOUBLE = {"unit": 2, "value": 100.0}, {"unit": 2, "value": 200.0}


def _taille_2x(hh, largeur=DOUBLE):
    """largeur (200 % : deux fois la cale) et hauteur fixe 2 × hh, sans grandir ni rétrécir, CENTRÉ (le polygone de stats
    de FM est étiré par son style d'origine : étiré, il se calerait en haut de la cale et déborderait par le bas)"""
    return {"width": largeur, "min-width": largeur, "max-width": largeur, "height": 2 * hh, "min-height": 2 * hh,
            "max-height": 2 * hh, "flex-grow": 0, "flex-shrink": 0, "align-self": "center"}


def _cale_2x(t, parent, hh):
    """la cale visible du polygone : toute la largeur, hh de haut, qui COUPE ce qui dépasse ; ce qu'on y met est centré"""
    return boite(t, parent, {"flex-shrink": 0, "height": hh, "min-height": hh, "max-height": hh, "overflow": "hidden"},
                 ["row-direction-normal", "justify-content-center", "align-items-center", "align-self-stretch"])


def _regler_polygone_2x(t, poly, hh, rayon_px, etiquettes=GUID_ETIQUETTES, anneaux=None):
    """le graphique remplit son parent (2 × la cale) ; rayon = rayon_px : FM le prend en % du plus petit côté du
    graphique, sa hauteur 2 × hh (sa largeur, 2 × celle de la cale, est toujours plus grande ici)"""
    sd = t.sd(poly)
    sd["name"] = ""
    sd["SpiderChartRadiusPercentage"] = round(100.0 * rayon_px / (2 * hh), 2)
    if anneaux is not None:
        sd["NumberOfInnerRings"] = anneaux
    sd["LabelsTemplate"]["m_AssetGUID"] = etiquettes
    t.elem(poly)["m_Classes"] = [x for x in t.elem(poly)["m_Classes"]
                                 if x not in ("justify-content-end", "flex-grow-class", "align-self-stretch",
                                              "base-template-grow")]
    t.styles.style(t, poly, _taille_2x(hh, PLEIN))


def _polygone_2x(t, k, parent, hh, rayon_px, remap, poser):
    """un polygone des attributs SANS « flash » au changement de joueur (Kinito, 08/11, capture 33 : « les polygones
    semblent se redimensionner pour revenir à la même taille ; Alex a déjà eu ce problème et l'a fixé »).
    Ce qu'Alex a trouvé (entete_tuile v12 puis v22, fiche_fmguru v31) : au changement de joueur, FM dessine d'abord une
    image SANS étiquettes, au rayon demandé en entier, puis les étiquettes reviennent et FM réduit le rayon pour qu'elles
    tiennent dans le graphique : le polygone saute. Sa solution, reprise ici : une cale visible qui coupe (_cale_2x) et,
    centré dedans, le graphique DEUX fois plus grand (200 % de large, 2 × hh de haut) : les étiquettes y tiennent
    toujours, FM ne réduit plus, la taille est la même sur les deux images ; le rayon est donné en px (rayon_px),
    choisi pour que les étiquettes tiennent dans la cale visible (voir RAYONS_BLOC). Le graphique reste dans un
    SIVisible lié aux données du joueur (person.Age > 0 : caché tant qu'elles ne sont pas lues, comme avant).
    remap(dans) pose le remapper player <- person, poser(dans) recopie le polygone de FM ; rend le polygone posé"""
    b = k.s_vis.sd(k.vis)["Binding"]
    zone = _cale_2x(t, parent, hh)
    attente = ni.new_visible(t, k.s_vis, k.vis, zone, None, "", ni.make_binding(b, OP_SUP, ["person.Age"], 0))
    t.styles.style(t, attente, _taille_2x(hh))
    rm = remap(attente)
    t.styles.style(t, rm, _taille_2x(hh, PLEIN))
    poly = poser(rm)
    _regler_polygone_2x(t, poly, hh, rayon_px, anneaux=ANNEAUX)
    return poly


def _rapport_bloc(t, k, kc, parent):
    """le rapport (_rapport47 : titre, note ou « Observer joueur », Pour puis Contre avec leurs phrases, ou « Pas
    encore de rapport ») en bas de la colonne de droite, POLY_H de haut (v15 : option « polygone » de l'app ; bloc
    v16 : toujours, le polygone des attributs est dans la bande). kc = les sources de la BANDE, k celles du bloc (le
    défilement de FM) ; la tuile reçoit team, pas localteam : un remapper localteam <- team"""
    zone = boite(t, parent, {"flex-shrink": 0, "height": POLY_H, "min-height": POLY_H, "max-height": POLY_H,
                             "overflow": "hidden", "padding-top": 10, "padding-left": 8, "padding-right": 8},
                 ["column-direction-normal", "align-items-center", "align-self-stretch"])
    rm = remapper(t, kc.rm_model, zone, {"localteam": ("team", EQUIPE)},
                  ["column-direction-normal", "align-items-center", "align-self-stretch"])
    t.styles.style(t, rm, {"flex-grow": 1, "min-height": 0})
    return _rapport47(t, kc, rm, k)


def _colonne_droite(t, k, ligne, kc):
    """v3 : tout le reste de la ligne. En haut, deux moitiés [Personnalité, Rapports médias, Projets | Taille,
    Réputation, Caractéristiques] ; dessous, le rapport (bloc v16 ; jusqu'à la v15, le polygone des attributs,
    _polygone_2x au rayon RAYONS_BLOC : il est maintenant dans la bande). kc = sources de la bande"""
    col = boite(t, ligne, DEMI, ["column-direction-normal", "align-self-stretch"])
    haut = boite(t, col, {**MOITIE, "flex-direction": "row"}, ["row-direction-normal", "align-self-stretch"])
    g = boite(t, haut, DEMI, ["column-direction-normal", "align-self-stretch"])
    _perso_medias(t, k, g)
    _trait(t, k, g)
    msgs = _projets(t, k, g)
    _trait(t, k, haut, True)
    d = boite(t, haut, DEMI, ["column-direction-normal", "align-self-stretch"])
    _taille_reputation(t, k, d)
    _trait(t, k, d)
    msgs += _liste_qui_defile(t, k, d, k.traits, "TraitsTitleFrame")
    _trait(t, k, col)
    msgs += _rapport_bloc(t, k, kc, col)
    return msgs


def _sans_souris(t, r):
    """l'élément ne prend pas la souris (pickingMode Ignore) : ce qui est dessous la reçoit"""
    sd = t.sd(r)
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1


def construire_tuile(t, k):
    """la tuile (modèle d'origine) vidée, puis notre bloc : une disposition par taille du texte"""
    uxml = t.tt["m_VisualTree"]["rid"]
    for c in list(t.children(uxml)):
        t.remove(c)
    t.tt["m_Usings"] = []
    t.tt["m_ContentContainerId"] = 0
    retirer_regles(t, range(len(t.styles.sh["m_Rules"])))
    b = k.s_vis.sd(k.vis)["Binding"]
    racine = _vide(t, k.bloc.s, k.titre_infos and k.bloc.s.parent[k.titre_infos], uxml,
                   ["column-direction-normal", "flex-grow-class", "align-self-stretch"], nom=NOM_TUILE)
    msgs = []
    kc = None   # v12 : les sources de la bande, pour le bas de la carte du joueur
    for nom_t, bas, haut, largeurs, _haut_perso, cotes in TAILLES_BLOC:
        dans = racine
        if bas is not None:
            dans = visible(t, k, dans, None, "", ni.make_binding(b, OP_SUP, [TAILLE_TEXTE], bas - 1), {"flex-grow": 1})
        if haut is not None:
            dans = visible(t, k, dans, None, "", ni.make_binding(b, OP_INF, [TAILLE_TEXTE], haut), {"flex-grow": 1})
        # la carte de FM (fond, bord, coins, marges intérieures du bloc) : ses classes, en ligne
        # v8 : la carte remplit toute la case du bloc (elle était à la hauteur de son contenu, calée en bas de la case :
        # son haut bougeait d'un joueur à l'autre) ; ce qui ne tient pas défile dans sa place
        # v11 : la place de la carte du joueur (posée par la bande, de la bande au bas du bloc), à gauche ; les
        # conteneurs qui la recouvrent laissent passer la souris (le club, la ville de naissance de la carte)
        # v14 (capture 30, « le minimum d'espace entre le bandeau du haut et les blocs d'en dessous ») : le bloc remonte
        # de JOINTURE, jusqu'à la ligne où le jeu coupe la zone du bloc (10 px sous la bande, rien de plus près)
        zone = boite(t, dans, {"flex-direction": "column", "flex-grow": 1, "flex-shrink": 1, "min-height": 0,
                               "padding-left": CARTE_L + ECART, "margin-top": -JOINTURE}, ["align-self-stretch"])
        for x in {zone, dans, racine}:
            _sans_souris(t, x)
        ligne = boite(t, zone, {"flex-direction": "row", "align-items": "stretch", "flex-grow": 1, "flex-shrink": 1,
                                "min-height": 0, "overflow": "hidden"},
                      [c for c in k.bloc.s.elem(k.carte).get("m_Classes") or []])
        # v3 (maquette 47) : postes (fixe) | notes (sans l'Entraînement) | colonne de droite (le reste)
        _colonne_postes(t, k, ligne, cotes["terrain"], base=POSTES_L)
        _trait(t, k, ligne, True)
        msgs += _tableau(t, k, ligne, largeurs, entrainement=False)
        _trait(t, k, ligne, True)
        # v12 : les sources de la bande, pour la carte du joueur (et v15, option « polygone », pour le rapport)
        if kc is None:
            kc = Sources(t, True)   # son remapper modèle : un de la tuile (il y en a maintenant)
            manque = manquants_carte(kc)
            if manque:
                return msgs + [f"{m} (introuvable)" for m in manque]
            # bloc v19 : « Observer joueur » avec notre gabarit de bouton s'il est dans le jeu (posé par la bande,
            # appliquée AVANT le bloc) ; sinon le gabarit de FM. Voir tuile_gabarit()
            kc.gab_observer = GUID_GABARIT if gabarit_a_jour() else ""
        msgs += _colonne_droite(t, k, ligne, kc)
        # v12 : la carte du joueur, à gauche, dans la place que le bloc lui laisse
        msgs += carte_bas47(t, kc, dans, nom_t)
    # modèles inclus déclarés : ceux qu'on utilise vraiment (le bloc des pieds est recopié), rangés par nom comme chez FM
    alias = {t.elem(r).get("m_TemplateAlias") for r in t.walk()} - {None, ""}
    t.tt["m_Usings"] = sorted((u for u in t.tt["m_Usings"] if u.get("alias") in alias), key=lambda u: u["alias"])
    return msgs


def _composant(t):
    ce = racine_de(t)
    return ce if typ(t, ce).endswith("ComponentElement") else None


def bloc_a_jour(t):
    ce = _composant(t)
    kids = [t.name(x) for x in t.children(ce)] if ce is not None else []
    return NOM_BLOC_AUTRES in kids and NOM_BLOC_LARGE in kids


def tuile_a_jour():
    o = hp.ouvrir(TUILE)
    return o is not None and any(t_name == NOM_TUILE for t_name in (o[3].name(x) for x in o[3].children(
        o[3].tt["m_VisualTree"]["rid"])))


def tuile_gabarit():
    """bloc v19 : la tuile dans le jeu fait-elle prendre NOTRE gabarit de bouton à « Observer joueur » ? (elle doit le
    faire exactement quand le gabarit est dans le jeu : jamais citer le modèle de FM tel quel)"""
    o = hp.ouvrir(TUILE)
    if o is None:
        return False
    s = o[3]
    return any(typ(s, r) == "FM.UI.FMActionButton"
               and (s.sd(r).get("ActionsListWidget") or {}).get("m_AssetGUID") == GUID_GABARIT for r in s.walk())


# ---------- bloc v19 : notre modèle de ligne des phrases Pour / Contre (GABARIT_PHRASE) ----------
class SourcesPhrase:
    """les morceaux de FM du modèle de ligne : la ligne, le texte et l'infobulle du bouton d'action de FM (d'origine)"""
    def __init__(self):
        self.g_liste = Src("ActionsListWidget")
        self.actif_src = Src("GenericActionButtonWidget")
        self.g_donnees = Src("GenericActionButtonDataWidget")
        self.gab = morceaux_gabarit(self.g_liste.s, self.actif_src.s, self.g_donnees.s)

    def manquants(self):
        return [f"modèle de ligne des phrases : {nom}" for nom in ("ligne", "texte", "bulle", "bulle_texte")
                if self.gab.get(nom) is None]


def _nu(t, src, rid, parent, nom=None):
    """un élément d'un modèle de FM d'origine, SANS ses enfants ni son style (on pose les nôtres)"""
    r = t.clone(rid, parent, src=src.s)
    for x in list(t.children(r)):
        t.remove(x)
    no_styles(t, r)
    if nom is not None:
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
    return r


def _lier_texte(t, r, chemin):
    sd = t.sd(r)
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["TextBinding_UxmlAttributeFlags"] = 1
    sd["DebugDisplay"] = chemin


def construire_phrase(t, k):
    """réécrit le modèle t (GABARIT_PHRASE, cité par rien) en ligne d'une phrase Pour / Contre : la ligne
    (PASTILLE_ALEX_PAS de haut : en face de la pastille d'Alex ; elle prend la souris), la phrase (« … ») et
    l'infobulle de FM à plat avec la phrase entière (comme les lignes de la v16)"""
    g, sd_ = k.gab, k.g_donnees
    racine = t.tt["m_VisualTree"]["rid"]
    for x in list(t.children(racine)):
        t.remove(x)
    ligne = _nu(t, sd_, g["ligne"], racine, NOM_PHRASE)
    t.elem(ligne)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.styles.style(t, ligne, {"height": PASTILLE_ALEX_PAS, "min-height": PASTILLE_ALEX_PAS,
                              "max-height": PASTILLE_ALEX_PAS, "flex-shrink": 0, "flex-grow": 0, "min-width": 0,
                              "overflow": "hidden", "align-self": "stretch"})
    t.sd(ligne)["pickingMode"], t.sd(ligne)["pickingMode_UxmlAttributeFlags"] = 0, 1
    tx = _nu(t, sd_, g["texte"], ligne)
    _lier_texte(t, tx, CHEMIN_PHRASE)
    t.elem(tx)["m_Classes"] = ["body-sm", "global-text-primary", "content-no-wrap", "content-ellipsis"]
    t.styles.style(t, tx, {"flex-shrink": 1, "min-width": 0, "max-width": {"unit": 2, "value": 100.0}})
    _sans_clic(t, tx)
    bu = _gab_copie(t, sd_, g["bulle"], ligne)
    lab = _gab_copie(t, sd_, g["bulle_texte"], bu)
    _lier_texte(t, lab, CHEMIN_PHRASE)
    return [f"{GABARIT_PHRASE} : notre ligne des phrases Pour / Contre (bloc v{VERSION_BLOC})"]


def phrase_a_jour():
    o = hp.ouvrir(GABARIT_PHRASE)
    return o is not None and any(o[3].name(x) == NOM_PHRASE for x in o[3].children(o[3].tt["m_VisualTree"]["rid"]))


def retirer_phrase():
    o = ouvrir_modele(GABARIT_PHRASE)
    if o is None or not any((o[3].name(x) or "").startswith(PREFIXE_BLOC) for x in o[3].walk()):
        return []
    orig = ouvrir_modele(GABARIT_PHRASE, original=True)
    if orig is None:
        return [f"{GABARIT_PHRASE} : pas de sauvegarde d'origine, laissé"]
    enregistrer(*orig, modele=GABARIT_PHRASE)
    return [f"{GABARIT_PHRASE} : remis d'origine"]


def bloc_retirer(t):
    """nos deux SIVisible enlevés, l'élément de FM remis à sa place ; True si quelque chose était posé"""
    ce = _composant(t)
    fait = False
    for x in [x for x in (t.children(ce) if ce is not None else []) if t.name(x).startswith(PREFIXE_BLOC)]:
        i = t.children(ce).index(x)
        if t.name(x) == NOM_BLOC_AUTRES:
            for j, y in enumerate(list(t.children(x))):
                move(t, y, ce, i + j)
        t.remove(x)
        fait = True
    us = t.tt.get("m_Usings") or []
    if any(u.get("alias") == TUILE for u in us):
        t.tt["m_Usings"] = [u for u in us if u.get("alias") != TUILE]
        fait = True
    return fait


def bloc_poser(t, k):
    ce = _composant(t)
    carte = next((x for x in t.children(ce) if typ(t, x).endswith("ExpandableContentElement")), None) \
        if ce is not None else None
    if carte is None:
        return [f"{BLOC} : élément de FM du bloc (ExpandableContentElement) introuvable"]
    b = k.s_vis.sd(k.vis)["Binding"]
    i = t.children(ce).index(carte)
    # données du SIVisible de FM telles quelles (pas de style, drapeaux d'origine) : les fonctions d'Alex qui recopient
    # « le 1er SIVisible » du bloc (hors_defaut, make_visible) tombent sur le nôtre et en font la même copie qu'avant
    autres = ni.new_visible(t, k.s_vis, k.vis, ce, i, NOM_BLOC_AUTRES, ni.make_binding(b, OP_SUP, [MODE], 0),
                            ["flex-grow-class", "align-self-stretch"])
    move(t, carte, autres)
    large = ni.new_visible(t, k.s_vis, k.vis, ce, i + 1, NOM_BLOC_LARGE, ni.equal_binding(b, MODE, 0),
                           ["flex-grow-class", "align-self-stretch"])
    # notre modèle, inclus (un modèle inclus de FM recopié : son alias et son modèle changés)
    inst = t.clone(k.trait_v, large, src=k.bloc.s)
    e = t.elem(inst)
    e["m_TemplateAlias"], e["m_SerializedDataOverride"], e["m_RuleIndex"] = TUILE, [], -1
    e["m_Classes"] = ["flex-grow-class", "align-self-stretch"]
    sd = t.sd(inst)
    sd["name"], sd["templateId"], sd["templateId_UxmlAttributeFlags"] = "", TUILE, 1
    # déclaré à la fin (comme Alex) : l'ordre des autres ne bouge pas, le retrait rend la liste telle quelle
    us = [u for u in t.tt.get("m_Usings") or [] if u.get("alias") != TUILE]
    us.append({"alias": TUILE, "path": GUID_TUILE, "asset": {"m_FileID": 0, "m_PathID": 0}})
    t.tt["m_Usings"] = us
    return []


def ouvrir_modele(modele, original=False):
    if original:
        return hp.ouvrir(modele, depart_original=True)
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    return bundle, obj, tt, t


def appliquer_bloc():
    """(changé, messages) : notre bloc dans la tuile, et le grand bloc qui l'inclut en Large"""
    ob = ouvrir_modele(BLOC)
    if ob is None or _composant(ob[3]) is None:
        return False, [f"{BLOC} : introuvable ou inattendu, rien n'est changé"]
    # bloc v19 : aussi notre modèle de ligne des phrases, et « Observer joueur » avec notre gabarit exactement quand
    # il est dans le jeu (la bande, appliquée avant, a pu le poser ou le retirer)
    if bloc_a_jour(ob[3]) and tuile_a_jour() and phrase_a_jour() and tuile_gabarit() == gabarit_a_jour():
        return False, [f"{BLOC} : déjà appliqué (bloc v{VERSION_BLOC})"]
    k = SourcesBloc()
    kp = SourcesPhrase()
    m = k.manquants() + kp.manquants()
    if m:
        return False, [f"grand bloc : morceaux de FM introuvables ({', '.join(m)}), rien n'est changé"]
    otu = ouvrir_modele(TUILE, original=True)
    if otu is None:
        return False, [f"{TUILE} : introuvable, rien n'est changé"]
    op = ouvrir_modele(GABARIT_PHRASE, original=True)
    if op is None:
        return False, [f"{GABARIT_PHRASE} : introuvable ou sans sauvegarde d'origine, rien n'est changé"]
    msgs = construire_phrase(op[3], kp)
    msgs += construire_tuile(otu[3], k)
    tb = ob[3]
    bloc_retirer(tb)
    base = len(tb.styles.sh["m_Rules"])
    msgs += bloc_poser(tb, k)
    retirer_regles(tb, range(base, len(tb.styles.sh["m_Rules"])))
    if any("introuvable" in x for x in msgs):
        return False, msgs + ["grand bloc : rien n'est changé"]
    enregistrer(*op, modele=GABARIT_PHRASE)   # bloc v19 : AVANT la tuile, qui le cite
    enregistrer(*otu, modele=TUILE)
    enregistrer(*ob, modele=BLOC)
    return True, msgs + [f"{BLOC} : notre bloc en 1080p Large ({len(TAILLES_BLOC)} tailles du texte, modèle {TUILE}) ; "
                         f"en Moyen / Petit, celui qui y était, tel quel"]


def retirer_bloc():
    msgs = []
    ob = ouvrir_modele(BLOC)
    if ob is not None and bloc_retirer(ob[3]):
        enregistrer(*ob, modele=BLOC)
        msgs.append(f"{BLOC} : notre bloc retiré (celui qui y était est remis tel quel)")
    otu = ouvrir_modele(TUILE)
    if otu is not None and any(otu[3].name(x).startswith(PREFIXE_BLOC) for x in otu[3].walk()):
        orig = ouvrir_modele(TUILE, original=True)
        if orig is None:
            msgs.append(f"{TUILE} : pas de sauvegarde d'origine, laissé")
        else:
            enregistrer(*orig, modele=TUILE)
            msgs.append(f"{TUILE} : remis d'origine")
    return msgs + retirer_phrase()


# ---------- commandes ----------
def appliquer_entete():
    """la bande (étape 1) ; True si quelque chose est à enregistrer"""
    o = ouvrir_entete()
    if o is None:
        print(f"{MODELE} : introuvable, rien n'est changé")
        return False
    t = o[3]
    if place_1080p(t) is None:
        print(f"{MODELE} : aiguillage 1080p de FM (UseStandard) introuvable (mise à jour de FM ?) ; rien n'est changé")
        return False
    if a_jour(t) and drapeau_a_jour() and gabarit_a_jour() and icones_a_jour():
        print(f"{MODELE} : déjà appliqué (v{VERSION})")
        return False
    ok, msgs = poser_drapeau()
    for m in msgs:
        print(f"drapeau : {m}")
    k = Sources(t, ok)
    m = k.manquants()
    if m:
        print(f"en-tête Large : morceaux de FM introuvables ({', '.join(m)}), rien n'est changé")
        return False
    # v13 : notre gabarit de bouton d'action, refait depuis l'ORIGINAL du modèle (cité par rien) : AVANT la bande, qui
    # le cite ; sans lui, rien n'est changé (la bande ne doit jamais citer le modèle de FM tel quel)
    og = ouvrir_modele(GABARIT_BOUTON, original=True)
    if og is None:
        print(f"{GABARIT_BOUTON} : introuvable ou sans sauvegarde d'origine, rien n'est changé")
        return False
    for x in construire_gabarit(og[3], k):
        print(x)
    # v15 : les deux gabarits de boutons-icônes (case du contrat), pareil
    icones = []
    for cle, (modele, _guid, classe) in GABARITS_ICONES.items():
        oi = ouvrir_modele(modele, original=True)
        if oi is None:
            print(f"{modele} : introuvable ou sans sauvegarde d'origine, rien n'est changé")
            return False
        for x in construire_gabarit(oi[3], k, icone=classe, cle=cle):
            print(x)
        icones.append((oi, modele))
    retirer_regles(t, retirer_tout(t))   # une ancienne version d'abord (v1-v4 : dans la tuile d'Alex)
    base = len(t.styles.sh["m_Rules"])
    msgs = poser(t, k, place_1080p(t)) + poser_photo(t, k)
    # style() d'Alex crée toujours une NOUVELLE règle (l'ancienne reste, orpheline) : nos orphelines (après base)
    # enlevées tout de suite, pour qu'au retrait toutes nos règles partent avec nos références (v1 : 36 restaient)
    retirer_regles(t, range(base, len(t.styles.sh["m_Rules"])))
    for x in dict.fromkeys(msgs):
        print(f"{MODELE} : {x}")
    if any("introuvable" in x for x in msgs):
        print(f"{MODELE} : rien n'est changé")
        return False
    enregistrer(*og, modele=GABARIT_BOUTON)
    for oi, modele in icones:
        enregistrer(*oi, modele=modele)
    enregistrer(*o)
    print(f"{MODELE} : notre bande en 1080p Large ({len(TAILLES_TEXTE)} tailles du texte) ; ailleurs, ce qui y était "
          f"(tuile d'Alex ou en-tête de FM) tel quel"
          + ("" if ok else " ; nation avec le logo de FM (fonction du drapeau pas posée)"))
    return True


def cmd_appliquer():
    change = appliquer_entete()
    ok, msgs = appliquer_bloc()
    for x in dict.fromkeys(msgs):
        print(x)
    if change or ok:
        nb.save_all()
    _marquer()


def cmd_retirer(silencieux=False):
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rien = True
    o = ouvrir_entete()
    if o is not None:
        t = o[3]
        avant = len(t.tt["references"]["RefIds"])
        enleves = retirer_tout(t)
        if len(t.tt["references"]["RefIds"]) != avant:
            retirer_regles(t, enleves)
            enregistrer(*o)
            print(f"{MODELE} : notre bande retirée (ce qui y était est remis tel quel)")
            rien = False
    for m in retirer_drapeau() + retirer_bloc() + retirer_gabarit():
        print(m)
        rien = False
    if rien:
        if not silencieux:
            print("rien à retirer")
        return
    nb.save_all()


def cmd_etat():
    o = ouvrir_entete()
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        sw = place_1080p(t)
        if sw is None:
            print(f"{MODELE} : aiguillage 1080p de FM introuvable")
        else:
            pl = t.children(sw)[0]
            ici = t.name(pl) == NOM_PLACE
            noms = sorted({t.name(x) for x in t.children(pl)} - {NOM_AUTRES}) if ici else []
            dedans = t.children(next(x for x in t.children(pl) if t.name(x) == NOM_AUTRES))[:1] if ici else [pl]
            print(f"{MODELE} : " + (f"à jour, v{VERSION}" if a_jour(t) else
                                    f"ANCIENNE version ({', '.join(noms)})" if ici else
                                    "v1-v4 (dans la tuile d'Alex)" if anciens(t) else "pas posée"))
            print("  en Moyen / Petit, à cette place :", ", ".join(t.name(x) or t.elem(x).get("m_TemplateAlias") or "?"
                                                         for x in dedans))
            print("  photo de FM :", "cachée par la tuile d'Alex" if CACHE_ALEX in ancetres(
                t, first(t, lambda r: t.name(r) == PHOTO) or -1) else "cachée en 1080p Large (nous)" if photo_ok(t)
                else "visible partout")
    print(f"fonction du drapeau ({NOM_CIBLE}) :", "posée" if drapeau_a_jour() else "d'origine")
    og = ouvrir_modele(GABARIT_BOUTON)
    print(f"gabarit des boutons ({GABARIT_BOUTON}) :", "introuvable" if og is None else "à jour" if gabarit_a_jour()
          else "ANCIENNE version" if any(og[3].name(x).startswith(PREFIXE) for x in og[3].walk()) else "d'origine")
    for cle, (modele, _guid, _classe) in GABARITS_ICONES.items():
        oi = ouvrir_modele(modele)
        print(f"gabarit du bouton-icône « {cle} » ({modele}) :", "introuvable" if oi is None
              else "à jour" if gabarit_a_jour(modele, nom_icone(cle))
              else "ANCIENNE version" if any((oi[3].name(x) or "").startswith(PREFIXE) for x in oi[3].walk())
              else "d'origine")
    ob = ouvrir_modele(BLOC)
    if ob is None:
        print(f"{BLOC} : introuvable")
    else:
        tb = ob[3]
        ce = _composant(tb)
        noms = [tb.name(x) for x in tb.children(ce)] if ce is not None else []
        print(f"{BLOC} : " + (f"à jour, bloc v{VERSION_BLOC}" if bloc_a_jour(tb) and tuile_a_jour() else
                              f"ANCIENNE version ({', '.join(n for n in noms if n.startswith(PREFIXE_BLOC))})"
                              if any(n.startswith(PREFIXE_BLOC) for n in noms) else "pas posé"))
        print(f"  {TUILE} :", "notre bloc" if tuile_a_jour() else "d'origine ou ancienne version")
        print("  « Observer joueur » :", "notre gabarit de bouton" if tuile_gabarit() else "gabarit de FM")
    op = ouvrir_modele(GABARIT_PHRASE)
    print(f"ligne des phrases ({GABARIT_PHRASE}) :", "introuvable" if op is None else "à jour" if phrase_a_jour()
          else "ANCIENNE version" if any((op[3].name(x) or "").startswith(PREFIXE_BLOC) for x in op[3].walk())
          else "d'origine")
    print("réapplication automatique (choix 1) :", "oui" if os.path.exists(MARKER) else "non")


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
            print("en-tête Large : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
