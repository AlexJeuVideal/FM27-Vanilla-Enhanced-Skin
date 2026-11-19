"""Maillot de dos de l'en-tête (fiche du skin de base, style gomez) : découpe de maillot_dos.png en rectangles.

Le PNG (fourni par le joueur, 2026-11-19) : rouge = 1re couleur du kit, vert = 2e couleur (col, bouts de manches).
decoupe(h) -> (largeur, [(couleur "1" / "2", opacité, [rect…]), …], [(voile rgba, [rect…]), …]) ; rect = (x, y, l, h).
gom47 (le joueur : « pourquoi c'est pixelisé, ma version était niquel ») : lignes de 1 px (forme exacte) + bords
anti-crénelés (pixels du bord en couleur du kit à 2/3 et 1/3 d'opacité, d'après l'alpha du PNG) ; ombres du PNG
(lissées, 2 niveaux) en voiles noirs par-dessus.
"""
import os

from PIL import Image, ImageFilter

PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maillot_dos.png")
FLOU = 1.5
PAS = 1   # gom45 : 3 ; gom46 : 2 ; gom47 : 1 (pixelisé sinon)
# (bas, haut, voile) : rapport luminosité / ton plein de la zone couleur 1
NIVEAUX = [(0.0, 0.72, (0.0, 0.0, 0.0, 0.30)), (0.72, 0.90, (0.0, 0.0, 0.0, 0.14))]
# alpha du PNG (0-255) -> opacité de la couleur du kit : plein, bord 2/3, bord 1/3 (sous ALPHA_MIN : rien)
# gom52 (le joueur : « un poil de rouge en haut ») : le niveau 1/3 (jaune sur fond sombre = brun-rouge aux épaules) retiré
BORDS = [(200, 1.0), (110, 0.66)]
_cache = {}


def _rects(pts, w, h, pas=1):
    """runs par bande de pas lignes (ligne du milieu de la bande), fusionnés verticalement quand identiques"""
    out, ouverts = [], {}
    for y in list(range(0, h, pas)) + [h]:
        runs, x = [], 0
        ym = min(h - 1, y + pas // 2)
        while y < h and x < w:
            if (x, ym) in pts:
                x0 = x
                while x < w and (x, ym) in pts:
                    x += 1
                runs.append((x0, x))
            else:
                x += 1
        nouveaux = {}
        for run in runs:
            nouveaux[run] = ouverts.pop(run, y)
        for (x0, x1), y0 in ouverts.items():
            out.append((x0, y0, x1 - x0, min(y, h) - y0))
        ouverts = nouveaux
    return out


def decoupe(h):
    if h in _cache:
        return _cache[h]
    im = Image.open(PNG).convert("RGBA")
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    px = im.load()
    val = Image.new("L", (w, h))
    vp = val.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            vp[x, y] = max(r, g, b) if a >= 128 else 0
    vp = val.filter(ImageFilter.GaussianBlur(FLOU)).load()
    zones = {(k, op): set() for k in "12" for _, op in BORDS}
    valeurs = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            niveau = next((op for seuil, op in BORDS if a >= seuil), None)
            if niveau is None:
                continue
            k = "2" if g > r else "1"
            zones[k, niveau].add((x, y))
            if k == "1" and niveau == 1.0:
                valeurs.append(((x, y), vp[x, y]))
    tri = sorted(v for _, v in valeurs)
    plein = tri[len(tri) * 3 // 4] or 1
    voiles = []
    for bas, haut, couleur in NIVEAUX:
        pts = {p for p, v in valeurs if bas <= v / plein < haut}
        voiles.append((couleur, _rects(pts, w, h, PAS)))
    _cache[h] = (w, [(k, op, _rects(p, w, h, PAS)) for (k, op), p in zones.items() if p], voiles)
    return _cache[h]
