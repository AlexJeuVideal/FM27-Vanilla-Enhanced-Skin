"""Boîte à outils des modèles d'écran (UXML) : arbre d'éléments (Tree), styles intégrés (Styles), conteneurs
conditionnels (SIVisible : make_visible, polygon_visible). Utilisée par presque tous les scripts.
(Avant le rangement du 2026-11-12 : dans style_mediatique_et_meilleur_pied.py.)
"""
import copy
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)


# ---------- outils sur l'arbre d'un modèle ----------
class Tree:
    def __init__(self, tt):
        self.tt = tt
        self.refs = {r["rid"]: r for r in tt["references"]["RefIds"]}
        self.parent = {}
        for rid, r in self.refs.items():
            for k in (r.get("data") or {}).get("m_Children") or []:
                self.parent[k["rid"]] = rid
        self.used_ids = {(r.get("data") or {}).get("m_Id") for r in self.refs.values()}

    def elem(self, rid):
        return self.refs[rid]["data"]

    def sd(self, rid):
        """données sérialisées (nom, liaisons...) d'un élément"""
        s = (self.elem(rid).get("m_SerializedData") or {}).get("rid")
        return (self.refs.get(s) or {}).get("data") or {}

    def children(self, rid):
        return [k["rid"] for k in self.elem(rid).get("m_Children") or []]

    def walk(self, rid=None):
        rid = self.tt["m_VisualTree"]["rid"] if rid is None else rid
        yield rid
        for c in self.children(rid):
            yield from self.walk(c)

    def find(self, pred, root=None):
        return [r for r in self.walk(root) if pred(r)]

    def name(self, rid):
        return self.sd(rid).get("name") or ""

    def binding(self, rid, key="Binding"):
        b = self.sd(rid).get(key)
        return b["m_direct"]["Path"]["m_path"] if isinstance(b, dict) and b.get("m_kind") == 1 else None

    def new_rid(self):
        r = max(self.refs) + 1
        self.refs[r] = None   # réservé
        return r

    def new_id(self):
        while True:
            i = random.randint(-2**31, 2**31 - 1)
            if i not in self.used_ids and i not in (0, -1):
                self.used_ids.add(i)
                return i

    def closure(self, root):
        """tous les rid d'un sous-arbre : éléments, données sérialisées, composants, surcharges"""
        seen, todo = set(), [root]
        while todo:
            rid = todo.pop()
            if rid in seen or rid not in self.refs or rid == -2:
                continue
            seen.add(rid)

            def scan(x, key=None):
                if isinstance(x, dict):
                    if set(x) == {"rid"} and key != "m_Parent":
                        todo.append(x["rid"])
                    for k, v in x.items():
                        scan(v, k)
                elif isinstance(x, list):
                    for v in x:
                        scan(v, key)
            scan(self.refs[rid].get("data") or {})
        return seen

    def clone(self, root, new_parent, index=None, src=None):
        """copie un sous-arbre (de ce modèle, ou du modèle src) sous new_parent, avec de nouveaux rid et identifiants"""
        src = src or self
        rids = sorted(src.closure(root))
        rid_map = {old: self.new_rid() for old in rids}
        id_map = {}
        for old in rids:
            d = src.refs[old].get("data") or {}
            if "m_Id" in d and d["m_Id"] not in (0, -1):
                id_map[d["m_Id"]] = self.new_id()

        def remap(x, key=None):
            if isinstance(x, dict):
                if set(x) == {"rid"} and x["rid"] in rid_map:
                    return {"rid": rid_map[x["rid"]]}
                out = {}
                for k, v in x.items():
                    if k in ("m_Id", "m_ParentId", "uxmlAssetId") and isinstance(v, int) and v in id_map:
                        out[k] = id_map[v]
                    else:
                        out[k] = remap(v, k)
                return out
            if isinstance(x, list):
                return [remap(v, key) for v in x]
            return x

        for old in rids:
            r = copy.deepcopy(src.refs[old])
            r["rid"] = rid_map[old]
            if "data" in r:
                r["data"] = remap(r["data"])
            self.refs[r["rid"]] = r
            self.tt["references"]["RefIds"].append(r)
        new_root = rid_map[root]
        self.elem(new_root)["m_Parent"] = {"rid": new_parent}
        kids = self.elem(new_parent)["m_Children"]
        kids.insert(len(kids) if index is None else index, {"rid": new_root})
        self.parent[new_root] = new_parent
        for old in rids:   # parents des éléments copiés
            for k in (self.refs[rid_map[old]].get("data") or {}).get("m_Children") or []:
                self.parent[k["rid"]] = rid_map[old]
        return new_root

    def clone_shallow(self, rid, new_parent, index=None):
        """copie un seul élément (sans ses enfants ni surcharges) sous new_parent"""
        e = copy.deepcopy(self.refs[rid])
        sd = copy.deepcopy(self.refs[e["data"]["m_SerializedData"]["rid"]])
        e["rid"], sd["rid"] = self.new_rid(), self.new_rid()
        ident = self.new_id()
        ed = e["data"]
        ed.update({"m_Id": ident, "m_Parent": {"rid": new_parent}, "m_Children": [], "m_SerializedData": {"rid": sd["rid"]}})
        if "m_SerializedDataOverride" in ed:
            ed["m_SerializedDataOverride"] = []
        sd["data"]["uxmlAssetId"] = ident
        for r in (e, sd):
            self.refs[r["rid"]] = r
            self.tt["references"]["RefIds"].append(r)
        kids = self.elem(new_parent)["m_Children"]
        kids.insert(len(kids) if index is None else index, {"rid": e["rid"]})
        self.parent[e["rid"]] = new_parent
        return e["rid"]

    def remove(self, rid):
        """retire un sous-arbre (élément, enfants et leurs données)"""
        p = self.parent.get(rid)
        if p is not None:
            self.elem(p)["m_Children"] = [k for k in self.elem(p)["m_Children"] if k["rid"] != rid]
        gone = self.closure(rid)
        self.tt["references"]["RefIds"] = [r for r in self.tt["references"]["RefIds"] if r["rid"] not in gone]
        for g in gone:
            self.refs.pop(g, None)

    def to_visible(self, rid, model_visible, path, invert, name):
        """transforme un conteneur en élément à affichage conditionnel (SIVisible) sur <path>"""
        e = self.elem(rid)
        old_sd = e["m_SerializedData"]["rid"]
        data = copy.deepcopy(self.refs[self.elem(model_visible)["m_SerializedData"]["rid"]])
        data["rid"] = self.new_rid()
        d = data["data"]
        d["uxmlAssetId"] = e.get("m_Id", d.get("uxmlAssetId"))
        d["name"] = name
        d["Binding"]["m_kind"] = 1
        d["Binding"]["m_direct"]["Path"]["m_path"] = path
        d["InvertDirectBinding"] = 1 if invert else 0
        d["StyleClassToApplyOnVisible"] = ""
        self.refs[data["rid"]] = data
        self.tt["references"]["RefIds"].append(data)
        e["m_FullTypeName"] = "SI.Bindable.SIVisible"
        e["m_SerializedData"] = {"rid": data["rid"]}
        self.tt["references"]["RefIds"] = [r for r in self.tt["references"]["RefIds"] if r["rid"] != old_sd]
        self.refs.pop(old_sd, None)

    def finish(self):
        """remet la liste des références dans l'ordre (vides réservés retirés)"""
        self.tt["references"]["RefIds"] = sorted((r for r in self.tt["references"]["RefIds"] if r), key=lambda r: r["rid"])


# ---------- styles intégrés d'un modèle (sans le mod) ----------
# Chaque modèle a sa feuille de style interne ("inlineStyle", tt["inlineSheet"]) ; un élément y pointe par
# m_RuleIndex. Une règle = liste de propriétés (m_Id = StylePropertyId d'Unity, lu dans les DLL du jeu), chaque
# valeur = (type, index dans la liste du type). Types (StyleValueType) : 1 mot-clé (index = StyleValueKeyword),
# 2 nombre, 3 dimension (unit 1 = px, 2 = %), 4 couleur, 7 valeur d'énumération, 8 variable, 9 texte.
PROPRIETES = {   # nom CSS : (StylePropertyId, type)
    "max-width": (131095, 3), "min-width": (131097, 3), "min-height": (131096, 3), "flex-basis": (131082, 3),
    "flex-grow": (131084, 2), "flex-shrink": (131085, 2), "overflow": (458768, 7), "margin-bottom": (131090, 3),
    "border-top-width": (131079, 3), "border-bottom-width": (131076, 3), "border-left-width": (131077, 3),
    "border-right-width": (131078, 3), "background-color": (458752, 4), "background-image": (458753, 1),
}
MOT_CLE_AUCUN = 6   # StyleValueKeyword.None
# les mises en forme que le mod (Fit.cs) appliquait autrefois à partir de classes repères
LARGEUR_MAX = lambda w: {"max-width": w, "min-width": 0, "flex-shrink": 1, "overflow": "hidden"}  # noqa: E731
MOITIE = {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-height": 0, "overflow": "hidden"}
FIXE = {"flex-shrink": 0}
SANS_CADRE = {"border-top-width": 0, "border-bottom-width": 0, "border-left-width": 0, "border-right-width": 0,
              "background-color": (0, 0, 0, 0), "background-image": MOT_CLE_AUCUN}
_TABLES = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}


class Styles:
    """feuille de style intégrée d'un modèle : lue une fois, enregistrée par save() (avant nb.save_all())"""

    def __init__(self, bundle, tt):
        pid = tt["inlineSheet"]["m_PathID"]
        self.obj = next(o for o in nb.env_of(bundle).objects if o.path_id == pid)
        self.cle = (bundle, pid)
        # feuille déjà réécrite dans ce passage : read_typetree rendrait l'ancienne (voir nb._ecrits)
        deja = nb._ecrits.get(self.cle)
        self.sh = copy.deepcopy(deja) if deja is not None else self.obj.read_typetree()
        self.changed = False

    def _index(self, typ, value):
        if typ == 1:
            return int(value)
        table = self.sh.setdefault(_TABLES[typ], [])
        if typ == 3 and not isinstance(value, dict):
            value = {"unit": 1, "value": float(value)}
        elif typ == 4 and not isinstance(value, dict):
            value = dict(zip("rgba", (float(v) for v in value)))
        elif typ == 2:
            value = float(value)
        if value not in table:
            table.append(value)
        return table.index(value)

    def values(self, idx):
        """règle n° idx décodée : [(m_Id, [(type, valeur)])]"""
        out = []
        for p in self.sh["m_Rules"][idx]["m_Properties"]:
            vals = []
            for v in p["m_Values"]:
                typ = v["m_ValueType"]
                if typ != 1 and typ not in _TABLES:
                    raise ValueError(f"type de valeur de style non géré : {typ}")
                vals.append((typ, v["valueIndex"] if typ == 1 else self.sh[_TABLES[typ]][v["valueIndex"]]))
            out.append((p["m_Id"], p["m_CustomName"], vals))
        return out

    def add_rule(self, props):
        """ajoute une règle [(m_Id, nom perso, [(type, valeur)])] et renvoie son numéro"""
        rule = {"m_ComplexSelectors": [], "line": -1, "m_Properties": [
            {"m_Id": pid, "m_CustomName": custom, "m_Line": -1,
             "m_Values": [{"m_ValueType": typ, "valueIndex": self._index(typ, val)} for typ, val in vals]}
            for pid, custom, vals in props]}
        self.sh["m_Rules"].append(rule)
        self.changed = True
        return len(self.sh["m_Rules"]) - 1

    def style(self, t, rid, css):
        """style intégré de l'élément rid : sa règle actuelle (copiée, d'autres éléments peuvent la partager)
        complétée / remplacée par css {nom CSS: valeur}"""
        e = t.elem(rid)
        old = self.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
        new = {PROPRIETES[k][0]: (PROPRIETES[k][0], "", [(PROPRIETES[k][1], v)]) for k, v in css.items()}
        e["m_RuleIndex"] = self.add_rule([p for p in old if p[0] not in new] + list(new.values()))

    def copy_from(self, src, t, root):
        """après Tree.clone(..., src=) : les éléments copiés pointent vers les règles de la feuille du modèle source ;
        on recopie ces règles ici"""
        for r in t.walk(root):
            e = t.elem(r)
            if e.get("m_RuleIndex", -1) >= 0:
                e["m_RuleIndex"] = self.add_rule(src.values(e["m_RuleIndex"]))

    def save(self):
        if self.changed:
            self.obj.save_typetree(self.sh)
            nb._ecrits[self.cle] = self.sh


def no_styles(t, root):
    """retire les styles intégrés d'un sous-arbre copié d'un autre modèle (ils pointeraient vers de mauvaises règles)"""
    for r in t.walk(root):
        if t.elem(r).get("m_RuleIndex", -1) >= 0:
            t.elem(r)["m_RuleIndex"] = -1



def named(t, name):
    return [r for r in t.walk() if t.name(r) == name]

# bouton "polygone" de la fiche joueur : FM range dans visibilityMask les colonnes de l'ExpandableContentElement
# qui rentrent ; le bouton est visible si la colonne 6 (polygone) est CACHÉE (dernier argument = 1, inversé)
FONCTION_COLONNE_VISIBLE = "807d96119392d4a478953c6ff056e3ba"
CLASSE_SI_POLYGONE = "uipicker-si-polygone"   # repère des conteneurs posés par polygon_visible (aucun effet en jeu)


def polygon_button(t):
    """le SIVisible du bouton polygone de FM (colonne 6, inversé), ou None"""
    for r in t.walk():
        b = t.sd(r).get("Binding")
        if (isinstance(b, dict) and b.get("m_kind") == 2
                and b["m_visualFunction"]["m_target"]["m_guid"] == FONCTION_COLONNE_VISIBLE
                and bytes(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"][-17:])
                == b"BooleanVisualArg\x01"):
            return r
    return None


def polygon_visible(t, rid, inverse=False):
    """transforme le conteneur rid en SIVisible affiché seulement quand la colonne du polygone (Pour / Contre) est
    affichée, donc pas en mode Défaut. C'est FM qui décide (même liaison que le bouton polygone, non inversée ;
    inverse=True : affiché seulement quand la colonne n'est pas là, comme le bouton).
    Renvoie False si le bouton du polygone est introuvable dans ce modèle."""
    model = polygon_button(t)
    if model is None:
        return False
    args = t.sd(model)["Binding"]["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]
    e = t.elem(rid)
    old_sd = e["m_SerializedData"]["rid"]
    data = copy.deepcopy(t.refs[t.elem(model)["m_SerializedData"]["rid"]])
    data["rid"] = t.new_rid()
    d = data["data"]
    d["uxmlAssetId"] = e["m_Id"]
    d["name"] = ""
    d["Binding"]["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = list(args[:-1]) + [1 if inverse else 0]
    t.refs[data["rid"]] = data
    t.tt["references"]["RefIds"].append(data)
    e["m_FullTypeName"] = "SI.Bindable.SIVisible"
    e["m_SerializedData"] = {"rid": data["rid"]}
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r and r["rid"] != old_sd]
    t.refs.pop(old_sd, None)
    if CLASSE_SI_POLYGONE not in (e.get("m_Classes") or []):
        e["m_Classes"] = list(e.get("m_Classes") or []) + [CLASSE_SI_POLYGONE]
    return True


def make_visible(t, model, parent, index, path, name, classes):
    """nouveau conteneur conditionnel (SIVisible) : visible si <path> est vrai / non nul (utilisé par hors_defaut.py)"""
    v = t.clone_shallow(model, parent, index)
    d = t.sd(v)
    d["name"] = name
    vf = copy.deepcopy(d["Binding"]["m_visualFunction"])
    vf["m_target"]["m_guid"] = ""
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    d["Binding"] = {"m_kind": 1, "m_direct": {"Path": {"m_path": path}, "Nullable": 0}, "m_visualFunction": vf}
    d["BindFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                         "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    d["InvertDirectBinding"] = 0
    d["StyleClassToApplyOnVisible"] = ""
    t.elem(v)["m_Classes"] = list(classes)
    return v

