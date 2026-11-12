"""[AJOUT KINITO] Capitaines : des vues personnalisables dans « Tout l'effectif », comme la Base de données des joueurs.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : « dans l'onglet capitaine il faut voir à ajouter une vue personnalisable, comme pour les
recommandations, [avec la] possibilité d'importer ». Même recette que kinito_rapports_vues (rapports des recruteurs, validé
en jeu le 2026-11-12), sans rien lui emprunter : un ajout Kinito n'importe jamais un autre ajout Kinito.

Relevé dans le jeu (2026-11-12, rien de deviné) : Effectif > Capitaines = SquadCaptainsBlock. Son tableau « Tout
l'effectif » (StreamedTable #FilteredPlayersTable, données team.FilteredPlayers) a la MÊME fabrique de colonnes que la
Base de données des joueurs (PlayerTableFactory, 49c25af4…) ; il lit la collection de vues SquadCaptainsPlayerTableView-
Collection (a0216e8d…, 2 vues toutes faites : Attributs capitaine, Stats) par InitialiseStreamedTableFromViewCollection,
avec la vue choisie dans la variable du bloc selectedView (déclarée comme dans la Base de données). Ce qui lui manque :
- sur le tableau : ContextMenuData (menu du clic droit sur les en-têtes), AllowColumnReordering / AllowColumnResizing,
  ViewDropdownName « ViewDropdown », ScrollViewMode et HorizontalScrollerVisibility — recopiés de la Base de données ;
- sur la collection (ui-tableviews) : m_customViewDisplayName / m_customViewNamePrefix (GameID 0 ici) et m_contextMenuData
  (menu « Insérer colonne », vide ici) — recopiés de PlayerSearchResultsViewCollection telle qu'elle est dans le jeu ;
- son menu des vues (#TableViewDropdown, modèle TableViewDropdown) est placé AVANT le tableau, comme chez les recruteurs :
  relié avant le tableau, il n'aurait pas les actions (copier, renommer, supprimer, importer, exporter) à l'ouverture
  (mesuré pour les recruteurs avec le mouchard du tableau de FMSonde 0.13). Il est donc mis dans un SIVisible (copie de
  #position-view-visible de la Base de données) sur la variable VUES_PRETES, fausse au départ, AlwaysInstantiate = 1 (le
  tableau trouve son menu, qui n'est relié qu'une fois visible) ; un SIDelayEvent de FM (celui, sans enfant, de
  GameCreationGameSummaryScreen), posé à la fin du bloc, la passe à vrai DELAI s plus tard. VUES_PRETES est déclarée dans le
  BindingVariablesComponent du ComponentElement racine (comme pour PlayerRecommendationsTopBlock des recruteurs).
Les deux autres tableaux du bloc (Capitaines, Suppléants) ne changent pas. Aucune variable existante n'est redéclarée.

Fichiers touchés :
- SquadCaptainsBlock (bundle gameworld, et sa feuille de style intégrée) — seul propriétaire (aucun script
  d'AlexJeuVideal ni d'autre ajout Kinito n'y touche) : appliquer repart de l'original, retirer le remet.
- ui-tableviews : PARTAGÉ avec AlexJeuVideal (colonne_personnalite, entrainement_pouces, etat_esprit_fm24,
  tactiques_forme_valeur) et avec kinito_rapports_vues. Ce script ne touche que SquadCaptainsPlayerTableViewCollection :
  appliquer la repart de son original, retirer la remet d'origine, sans toucher au reste. Attention : le « retirer » de
  colonne_personnalite remet tout ui-tableviews d'origine, ce qui efface aussi cet ajout jusqu'au prochain choix 1.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_capitaines_vues.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_capitaines_vues.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_capitaines_vues.py etat
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

DELAI = 0.5   # s : le menu des vues apparaît (et se relie) ce temps après l'ouverture du bloc (comme chez les recruteurs)
VERSION = 2   # v2 (MODIF D'ALEX, 2026-11-01) : menu « Insérer colonne » sans les entrées à Requirement (Efficacité
              # tactique = ShowTacticalEffectivenessRequirement, Hidden = InGameEditorRequirement), comme
              # kinito_rapports_vues v6 (plantage de FM à la 1re tactique, validé en jeu) ; plantages vus ici le 2026-10-31
MODELE = "SquadCaptainsBlock"
COLLECTION = "SquadCaptainsPlayerTableViewCollection"
GUID_COLLECTION = "a0216e8d74ac92642ae8716ff6ebb02c"     # celle que lit le tableau « Tout l'effectif »
SOURCE_TABLEAU = ("PersonSearchMainContentBlock", "playertable")   # Base de données des joueurs
SOURCE_COLLECTION = "PlayerSearchResultsViewCollection"
FABRIQUE = "49c25af415c53814d8d3ed658d867204"           # PlayerTableFactory : la même des deux côtés (vérifié)
REGLAGES = ["ContextMenuData", "AllowColumnReordering", "AllowColumnResizing", "ViewDropdownName", "ScrollViewMode",
            "HorizontalScrollerVisibility"]
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
REPERE = f"UIPickerKinito-capitaines-v{VERSION}"       # debug_name posé sur la 1re entrée du menu « Insérer colonne »
VUES_PRETES = "kinitovuesprete"                                          # variable booléenne du bloc, fausse au départ
DECLARATION_PRETE = {"m_name": VUES_PRETES, "m_scopeValue": {"m_serializedData": "Bool|0|"}}   # comme PositionViewVisible
SOURCE_VISIBLE = ("PersonSearchMainContentBlock", "position-view-visible")   # SIVisible de FM sur une variable booléenne
SOURCE_DELAI = "GameCreationGameSummaryScreen"                              # SIDelayEvent de FM sans enfant
MENU_VUES = "TableViewDropdown"                                             # le menu des vues du tableau
PREFIXE = "UIPickerKinito"
NOM_ENVELOPPE = f"{PREFIXE}-capitaines-menu-v{VERSION}"
NOM_DELAI = f"{PREFIXE}-capitaines-delai-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_capitaines_vues.actif")


# ---------- le tableau (modèle) ----------
def tableaux(t):
    """les StreamedTable du modèle qui lisent la collection de « Tout l'effectif » (pas ceux des capitaines / suppléants)"""
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
    for r in tableaux(t):
        d = t.sd(r)
        if (d.get("FactoryAsset") or {}).get("m_AssetGUID") != FABRIQUE:
            return -1
        d.update(copy.deepcopy(src))
        faits += 1
    return faits


def _ancetres(t, r):
    out = []
    while r is not None:
        out.append(r)
        r = t.parent.get(r)
    return out


def element_variables(t):
    """(données où déclarer, élément où poser le délai) : le plus proche élément qui englobe le menu des vues et le
    tableau et peut porter des variables — un BindingVariables, ou un ComponentElement qui a un BindingVariablesComponent.
    Une chaîne si rien ne convient (on ne transforme aucun élément ici)."""
    menus = [r for r in t.walk() if t.name(r) == MENU_VUES]
    if not menus:
        return "menu des vues (%s) introuvable" % MENU_VUES
    tous = menus + tableaux(t)
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
    return "élément englobant introuvable"


def variable_deja_declaree(t):
    """vrai si un élément du modèle d'origine déclare déjà une variable de ce nom (on ne masque rien)"""
    for r in t.walk():
        try:
            sd = t.sd(r) or {}
        except Exception:
            continue
        if not isinstance(sd, dict):
            continue
        for k in ("ValueVariables", "ReferenceVariables"):
            if any(v.get("m_name") == VUES_PRETES for v in (sd.get(k) or [])):
                return True
        for c in sd.get("m_components") or []:
            d = t.refs[c["rid"]].get("data") or {}
            for k in ("ValueVariables", "ReferenceVariables"):
                if any(v.get("m_name") == VUES_PRETES for v in (d.get(k) or [])):
                    return True
    return False


# ---------- le menu des vues relié après le tableau ----------
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
    """chaque #TableViewDropdown passe dans un SIVisible sur VUES_PRETES, à sa place (même parent, même rang)"""
    menus = [r for r in t.walk() if t.name(r) == MENU_VUES]
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

    # v2 : entrées à Requirement laissées de côté (et leurs sous-entrées), retirées des ChildList
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
    """v2 : entrée de menu liée à un Requirement de FM (Efficacité tactique, éditeur)"""
    req = (e or {}).get("Requirement")
    return isinstance(req, dict) and bool(req.get("m_PathID") or req.get("m_FileID"))


# ---------- commandes ----------
def a_jour(o, src_t):
    t = o[3]
    rs = tableaux(t)
    return bool(rs) and src_t is not None and all(tableau_a_jour(t, r, src_t) for r in rs) and menu_retarde(t)


def cmd_appliquer():
    src_t = reglages_source()
    o = ouvrir(MODELE)
    env = nb.env_of(VUES)
    col = mono(env, COLLECTION)
    src_c = mono(env, SOURCE_COLLECTION)
    if src_t is None or col is None or src_c is None or o is None:
        print("[Kinito] Capitaines : morceaux de FM introuvables (tableau, collection de vues ou recherche de joueurs), "
              "rien enregistré")
        return
    if collection_a_jour(col.read_typetree()) and a_jour(o, src_t):
        print("[Kinito] Capitaines : déjà appliqué")
    else:
        src = Sources()
        if not src.ok():
            print("[Kinito] Capitaines : SIVisible ou SIDelayEvent de FM introuvable (ou format d'événement changé), "
                  "rien enregistré")
            return
        o = ouvrir(MODELE, depart_original=True)
        if o is None:
            print(f"[Kinito] Capitaines : {MODELE} introuvable, rien enregistré")
            return
        t = o[3]
        if variable_deja_declaree(t):
            print(f"[Kinito] Capitaines : une variable {VUES_PRETES} existe déjà dans {MODELE}, rien enregistré")
            return
        n = modifier_tableaux(t, src_t)
        if n != 1:
            print(f"[Kinito] Capitaines : tableau « Tout l'effectif » de {MODELE} introuvable, en double ou d'une autre "
                  "fabrique, rien enregistré")
            return
        ev = element_variables(t)
        if isinstance(ev, str):
            print(f"[Kinito] Capitaines : {MODELE} : {ev}, rien enregistré")
            return
        nm = envelopper_menus(t, src)
        if nm != 1:
            print(f"[Kinito] Capitaines : {nm} menus des vues trouvés dans {MODELE} (1 attendu), rien enregistré")
            return
        ajouter_delai(t, ev[0], ev[1], src)
        tt = hp.original(VUES, col) or col.read_typetree()
        m = construire_collection(tt, src_c.read_typetree())
        if "introuvable" in m:
            print(f"[Kinito] Capitaines : {m}, rien enregistré")
            return
        print(f"[Kinito] Capitaines : {MODELE} : tableau « Tout l'effectif » (menu du clic droit, colonnes déplaçables et "
              f"redimensionnables, défilement horizontal, lien avec le menu des vues) ; menu des vues relié {DELAI} s après "
              f"l'ouverture (variable {VUES_PRETES} sur {typ(t, ev[1])} #{t.name(ev[1]) or '(sans nom)'})")
        print(f"[Kinito] Capitaines : {COLLECTION} : {m}")
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
    o = ouvrir(MODELE)
    if o is not None:
        bundle, obj, tt, t = o
        if any(t.sd(r).get("AllowColumnReordering") for r in tableaux(t)) or any(t.name(r).startswith(PREFIXE) for r in t.walk()):
            orig = hp.original(bundle, obj)
            if orig is None:
                print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            else:
                obj.save_typetree(orig)
                sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])   # la feuille de style aussi
                if sheet is not None:
                    t.styles.sh, t.styles.changed = sheet, True
                    t.styles.save()
                nb._dirty.add(bundle)
                fait = True
                print(f"{MODELE} : remis d'origine")
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
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} : introuvable")
    else:
        t = o[3]
        rs = tableaux(t)
        ok = rs and src_t and all(tableau_a_jour(t, r, src_t) for r in rs)
        print(f"{MODELE} : " + ("tableau personnalisable" if ok else "tableau d'origine")
              + (f", menu des vues relié après le tableau (v{VERSION})" if menu_retarde(t) else ", menu des vues d'origine"))
    col = mono(nb.env_of(VUES), COLLECTION)
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
            print("[Kinito] Capitaines : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
