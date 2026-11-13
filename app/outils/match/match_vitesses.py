"""Match : crans de la « Vitesse du match pendant les temps forts » (menu du match / préférences).

FM : 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 10 (11 crans, le curseur donne un rang dans cette liste). Ici la
liste est remplacée par VITESSES_PENDANT, aux deux endroits où FM la range (données, pas le programme) :
- liste du menu : `m_speedDuringHighlightsOptions` (MonoBehaviour de initscene-assets_assets_all.bundle) ;
- liste du match : `m_matchDefaultPlaybackSettings[*].m_speedValues` (MonoBehaviour de la scène
  scenes_scenes_initscene.bundle), seulement les entrées qui ont la liste de FM.
Seul écrivain de ces deux bundles. Retirer remet la liste de FM.

Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
# 2026-11-13, le joueur : x 1.4 entre le 4e (1.25) et le 5e (1.5)
VITESSES_PENDANT = [0.5, 0.75, 1, 1.25, 1.4, 1.5, 1.75, 2, 2.5, 3, 4, 10]
# =====================================================================================================

VERSION = 1   # v1 : x 1.4 ajouté (12 crans)
FM_PENDANT = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4, 10]
MENU = ("initscene-assets_assets_all.bundle", "m_speedDuringHighlightsOptions")
MATCH = ("scenes_scenes_initscene.bundle", "m_matchDefaultPlaybackSettings")
MARKER = os.path.join(backup.BACKUP_DIR, "match_vitesses.actif")


def _signature(liste):
    """octets d'un tableau float32 sérialisé : nombre (int32) + valeurs"""
    return struct.pack(f"<i{len(liste)}f", len(liste), *liste)


def _egal(a, b):
    return len(a) == len(b) and all(abs(x - y) < 1e-4 for x, y in zip(a, b))


def _objet(bundle, champ):
    """(chemin du bundle, objet, typetree) du MonoBehaviour qui a ce champ"""
    p = os.path.join(nb.AA, bundle)
    if not os.path.exists(p):
        return p, None, None
    for o in nb.env_of(p).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            raw = o.get_raw_data()
        except Exception:
            continue
        if len(raw) > 20000 or not any(_signature(liste) in raw for liste in (FM_PENDANT, VITESSES_PENDANT)):
            continue   # lire seulement les objets qui portent la liste (read_typetree sur d'autres : risque de plantage)
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if champ in tt:
            return p, o, tt
    return p, None, None


def regler(avec):
    voulu = [float(v) for v in (VITESSES_PENDANT if avec else FM_PENDANT)]
    autre = FM_PENDANT if avec else VITESSES_PENDANT
    msgs = []
    p, o, tt = _objet(*MENU)
    if tt is None:
        msgs.append(f"{MENU[1]} introuvable (mise à jour du jeu ?)")
    elif not _egal(tt[MENU[1]], voulu):
        if not _egal(tt[MENU[1]], autre):
            msgs.append(f"menu : liste inattendue {tt[MENU[1]]}, laissée")
        else:
            tt[MENU[1]] = voulu
            o.save_typetree(tt)
            nb._dirty.add(p)
            msgs.append(f"menu : {len(voulu)} crans")
    p, o, tt = _objet(*MATCH)
    if tt is None:
        msgs.append(f"{MATCH[1]} introuvable (mise à jour du jeu ?)")
    else:
        n = 0
        for e in tt[MATCH[1]]:
            if _egal(e.get("m_speedValues") or [], autre):
                e["m_speedValues"] = list(voulu)
                n += 1
        if n:
            o.save_typetree(tt)
            nb._dirty.add(p)
            msgs.append(f"match : {n} liste(s) à {len(voulu)} crans")
        elif not any(_egal(e.get("m_speedValues") or [], voulu) for e in tt[MATCH[1]]):
            msgs.append("match : liste de FM introuvable, laissée")
    return msgs


def cmd(avec):
    if not avec and os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = regler(avec)
    for m in msgs or (["déjà appliqué"] if avec else ["rien à retirer"]):
        print(f"vitesses du match : {m}")
    nb.save_all()
    if avec and not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_etat():
    for b, champ in (MENU, MATCH):
        _, _, tt = _objet(b, champ)
        if tt is None:
            print(f"{champ} : introuvable")
        elif champ == MENU[1]:
            print("menu :", tt[champ])
        else:
            print("match :", [e.get("m_speedValues") for e in tt[champ]])
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd(True)
    elif op == "retirer":
        cmd(False)
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd(True)
        else:
            print("vitesses du match : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
