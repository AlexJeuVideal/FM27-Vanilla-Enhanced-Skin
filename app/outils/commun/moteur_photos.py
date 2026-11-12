"""Photos des joueurs sur les terrains (moteur commun) : photo FM (thumbnails-alt-person-picture, recopiée de
PlayerIndicatorBestXICard, menu clic droit coupé comme là-bas) à côté du maillot de chaque carte.
Utilisé par tactiques\\photos_tactiques.py et match\\photos_match.py : chacun donne ses cartes (CIBLES), ses
réglages, sa VERSION et son marqueur. Chaque script est seul propriétaire de ses cartes : appliquer repart toujours
des originaux sauvegardés, retirer les remet.
(Avant le rangement du 2026-11-12 : photos_terrain.py, les deux ensemble.)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, no_styles  # noqa: E402
from elements import copy_usings, move  # noqa: E402
from club_page_bas import original  # noqa: E402

LOGOS_DESSUS = True           # tactiques : logos de mouvement du rôle (à gauche / à droite) par-dessus la photo
CIBLES = []                   # (modèle, repère, chemin de la personne, réglages) : donnés par le script appelant
MARKER = None
VERSION = 0
PREFIXE = "UIPickerPhotoTerrain"
NOM = f"{PREFIXE}-v{VERSION}"
PHOTO_SOURCE = "PlayerIndicatorBestXICard"     # BindingRemapper person -> position.Player + photo FM
PHOTO_MODELE = "thumbnails-alt-person-picture"

for k, v in {"width": (131105, 3), "height": (131087, 3), "margin-right": (131092, 3),
             "margin-left": (131091, 3), "top": (131104, 3), "left": (131089, 3),
             "flex-direction": (131083, 7), "align-items": (131073, 7), "justify-content": (131088, 7),
             "max-height": (131094, 3), "min-height": (131096, 3), "right": (131103, 3),
             "bottom": (131080, 3), "position": (131102, 7)}.items():
    sm.PROPRIETES.setdefault(k, v)


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def repere(t, rep):
    """élément devant lequel poser la photo"""
    if rep.startswith("#"):
        return next((r for r in t.walk() if t.name(r) == rep[1:]), None)
    return next((r for r in t.walk() if typ(t, r) == rep and t.name(t.parent.get(r, r)) == "ShirtAndRoleMovements"),
                None)


def largeur(t, rid, defaut=34.0):
    """largeur en px de l'élément d'après son style intégré (min-width / width), sinon defaut"""
    if t.elem(rid).get("m_RuleIndex", -1) < 0:
        return defaut
    vals = {pid: v for pid, _, v in t.styles.values(t.elem(rid)["m_RuleIndex"])}
    for pid in (131105, 131097):   # Width, MinWidth
        v = vals.get(pid)
        if v and v[0][0] == 3 and v[0][1].get("unit") == 1:
            return v[0][1]["value"]
    return defaut


def source_photo():
    """(arbre, BindingRemapper parent de la 1re photo) du modèle source"""
    _, _, tt = nb.find_vta(PHOTO_SOURCE)
    if tt is None:
        return None, None
    s = Tree(tt)
    photo = next((r for r in s.walk() if s.elem(r).get("m_TemplateAlias") == PHOTO_MODELE), None)
    if photo is None or typ(s, s.parent[photo]) != "BindingRemapper":
        return s, None
    return s, s.parent[photo]


def ouvrir(modele, depart_original=False):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    sheet = None
    if depart_original:
        orig = original(bundle, obj)
        if orig is not None:
            tt = orig
            sheet = original(bundle, obj, tt["inlineSheet"]["m_PathID"])
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    if sheet is not None:   # feuille d'origine aussi : les règles des versions précédentes ne s'empilent pas
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, tt, t


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def poser_photo(t, s, rm_src, rep, chemin, cfg):
    """photo (BindingRemapper person -> chemin + photo FM) à côté du maillot repère ; renvoie un message"""
    cible = repere(t, rep)
    if cible is None:
        return f"repère {rep} introuvable"
    taille, chevauche, remonter = cfg["photo"], cfg["chevauche"], cfg["remonter"]
    garder, dessus = cfg["maillot"] != "retire", cfg["maillot"] == "dessus"
    parent = t.parent[cible]
    index = t.children(parent).index(cible)
    # photo par-dessus : elle doit être dessinée après le maillot, donc venir après lui (pas de z-index en UI Toolkit)
    rm = t.clone(rm_src, parent, index + 1 if dessus else index, src=s)
    copy_usings(t, s, rm_src)
    no_styles(t, rm)
    sd = t.sd(rm)
    sd.update(name=NOM, name_UxmlAttributeFlags=1)
    for m in sd.get("Mappings") or []:
        if m.get("from") == "person":
            m["to"]["m_path"] = chemin
    t.elem(rm)["m_Classes"] = []
    css = {"width": taille, "height": taille, "flex-shrink": 0}
    msgs = [f"photo {taille} px ({chemin})"]
    if dessus:
        # mise en page [maillot][photo] resserrée de chevauche, puis échange visuel (left relatif) :
        # photo à gauche, maillot à droite, même largeur totale
        maillot = cfg.get("maillot_px") or largeur(t, cible)
        decale = cfg.get("decaler", 0)   # décalage visuel de tout le groupe
        css["margin-left"] = -chevauche
        css["left"] = -(maillot - chevauche) + decale
        taille_maillot = {}
        if cfg.get("maillot_px"):   # FM fixe parfois aussi min / max (tactiques : 34 px partout)
            taille_maillot = {k: maillot for k in ("width", "height", "min-width", "min-height", "max-width",
                                                   "max-height")}
        if cfg.get("maillot_bas"):
            taille_maillot["top"] = cfg["maillot_bas"]
            msgs.append(f"maillot décalé de {cfg['maillot_bas']:+g} px en hauteur")
        t.styles.style(t, cible, {"left": taille - chevauche + decale, **taille_maillot})
        if decale:
            msgs.append(f"groupe décalé de {decale:+g} px")
        if rep != "FMTacticsShirt":   # #ShirtAndRoleMovements est déjà en ligne ; ailleurs le parent est en colonne
            ligne = {"flex-direction": "row"}
            if cfg.get("centrer"):   # zone entière entre ses voisines, contenu centré, bas alignés
                ligne.update({"flex-grow": 1, "justify-content": "center", "align-items": "flex-end"})
                if remonter:   # tout le groupe monte (décalage visuel seul)
                    ligne["top"] = -remonter
                    msgs.append(f"groupe remonté de {remonter} px")
                    remonter = 0
            t.styles.style(t, parent, ligne)
        msgs.append(f"par-dessus le maillot ({maillot:g} px), {chevauche} px l'un sur l'autre"
                    + (", centrés, bas alignés" if cfg.get("centrer") else ""))
    elif garder:
        if chevauche:
            css["margin-right"] = -chevauche
        if cfg.get("ecart"):   # 2026-11-05 : petit écart photo | maillot (côte à côte)
            css["margin-right"] = cfg["ecart"]
        if cfg.get("maillot_px"):
            m = cfg["maillot_px"]
            t.styles.style(t, cible, {k: m for k in ("width", "height", "min-width", "min-height", "max-width",
                                                     "max-height")})
            msgs.append(f"maillot {m} px")
        if cfg.get("centrer"):   # groupe photo + maillot centré, bas alignés
            t.styles.style(t, parent, {"flex-direction": "row", "justify-content": "center",
                                       "align-items": "flex-end"})
            msgs.append(f"côte à côte ({cfg.get('ecart', 0)} px), centrés")
    if remonter:   # décalage visuel seul (position relative) : la carte ne change pas de taille
        css["top"] = -remonter
        msgs.append(f"remontée de {remonter} px")
    if rep == "FMTacticsShirt" and LOGOS_DESSUS:   # logos absolus : dessinés après la photo = par-dessus
        logos = [k for k in t.children(parent) if t.name(k).endswith("RoleRemapper")]
        for k in logos:
            move(t, k, parent)
        msgs.append(f"{len(logos)} logos de rôle par-dessus")
        coin = cfg.get("logos_coins")
        if coin is not None and logos:
            # carte = parent de #ShirtAndIcons (#tactics-draggable) : le rectangle des rôles en part du haut, et
            # #ShirtAndIcons est dessiné au-dessus (top -32). Logos en derniers enfants de la carte : par-dessus le
            # rectangle, sans être rognés (v13 : mis DANS le rectangle, qui coupe ce qui dépasse -> invisibles).
            carte = t.parent[t.parent[parent]]
            for k in logos:
                move(t, k, carte)
                t.elem(k)["m_RuleIndex"] = -1   # plus de left / right / bottom 4 de FM
                cote = "left" if t.name(k).startswith("IP") else "right"
                t.styles.style(t, k, {"position": "absolute", cote: coin, "top": coin + cfg.get("logos_haut", 0)})
            msgs.append(f"logos sur les coins supérieurs de la carte (#{t.name(carte)}, {coin:g} px, "
                        f"haut {coin + cfg.get('logos_haut', 0):g} px)")
    t.styles.style(t, rm, css)
    for p in t.children(rm):
        t.styles.style(t, p, {"width": taille, "height": taille})
    if not garder:
        t.remove(cible)
        msgs.append("maillot retiré")
    return ", ".join(msgs)


def cmd_appliquer():
    s, rm_src = source_photo()
    if rm_src is None:
        print(f"photo FM introuvable dans {PHOTO_SOURCE} (mise à jour du jeu ?) : rien fait")
        return
    a_enregistrer = []
    for modele, rep, chemin, cfg in CIBLES:
        actuel = ouvrir(modele)
        if actuel is None:
            print(f"{modele} : introuvable, ignoré")
            continue
        if any(actuel[3].name(r) == NOM for r in marques(actuel[3])):
            print(f"{modele} : déjà appliqué")
            continue
        travail = ouvrir(modele, depart_original=True)
        if marques(travail[3]):
            print(f"{modele} : pas de sauvegarde d'origine propre, ignoré")
            continue
        msg = poser_photo(travail[3], s, rm_src, rep, chemin, cfg)
        print(f"{modele} : {msg}")
        if "introuvable" in msg:
            continue
        a_enregistrer.append(travail)
    for bundle, obj, tt, t in a_enregistrer:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    if a_enregistrer:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    for modele, *_ in CIBLES:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{modele} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele, *_ in CIBLES:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        noms = sorted({o[3].name(r) for r in marques(o[3])})
        print(f"{modele} : " + (f"photo ({', '.join(noms)} ; version actuelle v{VERSION})" if noms else "d'origine"))
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
            print("photos sur le terrain : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
