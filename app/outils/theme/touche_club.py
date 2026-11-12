"""Touche de couleur du club sur une barre du haut unie (2026-11-11, demande du joueur, ESSAI) : partie du logo (à
gauche), fondue vers la droite. Appelé par couleurs_interface (seul écrivain de PrimaryNavigationBarGradient), clés
« touche » (style), « touche_long » (longueur, % de la barre) et « touche_force » (opacité de départ, %).

Couches = copies du SIGradient de FM de la barre (fonction 9f612110 : chemin d'une couleur du club + opacité de début
et de fin, ex. NewsDynamicBackground 0,6 -> 0) : couleur du club SANS crash (technique.md § Pièges), posées dans
l'élément devenu un aplat (couleurs_interface.en_fond_fixe), en position absolue, clics ignorés.
GradientDirection (enum SIGradient, lu dans global-metadata) : 0 TopToBottom, 1 LeftToRight, 2-5 EndColour<coin>
(BottomLeft, TopLeft, TopRight, BottomRight : le coin prend la couleur de fin), 13 RightToLeft. Valeurs des coins
supposées dans l'ordre de l'enum : PAS vu en jeu.
Styles : net (aplat près du logo puis fondu), doux (fondu dès le logo), halo (4 quarts autour du logo, coins), liseret
(fine ligne en bas), deux (couleur principale puis secondaire).
"""
import copy
import os
import struct
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401
import arbre as sm  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

STYLES = ("net", "doux", "halo", "liseret", "deux")
LONG_BASE, FORCE_BASE = 30, 45   # % (comme les maquettes validées par le joueur)
LONG_MIN, LONG_MAX = 10, 90
FORCE_MIN, FORCE_MAX = 10, 90
HALO_CENTRE = 30                 # px : milieu du logo depuis le bord gauche de la barre (estimé, PAS mesuré en jeu)
LISERET_HAUTEUR = 3              # px
HAUT_BAS, GAUCHE_DROITE = 0, 1
COIN_BAS_GAUCHE, COIN_HAUT_GAUCHE, COIN_HAUT_DROITE, COIN_BAS_DROITE = 2, 3, 4, 5
PRINCIPALE, SECONDAIRE = "TitlebarBackgroundColour", "SecondaryColor"
PREFIXE = "UIPickerTouche"
IGNORE = 1
for k, v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "bottom": (131080, 3),
             "width": (131105, 3), "height": (131087, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)


def pc(v):
    return {"unit": 2, "value": float(v)}


def borne(v, base, lo, hi):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return base


def couches(style, long_, force):
    """[(gauche, largeur, haut, hauteur, alpha début, alpha fin, direction, couleur)] ; positions = px (nombre) ou
    % (pc(...)) ; haut / hauteur None = toute la hauteur ; « bas » = collée en bas"""
    f = force / 100
    L = long_
    if style == "net":
        return [(0, pc(L * .25), None, None, f, f, GAUCHE_DROITE, PRINCIPALE),
                (pc(L * .25), pc(L * .75), None, None, f, 0, GAUCHE_DROITE, PRINCIPALE)]
    if style == "doux":
        return [(0, pc(L), None, None, f * .85, 0, GAUCHE_DROITE, PRINCIPALE)]
    if style == "liseret":
        return [(0, pc(L), "bas", LISERET_HAUTEUR, min(1, f * 1.8), 0, GAUCHE_DROITE, PRINCIPALE)]
    if style == "deux":
        m = L * .45
        return [(0, pc(m), None, None, f, 0, GAUCHE_DROITE, PRINCIPALE),
                (0, pc(m), None, None, 0, f * .6, GAUCHE_DROITE, SECONDAIRE),
                (pc(m), pc(L - m), None, None, f * .6, 0, GAUCHE_DROITE, SECONDAIRE)]
    if style == "halo":   # coin le plus près du logo = couleur (fin), les 3 autres transparents (début)
        c = HALO_CENTRE
        return [(0, c, 0, pc(50), 0, f, COIN_BAS_DROITE, PRINCIPALE),
                (0, c, "bas", pc(50), 0, f, COIN_HAUT_DROITE, PRINCIPALE),
                (c, pc(L), 0, pc(50), 0, f, COIN_BAS_GAUCHE, PRINCIPALE),
                (c, pc(L), "bas", pc(50), 0, f, COIN_HAUT_GAUCHE, PRINCIPALE)]
    return []


def _args(f_src, couleur, a0, a1):
    args = decode_args(f_src["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemin = bytes(args[0][1])[1:]
    n = 0   # varint de longueur
    while chemin[n] & 0x80:
        n += 1
    p = chemin[n + 1:].decode()
    p = p.rsplit(".", 1)[0] + "." + couleur
    args[0][1] = b"\x01" + _enc_varint(len(p)) + p.encode()
    args[1][1] = struct.pack("<f", a0)
    args[2][1] = struct.pack("<f", a1)
    return encode_args(args)


def poser(t, styles, r, cfg):
    """couches dans le SIGradient r (encore un dégradé : appeler AVANT en_fond_fixe) ; renvoie un message ou None"""
    style = cfg.get("touche")
    if style not in STYLES:
        return None
    long_ = borne(cfg.get("touche_long"), LONG_BASE, LONG_MIN, LONG_MAX)
    force = borne(cfg.get("touche_force"), FORCE_BASE, FORCE_MIN, FORCE_MAX)
    f_src = t.sd(r).get("BindGradientFunc")
    args = decode_args(f_src["m_inputs"]["m_variable"]["m_argumentBytes"]) if isinstance(f_src, dict) else []
    if len(args) != 3 or not bytes(args[0][1]).endswith(PRINCIPALE.encode()):
        return "touche du club : dégradé de FM pas reconnu (le jeu a changé ?)"
    for i, (x, w, y, h, a0, a1, d, couleur) in enumerate(couches(style, long_, force)):
        c = t.clone_shallow(r, r)
        sd = t.sd(c)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}{i}", 1
        sd["pickingMode"] = IGNORE
        if "pickingMode_UxmlAttributeFlags" in sd:
            sd["pickingMode_UxmlAttributeFlags"] = 1
        sd["GradientDirection"] = d
        f = copy.deepcopy(f_src)
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = _args(f_src, couleur, a0, a1)
        sd["BindGradientFunc"] = f
        e = t.elem(c)
        e["m_Classes"], e["m_RuleIndex"] = [], -1
        css = {"position": "absolute", "left": x, "width": w, "height": pc(100) if h is None else h}
        css["bottom" if y == "bas" else "top"] = 0 if y in (None, "bas") else y
        styles.style(t, c, css)
    return f"touche du club « {style} », {long_} %, force {force} %"
