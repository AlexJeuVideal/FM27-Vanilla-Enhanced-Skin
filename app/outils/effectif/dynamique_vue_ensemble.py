"""Dynamique de groupe > Vue d'ensemble : blocs du haut moins hauts, tableau « Problèmes » plus haut.

L'écran est une grille de tuiles (SquadAtmosphereCardComposition-*, bundle ui-tileslayouts). En haut : Soutien de
l'entraîneur, Cohésion d'équipe, Atmosphère au club (4 rangées chez FM) ; dessous : Problèmes ; en bas : les petites
tuiles (Capitaines, Hiérarchie, Cercles d'amis, État d'esprit), seulement décalées vers le bas. FM étire les blocs du
haut pour remplir l'écran : on fixe donc hauteur ET minimum des blocs du haut et de Problèmes (voir réglages).

Toujours calculé à partir des valeurs d'origine (sauvegarde) : relancer ou changer le réglage ne cumule rien.
Retirer remet les places d'origine de ces tuiles (le reste du bundle, dont les tuiles de tuiles_grille, est gardé).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\effectif\\dynamique_vue_ensemble.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\effectif\\dynamique_vue_ensemble.py retirer
  .venv\\Scripts\\python.exe outils\\effectif\\dynamique_vue_ensemble.py etat
"""
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (correctif UnityPy, chemins du jeu)
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
HAUT_RANGEES = 5      # hauteur des blocs du haut, en rangées de la grille (FM : 4, étirés à ~12 en grand écran)
PROBLEMES_RANGEES = 3    # hauteur de BASE de Problèmes (FM : 3) ; il grandit ensuite pour remplir l'écran.
# FM ne descend jamais sous la hauteur de base : haut + Problèmes + 2 doit tenir dans le mode aux plus grosses rangées
# (FM d'origine : 9 rangées en tout ; v3 à 5 + 8 + 2 = 15 : tuiles du bas sous l'écran en mode ~75 px / rangée).
# FM : chaque tuile part de sa taille minimale, la place en trop va aux tuiles qui peuvent grandir. Chez FM, Problèmes
# a un MAXIMUM de 3 rangées (m_maxSize 100x3) : toute la place partait dans les blocs du haut (max 100).
# v3 : blocs du haut min = max = HAUT_RANGEES, Problèmes sans maximum → il prend le reste, dans chaque mode
# d'affichage (v2 : hauteurs fixes, tuiles du bas sous l'écran quand les rangées sont plus hautes).
PROBLEMES_MAX = 100
COMPOSITIONS = [      # tailles de fenêtre touchées (FM : Large = grand écran, Standard = moyen, sans suffixe = défaut)
    "SquadAtmosphereCardComposition-Large",
    "SquadAtmosphereCardComposition-Standard",
    "SquadAtmosphereCardComposition",
]
# =====================================================================================================

TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
PROBLEMES = "SquadIssues"
MARKER = os.path.join(backup.BACKUP_DIR, "dynamique_vue_ensemble.actif")
DRY_RUN = "--dry-run" in sys.argv


def compositions(env):
    """{nom: (objet, typetree)} des compositions voulues"""
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in COMPOSITIONS:
            tt = o.read_typetree()
            if "m_gridComponents" in tt:
                out[n] = (o, tt)
    return out


def origine():
    """compositions d'origine (sauvegarde si le bundle a déjà été modifié)"""
    src = backup.backup_path(TUILES)
    return compositions(UnityPy.load(src if os.path.exists(src) else TUILES))


def places(tt):
    """{tuile: (location, minSize, maxSize)}"""
    return {c["m_elementID"]: (dict(c["m_location"]), dict(c["m_minSize"]), dict(c["m_maxSize"]))
            for c in tt["m_gridComponents"]}


def voulu(orig_tt):
    """{tuile: (location, minSize, maxSize)} : blocs du haut HAUT_RANGEES (min = max), Problèmes PROBLEMES_RANGEES
    sans maximum (minimum FM gardé), petites tuiles du bas décalées dessous"""
    p = places(orig_tt)
    hauts = [k for k, (l, _, _) in p.items() if l["y"] == 0]
    if not hauts or PROBLEMES not in p:
        return None
    h = max(p[k][0]["height"] for k in hauts)
    pb = p[PROBLEMES][0]
    if pb["y"] != h:
        return None
    bas_orig = pb["y"] + pb["height"]
    decalage = HAUT_RANGEES + PROBLEMES_RANGEES - bas_orig
    for k in hauts:
        l, mn, mx = p[k]
        l["height"] = mn["y"] = mx["y"] = HAUT_RANGEES
    l, mn, mx = p[PROBLEMES]
    l["y"], l["height"] = HAUT_RANGEES, PROBLEMES_RANGEES
    mn["y"] = min(mn["y"], PROBLEMES_RANGEES)
    mx["y"] = PROBLEMES_MAX
    bas = [k for k, (l, _, _) in p.items() if l["y"] >= bas_orig]
    for k in bas:
        p[k][0]["y"] += decalage
    return {k: p[k] for k in hauts + [PROBLEMES] + bas}


def run(retirer):
    env = UnityPy.load(TUILES)
    actuels, orig = compositions(env), origine()
    change = 0
    for nom in COMPOSITIONS:
        if nom not in actuels or nom not in orig:
            print(f"{nom} : introuvable (renommée par une mise à jour ?), ignorée")
            continue
        o, tt = actuels[nom]
        cible = places(orig[nom][1]) if retirer else voulu(orig[nom][1])
        if cible is None:
            print(f"{nom} : disposition inattendue (le jeu a changé ?), ignorée")
            continue
        fait = []
        for c in tt["m_gridComponents"]:
            if c["m_elementID"] not in cible:
                continue
            l, mn, mx = cible[c["m_elementID"]]
            if (c["m_location"], c["m_minSize"], c["m_maxSize"]) != (l, mn, mx):
                c["m_location"].update(l)
                c["m_minSize"].update(mn)
                c["m_maxSize"].update(mx)
                fait.append(f"{c['m_elementID']} y={l['y']} {l['width']}x{l['height']}")
        if fait:
            o.save_typetree(tt)
            change += 1
            print(f"{nom} : " + ", ".join(fait))
        else:
            print(f"{nom} : " + ("déjà d'origine" if retirer else "déjà appliqué"))
    if change:
        data = env.file.save(packer="original")
        if DRY_RUN:
            print(f"(essai à blanc : rien écrit, {os.path.basename(TUILES)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(TUILES, data)
    if not DRY_RUN:
        if retirer and os.path.exists(MARKER):
            os.remove(MARKER)
        elif not retirer:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)


def cmd_etat():
    actuels, orig = compositions(UnityPy.load(TUILES)), origine()
    for nom in COMPOSITIONS:
        if nom not in actuels:
            print(f"{nom} : introuvable")
            continue
        p, v = places(actuels[nom][1]), voulu(orig[nom][1]) if nom in orig else None
        pb = p.get(PROBLEMES, ({}, {}))[0]
        etat = "appliqué" if v and all(p.get(k) == x for k, x in v.items()) else \
            ("d'origine" if nom in orig and p == places(orig[nom][1]) else "autre disposition")
        print(f"{nom} : {etat} (Problèmes y={pb.get('y')} hauteur {pb.get('height')})")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        run(retirer=False)
    elif op == "retirer":
        run(retirer=True)
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            run(retirer=False)
        else:
            print("vue d'ensemble de la dynamique : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
