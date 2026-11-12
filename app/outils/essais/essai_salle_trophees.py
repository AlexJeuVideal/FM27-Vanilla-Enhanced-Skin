"""ESSAI : bandeau « Salle des trophées » à la place des Actualités de la page club (2026-11-09).

Choix du joueur : tous les modes d'affichage (Défaut / Détaillé / Condensé), victoires seulement, ordre du palmarès de
FM, défilement de droite à gauche à la souris (pas automatique). Rien de FM n'est remplacé ailleurs :
- carte d'un trophée = modèle LIBRE de FM réécrit (CareerMilestoneYearRow, jamais affiché par FM, liste
  notes_claude\\modeles_libres_2026-11-05.txt) : paramètre `row` (ligne du palmarès, type 1850369140) ; SIVisible
  « row.Winners.Count > 0 » > image du trophée (chargeur d'images de FM en type Continent, id de la compétition :
  FMVE Trophies, commun\\trophees_photos.py) + nom (zone de survol : bulle avec les années de victoire) + nombre ;
- bandeau = titre + SIScrollView horizontal > WrappedObjectList (recopiée de TeamMeetingBlock #Players) sur la liste
  du palmarès du club (chemin lu dans la liste du palmarès déjà présente dans ClubSiteBlock), ItemTemplate = la carte.
ClubSiteBlock appartient à club_page_bas : l'essai repart de l'original (+ club_page_bas reconstruit s'il est actif),
puis pose le bandeau à la place de #News (ou de son SIVisible « hors Défaut »).
Essai : texte FR seul ; seulement ClubSiteBlock (fenêtre large ; MidRes / LowRes plus tard).

Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_salle_trophees.py appliquer [--dry-run] | retirer [--dry-run]
"""
import copy
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from elements import copy_usings  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint, text_direct, text_static  # noqa: E402
import club_page_bas as cpb  # noqa: E402
import trophees_photos  # noqa: E402

# =====================================================================================================
TITRE = "Salle des trophées"   # essai : FR seul
CARTE_LARGEUR = 124            # px (v3 : 116 -> 124)
IMAGE_TAILLE = 100             # px (v2 : 72 -> 84 ; v3 : 100, « remplir mieux le bandeau »)
NOM_HAUTEUR = 32               # px, zone du nom fixe (2 lignes) : tous les nombres sur la même ligne (v2)
HAUTEUR_DEFILE = 174           # px, hauteur du bandeau sous le titre (barre comprise ; v4 : 192 -> 174, vide en bas)
MARGE_BAS = 2                  # px sous le bloc (v4 : 8 -> 2)
BARRE = "unity-scroll-view__horizontal-scroller"   # barre horizontale de Unity : visible au survol du bloc (v3)
# =====================================================================================================
PAGE = "ClubSiteBlock"
CARTE = "CareerMilestoneYearRow"                      # modèle libre (jamais affiché par FM)
GUID_CARTE = "319a011ca9602c543a54c413cfa38cd0"       # son GUID Addressables (m_Container vérifié le 2026-11-09)
TYPE_LIGNE = 1850369140                               # type de `row` des lignes du palmarès (ClubHistoryHonourCardRow)
SOURCE_LISTE = ("TeamMeetingBlock", "Players")         # WrappedObjectList de FM
SOURCE_LOGO = "CompetitionLogo"                        # SIImage du chargeur d'images (comp.ObjectLookupData)
SOURCE_SURVOL = "PlayerReportPreviewTooltip"           # « i » de FM : zone de survol + SI.Bindable.Tooltip
TYPE_IMAGE = 11                                        # Continent : graphics/pictures/continent/<id>/logo
VERSION = 4   # v2 : trophée 84 px, zone du nom à hauteur fixe (nombres alignés) ; v3 : 100 px, barre au survol ;
              # v4 : moins de vide en bas
CL_BLOC = f"uipicker-trophees-v{VERSION}"
NOM_BLOC = f"UIPickerSalleTrophees-v{VERSION}"
NOM_CARTE = f"UIPickerTropheeCarte-v{VERSION}"
SCROLL_HORIZONTAL, BARRE_AUTO, BARRE_CACHEE = 1, 0, 2
OP_SUPERIEUR = 4
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "min-width": (131096, 3), "max-width": (131095, 3),
               "margin-right": (131092, 3), "margin-bottom": (131090, 3), "margin-top": (131093, 3),
               "flex-direction": (131083, 7), "flex-wrap": (131085, 7), "text-align": (65546, 7),
               "white-space": (65552, 7), "padding-left": (131099, 3), "padding-right": (131100, 3),
               "padding-top": (131101, 3), "padding-bottom": (131098, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
CENT = {"unit": 2, "value": 100.0}


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def first(t, pred, root=None):
    return next((r for r in t.walk(root) if pred(r)), None)


def plain(t, model, parent, cls, index=None, name=""):
    r = t.clone_shallow(model, parent, index)
    t.elem(r)["m_Classes"] = list(cls)
    t.elem(r)["m_RuleIndex"] = -1
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = name, 1 if name else 0
    return r


def source(nom):
    bundle, _, tt = nb.find_vta(nom)
    if tt is None:
        return None, None
    s = Tree(tt)
    return s, Styles(bundle, tt)


def path_arg(binding, path):
    """liaison de fonction FM (clé + chemin) avec un autre chemin"""
    b = copy.deepcopy(binding)
    args = decode_args(b["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = path.encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    b["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return b


def _arguments(sd):
    trouves = []

    def fouille(x):
        if isinstance(x, dict):
            ab = x.get("m_argumentBytes")
            if ab and b"GraphicsUtils+ResourceType" in bytes(ab):
                trouves.append(x)
            for v in x.values():
                fouille(v)
        elif isinstance(x, list):
            for v in x:
                fouille(v)
    fouille(sd)
    return trouves


# ---------- la carte (modèle libre réécrit) ----------
def image_trophee(t, parent):
    s, _ = source(SOURCE_LOGO)
    img = s and first(s, lambda r: typ(s, r) == "SIImage" and any(
        b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in _arguments(s.sd(r))))
    if img is None:
        return None
    r = t.clone(img, parent, None, src=s)
    for k in list(t.children(r)):
        t.remove(k)
    t.elem(r)["m_RuleIndex"] = -1
    t.elem(r)["m_Classes"] = []
    for x in _arguments(t.sd(r)):
        args = decode_args(x["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                a[1] = TYPE_IMAGE.to_bytes(4, "little")
            elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                ch = a[1][2:].decode()
                if ch.startswith("comp."):
                    ch = "row.Competition." + ch[len("comp."):]
                    a[1] = b"\x01" + _enc_varint(len(ch)) + ch.encode()
        x["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, r, {"width": IMAGE_TAILLE, "height": IMAGE_TAILLE, "min-width": IMAGE_TAILLE,
                          "min-height": IMAGE_TAILLE, "flex-shrink": 0, "margin-bottom": 6})
    return r


def zone_survol(t, parent):
    """« i » de FM recopié sans son icône, bulle vidée ; renvoie (zone, bulle)"""
    s, st = source(SOURCE_SURVOL)
    src = s and first(s, lambda r: "object-preview-hover-hotspot" in (s.elem(r).get("m_Classes") or []))
    if src is None:
        return None, None
    z = t.clone(src, parent, None, src=s)
    copy_usings(t, s, src)
    t.styles.copy_from(st, t, z)
    no_styles(t, z)
    t.elem(z)["m_Classes"] = ["sitext-hover-cursor", "align-items-center"]
    bulle = first(t, lambda r: typ(t, r) == "Tooltip", z)
    if bulle is None:
        return None, None
    for c in t.children(z):
        if c != bulle:
            t.remove(c)
    for c in t.children(bulle):
        t.remove(c)
    t.styles.style(t, z, {"max-width": CENT, "height": NOM_HAUTEUR, "min-height": NOM_HAUTEUR, "max-height":
                          NOM_HAUTEUR, "flex-shrink": 0, "justify-content": "flex-start", "overflow": "hidden"})
    return z, bulle


def construire_carte(t):
    racine = t.children(t.tt["m_VisualTree"]["rid"])
    expect = next((r for r in racine if typ(t, r) in ("BindingRoot", "BindingExpect")), None)
    row = expect and first(t, lambda r: t.name(r) == "Row", expect)
    txt = expect and first(t, lambda r: t.name(r) == "AchievementText", expect)
    if None in (expect, row, txt):
        return [f"{CARTE} : repères introuvables (#Row / #AchievementText)"]
    params = t.sd(expect).get("Parameters") or []
    if not params:
        return [f"{CARTE} : paramètre introuvable"]
    params[:] = [params[0]]
    params[0]["name"], params[0]["type"] = "row", {"id": TYPE_LIGNE}
    t.elem(expect)["m_Classes"] = []
    s_vis, vis = ni.visible_model()
    if vis is None:
        return ["modèle de comparaison FM introuvable"]
    v = ni.new_visible(t, s_vis, vis, expect, 0, NOM_CARTE,
                       ni.make_binding(s_vis.sd(vis)["Binding"], OP_SUPERIEUR, ["row.Winners.Count"], 0))
    t.sd(v)["name_UxmlAttributeFlags"] = 1
    t.elem(v)["m_RuleIndex"] = -1
    carte = plain(t, row, v, ["align-items-center"])
    t.styles.style(t, carte, {"width": CARTE_LARGEUR, "min-width": CARTE_LARGEUR, "flex-shrink": 0,
                              "padding-left": 4, "padding-right": 4, "padding-top": 4, "margin-right": 8})
    if image_trophee(t, carte) is None:
        return [f"{SOURCE_LOGO} : image introuvable"]
    z, bulle = zone_survol(t, carte)
    if z is None:
        return [f"{SOURCE_SURVOL} : zone de survol introuvable"]
    nom = text_direct(t, txt, z, "row.Competition.Name")
    t.elem(nom)["m_Classes"] = ["body-sm-regular", "global-text-primary"]
    t.elem(nom)["m_RuleIndex"] = -1
    t.styles.style(t, nom, {"text-align": "middle-center", "white-space": "normal", "max-width": CARTE_LARGEUR})
    p = plain(t, row, bulle, ["padding-horizontal-global-padding-regular", "padding-vertical-global-padding-regular"])
    ans = text_direct(t, txt, p, "row.Winners.Years")
    t.elem(ans)["m_Classes"] = ["body-sm-regular", "global-text-primary"]
    t.elem(ans)["m_RuleIndex"] = -1
    nb_ = text_direct(t, txt, carte, "row.Winners.Count")
    t.elem(nb_)["m_Classes"] = ["heading-small-16px", "global-text-primary"]
    t.elem(nb_)["m_RuleIndex"] = -1
    t.styles.style(t, nb_, {"text-align": "middle-center", "margin-top": 2})
    t.remove(row)   # #Row d'origine (trait, image de récompense, texte) : plus utilisé
    return [f"carte : image {IMAGE_TAILLE} px (type {TYPE_IMAGE}) + nom (années au survol) + nombre, victoires seulement"]


# ---------- le bandeau (ClubSiteBlock) ----------
def regle(t, survol, props, specificite):
    """règle « .CL_BLOC[:hover] .BARRE » dans la feuille intégrée du modèle (comme kinito_cartes_jeunes.regle_survol,
    vu en jeu : parties [classe (+ pseudo-classe hover)] puis [classe], relations 0 puis 2 = descendant)"""
    idx = t.styles.add_rule(props)
    tete = [{"m_Value": CL_BLOC, "m_Type": 3}] + ([{"m_Value": "hover", "m_Type": 4}] if survol else [])
    t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": specificite, "ruleIndex": idx, "m_Selectors": [
        {"m_Parts": tete, "m_PreviousRelationship": 0},
        {"m_Parts": [{"m_Value": BARRE, "m_Type": 3}], "m_PreviousRelationship": 2}]}]


def barre_au_survol(t, bloc):
    """barre de défilement invisible, visible quand la souris est dans le bloc (opacité : sa place reste)"""
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}
    feuilles = t.elem(bloc).setdefault("m_Stylesheets", [])
    if ref not in feuilles:
        feuilles.append(ref)
    opacite = 458767   # StylePropertyId Opacity (float)
    regle(t, False, [(opacite, "", [(2, 0.0)])], 20)
    regle(t, True, [(opacite, "", [(2, 1.0)])], 31)
def construire_bandeau(t):
    news = first(t, lambda r: t.name(r) == "News")
    if news is None:
        return [f"{PAGE} : #News introuvable"]
    cible = news
    if t.name(t.parent[news]).startswith(cpb.PREFIXE + "Actualites"):   # SIVisible « hors Défaut » de club_page_bas
        cible = t.parent[news]
    parent = t.parent[cible]
    idx = t.children(parent).index(cible)
    honneurs = first(t, lambda r: typ(t, r) == "StreamedObjectList" and "HistoryHonours" in (
        ((t.sd(r).get("Binding") or {}).get("m_direct") or {}).get("Path", {}).get("m_path") or ""))
    chemin = honneurs and t.sd(honneurs)["Binding"]["m_direct"]["Path"]["m_path"]   # club.HistoryHonours.HistoryHonoursList
    defile_src = first(t, lambda r: typ(t, r) == "SIScrollView")
    texte_src = first(t, lambda r: typ(t, r) == "SIText" and isinstance(t.sd(r).get("TextBinding"), dict))
    s_l, _ = source(SOURCE_LISTE[0])
    liste_src = s_l and first(s_l, lambda r: s_l.name(r) == SOURCE_LISTE[1] and typ(s_l, r) == "WrappedObjectList")
    manque = [n for n, x in (("liste du palmarès", chemin), ("SIScrollView", defile_src), ("SIText", texte_src),
                             (f"{SOURCE_LISTE[0]} #{SOURCE_LISTE[1]}", liste_src)) if not x]
    if manque:
        return [f"{PAGE} : {', '.join(manque)} introuvable(s)"]
    bloc = plain(t, news, parent, [CL_BLOC], idx, NOM_BLOC)
    barre_au_survol(t, bloc)
    t.styles.style(t, bloc, {"width": CENT, "flex-grow": 0, "flex-shrink": 0, "margin-bottom": MARGE_BAS})
    titre = text_static(t, texte_src, bloc, TITRE)
    t.elem(titre)["m_Classes"] = ["heading-small-16px", "global-text-primary"]
    t.elem(titre)["m_RuleIndex"] = -1
    t.styles.style(t, titre, {"margin-bottom": 8})
    defile = t.clone_shallow(defile_src, bloc)
    sd = t.sd(defile)
    sd["name"] = ""
    t.elem(defile)["m_Classes"] = []
    t.elem(defile)["m_RuleIndex"] = -1
    sd["mode"], sd["mode_UxmlAttributeFlags"] = SCROLL_HORIZONTAL, 1
    sd["horizontalScrollerVisibility"], sd["horizontalScrollerVisibility_UxmlAttributeFlags"] = BARRE_AUTO, 1
    sd["verticalScrollerVisibility"], sd["verticalScrollerVisibility_UxmlAttributeFlags"] = BARRE_CACHEE, 1
    t.styles.style(t, defile, {"width": CENT, "height": HAUTEUR_DEFILE, "flex-shrink": 0})
    w = t.clone(liste_src, defile, 0, src=s_l)
    no_styles(t, w)
    sd = t.sd(w)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_CARTE, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
    sd["ItemParamName"] = "row"
    t.elem(w)["m_Classes"] = []
    t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "nowrap", "flex-shrink": 0})
    t.remove(cible)
    return [f"bandeau à la place de #News{' (et de son SIVisible hors Défaut)' if cible != news else ''} : "
            f"{chemin}, défilement horizontal"]


# ---------- ouverture / enregistrement ----------
def ouvrir(modele):
    """modèle repris de l'original (feuille de style d'origine aussi)"""
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    orig = cpb.original(bundle, obj)
    if orig is None:
        return None
    sheet = cpb.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    t = Tree(orig)
    t.styles = Styles(bundle, orig)
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, orig, t


def page_de_base():
    """ClubSiteBlock d'origine, reconstruit par club_page_bas s'il est actif ; (travail, messages)"""
    o = ouvrir(PAGE)
    if o is None:
        return None, [f"{PAGE} : pas de sauvegarde d'origine"]
    if os.path.exists(cpb.MARKER):
        return o, [f"club_page_bas : {m}" for m in cpb.construire(o[3])]
    return o, []


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    cmd = argv[0] if argv else ""
    if cmd not in ("appliquer", "retirer"):
        sys.exit(__doc__)
    if cmd == "retirer":   # rien posé : rien réécrit (105 / choix 1 retirent tous les essais)
        poses = []
        for m in (PAGE, CARTE):
            _, _, tt = nb.find_vta(m)
            if tt is not None:
                t = Tree(tt)
                poses += [n for n in (t.name(r) for r in t.walk()) if n.startswith(("UIPickerSalleTrophees",
                                                                                   "UIPickerTropheeCarte"))]
        if not poses:
            print("salle des trophées : rien à retirer")
            return
    page, msgs = page_de_base()
    carte = ouvrir(CARTE)
    if page is None or carte is None:
        print(f"salle des trophées : {PAGE} / {CARTE} sans sauvegarde d'origine, rien fait")
        return
    if cmd == "appliquer":
        msgs += construire_carte(carte[3]) + construire_bandeau(page[3])
        d, n = trophees_photos.ecrire(nb.DRY_RUN)
        msgs.append(f"images : {n} trophées dans {d}" if d else "images : dossier FMVE Trophies absent")
    else:
        msgs.append(f"{PAGE} et {CARTE} remis (club_page_bas gardé s'il est actif)")
    for m in msgs:
        print(f"salle des trophées : {m}")
    if any("introuvable" in m for m in msgs):
        print("salle des trophées : rien enregistré")
        return
    for bundle, obj, tt, t in (page, carte):
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
