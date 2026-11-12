"""ESSAI : carte de la connaissance du monde (Recrutement > Connaissance du monde), 1re étape (2026-11-10).

But final : une carte du monde à droite du tableau des pays, chaque pays connu coloré selon son niveau. FM n'affiche
une image perso que par un NUMÉRO (chargeur d'images 7a35874b, type Continent : graphics/pictures/continent/<id>/logo,
comme les trophées). Les ids des pays tombent sur des ids de compétitions (Cameroun 11 = Premier League...) : la
carte effacerait ces trophées. Piste : l'id de la sélection FÉMININE du pays (France 2000169625, ids 2000169482 à
2000169731 dans lang_db, aucun ne tombe sur une compétition).

Essai (tableau des pays seulement, cellule WorldKnowledgeNationCell, FR seul) : sur la 2e ligne de chaque pays,
après la région :
- une pastille (image de test ronde blanche, teinte VERTE par le tintColor du SIImage) chargée par
  Nation.MainWomanTeamContainer.ObjectLookupData en type Continent ;
- le numéro lu par FM : Nation.MainWomanTeamContainer.UniqueId.
graphics : dossier « UIPicker Essai Carte » (essai_carte.png + config.xml vers continent/<id>/logo pour les ids
2000169470 à 2000169750).
Réussi = pastille VERTE à côté de chaque pays + numéro ~2000169xxx (rond blanc = la teinte ne marche pas ; rien =
le chargeur ne prend pas ce chemin ; pas de numéro = FM ne donne pas la sélection féminine ici).
v1 en jeu (2026-11-10) : numéro OK, pas de pastille (les 3 chemins de couleur du chargeur étaient vides) -> v2 : chemins
de couleur de la sélection, 2 pastilles (verte = teinte, blanche = sans teinte).
v2 en jeu : place prise, rien d'affiché -> v3 : 4 pastilles (VARIANTES : sélection, son équipe, 2 témoins), sans numéro.

Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_carte_monde.py appliquer [--dry-run] | retirer [--dry-run]
"""
import gzip
import os
import shutil
import struct
import sys
import zlib

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import arbre as sm  # noqa: E402
import stades_photos  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint, text_direct  # noqa: E402

MODELE = "WorldKnowledgeNationCell"
SOURCE = "CompetitionLogo"           # son SIImage : chargeur d'images, comp.ObjectLookupData
VERSION = 3   # v1 en jeu : numéro OK (Maroc 2000169547, Japon 2000169494), pas de pastille (chemins de couleur vides)
              # v2 en jeu : place prise, images vides -> v3 : plusieurs chemins + témoins, plus de numéro
PREFIXE = "UIPickerEssaiCarte"
NOM_IMAGE = f"{PREFIXE}Image-v{VERSION}"
TYPE_IMAGE = 11                      # Continent
TEINTE = {"r": 0.25, "g": 0.85, "b": 0.35, "a": 1.0}
# (préfixe des chemins du chargeur, type d'image, teinte) : pastilles de gauche à droite
# v3 en jeu (2026-11-10) : 1-2 (sélection féminine, son équipe) = RIEN ; 3 = trophée (Maroc, Japon : id = compétition)
# ou CARRÉ BLANC (image absente : FM cherche bien continent/<id du pays>/logo) ; 4 = logo du pays
VARIANTES = [
    ("Nation.MainWomanTeamContainer.", 11, TEINTE),            # 1 sélection féminine (comme v2)
    ("Nation.MainWomanTeamContainer.MainTeam.", 11, TEINTE),   # 2 son équipe première
    ("Nation.", 11, None),     # 3 témoin : id du PAYS en Continent -> trophée / vide de la compétition du même id
    ("Nation.", 3, None),      # 4 témoin : chargeur normal d'un pays (logo du pays)
]
TAILLE = 18
IDS = range(2000169470, 2000169751)  # sélections féminines (lang_db FM27 : 2000169482 à 2000169731)
DOSSIER = "UIPicker Essai Carte"
FICHIER = "essai_carte"
CIBLE = "graphics/pictures/continent/{id}/logo"
for k, v in {"width": (131105, 3), "height": (131087, 3), "margin-left": (131091, 3),
             "flex-direction": (131083, 7), "align-items": (131073, 7)}.items():
    sm.PROPRIETES.setdefault(k, v)


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


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def poser(t, sh):
    _, _, stt = nb.find_vta(SOURCE)
    if stt is None:
        return [f"{SOURCE} introuvable"]
    s = Tree(stt)
    img = next((r for r in s.walk() if typ(s, r) == "SIImage"
                and any(b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in _arguments(s.sd(r)))), None)
    region = next((r for r in t.walk() if t.name(r) == "text" and typ(t, r) == "SIText"
                   and "DisplayRegion" in (t.sd(r)["TextBinding"]["m_direct"]["Path"]["m_path"] or "")), None)
    if img is None or region is None:
        return [f"{SOURCE} : image introuvable" if img is None else f"{MODELE} : texte de la région introuvable"]
    ligne = t.parent[region]
    sh.style(t, ligne, {"flex-direction": "row", "align-items": "center"})
    for k, (prefixe, type_image, teinte) in enumerate(VARIANTES, 1):
        nom = f"{NOM_IMAGE}-{k}"
        r = t.clone(img, ligne, None, src=s)
        for k in list(t.children(r)):
            t.remove(k)
        t.elem(r)["m_RuleIndex"] = -1
        t.elem(r)["m_Classes"] = []
        t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
        if teinte:
            t.sd(r)["tintColor"] = dict(teinte)
        for x in _arguments(t.sd(r)):
            args = decode_args(x["m_argumentBytes"])
            for a in args:
                if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                    a[1] = type_image.to_bytes(4, "little")
                elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                    ch = a[1][2:].decode()
                    if ch.startswith("comp."):
                        ch = prefixe + ch[len("comp."):]
                        a[1] = b"\x01" + _enc_varint(len(ch)) + ch.encode()
            x["m_argumentBytes"] = encode_args(args)
        sh.style(t, r, {"width": TAILLE, "height": TAILLE, "min-width": TAILLE, "flex-shrink": 0, "margin-left": 4})
    return [f"{len(VARIANTES)} pastilles : " + " | ".join(f"{p}* type {ty}" for p, ty, _ in VARIANTES)]


def retirer(t):
    old = [r for r in t.walk() if (t.name(r) or "").startswith(PREFIXE)]
    for r in old:
        t.remove(r)
    return ["essai retiré"] if old else []


# ---------- graphics ----------
def _png_rond(taille=64):
    """PNG : rond blanc plein sur fond transparent (bibliothèque standard)"""
    c = (taille - 1) / 2
    lignes = b""
    for y in range(taille):
        lignes += b"\x00" + b"".join(b"\xff\xff\xff\xff" if (x - c) ** 2 + (y - c) ** 2 <= c * c else b"\x00\x00\x00\x00"
                                     for x in range(taille))

    def bloc(k, d):
        return struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", taille, taille, 8, 6, 0, 0, 0))
            + bloc(b"IDAT", zlib.compress(lignes)) + bloc(b"IEND", b""))


def dossier():
    return os.path.join(stades_photos.graphics(), DOSSIER)


def _competitions():
    with gzip.open(os.path.join(os.path.dirname(ICI), "commun", "competitions.txt.gz"), "rt", encoding="utf-8") as h:
        return {int(x.split("\t")[0]) for x in h if x.split("\t")[0].strip().isdigit()}


def poser_graphics(a_blanc):
    g = stades_photos.graphics()
    if not os.path.isdir(g):
        print(f"graphics : {g} absent, rien posé")
        return
    comps = _competitions()
    ids = [i for i in IDS if i not in comps]
    lignes = "\n".join(f'\t\t<record from="{FICHIER}" to="{CIBLE.format(id=i)}"/>' for i in ids)
    xml = ("<record>\n\t<boolean id=\"preload\" value=\"false\"/>\n\t<boolean id=\"amap\" value=\"false\"/>\n"
           "\t<!-- ESSAI carte du monde (FM27 Vanilla Enhanced Skin), retiré par le choix 105 -->\n"
           f"\t<list id=\"maps\">\n{lignes}\n\t</list>\n</record>\n")
    d = dossier()
    if not a_blanc:
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, FICHIER + ".png"), "wb") as h:
            h.write(_png_rond())
        with open(os.path.join(d, "config.xml"), "w", encoding="utf-8") as h:
            h.write(xml)
    print(f"graphics : {d} ({len(ids)} numéros)" + (" [à blanc : rien écrit]" if a_blanc else ""))


def retirer_graphics(a_blanc):
    d = dossier()
    if os.path.isdir(d):
        if not a_blanc:
            shutil.rmtree(d)
        print(f"graphics : {d} supprimé" + (" [à blanc]" if a_blanc else ""))


def main(argv):
    a_blanc = "--dry-run" in argv
    if a_blanc:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    cmd = argv[0] if argv else ""
    if cmd not in ("appliquer", "retirer"):
        sys.exit(__doc__)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        sys.exit(f"{MODELE} introuvable")
    t, sh = Tree(tt), Styles(bundle, tt)
    deja = any(t.name(r) == f"{NOM_IMAGE}-1" for r in t.walk())
    if cmd == "appliquer" and deja:
        print(f"{MODELE} : déjà appliqué")
        poser_graphics(a_blanc)
        return
    msgs = retirer(t)
    if cmd == "appliquer":
        msgs = poser(t, sh)
    print(f"{MODELE} : " + (", ".join(msgs) or "rien à faire"))
    if msgs and "introuvable" not in msgs[0]:
        t.finish()
        sh.changed = True
        sh.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()
    if cmd == "appliquer":
        poser_graphics(a_blanc)
    else:
        retirer_graphics(a_blanc)


if __name__ == "__main__":
    main(sys.argv[1:])
