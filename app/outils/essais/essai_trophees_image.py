"""ESSAI : une image par trophée, ciblée par l'id de la compétition (pour la salle des trophées, 2026-11-09).

FM n'a pas de type d'image « trophée » (GraphicsUtils.ResourceType : 0 Club, 1 Comp, 2 Team, 3 Nation, 4 Person,
5-8 / 13-14 maillots, 9 DBSummaryPerson, 10 NewGen, 11 Continent, 12 Unsupported, 15 Flag) et ignore le texte du
chargeur pour Comp (essai stades v21). Idée, comme les stades : le chargeur d'images de FM (fonction 7a35874b) avec
l'id de la COMPÉTITION mais en type Continent (11) -> graphics/pictures/continent/<id compétition>/logo, chemin
libre (7 continents seulement).

Essai :
- bundle : dans chaque ligne du palmarès (ClubHistoryHonourCardRow : bloc Honneurs de la page club, Club > Histoire),
  une image 48 x 48 avant le nom de la compétition = SIImage de CompetitionLogo recopié, type 11, chemin
  row.Competition.ObjectLookupData ;
- graphics : dossier « UIPicker Essai Trophees » (essai_trophee.png = coupe dorée « TEST ») + config.xml qui l'envoie
  à continent/<id>/logo pour TOUS les ids de compétition (competitions.txt.gz).
Réussi = la coupe « TEST » devant chaque compétition du palmarès : VALIDÉ en jeu le 2026-11-09. Depuis, la coupe
TEST n'est plus posée : les images viennent de FMVE Trophies (commun\\trophees_photos.py, TROPHY<id>.png).

Outils FM.bat : 124 (essais pas validés) ; retrait : 105 (catalogue.ESSAIS).
Usage : essai_trophees_image.py appliquer [--dry-run] | retirer [--dry-run]
"""
import os
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import arbre as sm  # noqa: E402
import stades_photos  # noqa: E402
import trophees_photos  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

MODELE = "ClubHistoryHonourCardRow"
SOURCE = "CompetitionLogo"           # son SIImage : chargeur d'images, comp.ObjectLookupData, type 1
NOM = "UIPickerEssaiTrophee-v1"
TYPE_IMAGE = 11                      # Continent
CHEMIN = "row.Competition."          # remplace « comp. » du modèle source
DOSSIER = "UIPicker Essai Trophees"
IMAGE = os.path.join(ICI, "essai_trophee.png")
NOM_IMAGE = "essai_trophee"
CIBLE = "graphics/pictures/continent/{id}/logo"
TAILLE = 48
for k, v in {"width": (131105, 3), "height": (131087, 3), "margin-right": (131092, 3)}.items():
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


def poser_image(t, sh):
    _, _, stt = nb.find_vta(SOURCE)
    if stt is None:
        return [f"{SOURCE} introuvable"]
    s = Tree(stt)
    img = next((r for r in s.walk() if (s.elem(r).get("m_FullTypeName") or "").endswith("SIImage")
                and any(b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in _arguments(s.sd(r)))), None)
    contenu = next((r for r in t.walk() if t.name(r) == "Content"), None)
    if img is None or contenu is None:
        return [f"{SOURCE} : image introuvable" if img is None else f"{MODELE} #Content introuvable"]
    r = t.clone(img, contenu, 0, src=s)
    for k in list(t.children(r)):
        t.remove(k)
    t.elem(r)["m_RuleIndex"] = -1
    t.elem(r)["m_Classes"] = []
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = NOM, 1
    chemins_vus = []
    for x in _arguments(t.sd(r)):
        args = decode_args(x["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                a[1] = TYPE_IMAGE.to_bytes(4, "little")
            elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                ch = a[1][2:].decode()
                if ch.startswith("comp."):
                    ch = CHEMIN + ch[len("comp."):]
                    a[1] = b"\x01" + _enc_varint(len(ch)) + ch.encode()
                chemins_vus.append(ch)
        x["m_argumentBytes"] = encode_args(args)
    sh.style(t, r, {"width": TAILLE, "height": TAILLE, "margin-right": 8})
    return [f"image type {TYPE_IMAGE} posée ({', '.join(chemins_vus)})"]


def retirer_image(t, sh=None):
    old = [r for r in t.walk() if (t.name(r) or "").startswith("UIPickerEssaiTrophee")]
    for r in old:
        t.remove(r)
    return ["image retirée"] if old else []


def dossier():
    return os.path.join(stades_photos.graphics(), DOSSIER)


def poser_graphics(a_blanc):
    """coupe « TEST » validée en jeu le 2026-11-09 : plus posée (elle visait les mêmes emplacements que FMVE
    Trophies) ; son dossier est retiré et le config.xml des vrais trophées refait (trophees_photos)"""
    retirer_graphics(a_blanc)
    d, n = trophees_photos.ecrire(a_blanc)
    print(f"graphics : {d or trophees_photos.dossier() + ' (absent)'} ({n} trophées)"
          + (" [à blanc : rien écrit]" if a_blanc else ""))


def retirer_graphics(a_blanc):
    d = dossier()
    if os.path.isdir(d):
        if not a_blanc:
            shutil.rmtree(d)
        print(f"graphics : {d} supprimé" + (" [à blanc]" if a_blanc else ""))


def main(argv):
    a_blanc = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    cmd = argv[0] if argv else ""
    if cmd not in ("appliquer", "retirer"):
        sys.exit(__doc__)
    bundle, obj, tt = nb.find_vta(MODELE)
    if tt is None:
        sys.exit(f"{MODELE} introuvable")
    t, sh = Tree(tt), Styles(bundle, tt)
    msgs = retirer_image(t, sh)
    if cmd == "appliquer":
        msgs = poser_image(t, sh)
    print(f"{MODELE} : " + (", ".join(msgs) or "rien à faire"))
    if msgs and "introuvable" not in msgs[0]:
        t.finish()
        sh.changed = True
        sh.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
        nb.save_all()
        (poser_graphics if cmd == "appliquer" else retirer_graphics)(a_blanc)
    elif cmd == "retirer":
        retirer_graphics(a_blanc)


if __name__ == "__main__":
    main(sys.argv[1:])
