"""Notes /20 des installations au lieu des libellés de FM (Bon, Excellent...).

Notes exactes : FM les transmet en « étoiles » sur 20 (MainTeam.YouthFacilitiesStars / YouthRecruitmentStars,
MinValue / MaxValue ; égaux pour ton club). On affiche le mini, puis « -maxi » seulement s'ils diffèrent.
Encadrement des jeunes : club.YouthCoachingLevel, posé par la recette des notes.
Entraînement : aucune note exacte transmise, seulement un palier (code Rating 11..20, et 1..10) = fourchette connue
(tables des anciens FM) : un texte fixe par palier (« 10-11 »), affiché seulement quand Rating vaut ce palier
(fonction FM BindIntToVisible, égalité). Les couleurs de FM ne changent pas.

Modèles touchés :
- FacilitiesRatingTraining / FacilitiesRatingYouth : pastilles Entraînement / Jeunes (Infos club, tuiles, emplois...).
- ClubFacilitiesTrainingBlock : sa pastille (modèle générique FacilitiesRating) devient FacilitiesRatingTraining.
- YouthFacilitiesBlock_4x4 : la pastille Recrutement des jeunes est recopiée dans la tuile avec ses paliers.

Menu Outils FM.bat : 16 (catégorie), puis la fonction ; réappliqué par le choix 1.
"""
import copy
import json
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from elements import move  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
# Entraînement / Structures de formation : palier 1..10 -> fourchette de notes
PALIERS_INSTALLATIONS = ["1-3", "4-5", "6-7", "8-9", "10-11", "12-13", "14-15", "16-17", "18-19", "20"]
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "notes_installations.actif")
NOM_PALIER = "UIPickerPalier"
NOM_RECRUTEMENT = "UIPickerRecrutement"
NOM_EXACTE = "UIPickerNoteExacte"
FN_EGAL = "d52cf0b2ba55c764b9ecda52092aa257"          # BindIntToVisible (opérateur, entier, chemin)
SOURCE_VISIBLE = "NonPlayerAttributesBlock_Tooltip"     # contient des SIVisible BindIntToVisible
FN_COMPARE = "a7578b809e01fc84881e9781c448d0bc"       # BindIntPropertyComparisonToVisible (op, clé, clé, A, B)
SOURCE_COMPARE = "FeedbackTacticsBlock"                 # contient des SIVisible BindIntPropertyComparisonToVisible
OPS_DIFFERENT = (0, 4)   # « A < B » et « A > B » (ordre exact de l'énumération inconnu : une seule est vraie si A != B)
PASTILLES = {"FacilitiesRatingTraining": "Club.TrainingFacilityRating.Rating"}     # paliers (fourchettes)
EXACTES = {"FacilitiesRatingYouth": "Club.MainTeam.YouthFacilitiesStars"}          # note exacte (étoiles)
ETOILES_RECRUTEMENT = "club.MainTeam.YouthRecruitmentStars"
BLOC_ENTRAINEMENT = "ClubFacilitiesTrainingBlock"
TUILE_JEUNES = "YouthFacilitiesBlock_4x4"
GUID_PASTILLE_ENTRAINEMENT = "d14babcd8c475fe42a451788b83f377b"
# note exacte de l'entraînement (2026-11-12, essai 34 séries 9-10) : l'objet éditeur du club existe hors de l'éditeur ;
# ses 2 lecteurs de liste (IGEEditSectionsTabs) recopiés : section INDEX_SECTION (Infrastructures) puis champ
# INDEX_CHAMP (Entraînement), valeur .PropertyValue ; vide (pas d'éditeur ? MAJ de FM ?) = fourchette (paliers)
NOM_EDITEUR = "UIPickerNoteEditeur"
# v2 (2026-10-30, partie sans l'éditeur : objet éditeur absent -> lecteurs muets, repli caché avec eux) : aiguillage
# de FM « données valides ? » (BindingSetter isDataValid + BindableSwitchElement Data / NoData) au-dessus des lecteurs,
# NoData = copie des paliers
NOM_EDITEUR_GARDE = "UIPickerNoteEditeurGarde-v2"
SOURCE_GARDE, GARDE_SETTER = "PersonPersonalBlock_SocialGroup", "BindingDataSetter"
LISTE_EDITEUR = "Club.Editor.GenericSections"
INDEX_SECTION, INDEX_CHAMP = 3, 11
SOURCE_LECTEURS = "IGEEditSectionsTabs"
LECTEUR_SECTIONS, LECTEUR_CHAMPS = "FirstTabBindVariables", "SecondTabLayerSetter"
SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL = "NonPlayerAttributesBlock", "240779c127ba1174a812adf0be56e006"   # texte == / != valeur
CHEMIN_RECRUTEMENT = "club.YouthRecruitment"
CHEMIN_ENCADREMENT = "club.YouthCoaching"         # libellé de FM (niveau 1-8)
NOTE_ENCADREMENT = "club.YouthCoachingLevel"      # vraie note /20


# ---------- arguments des fonctions visuelles ----------
def _varint(data, i):
    n = s = 0
    while True:
        c = data[i]
        i += 1
        n |= (c & 0x7f) << s
        s += 7
        if not c & 0x80:
            return n, i


def _enc_varint(n):
    out = bytearray()
    while True:
        c = n & 0x7f
        n >>= 7
        out.append(c | (0x80 if n else 0))
        if not n:
            return bytes(out)


def decode_args(ab):
    data = bytes(ab)
    n, i = _varint(data, 0)
    out = []
    for _ in range(n):
        size = struct.unpack_from("<i", data, i)[0]
        i += 4
        chunk = data[i:i + size]
        i += size
        tl, j = _varint(chunk, 0)
        out.append([chunk[j:j + tl], chunk[j + tl:]])
    return out


def encode_args(args):
    out = bytearray(_enc_varint(len(args)))
    for typ, val in args:
        chunk = _enc_varint(len(typ)) + typ + val
        out += struct.pack("<i", len(chunk)) + chunk
    return list(out)


def make_binding(model_binding, op, paths, value=None):
    """copie d'une liaison de comparaison de FM avec l'opérateur, l'entier et les chemins (dans l'ordre) voulus"""
    b = copy.deepcopy(model_binding)
    vf = b["m_visualFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    todo = list(paths)
    for a in args:
        if a[0].endswith(b"ComparisonOperator]"):
            a[1] = struct.pack("<i", op)
        elif a[0] == b"SI.VisualScripting.Int32VisualArg" and value is not None:
            a[1] = struct.pack("<i", value)
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]") and todo:
            p = todo.pop(0).encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return b


def equal_binding(model_binding, path, value):
    """liaison « visible si <path> == value », d'après une liaison BindIntToVisible de FM"""
    return make_binding(model_binding, 2, [path], value)


# ---------- outils ----------
def first(t, pred, root=None):
    return next((r for r in t.walk(root) if pred(r)), None)


def src_tree(model):
    bundle, _, tt = nb.find_vta(model)
    return (Tree(tt), bundle) if tt is not None else (None, None)


def visible_model(source=SOURCE_VISIBLE, guid=FN_EGAL):
    s, _ = src_tree(source)
    if s is None:
        return None, None
    r = first(s, lambda r: (s.elem(r).get("m_FullTypeName") or "").endswith("SIVisible")
              and (s.sd(r).get("Binding") or {}).get("m_kind") == 2
              and s.sd(r)["Binding"]["m_visualFunction"]["m_target"]["m_guid"] == guid)
    return s, r


def new_visible(t, s, vis, parent, index, name, binding, classes=()):
    """SIVisible vide (copié du modèle de FM vis du modèle s) avec la liaison voulue"""
    v = t.clone(vis, parent, index, src=s)
    for c in list(t.children(v)):
        t.remove(c)
    no_styles(t, v)
    t.sd(v)["name"] = name
    t.sd(v)["Binding"] = binding
    t.elem(v)["m_Classes"] = list(classes)
    return v


def text_static(t, model, parent, text, index=None):
    txt = t.clone(model, parent, index)
    sd = t.sd(txt)
    sd["text"], sd["text_UxmlAttributeFlags"] = text, 1
    sd["DebugDisplay"] = text
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 0
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    return txt


def text_direct(t, model, parent, path, index=None):
    txt = t.clone(model, parent, index)
    sd = t.sd(txt)
    sd["text"], sd["text_UxmlAttributeFlags"] = "", 0
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = path
    return txt


def paliers(t, desc, path, values):
    """remplace le texte desc par un texte fixe par valeur, visible seulement quand path == valeur"""
    s, vis = visible_model()
    if vis is None:
        return False
    parent = t.parent[desc]
    index = t.children(parent).index(desc)
    for k, (value, text) in enumerate(values):
        v = new_visible(t, s, vis, parent, index + k, NOM_PALIER, equal_binding(s.sd(vis)["Binding"], path, value))
        text_static(t, desc, v, text)
    t.remove(desc)
    return True


def exacte(t, setter, base):
    """contenu de la pastille (setter) remplacé par la note exacte base.MinValue, suivie de « -base.MaxValue »
    seulement si les deux diffèrent ; garde un texte de FM comme modèle (description ou texte d'un palier)"""
    old = t.children(setter)
    model = first(t, lambda r: (t.elem(r).get("m_FullTypeName") or "").endswith("SIText"), setter)
    s, vis = visible_model(SOURCE_COMPARE, FN_COMPARE)
    if model is None or vis is None:
        return False
    cls = [c for c in t.elem(setter).get("m_Classes") or [] if c not in ("row-direction-normal", "align-items-center")]
    t.elem(setter)["m_Classes"] = cls + ["row-direction-normal", "align-items-center"]
    mn = text_direct(t, model, setter, base + ".MinValue")
    t.sd(mn)["name"] = NOM_EXACTE
    for op in OPS_DIFFERENT:
        b = make_binding(s.sd(vis)["Binding"], op, [base + ".MinValue", base + ".MaxValue"])
        v = new_visible(t, s, vis, setter, None, "", b, ["row-direction-normal", "align-items-center"])
        text_static(t, model, v, "-")
        text_direct(t, model, v, base + ".MaxValue")
    for r in old:
        t.remove(r)
    return True


def rating_values():
    vals = [(-1, "-")]
    for code in range(1, 21):
        vals.append((code, PALIERS_INSTALLATIONS[(code - 1) % 10]))
    return vals


# ---------- modifications ----------
def reparer_paliers(t):
    """textes des paliers reconvertis en code brut par l'ancienne recette (texte direct) : remis en texte fixe"""
    n = 0
    for v in [r for r in t.walk() if t.name(r) == NOM_PALIER]:
        for r in t.walk(v):
            tb = t.sd(r).get("TextBinding")
            if tb and tb.get("m_kind") == 1 and t.sd(r).get("text"):
                tb["m_kind"] = 0
                tb["m_direct"]["Path"]["m_path"] = ""
                n += 1
    return [f"{n} palier(s) réparé(s) (code brut -> fourchette)"] if n else []


def pastille(t, path):
    if first(t, lambda r: t.name(r) == NOM_PALIER):
        return reparer_paliers(t) + entrainement_exacte(t)
    desc = first(t, lambda r: t.name(r) == "description")
    if desc is None:
        return ["texte de la pastille introuvable, ignoré"]
    if not paliers(t, desc, path, rating_values()):
        return ["modèle de visibilité introuvable, ignoré"]
    return ["pastille : fourchette de notes /20 au lieu du libellé"] + entrainement_exacte(t)


def _lecteur(t, s, src, parent, liste, index):
    """BindingSetter de l'éditeur recopié sous parent, réduit à sa variable n° 0 (sans enfants) : élément index de liste ;
    renvoie (setter, nom de la variable)"""
    c = t.clone(src, parent, src=s)
    for k in list(t.children(c)):
        t.remove(k)
    t.sd(c)["name"] = ""
    t.elem(c)["m_Classes"], t.elem(c)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    f = copy.deepcopy(t.sd(c)["BindFunction"][0])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins_ = [a for a in args if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]")]
    p = liste.encode()
    chemins_[0][1] = b"\x01" + _enc_varint(len(p)) + p
    variable = chemins_[1][1][2:].decode()
    for a in args:
        if a[0] == b"SI.VisualScripting.Int32VisualArg":
            a[1] = struct.pack("<i", index)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.sd(c)["BindFunction"] = [f]
    return c, variable


def _texte_visible(t, s, vis, parent, chemin, vide, nom):
    """SIVisible « chemin vide » (vide) ou « chemin pas vide » (fonction FM texte égal / différent de "")"""
    b = copy.deepcopy(s.sd(vis)["Binding"])
    args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0] == b"SI.VisualScripting.StringVisualArg":
            a[1] = b"\x01" + _enc_varint(0)
        elif a[0] == b"SI.VisualScripting.BooleanVisualArg":
            a[1] = b"\x00" if vide else b"\x01"   # FM : 1 = visible si différent
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = chemin.encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return new_visible(t, s, vis, parent, None, nom, b, ["row-direction-normal", "align-items-center"])


def entrainement_exacte(t):
    """pastille Entraînement : note exacte lue dans l'objet éditeur du club, la fourchette (paliers) si elle est vide"""
    if first(t, lambda r: t.name(r) == NOM_EDITEUR_GARDE):
        return []
    msgs = []
    for v in [r for r in t.walk() if t.name(r) == NOM_EDITEUR]:   # v1 (sans garde) : paliers ressortis, lecteurs retirés
        parent, i = t.parent[v], t.children(t.parent[v]).index(v)
        for r in [r for r in t.walk(v) if t.name(r) == NOM_PALIER]:
            move(t, r, parent, i)
            i += 1
        t.remove(v)
        msgs.append("note exacte v1 retirée (sans garde)")
    return msgs + note_editeur(t, [r for r in t.walk() if t.name(r) == NOM_PALIER], LISTE_EDITEUR)


def _garde(t, parent, liste):
    """aiguillage de FM « données valides ? » sur liste, posé en tête de parent : renvoie (Data, NoData) vidés"""
    s, _ = src_tree(SOURCE_GARDE)
    src = s and first(s, lambda r: s.name(r) == GARDE_SETTER)
    if src is None or len(s.children(src)) != 1 or len(s.children(s.children(src)[0])) != 2:
        return None
    g = t.clone(src, parent, 0, src=s)
    t.sd(g)["name"], t.sd(g)["name_UxmlAttributeFlags"] = NOM_EDITEUR_GARDE, 1
    t.elem(g)["m_Classes"], t.elem(g)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    f = t.sd(g)["BindFunction"][0]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    p = liste.encode()
    args[0][1] = b"\x01" + _enc_varint(len(p)) + p          # chemin testé (2e argument : la variable isDataValid)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sw = t.children(g)[0]
    b = t.sd(sw)["Binding"]["m_visualFunction"]
    args = decode_args(b["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:   # FM : [person.IsVirtual faux] et [isDataValid vrai] -> isDataValid seul
        if a[0].startswith(b"SI.VisualScripting.StructListVisualArg"):
            a[1] = b"\x01\x01\x0bisDataValid\x01"
    b["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.sd(sw)["name"] = ""
    branches = t.children(sw)
    for br in branches:
        for k in list(t.children(br)):
            t.remove(k)
        t.sd(br)["name"] = ""
        t.elem(br)["m_Classes"], t.elem(br)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    t.elem(sw)["m_Classes"], t.elem(sw)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    return branches[0], branches[1]


def note_editeur(t, paliers_, liste, contenu=None):
    """note exacte de l'entraînement à la place des paliers (frères), qui restent en repli si elle est vide ; liste =
    chemin de la liste de l'éditeur dans ce modèle (Club. / club.) ; contenu(parent, chemin de la note) = ce qui
    l'affiche (défaut : texte, sur le modèle du 1er palier) ; aussi pour club_bandeau_installations (note, étoiles)"""
    s, _ = src_tree(SOURCE_LECTEURS)
    st, vis = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
    var = s and first(s, lambda r: s.name(r) == LECTEUR_SECTIONS)
    champs = s and first(s, lambda r: s.name(r) == LECTEUR_CHAMPS)
    if not paliers_ or None in (var, champs, vis) or not s.children(var):
        return ["note exacte de l'entraînement : lecteurs de l'éditeur introuvables, fourchette gardée"]
    setter = t.parent[paliers_[0]]
    modele = first(t, lambda r: (t.elem(r).get("m_FullTypeName") or "").endswith("SIText"), paliers_[0])
    # BindingVariables + 1er lecteur (sections), puis le 2e (champs) dedans
    v = t.clone(var, setter, 0, src=s)
    for k in t.children(v)[1:]:
        t.remove(k)
    t.sd(v)["name"], t.sd(v)["name_UxmlAttributeFlags"] = NOM_EDITEUR, 1
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = ["row-direction-normal", "align-items-center"], -1
    src_sections = t.children(v)[0]
    sections, nom_section = _lecteur(t, t, src_sections, v, liste, INDEX_SECTION)
    t.remove(src_sections)
    champ, nom_champ = _lecteur(t, s, champs, sections, f"{nom_section}.Fields", INDEX_CHAMP)
    valeur = f"{nom_champ}.PropertyValue"
    exact = _texte_visible(t, st, vis, champ, valeur, False, "")
    if contenu is not None:
        contenu(exact, valeur)
    else:
        txt = text_direct(t, modele, exact, valeur)
        t.sd(txt)["name"] = ""
    repli = _texte_visible(t, st, vis, champ, valeur, True, "")
    branches = _garde(t, setter, liste)
    if branches is not None:   # v2 : sans objet éditeur, copie des paliers dans NoData
        move(t, v, branches[0])
        for r in paliers_:
            t.clone(r, branches[1])
    for r in paliers_:
        move(t, r, repli)
    if branches is None:
        return ["pastille Entraînement : note exacte (objet éditeur du club), fourchette si elle est vide ou sans "
                "éditeur (garde introuvable : fourchette absente sans éditeur)"]
    return ["pastille Entraînement : note exacte (objet éditeur du club), fourchette si elle est vide ou sans éditeur"]


def pastille_exacte(t, base):
    if first(t, lambda r: t.name(r) == NOM_EXACTE):
        return []
    setter = first(t, lambda r: t.name(r) == "border-setter")
    if setter is None or not exacte(t, setter, base):
        return ["pastille ou modèles introuvables, ignoré"]
    return ["pastille : note exacte /20"]


def bloc_entrainement(t):
    inst = [r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == "facilities-rating"
            and not t.elem(r).get("m_SerializedDataOverride")]
    if not inst:
        return [] if any(t.elem(r).get("m_TemplateAlias") == "FacilitiesRatingTraining" for r in t.walk()) \
            else ["pastille introuvable, ignoré"]
    usings = t.tt.setdefault("m_Usings", [])
    if not any(u["alias"] == "FacilitiesRatingTraining" for u in usings):
        model = next(u for u in usings if u["alias"] == "facilities-rating")
        u = copy.deepcopy(model)
        u["alias"], u["path"] = "FacilitiesRatingTraining", GUID_PASTILLE_ENTRAINEMENT
        usings.append(u)
    for r in inst:
        t.elem(r)["m_TemplateAlias"] = "FacilitiesRatingTraining"
        if "templateId" in t.sd(r):
            t.sd(r)["templateId"] = "FacilitiesRatingTraining"
    return ["pastille Entraînement : modèle FacilitiesRatingTraining (fourchettes)"]


def recrutement(t):
    done = first(t, lambda r: t.name(r) == NOM_RECRUTEMENT)
    if done is not None:   # version précédente (fourchettes) : on passe à la note exacte
        if first(t, lambda r: t.name(r) == NOM_EXACTE, done):
            return []
        setter = first(t, lambda r: t.name(r) == "border-setter", done)
        if setter is None or not exacte(t, setter, ETOILES_RECRUTEMENT):
            return ["pastille recopiée ou modèles introuvables, ignoré"]
        return ["Recrutement des jeunes : note exacte /20 (au lieu de la fourchette)"]
    inst = None
    for r in t.walk():
        e = t.elem(r)
        if e.get("m_TemplateAlias") != "facilities-rating":
            continue
        for ov in e.get("m_SerializedDataOverride") or []:
            tb = (t.refs[ov["m_SerializedData"]["rid"]].get("data") or {}).get("TextBinding") or {}
            if tb and (tb["m_direct"]["Path"]["m_path"].lower() == CHEMIN_RECRUTEMENT.lower()
                       or CHEMIN_RECRUTEMENT.lower() in (p.lower() for p in nb.paths_in(
                           tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]))):
                inst = r
    s, s_bundle = src_tree("FacilitiesRating")
    if inst is None or s is None:
        return ["pastille Recrutement des jeunes introuvable, ignoré"]
    cont = first(s, lambda r: s.name(r) == "rating-container")
    by_id = {s.elem(r).get("m_Id"): s.name(r) for r in s.walk()}
    overrides = {by_id.get(ov["m_ElementId"]): t.refs[ov["m_SerializedData"]["rid"]]["data"]
                 for ov in t.elem(inst).get("m_SerializedDataOverride") or []}
    parent = t.parent[inst]
    new = t.clone(cont, parent, t.children(parent).index(inst), src=s)
    t.styles.copy_from(Styles(s_bundle, s.tt), t, new)
    t.sd(new)["name"] = NOM_RECRUTEMENT
    t.sd(new)["name_UxmlAttributeFlags"] = 1
    t.elem(new)["m_Classes"] = list(t.elem(new).get("m_Classes") or []) + list(t.elem(inst).get("m_Classes") or [])
    for r in t.walk(new):   # couleurs : celles que la tuile donnait à la pastille (niveau de recrutement)
        ov = overrides.get(t.name(r))
        if ov and "BindFunction" in ov:
            t.sd(r)["BindFunction"] = copy.deepcopy(ov["BindFunction"])
    setter = first(t, lambda r: t.name(r) == "border-setter", new)
    t.remove(inst)
    if setter is None or not exacte(t, setter, ETOILES_RECRUTEMENT):
        return ["texte de la pastille recopiée introuvable, ignoré"]
    return ["Recrutement des jeunes : note exacte /20 au lieu du libellé"]


def encadrement(t):
    """Encadrement des jeunes : la note (club.YouthCoachingLevel) au lieu du libellé. Faisait partie de la seule
    recette des textes (choix 3) : sans elle, la tuile Infrastructure gardait le libellé (MAJ du 2026-11-12)"""
    found = [d for _, d in nb.targets(t.tt, "@" + CHEMIN_ENCADREMENT)]
    for d in found:
        d["TextBinding"]["m_kind"] = 1
        d["TextBinding"]["m_direct"]["Path"]["m_path"] = NOTE_ENCADREMENT
    return ["Encadrement des jeunes : note /20 au lieu du libellé"] if found else []


def tuile_jeunes(t):
    return recrutement(t) + encadrement(t)


def jobs():
    return [(m, (lambda p: lambda t: pastille(t, p))(p)) for m, p in PASTILLES.items()] \
        + [(m, (lambda b: lambda t: pastille_exacte(t, b))(b)) for m, b in EXACTES.items()] \
        + [(BLOC_ENTRAINEMENT, bloc_entrainement), (TUILE_JEUNES, tuile_jeunes)]


MODELES = list(PASTILLES) + list(EXACTES) + [BLOC_ENTRAINEMENT, TUILE_JEUNES]
MODELES_ORIGINE = MODELES + ["FacilitiesRating"]   # + pastille générique, touchée par la recette des textes


# ---------- commandes ----------
def cmd_appliquer():
    changed = 0
    for model, fn in jobs():
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        t = Tree(tt)
        t.styles = Styles(bundle, tt)
        msgs = fn(t)
        for m in msgs or ["déjà appliqué"]:
            print(f"{model} : {m}")
        if not [m for m in msgs if "introuvable" not in m]:
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        changed += 1
    if changed:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def remettre_origine():
    """modèles des installations (les nôtres + ceux de la recette des textes, qui n'est posée qu'avec cette fonction
    depuis le 2026-10-31) différents de la sauvegarde : remis d'origine, libellés de FM (Bon, Correct...)"""
    changed = False
    for model in MODELES_ORIGINE:
        bundle, obj, tt = nb.find_vta(model)
        if tt is None or not os.path.exists(backup.backup_path(bundle)):
            continue
        orig_env = UnityPy.load(backup.backup_path(bundle))
        orig = next((o for o in orig_env.objects if o.path_id == obj.path_id), None)
        if orig is None:
            continue
        orig_tt = orig.read_typetree()
        if tt != orig_tt:
            obj.save_typetree(orig_tt)
            nb._dirty.add(bundle)
            changed = True
            print(f"{model} : remis d'origine")
    if changed:
        nb.save_all()
    return changed


def cmd_retirer():
    """remet les modèles touchés tels qu'à l'origine (sauvegarde) ; la recette des textes n'est plus réappliquée
    (elle affichait des notes même fonction coupée, signalé le 2026-10-31)"""
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    if not remettre_origine():
        print("rien à retirer")


def cmd_etat():
    for model in MODELES:
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
            continue
        t = Tree(tt)
        n = len([r for r in t.walk() if t.name(r) == NOM_PALIER])
        exact = any(t.name(r) == NOM_EXACTE for r in t.walk())
        alias = any(t.elem(r).get("m_TemplateAlias") == "FacilitiesRatingTraining" for r in t.walk())
        print(f"{model} : " + ("note exacte" if exact else f"{n} paliers" if n else
                               "pastille FacilitiesRatingTraining" if alias else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
        elif not remettre_origine():   # notes laissées par l'ancienne recette posée d'office : retirées
            print("notes des installations : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
