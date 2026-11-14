"""Bundles des fonds (ui-backgrounds_assets_.bundle + ui-backgrounds_assets_common.bundle) : UN SEUL ÉCRIVAIN,
repart toujours de l'original.

Deux fonctions y écrivent :
- theme_fond : fond des pages (texture fm27_skin_default peinte dans la couleur choisie, + variantes PAGES_CLUB) ;
  en mode couleur, aussi les fonds des compétitions sous licence et fonds plein écran (les deux bundles) ;
- club_page_bas : stade générique des clubs sans photo, posé à la place de la texture
  de test inutilisée de FM « caraboa-cup-skin-test-min » (citée par aucun écran ; GUID dans club_page_bas).
ecrire() refait les bundles avec ce qui est actif (marqueurs), ou les remet d'origine si plus rien ne l'est.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import notes_au_lieu_des_libelles as nb  # noqa: E402

BUNDLE = os.path.join(nb.AA, "ui-backgrounds_assets_.bundle")
# 2026-11-14 : 2e lot de fonds de compétition : common (premier_league_skin_fm26, efl-*-skin, uefa-cl_*_skin_fm26…).
# JAMAIS 1x-4x : écrans VAR (panneaux 600x400 + uefa-champions_league-skin du 1x), le joueur : « la VAR on touche pas »
BUNDLES_EN_PLUS = [os.path.join(nb.AA, "ui-backgrounds_assets_common.bundle")]
STADE_TEXTURE = "caraboa-cup-skin-test-min"
STADE_IMAGE = os.path.join(chemins.OUTILS, "club", "images", "UIPickerStadeDefaut.png")
AUTO = object()


def theme_auto():
    """couleur du fond (marqueur de theme_fond) en (r, g, b), ou None"""
    try:
        with open(os.path.join(backup.BACKUP_DIR, "theme_fond.actif"), encoding="utf-8") as f:
            c = json.load(f).get("couleur")
    except (OSError, ValueError):
        return None
    if not c:
        return None
    import theme_fond
    return theme_fond.to_rgb(c)


def stade_auto():
    return os.path.exists(os.path.join(backup.BACKUP_DIR, "club_page_bas.actif"))


def _textures(env):
    tex = {}
    for o in env.objects:
        if o.type.name == "Texture2D":
            t = o.read()
            tex[t.m_Name] = t
    return tex


def _ecrire_bundle(bundle, data, faits, a_blanc):
    import hashlib
    if os.path.exists(bundle) and hashlib.sha256(data).hexdigest() == backup._sha(bundle):
        # déjà ce bundle dans le jeu (2026-11-12 : l'essai à blanc disait toujours « ferait », Vérifier signalait
        # club_page_bas « pas à jour » alors qu'il l'était)
        print(f"fonds : déjà à jour ({' + '.join(faits)})")
        return
    if a_blanc:
        print(f"(essai à blanc : rien écrit, {os.path.basename(bundle)} ferait {len(data) / 1e6:.2f} Mo : "
              + " + ".join(faits) + ")")
    else:
        backup.write_bundle(bundle, data)
        print("fonds : " + " + ".join(faits))


def _remettre(bundle, a_blanc):
    if a_blanc:
        print(f"(essai à blanc) fonds : {os.path.basename(bundle)} remis d'origine")
    elif os.path.exists(backup.backup_path(bundle)) and backup._sha(bundle) != backup._sha(backup.backup_path(bundle)):
        backup.restore(bundle)


def ecrire(theme=AUTO, stade=AUTO, a_blanc=False):
    """theme = (r, g, b) ou None ; stade = True / False ; AUTO = d'après les marqueurs"""
    import UnityPy
    from PIL import Image
    from UnityPy.enums import TextureFormat
    theme = theme_auto() if theme is AUTO else theme
    stade = stade_auto() if stade is AUTO else stade
    orig = backup.backup_path(BUNDLE)
    if theme is None and not stade:
        if a_blanc:
            print("(essai à blanc) fonds : remis d'origine")
        elif os.path.exists(orig):
            backup.restore(BUNDLE)
        for b in BUNDLES_EN_PLUS:
            _remettre(b, a_blanc)
        return
    env = UnityPy.load(orig if os.path.exists(orig) else BUNDLE)
    tex = _textures(env)
    faits = []
    competitions = False
    if theme is not None:
        import theme_fond
        theme_fond.peindre(tex, theme)
        faits.append("fond des pages")
        competitions = bool(theme_fond._COMPET)
    if stade:
        t = tex.get(STADE_TEXTURE)
        if t is None:
            print(f"fonds : texture {STADE_TEXTURE} introuvable (le jeu a changé ?), stade générique ignoré")
        else:
            t.set_image(Image.open(STADE_IMAGE).convert("RGBA"), target_format=TextureFormat.RGBA32, mipmap_count=1)
            t.save()
            faits.append("stade générique")
    _ecrire_bundle(BUNDLE, env.file.save(packer="original"), faits, a_blanc)
    for b in BUNDLES_EN_PLUS:
        if not os.path.exists(b):
            continue
        if not competitions:
            _remettre(b, a_blanc)
            continue
        orig_c = backup.backup_path(b)
        env_c = UnityPy.load(orig_c if os.path.exists(orig_c) else b)
        n = theme_fond.peindre_competitions(_textures(env_c))
        print(f"fonds des compétitions ({os.path.basename(b)}) : {n} à la couleur du fond")
        if n:
            _ecrire_bundle(b, env_c.file.save(packer="original"), ["fonds des compétitions"], a_blanc)


# ESSAI (2026-11-14, le joueur : « un thème où tu repeins chaque image, pour savoir quoi fait quoi ») : chaque texture
# des 2 bundles = couleur vive différente + son numéro et son nom en gros. Retour normal : toute autre écriture des
# fonds (thème appliqué / retiré, choix 1), qui repart de l'original.
def _vignette(i, nom, larg, haut):
    import colorsys
    from PIL import Image, ImageDraw, ImageFont
    w = 640
    h = max(120, round(w * haut / max(larg, 1)))
    # couleurs les plus différentes possible : teinte au nombre d'or, saturation et luminosité qui tournent aussi
    s, v = (1.0, 0.55, 0.85)[i % 3], (1.0, 0.62, 0.38)[(i // 3) % 3]
    r, g, b = (round(c * 255) for c in colorsys.hsv_to_rgb((i * 0.618) % 1, s, v))
    im = Image.new("RGBA", (w, h), (r, g, b, 255))
    dr = ImageDraw.Draw(im)
    gros, petit = ImageFont.load_default(size=min(90, h // 3)), ImageFont.load_default(size=30)
    for x, y in ((6, 4), (w - 80, 4), (6, h - 38), (w - 80, h - 38)):   # numéro dans les coins (image coupée)
        dr.text((x + 2, y + 2), f"#{i}", font=petit, fill=(0, 0, 0, 255))
        dr.text((x, y), f"#{i}", font=petit, fill=(255, 255, 255, 255))
    lignes = [nom[k:k + 34] for k in range(0, len(nom), 34)]
    y = max(4, (h - min(90, h // 3) - 36 * len(lignes)) // 2)
    for texte, police, pas in [(f"#{i}", gros, min(90, h // 3) + 6)] + [(l, petit, 36) for l in lignes]:
        tw = dr.textlength(texte, font=police)
        x = (w - tw) / 2
        dr.text((x + 2, y + 2), texte, font=police, fill=(0, 0, 0, 255))
        dr.text((x, y), texte, font=police, fill=(255, 255, 255, 255))
        y += pas
    return im


def essai_noms(a_blanc=False):
    import UnityPy
    from UnityPy.enums import TextureFormat
    i = 0
    for b in [BUNDLE] + BUNDLES_EN_PLUS:
        if not os.path.exists(b):
            continue
        o = backup.backup_path(b)
        env = UnityPy.load(o if os.path.exists(o) else b)
        tex = _textures(env)
        for nom in sorted(tex, key=str.lower):
            i += 1
            t = tex[nom]
            print(f"  #{i} {nom} ({os.path.basename(b)})")
            t.set_image(_vignette(i, nom, t.m_Width, t.m_Height), target_format=TextureFormat.RGBA32, mipmap_count=1)
            t.save()
        _ecrire_bundle(b, env.file.save(packer="original"), ["ESSAI noms des images"], a_blanc)


if __name__ == "__main__":
    if sys.argv[1:2] == ["essai-noms"]:
        essai_noms(a_blanc="--dry-run" in sys.argv)
    else:
        sys.exit("fonds_jeu.py essai-noms [--dry-run]")
