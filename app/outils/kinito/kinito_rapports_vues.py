"""[AJOUT KINITO] Rapports des recruteurs : des vues personnalisables, comme la Base de données des joueurs.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : « sur cet écran [Recrutement > Vue d'ensemble, Rapports des recruteurs], je peux
choisir parmi des vues toutes faites, mais je ne peux pas construire ma propre vue comme ailleurs ».

Relevé dans le jeu (2026-11-12, rien de deviné) : le tableau des recommandations (StreamedTable #table de
RecruitmentContentBlock et de PlayerRecommendationsMainBlock, données Team.Manager.ScoutingCentreActions.Players) et
celui de la Base de données des joueurs (PersonSearchMainContentBlock #playertable) utilisent la MÊME fabrique de
colonnes, PlayerTableFactory (49c25af4…) : toutes les colonnes de la recherche existent pour les recommandations.
Ce qui manque aux recommandations, et que la recherche a :
- sur le tableau : ContextMenuData = StreamedTableContextMenuData (bd30edff… : le menu du clic droit sur les en-têtes —
  insérer / retirer / remplacer une colonne, ajuster, copier / renommer / supprimer / importer / exporter une vue),
  AllowColumnReordering 1, AllowColumnResizing 1, ViewDropdownName « ViewDropdown » (la liste du modèle
  TableViewDropdown, celui du menu « Club ▾ »), ScrollViewMode 2 (vertical et horizontal) et, en v2,
  HorizontalScrollerVisibility 0 AVEC sa marque (sans marque, le jeu prend son défaut : pas de barre horizontale, vu
  en jeu par Kinito en v1 : colonnes cachées à droite) ;
- sur la collection de vues PlayerRecommendationsTableViewCollection (ui-tableviews) : m_customViewDisplayName et
  m_customViewNamePrefix (GameID 0 ici ; posés sur les collections personnalisables du jeu) et m_contextMenuData (la
  liste des colonnes du menu « Insérer colonne », vide ici).
Le script recopie ces réglages de la recherche de joueurs (PlayerSearchResultsViewCollection, telle qu'elle est dans le
jeu : avec la colonne Personnalité d'AlexJeuVideal si elle est active, menu 23, fonction 1). Les 11 vues toutes faites restent.
Le menu des vues est relié APRÈS le tableau : dans un SIVisible sur VUES_PRETES, passé à vrai DELAI s plus tard par un
SIDelayEvent ; relié avant le tableau, il n'aurait pas ses actions (copier, renommer…) à l'ouverture (v4, mesuré).

Historique des versions (demandes, relevés en jeu, essais) : résumé dans « AJOUTS KINITO - DETAILS.md »,
§ 6 ; texte complet gardé par Kinito.

Fichiers touchés :
- RecruitmentContentBlock, PlayerRecommendationsMainBlock et, depuis la v4, PlayerRecommendationsTopBlock (bundle
  gameworld, et leur feuille de style intégrée) — seul propriétaire (aucun script
  d'AlexJeuVideal ni d'autre ajout Kinito n'y touche), appliquer repart de l'original, retirer le remet. Seul le
  tableau « club » (celui qui lit PlayerRecommendationsTableViewCollection) change, pas celui des sélections.
- ui-tableviews : PARTAGÉ avec AlexJeuVideal (colonne_personnalite, entrainement_pouces, etat_esprit_fm24,
  tactiques_forme_valeur travaillent sur le bundle tel qu'il est). Ce script ne touche que
  PlayerRecommendationsTableViewCollection : appliquer la repart de son original, retirer la remet d'origine, sans
  toucher au reste. Attention : le « retirer » de colonne_personnalite remet tout ui-tableviews d'origine, ce qui
  efface aussi cet ajout jusqu'au prochain choix 1 (le statut 116 le signale).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapports_vues.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapports_vues.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_rapports_vues.py etat
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
from notes_installations import first  # noqa: E402

DELAI = 0.5   # s : le menu des vues apparaît (et se relie) ce temps après l'ouverture du bloc (Base de données : ~50 ms)
VERSION = 6   # v6 (MODIF D'ALEX, 2026-11-01) : menu « Insérer colonne » sans les entrées à Requirement (Efficacité
              # tactique = ShowTacticalEffectivenessRequirement, Hidden = InGameEditorRequirement) : plantage de FM à la
              # 1re tactique d'une partie neuve après Recrutement (NRE StreamedTableViewSettingsCollection.CheckRequirements),
              # disparu une fois ce script retiré (124 du 2026-11-01) ;
              # v5 (MODIF D'ALEX, MAJ de FM du 2026-11-12) : BindingVariablesComponent remis sur le bloc du haut ;
              # v4 (mouchard du tableau, voir plus haut) : le menu des vues se relie après le tableau, comme dans la Base de
              # données (SIVisible sur une variable du bloc, passée à vrai par un SIDelayEvent) ;
              # la variable selectedtableview de la v3 est retirée (elle vidait le tableau de Recrutement > Recrutement) ;
              # v3 (retirée) : la vue choisie déclarée comme variable du bloc (selectedtableview), comme selectedView dans la
              # Base de données — sans effet sur les actions du menu, et elle masquait la vue passée par l'écran
              # v2 : HorizontalScrollerVisibility recopiée aussi (0 avec sa marque dans la recherche, sans marque ici : défaut du jeu)
MODELES_TABLEAUX = ["RecruitmentContentBlock", "PlayerRecommendationsMainBlock"]        # le tableau « club »
MODELES = MODELES_TABLEAUX + ["PlayerRecommendationsTopBlock"]                            # + le menu de Recrutement > Recrutement
COLLECTION = "PlayerRecommendationsTableViewCollection"
GUID_COLLECTION = "7aa6a532120b7da4fb70e90ed381585a"     # celle que lit le tableau « club » des recommandations
SOURCE_TABLEAU = ("PersonSearchMainContentBlock", "playertable")   # Base de données des joueurs
SOURCE_COLLECTION = "PlayerSearchResultsViewCollection"
FABRIQUE = "49c25af415c53814d8d3ed658d867204"           # PlayerTableFactory : la même des deux côtés (vérifié)
REGLAGES = ["ContextMenuData", "AllowColumnReordering", "AllowColumnResizing", "ViewDropdownName", "ScrollViewMode",
            "HorizontalScrollerVisibility"]
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
REPERE = f"UIPickerKinito-rapports-v{VERSION}"         # debug_name posé sur la 1re entrée du menu « Insérer colonne »
VUE_ECRAN = "selectedtableview"     # la vue choisie, passée par l'écran : jamais redéclarée ici (la v3 l'a fait, à tort)
SOURCE_VARIABLES = ("PlayerRecommendationsMainBlock", "BindingVariables_FM")   # élément BindingVariables de FM (modèle)
TYPE_VARIABLES = "SI.Bindable.BindingVariables"
SOURCE_COMPOSANT = "SquadCaptainsBlock"                  # v5 : son ComponentElement racine a un BindingVariablesComponent
TYPE_COMPOSANT = "SI.Bindable.BindingVariablesComponent"
# v4
VUES_PRETES = "kinitovuesprete"                                          # variable booléenne du bloc, fausse au départ
DECLARATION_PRETE = {"m_name": VUES_PRETES, "m_scopeValue": {"m_serializedData": "Bool|0|"}}   # comme PositionViewVisible
SOURCE_VISIBLE = ("PersonSearchMainContentBlock", "position-view-visible")   # SIVisible de FM sur une variable booléenne
SOURCE_DELAI = "GameCreationGameSummaryScreen"                              # SIDelayEvent de FM sans enfant
MENU_VUES = "ClubTableViewDropdown"                                         # le menu des vues du tableau « club »
PREFIXE = "UIPickerKinito"
NOM_ENVELOPPE = f"{PREFIXE}-rapports-menu-v{VERSION}"
NOM_DELAI = f"{PREFIXE}-rapports-delai-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_rapports_vues.actif")


# ---------- les tableaux (modèles) ----------
def tableaux_club(t):
    """les StreamedTable du modèle qui lisent la collection des recommandations (pas celle des sélections)"""
    out = []
    for r in t.walk():
        if typ(t, r) != "StreamedTable":
            continue
        init = bytes(((t.sd(r).get("InitFunction") or {}).get("m_inputs") or {}).get("m_variable", {}).get("m_argumentBytes") or [])
        if GUID_COLLECTION.encode() in init:
            out.append(r)
    return out


def reglages_source():
    o = ouvrir(SOURCE_TABLEAU[0], depart_original=True)
    if o is None:
        return None
    t = o[3]
    r = next((r for r in t.walk() if typ(t, r) == "StreamedTable" and t.sd(r).get("name") == SOURCE_TABLEAU[1]), None)
    if r is None or (t.sd(r).get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE:
        return None
    d = t.sd(r)
    out = {}
    for k in REGLAGES:
        if k not in d:
            return None
        out[k] = copy.deepcopy(d[k])
        out[k + "_UxmlAttributeFlags"] = d.get(k + "_UxmlAttributeFlags", 1)
    return out


def tableau_a_jour(t, r, src):
    d = t.sd(r)
    return all(d.get(k) == v for k, v in src.items())


def modifier_tableaux(t, src):
    faits = 0
    for r in tableaux_club(t):
        d = t.sd(r)
        if (d.get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE:
            return -1
        d.update(copy.deepcopy(src))
        faits += 1
    return faits


# ---------- v3 : la vue choisie, variable du bloc ----------
def modele_variables():
    """la référence (rid, type, données) d'un élément BindingVariables de FM, pour en faire d'autres"""
    o = ouvrir(SOURCE_VARIABLES[0], depart_original=True)
    if o is None:
        return None
    t = o[3]
    r = next((r for r in t.walk() if t.name(r) == SOURCE_VARIABLES[1] and typ(t, r) == "BindingVariables"), None)
    return r is not None and copy.deepcopy(t.refs[t.elem(r)["m_SerializedData"]["rid"]])


def vue_masquee(t):
    """vrai si la vue passée par l'écran est cachée par une variable du même nom (la v3)"""
    return any(v.get("m_name") == VUE_ECRAN
               for r in t.walk() if typ(t, r) == "BindingVariables" for v in t.sd(r).get("ReferenceVariables") or [])


def _ancetres(t, r):
    out = []
    while r is not None:
        out.append(r)
        r = t.parent.get(r)
    return out


def element_variables(t, modele):
    """(données où déclarer, élément où poser le délai) : l'élément qui englobe tous les menus des vues (et les tableaux
    « club ») et peut porter des variables — un BindingVariables, ou un ComponentElement qui a un BindingVariablesComponent ;
    sinon l'enfant de la racine (BindingExpect, qui ne peut pas porter de variable), changé en BindingVariables comme le
    fait to_visible d'AlexJeuVideal (il garde ses classes). Une chaîne si rien ne convient."""
    menus = [r for r in t.walk() if t.name(r) == MENU_VUES]
    if not menus:
        return "menu des vues (%s) introuvable" % MENU_VUES
    tous = menus + tableaux_club(t)
    communs = set(_ancetres(t, tous[0]))
    for x in tous[1:]:
        communs &= set(_ancetres(t, x))
    for x in [x for x in _ancetres(t, tous[0]) if x in communs]:          # du plus proche à la racine
        if typ(t, x) == "BindingVariables":
            return t.sd(x), x
        if typ(t, x) == "ComponentElement":
            comp = next((c["rid"] for c in t.sd(x).get("m_components") or []
                         if "BindingVariablesComponent" in t.refs[c["rid"]]["type"]["class"]), None)
            if comp is not None:
                return t.refs[comp]["data"], x
    # v5 (MODIF D'ALEX, MAJ de FM du 2026-11-12) : FM a retiré le BindingVariablesComponent vide du ComponentElement
    # racine de PlayerRecommendationsTopBlock -> on lui en remet un, recopié de celui de FM dans SquadCaptainsBlock
    ce = next((x for x in _ancetres(t, tous[0]) if x in communs and typ(t, x) == "ComponentElement"), None)
    if ce is not None:
        donnees = ajouter_composant_variables(t, ce)
        if donnees is not None:
            return donnees, ce
    racine = t.children(t.tt["m_VisualTree"]["rid"])[0]
    enfants = t.children(racine)
    if typ(t, racine) != "BindingExpect" or len(enfants) != 1 or typ(t, enfants[0]) != "VisualElement" \
            or enfants[0] not in communs:
        return "élément englobant introuvable"
    bv = enfants[0]
    e = t.elem(bv)
    ancien = e["m_SerializedData"]["rid"]
    neuf = copy.deepcopy(modele)
    neuf["rid"] = t.new_rid()
    d, d_ancien = neuf["data"], t.refs[ancien]["data"]
    for k, v in d_ancien.items():          # ce que l'élément avait (nom, etc.) est gardé
        if k in d:
            d[k] = copy.deepcopy(v)
    d["uxmlAssetId"] = e.get("m_Id", d.get("uxmlAssetId"))
    d["ValueVariables"], d["ReferenceVariables"] = [], []
    t.refs[neuf["rid"]] = neuf
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] != ancien]
    t.tt["references"]["RefIds"].append(neuf)
    t.refs.pop(ancien, None)
    e["m_FullTypeName"] = TYPE_VARIABLES
    e["m_SerializedData"] = {"rid": neuf["rid"]}
    return t.sd(bv), bv


def ajouter_composant_variables(t, ce):
    """v5 : un BindingVariablesComponent vide (objet UXML enfant + ses données dans m_components) posé sur le
    ComponentElement ce, recopié de celui de FM (SquadCaptainsBlock) ; ses données, ou None si le modèle manque"""
    o = ouvrir(SOURCE_COMPOSANT, depart_original=True)
    if o is None:
        return None
    s = o[3]
    obj = next((r for r in s.walk() if s.elem(r).get("m_FullTypeName") == TYPE_COMPOSANT), None)
    if obj is None:
        return None
    parent = s.parent[obj]
    dat = next((c["rid"] for c in s.sd(parent).get("m_components") or []
                if s.refs[c["rid"]]["data"].get("uxmlAssetId") == s.elem(obj)["m_Id"]), None)
    if dat is None:
        return None
    ident = t.new_id()
    r_obj, r_dat = copy.deepcopy(s.refs[obj]), copy.deepcopy(s.refs[dat])
    r_obj["rid"], r_dat["rid"] = t.new_rid(), t.new_rid()
    r_obj["data"].update({"m_Id": ident, "m_ParentId": t.elem(ce)["m_Id"], "m_Parent": {"rid": ce}, "m_Children": [],
                          "m_Properties": []})                                  # vide, comme celui d'avant la MAJ
    r_dat["data"].update({"uxmlAssetId": ident, "ValueVariables": [], "ReferenceVariables": [],
                          "ValueVariables_UxmlAttributeFlags": 0, "ReferenceVariables_UxmlAttributeFlags": 0})
    for r in (r_obj, r_dat):
        t.refs[r["rid"]] = r
        t.tt["references"]["RefIds"].append(r)
    t.elem(ce)["m_Children"].insert(0, {"rid": r_obj["rid"]})
    t.parent[r_obj["rid"]] = ce
    sd = t.sd(ce)
    sd.setdefault("m_components", []).append({"rid": r_dat["rid"]})
    sd["m_components_UxmlAttributeFlags"] = 1
    return r_dat["data"]


# ---------- v4 : le menu des vues relié après le tableau ----------
def _texte(x):
    x = x.encode()
    return bytes([1, 1, len(x)]) + x


def _bloc(b):
    return struct.pack("<i", len(b)) + b


def copier(source, destination):
    """contenu d'un événement « copier la valeur de <source> dans <destination> » (217,15,225,87)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])


def liste(contenus):
    """liste d'événements : [1,1,1,N] puis [1] + longueur + contenu pour chacun"""
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def evenements_ok():
    """le format écrit ici = celui de FM, refait à l'octet près (copie de ClubNationInfoTabButton)"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return liste([copier("rowindex", "selected-tab")]) == attendu


class Sources:
    def __init__(self):
        v = ouvrir(SOURCE_VISIBLE[0], depart_original=True)
        self.tv = v and v[3]
        self.visible = self.tv and first(self.tv, lambda r: self.tv.name(r) == SOURCE_VISIBLE[1]
                                         and typ(self.tv, r) == "SIVisible")
        d = ouvrir(SOURCE_DELAI, depart_original=True)
        self.td = d and d[3]
        self.delai = self.td and first(self.td, lambda r: self.td.elem(r).get("m_FullTypeName") == "FM.UI.SIDelayEvent"
                                       and not self.td.children(r))

    def ok(self):
        return None not in (self.visible, self.delai) and evenements_ok()


def _parent_id(t, rid):
    """clone ne refait que m_Parent : l'identifiant du parent aussi (s'il est noté)"""
    p = t.parent[rid]
    if "m_ParentId" in t.elem(rid):
        t.elem(rid)["m_ParentId"] = t.elem(p).get("m_Id", t.elem(rid)["m_ParentId"])


def _nommer(t, rid, nom):
    t.sd(rid)["name"], t.sd(rid)["name_UxmlAttributeFlags"] = nom, 1


def envelopper_menus(t, src):
    """chaque #ClubTableViewDropdown passe dans un SIVisible sur VUES_PRETES, à sa place (même parent, même rang)"""
    menus = [r for r in t.walk() if t.name(r) == MENU_VUES]
    if not menus:
        return 0
    for m in menus:
        p = t.parent[m]
        rang = [k["rid"] for k in t.elem(p)["m_Children"]].index(m)
        v = t.clone(src.visible, p, index=rang, src=src.tv)
        for k in list(t.children(v)):
            t.remove(k)
        _parent_id(t, v)
        _nommer(t, v, NOM_ENVELOPPE)
        sd = t.sd(v)
        sd["Binding"]["m_kind"] = 1
        sd["Binding"]["m_direct"]["Path"]["m_path"] = VUES_PRETES
        sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 0, 1
        sd["AlwaysInstantiate"], sd["AlwaysInstantiate_UxmlAttributeFlags"] = 1, 1   # le tableau trouve son menu
        t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
        # le menu, déplacé dans l'enveloppe
        t.elem(p)["m_Children"] = [k for k in t.elem(p)["m_Children"] if k["rid"] != m]
        t.elem(v)["m_Children"].append({"rid": m})
        t.elem(m)["m_Parent"] = {"rid": v}
        t.parent[m] = v
        _parent_id(t, m)
    return len(menus)


def ajouter_delai(t, donnees, parent, src):
    """VUES_PRETES déclarée dans <donnees> (un BindingVariables ou un BindingVariablesComponent) ; SIDelayEvent de FM à la
    fin de <parent> (l'élément qui les porte) : VUES_PRETES passe à vrai DELAI s après la liaison du bloc"""
    vv = donnees.setdefault("ValueVariables", [])
    if not any(x.get("m_name") == VUES_PRETES for x in vv):
        vv.append(copy.deepcopy(DECLARATION_PRETE))
    donnees["ValueVariables_UxmlAttributeFlags"] = 1
    dl = t.clone(src.delai, parent, src=src.td)
    _parent_id(t, dl)
    _nommer(t, dl, NOM_DELAI)
    t.elem(dl)["m_Classes"], t.elem(dl)["m_RuleIndex"] = [], -1
    t.styles.style(t, dl, {"position": "absolute", "width": 0, "height": 0})
    d = t.sd(dl)
    d["m_duration"], d["m_duration_UxmlAttributeFlags"] = float(DELAI), 1
    d["TransitionEvents"] = {"m_bytes": liste([copier("const.True", VUES_PRETES)])}
    d["TransitionEvents_UxmlAttributeFlags"] = 1


def menu_retarde(t):
    noms = [t.name(r) for r in t.walk()]
    return (NOM_DELAI in noms and noms.count(NOM_ENVELOPPE) >= 1
            and all(t.name(t.parent[r]) == NOM_ENVELOPPE for r in t.walk() if t.name(r) == MENU_VUES))


# ---------- la collection de vues (ui-tableviews, partagé) ----------
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


def collection_a_jour(tt):
    return (tt.get("m_customViewDisplayName", {}).get("GameID")
            and any(e.get("debug_name") == REPERE for e in tt.get("m_contextMenuData") or []))


def construire_collection(tt, src):
    """tt : la collection d'origine ; src : celle de la recherche de joueurs (telle qu'elle est dans le jeu). Copie le
    nom et le préfixe des vues personnalisées, et le menu « Insérer colonne » avec ses entrées (nouveaux rid)."""
    menu = src.get("m_contextMenuData") or []
    if not menu or not src.get("m_customViewDisplayName", {}).get("GameID"):
        return "menu ou nom de vue personnalisée de la recherche de joueurs introuvable"
    tt["m_customViewDisplayName"] = copy.deepcopy(src["m_customViewDisplayName"])
    tt["m_customViewNamePrefix"] = copy.deepcopy(src["m_customViewNamePrefix"])
    refs_src = {r["rid"]: r for r in src["references"]["RefIds"]}
    # toutes les entrées du menu (sous-menus compris) : les rid cités par les ChildList, de proche en proche
    a_copier, pile = [], [c["rid"] for e in menu for c in e.get("ChildList") or []]
    while pile:
        rid = pile.pop()
        if rid in a_copier or rid not in refs_src:
            continue
        a_copier.append(rid)
        pile += [c["rid"] for c in (refs_src[rid].get("data") or {}).get("ChildList") or []]
    refs = tt.setdefault("references", {"version": 2, "RefIds": []})
    base = max([r["rid"] for r in refs["RefIds"]] + [0]) + 1
    nouveaux = {old: base + i for i, old in enumerate(sorted(a_copier))}

    def remap(x):
        if isinstance(x, dict):
            if set(x) == {"rid"} and x["rid"] in nouveaux:
                return {"rid": nouveaux[x["rid"]]}
            return {k: remap(v) for k, v in x.items()}
        if isinstance(x, list):
            return [remap(v) for v in x]
        return x

    # v6 : entrées à Requirement laissées de côté (et leurs sous-entrées), retirées des ChildList
    sans = {rid for rid in a_copier if avec_condition(refs_src[rid].get("data"))}
    pile = list(sans)
    while pile:
        for c in (refs_src[pile.pop()].get("data") or {}).get("ChildList") or []:
            if c["rid"] in refs_src and c["rid"] not in sans:
                sans.add(c["rid"])
                pile.append(c["rid"])
    gardes = [rid for rid in sorted(a_copier) if rid not in sans]
    nouveaux = {old: base + i for i, old in enumerate(gardes)}

    def epurer(e):
        e = copy.deepcopy(e)
        if e.get("ChildList"):
            e["ChildList"] = [c for c in e["ChildList"] if c["rid"] not in sans]
        return remap(e)

    for old in gardes:
        r = copy.deepcopy(refs_src[old])
        r["data"] = epurer(r.get("data") or {})
        r["rid"] = nouveaux[old]
        refs["RefIds"].append(r)
    tt["m_contextMenuData"] = [epurer(e) for e in menu if not avec_condition(e)]
    tt["m_contextMenuData"][0]["debug_name"] = REPERE
    return (f"menu « Insérer colonne » de la recherche de joueurs ({len(tt['m_contextMenuData'])} rubriques, "
            f"{len(gardes)} entrées, {len(sans)} à condition laissées de côté) et nom des vues personnalisées")


def avec_condition(e):
    """v6 : entrée de menu liée à un Requirement de FM (Efficacité tactique, éditeur)"""
    req = (e or {}).get("Requirement")
    return isinstance(req, dict) and bool(req.get("m_PathID") or req.get("m_FileID"))


# ---------- commandes ----------
def etat_actuel():
    """(modèles ouverts, collection (objet, typetree), réglages source) ; None si un morceau manque"""
    modeles = {m: ouvrir(m) for m in MODELES}
    env = nb.env_of(VUES)
    col = mono(env, COLLECTION)
    return modeles, col, env


def cmd_appliquer():
    src_t = reglages_source()
    modeles, col, env = etat_actuel()
    src_c = mono(env, SOURCE_COLLECTION)
    if src_t is None or col is None or src_c is None or None in modeles.values():
        print("[Kinito] Rapports : morceaux de FM introuvables (tableaux, collection de vues ou recherche de joueurs), "
              "rien enregistré")
        return
    deja = collection_a_jour(col.read_typetree()) and all(
        (m not in MODELES_TABLEAUX or (tableaux_club(o[3]) and all(tableau_a_jour(o[3], r, src_t) for r in tableaux_club(o[3]))))
        and not vue_masquee(o[3]) and menu_retarde(o[3]) for m, o in modeles.items())
    if deja:
        print("[Kinito] Rapports : déjà appliqué")
    else:
        msgs = []
        travail = {}
        modele = modele_variables()
        if not modele:
            print("[Kinito] Rapports : élément BindingVariables de FM introuvable, rien enregistré")
            return
        src = Sources()
        if not src.ok():
            print("[Kinito] Rapports : SIVisible ou SIDelayEvent de FM introuvable (ou format d'événement changé), "
                  "rien enregistré")
            return
        for m in MODELES:
            o = ouvrir(m, depart_original=True)
            if o is None:
                print(f"[Kinito] Rapports : {m} introuvable, rien enregistré")
                return
            t = o[3]
            texte = ""
            if m in MODELES_TABLEAUX:
                n = modifier_tableaux(t, src_t)
                if n <= 0:
                    print(f"[Kinito] Rapports : tableau des recommandations de {m} introuvable ou d'une autre fabrique, "
                          "rien enregistré")
                    return
                texte = (f"{n} tableau (menu du clic droit, colonnes déplaçables et redimensionnables, défilement "
                         "horizontal, lien avec le menu des vues) ; ")
            ev = element_variables(t, modele)
            if isinstance(ev, str):
                print(f"[Kinito] Rapports : {m} : {ev}, rien enregistré")
                return
            nm = envelopper_menus(t, src)
            ajouter_delai(t, ev[0], ev[1], src)
            travail[m] = o
            msgs.append(f"{m} : {texte}{nm} menu(s) des vues relié(s) {DELAI} s après l'ouverture (variable "
                        f"{VUES_PRETES} sur {typ(t, ev[1])} #{t.name(ev[1]) or '(sans nom)'})")
        tt = hp.original(VUES, col) or col.read_typetree()
        m = construire_collection(tt, src_c.read_typetree())
        if "introuvable" in m:
            print(f"[Kinito] Rapports : {m}, rien enregistré")
            return
        msgs.append(f"{COLLECTION} : {m}")
        for x in msgs:
            print(f"[Kinito] Rapports : {x}")
        for o in travail.values():
            bundle, obj, tto, t = o
            t.finish()
            t.styles.save()
            obj.save_typetree(tto)
            nb._dirty.add(bundle)
        col.save_typetree(tt)
        nb._dirty.add(VUES)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for m in MODELES:
        o = ouvrir(m)
        if o is None:
            continue
        bundle, obj, tt, t = o
        if not (any(t.sd(r).get("AllowColumnReordering") for r in tableaux_club(t)) or vue_masquee(t)
                or any(t.name(r).startswith(PREFIXE) for r in t.walk())):
            continue
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])   # v4 : la feuille de style aussi
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{m} : remis d'origine")
    col = mono(nb.env_of(VUES), COLLECTION)
    if col is not None and col.read_typetree().get("m_customViewDisplayName", {}).get("GameID"):   # toute version
        orig = hp.original(VUES, col)
        if orig is None:
            print(f"{COLLECTION} : pas de sauvegarde d'origine, rien fait")
        else:
            col.save_typetree(orig)
            nb._dirty.add(VUES)
            fait = True
            print(f"{COLLECTION} : remise d'origine (le reste de ui-tableviews n'est pas touché)")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    src_t = reglages_source()
    modeles, col, env = etat_actuel()
    for m, o in modeles.items():
        if o is None:
            print(f"{m} : introuvable")
            continue
        rs = tableaux_club(o[3])
        ok = rs and src_t and all(tableau_a_jour(o[3], r, src_t) for r in rs)
        print(f"{m} : " + (("tableau personnalisable, " if ok else "tableau d'origine, ") if m in MODELES_TABLEAUX else "")
              + ("vue de l'écran MASQUÉE (v3, à refaire : choix 1)" if vue_masquee(o[3]) else "vue de l'écran transmise")
              + (f", menu des vues relié après le tableau (v{VERSION})" if menu_retarde(o[3]) else ", menu des vues d'origine"))
    if col is None:
        print(f"{COLLECTION} : introuvable")
    else:
        tc = col.read_typetree()
        print(f"{COLLECTION} : " + ("vues personnalisables (à jour, v%d)" % VERSION if collection_a_jour(tc)
                                    else "vues personnalisables, version précédente (à refaire : choix 1)"
                                    if tc.get("m_customViewDisplayName", {}).get("GameID") else "d'origine"))
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
            print("[Kinito] Rapports : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
