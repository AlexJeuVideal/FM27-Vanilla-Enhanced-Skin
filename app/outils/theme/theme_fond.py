"""Thème du fond des pages : remplace le fond violet de FM dans les fichiers du jeu (sans le mod).

Le fond par défaut de FM est l'image "fm27_skin_default" (violette, avec le grand logo) du bundle
ui-backgrounds_assets_.bundle. Les pages aux couleurs du club utilisent "fm27_skin_blended" (même dessin, en rouge)
que FM recolore avec la couleur du club. Ce script peint l'image violette à partir de ce dessin, dans la couleur
donnée : "appliquer rouge", "appliquer blue", "appliquer #8A1538" (menu : "30 rouge"), sinon COULEUR.
Liste des noms : "liste". (« club » retiré le 2026-11-12 à la demande du joueur.)

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\theme\\theme_fond.py appliquer [couleur] [infobulle] [--lisse|--motifs] [--dry-run]
  .venv\\Scripts\\python.exe outils\\theme\\theme_fond.py apercu [couleur]   (image d'essai dans backups\\, rien n'est écrit)
  .venv\\Scripts\\python.exe outils\\theme\\theme_fond.py liste
  .venv\\Scripts\\python.exe outils\\theme\\theme_fond.py retirer       (fond violet d'origine)
  .venv\\Scripts\\python.exe outils\\theme\\theme_fond.py etat
"""
import json
import os
import sys

import UnityPy
from PIL import Image, ImageChops
from UnityPy.enums import TextureFormat

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import notes_au_lieu_des_libelles as nb  # noqa: E402

# =====================================================================================================
# RÉGLAGES MODIFIABLES
COULEUR = "#2B2F36"           # sans couleur donnée : ex. "#1F6F43" (vert), "#2B2F36" (anthracite), "#14284B" (bleu nuit)
# Pages de club (effectif, site du club...) : FM recolore lui-même leur fond aux couleurs du club (pendant le jeu,
# impossible à remplacer par les fichiers). Choix :
#   "club"        : comme FM (couleurs du club)
#   "noir"        : fond uni très sombre (le noir ne prend aucune couleur de club)
#   "transparent" : on voit à travers... mais aussi la page précédente en fantôme (déconseillé)
#   "portail"     : le cadre des pages de club (modèles FigmaBaseSite*) lit le même fond que les autres pages
#                   (game.BackgroundImage.BackgroundImage) au lieu de la fonction "image rouge + couleurs du club"
#   "mire"        : 8 bandes (rouge, vert, bleu, blanc, gris, jaune, cyan, magenta) pour mesurer comment FM recolore
# (abandonné : brancher toutes les pages sur la fonction du site du club fait planter le jeu au chargement, la
#  fonction lit les couleurs dans le contexte du site du club, absent ailleurs)
PAGES_CLUB = "portail"
# Option « fond_pages » (page 500, outils\options.py) : "officiels" = cadres de FM gardés (fonds sous licence des
# compétitions / clubs affichés quand FM en a), la couleur reste sur l'image par défaut (tout ce qui n'a pas de fond
# officiel). "couleur" (défaut) = PAGES_CLUB ci-dessus.
try:
    import options as _options
    if _options.get("fond_pages") == "officiels":
        PAGES_CLUB = "origine"
except Exception:   # options.py absent : réglage ci-dessus
    pass
MIRE = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (128, 128, 128), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
# Couleur secondaire = fond des infobulles (popup du joueur au survol...). Donnée après la couleur principale
# ("30 rouge anthracite", "30 rouge #202020") ; sans couleur secondaire : ce gris foncé (plus de « couleur du fond
# assombrie » depuis le 2026-11-12, demande du joueur). None = gris d'origine de FM.
INFOBULLE_DEFAUT = "#1C1D20"
# =====================================================================================================

AA = nb.AA   # dossier du jeu : chemin_jeu.py (demandé par Outils FM.bat)
BUNDLE = os.path.join(AA, "ui-backgrounds_assets_.bundle")
CIBLE = "fm27_skin_default"
SOURCE = "fm27_skin_blended"
MARKER = os.path.join(backup.BACKUP_DIR, "theme_fond.actif")
DRY_RUN = "--dry-run" in sys.argv


# couleurs au choix : "30 rouge", "30 blue", "30 #8A1538"... (teintes assez soutenues pour garder le texte lisible)
# Chaque famille existe en 4 nuances : "rouge-clair", "rouge", "rouge-fonce", "rouge-sombre" (idem en anglais :
# "red-light", "red-dark", "red-deep"). Les noms de couleurs web anglais marchent aussi (ex. "crimson", "royalblue").
FAMILLES = [   # (noms, couleur de base)
    (("rouge", "red"), "#B3121F"),
    (("cerise", "cherry"), "#A3123E"),
    (("framboise", "raspberry"), "#B01E5A"),
    (("bordeaux", "burgundy"), "#7A1430"),
    (("rose", "pink"), "#B0305E"),
    (("fuchsia", "magenta"), "#A0207A"),
    (("prune", "plum"), "#6E2257"),
    (("violet", "purple"), "#6A3FA0"),
    (("lavande", "lavender"), "#6F5CB0"),
    (("indigo",), "#3B2D8F"),
    (("bleu", "blue"), "#1D4FA3"),
    (("roi", "royal"), "#2547C0"),
    (("ciel", "sky"), "#2A7AB8"),
    (("azur", "azure"), "#1C86C8"),
    (("marine", "navy"), "#14284B"),
    (("acier", "steel"), "#3D5A78"),
    (("petrole", "petrol"), "#0E5566"),
    (("turquoise", "teal"), "#0F7A78"),
    (("cyan",), "#0B8A9A"),
    (("menthe", "mint"), "#1E8A6A"),
    (("emeraude", "emerald"), "#0E7A4E"),
    (("vert", "green"), "#1F7A3A"),
    (("sapin", "forest"), "#1B5E34"),
    (("olive",), "#6B7224"),
    (("kaki", "khaki"), "#7A7040"),
    (("citron", "lime"), "#6E9A12"),
    (("jaune", "yellow"), "#B08A00"),
    (("or", "gold"), "#A07A1E"),
    (("moutarde", "mustard"), "#A3841A"),
    (("orange",), "#C2560C"),
    (("mandarine", "tangerine"), "#D0641A"),
    (("corail", "coral"), "#C04A3A"),
    (("saumon", "salmon"), "#B85A50"),
    (("brique", "brick"), "#9A3A22"),
    (("rouille", "rust"), "#9A4A1A"),
    (("cuivre", "copper"), "#A0582A"),
    (("bronze",), "#8A6230"),
    (("marron", "brown"), "#6B4423"),
    (("chocolat", "chocolate"), "#5A3220"),
    (("beige", "sand"), "#8A7A5A"),
    (("taupe",), "#6A5E54"),
    (("ardoise", "slate"), "#4A5868"),
    (("gris", "grey", "gray"), "#4A5058"),
    (("anthracite", "charcoal"), "#2B2F36"),
    (("noir", "black"), "#202329"),
]
NUANCES = {   # suffixe : facteur de luminosité
    ("-clair", "-light"): 1.35,
    ("",): 1.0,
    ("-fonce", "-dark"): 0.7,
    ("-sombre", "-deep"): 0.45,
}
CHOIX = None   # couleur donnée en argument (prioritaire sur COULEUR)
CHOIX2 = None  # couleur secondaire (infobulles) donnée en argument
# fond lisse (option facultative de la page Couleurs, 2026-11-12) : la couleur choisie unie, sans les formes en
# diagonale ni les dégradés du dessin de FM (depuis le 2026-11-10 : la couleur exacte, plus la teinte moyenne).
# --lisse / --motifs en argument ; sans : celui du marqueur (le choix 30 du menu, club_page_bas le gardent)
LISSE = None


def _shade(hexa, k):
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(min(255, round(v * k)) for v in (r, g, b))


COULEURS = {}
for _noms, _base in FAMILLES:
    for _sufs, _k in NUANCES.items():
        for _n in _noms:
            for _s in _sufs:
                COULEURS[_n + _s] = _shade(_base, _k)
                COULEURS[_n + _s.replace("-", "")] = COULEURS[_n + _s]   # "rougefonce" marche aussi


def colour():
    return to_rgb(CHOIX or COULEUR)


def colour2():
    """couleur des infobulles : celle donnée, sinon le gris foncé ; None = gris de FM"""
    c = CHOIX2 or INFOBULLE_DEFAUT
    if c is None:
        return None
    a = alpha(c)   # opacité choisie (#RRGGBBAA) : 4e valeur, lue par couleurs_interface._infobulle
    return to_rgb(c) + ((a,) if a < 1 else ())


def alpha(c):
    """opacité (0..1) d'un code #RRGGBBAA ; 1 pour tout le reste (#RRGGBB, noms). Le fond des pages l'ignore
    (image opaque : transparente, on verrait la page précédente en fantôme)"""
    c = (c or "").strip().lstrip("#") if isinstance(c, str) else ""
    if len(c) == 8 and all(ch in "0123456789abcdefABCDEF" for ch in c):
        return int(c[6:], 16) / 255
    return 1.0


def to_rgb(c):
    """(r, g, b) ; un code #RRGGBBAA donne aussi ses 3 couleurs (l'opacité : alpha())"""
    key = c.strip().lower().replace("é", "e").replace("è", "e").replace(" ", "-")
    if key == "club":
        sys.exit("la couleur « club » n'existe plus : choisis une couleur (ex. 30 rouge, 30 #3C3F45)\n" + liste())
    c = COULEURS.get(key, c).strip().lstrip("#")
    if len(c) in (6, 8) and all(ch in "0123456789abcdefABCDEF" for ch in c):
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    try:   # nom de couleur web anglais (crimson, royalblue, darkolivegreen...)
        from PIL import ImageColor
        return ImageColor.getrgb(key.replace("-", ""))[:3]
    except ValueError:
        sys.exit(f"couleur inconnue : {c!r}\n" + liste())


def label():
    return (CHOIX or "couleur") + " " + "#%02X%02X%02X" % colour()


def liste():
    fam = ", ".join("/".join(n) for n, _ in FAMILLES)
    return ("couleurs : " + fam + "\n"
            "nuances : ajoute -clair, -fonce ou -sombre (ex. rouge-fonce, bleu-clair, vert-sombre ; en anglais "
            "-light, -dark, -deep)\n"
            "ou un code #RRGGBB (#RRGGBBAA : avec opacité, sauf le fond des pages), ou un nom de couleur web anglais (crimson, royalblue, darkolivegreen...)")


def textures(env):
    out = {}
    for o in env.objects:
        if o.type.name == "Texture2D":
            t = o.read()
            if t.m_Name in (CIBLE, SOURCE):
                out[t.m_Name] = t
    return out


def paint(src, rgb):
    """le dessin rouge prend la couleur choisie (comme FM le fait pour le club) ; le bandeau sombre du haut reste"""
    r, g, b = src.convert("RGB").split()
    chans = []
    for i, (keep) in enumerate((None, g, b)):
        part = r.point(lambda v, k=rgb[i]: v * k // 255)
        chans.append(part if keep is None else ImageChops.add(part, keep))
    return Image.merge("RGB", chans)


def lisse():
    return bool(marker().get("lisse")) if LISSE is None else LISSE


def fond(src, rgb):
    """fond lisse (2026-11-10, demande du joueur) : exactement la couleur choisie, unie ; sinon le dessin de FM peint"""
    if lisse():
        return Image.new("RGB", src.size, tuple(rgb))
    return paint(src, rgb)


def build(path=BUNDLE):
    env = UnityPy.load(path)
    tex = textures(env)
    if CIBLE not in tex or SOURCE not in tex:
        sys.exit("images de fond introuvables (le jeu a changé ?)")
    return env, tex, fond(tex[SOURCE].image, colour())


def cmd_apercu():
    _, _, img = build(backup.backup_path(BUNDLE) if os.path.exists(backup.backup_path(BUNDLE)) else BUNDLE)
    out = os.path.join(backup.BACKUP_DIR, "apercu_theme_fond.png")
    os.makedirs(backup.BACKUP_DIR, exist_ok=True)
    small = img.copy()
    small.thumbnail((1280, 720))
    small.save(out)
    print(f"aperçu ({label()}) : {out}")


# tous les modèles dont le cadre (Card-frame) ou le fond (background_image) lit le fond des pages : pages de club
# (FigmaBaseSite*) et toutes les autres (effectif, rapports, outils...), plus le fond général GameWorldBackground
SITES = ("FigmaBaseSiteTemplate", "FigmaBaseSiteMultiGridTemplate",
         "FigmaBaseToolTemplate", "FigmaBaseToolTabbedTemplate", "FigmaBaseToolHeaderTemplate",
         "FigmaBaseToolTabbedHeaderTemplate", "FigmaBaseToolMultiGridTemplate", "FigmaBaseReportTabbedTemplate",
         "FigmaFullscreenBlockTemplate", "OnlineManagerAndGameStatus", "OnlineManagerAndGameStatusFullscreen",
         "ContractNegotiationToolTemplate", "PressConferenceDynamicCard", "PressConferenceSingleQuestionDynamicCard",
         "GameWorldBackground")
# toujours le fond de FM, quelle que soit la couleur choisie (demande du joueur 2026-11-10 : conférences de presse =
# image du stade / du club de FM). Restent dans SITES pour être remis d'origine sur un jeu déjà modifié.
HORS_THEME = ("PressConferenceDynamicCard", "PressConferenceSingleQuestionDynamicCard")
# écrans de match : ils incluent un modèle de base partagé (FigmaBaseTool*) ; leur surcharge du cadre de ce modèle
# (m_SerializedDataOverride, créée si absente) reçoit le cadre d'origine de FM, le reste du jeu garde notre fond
CARTES_MATCH = {"MatchPreviewCard": "FigmaBaseToolTemplate",
                "MatchPreparationCard": "FigmaBaseToolMultiGridTemplate",
                "PostMatchNewsPanel": "FigmaBaseToolMultiGridTemplate"}
# FM remplit game.BackgroundImage avec l'image rouge recolorée sur les pages de club : le cadre y reçoit donc une
# image FIXE, fm27_skin_default (GUID Addressables = clé du bundle ui-backgrounds), comme les images fixes de FM
GUID_DEFAULT = "a12c7fa5a8cef8149b7e084de2dcc07b"


def card_frame(tt):
    for r in (tt.get("references") or {}).get("RefIds", []):
        d = r.get("data") or {}
        if d.get("name") in ("Card-frame", "background_image") and "Binding" in d and "ImageKind" in d:
            return d
    return None


CHAMPS = ("Binding", "ImageKind", "StaticImage", "StaticImage_UxmlAttributeFlags", "Binding_UxmlAttributeFlags")
_ORIGINAUX = {}


def originaux():
    """{modèle: cadre d'origine} lus une fois dans les bundles de modèles sauvegardés (ou actuels s'ils sont intacts)"""
    if not _ORIGINAUX:
        for bundle in nb.BUNDLES:
            src = backup.backup_path(bundle)
            for o in UnityPy.load(src if os.path.exists(src) else bundle).objects:
                if o.type.name != "MonoBehaviour":
                    continue
                try:
                    name = o.peek_name()
                    if name in SITES:
                        d = card_frame(o.read_typetree())
                        if d:
                            _ORIGINAUX[name] = d
                    elif name in CARTES_MATCH:
                        _ORIGINAUX[name] = o.read_typetree()   # carte entière (surcharges d'origine)
                except Exception:
                    pass
    return _ORIGINAUX


def _surcharge(tt, alias, eid):
    """(entrée de surcharge, données) du cadre eid dans l'instance du modèle alias ; (instance, None) si absente"""
    R = {r["rid"]: r for r in tt["references"]["RefIds"]}
    for r in R.values():
        dd = r.get("data") or {}
        if dd.get("m_TemplateAlias") == alias and "m_SerializedDataOverride" in dd:
            for ov in dd["m_SerializedDataOverride"]:
                if ov["m_ElementId"] == eid and ov["m_ElementIdsPath"] == [eid]:
                    return dd, ov, R[ov["m_SerializedData"]["rid"]]["data"]
            return dd, None, None
    return None, None, None


def cartes_match(mode):
    """mode "portail" : la surcharge du cadre des écrans de match = cadre d'origine de FM ; sinon surcharges d'origine"""
    for carte, modele in CARTES_MATCH.items():
        tpl = originaux().get(modele)
        orig = originaux().get(carte)
        bundle, obj, tt = nb.find_vta(carte)
        if tpl is None or orig is None or tt is None:
            print(f"{carte} : introuvable (le jeu a changé ?), ignoré")
            continue
        eid = tpl["uxmlAssetId"]
        inst, ov, data = _surcharge(tt, modele, eid)
        if inst is None:
            print(f"{carte} : modèle {modele} introuvable, ignoré")
            continue
        _, ov0, data0 = _surcharge(orig, modele, eid)
        avant = json.dumps(tt, sort_keys=True)
        if mode == "portail":
            voulu = {k: tpl[k] for k in CHAMPS}
            if ov is None:   # nouvelle surcharge : copie du cadre d'origine du modèle
                types = [r for r in tt["references"]["RefIds"] if r["type"]["class"] == "SIImage/UxmlSerializedData"]
                if not types:
                    print(f"{carte} : type SIImage absent, ignoré")
                    continue
                rid = max(r["rid"] for r in tt["references"]["RefIds"]) + 1
                tt["references"]["RefIds"].append({"rid": rid, "type": dict(types[0]["type"]),
                                                   "data": json.loads(json.dumps(tpl))})
                inst["m_SerializedDataOverride"].append({"m_ElementId": eid, "m_ElementIdsPath": [eid],
                                                         "m_SerializedData": {"rid": rid}})
            else:
                data.update(json.loads(json.dumps(voulu)))
            texte = "fond d'origine de FM"
        else:
            if ov is not None and ov0 is None:   # surcharge ajoutée par nous : retirée
                inst["m_SerializedDataOverride"].remove(ov)
                rid = ov["m_SerializedData"]["rid"]
                tt["references"]["RefIds"] = [r for r in tt["references"]["RefIds"] if r["rid"] != rid]
            elif ov is not None:
                data.update(json.loads(json.dumps({k: data0[k] for k in CHAMPS})))
            texte = "surcharge d'origine"
        if json.dumps(tt, sort_keys=True) != avant:
            print(f"{carte} : {texte}")
            obj.save_typetree(tt)
            nb._dirty.add(bundle)


def cible(mode, d, model):
    """les CHAMPS du cadre voulu : "portail" (image fixe) ou "origine" (FM)"""
    if mode == "origine":
        src = originaux().get(model)
    else:
        src = json.loads(json.dumps({k: d[k] for k in CHAMPS}))
        src["ImageKind"] = 0
        src["StaticImage"]["m_AssetGUID"] = GUID_DEFAULT
        src["StaticImage_UxmlAttributeFlags"] = 1
        bd = src["Binding"]
        bd["m_kind"] = 0
        bd["m_direct"]["Path"]["m_path"] = ""
        vf = bd["m_visualFunction"]
        vf["m_target"]["m_guid"] = ""
        vf["m_inputs"]["m_variable"]["m_argumentBytes"] = []
        vf["m_outputs"]["m_variable"]["m_argumentBytes"] = []
        src["Binding_UxmlAttributeFlags"] = 0
    return None if src is None else json.loads(json.dumps({k: src[k] for k in CHAMPS}))


def cadres(mode):
    """mode "portail" : voir PAGES_CLUB ; tout autre réglage = "origine" (cadres de FM)"""
    mode_pages = mode if mode == "portail" else "origine"
    for model in SITES:
        mode = "origine" if model in HORS_THEME else mode_pages
        texte = {"portail": "image fixe du portail", "origine": "fond d'origine de FM"}[mode]
        bundle, obj, tt = nb.find_vta(model)
        d = card_frame(tt) if tt is not None else None
        if d is None:
            print(f"{model} : cadre introuvable (le jeu a changé ?), ignoré")
            continue
        voulu = cible(mode, d, model)
        if voulu is None:
            print(f"{model} : original introuvable, laissé tel quel")
            continue
        if json.dumps({k: d[k] for k in CHAMPS}, sort_keys=True) == json.dumps(voulu, sort_keys=True):
            continue
        d.update(voulu)
        print(f"{model} : {texte}")
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    cartes_match(mode_pages)
    nb.save_all()


# fond des infobulles : règle USS ".sitooltip" (background-color = var(--layout-surfaces-modules-modal)),
# présente dans deux feuilles de style (SIStyles, AlwaysAppliedStyleSheet)
STYLES = [os.path.join(AA, "ui-styles_assets_common.bundle"), os.path.join(AA, "ui-styles_assets_default.bundle")]
INFOBULLE_CLASSE = "sitooltip"
FOND_ID = 458752   # StylePropertyId background-color


def infobulles(rgb):
    """rgb = couleur du fond des infobulles, None = celle de FM. Les 2 bundles de styles portent aussi les couleurs de
    couleurs_interface (accent, texte de la barre) : un seul endroit les réécrit tous les deux depuis l'original."""
    import couleurs_interface
    couleurs_interface.ecrire_styles(rgb)


def peindre(tex, rgb):
    """textures du fond {nom: Texture2D} (lues dans l'original) peintes dans la couleur rgb ; appelé par
    fonds_jeu.ecrire(), seul écrivain du bundle des fonds (partagé avec le stade générique de club_page_bas)"""
    if CIBLE not in tex or SOURCE not in tex:
        sys.exit("images de fond introuvables (le jeu a changé ?)")
    t = tex[CIBLE]
    if lisse():   # couleur unie : petite image non compressée (DXT1 décalait la couleur : #17181B -> 16,24,24)
        # RGBA32 : seul format non compressé du moteur Rust de l'app (RGB24 refusé)
        t.set_image(Image.new("RGBA", (64, 36), tuple(rgb) + (255,)), target_format=TextureFormat.RGBA32,
                    mipmap_count=1)
    else:
        t.set_image(fond(tex[SOURCE].image, rgb).convert("RGB"), target_format=TextureFormat.DXT1, mipmap_count=1)
    t.save()
    if PAGES_CLUB in ("noir", "transparent"):   # image des pages de club, que FM recolore aux couleurs du club
        b = tex[SOURCE]
        alpha = 0 if PAGES_CLUB == "transparent" else 255
        b.set_image(Image.new("RGBA", (64, 36), (0, 0, 0, alpha)), target_format=TextureFormat.RGBA32, mipmap_count=1)
        b.save()
        print("pages de club :", PAGES_CLUB)
    elif PAGES_CLUB == "mire":
        im = Image.new("RGBA", (256, 36))
        for i, c in enumerate(MIRE):
            im.paste(c + (255,), (i * 32, 0, i * 32 + 32, 36))
        b = tex[SOURCE]
        b.set_image(im, target_format=TextureFormat.RGBA32, mipmap_count=1)
        b.save()
        print("pages de club : mire de test")


def cmd_appliquer():
    import fonds_jeu
    cadres(PAGES_CLUB)
    infobulles(colour2())
    print(f"fond : {label()}" + (" (lisse)" if lisse() else ""))
    # repart toujours de l'original : réappliquer avec une autre couleur ne cumule pas
    fonds_jeu.ecrire(theme=colour(), a_blanc=DRY_RUN)
    if DRY_RUN:
        return
    plat = lisse()   # lu avant de réécrire le marqueur
    with open(MARKER, "w", encoding="utf-8") as f:   # la couleur choisie, pour la réappliquer après une MAJ
        json.dump({"actif": True, "couleur": "#%02X%02X%02X" % colour(), "nom": CHOIX or COULEUR,
                   "infobulle": CHOIX2,   # None = gris foncé par défaut (suit INFOBULLE_DEFAUT)
                   "lisse": plat}, f)


def marker():
    try:
        return json.load(open(MARKER, encoding="utf-8"))
    except Exception:
        return {}


def cmd_retirer():
    if os.path.exists(MARKER):
        os.remove(MARKER)
    cadres("origine")
    infobulles(None)
    import fonds_jeu   # fond d'origine ; le stade générique de la page club reste s'il est actif
    fonds_jeu.ecrire(theme=None)


def cmd_etat():
    print("fond :", "modifié" if os.path.exists(backup.backup_path(BUNDLE) + ".written.sha256") else "d'origine (violet)")
    m = marker()
    if m.get("couleur"):
        print("couleur appliquée :", m.get("nom", ""), m["couleur"])
        print("infobulles :", m.get("infobulle") or f"gris foncé par défaut {INFOBULLE_DEFAUT}")
        print("fond lisse :", "oui" if m.get("lisse") else "non (dessin de FM)")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if m else "non")
    print(liste())


def main(argv):
    global CHOIX, CHOIX2, LISSE
    if "--lisse" in argv or "--motifs" in argv:
        LISSE = "--lisse" in argv
    argv = [a for a in argv if a not in ("--dry-run", "--lisse", "--motifs")]
    op = argv[0] if argv else ""
    if len(argv) > 1 and argv[1].strip():
        CHOIX = argv[1].strip()
    if len(argv) > 2 and argv[2].strip():
        CHOIX2 = argv[2].strip()
    if op == "appliquer":
        cmd_appliquer()
    elif op == "liste":
        print(liste())
    elif op == "apercu":
        cmd_apercu()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            CHOIX = marker().get("couleur") or CHOIX   # la dernière couleur choisie
            CHOIX2 = marker().get("infobulle") or CHOIX2
            cmd_appliquer()
        else:
            print("thème du fond : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    # fonds_jeu fait « import theme_fond » : sans ça, 2e copie du module avec LISSE vide -> relit l'ancien marqueur
    # (thème lisse posé par-dessus un fond dessiné = resté dessiné, 2026-11-11)
    sys.modules.setdefault("theme_fond", sys.modules[__name__])
    main(sys.argv[1:])
