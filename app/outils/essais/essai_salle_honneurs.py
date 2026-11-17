"""ESSAI salle des trophées : Club > Histoire du club > Honneurs devient une vraie salle des trophées (2026-11-15).

- Fond : image IA du joueur (rouge = marbre noir, blanche = marbre blanc ; outils\\club\\images\\UIPickerSalle*),
  posée par commun\\fonds_jeu.py dans la texture « Trophy Cabinet » de FM (citée par aucun écran). Murs « club » :
  image aux murs transparents + aplat à la couleur du club dessous (teamcontainer.TitlebarBackgroundColour, comme le
  stade générique de club_page_bas).
- Salle = boîte de taille fixe par mode d'affichage (proportions de l'image : les étagères restent au bon endroit),
  centrée dans #Frame (débord coupé). Trophées gagnés seulement, ordre du palmarès de FM, 6 par étagère (1 par
  vitrine des côtés, 2 dans la grande du centre), 3 étagères = 18 au plus (les suivants coupés).
- Carte d'un trophée = modèle LIBRE de FM réécrit (ClubSiteClubNewsCard, jamais affiché) : image (pack FMVE Trophies,
  comme salle_trophees), nombre de victoires en pastille, nom + années dans une bulle au survol.
- ClubHistoryHonoursBlock (liste du palmarès) : repart de l'original ; retirer le remet.

Usage : essai_salle_honneurs.py appliquer [rouge|blanche] [club] [--dry-run] | retirer [--dry-run] | etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, no_styles  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402
import salle_trophees as st  # noqa: E402
import club_page_bas as cpb  # noqa: E402
import fonds_jeu  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
# largeur de la salle (px FM) par mode d'affichage (0 = Large, 1 = Medium, 2 = Small) ; hauteur = 16:9
LARGEUR = {0: 1280, 1: 1600, 2: 1600}
IMAGE_PART = 0.72         # image du trophée : part de la largeur d'une place (limitée par la hauteur d'étagère)
POLICE_NOMBRE = {0: 12, 1: 14, 2: 14}
# géométrie de chaque image (fractions) : bord gauche de la 1re place, pas entre 2 places (6 par étagère, centres
# dans les vitrines), bas des 3 étagères (dessus du verre / fond de vitrine). Mesuré sur les images 1672 x 941.
GEO = {"Rouge": dict(gauche=112 / 1672, pas=241.8 / 1672, haut=375 / 941, bas=632 / 941),
       "Blanche": dict(gauche=117 / 1672, pas=240 / 1672, haut=373 / 941, bas=655 / 941)}
FOND_AUTOUR = {"Rouge": (18 / 255, 6 / 255, 8 / 255, 1), "Blanche": (40 / 255, 14 / 255, 18 / 255, 1)}   # autour
PAR_ETAGERE, ETAGERES = 6, 3
# =====================================================================================================

BLOC = "ClubHistoryHonoursBlock"
CARTE = "ClubSiteClubNewsCard"
GUID_CARTE = "feafd82777195a84aa513bc26d0245cf"
FOND_GENERAL = "GameWorldBackground"
COULEUR_CLUB = "teamcontainer.TitlebarBackgroundColour"
VERSION = 1
PREFIXE = "UIPickerSalleHonneurs"
NOM_BLOC = f"{PREFIXE}-v{VERSION}"
NOM_CARTE = f"{PREFIXE}Carte-v{VERSION}"
MARKER = fonds_jeu.SALLE_MARKER
POURCENT = cpb.POURCENT
for _k, _v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
               "bottom": (131080, 3), "width": (131105, 3), "height": (131087, 3), "min-width": (131097, 3),
               "min-height": (131096, 3), "max-width": (131095, 3), "max-height": (131094, 3),
               "flex-direction": (131083, 7), "flex-wrap": (131086, 7), "justify-content": (131088, 7),
               "align-items": (131073, 7), "padding-left": (131099, 3), "padding-right": (131100, 3),
               "padding-top": (131101, 3), "padding-bottom": (131098, 3), "margin-bottom": (131090, 3),
               "font-size": (65537, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
PLEIN = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0,
         "width": POURCENT(100), "height": POURCENT(100)}


def tailles(theme, k):
    g = GEO[theme]
    w = LARGEUR[k]
    h = round(w * 9 / 16)
    pas = w * g["pas"]
    rang = h * (g["bas"] - g["haut"]) / (ETAGERES - 1)
    return dict(w=w, h=h, cw=round(pas), rh=round(rang), gauche=round(w * g["gauche"]),
                haut=round(h * g["haut"] - rang), img=round(min(pas * IMAGE_PART, rang * 0.85)))


# ---------- la carte (modèle libre réécrit) ----------
def construire_carte(t, theme):
    racine = t.children(t.tt["m_VisualTree"]["rid"])
    root = next((r for r in racine if st.typ(t, r) in ("BindingRoot", "BindingExpect")), None)
    src = st.ouvrir(st.CARTE)   # CareerMilestoneYearRow d'origine : #Row, #AchievementText
    if root is None or src is None:
        return [f"{CARTE} : racine ou {st.CARTE} d'origine introuvable"]
    s = src[3]
    srow = st.first(s, lambda r: s.name(r) == "Row")
    stxt = st.first(s, lambda r: s.name(r) == "AchievementText")
    if srow is None or stxt is None:
        return [f"{st.CARTE} : #Row / #AchievementText introuvables"]
    params = t.sd(root).get("Parameters") or []
    if not params:
        return [f"{CARTE} : paramètre introuvable"]
    params[:] = [params[0]]
    params[0]["name"], params[0]["type"] = "row", {"id": st.TYPE_LIGNE}
    for k in list(t.children(root)):
        t.remove(k)
    t.elem(root)["m_Classes"] = []
    t.elem(root)["m_RuleIndex"] = -1   # style d'origine flex-grow 1 : les places s'étireraient (et les vides aussi)
    row = t.clone(srow, root, None, src=s)
    txt = t.clone(stxt, root, None, src=s)
    for r in (row, txt):
        no_styles(t, r)
    for k in list(t.children(row)):
        t.remove(k)
    # outils de salle_trophees.Carte (image, zone de survol, texte) sur ce modèle
    c = st.Carte.__new__(st.Carte)
    c.t, c.row, c.txt = t, row, txt
    sl, _ = st.source(st.SOURCE_LOGO)
    c.logo = (sl, sl and st.first(sl, lambda r: st.typ(sl, r) == "SIImage" and any(
        b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in st._arguments(sl.sd(r)))))
    ss, sst = st.source(st.SOURCE_SURVOL)
    c.survol = (ss, sst, ss and st.first(ss, lambda r: "object-preview-hover-hotspot" in (ss.elem(r).get("m_Classes")
                                                                                         or [])))
    if c.logo[1] is None or c.survol[2] is None:
        return [f"{st.SOURCE_LOGO} / {st.SOURCE_SURVOL} introuvables"]
    v = st.visible(t, root, "row.Winners.Count", st.OP_SUPERIEUR, 0, NOM_CARTE, 0)
    if v is None:
        return ["modèle de comparaison FM introuvable"]
    modes = {k: st.visible(t, v, st.MODE_AFFICHAGE, st.OP_EGAL, k, f"{NOM_CARTE}-mode{k}") for k in LARGEUR}
    for k, vk in modes.items():
        T = tailles(theme, k)
        place = st.plain(t, row, vk, [])
        t.styles.style(t, place, {"width": T["cw"], "min-width": T["cw"], "height": T["rh"], "min-height": T["rh"],
                                  "flex-shrink": 0, "flex-direction": "column", "justify-content": "flex-end",
                                  "align-items": "center"})
        z, bulle = c.zone_survol(place, T["img"])
        cadre = st.plain(t, row, z, [])
        t.styles.style(t, cadre, {"width": T["img"], "height": T["img"], "min-width": T["img"],
                                  "min-height": T["img"], "flex-shrink": 0})
        vi = st.visible(t, cadre, "row.Competition.UniqueId", st.OP_SUPERIEUR, st.ID_MAX_CONTINENT)
        c.image(vi if vi is not None else cadre, T["img"])
        pastille = st.plain(t, row, cadre, [])
        t.styles.style(t, pastille, {"position": "absolute", "right": 0, "top": 0, "padding-left": 5,
                                     "padding-right": 5, "background-color": (0, 0, 0, 0.6)})
        c.texte(pastille, "row.Winners.Count", ["heading-small-16px", "global-text-primary"],
                {"font-size": POLICE_NOMBRE[k], "text-align": "middle-center"})
        if bulle is not None:
            p = st.plain(t, row, bulle, ["padding-horizontal-global-padding-regular",
                                         "padding-vertical-global-padding-regular"])
            c.texte(p, "row.Competition.Name", ["heading-small-16px", "global-text-primary"], {})
            c.texte(p, "row.Winners.Years", ["body-sm-regular", "global-text-primary"], {})
    t.remove(row)
    t.remove(txt)
    return [f"carte : image + nombre, nom et années au survol ; places {', '.join(str(tailles(theme, k)['cw']) + ' px' for k in LARGEUR)}"]


# ---------- le bloc (ClubHistoryHonoursBlock) ----------
def fond_image(t, parent):
    _, _, tg = nb.find_vta(FOND_GENERAL)
    s = Tree(tg) if tg is not None else None
    img = s and st.first(s, lambda r: s.name(r) == "background_image")
    if img is None:
        return None
    r = t.clone(img, parent, None, src=s)
    for k in list(t.children(r)):
        t.remove(k)
    e = t.elem(r)
    e["m_RuleIndex"], e["m_Classes"] = -1, ["siimage"]
    d = t.sd(r)
    d["name"], d["name_UxmlAttributeFlags"] = "", 0
    d["ImageKind"] = 0
    d["StaticImage"]["m_AssetGUID"] = fonds_jeu.SALLE_GUID
    d["StaticImage_UxmlAttributeFlags"] = 1
    if "ScaleMode" in d:
        d["ScaleMode"] = 0   # étirée sur la boîte (mêmes proportions)
        if "ScaleMode_UxmlAttributeFlags" in d:
            d["ScaleMode_UxmlAttributeFlags"] = 1
    bd = d["Binding"]
    bd["m_kind"] = 0
    bd["m_direct"]["Path"]["m_path"] = ""
    bd["m_visualFunction"]["m_target"]["m_guid"] = ""
    bd["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    bd["m_visualFunction"]["m_outputs"]["m_variable"]["m_argumentBytes"] = []
    if "Binding_UxmlAttributeFlags" in d:
        d["Binding_UxmlAttributeFlags"] = 0
    t.styles.style(t, r, PLEIN)
    return r


def aplat_club(t, parent):
    s, _ = st.source(cpb.COULEUR_SOURCE[0])
    src = s and st.first(s, lambda r: ((s.sd(r).get("Binding") or {}).get("m_visualFunction") or {})
                         .get("m_target", {}).get("m_guid", "").startswith(cpb.COULEUR_SOURCE[1]))
    if not src:
        return None
    a = t.clone(src, parent, None, src=s)
    for k in list(t.children(a)):
        t.remove(k)
    t.elem(a)["m_RuleIndex"], t.elem(a)["m_Classes"] = -1, []
    t.sd(a)["name"], t.sd(a)["name_UxmlAttributeFlags"] = "", 0
    vf = t.sd(a)["Binding"]["m_visualFunction"]
    args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
    for x in args:
        if x[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            x[1] = b"\x01" + _enc_varint(len(COULEUR_CLUB)) + COULEUR_CLUB.encode()
    vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, a, PLEIN)
    return a


def construire_bloc(t, theme, murs):
    frame = st.first(t, lambda r: t.name(r) == "Frame")
    liste = frame and st.first(t, lambda r: st.typ(t, r) == "StreamedObjectList", frame)
    chemin = liste and t.sd(liste)["Binding"]["m_direct"]["Path"]["m_path"]   # teamcontainer.HistoryHonours...
    s_l, _ = st.source(st.SOURCE_LISTE[0])
    liste_src = s_l and st.first(s_l, lambda r: s_l.name(r) == st.SOURCE_LISTE[1]
                                 and st.typ(s_l, r) == "WrappedObjectList")
    manque = [n for n, x in (("#Frame", frame), ("liste du palmarès", chemin),
                             (" #".join(st.SOURCE_LISTE), liste_src)) if not x]
    if manque:
        return [f"{BLOC} : {', '.join(manque)} introuvable(s)"]
    for k in list(t.children(frame)):
        t.remove(k)
    t.sd(frame)["name"] = NOM_BLOC   # repère (#Frame n'est cherché par personne d'autre)
    t.elem(frame)["m_Classes"] = [c for c in t.elem(frame)["m_Classes"] if c not in ("siblock-padding", "siblock-border")]
    t.styles.style(t, frame, {"overflow": "hidden", "align-items": "center", "justify-content": "center",
                              "flex-grow": 1, "background-color": FOND_AUTOUR[theme]})
    for k in LARGEUR:
        T = tailles(theme, k)
        vk = st.visible(t, frame, st.MODE_AFFICHAGE, st.OP_EGAL, k, f"{NOM_BLOC}-mode{k}")
        if vk is None:
            return ["modèle de comparaison FM introuvable"]
        boite = st.plain(t, frame, vk, [])
        for c in list(t.children(boite)):
            t.remove(c)
        t.styles.style(t, boite, {"width": T["w"], "height": T["h"], "min-width": T["w"], "min-height": T["h"],
                                  "flex-shrink": 0, "overflow": "hidden"})
        if murs == "club" and aplat_club(t, boite) is None:
            return [f"{cpb.COULEUR_SOURCE[0]} : échantillon de couleur introuvable"]
        if fond_image(t, boite) is None:
            return [f"{FOND_GENERAL} : image de fond introuvable"]
        vitrines = st.plain(t, frame, boite, [])
        for c in list(t.children(vitrines)):
            t.remove(c)
        larg, haut = T["cw"] * PAR_ETAGERE, T["rh"] * ETAGERES
        t.styles.style(t, vitrines, {"position": "absolute", "left": T["gauche"], "top": T["haut"],
                                     "width": larg, "height": haut, "overflow": "hidden"})
        w = t.clone(liste_src, vitrines, 0, src=s_l)
        no_styles(t, w)
        sd = t.sd(w)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_CARTE, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["VisualFuncBinding"] = st.path_arg(sd["VisualFuncBinding"], chemin)
        sd["ItemParamName"] = "row"
        t.elem(w)["m_Classes"] = []
        t.styles.style(t, w, {"flex-direction": "row", "flex-wrap": "wrap", "width": larg, "min-width": larg,
                              "max-width": larg, "flex-shrink": 0})
    return [f"salle {theme} (murs {murs}) : boîte {', '.join(str(LARGEUR[k]) for k in LARGEUR)} px, "
            f"{PAR_ETAGERE} x {ETAGERES} places ({chemin})"]


# ---------- commandes ----------
def marques(t):
    return [n for n in (t.name(r) for r in t.walk()) if n.startswith(PREFIXE)]


def reglage(argv):
    theme = "Blanche" if "blanche" in [a.lower() for a in argv] else "Rouge"
    murs = "club" if "club" in [a.lower() for a in argv] else "image"
    return {"theme": theme, "murs": murs}


def cmd_appliquer(argv):
    salle = reglage(argv)
    st.images()
    bloc, carte = st.ouvrir(BLOC), st.ouvrir(CARTE)
    if bloc is None or carte is None:
        print(f"{BLOC} / {CARTE} : introuvable ou pas de sauvegarde d'origine, rien fait")
        return
    msgs = construire_carte(carte[3], salle["theme"]) + construire_bloc(bloc[3], salle["theme"], salle["murs"])
    for m in msgs:
        print(f"salle des trophées : {m}")
    if any("introuvable" in m for m in msgs):
        print("salle des trophées : rien enregistré")
        return
    st.enregistrer([bloc, carte])
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump(salle, f)
    fonds_jeu.ecrire(a_blanc=nb.DRY_RUN, salle=salle)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    actuels = [st.ouvrir(m, False) for m in (BLOC, CARTE)]
    if all(a is not None and not marques(a[3]) for a in actuels):
        print("salle des trophées : rien à retirer dans les modèles")
    else:
        travail = [st.ouvrir(m) for m in (BLOC, CARTE)]
        if None in travail:
            print("salle des trophées : pas de sauvegarde d'origine, rien fait")
            return
        st.enregistrer(travail)
        print("salle des trophées : palmarès de FM remis")
    fonds_jeu.ecrire(a_blanc=nb.DRY_RUN, salle=None)


def cmd_etat():
    for m in (BLOC, CARTE):
        o = st.ouvrir(m, False)
        print(f"{m} : " + ("introuvable" if o is None else (", ".join(marques(o[3])) or "d'origine")))
    print("marqueur :", fonds_jeu.salle_auto())


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer(argv[1:])
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
