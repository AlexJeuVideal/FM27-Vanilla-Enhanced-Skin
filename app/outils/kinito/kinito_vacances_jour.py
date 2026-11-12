"""[AJOUT KINITO] Calendrier, onglet Général : partir en vacances jusqu'à un jour précis, depuis la case de ce jour.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : « dans FM24, une petite flèche en haut à droite d'une case journalière permettait de
partir en vacances jusqu'à cette date : la date était remplie directement au lieu de la chercher ». Forme choisie : une
icône directe (pas de menu).

Portail > Calendrier > Général : en haut à droite de chaque jour À VENIR, l'icône vacances de FM
(game-concepts-holiday, 16 px, dans le bouton « contrôle » de FM, celui de la poubelle des contrats) ; son nom au
survol. Un clic ouvre la fenêtre des vacances de FM (panneau GoOnHolidayCard) en lui passant deux paramètres :
kinitovacances = vrai et kinitodate = la date du jour (day.Date). Dans la fenêtre, un SIDelayEvent, relié aux données
seulement quand kinitovacances est passé, met DELAI s après l'ouverture le type de retour sur 4 (« Choisir… ») puis la
date de retour sur kinitodate. Ouverte par le bouton « Partir en vacances » de FM (sans paramètre), la fenêtre ne
change pas.

Historique des versions (demandes, relevés en jeu, essais) : résumé dans « AJOUTS KINITO - DETAILS.md »,
§ 5 ; texte complet gardé par Kinito.

Relevé dans le jeu (2026-11-12), rien de deviné :
- la case d'un jour (CalendarDay_block, paramètre day) connaît sa date : day.Date (GameDate, relevé F7), que FM compare
  déjà dans cette case (BindAndSetGameDatePropertyComparison, day.Date / highlightedday.Date) ;
- le bouton « Partir en vacances » ouvre le panneau GoOnHolidayCard (ui-panelids, GUID 7ee51df4…, parameters vide) ;
  son modèle GoOnHolidayCard a un BindingRootComponent (Parameters vide) et un BindingRemapperComponent
  (holiday -> human.GoOnHoliday) ; le GoOnHolidayWidget qu'il contient affiche
  holiday = game.GameCurrentManager.GoOnHoliday. Un panneau reçoit ses paramètres comme les Rencontres :
  CalendarToolFixturesTab déclare « calendartab », « team », « highlightedday » dans ses parameters ET dans le
  BindingRoot de son modèle (CalendarTool) ; l'événement d'ouverture avec paramètres est celui d'entrainement_equipes
  (evenement_ecran), dont le contenu sans paramètre est celui du bouton de FM à l'octet près (vérifié par _verifier) ;
- menu « Retour de vacances » (relevé F7) : 0 « Dans une semaine », 1 « Dans un mois », 2 « Pour le prochain match »,
  4 « Choisir… » ; le sélecteur de date ne s'affiche que sur 4 (#ChooseDayVisible : égal, 4) ; les boutons radio
  écrivent ReturnDateType (3 après N jours, 6 sans date fixe) ; la date du sélecteur est holiday.ReturnDate ;
- SIDelayEvent (FM.UI) : BindToData -> StartTransition, ses TransitionEvents partent après m_duration s (modèles FM :
  StateSetPieceWizardCreation, GameCreationGameSummaryScreen 1,0 s) ; SIVisible ne relie ses enfants aux données que
  visible (m_childrenBound, AlwaysBindChildren faux par défaut) : c'est le garde-fou du bouton de FM ;
- liste de plusieurs événements : [1,1,1,N] puis, pour chacun, [1] + longueur (int32) + contenu.

Vu en jeu (v2 → v3) : le type 4 seul ne suffit pas, le menu reste sur son option ; il faut aussi écrire l'option du
menu (« Choisir… », la dernière de la liste) : c'est ce que fait la v3.

Visible seulement (SIVisible de FM, InvertDirectBinding) : onglet Général (istraining faux : la même case sert aux
calendriers d'entraînement, istraining vrai), jour pas passé (day.HasDayPassed), pas aujourd'hui (day.IsCurrentDay),
pas déjà en vacances (game.GameCurrentManager.IsOnHoliday, comme le bouton de FM).

Touchés (seul propriétaire de chacun : aucun script d'AlexJeuVideal ni d'autre ajout Kinito n'y touche) :
- CalendarDay_block (bundle global) et GoOnHolidayCard (modèle, bundle gameworld) : appliquer repart de l'original,
  retirer le remet ;
- le panneau GoOnHolidayCard (bundle ui-panelids, que rien d'autre ne modifie) : ses parameters reçoivent les deux
  noms ; appliquer repart de son original, retirer le remet.
Morceaux de FM recopiés, sans les modifier : le bouton de la poubelle de ContractNegotiationAddOnItem
(#buttons-controls-pc-default + son icône simple), l'infobulle de RoleLabelwIcon (Tooltip > SIText), le SIVisible
#GradientHeaderVisible de la case, le SIDelayEvent de GameCreationGameSummaryScreen.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vacances_jour.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vacances_jour.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vacances_jour.py etat
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
import langue  # noqa: E402  (textes fixes en français ou en anglais, choix 106)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
ICONE_CLASSE = "game-concepts-holiday"   # icône vacances de FM (16 x 16 dans FMImages_1x, comme la poubelle)
BOUTON = 20          # px, côté du bouton (icône 16 + 2 de chaque côté, comme les cadenas des contrats)
ICONE = 16           # px
MARGE_DROITE = 4     # px, écart avec le bord droit de la case
DELAI = 0.5          # s, après l'ouverture de la fenêtre (elle s'ouvre en 0,33 s et repart de ses réglages)
TEXTE = langue.texte("Partir en vacances jusqu'à cette date", "Go on holiday until this date")
# =====================================================================================================

VERSION = 3   # v1 : la case écrivait type et date avant l'affichage (écrasés) ; v2 : la fenêtre les écrit une fois ouverte
              # (vu en jeu : type 4 et date bien écrits, mais le menu reste sur son option 0) ; v3 : l'option du menu aussi
MODELE = "CalendarDay_block"
FENETRE = "GoOnHolidayCard"                                            # modèle de la fenêtre (gameworld)
PANNEAU = "GoOnHolidayCard"                                            # son panneau (ui-panelids)
PANNEAUX = os.path.join(nb.AA, "ui-panelids_assets_all.bundle")
SOURCE_POPUP = ("CalendarHeaderSeasonBlock", "GoOnHolidayButton")      # bouton FM « Partir en vacances »
GUID_POPUP = "7ee51df42b0a89646a12ba40c2446ee5"                        # le panneau qu'il ouvre (GoOnHolidayCard)
SOURCE_BOUTON = ("ContractNegotiationAddOnItem", "buttons-controls-pc-default")   # bouton-icône FM (poubelle)
SOURCE_BULLE = "RoleLabelwIcon"                                        # Tooltip > SIText, posé dans une ligne FM
SOURCE_VISIBLE = "GradientHeaderVisible"                               # SIVisible direct de la case (day.IsCurrentDay)
SOURCE_DELAI = "GameCreationGameSummaryScreen"                         # SIDelayEvent de FM sans enfant
SOURCE_REGLAGE = ("GoOnHolidayWidget", "BindingSetter")                 # élément BindingSetter de FM (son enfant est retiré)
SOURCE_DERNIER = ("TransferBlockMainFrame", "lastItem")                 # BindListItemUsingIndexToDestination(liste, lastItem, 1, vrai, faux) : le dernier élément
OPTION = "kinitooption"                                                # variable : la dernière option du menu « Retour de vacances »
VACANCES = "game.GameCurrentManager.GoOnHoliday"                       # ce qu'affiche GoOnHolidayWidget
ALIAS = "kinitoholiday"                                                # notre renvoi vers VACANCES dans la fenêtre
PARAM_DRAPEAU = "kinitovacances"                                       # passé par notre icône seulement
PARAM_DATE = "kinitodate"
DATE_JOUR = "day.Date"
TYPE_DATE_PRECISE = "const.Four"     # option 4 du menu « Retour de vacances » : « Choisir… », qui montre le sélecteur
CONDITIONS = [                        # (nom, chemin) : visible quand le chemin est FAUX
    ("onglet-general", "istraining"),
    ("jour-a-venir", "day.HasDayPassed"),
    ("pas-aujourdhui", "day.IsCurrentDay"),
    ("pas-en-vacances", "game.GameCurrentManager.IsOnHoliday"),
]
PREFIXE = "UIPickerKinito"
NOM = f"{PREFIXE}-vacances-jour-v{VERSION}{langue.SUFFIXE}"
NOM_FENETRE = f"{PREFIXE}-vacances-fenetre-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_vacances_jour.actif")


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


# ---------- événements (format de FM) ----------
def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def copier(source, destination):
    """contenu d'un événement « copier la valeur de <source> dans <destination> » (217,15,225,87)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])


def ouvrir_panneau(guid, params):
    """contenu d'un événement « ouvrir le panneau <guid> avec ces paramètres [(nom, chemin)] » : le format
    d'entrainement_equipes.evenement_ecran (vérifié par AlexJeuVideal sur TrainingOverviewCalendarBlock), sans l'octet
    qu'elle ajoute après la liste"""
    corps = bytes([211, 101, 102, 7, 2])
    corps += _bloc(bytes([1, 0, 1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += _bloc(bytes([1, 0, 1, 1, 1, 32]) + guid.encode() + bytes([1, 0, 3, 0, 0, 0, 1, 1, 0]))
    corps += b"\x01\x01" + _enc_varint(len(params))
    for nom, chemin in params:
        corps += _bloc(_texte(nom) + _bloc(_texte(chemin)) + b"\x00")
    corps += b"\x00\x00"
    return corps


def liste(contenus):
    """liste d'événements : [1,1,1,N] puis [1] + longueur + contenu pour chacun"""
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def decouper(octets):
    """contenus des événements d'une liste ; None si le format n'est pas celui attendu"""
    b = bytes(octets)
    if len(b) < 4 or b[:3] != b"\x01\x01\x01":
        return None
    i, out = 4, []
    for _ in range(b[3]):
        if i + 5 > len(b) or b[i] != 1:
            return None
        n = struct.unpack_from("<i", b, i + 1)[0]
        out.append(b[i + 5:i + 5 + n])
        i += 5 + n
    return out if i == len(b) else None


def _verifier_evenements():
    """les formats écrits ici = ceux de FM, refaits à l'octet près : la copie de ClubNationInfoTabButton, et l'ouverture
    du bouton « Partir en vacances » (original de CalendarHeaderSeasonBlock) sans paramètre"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    if liste([copier("rowindex", "selected-tab")]) != attendu:
        return False
    o = ouvrir(SOURCE_POPUP[0], depart_original=True)
    if o is None:
        return False
    t = o[3]
    b = first(t, lambda r: t.name(r) == SOURCE_POPUP[1] and typ(t, r) == "SIButton")
    contenus = b is not None and decouper(t.sd(b).get("Events", {}).get("m_bytes") or [])
    return bool(contenus) and len(contenus) == 1 and contenus[0] == ouvrir_panneau(GUID_POPUP, [])


# ---------- la case du jour ----------
class Sources:
    def __init__(self):
        o = ouvrir(SOURCE_BOUTON[0], depart_original=True)
        self.tb = o and o[3]
        self.bouton = self.tb and first(self.tb, lambda r: self.tb.name(r) == SOURCE_BOUTON[1]
                                        and typ(self.tb, r) == "SIButton")
        u = ouvrir(SOURCE_BULLE, depart_original=True)
        self.tu = u and u[3]
        self.bulle = self.tu and first(self.tu, lambda r: typ(self.tu, r) == "Tooltip"
                                       and len(self.tu.children(r)) == 1
                                       and typ(self.tu, self.tu.children(r)[0]) == "SIText")
        v = ouvrir(MODELE, depart_original=True)
        self.tv = v and v[3]
        self.visible = self.tv and first(self.tv, lambda r: self.tv.name(r) == SOURCE_VISIBLE and typ(self.tv, r) == "SIVisible")
        d = ouvrir(SOURCE_DELAI, depart_original=True)
        self.td = d and d[3]
        self.delai = self.td and first(self.td, lambda r: self.td.elem(r).get("m_FullTypeName") == "FM.UI.SIDelayEvent"
                                       and not self.td.children(r))
        g = ouvrir(SOURCE_REGLAGE[0], depart_original=True)
        self.tg = g and g[3]
        self.reglage = self.tg and first(self.tg, lambda r: typ(self.tg, r) == SOURCE_REGLAGE[1])
        # la fonction FM qui met le dernier élément d'une liste dans une variable (relue, pas écrite en dur)
        self.fn_dernier = None
        s = ouvrir(SOURCE_DERNIER[0], depart_original=True)
        if s is not None:
            for r in s[3].tt["references"]["RefIds"]:
                for f in (r.get("data") or {}).get("BindFunction") or []:
                    if isinstance(f, dict) and any(a[1] == b"\x01" + _enc_varint(len(SOURCE_DERNIER[1])) + SOURCE_DERNIER[1].encode()
                                                   for a in decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])):
                        self.fn_dernier = copy.deepcopy(f)

    def ok(self):
        icones = self.bouton is not None and [k for k in self.tb.children(self.bouton) if typ(self.tb, k) == "VisualElement"]
        return (None not in (self.bouton, self.bulle, self.visible, self.delai, self.reglage, self.fn_dernier)
                and len(icones or []) == 1)


def _parent_id(t, rid):
    """clone / clone_shallow ne refont que m_Parent : l'identifiant du parent aussi (composants seulement)"""
    p = t.parent[rid]
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(rid)["m_ParentId"])


def _nommer(t, rid, nom):
    t.sd(rid)["name"], t.sd(rid)["name_UxmlAttributeFlags"] = nom, 1


def _visible(t, src, parent, chemin, inverse, nom):
    """SIVisible direct de FM (copie de #GradientHeaderVisible, sans son enfant) sur <chemin>"""
    v = t.clone(src.visible, parent, src=src.tv)
    for k in list(t.children(v)):
        t.remove(k)
    _parent_id(t, v)
    sd = t.sd(v)
    _nommer(t, v, nom)
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = (1 if inverse else 0), 1
    t.elem(v)["m_Classes"] = []
    t.elem(v)["m_RuleIndex"] = -1
    return v


def construire_case(t, src):
    entete = first(t, lambda r: t.name(r) == "Header")
    if entete is None:
        return ["en-tête de la case introuvable"]
    # quatre SIVisible imbriqués : visible quand chaque chemin est faux
    parent = entete
    for i, (nom, chemin) in enumerate(CONDITIONS):
        v = _visible(t, src, parent, chemin, True, NOM if i == 0 else f"{PREFIXE}-vacances-jour-{nom}")
        if i == 0:   # en haut à droite de l'en-tête, centré en hauteur, par-dessus le reste
            t.styles.style(t, v, {"position": "absolute", "right": MARGE_DROITE, "top": 0, "bottom": 0,
                                  "flex-direction": "column", "justify-content": "center", "align-items": "center"})
        parent = v
    # le bouton-icône de FM (poubelle des contrats) : icône vacances, infobulle, clic = la fenêtre avec la date
    b = t.clone(src.bouton, parent, src=src.tb)
    t.styles.copy_from(src.tb.styles, t, b)
    _parent_id(t, b)
    _nommer(t, b, f"{PREFIXE}-vacances-jour-bouton")
    t.sd(b)["Events"] = {"m_bytes": liste([ouvrir_panneau(GUID_POPUP, [(PARAM_DRAPEAU, "const.True"),
                                                                       (PARAM_DATE, DATE_JOUR)])])}
    t.sd(b)["Events_UxmlAttributeFlags"] = 1
    t.styles.style(t, b, {"width": BOUTON, "min-width": BOUTON, "height": BOUTON, "min-height": BOUTON, "padding": 0,
                          "margin-left": 0, "margin-right": 0, "margin-top": 0, "margin-bottom": 0,
                          "justify-content": "center", "align-items": "center"})
    icone = next(k for k in t.children(b) if typ(t, k) == "VisualElement")
    _nommer(t, icone, f"{PREFIXE}-vacances-jour-icone")
    t.elem(icone)["m_Classes"] = [ICONE_CLASSE]
    t.styles.style(t, icone, {"width": ICONE, "height": ICONE})
    bulle = t.clone(src.bulle, b, src=src.tu)   # sur le bouton entier
    t.styles.copy_from(src.tu.styles, t, bulle)
    _parent_id(t, bulle)
    _nommer(t, bulle, f"{PREFIXE}-vacances-jour-bulle")
    texte = t.children(bulle)[0]
    _nommer(t, texte, f"{PREFIXE}-vacances-jour-bulle-texte")
    ts = t.sd(texte)
    ts.update(text=TEXTE, text_UxmlAttributeFlags=1)
    ts["TextBinding"]["m_kind"] = 0
    ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    return [f"icône vacances en haut à droite des jours à venir (onglet Général), bulle « {TEXTE} », clic = fenêtre "
            f"des vacances avec {PARAM_DRAPEAU} = vrai et {PARAM_DATE} = {DATE_JOUR}"]


# ---------- la fenêtre des vacances (modèle GoOnHolidayCard) ----------
def _parametre(nom):
    """déclaration d'un paramètre facultatif sans type, comme « calendartab » dans le BindingRoot de CalendarTool"""
    return {"m_serialisedType": 0, "name": nom, "type": {"id": 0}, "isOptional": 1,
            "defaultValue": {"m_kind": 0, "Path": {"m_path": ""}, "m_scopeValue": {"m_serializedData": ""}}}


def construire_fenetre(t, src):
    racine = t.tt["m_VisualTree"]["rid"]
    comp = next((k for k in t.children(racine) if typ(t, k) == "ComponentElement"), None)
    if comp is None:
        return ["racine de la fenêtre des vacances introuvable"]
    composants = [x["rid"] for x in t.sd(comp).get("m_components") or []]
    racine_c = next((x for x in composants if "BindingRootComponent" in t.refs[x]["type"]["class"]), None)
    renvoi_c = next((x for x in composants if "BindingRemapperComponent" in t.refs[x]["type"]["class"]), None)
    if racine_c is None or renvoi_c is None:
        return ["composants de la fenêtre des vacances introuvables"]
    # les deux paramètres (en plus de ceux que FM y mettrait un jour)
    d = t.refs[racine_c]["data"]
    params = d.setdefault("Parameters", [])
    for nom in (PARAM_DRAPEAU, PARAM_DATE):
        if not any(p.get("name") == nom for p in params):
            params.append(_parametre(nom))
    d["Parameters_UxmlAttributeFlags"] = 1
    # notre renvoi vers ce qu'affiche GoOnHolidayWidget (FM met « holiday » sur human.GoOnHoliday à ce niveau)
    m = t.refs[renvoi_c]["data"].setdefault("Mappings", [])
    modele = next((x for x in m if x.get("from") == "holiday"), None)
    if modele is None:
        return ["renvoi « holiday » de la fenêtre des vacances introuvable"]
    neuf = copy.deepcopy(modele)
    neuf["from"], neuf["to"]["m_path"] = ALIAS, VACANCES
    m.append(neuf)
    # SIVisible sur kinitovacances (passé par notre icône seulement), qui contient le SIDelayEvent
    v = _visible(t, src, comp, PARAM_DRAPEAU, False, NOM_FENETRE)
    t.styles.style(t, v, {"position": "absolute", "width": 0, "height": 0})
    # v3 : un BindingSetter (élément de FM, son enfant retiré) déclare OPTION (variable de référence sans type, comme
    # 417 variables du jeu) et y met la dernière option du menu « Retour de vacances » (« Choisir… »)
    g = t.clone(src.reglage, v, src=src.tg)
    for k in list(t.children(g)):
        t.remove(k)
    _parent_id(t, g)
    t.elem(g)["m_Classes"] = []
    t.elem(g)["m_RuleIndex"] = -1
    sg = t.sd(g)
    _nommer(t, g, f"{PREFIXE}-vacances-fenetre-option")
    f = copy.deepcopy(src.fn_dernier)
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        return ["fonction « dernier élément d'une liste » : arguments inattendus"]
    for a, chemin in zip(chemins, (f"{ALIAS}.ReturnDateDropdown", OPTION)):
        a[1] = b"\x01" + _enc_varint(len(chemin)) + chemin.encode()
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sg["BindFunction"], sg["BindFunction_UxmlAttributeFlags"] = [f], 1
    sg["ValueVariables"] = []
    sg["ReferenceVariables"] = [{"m_type": {"id": 0}, "m_initToNull": 1, "m_name": OPTION}]
    sg["ValueVariables_UxmlAttributeFlags"], sg["ReferenceVariables_UxmlAttributeFlags"] = 1, 1
    dl = t.clone(src.delai, g, src=src.td)
    t.styles.copy_from(src.td.styles, t, dl)
    _parent_id(t, dl)
    sd = t.sd(dl)
    _nommer(t, dl, f"{PREFIXE}-vacances-fenetre-ecriture")
    sd["m_duration"], sd["m_duration_UxmlAttributeFlags"] = float(DELAI), 1
    sd["TransitionEvents"] = {"m_bytes": liste([
        copier(OPTION, f"{ALIAS}.returndatedropdownselectedoption"),   # l'option du menu, comme l'écrit son SIDropdown
        copier(TYPE_DATE_PRECISE, f"{ALIAS}.ReturnDateType"),
        copier(PARAM_DATE, f"{ALIAS}.ReturnDate"),                    # en dernier : rien ne l'écrase après
    ])}
    sd["TransitionEvents_UxmlAttributeFlags"] = 1
    return [f"fenêtre des vacances : paramètres {PARAM_DRAPEAU} / {PARAM_DATE}, renvoi {ALIAS} -> {VACANCES}, "
            f"{DELAI} s après l'ouverture : option du menu = sa dernière (« Choisir… »), type {TYPE_DATE_PRECISE}, puis "
            f"date {PARAM_DATE} (seulement si {PARAM_DRAPEAU} est passé)"]


# ---------- le panneau (ui-panelids) ----------
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


def panneau_a_jour(tt):
    p = ((tt.get("m_panelDescription") or {}).get("parameters")) or []
    return PARAM_DRAPEAU in p and PARAM_DATE in p


def construire_panneau(tt):
    p = tt.get("m_panelDescription", {}).get("parameters")
    if p is None:
        return "paramètres du panneau des vacances introuvables"
    for nom in (PARAM_DRAPEAU, PARAM_DATE):
        if nom not in p:
            p.append(nom)
    return f"panneau {PANNEAU} : paramètres {', '.join(p)}"


# ---------- écriture ----------
def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre_original(o, nom):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{nom} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{nom} : remis d'origine")
    return True


# ---------- commandes ----------
def cmd_appliquer():
    if not _verifier_evenements():
        print("[Kinito] Vacances jour : format d'événement inattendu, rien enregistré")
        return
    case, fen = ouvrir(MODELE), ouvrir(FENETRE)
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    if case is None or fen is None or pan is None:
        print(f"[Kinito] Vacances jour : {MODELE}, {FENETRE} ou le panneau des vacances introuvable "
              "(renommé par une mise à jour ?), ignoré")
        return
    deja = (any(case[3].name(r) == NOM for r in marques(case[3]))
            and any(fen[3].name(r) == NOM_FENETRE for r in marques(fen[3]))
            and panneau_a_jour(pan.read_typetree()))
    if deja:
        print("[Kinito] Vacances jour : déjà appliqué")
    else:
        src = Sources()
        if not src.ok():
            print("[Kinito] Vacances jour : morceaux de FM introuvables (bouton, infobulle, SIVisible ou SIDelayEvent), "
                  "rien enregistré")
            return
        travail_c, travail_f = ouvrir(MODELE, depart_original=True), ouvrir(FENETRE, depart_original=True)
        if marques(travail_c[3]) or marques(travail_f[3]):
            print(f"[Kinito] Vacances jour : pas de sauvegarde d'origine propre de {MODELE} ou {FENETRE}, ignoré")
            return
        msgs = construire_case(travail_c[3], src) + construire_fenetre(travail_f[3], src)
        tt_p = hp.original(PANNEAUX, pan) or pan.read_typetree()
        msgs.append(construire_panneau(tt_p))
        for m in msgs:
            print(f"[Kinito] Vacances jour : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Vacances jour : rien enregistré")
            return
        enregistrer(*travail_c)
        enregistrer(*travail_f)
        pan.save_typetree(tt_p)
        nb._dirty.add(PANNEAUX)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for nom in (MODELE, FENETRE):
        o = ouvrir(nom)
        if o is not None and marques(o[3]):
            fait = remettre_original(o, nom) or fait
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    if pan is not None and panneau_a_jour(pan.read_typetree()):
        orig = hp.original(PANNEAUX, pan)
        if orig is None:
            print(f"panneau {PANNEAU} : pas de sauvegarde d'origine, rien fait")
        else:
            pan.save_typetree(orig)
            nb._dirty.add(PANNEAUX)
            fait = True
            print(f"panneau {PANNEAU} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    case, fen = ouvrir(MODELE), ouvrir(FENETRE)
    pan = mono(nb.env_of(PANNEAUX), PANNEAU)
    if case is None or fen is None or pan is None:
        print(f"{MODELE}, {FENETRE} ou le panneau des vacances introuvable")
        return
    t = case[3]
    if any(t.name(r) == NOM for r in marques(t)):
        print(f"{MODELE} : icône vacances présente (à jour, v{VERSION})")
    else:
        print(f"{MODELE} : " + ("ANCIENNE version" if marques(t) else "absente"))
    tf = fen[3]
    print(f"{FENETRE} : " + ("écriture de la date présente (à jour)" if any(tf.name(r) == NOM_FENETRE for r in marques(tf))
                             else ("ANCIENNE version" if marques(tf) else "d'origine")))
    print(f"panneau {PANNEAU} : " + ("paramètres présents" if panneau_a_jour(pan.read_typetree()) else "d'origine"))
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
            print("[Kinito] Vacances jour : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
