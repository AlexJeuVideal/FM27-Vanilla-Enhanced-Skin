"""Entraînement > Entraînement individuel, vue Détails : vues personnalisables (largeurs des colonnes GARDÉES), comme la
Base de données des joueurs. Demande du joueur (2026-11-26) : « les vues ont pas l'air de se save ».

Relevé (2026-11-26, rien de deviné) : FM n'enregistre les largeurs que dans une VUE PERSO (SaveAndApplyCustomView,
ColumnWidths de la vue) ; il ne garde seul que le tri (sorted-column-persistence-key). Un tableau sur une vue fixe
(InitFunction 446475dd, sans collection) oublie donc la largeur en quittant l'écran. Aucune des 65 collections de vues
de FM n'est libre ; PlayerIndividualTrainingTableCollection-PhoneLandscape est celle que FM a faite pour CET écran en
version téléphone (citée seulement par TeamIndividualTrainingTool, jamais affichée sur PC).

Recette = celle de kinito_capitaines_vues (validée en jeu) :
- collection (ui-tableviews) : ses vues = la vue Détails de FM (IndividualTrainingDetailedViewTable, telle que la
  laissent entrainement_pouces et 26.15) ; m_customViewDisplayName / m_customViewNamePrefix recopiés de la recherche
  de joueurs (PlayerSearchResultsViewCollection). Pas de menu « Insérer colonne » (fabrique d'entraînement, pas celle
  des joueurs). Retirer la remet d'origine.
- tableaux de la vue Détails (celui de FM et les copies Kinito du mode Large, TeamIndividualTrainingBlock) :
  InitFunction « depuis une collection » de SquadCaptainsBlock #FilteredPlayersTable (f93b92de : GUID de la collection,
  variable de la vue choisie), ContextMenuData de la recherche (bd30edff : clic droit des en-têtes), déplacement et
  largeur réglables, ViewDropdownName « ViewDropdown ».
- variable VAR (référence, type 1513318467 comme selectedView des Capitaines) déclarée dans le composant de variables
  de la racine de l'écran.
- menu des vues : l'instance TableViewDropdown de SquadCaptainsBlock recopiée dans #Header (vue Détails) avant
  #Filter, sa liste de choix sur notre collection ; dans un SIVisible sur PRET (fausse au départ, AlwaysInstantiate)
  qu'un SIDelayEvent passe à vrai DELAI s après l'ouverture (relié avant le tableau, le menu n'aurait pas ses actions :
  mesuré par Kinito pour les rapports).
Appelé par kinito_largeur_liste (dernier à écrire l'écran) : poser() après ses tableaux, retirer() avant les siens.
"""
import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import decode_args, encode_args  # noqa: E402

VERSION = 2   # v2 (2026-11-26) : v1 VUE EN JEU : liste VIDE (menu présent, « Détails », aucune ligne ni en-tête). Cause
# trouvée : la vue Détails est un sous-composant (ComponentElement dans #ViewContent) ; VAR / PRET étaient déclarées sur
# la racine de l'écran, hors de sa portée. v2 : déclarées dans le composant de la vue Détails (celui qui contient #Header
# et les tableaux), délai posé dedans. Et demande du joueur : menu des vues INVISIBLE (« on va jamais l'utiliser ») : il
# reste là (FM en a besoin pour créer / reprendre la vue perso quand on règle une largeur), enveloppe de taille 0 cachée.
COLLECTION = "PlayerIndividualTrainingTableCollection-PhoneLandscape"
VUE = "IndividualTrainingDetailedViewTable"
SOURCE_COLLECTION = "PlayerSearchResultsViewCollection"
SOURCE_ECRAN, SOURCE_TABLEAU = "SquadCaptainsBlock", "FilteredPlayersTable"
GUID_CAPITAINES = "a0216e8d74ac92642ae8716ff6ebb02c"     # sa collection, dans son InitFunction et son menu
VAR_CAPITAINES = "selectedView"
SOURCE_MENU_ALIAS = "TableViewDropdown"
MENU_RECHERCHE = "bd30edffabc96284cbfee63884ed3d7f"       # ContextMenuData de la recherche de joueurs
FABRIQUE = "576f87703a70f31439d7cab20456e517"            # PlayerIndividualTrainingTableFactory
VAR = "uipickervueindiv"
PRET = "uipickervueindivprete"
DELAI = 0.5
PREFIXE = "UIPickerVuesIndiv"
NOM_ENVELOPPE = f"{PREFIXE}-menu-v{VERSION}"
NOM_DELAI = f"{PREFIXE}-delai-v{VERSION}"
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
TYPE_VUE = 1513318467
NOM_VUE = 43280   # texte FM « Détaillé » (onglet #TabDetailed de l'écran, DebugDisplay « Detailed »)
import arbre  # noqa: E402
arbre.PROPRIETES.setdefault("opacity", (458767, 2))   # StylePropertyId Opacity (comme moteur_graphes)
CACHE = {"position": "absolute", "width": 0, "height": 0, "overflow": "hidden", "opacity": 0.0}


# ---------- collection (ui-tableviews) ----------
def _monos(env):
    out = {}
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                out[o.peek_name()] = o
            except Exception:
                pass
    return out


def guid_collection(env):
    ab = next(o for o in env.objects if o.type.name == "AssetBundle").read_typetree()
    pid = _monos(env)[COLLECTION].path_id
    for guid, info in ab["m_Container"]:
        if any(x["m_PathID"] == pid for x in
               ab["m_PreloadTable"][info["preloadIndex"]:info["preloadIndex"] + info["preloadSize"]]):
            return guid
    return None


def collection_voulue(env):
    """(objet, typetree voulu) ; None si un morceau manque"""
    m = _monos(env)
    if not all(n in m for n in (COLLECTION, VUE, SOURCE_COLLECTION)):
        return None
    o = m[COLLECTION]
    tt = hp.original(VUES, o) or o.read_typetree()
    src = m[SOURCE_COLLECTION].read_typetree()
    if not tt.get("m_tableViewSettings") or not src.get("m_customViewDisplayName", {}).get("GameID"):
        return None
    vue = m[VUE]
    entree = copy.deepcopy(tt["m_tableViewSettings"][0])
    entree["PropertyValue"]["m_PathID"] = vue.path_id
    entree["DisplayValue"] = copy.deepcopy(vue.read_typetree()["m_tableView"]["m_viewName"])
    if not entree["DisplayValue"].get("GameID"):   # vue sans nom : celui de l'onglet « Détaillé » de l'écran
        entree["DisplayValue"] = {"GameID": NOM_VUE}
    tt["m_tableViewSettings"] = [entree]
    tt["m_customViewDisplayName"] = copy.deepcopy(src["m_customViewDisplayName"])
    tt["m_customViewNamePrefix"] = copy.deepcopy(src["m_customViewNamePrefix"])
    tt["m_contextMenuData"] = []
    return o, tt


def collection_a_jour(env):
    x = collection_voulue(env)
    return x is not None and x[0].read_typetree() == x[1]


def collection_poser(env):
    """True si changé ; None si introuvable"""
    x = collection_voulue(env)
    if x is None:
        return None
    o, tt = x
    if o.read_typetree() == tt:
        return False
    o.save_typetree(tt)
    return True


def collection_d_origine(env):
    o = _monos(env).get(COLLECTION)
    orig = o and hp.original(VUES, o)
    return orig is None or o.read_typetree() == orig


def collection_retirer(env):
    o = _monos(env).get(COLLECTION)
    orig = o and hp.original(VUES, o)
    if orig is None or o.read_typetree() == orig:
        return False
    o.save_typetree(orig)
    return True


# ---------- l'écran ----------
def _texte(s):
    b = s.encode()
    return bytes([1, len(b)]) + b


class Sources:
    def __init__(self, guid):
        o = ouvrir(SOURCE_ECRAN, depart_original=True)
        self.tc = o and o[3]
        self.tt_c = o and o[2]
        tc = self.tc
        tab = tc and next((r for r in tc.walk() if typ(tc, r) == "StreamedTable"
                           and tc.sd(r).get("name") == SOURCE_TABLEAU), None)
        self.menu = tc and next((r for r in tc.walk() if tc.elem(r).get("m_TemplateAlias") == SOURCE_MENU_ALIAS), None)
        self.using = tc and next((u for u in o[2].get("m_Usings") or [] if u.get("alias") == SOURCE_MENU_ALIAS), None)
        self.init = None
        if tab is not None:
            f = copy.deepcopy(tc.sd(tab)["InitFunction"])
            args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            ok = 0
            for a in args:
                if bytes(a[0]).endswith(b"AssetReferenceVisualArg") and GUID_CAPITAINES.encode() in bytes(a[1]):
                    a[1] = bytes(a[1]).replace(GUID_CAPITAINES.encode(), guid.encode())
                    ok += 1
                elif bytes(a[0]).endswith(b"BindingPath]") and bytes(a[1]) == _texte(VAR_CAPITAINES):
                    a[1] = _texte(VAR)
                    ok += 1
            if ok == 2:
                f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
                self.init = f
        import kinito_capitaines_vues as kcv   # SIVisible / SIDelayEvent de FM et format des événements (lus seulement)
        self.kcv = kcv
        self.k = kcv.Sources()

    def manque(self):
        return [n for n, v in (("tableau des Capitaines", self.init), ("menu des vues", self.menu),
                               ("déclaration du menu", self.using)) if v is None] + \
            ([] if self.k.ok() else ["SIVisible / SIDelayEvent de FM"])


def _vars(t, r):
    """données du BindingVariablesComponent de l'élément r (None s'il n'en a pas)"""
    sd = t.sd(r) if isinstance(t.sd(r), dict) else {}
    for c in sd.get("m_components") or []:
        if "BindingVariablesComponent" in t.refs[c["rid"]]["type"]["class"]:
            return t.refs[c["rid"]].setdefault("data", {})
    return None


def _composant_vue(t, header):
    """(élément, données de ses variables) : le ComponentElement le plus proche au-dessus de #Header (la vue Détails,
    qui contient aussi les tableaux), avec des variables déclarées (celle du mode Large de kinito_largeur_liste)"""
    r = t.parent.get(header)
    while r is not None:
        if typ(t, r) == "ComponentElement":
            d = _vars(t, r)
            return (r, d) if d is not None else None
        r = t.parent.get(r)
    return None


def _tous_vars(t):
    return [d for d in (_vars(t, r) for r in t.walk()) if d is not None]


def _a_nous(t, r):
    return t.name(r).startswith(PREFIXE)


def _menu(t):
    return [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == SOURCE_MENU_ALIAS and _a_nous(t, t.parent.get(r))]


def collection_citee(t, r, guid):
    f = t.sd(r).get("InitFunction") or {}
    return guid.encode() in bytes(((f.get("m_inputs") or {}).get("m_variable") or {}).get("m_argumentBytes") or [])


def poser(t, tt, tableaux, guid):
    """tableaux : ceux de la vue Détails ; messages (« introuvable » = rien à enregistrer)"""
    src = Sources(guid)
    if src.manque():
        return [f"vues perso : morceaux de FM introuvables : {', '.join(src.manque())}"]
    if not tableaux or any((t.sd(r).get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE for r in tableaux):
        return ["vues perso : tableaux de la vue Détails introuvables"]
    header = next((r for r in t.walk() if t.name(r) == "Header"), None)
    filtre = header is not None and next((k for k in t.children(header) if t.name(k) == "Filter"), None)
    cv = header is not None and _composant_vue(t, header)
    if not cv or filtre is None or not all(r in set(t.walk(cv[0])) for r in tableaux):
        return ["vues perso : variables de l'écran ou #Header / #Filter introuvables"]
    comp, d = cv
    for r in tableaux:
        sd = t.sd(r)
        for k, v in (("InitFunction", copy.deepcopy(src.init)), ("ViewDropdownName", "ViewDropdown"),
                     ("AllowColumnResizing", 1), ("AllowColumnReordering", 1),
                     ("ContextMenuData", {"m_AssetGUID": MENU_RECHERCHE, "m_SubObjectName": "", "m_SubObjectType": ""})):
            sd[k], sd[k + "_UxmlAttributeFlags"] = v, 1
    rv = d.setdefault("ReferenceVariables", [])
    if not any(v.get("m_name") == VAR for v in rv):
        rv.append({"m_type": {"id": TYPE_VUE}, "m_initToNull": 0, "m_name": VAR})
    d["ReferenceVariables_UxmlAttributeFlags"] = 1
    vv = d.setdefault("ValueVariables", [])
    if not any(v.get("m_name") == PRET for v in vv):
        vv.append({"m_name": PRET, "m_scopeValue": {"m_serializedData": "Bool|0|"}})
    d["ValueVariables_UxmlAttributeFlags"] = 1
    # le menu, dans son enveloppe (SIVisible sur PRET), avant #Filter
    k = src.kcv
    rang = [x["rid"] for x in t.elem(header)["m_Children"]].index(filtre)
    env = t.clone(src.k.visible, header, index=rang, src=src.k.tv)
    for x in list(t.children(env)):
        t.remove(x)
    k._parent_id(t, env)
    k._nommer(t, env, NOM_ENVELOPPE)
    sd = t.sd(env)
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = PRET
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 0, 1
    sd["AlwaysInstantiate"], sd["AlwaysInstantiate_UxmlAttributeFlags"] = 1, 1
    t.elem(env)["m_Classes"], t.elem(env)["m_RuleIndex"] = [], -1
    t.styles.style(t, env, CACHE)   # v2 : menu là mais invisible (taille 0, contenu rogné, transparent)
    m = t.clone(src.menu, env, src=src.tc)
    k._parent_id(t, m)
    ovr = t.elem(m)["m_SerializedDataOverride"]
    fait = 0
    for o in ovr:
        dd = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
        f = dd.get("BindChoicesFunction")
        if isinstance(f, dict):
            b = bytes(f["m_inputs"]["m_variable"]["m_argumentBytes"])
            if GUID_CAPITAINES.encode() in b:
                f["m_inputs"]["m_variable"]["m_argumentBytes"] = list(b.replace(GUID_CAPITAINES.encode(), guid.encode()))
                fait += 1
    if fait != 1:
        return ["vues perso : liste de choix du menu des vues de forme inattendue (introuvable)"]
    if not any(u.get("alias") == SOURCE_MENU_ALIAS for u in tt.get("m_Usings") or []):
        tt.setdefault("m_Usings", []).append(copy.deepcopy(src.using))
    # le délai : à la fin du composant de la vue Détails (v2 : il écrit PRET dans sa portée)
    dl = t.clone(src.k.delai, comp, src=src.k.td)
    k._parent_id(t, dl)
    k._nommer(t, dl, NOM_DELAI)
    t.elem(dl)["m_Classes"], t.elem(dl)["m_RuleIndex"] = [], -1
    t.styles.style(t, dl, {"position": "absolute", "width": 0, "height": 0})
    s = t.sd(dl)
    s["m_duration"], s["m_duration_UxmlAttributeFlags"] = float(DELAI), 1
    s["TransitionEvents"] = {"m_bytes": k.liste([k.copier("const.True", PRET)])}
    s["TransitionEvents_UxmlAttributeFlags"] = 1
    return [f"vues perso : {len(tableaux)} tableaux de la vue Détails sur {COLLECTION} (vues perso, largeurs "
            f"gardées), menu des vues caché dans #Header, relié {DELAI} s après l'ouverture"]


def a_jour(t, tableaux, guid):
    header = next((r for r in t.walk() if t.name(r) == "Header"), None)
    cv = header is not None and _composant_vue(t, header)
    noms = [t.name(r) for r in t.walk()]
    return (bool(tableaux) and all(collection_citee(t, r, guid) and t.sd(r).get("ViewDropdownName") == "ViewDropdown"
                                   for r in tableaux)
            and NOM_ENVELOPPE in noms and NOM_DELAI in noms and len(_menu(t)) == 1 and bool(cv)
            and any(v.get("m_name") == VAR for v in cv[1].get("ReferenceVariables") or []))


def retirer(t, tableau_fm, champs_fm):
    """nos éléments retirés, nos variables, et le tableau de FM rendu (champs_fm : ses champs d'origine) ; True si
    changé"""
    fait = False
    for r in [r for r in t.walk() if _a_nous(t, r)]:
        if r in t.parent:
            t.remove(r)
            fait = True
    for d in _tous_vars(t):   # v1 les déclarait sur la racine, v2 dans la vue Détails
        for k, n in (("ReferenceVariables", VAR), ("ValueVariables", PRET)):
            if not any(v.get("m_name") == n for v in d.get(k) or []):
                continue
            d[k] = [v for v in d.get(k) or [] if v.get("m_name") != n]
            fait = True
    if tableau_fm is not None and champs_fm:
        sd = t.sd(tableau_fm)
        for k, v in champs_fm.items():
            if sd.get(k) != v:
                sd[k] = copy.deepcopy(v)
                fait = True
    return fait


CHAMPS = ("InitFunction", "ViewDropdownName", "AllowColumnReordering", "ContextMenuData")
