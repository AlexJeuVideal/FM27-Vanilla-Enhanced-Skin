"""Match en direct : la tuile « Banc de touche » devient une tuile à choix (⌄) comme les autres (2026-11-18, le joueur).

FM met le Banc de touche (DugoutTileDescription) en « bloc » (config Type 1) : la grille ne lui donne pas le ⌄ des
choix et il n'est pas proposé dans le ⌄ des autres tuiles -> coincé à sa place dans toutes les vues. Ici :
- ses configs passent en « tuile » (Type 0, comme xG, Événements, cartes de passes...) : ⌄ avec les mêmes choix
  communs que les autres tuiles de l'écran, et Banc de touche proposé dans leur ⌄ ;
- dans les compositions de l'écran de match qui ont la place « Dugout » (Large, Standard, Small, avec / sans
  championnat, match de ton équipe ou non ; pas le téléphone), la Carte de passes de l'équipe à domicile est choisie
  d'office (Banc de touche reste au ⌄).

Toujours calculé à partir des valeurs d'origine (sauvegarde) : relancer ne cumule rien.
Une disposition de l'écran gardée par la partie (tuile changée au ⌄) passe avant.

Usage (jeu fermé) : match_tuile_banc.py appliquer [--dry-run] | retirer [--dry-run] | etat | si-actif
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
BANC = "DugoutTileDescription"
DEFAUT = "HomeTeamPassMapTileDescription"      # tuile d'office à la place du banc (le joueur : « map de passe domicile »)
PLACE = "Dugout"                               # m_elementID de la place du banc dans les compositions
ENSEMBLES = ["MatchExperienceGridCompositionSet", "MatchExperienceGridCompositionSet-NoLeague",
             "MatchExperienceHumanGridCompositionSet", "MatchExperienceHumanGridCompositionSet-NoLeague"]
SANS = ("Phone_Landscape",)                    # compositions laissées à FM (téléphone : banc déjà au choix)
# =====================================================================================================

TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
MARKER = os.path.join(backup.BACKUP_DIR, "match_tuile_banc.actif")
DRY_RUN = "--dry-run" in sys.argv


def par_nom(env):
    out = {}
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            out.setdefault(o.peek_name(), o)
        except Exception:
            continue
    return out


def compositions(env, noms):
    """{nom: objet} des compositions des ENSEMBLES"""
    par_pid = {o.path_id: o for o in env.objects}
    out = {}
    for e in ENSEMBLES:
        o = noms.get(e)
        if o is None:
            continue
        for v in o.read_typetree().get("m_gridBreakpointCompositionData", {}).get("m_values", []):
            for r in v["m_value"]:
                c = par_pid.get(r["m_PathID"]) if r.get("m_FileID", 0) == 0 else None
                if c is not None:
                    out[c.peek_name()] = c
    return out


def origine():
    src = backup.backup_path(TUILES)
    return UnityPy.load(src if os.path.exists(src) else TUILES)


def voulu_banc(tt_orig, retirer):
    tt = json.loads(json.dumps(tt_orig))
    if not retirer:
        for c in tt["<Configurations>k__BackingField"]:
            c["Type"] = 0
    return tt["<Configurations>k__BackingField"]


def voulu_place(comp_orig, ref_defaut, confs_defaut, retirer):
    """v2 (chez FM Guru, Grand ET Moyen, v1 vue : carrousel à points avec seulement Carte de passes + Banc) : place
    à PLUSIEURS descriptions = carrousel limité à elles (une disposition gardée par FM peut le masquer) ; une seule
    = ⌄ avec tous les choix.
    -> une seule description (Carte de passes), avec sa propre config à la taille de celle du banc ; Banc de touche
    reste au ⌄ (Type 0)"""
    descs = [dict(d) for d in comp_orig["m_configDescriptions"]]
    confs = json.loads(json.dumps(comp_orig["m_gridElementConfigs"]))
    if not retirer:
        descs = [dict(ref_defaut)]
        # taille de la place d'abord (comme Événements / xG à côté), sinon celle de la config du banc
        tailles = [{"x": comp_orig["m_location"]["width"], "y": comp_orig["m_location"]["height"]}] \
            + [c["Size"] for c in confs]
        choix = next((c for t in tailles for c in confs_defaut if c["Size"] == t), confs_defaut[0])
        confs = [json.loads(json.dumps(choix))]
    return descs, confs


def run(retirer):
    env, env_o = UnityPy.load(TUILES), origine()
    noms, noms_o = par_nom(env), par_nom(env_o)
    if BANC not in noms or BANC not in noms_o or DEFAUT not in noms:
        print("Banc de touche / carte de passes introuvables dans les tuiles du match (le jeu a changé ?), ignoré")
        return
    change = 0
    # 1. Banc de touche : configs en « tuile » (⌄ des choix communs)
    o = noms[BANC]
    tt = o.read_typetree()
    confs = voulu_banc(noms_o[BANC].read_typetree(), retirer)
    if tt["<Configurations>k__BackingField"] != confs:
        tt["<Configurations>k__BackingField"] = confs
        o.save_typetree(tt)
        change += 1
        print("Banc de touche : " + ("bloc d'origine (sans choix)" if retirer else "tuile à choix (⌄)"))
    else:
        print("Banc de touche : " + ("déjà d'origine" if retirer else "déjà tuile à choix"))
    # 2. place du banc : carte de passes domicile d'office
    ref = {"m_FileID": 0, "m_PathID": noms[DEFAUT].path_id}
    confs_defaut = noms_o[DEFAUT].read_typetree()["<Configurations>k__BackingField"]
    actuelles, orig = compositions(env, noms), compositions(env_o, noms_o)
    if not actuelles:
        print("compositions de l'écran de match introuvables (le jeu a changé ?), ignoré")
    for nom, c_o in sorted(actuelles.items()):
        if nom.endswith(SANS) or nom not in orig:
            continue
        tt = c_o.read_typetree()
        comp_o = {c["m_elementID"]: c for c in orig[nom].read_typetree()["m_gridComponents"]}
        if PLACE not in comp_o:
            continue
        for c in tt["m_gridComponents"]:
            if c["m_elementID"] != PLACE:
                continue
            descs, confs = voulu_place(comp_o[PLACE], ref, confs_defaut, retirer)
            if (c["m_configDescriptions"], c["m_gridElementConfigs"]) != (descs, confs):
                c["m_configDescriptions"], c["m_gridElementConfigs"] = descs, confs
                c_o.save_typetree(tt)
                change += 1
                print(f"{nom} : " + ("Banc de touche d'office" if retirer else
                                     "Carte de passes domicile d'office (Banc de touche au ⌄)"))
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
    noms = par_nom(UnityPy.load(TUILES))
    o = noms.get(BANC)
    if o is None:
        print("Banc de touche introuvable (le jeu a changé ?)")
        return
    types = {c["Type"] for c in o.read_typetree()["<Configurations>k__BackingField"]}
    print("Banc de touche :", "tuile à choix" if types == {0} else "d'origine (bloc)")
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
            print("tuile Banc de touche à choix : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
