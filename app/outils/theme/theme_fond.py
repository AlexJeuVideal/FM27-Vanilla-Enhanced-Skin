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
import colorsys
import json
import os
import sys

import UnityPy
from PIL import Image, ImageChops, ImageOps
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
         "GameWorldBackground",
         # 2026-11-15 (le joueur + un utilisateur de l'app : Recrutement / Club aux couleurs de l'équipe) : ces écrans
         # ont LEUR cadre (Card-frame, fonction visuelle 3c361014… = couleurs du club, comme FigmaBaseSite*)
         "RecruitmentScreen", "ClubScreen", "NationalPoolScreen", "NationScreen")
# toujours le fond de FM, quelle que soit la couleur choisie (demande du joueur 2026-11-10 : conférences de presse =
# image du stade / du club de FM). Restent dans SITES pour être remis d'origine sur un jeu déjà modifié.
# 2026-11-14 (le joueur : « interview bord du terrain / presse ou autre : un fond uni, faut pas ») : GameWorldBackground
# = fond général ; FM y montre game.BackgroundImage (sièges des interviews…) ou la 3D (Use3DBackground) ; notre image
# fixe cachait les sièges -> cadre de FM. PAS VU : vérifier aussi que les pages gardent le fond du thème.
# 2026-11-14 (capture du joueur, FM sans skin) : Préférences ouvertes du menu principal = menu + vestiaire 3D visibles
# derrière ; chez nous fond uni plein : le cadre plein écran FigmaFullscreenBlockTemplate recevait notre image FIXE
# (toujours opaque) ; FM y lit game.BackgroundImage (rien au menu principal = transparent ; en partie = fond des pages,
# déjà repeint) -> cadre de FM
# FigmaFullscreenBlockTemplate RETIRÉ (le même jour) : fausse piste (Préférences = règle report-container de
# couleurs_interface) et c'est le cadre des pages Effectif / Recrutement / Club -> elles prenaient les couleurs du club
HORS_THEME = ("PressConferenceDynamicCard", "PressConferenceSingleQuestionDynamicCard", "GameWorldBackground")
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


# Overview du portail (PortalScreen) : pas de cadre à lui, on y voit le fond général GameWorldBackground (laissé à FM
# pour les sièges des interviews / la presse) -> FM y montrait son fond officiel (ex. Premier League). Retour v1.95
# (2026-11-14), le joueur : la couleur choisie sur l'Overview, PAS sur la presse. En mode "portail", #Overview est
# enveloppé dans un SIImage (copie du background_image de GameWorldBackground) qui affiche notre image fixe.
# v2 (2026-11-14, vu en jeu) : l'enveloppe v1 ne prenait pas la largeur (SIImage = sa propre taille) : tout le portail
# écrasé dans une bande de ~10 px à gauche. Désormais l'image est une SŒUR posée juste AVANT #Overview, en position
# absolue sur toute la surface (left / top / right / bottom 0) : #Overview et la mise en page de FM ne bougent plus.
ECRAN_PORTAIL = "PortalScreen"
CLASSE_PORTAIL = "uipicker-fond-portail-v2"
FOND_GENERAL = "GameWorldBackground"


def _arbre():
    import arbre
    return arbre


def backup_original_feuille(bundle, obj):
    """feuille de style intégrée d'ORIGINE du modèle obj (sauvegarde), None si introuvable"""
    import hierarchie_pyramide as hp
    orig = hp.original(bundle, obj)
    return orig and hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])


def fond_portail(mode):
    arbre = _arbre()
    bundle, obj, tt = nb.find_vta(ECRAN_PORTAIL)
    if tt is None:
        print(f"{ECRAN_PORTAIL} : introuvable (le jeu a changé ?), ignoré")
        return
    t = arbre.Tree(tt)
    avant = json.dumps(tt, sort_keys=True)
    if mode == "portail":   # déjà en place (version actuelle, image fixe) : rien à faire
        deja = [r for r in t.walk() if CLASSE_PORTAIL in (t.elem(r).get("m_Classes") or [])]
        if len(deja) == 1 and t.sd(deja[0]).get("StaticImage", {}).get("m_AssetGUID") == GUID_DEFAULT:
            return
    # retire nos enveloppes (toute version) : leurs enfants reprennent leur place
    for r in [r for r in t.walk() if any(c.startswith("uipicker-fond-portail-") for c in t.elem(r).get("m_Classes") or [])]:
        p = t.parent[r]
        kids = t.elem(p)["m_Children"]
        i = next(k for k, c in enumerate(kids) if c["rid"] == r)
        for j, c in enumerate(t.children(r)):
            t.elem(c)["m_Parent"] = {"rid": p}
            t.parent[c] = p
            kids.insert(i + 1 + j, {"rid": c})
        t.elem(r)["m_Children"] = []
        t.remove(r)
    st = arbre.Styles(bundle, tt)
    if mode == "portail":
        ov = [r for r in t.walk() if t.name(r) == "Overview"]
        _, _, tg = nb.find_vta(FOND_GENERAL)
        src = arbre.Tree(tg) if tg is not None else None
        img = [r for r in src.walk() if src.name(r) == "background_image"] if src else []
        if len(ov) != 1 or not img:
            print(f"{ECRAN_PORTAIL} : #Overview ou image de fond introuvable (le jeu a changé ?), ignoré")
        else:
            ov = ov[0]
            p = t.parent[ov]
            kids = t.elem(p)["m_Children"]
            i = next(k for k, c in enumerate(kids) if c["rid"] == ov)
            fond = t.clone(img[0], p, i, src=src)   # juste avant #Overview : dessiné derrière lui
            for k in list(t.children(fond)):
                t.remove(k)
            e = t.elem(fond)
            e["m_RuleIndex"] = -1
            e["m_Classes"] = ["siimage", CLASSE_PORTAIL]
            d = t.sd(fond)
            d["name"] = "uipicker_fond_portail"
            d.update(cible("portail", d, FOND_GENERAL))
            for nom_css, pid_type in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3),
                                      "right": (131103, 3), "bottom": (131080, 3)}.items():
                arbre.PROPRIETES.setdefault(nom_css, pid_type)
            st.style(t, fond, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
    else:   # plus rien de nous : la feuille de style d'origine si aucune règle ajoutée n'est utilisée
        orig = backup_original_feuille(bundle, obj)
        if orig is not None and all(t.elem(r).get("m_RuleIndex", -1) < len(orig["m_Rules"]) for r in t.walk()) \
                and st.sh != orig:
            st.sh, st.changed = orig, True
    t.finish()
    st.save()
    if json.dumps(tt, sort_keys=True) != avant or st.changed:
        print(f"{ECRAN_PORTAIL} : " + ("fond de la couleur choisie" if mode == "portail" else "fond de FM"))
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt   # relu tel quel par find_vta dans le même passage
        nb._dirty.add(bundle)


# ESSAI vide (2026-11-14, le joueur : « je veux du vide derrière les Préférences, pas une couleur unie ») : image du
# fond général GameWorldBackground à opacité 0, pour voir ce qu'il y a dessous (l'écran du jeu ou du noir). Commande
# essai-vide ; tout appliquer normal (cadres) l'enlève (feuille de style d'origine du modèle remise)
ESSAI_VIDE_CLASSE = "uipicker-essai-vide-v1"


def essai_vide(actif):
    arbre = _arbre()
    bundle, obj, tt = nb.find_vta(FOND_GENERAL)
    if tt is None:
        print(f"{FOND_GENERAL} : introuvable, essai ignoré")
        return
    t = arbre.Tree(tt)
    st = arbre.Styles(bundle, tt)
    avant = json.dumps(tt, sort_keys=True)
    img = [r for r in t.walk() if t.name(r) == "background_image"]
    if actif and img:
        arbre.PROPRIETES.setdefault("opacity", (458767, 2))
        e = t.elem(img[0])
        if ESSAI_VIDE_CLASSE not in (e.get("m_Classes") or []):
            e["m_Classes"] = list(e.get("m_Classes") or []) + [ESSAI_VIDE_CLASSE]
        st.style(t, img[0], {"opacity": 0})
    else:
        for r in t.walk():
            e = t.elem(r)
            if ESSAI_VIDE_CLASSE in (e.get("m_Classes") or []):
                e["m_Classes"] = [c for c in e["m_Classes"] if c != ESSAI_VIDE_CLASSE]
                orig = backup_original_feuille(bundle, obj)
                if orig is not None:
                    st.sh, st.changed = orig, True
                    e["m_RuleIndex"] = -1
    t.finish()
    st.save()
    if json.dumps(tt, sort_keys=True) != avant or st.changed:
        print(f"{FOND_GENERAL} : " + ("ESSAI vide (image invisible)" if actif else "essai vide retiré"))
        obj.save_typetree(tt)
        nb._ecrits[(bundle, obj.path_id)] = tt
        nb._dirty.add(bundle)


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
    fond_portail(mode_pages)
    essai_vide(False)   # retire l'essai vide s'il est posé
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


# fonds plein écran en plus des « *skin* » (le joueur, 2026-11-14 : « tous les fonds in game du portail = couleur du
# skin ») : fond générique de FM27 (bundle des fonds) et, dans ui-backgrounds_assets_common, fond sombre à motif et fond
# des tournois internationaux. Les scènes en ovale (vestiaires, presse, et leurs versions Premier League / UEFA…) :
# jamais (règle du joueur : images propres à un écran).
# fm27-background-texture (trait pointillé en bas) retirée (le joueur, 2026-11-14) : image des chargements / derrière
# les Préférences, doit rester celle de FM
FONDS_EN_PLUS = ("dynamic-pattern-dark-texture", "international-tournament-default")
_COMPET = []   # [image, format] posés par peindre() (mode couleur), repris pour ui-backgrounds_assets_common


def peindre_competitions(tex, exclus=()):
    """fonds de compétition / fonds plein écran de {nom: Texture2D} = image de peindre() ; renvoie le nombre"""
    if not _COMPET:
        return 0
    im, fmt = _COMPET
    n = 0
    for nom, tc in tex.items():
        if ("skin" in nom.lower() or nom in FONDS_EN_PLUS) and nom not in exclus:
            tc.set_image(im, target_format=fmt, mipmap_count=1)
            tc.save()
            n += 1
    return n


# image des chargements (et derrière les Préférences en partie) : fond sombre + pointillé lumineux. Le joueur
# (2026-11-14) : « dans la couleur du skin, pas trop forte », « juste elle » ; v2 (le même soir) : « les bandes à la
# couleur accent, le reste à la couleur principale, pour chaque thème ». Masque de luminosité : sous CHARGEMENT_SEUIL =
# couleur du fond telle quelle ; au-dessus, vers l'accent (bandes + halo). Accent = clé « accent » de couleurs_interface
# (son marqueur) ; sans accent : même teinte que le fond, plus claire (CHARGEMENT_S / _V).
CHARGEMENT = "fm27-background-texture"
CHARGEMENT_S, CHARGEMENT_V = 0.55, 0.72
CHARGEMENT_SEUIL, CHARGEMENT_PLEIN = 50, 140   # luminosité (après étirement) : début du halo, bande pleine


def accent_choisi():
    """(r, g, b) de l'accent de couleurs_interface (marqueur), ou None"""
    try:
        with open(os.path.join(backup.BACKUP_DIR, "couleurs_interface.actif"), encoding="utf-8") as f:
            c = json.load(f).get("accent")
        return to_rgb(c) if c and c.lower() != "fm" else None
    except (Exception, SystemExit):   # to_rgb sort par sys.exit sur une couleur pas comprise
        return None


def chargement(tex, rgb):
    t = tex.get(CHARGEMENT)
    if t is None:
        print(f"{CHARGEMENT} : introuvable (le jeu a changé ?), image des chargements laissée")
        return
    acc = accent_choisi()
    if acc is None:
        h = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))[0]
        acc = tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, CHARGEMENT_S, CHARGEMENT_V))
    lum = ImageOps.autocontrast(t.image.convert("L").resize((1920, 1080), Image.LANCZOS), cutoff=0.2)
    masque = lum.point(lambda v: 0 if v < CHARGEMENT_SEUIL
                       else min(255, round((v - CHARGEMENT_SEUIL) * 255 / (CHARGEMENT_PLEIN - CHARGEMENT_SEUIL))))
    im = Image.composite(Image.new("RGB", lum.size, tuple(acc)), Image.new("RGB", lum.size, tuple(rgb)), masque)
    t.set_image(im, target_format=TextureFormat.DXT1, mipmap_count=1)
    t.save()
    print("image des chargements : fond " + "#%02X%02X%02X" % tuple(rgb) + ", bandes " + "#%02X%02X%02X" % tuple(acc))


def peindre(tex, rgb):
    """textures du fond {nom: Texture2D} (lues dans l'original) peintes dans la couleur rgb ; appelé par
    fonds_jeu.ecrire(), seul écrivain du bundle des fonds (partagé avec le stade générique de club_page_bas)"""
    if CIBLE not in tex or SOURCE not in tex:
        sys.exit("images de fond introuvables (le jeu a changé ?)")
    _COMPET[:] = []
    t = tex[CIBLE]
    if lisse():   # couleur unie : petite image non compressée (DXT1 décalait la couleur : #17181B -> 16,24,24)
        # RGBA32 : seul format non compressé du moteur Rust de l'app (RGB24 refusé)
        im, fmt = Image.new("RGBA", (64, 36), tuple(rgb) + (255,)), TextureFormat.RGBA32
    else:
        im, fmt = fond(tex[SOURCE].image, rgb).convert("RGB"), TextureFormat.DXT1
    t.set_image(im, target_format=fmt, mipmap_count=1)
    t.save()
    chargement(tex, rgb)
    # v2026-11-14 (retour Discord : « problème sur les compétitions sous licence, FA Cup OK ») : FM remplit
    # game.BackgroundImage avec le fond de la compétition quand elle en a un (fm27_skin_epl, _bundesliga, _uefa-ucl…,
    # même bundle) -> portail / pages sur ce fond officiel. Mode couleur : toutes ces images = notre fond.
    # Pas fm27_skin_blended (pages de club, SOURCE) ni la texture du stade générique (club_page_bas).
    if PAGES_CLUB == "portail":
        if fmt == TextureFormat.DXT1:   # 32 images en 4096 px = +150 Mo : 1920 px suffisent (fond flou, plein écran)
            im = im.resize((1920, 1080), Image.LANCZOS)
        _COMPET[:] = [im, fmt]
        n = peindre_competitions(tex, exclus=(CIBLE, SOURCE, "caraboa-cup-skin-test-min"))
        print(f"fonds des compétitions sous licence : {n} à la couleur du fond")
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
    # --dry-run respecté (2026-11-14 : il manquait, un « retirer --dry-run » a réécrit le fond du vrai jeu)
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    cadres("origine")
    infobulles(None)
    import fonds_jeu   # fond d'origine ; le stade générique de la page club reste s'il est actif
    fonds_jeu.ecrire(theme=None, a_blanc=DRY_RUN)


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
    elif op == "essai-vide":   # ESSAI : image du fond général invisible (marqueur pas touché ; appliquer l'enlève)
        essai_vide(True)
        nb.save_all()
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
