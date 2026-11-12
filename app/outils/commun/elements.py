"""Outils d'éléments partagés par les scripts des fiches (joueur, staff, entraînement) et d'autres : copie de
modèles inclus, déplacement, conteneur vide, boutons Féliciter / Critiquer / Rapport, et le lanceur commun des
ajouts « par nom » (un passage par modèle, sur l'état actuel du jeu).
(Avant le rangement du 2026-11-12 : dans fiches_plus.py.)
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree, Styles, FIXE, PROPRIETES  # noqa: E402

for _k, _v in {"align-self": (131074, 7), "flex-direction": (131083, 7), "flex-wrap": (131086, 7),
               "height": (131087, 3), "margin-right": (131092, 3), "margin-bottom": (131090, 3), "top": (131104, 3), "position": (131102, 7), "right": (131103, 3), "bottom": (131080, 3), "align-items": (131073, 7), "width-mot-cle": (131105, 1)}.items():
    PROPRIETES.setdefault(_k, _v)
CLASSE_ICONE_SEULE = "uipicker-icone-seule"  # boutons sans leur texte (action_buttons long=False, inutilisé :
                                             # seul cas qui dépend encore du mod, Fit.cs)
TYPE_PERSONNE = 1145176065
BOUTONS_SOURCE = "PlayerReportDevelopmentProgressReportBlock"   # onglet progrès : boutons Féliciter / Critiquer FM
NOTE_ENTRAINEMENT = "PlayerTrainingRatingCell"
NOTE_SOURCE = "IndividualTrainingPlayerHeaderContent"   # modèle FM qui inclut déjà la note


# ---------- outils ----------
def src_tree(model):
    _, _, tt = nb.find_vta(model)
    return Tree(tt) if tt is not None else None


def add_using(t, using):
    if using and not any(u.get("alias") == using["alias"] for u in t.tt.setdefault("m_Usings", [])):
        t.tt["m_Usings"].append(copy.deepcopy(using))


def copy_usings(t, s, root):
    """déclare dans t les modèles inclus utilisés par le sous-arbre root de s"""
    aliases = {s.elem(r).get("m_TemplateAlias") for r in s.walk(root)} - {None, ""}
    for u in s.tt.get("m_Usings") or []:
        if u.get("alias") in aliases:
            add_using(t, u)


def first(t, pred):
    return next((r for r in t.walk() if pred(r)), None)


def typ(t, r):
    return t.elem(r).get("m_FullTypeName") or ""


def move(t, rid, new_parent, index=None):
    old = t.parent[rid]
    t.elem(old)["m_Children"] = [k for k in t.elem(old)["m_Children"] if k["rid"] != rid]
    kids = t.elem(new_parent)["m_Children"]
    kids.insert(len(kids) if index is None else index, {"rid": rid})
    t.elem(rid)["m_Parent"] = {"rid": new_parent}
    t.parent[rid] = new_parent


def plain(t, parent, index, classes, name=""):
    """nouveau VisualElement vide"""
    model = first(t, lambda r: typ(t, r) == "UnityEngine.UIElements.VisualElement" and not t.elem(r).get("m_TemplateAlias")
                  and t.elem(r).get("m_SerializedData"))
    v = t.clone_shallow(model, parent, index)
    t.sd(v)["name"] = name
    t.elem(v)["m_Classes"] = list(classes)
    return v


def visible_model(t):
    return first(t, lambda r: typ(t, r).endswith("SIVisible") and isinstance(t.sd(r).get("Binding"), dict))


def action_buttons(t, parent, index, classes, name="", long=False, person="person", rapport=True):
    """Féliciter + Critiquer pour le joueur affiché : copie des boutons de FM de l'onglet progrès de la fiche
    (PlayerReportDevelopmentProgressReportBlock), mêmes actions instantanées que le rapport hebdo d'entraînement.
    Ils lisent "player" (une personne) : un BindingRemapper player -> person le leur fournit partout.
    long=False : icônes seules ; long=True : boutons avec leur texte, qui se partagent toute la largeur."""
    ns = src_tree(NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == NOTE_ENTRAINEMENT)
    rm = t.clone(ns.parent[note], parent, index, src=ns)   # un BindingRemapper, vidé
    for k in list(t.children(rm)):
        t.remove(k)
    t.sd(rm)["name"] = name
    # person=None : "player" existe déjà là où on pose les boutons (écran d'entraînement individuel)
    t.sd(rm)["Mappings"] = [] if person is None else [
        {"m_serialisedType": 0, "from": "player", "to": {"m_path": person}, "type": {"id": TYPE_PERSONNE}}]
    t.elem(rm)["m_Classes"] = ["row-direction-normal", "align-items-center"] \
        + (["flex-grow-class"] if long else [CLASSE_ICONE_SEULE]) + list(classes)
    if not long:
        t.styles.style(t, rm, FIXE)
    s = src_tree(BOUTONS_SOURCE)
    names = [("PraisePlayerButton", ["margin-right-global-gap-regular"]), ("WarnPlayerButton", [])]
    if rapport:
        names = [(n, ["margin-right-global-gap-regular"]) for n, _ in names] + [("RequestTrainingReportButton", [])]
    for nm, cls in names:
        btn = first(s, lambda r: s.name(r) == nm and typ(s, r) == "FM.UI.FMActionButton")
        v = t.clone(btn, rm, src=s)
        t.elem(v)["m_Classes"] = cls + (["flex-grow-class"] if long else [])
        if long:
            t.sd(v)["GrowToWidth"] = 1
            t.sd(v)["GrowToWidth_UxmlAttributeFlags"] = 1
    return rm


def set_text_binding(t, rid, binding):
    t.sd(rid)["TextBinding"] = copy.deepcopy(binding)


def types_ref_manquants(obj, tt):
    """2026-11-05 : un élément recopié d'un autre bundle de modèles (ex. FMSpiderChart dans une bannière du bundle
    global) a un type de référence que ce fichier ne déclare pas -> type recopié du fichier qui le déclare (même
    jeu, même description) ; renvoie les noms ajoutés"""
    af = obj.assets_file
    if af.ref_types is None:
        return []
    connus = {(r.m_ClassName, r.m_NameSpace, r.m_AssemblyName) for r in af.ref_types}
    ajoutes = []
    for ref in (tt.get("references") or {}).get("RefIds") or []:
        ty = (ref or {}).get("type") or {}
        cle = (ty.get("class"), ty.get("ns"), ty.get("asm"))
        if not cle[0] or cle in connus:
            continue
        donneur = None
        for b in nb.BUNDLES:
            for f in nb.env_of(b).files.values():
                for sf in ([f] if hasattr(f, "ref_types") else getattr(f, "files", {}).values()):
                    for r in getattr(sf, "ref_types", None) or []:
                        if (r.m_ClassName, r.m_NameSpace, r.m_AssemblyName) == cle:
                            donneur = r
        if donneur is None:
            continue
        af.ref_types.append(copy.copy(donneur))   # (script_type_index gardé : SIText a le même dans les 2 fichiers)
        connus.add(cle)
        ajoutes.append(cle[0])
    return ajoutes


# ---------- ajouts « par nom » : un passage par modèle, sur l'état actuel ----------
def appliquer_jobs(jobs, marker):
    """jobs : [(modèle, fonction(t) -> messages)] ; un message contenant « introuvable » = rien fait"""
    changed = 0
    for model, fn in jobs:
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        t = Tree(tt)
        t.styles = Styles(bundle, tt)
        msgs = fn(t)
        for m in msgs:
            print(f"{model} : {m}")
        if not [m for m in msgs if "introuvable" not in m]:
            if not msgs:
                print(f"{model} : déjà appliqué")
            continue
        t.finish()
        t.styles.save()
        for n in types_ref_manquants(obj, tt):
            print(f"{model} : type {n} déclaré dans le bundle (recopié)")
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt   # relu tel quel par les jobs suivants (find_vta)
        nb._dirty.add(bundle)
        changed += 1
    if changed:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(marker, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
