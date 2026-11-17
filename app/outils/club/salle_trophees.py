"""Salle des trophées : bandeau des trophées gagnés par le club, à la place des Actualités de la page club
(Vue d'ensemble), dans tous les modes d'affichage. Essai essai_salle_trophees v4 validé en jeu le 2026-11-09.

- Victoires seulement, ordre du palmarès de FM ; une carte par trophée : image (FMVE Trophies, commun\\
  trophees_photos.py), nom (années de victoire dans une bulle au survol), nombre de victoires ; défilement de droite à
  gauche à la souris, barre visible seulement quand la souris est dans le bloc.
- Mode d'affichage Défaut (« Large », écrans 1080p : FM agrandit tout) : cartes plus petites (TAILLES[0]), pour laisser
  la place aux transferts ; Détaillé / Condensé : TAILLES[1] (la v4 de l'essai).
- Rien de FM n'est remplacé ailleurs : la carte = modèle LIBRE de FM réécrit (CareerMilestoneYearRow, jamais affiché
  par FM : notes_claude\\modeles_libres_2026-11-05.txt) ; le bandeau = SIScrollView horizontal > WrappedObjectList
  (recopiée de TeamMeetingBlock #Players) sur club.HistoryHonours.HistoryHonoursList.
- ClubSiteBlock appartient à club_page_bas : on repart toujours de l'original (+ club_page_bas.construire s'il est
  actif) ; club_page_bas relance cette fonction après lui (catalogue.SUIVANTS). Retirer = la même page sans bandeau.
- Images : sans le pack de trophées (dossier graphics\\FMVE Trophies), FM met le logo de la compétition ; avec le pack,
  les compétitions sans image ont TROPHY_VIDE.png (transparent, trophees_photos.VIDE) : place vide.

Menu Outils FM.bat : 16 (catégorie), puis la fonction ; réappliqué par le choix 1.
Usage : salle_trophees.py appliquer | retirer | etat | si-actif [--dry-run]
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from elements import copy_usings, bulle_du_i  # noqa: E402
import notes_installations as ni  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint, text_direct, text_static  # noqa: E402
import club_page_bas as cpb  # noqa: E402
import trophees_photos  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
TITRE = L("Salle des trophées", "Trophy Room")
# par mode d'affichage (settings.AdaptiveScalingLevelIndex) : 0 = Défaut / « Large » (1080p, FM agrandit tout),
# 1 = les autres (Détaillé, Condensé). Valeurs en px :
#   carte (largeur), image, zone du nom (hauteur fixe : 2 lignes, nombres alignés), texte du nom (None = taille de FM),
#   texte du nombre (None = taille de FM), hauteur du défilement (barre comprise)
_NORMAL = dict(carte=124, image=100, nom=32, police_nom=None, police_nombre=None, defile=174)   # = essai v4 validé
TAILLES = {   # v2 : un SIVisible « mode == k » par mode (comme hierarchie_pyramide, vu en jeu ; v1 : « ≠ 0 »)
    0: dict(carte=92, image=62, nom=28, police_nom=11, police_nombre=14, defile=124),   # Défaut (« Large »)
    1: _NORMAL,   # Détaillé
    2: _NORMAL,   # Condensé
}
MARGE_BAS = 2   # px sous le bloc
# =====================================================================================================

PAGE = "ClubSiteBlock"
CARTE = "CareerMilestoneYearRow"                      # modèle libre (jamais affiché par FM)
GUID_CARTE = "319a011ca9602c543a54c413cfa38cd0"       # son GUID Addressables (m_Container vérifié le 2026-11-09)
TYPE_LIGNE = 1850369140                               # type de `row` des lignes du palmarès (ClubHistoryHonourCardRow)
SOURCE_LISTE = ("TeamMeetingBlock", "Players")         # WrappedObjectList de FM
# (v5 ESSAI RATÉ 2026-11-10 : chargeur Compétition avec nom d'image « trophy », source ClubInfoReportBlock -> FM
# affiche le LOGO de la compétition, le nom d'image est ignoré ; v4 : 1-7 liés -> logos CAF / AFC)
SOURCE_LOGO = "CompetitionLogo"                        # SIImage du chargeur d'images (comp.ObjectLookupData)
SOURCE_SURVOL = "PlayerReportPreviewTooltip"           # « i » de FM : zone de survol + SI.Bindable.Tooltip
TYPE_IMAGE = 11                                        # Continent : graphics/pictures/continent/<id>/logo
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"
OP_EGAL, OP_SUPERIEUR, OP_DIFFERENT = 2, 4, 5
VERSION = f"7{SUFFIXE}"   # v7 : FM du 2026-11-17, bulle des années reprise du sous-modèle du « i » ; -en : langue ; v2 : rangée jamais à la ligne, un SIVisible par mode (== 0 / 1 / 2) ;
                          # v3 : pas d'image pour les compétitions 1-7 (logos de continents de FM)
                          # v4 / v5 : essais ratés du 2026-11-10 ; v6 = v3 (retour)
ID_MAX_CONTINENT = 7      # ids 1-7 = continents (trophees_photos.CONTINENTS)
PREFIXE = "UIPickerBandeauTrophees"                    # (l'essai : UIPickerSalleTrophees / UIPickerTropheeCarte)
NOM_BLOC = f"{PREFIXE}-v{VERSION}"
NOM_CARTE = f"UIPickerCarteTrophee-v{VERSION}"
CL_BLOC = "uipicker-bandeau-trophees-v3"
BARRE = "unity-scroll-view__horizontal-scroller"       # barre horizontale de Unity : visible au survol du bloc
SCROLL_HORIZONTAL, BARRE_AUTO, BARRE_CACHEE = 1, 0, 2
OPACITE = 458767                                       # StylePropertyId Opacity (float)
MARKER = os.path.join(backup.BACKUP_DIR, "salle_trophees.actif")
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "min-width": (131096, 3), "max-width": (131095, 3),
               "min-height": (131097, 3), "max-height": (131094, 3), "margin-right": (131092, 3),
               "margin-bottom": (131090, 3), "margin-top": (131093, 3), "flex-direction": (131083, 7),
               "text-align": (65546, 7), "white-space": (65552, 7), "flex-wrap": (131086, 7),   # FlexWrap
               "padding-left": (131099, 3), "padding-right": (131100, 3), "padding-top": (131101, 3),
               "font-size": (65537, 3)}.items():
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
    return Tree(tt), Styles(bundle, tt)


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


def visible(t, parent, chemin, op, valeur, nom="", index=None):
    """SIVisible « chemin op valeur » (comparaison d'entiers de FM, comme club_page_bas)"""
    s_vis, vis = ni.visible_model()
    if vis is None:
        return None
    v = ni.new_visible(t, s_vis, vis, parent, index, nom, ni.make_binding(s_vis.sd(vis)["Binding"], op, [chemin], valeur))
    t.sd(v)["name_UxmlAttributeFlags"] = 1 if nom else 0
    t.elem(v)["m_RuleIndex"] = -1
    return v


def par_mode(t, parent, nom):
    """{mode : SIVisible « mode == k »} (les autres ne prennent pas de place)"""
    return {k: visible(t, parent, MODE_AFFICHAGE, OP_EGAL, k, f"{nom}-mode{k}") for k in TAILLES}


# ---------- la carte (modèle libre réécrit) ----------
class Carte:
    def __init__(self, t):
        self.t = t
        racine = t.children(t.tt["m_VisualTree"]["rid"])
        self.expect = next((r for r in racine if typ(t, r) in ("BindingRoot", "BindingExpect")), None)
        self.row = self.expect and first(t, lambda r: t.name(r) == "Row", self.expect)
        self.txt = self.expect and first(t, lambda r: t.name(r) == "AchievementText", self.expect)
        s, _ = source(SOURCE_LOGO)
        self.logo = (s, s and first(s, lambda r: typ(s, r) == "SIImage" and any(
            b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in _arguments(s.sd(r)))))
        s, st = source(SOURCE_SURVOL)
        self.survol = (s, st, s and first(s, lambda r: "object-preview-hover-hotspot" in (s.elem(r).get("m_Classes")
                                                                                         or [])))

    def manque(self):
        return [n for n, x in (("#Row", self.row), ("#AchievementText", self.txt), (SOURCE_LOGO, self.logo[1]),
                               (SOURCE_SURVOL, self.survol[2])) if x is None]

    def image(self, parent, taille):
        t, (s, img) = self.t, self.logo
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
        t.styles.style(t, r, {"width": taille, "height": taille, "min-width": taille, "min-height": taille,
                              "flex-shrink": 0})

    def zone_survol(self, parent, hauteur):
        """« i » de FM recopié sans son icône, bulle vidée ; renvoie (zone, bulle)"""
        t, (s, st, src) = self.t, self.survol
        z = t.clone(src, parent, None, src=s)
        copy_usings(t, s, src)
        t.styles.copy_from(st, t, z)
        no_styles(t, z)
        t.elem(z)["m_Classes"] = ["sitext-hover-cursor", "align-items-center"]
        bulle = bulle_du_i(t, z)   # FM du 2026-11-17 : bulle dans un sous-modèle
        for c in t.children(z):
            if c != bulle:
                t.remove(c)
        for c in t.children(bulle) if bulle is not None else []:
            t.remove(c)
        t.styles.style(t, z, {"max-width": CENT, "height": hauteur, "min-height": hauteur, "max-height": hauteur,
                              "flex-shrink": 0, "justify-content": "flex-start", "overflow": "hidden"})
        return z, bulle

    def texte(self, parent, chemin, classes, css):
        t = self.t
        r = text_direct(t, self.txt, parent, chemin)
        t.elem(r)["m_Classes"] = list(classes)
        t.elem(r)["m_RuleIndex"] = -1
        t.styles.style(t, r, css)
        return r

    def remplir(self, parent, k):
        T = TAILLES[k]
        t = self.t
        carte = plain(t, self.row, parent, ["align-items-center"])
        t.styles.style(t, carte, {"width": T["carte"], "min-width": T["carte"], "flex-shrink": 0, "padding-left": 4,
                                  "padding-right": 4, "padding-top": 4, "margin-right": 8 if k else 4})
        # v3 : cadre de la taille de l'image (place gardée) ; image seulement si l'id de la compétition > 7 (1-7 = ids des
        # continents : FM y garde ses logos, la Jupiler Pro League montrait la CAF ; essai du 2026-11-09)
        cadre = plain(t, self.row, carte, [])
        t.styles.style(t, cadre, {"width": T["image"], "height": T["image"], "min-width": T["image"],
                                  "min-height": T["image"], "flex-shrink": 0, "margin-bottom": 6})
        vi = visible(t, cadre, "row.Competition.UniqueId", OP_SUPERIEUR, ID_MAX_CONTINENT)
        self.image(vi if vi is not None else cadre, T["image"])
        z, bulle = self.zone_survol(carte, T["nom"])
        css = {"text-align": "middle-center", "white-space": "normal", "max-width": T["carte"]}
        if T["police_nom"]:
            css["font-size"] = T["police_nom"]
        self.texte(z, "row.Competition.Name", ["body-sm-regular", "global-text-primary"], css)
        if bulle is not None:
            p = plain(t, self.row, bulle, ["padding-horizontal-global-padding-regular",
                                           "padding-vertical-global-padding-regular"])
            self.texte(p, "row.Winners.Years", ["body-sm-regular", "global-text-primary"], {})
        css = {"text-align": "middle-center", "margin-top": 2}
        if T["police_nombre"]:
            css["font-size"] = T["police_nombre"]
        self.texte(carte, "row.Winners.Count", ["heading-small-16px", "global-text-primary"], css)

    def construire(self):
        t = self.t
        params = t.sd(self.expect).get("Parameters") or []
        if not params:
            return ["carte : paramètre introuvable"]
        params[:] = [params[0]]
        params[0]["name"], params[0]["type"] = "row", {"id": TYPE_LIGNE}
        t.elem(self.expect)["m_Classes"] = []
        v = visible(t, self.expect, "row.Winners.Count", OP_SUPERIEUR, 0, NOM_CARTE, 0)
        if v is None:
            return ["modèle de comparaison FM introuvable"]
        for k, vk in par_mode(t, v, NOM_CARTE).items():
            self.remplir(vk, k)
        t.remove(self.row)   # #Row d'origine (trait, image de récompense, texte) : plus utilisé
        tailles = " / ".join(f"{T['carte']}-{T['image']} px" for T in TAILLES.values())
        return [f"carte : image + nom (années au survol) + nombre, victoires seulement ; Défaut / autres modes : {tailles}"]


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
    regle(t, False, [(OPACITE, "", [(2, 0.0)])], 20)
    regle(t, True, [(OPACITE, "", [(2, 1.0)])], 31)


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
    t.styles.style(t, bloc, {"width": CENT, "flex-grow": 0, "flex-shrink": 0, "margin-bottom": MARGE_BAS})
    barre_au_survol(t, bloc)
    titre = text_static(t, texte_src, bloc, TITRE)
    t.elem(titre)["m_Classes"] = ["heading-small-16px", "global-text-primary"]
    t.elem(titre)["m_RuleIndex"] = -1
    t.styles.style(t, titre, {"margin-bottom": 8})
    for k, vk in par_mode(t, bloc, NOM_BLOC).items():
        if vk is None:
            return ["modèle de comparaison FM introuvable"]
        t.styles.style(t, vk, {"width": CENT})
        defile = t.clone_shallow(defile_src, vk)
        sd = t.sd(defile)
        sd["name"] = ""
        t.elem(defile)["m_Classes"] = []
        t.elem(defile)["m_RuleIndex"] = -1
        sd["mode"], sd["mode_UxmlAttributeFlags"] = SCROLL_HORIZONTAL, 1
        sd["horizontalScrollerVisibility"], sd["horizontalScrollerVisibility_UxmlAttributeFlags"] = BARRE_AUTO, 1
        sd["verticalScrollerVisibility"], sd["verticalScrollerVisibility_UxmlAttributeFlags"] = BARRE_CACHEE, 1
        t.styles.style(t, defile, {"width": CENT, "height": TAILLES[k]["defile"], "flex-shrink": 0})
        w = t.clone(liste_src, defile, 0, src=s_l)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_CARTE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "row"
        t.elem(w)["m_Classes"] = []
        # v2 : jamais à la ligne (v1 en jeu : cartes en trop sur une 2e ligne cachée, plus de défilement)
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "nowrap", "flex-shrink": 0})
    t.remove(cible)
    return [f"bandeau à la place des Actualités ({chemin}), défilement horizontal, barre au survol"]


# ---------- ouverture / enregistrement ----------
def ouvrir(modele, depart_original=True):
    """(bundle, obj, typetree, arbre) ; depart_original : repris de l'original (feuille de style d'origine aussi)"""
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    if not depart_original:
        t = Tree(tt)
        t.styles = Styles(bundle, tt)
        return bundle, obj, tt, t
    orig = cpb.original(bundle, obj)
    if orig is None:
        return None
    sheet = cpb.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    t = Tree(orig)
    t.styles = Styles(bundle, orig)
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, orig, t


def marques(t):
    return [n for n in (t.name(r) for r in t.walk()) if n.startswith((PREFIXE, "UIPickerCarteTrophee"))]


def page_de_base():
    """ClubSiteBlock d'origine, reconstruit par club_page_bas s'il est actif ; (travail, messages)"""
    o = ouvrir(PAGE)
    if o is None:
        return None, [f"{PAGE} : pas de sauvegarde d'origine"]
    if os.path.exists(cpb.MARKER):
        return o, [f"club_page_bas : {m}" for m in cpb.construire(o[3])]
    return o, []


def enregistrer(travail):
    for bundle, obj, tt, t in travail:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    nb.save_all()


def images():
    d, n = trophees_photos.ecrire(nb.DRY_RUN)
    print(L(f"images des trophées : {n} dans {d}", f"trophy images: {n} in {d}") if d else
          L("images des trophées : dossier FMVE Trophies absent (pack pas installé : cartes sans image)",
            "trophy images: no FMVE Trophies folder (pack not installed: cards without images)"))


def cmd_appliquer():
    images()
    actuels = [ouvrir(m, False) for m in (PAGE, CARTE)]
    if None in actuels:
        print(f"{PAGE} / {CARTE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    if NOM_BLOC in marques(actuels[0][3]) and NOM_CARTE in marques(actuels[1][3]):
        print(f"{PAGE} : déjà appliqué")
    else:
        page, msgs = page_de_base()
        carte = ouvrir(CARTE)
        if page is None or carte is None:
            print(f"{PAGE} / {CARTE} : pas de sauvegarde d'origine, ignoré")
            return
        c = Carte(carte[3])
        if c.manque():
            msgs.append(f"morceaux de FM introuvables ({', '.join(c.manque())})")
        else:
            msgs += c.construire() + construire_bandeau(page[3])
        msgs += ["ancienne version remplacée"] if marques(actuels[0][3]) or marques(actuels[1][3]) else []
        for m in msgs:
            print(f"{PAGE} : {m}")
        if any("introuvable" in m for m in msgs):
            print(f"{PAGE} : rien enregistré")
            return
        enregistrer([page, carte])
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    actuels = [ouvrir(m, False) for m in (PAGE, CARTE)]
    if None in actuels or not (marques(actuels[0][3]) or marques(actuels[1][3])):
        print("rien à retirer")
        return
    page, msgs = page_de_base()
    carte = ouvrir(CARTE)
    if page is None or carte is None:
        print(f"{PAGE} / {CARTE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    for m in msgs:
        print(f"{PAGE} : {m}")
    enregistrer([page, carte])
    print(f"{PAGE} : salle des trophées retirée (Actualités remises)")


def cmd_etat():
    o = ouvrir(PAGE, False)
    if o is None:
        print(f"{PAGE} : introuvable")
        return
    m = marques(o[3])
    print(f"{PAGE} : " + (f"appliqué ({', '.join(m)} ; version actuelle v{VERSION})" if m else "sans salle des trophées"))
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
            print("salle des trophées : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
