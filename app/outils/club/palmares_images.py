"""Palmarès en images : l'image du trophée (pack FMVE Trophies) devant chaque compétition du palmarès (bloc Honneurs de
la page club, Club > Histoire). Essai essai_trophees_image validé en jeu le 2026-11-09.

- ClubHistoryHonourCardRow (ligne du palmarès) : une image 48 x 48 avant le nom = SIImage de CompetitionLogo recopié,
  type Continent (11), chemin row.Competition.ObjectLookupData -> graphics/pictures/continent/<id compétition>/logo
  (images : commun\\trophees_photos.py, comme salle_trophees).
- Seul écrivain du modèle : appliquer repart de l'original, retirer le remet.

Menu Outils FM.bat : 16 (catégorie), puis la fonction ; réappliqué par le choix 1.
Usage : palmares_images.py appliquer | retirer | etat | si-actif [--dry-run]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402
import salle_trophees as st  # noqa: E402

TAILLE = 48          # px (image carrée)
MARGE = 8            # px entre l'image et le nom

MODELE = "ClubHistoryHonourCardRow"
SOURCE = "CompetitionLogo"           # son SIImage : chargeur d'images, comp.ObjectLookupData, type 1
CHEMIN = "row.Competition."          # remplace « comp. » du modèle source
VERSION = 1
PREFIXE = "UIPickerPalmaresImage"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "palmares_images.actif")
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "margin-right": (131092, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def marques(t):
    return [n for n in (t.name(r) for r in t.walk()) if n.startswith((PREFIXE, "UIPickerEssaiTrophee"))]


def construire(t):
    _, _, stt = nb.find_vta(SOURCE)
    if stt is None:
        return [f"{SOURCE} introuvable"]
    s = Tree(stt)
    img = next((r for r in s.walk() if (s.elem(r).get("m_FullTypeName") or "").endswith("SIImage")
                and any(b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in st._arguments(s.sd(r)))), None)
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
    for x in st._arguments(t.sd(r)):
        args = decode_args(x["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                a[1] = st.TYPE_IMAGE.to_bytes(4, "little")
            elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                ch = a[1][2:].decode()
                if ch.startswith("comp."):
                    ch = CHEMIN + ch[len("comp."):]
                    a[1] = b"\x01" + _enc_varint(len(ch)) + ch.encode()
                chemins_vus.append(ch)
        x["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, r, {"width": TAILLE, "height": TAILLE, "margin-right": MARGE})
    return [f"image du trophée posée ({', '.join(chemins_vus)})"]


def cmd_appliquer():
    st.images()
    actuel = st.ouvrir(MODELE, False)
    if actuel is None:
        print(f"{MODELE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    if NOM in marques(actuel[3]):
        print(f"{MODELE} : déjà appliqué")
    else:
        travail = st.ouvrir(MODELE)
        if travail is None:
            print(f"{MODELE} : pas de sauvegarde d'origine, ignoré")
            return
        msgs = construire(travail[3])
        msgs += ["ancienne version remplacée"] if marques(actuel[3]) else []
        for m in msgs:
            print(f"{MODELE} : {m}")
        if any("introuvable" in m for m in msgs):
            print(f"{MODELE} : rien enregistré")
            return
        st.enregistrer([travail])
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    actuel = st.ouvrir(MODELE, False)
    if actuel is None or not marques(actuel[3]):
        print("rien à retirer")
        return
    travail = st.ouvrir(MODELE)
    if travail is None:
        print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    st.enregistrer([travail])
    print(f"{MODELE} : images du palmarès retirées")


def cmd_etat():
    o = st.ouvrir(MODELE, False)
    if o is None:
        print(f"{MODELE} : introuvable")
        return
    m = marques(o[3])
    print(f"{MODELE} : " + (f"appliqué ({', '.join(m)} ; version actuelle v{VERSION})" if m else "sans images"))
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
            print("images du palmarès : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
