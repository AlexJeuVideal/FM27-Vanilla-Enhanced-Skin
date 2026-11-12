"""Bundle des fonds (ui-backgrounds_assets_.bundle) : UN SEUL ÉCRIVAIN, repart toujours de l'original.

Deux fonctions y écrivent :
- theme_fond : fond des pages (texture fm27_skin_default peinte dans la couleur choisie, + variantes PAGES_CLUB) ;
- club_page_bas : stade générique des clubs sans photo, posé à la place de la texture
  de test inutilisée de FM « caraboa-cup-skin-test-min » (citée par aucun écran ; GUID dans club_page_bas).
ecrire() refait le bundle avec ce qui est actif (marqueurs), ou le remet d'origine si plus rien ne l'est.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402
import notes_au_lieu_des_libelles as nb  # noqa: E402

BUNDLE = os.path.join(nb.AA, "ui-backgrounds_assets_.bundle")
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
        return
    env = UnityPy.load(orig if os.path.exists(orig) else BUNDLE)
    tex = {}
    for o in env.objects:
        if o.type.name == "Texture2D":
            t = o.read()
            tex[t.m_Name] = t
    faits = []
    if theme is not None:
        import theme_fond
        theme_fond.peindre(tex, theme)
        faits.append("fond des pages")
    if stade:
        t = tex.get(STADE_TEXTURE)
        if t is None:
            print(f"fonds : texture {STADE_TEXTURE} introuvable (le jeu a changé ?), stade générique ignoré")
        else:
            t.set_image(Image.open(STADE_IMAGE).convert("RGBA"), target_format=TextureFormat.RGBA32, mipmap_count=1)
            t.save()
            faits.append("stade générique")
    data = env.file.save(packer="original")
    import hashlib
    if os.path.exists(BUNDLE) and hashlib.sha256(data).hexdigest() == backup._sha(BUNDLE):
        # déjà ce bundle dans le jeu (2026-11-12 : l'essai à blanc disait toujours « ferait », Vérifier signalait
        # club_page_bas « pas à jour » alors qu'il l'était)
        print("fonds : déjà à jour (" + " + ".join(faits) + ")")
        return
    if a_blanc:
        print(f"(essai à blanc : rien écrit, {os.path.basename(BUNDLE)} ferait {len(data) / 1e6:.2f} Mo : "
              + " + ".join(faits) + ")")
    else:
        backup.write_bundle(BUNDLE, data)
        print("fonds : " + " + ".join(faits))
