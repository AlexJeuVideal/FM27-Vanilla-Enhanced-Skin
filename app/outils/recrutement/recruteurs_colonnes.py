"""Recrutement > Recherches ciblées > Recruteur / Analyste affecté : tableaux des recruteurs et des analystes
déverrouillés (largeur et ordre des colonnes, clic droit sur les en-têtes) et, depuis la v3, VUES PERSONNALISABLES
(menu des vues, Insérer colonne avec toutes les infos du staff, colonnes de base toujours réinsérables).

Relevé dans le jeu (2026-11-26, rien de deviné) : la fenêtre « Recruteur affecté » / « Analyste affecté » =
RecruitmentFocusAssignScoutAnalystDialog (bundle gameworld preload), racine BindingRoot (paramètres focusitem, type,
team ; champs ReferenceProperties / ValueProperties pour déclarer des variables), deux StreamedTable #scouts-table et
#analysts-table (fabrique RecruitmentFocusStaffTableFactory, 9 colonnes, lignes Team.TeamContainer.Scouts /
.Analysts = du staff, paramètre « binding » du même type que la recherche de staff), chacun sur UNE vue fixe
(InitFunction 446475dd) : RecruitmentFocusScoutsTable / RecruitmentFocusAnalystsTable (ui-tableviews).
- v1 / v2 : réglages de NationScreenOverviewBlock #StaffContractsTable (AllowColumnResizing 1, ResizeColumnWidthsToFit
  1, ContextMenuData bd30edff… = menu des en-têtes) + AllowColumnReordering 1 ; 2 colonnes de la fabrique ajoutées à
  chaque vue avant « Connaissance du monde » ; minimums à 16 px.
- v3 (demande du joueur 2026-11-26 : « vue full custom », « full infos staff », « les trucs de base toujours
  sélectionnables ») — recette de la recherche de staff de FM (PersonSearchMainContentBlock #nonplayertable) :
  * fabrique : les 173 colonnes de NonPlayerTableFactory (recherche de staff) qui ne lisent que la ligne
    (« binding. ») ajoutées à RecruitmentFocusStaffTableFactory (ses 9 colonnes gardées : Rôle, Connaissance du
    monde, Recherches en cours… restent les siennes) ;
  * collections de vues (aucune libre dans FM : deux citées seulement par des blocs téléphone, jamais affichés sur PC)
    TransferWindowTableViewCollection (recruteurs) et PlayerStatsExpandedTableViewCollection (analystes) : une vue
    de base chacune (celle de FM, nom = titre de la fenêtre), vues perso (noms de la recherche de staff), menu
    « Insérer colonne » = 1er groupe « Recruteur / Analyste affecté » (les 9 colonnes de la fenêtre : toujours
    remettables) + les groupes de la recherche de staff, réduits aux colonnes présentes, sans ceux à Requirement
    (plantage vu chez Kinito, rapports_vues v6) ;
  * tableaux : InitFunction « depuis une collection » de #nonplayertable (GUID et variable remplacés),
    ViewDropdownName (ViewDropdown / ViewAltDropdown : deux menus distincts), ScrollViewMode 2 et
    HorizontalScrollerVisibility 0 (défilement horizontal, comme la recherche) ;
  * menus des vues : TableViewDropdown (de SquadCaptainsBlock) et TableViewAltDropdown (#staff-view-dropdown de
    PersonSearchTableTopSection), liste de choix sur notre collection. CES MODÈLES LISENT ET ÉCRIVENT « selectedView »
    (BindingExpect + SelectionValueBinding, relevé) : chacun dans un BindingRemapper selectedView -> notre variable
    (comme #shortlist-view-dropdown-remapper de FM). Chaque menu entre la case « N'importe quel… » et son tableau, dans
    un SIVisible sur PRET qu'un SIDelayEvent passe à vrai 0,5 s après l'ouverture (relié après le tableau, comme chez
    Kinito) ; variables déclarées sur la BindingRoot.
Fichiers : le modèle (seul propriétaire : appliquer repart de l'original, retirer le remet) ; ui-tableviews (partagé) :
nos 2 vues et nos 2 collections, refaites depuis leur original ; ui-tablefactories (propriétaire moral_icone_seule, qui
repart de l'original : ce script le suit, SUIVANTS) : notre fabrique seule, refaite depuis son original.
Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import decode_args, encode_args  # noqa: E402
import colonnes_reglables as cr  # noqa: E402

VERSION = 7   # v7 (2026-11-26) : v6 VUE : « Taille automatique » (clic droit) toujours 3 pays et demi : elle répartit la
#               largeur au prorata des m_defaultWidth de la FABRIQUE (relevé sur la capture : 140 / 100 -> 206 / 148 px),
#               pas de la vue -> worldknowledge m_defaultWidth = LARGEUR_MONDE aussi dans la fabrique
# v6 (2026-11-26) : v5 VUE (fenêtre élargie OK) ; le joueur : « Connaissance du monde » assez large pour 5
#               pays, comme sa vue perso (« Copie de », largeur 288,75) : LARGEUR_MONDE dans les 2 vues de base (FM : 140)
# v5 (2026-11-26) : v4 VUE (« niquel ») ; le joueur : « élargir cet écran » (recruteurs et analystes,
#               même fenêtre) : #notifications-modal-dialog-default-default-unpacked (largeur de la classe partagée
#               notifications-modal-large-default-assign-a-scout) -> style intégré, largeur LARGEUR_FENETRE de l'écran
# v4 (2026-11-26) : v3 VUE EN JEU (« ça marche », vue « Copie de… » créée par FM) ; le joueur : menu des
#               vues « trop gros » -> en haut à droite, sur la ligne de la case « Affecter n'importe quel… » (enveloppe
#               en position absolue dans le conteneur, largeur LARGEUR_MENU)
# v3 (2026-11-26) : vues personnalisables (voir plus haut) ; v2 : minimums à 16 px
LARGEUR_MENU = 220.0   # px
LARGEUR_MONDE = 290.0   # v6 : colonne worldknowledge des vues de base (5 pays)
LARGEUR_FENETRE = 85.0   # v5 : % de l'écran (FM : ~60 %)
FENETRE = "notifications-modal-dialog-default-default-unpacked"
MODELE = "RecruitmentFocusAssignScoutAnalystDialog"
TABLEAUX = ("scouts-table", "analysts-table")
FABRIQUE = "5e888faab463ba740956f9230aa5fe90"            # RecruitmentFocusStaffTableFactory
FABRIQUE_NOM = "RecruitmentFocusStaffTableFactory"
SOURCE_FABRIQUE = "NonPlayerTableFactory"                # recherche de staff
SOURCE_TABLEAU = ("NationScreenOverviewBlock", "StaffContractsTable")
REGLAGES = {"AllowColumnResizing": 1, "AllowColumnReordering": 1, "ResizeColumnWidthsToFit": 1}
MENU = "ContextMenuData"                                  # recopié du tableau source
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
AJOUTS = {   # vue -> colonnes ajoutées (avant AVANT)
    "RecruitmentFocusScoutsTable": ["analysingdata", "tacticalknowledge"],
    "RecruitmentFocusAnalystsTable": ["judgepotential", "adaptability"],
}
AVANT = "worldknowledge"
MARKER = os.path.join(backup.BACKUP_DIR, "recruteurs_colonnes.actif")
# ---- v3 ----
RECHERCHE = ("PersonSearchMainContentBlock", "nonplayertable")   # tableau de la recherche de staff (FM)
COLLECTION_RECHERCHE = "NonPlayerSearchResultsViewCollection"
GUID_RECHERCHE = "2004e3038f39e474a800ae16ebd4490b"
VAR_FM = "selectedView"           # nom lu / écrit par les modèles des menus des vues
TYPE_VUE = 1513318467             # type des variables de vue (selectedView des Capitaines)
PRET = "uipickerrecruteursvuesprete"
DELAI = 0.5
PREFIXE = "UIPickerRecruteurs"
NOM_DELAI = f"{PREFIXE}-delai-v{VERSION}"
CAPITAINES = "SquadCaptainsBlock"                           # son #TableViewDropdown (GUID a0216e8d… dans ses choix)
GUID_CAPITAINES = "a0216e8d74ac92642ae8716ff6ebb02c"
HAUT_RECHERCHE = ("PersonSearchTableTopSection", "staff-view-dropdown")   # TableViewAltDropdown (GUID 2004e303…)
SOURCE_REMAP = ("PersonSearchTableTopSection", "shortlist-view-dropdown-remapper")
REFTYPE = {"class": "SIDropdownElement`1[[System.String, mscorlib]]", "ns": "SI.Bindable", "asm": "SI.Bindable"}
# tableau -> (collection, vue de base, variable, modèle du menu, nom du menu, titre FM (Recruteur / Analyste affecté),
#             conteneur)
CIBLES = {
    "scouts-table": ("TransferWindowTableViewCollection", "RecruitmentFocusScoutsTable", "uipickervuerecruteurs",
                     "TableViewDropdown", "ViewDropdown", 19732, "SIVisiable-scouts-container"),
    "analysts-table": ("PlayerStatsExpandedTableViewCollection", "RecruitmentFocusAnalystsTable",
                       "uipickervueanalystes", "TableViewAltDropdown", "ViewAltDropdown", 19733,
                       "SIVisiable-analysts-container"),
}


def tableaux(t):
    return [r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") in TABLEAUX]


def menu_source():
    o = ouvrir(SOURCE_TABLEAU[0], depart_original=True)
    if o is None:
        return None
    t = o[3]
    r = next((r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") == SOURCE_TABLEAU[1]), None)
    m = r is not None and t.sd(r).get(MENU)
    return copy.deepcopy(m) if m and m.get("m_AssetGUID") else None


def mono(env, nom):
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == nom:
                    return o
            except Exception:
                continue
    return None


def ids(tt):
    return [c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]]


def construire_vue(tt, nom):
    """tt : la vue d'origine. Ajoute les colonnes manquantes avant AVANT (réglages d'une colonne de FM)."""
    cfg = tt["m_tableView"]["m_tableConfig"]
    if AVANT not in ids(tt) or not cfg:
        return f"{nom} : colonne {AVANT} introuvable"
    modele = next(c for c in cfg if c["m_columnID"] == "judgeability") if "judgeability" in ids(tt) else cfg[-1]
    for col in AJOUTS[nom]:
        if col in ids(tt):
            continue
        c = copy.deepcopy(modele)
        c["m_columnID"] = col
        c["m_columnMetadata"]["m_titleTranslationIdOverride"] = {"GameID": 0}
        cfg.insert(ids(tt).index(AVANT), c)
    for c in cfg:   # v6
        if c["m_columnID"] == AVANT:
            c["m_columnMetadata"]["m_widthOverride"] = LARGEUR_MONDE
    cr.minimums_petits(cfg)   # v2 : colonnes réductibles jusqu'à 16 px
    return None


# ---------- v3 : la fabrique ----------
def _racines(r):
    out = set()
    for k in ("m_valueBindings", "m_headerValueBindings", "m_footerValueBindings"):
        for b in r.get(k) or []:
            p = b["to"]["m_path"]
            if p:
                out.add(p.split(".")[0])
    return out


def fabrique_voulue(ef):
    """(objet, typetree voulu) ; None si introuvable"""
    o, src = mono(ef, FABRIQUE_NOM), mono(ef, SOURCE_FABRIQUE)
    if o is None or src is None:
        return None
    tt = hp.original(FABRIQUES, o) or o.read_typetree()
    st = hp.original(FABRIQUES, src) or src.read_typetree()
    for r in tt["m_rowData"]:   # v7 : largeur de base (Taille automatique) de Connaissance du monde
        if r["m_id"] == AVANT:
            r["m_defaultWidth"] = LARGEUR_MONDE
    cs = _separateur()
    deja = {r["m_id"] for r in tt["m_rowData"]}
    for r in st["m_rowData"]:
        if r["m_id"] not in deja and _racines(r) <= {"binding", "const"} and not (cs and cs.a_nous(r["m_id"])):
            tt["m_rowData"].append(copy.deepcopy(r))
            deja.add(r["m_id"])
    if cs and cs.actif():   # comme colonnes_separateur (qui passe sur toutes les fabriques) : ses colonnes à la fin
        reste = [r for r in tt["m_rowData"] if not cs.a_nous(r["m_id"])]
        tt["m_rowData"] = reste + [cs.colonne(reste[0], c, k) for c, k in cs.toutes().items()]
    return o, tt


def _separateur():
    try:
        import colonnes_separateur as cs
        return cs
    except Exception:
        return None


# ---------- v3 : les collections ----------
def _guid(env, o):
    ab = next(x for x in env.objects if x.type.name == "AssetBundle").read_typetree()
    for guid, info in ab["m_Container"]:
        if info["asset"]["m_PathID"] == o.path_id:
            return guid
    return None


def _menu_colonnes(src_tt, colonnes, base, titre, fab_base):
    """(groupes, refs) du menu « Insérer colonne » : groupe de base puis ceux de la recherche de staff réduits à
    colonnes (sans entrée à Requirement)"""
    refs_src = {r["rid"]: r["data"] for r in src_tt["references"]["RefIds"]}
    refs = []

    def ajoute(data):
        rid = len(refs) + 1
        refs.append({"rid": rid, "type": copy.deepcopy(REFTYPE), "data": data})
        return rid

    def filtre(e):
        """copie de e (enfants filtrés) ou None"""
        if (e.get("Requirement") or {}).get("m_PathID"):
            return None
        kids = []
        for c in e.get("ChildList") or []:
            k = filtre(refs_src[c["rid"]])
            if k is not None:
                kids.append(k)
        if e.get("ChildList"):
            if not kids:
                return None
        elif e.get("PropertyValue") not in colonnes:
            return None
        n = copy.deepcopy(e)
        n["ChildList"] = kids
        return n

    def poser(e):
        e["ChildList"] = [{"rid": ajoute(poser(k))} for k in e["ChildList"]]
        return e

    modele = copy.deepcopy(next(r for r in refs_src.values() if not r.get("ChildList")))
    groupe = copy.deepcopy(src_tt["m_contextMenuData"][0])
    groupe.update({"debug_name": "", "name": "Base", "DisplayValue": {"GameID": titre}, "PropertyValue": "",
                   "Requirement": {"m_FileID": 0, "m_PathID": 0}, "ChildList": []})
    for cid in base:
        e = copy.deepcopy(modele)
        e.update({"debug_name": "", "name": cid, "DisplayValue": {"GameID": fab_base[cid]}, "PropertyValue": cid,
                  "Requirement": {"m_FileID": 0, "m_PathID": 0}, "ChildList": []})
        groupe["ChildList"].append(e)
    groupes = [groupe] + [g for g in (filtre(g) for g in src_tt["m_contextMenuData"]) if g is not None]
    return [poser(g) for g in groupes], refs


def collections_voulues(ev, fab_tt):
    """{tableau: (objet, typetree voulu, guid)} ; None si un morceau manque"""
    src = mono(ev, COLLECTION_RECHERCHE)
    if src is None or fab_tt is None:
        return None
    src_tt = hp.original(VUES, src) or src.read_typetree()
    colonnes = {r["m_id"] for r in fab_tt["m_rowData"]}
    fab_base = {r["m_id"]: r["m_translationID"]["GameID"] for r in fab_tt["m_rowData"]}
    out = {}
    for tab, (col, vue, _, _, _, titre, _) in CIBLES.items():
        o, v = mono(ev, col), mono(ev, vue)
        if o is None or v is None:
            return None
        guid = _guid(ev, o)
        tt = hp.original(VUES, o) or o.read_typetree()
        if not guid or not tt.get("m_tableViewSettings") or not src_tt.get("m_tableViewSettings"):
            return None
        e = copy.deepcopy(src_tt["m_tableViewSettings"][0])
        e.update({"debug_name": "", "name": "", "ChildList": [], "DisplayValue": {"GameID": titre},
                  "Requirement": {"m_FileID": 0, "m_PathID": 0}})
        e["PropertyValue"] = {"m_FileID": 0, "m_PathID": v.path_id}
        tt["m_tableViewSettings"] = [e]
        tt["m_customViewDisplayName"] = copy.deepcopy(src_tt["m_customViewDisplayName"])
        tt["m_customViewNamePrefix"] = copy.deepcopy(src_tt["m_customViewNamePrefix"])
        groupes, refs = _menu_colonnes(src_tt, colonnes, base_colonnes(fab_tt), titre, fab_base)
        tt["m_contextMenuData"] = groupes
        tt.setdefault("references", {"version": 2, "RefIds": []})
        tt["references"]["RefIds"] = refs
        cs = _separateur()
        if cs and cs.actif():   # son groupe « Séparateurs », comme il le met sur tous les menus Insérer colonne
            cs.menu_voulu(tt)
        out[tab] = (o, tt, guid)
    return out


def base_colonnes(fab_tt):
    """les colonnes de la fenêtre (celles de la fabrique d'origine, avant nos ajouts)"""
    return [r["m_id"] for r in fab_tt["m_rowData"][:BASE_N[0]]]


BASE_N = [9]


# ---------- v3 : le modèle ----------
def _texte(s):
    b = s.encode()
    return bytes([1, len(b)]) + b


class Sources:
    def __init__(self):
        o = ouvrir(RECHERCHE[0], depart_original=True)
        t = o and o[3]
        tab = t and next((r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") == RECHERCHE[1]),
                         None)
        self.tab = t.sd(tab) if tab is not None else None
        c = ouvrir(CAPITAINES, depart_original=True)
        self.tc = c and c[3]
        self.usings = {}
        self.menus = {}
        if self.tc:
            self.menus["TableViewDropdown"] = (self.tc, next((r for r in self.tc.walk()
                                                              if self.tc.elem(r).get("m_TemplateAlias") == "TableViewDropdown"), None), GUID_CAPITAINES)
            self.usings.update({u["alias"]: u for u in c[2].get("m_Usings") or []})
        h = ouvrir(HAUT_RECHERCHE[0], depart_original=True)
        self.th = h and h[3]
        if self.th:
            self.menus["TableViewAltDropdown"] = (self.th, next((r for r in self.th.walk()
                                                                 if self.th.name(r) == HAUT_RECHERCHE[1]), None), GUID_RECHERCHE)
            for u in h[2].get("m_Usings") or []:
                self.usings.setdefault(u["alias"], u)
            self.remap = next((r for r in self.th.walk() if self.th.name(r) == SOURCE_REMAP[1]
                               and typ(self.th, r) == "BindingRemapper"), None)
        else:
            self.remap = None
        import kinito_capitaines_vues as kcv   # SIVisible / SIDelayEvent de FM et format des événements (lus seulement)
        self.kcv = kcv
        self.k = kcv.Sources()

    def manque(self):
        m = [n for n, v in (("tableau de la recherche de staff", self.tab), ("remapper", self.remap)) if v is None]
        for a in ("TableViewDropdown", "TableViewAltDropdown"):
            if a not in self.menus or self.menus[a][1] is None or a not in self.usings:
                m.append(f"menu {a}")
        return m + ([] if self.k.ok() else ["SIVisible / SIDelayEvent de FM"])


def _init(src, guid, var):
    f = copy.deepcopy(src.tab["InitFunction"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    ok = 0
    for a in args:
        if bytes(a[0]).endswith(b"AssetReferenceVisualArg") and GUID_RECHERCHE.encode() in bytes(a[1]):
            a[1] = bytes(a[1]).replace(GUID_RECHERCHE.encode(), guid.encode())
            ok += 1
        elif bytes(a[0]).endswith(b"BindingPath]") and bytes(a[1]) == _texte(VAR_FM):
            a[1] = _texte(var)
            ok += 1
    if ok != 2:
        return None
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return f


def _vider(t, r, nom, src):
    for x in list(t.children(r)):
        t.remove(x)
    src.kcv._parent_id(t, r)
    src.kcv._nommer(t, r, nom)
    t.elem(r)["m_Classes"], t.elem(r)["m_RuleIndex"] = [], -1


def poser_modele(t, tt, src, guids, menu):
    """tout sur le modèle (parti de l'original) ; message d'erreur ou None"""
    rs = {t.sd(r).get("name"): r for r in tableaux(t)}
    racine = next((r for r in t.walk() if typ(t, r) == "BindingRoot"), None)
    if len(rs) != 2 or racine is None or any((t.sd(r).get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE
                                             for r in rs.values()):
        return f"tableaux ou racine de {MODELE} introuvables"
    conteneurs = {t.name(r): r for r in t.walk() if typ(t, r) == "SIVisible"}
    k = src.kcv
    for nom, r in rs.items():
        col, vue, var, alias, nom_menu, titre, cont = CIBLES[nom]
        if cont not in conteneurs:
            return f"{cont} introuvable"
        d = t.sd(r)
        for kk, v in REGLAGES.items():
            d[kk], d[kk + "_UxmlAttributeFlags"] = v, 1
        d[MENU], d[MENU + "_UxmlAttributeFlags"] = copy.deepcopy(menu), 1
        f = _init(src, guids[nom], var)
        if f is None:
            return "InitFunction de la recherche de staff de forme inattendue"
        for kk, v in (("InitFunction", f), ("ViewDropdownName", nom_menu),
                      ("ScrollViewMode", src.tab["ScrollViewMode"]),
                      ("HorizontalScrollerVisibility", src.tab["HorizontalScrollerVisibility"])):
            d[kk], d[kk + "_UxmlAttributeFlags"] = copy.deepcopy(v), 1
        # le menu : SIVisible (PRET) > BindingRemapper (selectedView -> var) > menu, après la case « N'importe quel… »
        c = conteneurs[cont]
        env = t.clone(src.k.visible, c, index=1, src=src.k.tv)
        _vider(t, env, f"{PREFIXE}-{nom}-menu-v{VERSION}", src)
        sd = t.sd(env)
        sd["Binding"]["m_kind"] = 1
        sd["Binding"]["m_direct"]["Path"]["m_path"] = PRET
        sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 0, 1
        sd["AlwaysInstantiate"], sd["AlwaysInstantiate_UxmlAttributeFlags"] = 1, 1
        t.styles.style(t, env, {"position": "absolute", "top": 0, "right": 0, "width": LARGEUR_MENU})   # v4
        rm = t.clone(src.remap, env, src=src.th)
        _vider(t, rm, f"{PREFIXE}-{nom}-remap-v{VERSION}", src)
        t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": VAR_FM, "to": {"m_path": var}, "type": {"id": 0}}]
        t.sd(rm)["Mappings_UxmlAttributeFlags"] = 1
        st, mr, gsrc = src.menus[alias]
        m = t.clone(mr, rm, src=st)
        k._parent_id(t, m)
        t.styles.copy_from(st.styles, t, m)
        fait = 0
        for ov in t.elem(m)["m_SerializedDataOverride"]:
            dd = t.refs[ov["m_SerializedData"]["rid"]].get("data") or {}
            bf = dd.get("BindChoicesFunction")
            if isinstance(bf, dict):
                b = bytes(bf["m_inputs"]["m_variable"]["m_argumentBytes"])
                if gsrc.encode() in b:
                    bf["m_inputs"]["m_variable"]["m_argumentBytes"] = list(b.replace(gsrc.encode(), guids[nom].encode()))
                    fait += 1
        if fait != 1:
            return f"liste de choix du menu {alias} de forme inattendue"
        if not any(u.get("alias") == alias for u in tt.get("m_Usings") or []):
            tt.setdefault("m_Usings", []).append(copy.deepcopy(src.usings[alias]))
    # v5 : la fenêtre plus large
    fen = next((r for r in t.walk() if t.name(r) == FENETRE), None)
    if fen is None:
        return f"#{FENETRE} introuvable"
    pc = {"unit": 2, "value": LARGEUR_FENETRE}
    t.styles.style(t, fen, {"width": pc, "max-width": pc})
    # variables sur la BindingRoot
    sd = t.sd(racine)
    rp = sd.setdefault("ReferenceProperties", [])
    for nom in rs:
        var = CIBLES[nom][2]
        if not any(v.get("m_name") == var for v in rp):
            rp.append({"m_type": {"id": TYPE_VUE}, "m_initToNull": 0, "m_name": var})
    sd["ReferenceProperties_UxmlAttributeFlags"] = 1
    vp = sd.setdefault("ValueProperties", [])
    if not any(v.get("m_name") == PRET for v in vp):
        vp.append({"m_name": PRET, "m_scopeValue": {"m_serializedData": "Bool|0|"}})
    sd["ValueProperties_UxmlAttributeFlags"] = 1
    # le délai, à la fin du cadre des tableaux
    cadre = t.parent[conteneurs[CIBLES["scouts-table"][6]]]
    dl = t.clone(src.k.delai, cadre, src=src.k.td)
    _vider(t, dl, NOM_DELAI, src)
    s = t.sd(dl)
    s["m_duration"], s["m_duration_UxmlAttributeFlags"] = float(DELAI), 1
    s["TransitionEvents"] = {"m_bytes": k.liste([k.copier("const.True", PRET)])}
    s["TransitionEvents_UxmlAttributeFlags"] = 1
    return None


def modele_a_jour(t, guids, menu):
    noms = {t.name(r) for r in t.walk()}
    rs = {t.sd(r).get("name"): r for r in tableaux(t)}
    if len(rs) != 2 or NOM_DELAI not in noms:
        return False
    for nom, r in rs.items():
        d = t.sd(r)
        b = bytes(((d.get("InitFunction") or {}).get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or [])
        if (not all(d.get(k) == v for k, v in REGLAGES.items()) or d.get(MENU) != menu or guids[nom].encode() not in b
                or f"{PREFIXE}-{nom}-menu-v{VERSION}" not in noms or f"{PREFIXE}-{nom}-remap-v{VERSION}" not in noms):
            return False
    return True


def _tout(ev, ef):
    """(vues {nom: (obj, tt)}, fabrique (obj, tt), collections) ; message si un morceau manque"""
    vues = {}
    for n in AJOUTS:
        v = mono(ev, n)
        if v is None:
            return f"vue {n} introuvable"
        tt = hp.original(VUES, v) or v.read_typetree()
        err = construire_vue(tt, n)
        if err:
            return err
        vues[n] = (v, tt)
    fab = fabrique_voulue(ef)
    if fab is None:
        return f"fabrique {FABRIQUE_NOM} ou {SOURCE_FABRIQUE} introuvable"
    orig = hp.original(FABRIQUES, fab[0]) or fab[0].read_typetree()
    BASE_N[0] = len(orig["m_rowData"])
    cols = collections_voulues(ev, fab[1])
    if cols is None:
        return "collections de vues introuvables"
    return vues, fab, cols


def cmd_appliquer():
    menu = menu_source()
    o = ouvrir(MODELE)
    ev, ef = nb.env_of(VUES), nb.env_of(FABRIQUES)
    x = _tout(ev, ef)
    if menu is None or o is None or isinstance(x, str):
        print("Recruteurs / analystes affectés : morceaux de FM introuvables (fenêtre, vues, fabrique ou menu des "
              f"en-têtes{' : ' + x if isinstance(x, str) else ''}), rien enregistré")
        return
    vues, fab, cols = x
    guids = {tab: c[2] for tab, c in cols.items()}
    if (modele_a_jour(o[3], guids, menu) and all(v.read_typetree() == tt for v, tt in vues.values())
            and fab[0].read_typetree() == fab[1] and all(c[0].read_typetree() == c[1] for c in cols.values())):
        print("Recruteurs / analystes affectés : déjà appliqué")
    else:
        src = Sources()
        if src.manque():
            print(f"Recruteurs / analystes affectés : morceaux de FM introuvables : {', '.join(src.manque())}, "
                  "rien enregistré")
            return
        o = ouvrir(MODELE, depart_original=True)
        bundle, obj, tto, t = o
        err = poser_modele(t, tto, src, guids, menu)
        if err:
            print(f"Recruteurs / analystes affectés : {err}, rien enregistré")
            return
        t.finish()
        t.styles.save()
        obj.save_typetree(tto)
        nb._dirty.add(bundle)
        for v, tt in vues.values():
            v.save_typetree(tt)
        for c in cols.values():
            c[0].save_typetree(c[1])
        nb._dirty.add(VUES)
        fab[0].save_typetree(fab[1])
        nb._dirty.add(FABRIQUES)
        nb.save_all()
        print(f"Recruteurs / analystes affectés : {MODELE} : colonnes redimensionnables et déplaçables, menu du clic "
              "droit sur les en-têtes, menu des vues au-dessus de chaque tableau")
        print(f"Recruteurs / analystes affectés : {FABRIQUE_NOM} : {len(fab[1]['m_rowData'])} colonnes "
              f"({len(fab[1]['m_rowData']) - BASE_N[0]} de la recherche de staff)")
        for tab, (c, tt, g) in cols.items():
            print(f"Recruteurs / analystes affectés : {tab} : collection {tt['m_Name']} (vues perso, Insérer colonne : "
                  f"{len(tt['m_contextMenuData'])} groupes, le 1er = les colonnes de la fenêtre)")
        for n, (v, tt) in vues.items():
            print(f"Recruteurs / analystes affectés : {n} : colonnes {', '.join(ids(tt))}")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    o = ouvrir(MODELE)
    if o is not None:
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        elif obj.read_typetree() != orig:
            obj.save_typetree(orig)
            nb._dirty.add(bundle)
            fait = True
            print(f"{MODELE} : remis d'origine")
    for chemin, noms in ((VUES, list(AJOUTS) + [c[0] for c in CIBLES.values()]), (FABRIQUES, [FABRIQUE_NOM])):
        env = nb.env_of(chemin)
        for n in noms:
            v = mono(env, n)
            orig = v and hp.original(chemin, v)
            if orig is not None and v.read_typetree() != orig:
                v.save_typetree(orig)
                nb._dirty.add(chemin)
                fait = True
                print(f"{n} : remis d'origine (le reste du bundle n'est pas touché)")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        noms = {t.name(r) for r in t.walk()}
        print(f"{MODELE} : " + ("vues personnalisables" if NOM_DELAI in noms else "pas de vues personnalisables (v3)"))
    env = nb.env_of(VUES)
    for n in AJOUTS:
        v = mono(env, n)
        print(f"{n} : " + ("introuvable" if v is None else ", ".join(ids(v.read_typetree()))))
    ef = nb.env_of(FABRIQUES)
    f = mono(ef, FABRIQUE_NOM)
    print(f"{FABRIQUE_NOM} : " + ("introuvable" if f is None else f"{len(f.read_typetree()['m_rowData'])} colonnes"))
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
            print("Recruteurs / analystes affectés : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
