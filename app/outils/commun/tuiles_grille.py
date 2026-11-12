"""Édition des compositions de grille (tuiles) de FM dans ui-tileslayouts_assets_all.bundle.

Chaque écran à tuiles a un "GridCompositionSet" (ex. ClubFinancesCardGridCompositionSet) qui contient,
pour chaque taille d'écran (breakpoint 0..3), une ou plusieurs compositions. Une composition place chaque
tuile (m_elementID) dans une grille : m_location = colonne x, ligne y, largeur, hauteur (en cases).

Usage (avec le Python du projet : .venv\\Scripts\\python.exe outils\\commun\\tuiles_grille.py ...) :
  sets [filtre]                      liste les ensembles de compositions
  list <set>                         affiche les tuiles de chaque composition de l'ensemble
  swap <set> <tuileA> <tuileB>       échange la place de deux tuiles (dans chaque composition qui a les deux)
  move <set> <tuile> <x> <y> [w h] --bp N [--comp NOM]
                                     place une tuile dans les compositions du breakpoint N
                                     (--comp : seulement la composition qui porte ce nom exact)
  apply [fichier]                    grave les tuiles déplacées en jeu avec le mod (lignes "@tiles:" de
                                     BepInEx\\config\\uipicker_layout.txt par défaut)
  restore                            remet le bundle d'origine

<set> peut omettre le suffixe "GridCompositionSet". Le jeu doit être fermé pour modifier.
"""
import os
import sys

import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402

from chemin_jeu import GAME, AA  # noqa: E402  (dossier du jeu demandé par Outils FM.bat)
BUNDLE = os.path.join(AA, "ui-tileslayouts_assets_all.bundle")
SUFFIX = "GridCompositionSet"


def load():
    env = UnityPy.load(BUNDLE)
    return env, {o.path_id: o for o in env.objects}


def name_of(o):
    try:
        return o.peek_name()
    except Exception:
        return None


def find_set(objs, name):
    wanted = {name, name + SUFFIX}
    for o in objs.values():
        if o.type.name == "MonoBehaviour" and name_of(o) in wanted:
            tt = o.read_typetree()
            if "m_gridBreakpointCompositionData" in tt:
                return tt
    sys.exit(f"ensemble introuvable : {name} (essaie : sets {name[:6]})")


def compositions(objs, set_tt):
    """[(breakpoint, objet, typetree)] pour toutes les compositions de l'ensemble (même fichier uniquement)."""
    out = []
    for entry in set_tt["m_gridBreakpointCompositionData"]["m_values"]:
        for ref in entry["m_value"]:
            if ref["m_FileID"] == 0 and ref["m_PathID"] in objs:
                o = objs[ref["m_PathID"]]
                out.append((entry["m_key"], o, o.read_typetree()))
    return sorted(out, key=lambda c: c[0])


def loc(c):
    l = c["m_location"]
    return f"x={l['x']:<3} y={l['y']:<3} {l['width']}x{l['height']}"


def save(env):
    backup.write_bundle(BUNDLE, env.file.save(packer="original"))


def cmd_sets(objs, filt=""):
    names = sorted({n for o in objs.values() if o.type.name == "MonoBehaviour"
                    for n in [name_of(o)] if n and n.endswith(SUFFIX) and filt.lower() in n.lower()})
    for n in names:
        print(n[: -len(SUFFIX)])
    print(f"({len(names)} ensemble(s))")


def cmd_list(objs, set_name):
    s = find_set(objs, set_name)
    for bp, o, tt in compositions(objs, s):
        print(f"\n[breakpoint {bp}] {tt['m_Name']}")
        for c in sorted(tt["m_gridComponents"], key=lambda c: (c["m_location"]["y"], c["m_location"]["x"])):
            print(f"  {c['m_elementID']:<40} {loc(c)}")


def cmd_swap(env, objs, set_name, a, b):
    s = find_set(objs, set_name)
    changed = 0
    for bp, o, tt in compositions(objs, s):
        ca = next((c for c in tt["m_gridComponents"] if c["m_elementID"] == a), None)
        cb = next((c for c in tt["m_gridComponents"] if c["m_elementID"] == b), None)
        if ca is None or cb is None:
            print(f"[bp {bp}] {tt['m_Name']} : {a if ca is None else b} absent, ignoré")
            continue
        la, lb = ca["m_location"], cb["m_location"]
        if (la["width"], la["height"]) != (lb["width"], lb["height"]):
            # tailles différentes : l'échange ferait chevaucher des tuiles, on ne touche pas à cette composition
            print(f"[bp {bp}] {tt['m_Name']} : tailles différentes ({loc(ca)} / {loc(cb)}), ignoré")
            continue
        ca["m_location"], cb["m_location"] = lb, la
        o.save_typetree(tt)
        changed += 1
        print(f"[bp {bp}] {tt['m_Name']} : {a} -> {loc(ca)} | {b} -> {loc(cb)}")
    if changed:
        save(env)
    else:
        print("rien modifié")


def cmd_move(env, objs, set_name, tile, nums, bp_wanted, comp=None):
    s = find_set(objs, set_name)
    changed = 0
    for bp, o, tt in compositions(objs, s):
        if bp != bp_wanted or (comp is not None and tt["m_Name"] != comp):
            continue
        c = next((c for c in tt["m_gridComponents"] if c["m_elementID"] == tile), None)
        if c is None:
            continue
        l = c["m_location"]
        l["x"], l["y"] = nums[0], nums[1]
        if len(nums) >= 4:
            l["width"], l["height"] = nums[2], nums[3]
        o.save_typetree(tt)
        changed += 1
        print(f"[bp {bp}] {tt['m_Name']} : {tile} -> {loc(c)}")
    if changed:
        save(env)
    else:
        print(f"{tile} introuvable au breakpoint {bp_wanted}" + (f" dans {comp}" if comp else ""))


LAYOUT = os.path.join(GAME, "BepInEx", "config", "uipicker_layout.txt")


def read_mod_tiles(path):
    """{composition: {tuile: (x, y, w, h)}} depuis le fichier de réglages du mod."""
    comps = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\r\n").split("|", 2)
            if len(parts) < 3 or not parts[0].startswith("@tiles:"):
                continue
            if parts[1] == "__mode":   # mode de compaction (4 = libre, les tuiles ne sont pas tassées)
                comps.setdefault(parts[0][len("@tiles:"):], {})["__mode"] = int(parts[2])
                continue
            vals = parts[2].split()
            if len(vals) != 4:
                continue
            comps.setdefault(parts[0][len("@tiles:"):], {})[parts[1]] = tuple(int(v) for v in vals)
    return comps


def cmd_apply(env, objs, path):
    if not os.path.exists(path):
        sys.exit(f"fichier introuvable : {path}")
    wanted = read_mod_tiles(path)
    if not wanted:
        sys.exit("aucune tuile déplacée dans ce fichier (déplace une tuile en jeu avec le mod d'abord)")

    by_name = {}
    for o in objs.values():
        if o.type.name == "MonoBehaviour":
            n = name_of(o)
            if n in wanted:
                by_name.setdefault(n, []).append(o)

    changed = 0
    for comp, tiles in wanted.items():
        found = False
        for o in by_name.get(comp, []):
            tt = o.read_typetree()
            if "m_gridComponents" not in tt:
                continue
            found = True
            seen = {"__mode"}
            mode = tiles.get("__mode")
            if mode is not None and tt.get("m_layoutMode") != mode:
                print(f"  {comp} : mode de compaction {tt.get('m_layoutMode')} -> {mode}" + (" (libre)" if mode == 4 else ""))
                tt["m_layoutMode"] = mode
                changed += 1
            for c in tt["m_gridComponents"]:
                t = tiles.get(c["m_elementID"])
                if t is None:
                    continue
                seen.add(c["m_elementID"])
                l = c["m_location"]
                if (l["x"], l["y"], l["width"], l["height"]) != t:
                    print(f"  {comp} : {c['m_elementID']:<36} {loc(c)}  ->  x={t[0]:<3} y={t[1]:<3} {t[2]}x{t[3]}")
                    l["x"], l["y"], l["width"], l["height"] = t
                    changed += 1
                # taille mini : le jeu refuserait une tuile plus petite que son m_minSize
                mn = c.get("m_minSize")
                if mn and (t[2] < mn["x"] or t[3] < mn["y"]):
                    mn["x"], mn["y"] = min(mn["x"], t[2]), min(mn["y"], t[3])
                    print(f"  {comp} : {c['m_elementID']:<36} taille mini abaissée à {mn['x']}x{mn['y']}")
                    changed += 1
            for missing in sorted(set(tiles) - seen):
                print(f"  {comp} : {missing} n'existe pas dans le bundle (tuile optionnelle ?), ignorée")
            o.save_typetree(tt)
        if not found:
            print(f"composition introuvable dans le bundle : {comp}")

    if changed:
        save(env)
        print(f"{changed} tuile(s) mise(s) à jour")
    else:
        print("le bundle a déjà cette disposition, rien à écrire")


def cmd_restore():
    backup.restore(BUNDLE)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    op, args = argv[0], argv[1:]
    if op == "restore":
        return cmd_restore()
    env, objs = load()
    if op == "apply":
        cmd_apply(env, objs, args[0] if args else LAYOUT)
    elif op == "sets":
        cmd_sets(objs, args[0] if args else "")
    elif op == "list" and len(args) == 1:
        cmd_list(objs, args[0])
    elif op == "swap" and len(args) == 3:
        cmd_swap(env, objs, *args)
    elif op == "move" and len(args) >= 4:
        opts = {}
        for flag in ("--bp", "--comp"):
            if flag in args:
                i = args.index(flag)
                opts[flag] = args[i + 1]
                args = args[:i] + args[i + 2:]
        cmd_move(env, objs, args[0], args[1], [int(v) for v in args[2:6]],
                 int(opts.get("--bp", 0)), opts.get("--comp"))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
