"""[AJOUT KINITO] 26.23 — Tactiques > Vue d'ensemble : les sélections d'équipe sauvegardées en boutons, à gauche de
« Filtre », au-dessus du tableau des joueurs. Un clic charge la sélection, comme Sélect. rapide > Gérer sélection
d'équipe > Utiliser sélection X.

Demande de Kinito (14/11/2026, captures de l'écran Tactiques) : « Il y a la possibilité dans le jeu de faire des
sélections de joueurs [...] et sauvegarder cette sélection. Serait-il possible ensuite d'avoir un raccourci qui
s'affiche à côté de Filtre avec les sélections sauvegardées ? » Ses choix (14/11) : NOTRE ajout (Alex a un essai
voisin, essai_raccourcis_selections : 5 boutons « 1 » à « 5 » à droite de Sélect. rapide, jamais vu en jeu ; Kinito le
prévient), le NOM de chaque sélection sur son bouton, les 5 PREMIÈRES au plus, rien PENDANT UN MATCH.

Ce que dit le jeu (lu le 14/11/2026 dans ses données et son code) :
- LA LISTE : `tactic.TeamSelections` (FM.UI.TacticReference, aucun contexte exigé : TacticReference::GetContextsInternal
  ne la cite pas) ; c'est elle que montre la fenêtre « Gérer sélection » de FM (TacticsManageTeamSelection, une
  StreamedObjectList de SaveLineupRow, dont le texte est `row.DisplayValue` : le nom de la sélection). Une sélection
  sauvegardée, supprimée ou renommée la change : nos boutons la suivent par liaison, sans rien réinstaller (à voir en
  jeu).
- LE CLIC : aucun bouton de FM n'envoie l'événement du moteur EventFmxSelectTeamSelection (1349539155, InteropEventIDs ;
  « Supprimer » et « Renommer » de Gérer sélection envoient EventFmxDelete/RenameTeamSelection avec la ligne choisie).
  Il ne part que par le menu Sélect. rapide : une liste d'actions « SpeakTo » (Tactic.SpeakTo.Actions.ActionsForDropdown,
  FM.UI.SpeakToActionsReference) dont l'action « Gérer sélection d'équipe » a un sous-menu (SubmenuActionsList) ; le
  choix d'une ligne envoie l'événement du menu (SelectionEvents du dropdown de TacticalPlannerSpeakToActions) avec les
  champs de l'action choisie (SelectedAction.*). Valeurs des entrées « Utiliser sélection » (Alex, 13/11, mod diag) :
  Event = 1349539155, ActionResponseValue = le RANG de la sélection (0, 1, 2…).
- v1 (14/11, VUE EN JEU : FM SE FERMAIT AU CLIC) : l'événement recopié avec des valeurs fixes et le chemin « null »
  pour les champs vides. Player.log : « InvalidCastException: Unable to cast object of type 'NullReference' to type
  'DynamicReference' » dans FM.UI.SpeakToActionEventContext.<OnSetup>b__41_8 (SpeakToActionEvent.cs:306). Désassemblé :
  OnSetup lie chaque champ de l'événement et le lit SANS tolérer le vide — ActionData, ActionProps, ConfirmationDialog-
  Data, OKDialogData par Get<DynamicReference>, ActionDataReferences par Get<List<TypedValue>> ; seul le 1er (NPC)
  essaie (TryGet<PersonReference>). Une valeur fabriquée ne convient donc pas.
- v2 : LES VRAIES ACTIONS DU MENU. SubmenuActionsList est une propriété liable de l'action (FM la lie lui-même :
  SpeakToOptionalActionButton, StreamedObjectList #SubActions path=action.SubmenuActionsList). On lit les 8 premières
  actions de Tactic.SpeakTo.Actions.ActionsForDropdown et leurs 8 premières sous-entrées (« élément n s'il existe »),
  et le bouton de la sélection n est celui de la seule sous-entrée dont Event = 1349539155 ET ActionResponseValue = n
  (deux SIVisible BindIntToVisible imbriqués ; leur graphe : TryCastToInt, puis Compare ; une valeur absente vaut 0,
  sans exception ; l'extérieur cache l'intérieur, donc « rang = 0 » n'est jugé que sur une entrée « Utiliser »).
  Candidates : les 8 actions, sous-entrées n + 1 à n + 3 (au menu : Sauvegarder, Gérer sélection, puis Utiliser 1,
  Utiliser 2…). Le clic envoie l'événement du menu, « SelectedAction. » remplacé par cette sous-entrée : exactement ce
  qu'envoie FM quand on choisit la ligne. Aucune entrée trouvée : pas de bouton (jamais d'erreur).
  SUPPOSÉ, À VOIR EN JEU : le nom (rang n de tactic.TeamSelections) est celui de la sélection que charge l'entrée de
  rang n du menu.
- v3 (relevé F7, sonde 0.28.2, 14/11) : la v2 posée n'a montré AUCUN bouton. Les lignes de ActionsForDropdown sont des
  enveloppes { RowData = l'action } : c'est RowData qui porte SubmenuActionsList. Chemin corrigé :
  ActionsForDropdown[i].RowData.SubmenuActionsList[j] ; chaque sous-entrée essayée telle quelle et par « .RowData »
  (240 boutons candidats). Relevé du même F7 : kinitoselnb = 2, tactic.TeamSelections = { « 1 », rang 0 } et
  { « 2 », rang 1 } (DisplayValue, Value).
- v4 (2e relevé F7, 14/11 14:16, la v3 posée : AUCUN bouton) : TOUTES les listes RowData.SubmenuActionsList sont VIDES
  (« [0 : ] »), y compris celle de « Gérer sélection d'équipe » (ligne 4), même après avoir ouvert le sous-menu : le
  jeu construit les sous-menus du menu Sélect. rapide dans son code (Alex avait raison sur ce point). Les vraies
  entrées « Utiliser sélection N » sont hors de portée d'un skin. Retour aux valeurs FIXES (celles d'Alex), mais
  chacune DU TYPE que lit le jeu (v1 : les champs entiers et booléens étaient passés, le plantage venait seulement des
  « null ») :
    · Event 1349539155, RejectConfirmationEvent 0, ActionResponseValue n, ActionResponseId -1, ActionID 0,
      NewsAction -1, DynamicCardId -1 : entiers ; IsExitButton, IsContinueMatchFlowButton : faux ;
    · ActionData, ActionProps, ConfirmationDialogData (ConfirmationStrings du jeu), OKDialogData (OkStrings) : une
      RÉFÉRENCE VIDE, déclarée comme FM la déclare (ValueVariable « DynamicReferenceScopeValue, m_data [] », recopiée de
      specificDate de CompetitionSiteFixturesTile_4x4) : vide, donc aucune fenêtre de confirmation ;
    · ActionDataReferences : une LISTE VIDE, Tactic.SpeakTo.Actions.ActionsForDropdown[0].RowData.SubmenuActionsList (vue
      vide et de type List<TypedValue> dans les deux relevés). Garde : la zone ne montre ses boutons que si cette liste
      existe (BindAndSetAOrBToDestinationUsingReferenceIsNullAsBool 079b54af de ViewedFixtureTooltip, vue en jeu dans
      26.9 : jamais de lecture d'une référence vide) — sans elle, pas de bouton, jamais de plantage.
- v5 (3e relevé F7, 14/11 14:36 ; la v4 posée : les boutons « 1 » et « 2 » s'affichent mais GRISÉS, FM ne se ferme
  plus) : `kinitoselvide` n'a AUCUNE valeur (une ValueVariable DynamicReferenceScopeValue à m_data vide ne crée rien) ;
  un bouton de FM reste grisé tant qu'une valeur de son événement manque (SIButton.UpdateSetupState -> SetEnabled selon
  l'état de ses événements, désassemblé). Les quatre champs « référence » sont pris sur une VRAIE action : la ligne
  d'en-tête « Sélect. rapide » (ActionsForDropdown[0].RowData.ActionData, .ActionProps, .ConfirmationDialogData,
  .OKDialogData : des DynamicReference dans les relevés), une garde 079b54af par champ. À VÉRIFIER AVANT LE 1er CLIC
  (sonde 0.28.3, F7 : contenu de ces références) : vides, sinon une fenêtre de confirmation pourrait s'ouvrir.

- v6 (Alex, 14/11, VU chez Alex : boutons « 1, 2, M, M1, M2 » à gauche de Filtre) : la zone passe À DROITE DE
  SÉLECT. RAPIDE (comme l'essai d'Alex), dernière de la rangée #DropdownMode de TacticalPlannerSpeakToActions (cité
  par TacticalPlannerHeader seul ; modèle qui reçoit SpeakTo et Tactic : mêmes chemins qu'avant). Les pièces de
  « Filtre » (SIVisible hors match, texte, classes, #StoppageVisible) sont lues dans l'ORIGINAL de
  TacticalPlannerTeamShapeTableTemplate, d'où l'ancienne zone est retirée. Boutons espacés à GAUCHE, 120 px au plus.
  Barre réactive : « élément n » en ForceUpdate (comme le nombre), pour qu'une sélection sauvegardée ou renommée
  apparaisse sans changer d'écran.

Comment (tout recopié de FM, fonctions lues dans leur graphe avant d'écrire leurs arguments) :
- L'ÉCRAN : TacticalPlannerTeamShapeTableTemplate (gameworld), cité par TacticalPlannerTeamShape seul (vérifié dans
  les données décompressées de tous les bundles : guid_cite.py), touché par aucune fonction d'Alex ni ajout Kinito.
  Sa rangée #Top : [menu des vues « Condition physique »] [changements / arrêts de jeu en match] [SIVisible « hors
  match » (tactic.IsDuringMatch inversé) > « Filtre »]. Notre zone se pose juste avant ce dernier, et prend la place
  libre (flex-grow) en rangeant ses boutons à droite : collés à « Filtre ».
- RIEN EN MATCH : notre zone est une copie du SIVisible de « Filtre » (même condition : caché pendant un match).
- LES VARIABLES (v4) : une BindingSetter de FM (SearchBindingsSetter de GlobalSearchCard, vidée, comme 26.18) déclare
  le nombre de sélections (kinitoselnb), les 5 premières (kinitosel0…4) et la 1re ligne du menu (kinitoqa0) :
  références nulles au départ ; les valeurs fixes de l'événement et les gardes (kinitosellisteok, kinitoselref<k>ok :
  v5) ; elle calcule :
    · le nombre : BindListItemsCountToInt (2fe07f5c ; entrées : SourceBinding, Destination, ForceUpdate), recopiée de
      FinancesDebtsAndLoansBlock_8x3 (comme 26.21, vue en jeu) ;
    · la sélection n : BindListItemUsingIndexToDestinationIfNotNull (1f968d66, la variante « s'il existe » de 21ee6b43
      de TransferBlockMainFrame, mêmes entrées : liste, destination, rang… ; un rang absent ne pose rien, comme 26.18,
      vue en jeu).
- UN BOUTON PAR SÉLECTION (v4) : sous la garde (kinitosellisteok = 1), un SIVisible « nombre > n » (BindIntToVisible
  d52cf0b2, recopiée de #StoppageVisible du même modèle ; entrées : opérateur, entier, clé, chemin ; graphe :
  TryCastToInt puis Compare, une valeur absente vaut 0), dedans un SIButton de FM (celui de Sélect. rapide) à l'allure
  de « Filtre » (ses classes de FM), clic = l'événement du menu réécrit, texte = le SIText de « Filtre » passé en
  liaison directe sur kinitosel<n>.DisplayValue. Un SIVisible caché ne relie pas ses enfants et ne prend pas de place.
  SUPPOSÉ, À VOIR EN JEU : ActionResponseValue = n charge la sélection de rang n (Alex), et c'est celle dont le nom est
  au rang n de tactic.TeamSelections (relevé : « 1 » rang 0, « 2 » rang 1).

Usage (jeu fermé) :
  python outils\\kinito\\kinito_raccourcis_selections.py appliquer [--dry-run]
  python outils\\kinito\\kinito_raccourcis_selections.py retirer [--dry-run]
  python outils\\kinito\\kinito_raccourcis_selections.py etat
  python outils\\kinito\\kinito_raccourcis_selections.py si-actif
"""
import copy
import json
import os
import struct
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
NOMBRE = 10                # Kinito (14/11) : 5 au plus ; Alex (14/11, v7) : 10
ECART = 8                  # px entre deux boutons (en haut : avant chacun ; à gauche de Filtre : après chacun)
LARGEUR_MAX = {"haut": 120, "filtre": 180}   # px : un nom plus long finit en « … » (en haut, la rangée est partagée)
# =====================================================================================================

# v8 (Alex, 14/11) : option de l'app (commun\options.py) « selections_emplacement » : « haut » (de base, à droite de
# Sélect. rapide) ou « filtre » (la place de Kinito, v1-v5 : à gauche de Filtre, au-dessus du tableau)
OPTION = "selections_emplacement"
OPTION_VALEURS = ("haut", "filtre")


def _emplacement():
    force = os.environ.get("KINITO_OPTION_SELECTIONS")   # essais sur copies (bancs) : la valeur imposée
    if force in OPTION_VALEURS:
        return force
    try:
        import options
        return options.get(OPTION)
    except Exception:   # l'option n'est pas (encore) dans l'app
        return "haut"


EMPLACEMENT = _emplacement()
EN_HAUT = EMPLACEMENT != "filtre"
VERSION = "11" if EN_HAUT else "11-filtre"   # dépend de l'option (sinon « déjà appliqué ») ; v9 : speakto de l'écran
#                                              (Effectif) ; v10 : DIAG ; v11 : DIAG coupé (VALIDÉ partout, 2026-11-14)
# DIAG (v10, Effectif seulement) : repères « Z V N L 0 1 2 3 » après chaque condition (zone hors match, variables, au
# moins 1 sélection, liste vide, 4 références). Relevé : N absent = équipe sans tactique (Sélect. rapide grisé), normal
DIAG = False
# v7 (Alex) : 10 boutons au lieu de 5 ; v1 (14/11) : FM se fermait au clic (champs « null ») ; v2 et v3 : les vraies
# actions du menu (aucun bouton, vu en jeu : le jeu ne les donne à aucune liaison) ; v4 : valeurs fixes typées, mais la
# référence vide n'avait pas de valeur (boutons grisés, vu en jeu) ; v5 : références de la ligne d'en-tête ;
# v6 (Alex) : à droite de Sélect. rapide, noms en ForceUpdate ; v8 : option d'emplacement
MODELE_HAUT = "TacticalPlannerSpeakToActions"              # la rangée de Sélect. rapide (#DropdownMode)
MODELE_FILTRE = "TacticalPlannerTeamShapeTableTemplate"    # la rangée #Top de « Filtre » ; ses pièces (original)
MODELE = MODELE_HAUT if EN_HAUT else MODELE_FILTRE         # où poser
AUTRE = MODELE_FILTRE if EN_HAUT else MODELE_HAUT          # d'où retirer
RANGEE = "DropdownMode"
# v8 (le joueur, 14/11) : aussi sur les écrans Effectif (Joueurs, Vue d'ensemble), toujours à droite de leur Sélect.
# rapide : chacun a son propre menu (BindingVariables #QuickPick : bouton + flèche, en rangée ; reçoit Tactic).
# Propriétaires de ces modèles (repartent de l'original) : effectif_boutons_entrainement (TeamSquadBlock),
# effectif_equipes (SquadOverviewTableBlock) -> ORDRE_SKIN après eux + SUIVANTS
MODELES_EFFECTIF = ("TeamSquadBlock", "SquadOverviewTableBlock")
RANGEE_EFFECTIF = "QuickPick"
PREFIXE = "UIPickerKinito-raccourcis-sel"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_raccourcis_selections.actif")

LISTE = "Tactic.TeamSelections"            # les sélections sauvegardées (FM.UI.TacticReference)
CHEMIN_NOM = "DisplayValue"                # le nom d'une sélection (SaveLineupRow : row.DisplayValue)
SPEAKTO = "Tactic.SpeakTo"                 # le « SpeakTo » de l'événement du menu (BindingRemapper de TacticalPlannerHeader)
ACTIONS_SOUS = "Actions.ActionsForDropdown"            # les lignes du menu Sélect. rapide (SpeakToActionsReference)
ACTIONS = f"{SPEAKTO}.{ACTIONS_SOUS}"
SPEAKTO_EFFECTIF = "speakto"   # v8 : écrans Effectif, le speakTo de l'écran (BindingRemapper speakto:tactic-speakto,
#                                celui de leur menu Sélect. rapide) ; Tactic.SpeakTo n'y est peut-être pas rempli
# v3 (relevé F7 de la sonde 0.28.2, 14/11 14:08) : chaque ligne de ActionsForDropdown est une ENVELOPPE
# DynamicReference { RowData = l'action } ; c'est l'action qui porte SubmenuActionsList (code 3543446C), Event (43
# pour la ligne « Sélect. rapide »), ActionData… (des DynamicReference, ActionDataReferences une liste). La v2 lisait
# SubmenuActionsList sur l'enveloppe : vide, aucun bouton. Les 7 lignes chez Kinito : Sélect. rapide, Choisir sans
# restriction, Faire tourner l'effectif, Choisir jeunes prometteurs, Gérer sélection d'équipe, Choisir rôles, Effacer.
LIGNE_ACTION = "RowData"                   # l'action d'une ligne du menu (enveloppe du dropdown)
SOUS_MENU = "SubmenuActionsList"           # les sous-entrées d'une action : TOUJOURS une liste vide (2e relevé F7, v4)
EVENEMENT_UTILISER = 1349539155            # InteropEventIDs.EventFmxSelectTeamSelection (= Event des entrées du menu)
OPERATEUR_EGAL = 2

# nos variables (déclarées par notre BindingSetter, vues par ses enfants)
V_NB = "kinitoselnb"
V_SEL = "kinitosel{}"
V_LIGNE0 = "kinitoqa0"                     # la 1re ligne du menu (« Sélect. rapide »)
LISTE_VIDE = f"{V_LIGNE0}.{LIGNE_ACTION}.{SOUS_MENU}"   # une vraie liste vide (List<TypedValue>), pour ActionDataReferences
V_LISTE_OK = "kinitosellisteok"            # vrai si LISTE_VIDE existe (la garde)
V_RANG = "kinitoselrang{}"
V_EV, V_MOINS1, V_ZERO, V_FAUX = "kinitoselev", "kinitoselmoins1", "kinitoselzero", "kinitoselfaux"
# v5 (3e relevé F7, 14/11 14:36, la v4 posée : boutons GRISÉS, FM ne se ferme plus) : la référence vide de la v4
# (ValueVariable DynamicReferenceScopeValue, m_data []) n'a AUCUNE valeur dans le jeu ; le bouton de FM reste grisé tant
# qu'une valeur de son événement manque (SIButton.UpdateSetupState -> SetEnabled selon l'état de ses événements). Les
# champs « référence » sont pris sur une VRAIE action du jeu, la ligne d'en-tête « Sélect. rapide » du menu
# (ActionsForDropdown[0].RowData : ses ActionData, ActionProps, ConfirmationDialogData, OKDialogData sont des
# DynamicReference, vues dans les relevés), chacun gardé (pas de bouton s'il manque)
REF_LIGNE0 = f"{V_LIGNE0}.{LIGNE_ACTION}"
CHAMPS_REF = ("ActionData", "ActionProps", "ConfirmationDialogData", "OKDialogData")
V_REF_OK = "kinitoselref{}ok"              # vrai si le champ de la ligne d'en-tête existe (une garde par champ)
# champ de l'action (SelectedAction.<champ> dans l'événement du menu) -> notre chemin, de son type ;
# « actionresponsevalue » : le rang, propre à chaque bouton
CHAMPS = {"event": V_EV, "rejectconfirmationevent": V_ZERO, "actionresponseid": V_MOINS1, "actionid": V_ZERO,
          "newsaction": V_MOINS1, "actiondatareferences": LISTE_VIDE, "dynamiccardid": V_MOINS1,
          "isexitbutton": V_FAUX, "iscontinuematchflowbutton": V_FAUX,
          **{c.lower(): f"{REF_LIGNE0}.{c}" for c in CHAMPS_REF}}
SOURCE_NUL, FONCTION_NUL = "ViewedFixtureTooltip", "079b54afdf49eb242aba84c36407187b"   # A ou B selon référence nulle
# chemins attendus dans l'événement du menu, dans l'ordre (relevé le 14/11 ; sinon on ne pose rien)
CHEMINS_MENU = ["null", "SpeakTo", "SelectedAction.Event", "SelectedAction.RejectConfirmationEvent",
                "SelectedAction.ActionResponseValue", "SelectedAction.ActionResponseId", "SelectedAction.ActionID",
                "SelectedAction.ActionData", "SelectedAction.ActionProps", "SelectedAction.NewsAction",
                "SelectedAction.ActionDataReferences", "SelectedAction.DynamicCardId", "SelectedAction.IsExitButton",
                "SelectedAction.ConfirmationDialogData", "SelectedAction.OKDialogData",
                "selectedaction.IsContinueMatchFlowButton"]

# pièces de FM (toutes du bundle gameworld, lues dans leur ORIGINAL)
SOURCE_MENU = "TacticalPlannerSpeakToActions"      # l'événement du menu Sélect. rapide et son SIButton (#button)
SOURCE_CALCUL, NOM_CALCUL = "GlobalSearchCard", "SearchBindingsSetter"   # une BindingSetter (variables + fonctions)
FONCTION_SOMME = "a82e4cf3a34b1ae41b85cacd4f63208c"   # sa fonction (reconnaissance seulement : on la remplace)
SOURCE_NOMBRE, FONCTION_NOMBRE = "FinancesDebtsAndLoansBlock_8x3", "2fe07f5cee1e6af4591dac596a720725"
SOURCE_ELEMENT, FONCTION_ELEMENT = "TransferBlockMainFrame", "21ee6b430323a494099e32901c5497cb"
FONCTION_ELEMENT_SI = "1f968d66d61c9a443ae9625b7a6ef5e3"   # BindListItemUsingIndexToDestinationIfNotNull
FONCTION_VISIBLE_ENTIER = "d52cf0b2ba55c764b9ecda52092aa257"   # BindIntToVisible (#StoppageVisible de ce modèle)
OPERATEUR_SUPERIEUR = 4                                        # ComparisonOperator : < 0, <= 1, = 2, >= 3, > 4, != 5

CHEMIN_ARG = b"GenericVisualArg`1[SI.Bindable.BindingPath]"
for _k, _v in {"flex-direction": (131083, 7), "justify-content": (131088, 7), "align-items": (131073, 7),
               "margin-right": (131092, 3), "margin-left": (131091, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


# ---------- petits outils ----------
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
    return bytes([1]) + _enc_varint(len(b)) + b


_REGLES = {}   # (id de la feuille, style) -> n° de règle : un même style = une seule règle (v2 : ~360 éléments)


def style_partage(t, r, css):
    """style intégré de r (qui n'a pas de règle à lui) : la règle déjà faite pour ce même style, sinon une neuve"""
    cle = (id(t.styles.sh), tuple(sorted(css.items())))
    if cle not in _REGLES:
        t.elem(r)["m_RuleIndex"] = -1
        t.styles.style(t, r, css)
        _REGLES[cle] = t.elem(r)["m_RuleIndex"]
    t.elem(r)["m_RuleIndex"] = _REGLES[cle]


def fonction_de_fm(modele, guid):
    """une copie de la première fonction de FM (BindFunction) de ce GUID dans ce modèle d'origine (None sinon), lue
    dans toutes ses références (chez FM, souvent dans un composant BindingSetterComponent)"""
    o = ouvrir(modele, depart_original=True)
    tt = o[3] if o else None
    for ref in (((tt.tt.get("references") or {}).get("RefIds") or []) if tt else []):
        fs = (ref.get("data") or {}).get("BindFunction")
        for f in fs if isinstance(fs, list) else []:
            if isinstance(f, dict) and (f.get("m_target") or {}).get("m_guid") == guid:
                return copy.deepcopy(f)
    return None


def _args(f, formes, quoi):
    """les arguments décodés de f, après vérification : autant que de formes, chacun finissant par la sienne"""
    a = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(a) != len(formes) or not all(bytes(x[0]).endswith(forme) for x, forme in zip(a, formes)):
        raise ValueError(f"{quoi} : arguments inattendus")
    return a


def _poser_args(f, a):
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(a)
    return f


# ---------- l'événement du menu Sélect. rapide, réécrit ----------
def evenement_menu(t):
    """SelectionEvents du menu Sélect. rapide (surcharge du dropdown de TacticalPlannerSpeakToActions)"""
    for r in t.walk():
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            ev = d.get("SelectionEvents")
            if isinstance(ev, dict) and b"SelectedAction.Event" in bytes(ev.get("m_bytes") or []):
                return ev
    return None


def chemins_evenement(b):
    """[(début, fin, chemin)] des chaînes d'un événement : en-tête 01 01 01 01 01, int32 longueur (du reste), int32
    action, puis des blocs int32 L, 01 01, n, chaîne (L = n + 3) ; None si la forme n'est pas celle-là"""
    if b[:5] != b"\x01" * 5 or struct.unpack_from("<i", b, 5)[0] != len(b) - 9:
        return None
    out, i = [], 13
    while i < len(b):
        if i + 7 <= len(b):
            L, n = struct.unpack_from("<i", b, i)[0], b[i + 6]
            if b[i + 4] == 1 and b[i + 5] == 1 and n < 128 and L == n + 3 and i + 7 + n <= len(b) \
                    and all(0x20 <= c < 0x7f for c in b[i + 7:i + 7 + n]):
                out.append((i, i + 7 + n, b[i + 7:i + 7 + n].decode()))
                i += 7 + n
                continue
        i += 1
    return out


def evenement_bouton(ev, rang, speakto=SPEAKTO):
    """l'événement du menu, ses chemins remplacés : SpeakTo -> speakto (Tactiques : Tactic.SpeakTo ; Effectif v8 : le
    « speakto » de l'écran, celui de son propre menu), SelectedAction.<champ> -> notre chemin
    du type que lit le jeu (CHAMPS ; le rang de ce bouton pour ActionResponseValue) ; « null » (NPC, comme le menu de
    FM) gardé ; un champ inconnu : refus (rien posé)"""
    b = bytes(ev["m_bytes"])
    morceaux = chemins_evenement(b)
    if morceaux is None or [c for _, _, c in morceaux] != CHEMINS_MENU:
        raise ValueError("événement du menu Sélect. rapide : forme inattendue (mise à jour du jeu ?)")
    out, pos = bytearray(b[:13]), 13
    for debut, fin, c in morceaux:
        out += b[pos:debut]
        if c == "SpeakTo":
            neuf = speakto
        elif c.lower().startswith("selectedaction."):
            champ = c.split(".", 1)[1].lower()
            neuf = V_RANG.format(rang) if champ == "actionresponsevalue" else CHAMPS.get(champ)
            if neuf is None:
                raise ValueError(f"événement du menu Sélect. rapide : champ inconnu {c}")
        else:
            neuf = c
        nb_ = neuf.encode()
        out += struct.pack("<i", len(nb_) + 3) + b"\x01\x01" + bytes([len(nb_)]) + nb_
        pos = fin
    out += b[pos:]
    struct.pack_into("<i", out, 5, len(out) - 9)
    nouveau = copy.deepcopy(ev)
    nouveau["m_bytes"] = list(out)
    return nouveau


# ---------- les pièces de FM ----------
def pieces_filtre(tf):
    """(Filtre, son SIVisible « hors match », la rangée #Top, son texte) dans l'arbre tf (None si absents)"""
    filtre = next((r for r in tf.walk() if typ(tf, r) == "SIFloatingPopupWidget"), None)
    hors_match = top = texte = None
    if filtre is not None:
        r = filtre
        while r in tf.parent and not (typ(tf, r) == "SIVisible" and tf.binding(r) == "tactic.IsDuringMatch"
                                      and tf.sd(r).get("InvertDirectBinding") == 1):
            r = tf.parent[r]
        if typ(tf, r) == "SIVisible" and r in tf.parent and tf.name(tf.parent[r]) == "Top":
            hors_match, top = r, tf.parent[r]
        texte = next((k for k in tf.children(filtre) if typ(tf, k) == "SIText"), None)
    return filtre, hors_match, top, texte


class Sources:
    def __init__(self, t, en_haut=None, rangee=RANGEE, speakto=SPEAKTO):
        self.speakto = speakto
        # dans le modèle touché : en haut, la rangée de Sélect. rapide (v6 ; écrans Effectif v8 : #QuickPick) ; à
        # gauche de Filtre, #Top et le SIVisible « hors match » de Filtre (notre zone juste avant lui, comme Kinito)
        self.en_haut = EN_HAUT if en_haut is None else en_haut
        self.rangee = self.hors_match_cible = None
        if self.en_haut:
            self.rangee = next((r for r in t.walk() if t.name(r) == rangee and typ(t, r) == "BindingVariables"), None)
        else:
            _, self.hors_match_cible, self.rangee, _ = pieces_filtre(t)
        # dans l'ORIGINAL du modèle de « Filtre » : son SIVisible « hors match », son texte, #StoppageVisible
        f = ouvrir(MODELE_FILTRE, depart_original=True)
        tf = self.tf = f[3] if f else None
        self.filtre = self.hors_match = self.top = self.texte = self.visible_entier = None
        if tf:
            self.filtre, self.hors_match, self.top, self.texte = pieces_filtre(tf)
        if tf:
            self.visible_entier = next((r for r in tf.walk() if typ(tf, r) == "SIVisible"
                                        and tf.name(r) == "StoppageVisible"
                                        and (((tf.sd(r).get("Binding") or {}).get("m_visualFunction") or {}).get(
                                            "m_target") or {}).get("m_guid") == FONCTION_VISIBLE_ENTIER), None)
        # ailleurs (originaux) : le menu Sélect. rapide, la BindingSetter, deux fonctions
        m = ouvrir(SOURCE_MENU, depart_original=True)
        self.tm = m[3] if m else None
        self.evenement = evenement_menu(self.tm) if self.tm else None
        self.bouton = next((r for r in self.tm.walk() if typ(self.tm, r) == "SIButton" and self.tm.name(r) == "button"),
                           None) if self.tm else None
        c = ouvrir(SOURCE_CALCUL, depart_original=True)
        self.tc = c[3] if c else None
        self.calcul = next((r for r in self.tc.walk() if self.tc.name(r) == NOM_CALCUL and any(
            (f.get("m_target") or {}).get("m_guid") == FONCTION_SOMME for f in self.tc.sd(r).get("BindFunction") or [])),
            None) if self.tc else None
        self.fn_nombre = fonction_de_fm(SOURCE_NOMBRE, FONCTION_NOMBRE)
        self.fn_element = fonction_de_fm(SOURCE_ELEMENT, FONCTION_ELEMENT)
        self.fn_nul = fonction_de_fm(SOURCE_NUL, FONCTION_NUL)

    def manque(self):
        noms = ("rangee", "filtre", "hors_match", "top", "texte", "visible_entier", "evenement", "bouton", "calcul",
                "fn_nombre", "fn_element", "fn_nul")
        return [n for n in noms if getattr(self, n) is None]


def fn_nul(src, reference, si_non_nulle, si_nulle, destination):
    """destination = si_non_nulle si reference n'est pas nulle, sinon si_nulle, sans jamais lire une référence vide
    (BindAndSetAOrBToDestinationUsingReferenceIsNullAsBool, ViewedFixtureTooltip ; entrées : ValidateReference,
    PrimaryBinding, FallbackBinding, Destination, ForceUpdate — graphe lu, comme 26.9 v19, vue en jeu)"""
    f = copy.deepcopy(src.fn_nul)
    a = _args(f, (CHEMIN_ARG, CHEMIN_ARG, CHEMIN_ARG, CHEMIN_ARG, b"BooleanVisualArg"),
              f"« référence nulle ? » de FM ({SOURCE_NUL})")
    a[0][1], a[1][1], a[2][1], a[3][1] = chaine(reference), chaine(si_non_nulle), chaine(si_nulle), chaine(destination)
    return _poser_args(f, a)


def fn_nombre(src, liste, destination):
    """destination (entier) = nombre d'éléments de liste (FM : FinancesDebtsAndLoansBlock_8x3, ForceUpdate gardé)"""
    f = copy.deepcopy(src.fn_nombre)
    a = _args(f, (CHEMIN_ARG, CHEMIN_ARG, b"BooleanVisualArg"), f"« nombre d'éléments » de FM ({SOURCE_NOMBRE})")
    a[0][1], a[1][1] = chaine(liste), chaine(destination)
    return _poser_args(f, a)


def fn_element(src, liste, destination, rang):
    """« élément n d'une liste, s'il existe » : liste[rang] -> destination, rien si le rang manque (variante IfNotNull,
    mêmes entrées, comme 26.18) ; les deux booléens de FM gardés (premier usage de TransferBlockMainFrame : depuis le
    début)"""
    f = copy.deepcopy(src.fn_element)
    f["m_target"]["m_guid"] = FONCTION_ELEMENT_SI
    a = _args(f, (CHEMIN_ARG, CHEMIN_ARG, b"Int32VisualArg", b"BooleanVisualArg", b"BooleanVisualArg"),
              f"« élément n d'une liste » de FM ({SOURCE_ELEMENT})")
    if bytes(a[3][1]) != b"\x00":
        raise ValueError(f"« élément n d'une liste » de FM ({SOURCE_ELEMENT}) : compté depuis la fin, inattendu")
    a[0][1], a[1][1], a[2][1] = chaine(liste), chaine(destination), struct.pack("<i", rang)
    a[4][1] = b"\x01"   # v6 : ForceUpdate (comme le nombre) : une sélection sauvegardée / renommée suit tout de suite
    return _poser_args(f, a)


# ---------- les pièces posées ----------
def copie_vide(t, src_t, rid, parent, index=None):
    """copie d'un élément d'un AUTRE modèle (src_t), sans ses enfants, sous parent (en dernier si index None)"""
    r = t.clone(rid, parent, index, src=src_t)
    for k in list(t.children(r)):
        t.remove(k)
    recaler_parent(t, r)
    return r


def zone(t, src, nom):
    """v6 : copie sans enfants du SIVisible « hors match » de Filtre, dernière de la rangée de Sélect. rapide (à droite
    de sa flèche), en rangée centrée, qui se tasse si la place manque"""
    if src.en_haut:
        r = copie_vide(t, src.tf, src.hors_match, src.rangee)
        css = {"flex-shrink": 1, "min-width": 0, "flex-direction": "row", "align-items": "center"}
    else:   # option « filtre » (place de Kinito) : juste avant Filtre, prend la place libre, boutons collés à Filtre
        r = copie_vide(t, src.tf, src.hors_match, src.rangee, t.children(src.rangee).index(src.hors_match_cible))
        css = {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "flex-direction": "row",
               "justify-content": "flex-end", "align-items": "center"}
    nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    t.styles.style(t, r, css)
    return r


def calcul(t, src, parent, nom):
    """la BindingSetter de FM (SearchBindingsSetter de GlobalSearchCard, vidée) : nos variables et nos fonctions"""
    sel = t.clone(src.calcul, parent, src=src.tc)
    for k in list(t.children(sel)):
        t.remove(k)
    recaler_parent(t, sel)   # (sa règle de style n'est pas recopiée : remplacée juste après, elle resterait orpheline)
    nommer(t, sel, nom)
    t.elem(sel)["m_Classes"], t.elem(sel)["m_RuleIndex"] = [], -1
    sd = t.sd(sel)
    modele_v = (sd.get("ValueVariables") or [None])[0]
    if modele_v is None:
        raise ValueError(f"BindingSetter de FM ({SOURCE_CALCUL}) : forme inattendue")

    def var(nv, donnee):
        v = copy.deepcopy(modele_v)
        v["m_name"], v["m_scopeValue"]["m_serializedData"] = nv, donnee
        return v

    sd["ValueVariables"] = ([var(V_NB, "Int|0|"), var(V_LISTE_OK, "Bool|0|"),
                             var(V_EV, f"Int|{EVENEMENT_UTILISER}|"), var(V_MOINS1, "Int|-1|"),
                             var(V_ZERO, "Int|0|"), var(V_FAUX, "Bool|0|")]
                            + [var(V_REF_OK.format(k), "Bool|0|") for k in range(len(CHAMPS_REF))]
                            + [var(V_RANG.format(n), f"Int|{n}|") for n in range(NOMBRE)])
    sd["ValueVariables_UxmlAttributeFlags"] = 1
    refs = [V_SEL.format(n) for n in range(NOMBRE)] + [V_LIGNE0]
    sd["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": nv} for nv in refs]
    sd["ReferenceVariables_UxmlAttributeFlags"] = 1
    sd["BindFunction"] = ([fn_nombre(src, LISTE, V_NB)]
                          + [fn_element(src, LISTE, V_SEL.format(n), n) for n in range(NOMBRE)]
                          + [fn_element(src, f"{src.speakto}.{ACTIONS_SOUS}", V_LIGNE0, 0),
                             fn_nul(src, LISTE_VIDE, "const.True", "const.False", V_LISTE_OK)]
                          + [fn_nul(src, f"{REF_LIGNE0}.{c}", "const.True", "const.False", V_REF_OK.format(k))
                             for k, c in enumerate(CHAMPS_REF)])
    sd["BindFunction_UxmlAttributeFlags"] = 1
    t.styles.style(t, sel, {"flex-direction": "row", "align-items": "center", "flex-shrink": 1, "min-width": 0})
    return sel


def visible_si(t, src, parent, nom, chemin, operateur, valeur):
    """copie sans enfants de #StoppageVisible : visible si (entier lu dans chemin) OPÉRATEUR valeur (BindIntToVisible :
    TryCastToInt puis Compare ; une valeur absente vaut 0, sans exception)"""
    r = copie_vide(t, src.tf, src.visible_entier, parent)
    nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1
    f = t.sd(r)["Binding"]["m_visualFunction"]
    a = _args(f, (b"GeneralVisualFunction+ComparisonOperator]", b"Int32VisualArg", b"BindingKeyVisualArg", CHEMIN_ARG),
              f"« montrer si entier » de FM (#StoppageVisible de {MODELE})")
    a[0][1], a[1][1], a[3][1] = struct.pack("<i", operateur), struct.pack("<i", valeur), chaine(chemin)
    _poser_args(f, a)
    style_partage(t, r, {"flex-direction": "row", "align-items": "center", "flex-shrink": 1, "min-width": 0})
    return r


def bouton(t, src, parent, nom, n):
    """le SIButton de Sélect. rapide, sans enfants, à l'allure de Filtre ; clic = l'événement du menu, champs du type
    lu par le jeu (v4) et rang n ; texte = le SIText de Filtre en liaison directe sur le nom de la sélection n"""
    b = t.clone(src.bouton, parent, src=src.tm)
    for k in list(t.children(b)):
        t.remove(k)
    recaler_parent(t, b)   # (sa règle de style n'est pas recopiée : remplacée juste après, elle resterait orpheline)
    nommer(t, b, nom)
    t.elem(b)["m_Classes"] = list(src.tf.elem(src.filtre).get("m_Classes") or [])   # celles de Filtre
    t.elem(b)["m_RuleIndex"] = -1
    t.sd(b)["Events"], t.sd(b)["Events_UxmlAttributeFlags"] = evenement_bouton(src.evenement, n, src.speakto), 1
    style_partage(t, b, {"margin-left" if src.en_haut else "margin-right": ECART,
                         "max-width": LARGEUR_MAX["haut" if src.en_haut else "filtre"], "flex-shrink": 1, "min-width": 0})
    x = t.clone(src.texte, b, src=src.tf)
    recaler_parent(t, x)
    nommer(t, x, f"{nom}-nom")
    t.elem(x)["m_Classes"], t.elem(x)["m_RuleIndex"] = ["content-no-wrap", "content-ellipsis"], -1
    tb = t.sd(x)["TextBinding"]
    tb["m_kind"] = 1
    tb.setdefault("m_direct", {"Path": {"m_path": ""}, "Nullable": 0})
    tb["m_direct"]["Path"]["m_path"] = f"{V_SEL.format(n)}.{CHEMIN_NOM}"
    tb["m_direct"]["Nullable"] = 1
    tb["m_visualFunction"]["m_target"]["m_guid"] = ""
    tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    return b


_N_REPERE = [0]


def repere(t, src, parent, texte, direct=False):
    """DIAG (v10, temporaire) : un petit texte (celui de Filtre) dans parent : fixe, ou lié au chemin texte (direct)"""
    x = t.clone(src.texte, parent, src=src.tf)
    recaler_parent(t, x)
    _N_REPERE[0] += 1
    nommer(t, x, f"{PREFIXE}-diag{_N_REPERE[0]}")
    t.elem(x)["m_RuleIndex"] = -1
    sd = t.sd(x)
    tb = sd["TextBinding"]
    tb.setdefault("m_direct", {"Path": {"m_path": ""}, "Nullable": 0})
    tb["m_visualFunction"]["m_target"]["m_guid"] = ""
    tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    if direct:
        tb["m_kind"], tb["m_direct"]["Path"]["m_path"], tb["m_direct"]["Nullable"] = 1, texte, 1
    else:
        sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = f" {texte} ", 1, texte
        tb["m_kind"], tb["m_direct"]["Path"]["m_path"] = 0, ""
    return x


def construire(t, en_haut=None, rangee=RANGEE, speakto=SPEAKTO):
    src = Sources(t, en_haut, rangee, speakto)
    if src.manque():
        return [f"pièces de FM introuvables : {', '.join(src.manque())} (mise à jour du jeu ?)"]
    try:
        z = zone(t, src, NOM)
        diag = DIAG and src.speakto == SPEAKTO_EFFECTIF
        if diag:
            repere(t, src, z, "Z")
        sel = calcul(t, src, z, f"{PREFIXE}-variables")
        if diag:
            repere(t, src, sel, "V")
            repere(t, src, visible_si(t, src, sel, f"{PREFIXE}-diagnb", V_NB, OPERATEUR_SUPERIEUR, 0), "N")
        garde = visible_si(t, src, sel, f"{PREFIXE}-garde", V_LISTE_OK, OPERATEUR_EGAL, 1)
        if diag:
            repere(t, src, garde, "L")
        for k in range(len(CHAMPS_REF)):   # v5 : une garde par champ « référence » de la ligne d'en-tête
            garde = visible_si(t, src, garde, f"{PREFIXE}-garde{k}", V_REF_OK.format(k), OPERATEUR_EGAL, 1)
            if diag:
                repere(t, src, garde, str(k))
        for n in range(NOMBRE):
            v = visible_si(t, src, garde, f"{PREFIXE}-si{n}", V_NB, OPERATEUR_SUPERIEUR, n)
            bouton(t, src, v, f"{PREFIXE}-bouton{n}", n)
    except ValueError as e:
        return [f"{e} : rien posé"]
    return [f"les {NOMBRE} premières sélections sauvegardées (tactic.TeamSelections) en boutons "
            + ("à droite de Sélect. rapide" if src.en_haut else "à gauche de Filtre") + ", "
            f"leur nom dessus ; clic = l'événement « Utiliser sélection » du menu, champs du type lu par le jeu "
            f"(références de la ligne d'en-tête du menu, liste vide) ; rien pendant un match"]


# ---------- retrait ----------
def retirer_zone(o):
    """retire notre zone du modèle, et les règles de style qu'elle avait ajoutées à sa feuille (comme 26.7)"""
    bundle, obj, tt, t = o
    racines = [r for r in marques(t) if r in t.parent and not t.name(t.parent[r]).startswith(PREFIXE)]
    for r in racines:   # chacune avec tout ce qu'elle contient
        t.remove(r)
    orig = hp.original(bundle, obj)
    feuille = orig and hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is None:
        return
    n0 = len(feuille["m_Rules"])
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    if not any(i >= n0 for i in utilisees):
        t.styles.sh, t.styles.changed = feuille, True   # plus aucune règle ajoutée utilisée : la feuille d'origine
        return
    regles = t.styles.sh["m_Rules"]
    garder = list(range(n0)) + [i for i in range(n0, len(regles)) if i in utilisees]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    t.styles.changed = True


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


# ---------- commandes ----------
def a_jour(t):
    return any(t.name(r) == NOM for r in marques(t))


def retirer_ancien():
    """v8 : la zone de l'AUTRE emplacement retirée de son modèle (True si retirée)"""
    o = ouvrir(AUTRE)
    if o is None or not marques(o[3]):
        return False
    retirer_zone(o)
    enregistrer(*o)
    print("[Kinito] Raccourcis des sélections : ancienne place retirée ("
          + ("à gauche de Filtre" if EN_HAUT else "à droite de Sélect. rapide") + ")")
    return True


def cibles():
    """(modèle, en haut ?, rangée) où poser : les Tactiques selon l'option, et (v8, le joueur) les écrans Effectif
    TOUJOURS à droite de leur Sélect. rapide (#QuickPick, même rangée que celle des Tactiques), quelle que soit l'option"""
    return [(MODELE, EN_HAUT, RANGEE, SPEAKTO)] + [(m, True, RANGEE_EFFECTIF, SPEAKTO_EFFECTIF)
                                                  for m in MODELES_EFFECTIF]


def cmd_appliquer():
    change = retirer_ancien()   # enregistré avec le reste (rien si la pose échoue : l'ancienne reste)
    for modele, en_haut, rangee, speakto in cibles():
        o = ouvrir(modele)
        if o is None:
            print(f"[Kinito] Raccourcis des sélections : {modele} introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if a_jour(o[3]):
            print(f"[Kinito] Raccourcis des sélections : {modele} déjà appliqué")
            continue
        if marques(o[3]):   # une ancienne version : retirée dans le même arbre, en mémoire, avant de reposer
            retirer_zone(o)
        msgs = construire(o[3], en_haut, rangee, speakto)
        for m in msgs:
            print(f"[Kinito] Raccourcis des sélections : {modele} : {m}")
        if any("introuvable" in m or "rien posé" in m for m in msgs):
            print(f"[Kinito] Raccourcis des sélections : {modele} : rien enregistré")
            continue
        enregistrer(*o)
        change = True
    if change:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    change = False
    for modele in (MODELE_HAUT, MODELE_FILTRE) + MODELES_EFFECTIF:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        retirer_zone(o)
        enregistrer(*o)
        change = True
        print(f"{modele} : raccourcis des sélections retirés (le reste du modèle n'est pas touché)")
    if change:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele, *_ in cibles():
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
        else:
            t = o[3]
            print(f"{modele} : " + (f"raccourcis présents (à jour, v{VERSION})" if a_jour(t)
                                    else ("ANCIENNE version" if marques(t) else "pas de raccourcis")))
    a = ouvrir(AUTRE)
    if a is not None and marques(a[3]):
        print(f"{AUTRE} : raccourcis encore là (autre emplacement : retirés au prochain « appliquer »)")
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
            print("[Kinito] Raccourcis des sélections : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
