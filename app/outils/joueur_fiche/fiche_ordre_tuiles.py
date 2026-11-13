"""Fiche joueur > Vue d'ensemble : ordre des tuiles du bas (2026-11-12, demande du joueur).

Ordre voulu : État d'esprit, Condition physique, Stats saison, Stats carrière, Forme, Entraînement (v10 : la place
Entraînement montre d'office l'Historique des blessures de FM, Entraînement reste au choix dans le ⌄). Rien d'autre ne
change : chaque tuile garde la largeur, la hauteur et les tailles mini / maxi de FM, seules les colonnes (x) sont
recalculées. Toutes les compositions de PlayerReportOverviewCompositionSet (Standard, Small, Large, Large-FMC ; pas
Entraînement en Small / Large-FMC : ordre des autres) ; Phone_Landscape n'a que le bloc du haut.
(Ancien essai essai_fiche_bas_bloc v5-v8 : même ordre + tailles fixes et bloc unique, mis de côté.)

Mode FM Guru (option fiche_fmguru = guru, 2026-11-07) : ordre de FM gardé et Efficacité tactique d'office à la place
2x2 d'Entraînement (Entraînement reste au choix dans le ⌄).

Toujours calculé à partir des valeurs d'origine (sauvegarde) : relancer ne cumule rien.
Une disposition de la page gardée par la partie (tuile changée au ⌄) passe avant.

Usage (jeu fermé) : fiche_ordre_tuiles.py appliquer [--dry-run] | retirer | etat | si-actif
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
ORDRE = ["Happiness", "FItness", "PlayerSeasonStats", "CareerStats", "PlayerForm", "PlayerTrainingOverview"]
# mode FM Guru (2026-11-07, maquette de l'ami du joueur) : ordre de FM gardé (État d'esprit, Condition, Forme,
# [Entraînement], Stats saison, Stats carrière) et la place 2x2 d'Entraînement montre d'office l'Efficacité tactique
# (Entraînement reste au choix dans le ⌄ de la tuile)
# v2 (2026-11-07, le joueur, capture en Small : vide à droite de la rangée du bas) : colonnes ajoutées à une tuile
# de la rangée, par composition (les suivantes se décalent d'autant)
# v3 (le joueur : « stats carrière un peu plus large, le reste décalé à droite pour combler ») : Carrière au lieu de
# Saison
# v4 : annulé : la capture était la composition Standard (16 col., pleine) avec une disposition gardée par la partie
# (Carrière en 2x2 au ⌄) ; Small est pleine aussi (12 col.) : +1 la faisait déborder
ELARGIR = {}
# v5 (le joueur, texte Small : composition Standard, Stats carrière affichée sur 2 colonnes + 1 colonne vide au bout ;
# « agrandis stats carrière, décale les 2 à droite ») : hypothèse = 15 colonnes en Small, la rangée de 16 ne tient
# pas et FM réduit Stats carrière -> largeur imposée (et mini) 3 : rangée de 15
# v6 (2026-11-07, le joueur, Large 2000 px : toujours 1 colonne vide au bout ; « Stats saison plus large, le reste
# collé au bord droit ») : v5 sans effet car FM n'a que des tailles 2 / 4 / 8 (Carrière 3 sans config 3x2 -> repliée
# en 2). Grille mesurée sur capture = 15 colonnes : Saison 5 (config 5x2 posée dans la composition, modèle 4x2 de FM
# étiré) + Carrière 2x2 (modèle 2x2 de FM, retouché par tuile_carriere) : 2+2+5+2+2+2 = 15.
# {composition: {tuile: (largeur, GUID du modèle)}} : place, mini / maxi et config de la tuile = cette largeur
# v7 (vu en jeu : v6 sans effet) : l'affichage Large du joueur = composition Large (20 col. prévues : Saison 8 +
# Carrière 4) dans une grille de 15 : FM replie Saison 8 -> 4 et Carrière 4 -> 2, d'où 14 + 1 vide. Même rangée de 15.
# v8 (vu en jeu, texte Small : rangée décalée mais Saison / Carrière rétrécies) : mesuré sur capture, la grille Large
# fait 30 col. (~51 px + 14) ; les tuiles à maxi 4 (État d'esprit, Condition, Forme, Entraînement) s'étirent seules
# de 2 à 4 ; FM de base = 4+4+8+4+4+4 = 28 + 2 vides. -> Saison 10 (mini 8 de FM gardé : grille plus étroite = repli
# sur 8, maxi 10), configs de FM gardées, Carrière d'origine : 4+4+10+4+4+4 = 30. Standard : d'origine (pas vue).
# {composition: {tuile: (largeur, mini, maxi)}}
# place 8 (rangée de 20 comme FM), maxi 10 : s'étire comme les tuiles 2 -> 4 quand la grille a la place
TAILLES = {"PlayerReportOverviewComposition-Large": {"PlayerSeasonStats": (8, 8, 10)}}
LARGEUR = {c: {k: w for k, (w, _, _) in t.items()} for c, t in TAILLES.items()}
SLOT_ENTRAINEMENT = "PlayerTrainingOverview"
GUID_EFFICACITE_2X2 = "d0a61cef5fce9e640bd4623e58da0cdc"   # TacticalEffectivenessTile_2x2
# v9 (2026-11-13, le joueur : « Entraînement fait doublon avec Progression en haut ») : essai, seulement par le .bat
# 124 (argument --blessures, pas d'option dans l'app) -> la tuile Historique des blessures de FM (celle de Condition
# physique, 4x2 : % manqué, temps total, dernière blessure ; clic = historique complet, version IA pour les autres
# équipes) choisie d'office à la place d'Entraînement (Entraînement reste au ⌄). Pas en mode Guru. Un passage sans
# l'argument (choix 1, app) remet Entraînement.
# v10 (2026-11-13, validé en jeu Medium + Small, le joueur : « ajoute-la globalement à nos tuiles, laisse
# l'entraînement sous la tuile comme ça ») : Historique des blessures d'office (hors mode Guru), plus d'argument ;
# Entraînement reste dans le ⌄ de la tuile. Liste de toutes les blessures dedans : joueur_fiche\tuile_blessures.
# v11 (2026-11-13, le joueur, vu en jeu : « parfait sur les autres joueurs, mets historique blessures SOUS
# éligibilité ») : Statut formé au club (= « Éligibilité », montré par FM aux joueurs des autres clubs : PlayerReport,
# visibilité player.ReportMode != 0 et != 2) remis AVANT les Blessures -> autres clubs : Éligibilité de base,
# Blessures au ⌄ ; tes joueurs (ReportMode 0 : Éligibilité cachée) : Blessures de base.
DESC_ELIGIBILITE = "PlayerHomegrownStatusTileDescription"
DESC_BLESSURES = "InjuryHistoryTileDescription"
GUID_BLESSURES = "67103b067801d3c4f824e737a8cb0f1e"        # InjuryHistoryTile_4x2
# =====================================================================================================

TUILES = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
ENSEMBLE = "PlayerReportOverviewCompositionSet"
JEU_TUILES = "PlayerReportOverviewTileSet"
MARKER = os.path.join(backup.BACKUP_DIR, "fiche_ordre_tuiles.actif")
DRY_RUN = "--dry-run" in sys.argv


def ordre():
    """ordre voulu : celui choisi dans l'app (glisser-déposer, options.ordre_tuiles) s'il range exactement les mêmes
    tuiles, sinon ORDRE (2026-11-11, le joueur)"""
    import options
    perso = options.ordre_tuiles()
    return perso if perso and sorted(perso) == sorted(ORDRE) else ORDRE


def guru():
    import options
    return options.get("fiche_fmguru") == "guru"


def description_efficacite(env):
    """référence (m_FileID, m_PathID) de la description Efficacité tactique : la seule du jeu de tuiles de la fiche
    qui est dans un autre fichier (les 12 autres sont dans ce bundle) ; None si introuvable / ambiguë"""
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != JEU_TUILES:
                continue
        except Exception:
            continue
        ext = [d for d in o.read_typetree().get("m_gridElementDescriptions", []) if d.get("m_FileID", 0) != 0]
        return dict(ext[0]) if len(ext) == 1 else None
    return None


def description_blessures(env, nom=DESC_BLESSURES):
    """référence (m_FileID 0, m_PathID) d'une description du même bundle (Historique des blessures par défaut) ; None
    si introuvable"""
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == nom:
                return {"m_FileID": 0, "m_PathID": o.path_id}
        except Exception:
            continue
    return None


def jeu_tuiles(env):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == JEU_TUILES:
                return o
        except Exception:
            continue
    return None


def configs_voulues(orig_c, loc, eff, bles=None, elig=None):
    """(m_configDescriptions, m_gridElementConfigs) de la place Entraînement : celles de FM, avec (mode Guru, place
    2x2) l'Efficacité tactique en premier = choisie d'office ; v9 (option fiche_blessures) : l'Historique des
    blessures en premier, à la taille de la place (2x2, étirée à 4 en Large)"""
    descs = [dict(d) for d in orig_c["m_configDescriptions"]]
    confs = json.loads(json.dumps(orig_c["m_gridElementConfigs"]))
    if bles is not None:
        descs.insert(0, dict(bles))
        confs.insert(0, {"Description": dict(bles), "Size": {"x": loc["width"], "y": loc["height"]},
                         "Asset": {"m_FileID": 0, "m_PathID": 0},
                         "AssetRef": {"m_AssetGUID": GUID_BLESSURES, "m_SubObjectName": "", "m_SubObjectType": ""},
                         "Type": 0})
        # v11 : Éligibilité (description + ses configs, ordre de FM gardé entre elles) remise devant les Blessures
        if elig is not None and elig in descs:
            descs = [d for d in descs if d == elig] + [d for d in descs if d != elig]
            confs = [c for c in confs if c["Description"] == elig] + [c for c in confs if c["Description"] != elig]
    elif eff is not None and (loc["width"], loc["height"]) == (2, 2):
        descs.insert(0, dict(eff))
        confs.insert(0, {"Description": dict(eff), "Size": {"x": 2, "y": 2},
                         "Asset": {"m_FileID": 0, "m_PathID": 0},
                         "AssetRef": {"m_AssetGUID": GUID_EFFICACITE_2X2, "m_SubObjectName": "",
                                      "m_SubObjectType": ""}, "Type": 0})
    return descs, confs


def compositions(env):
    """{nom: (objet, typetree)} des compositions de l'ensemble de la Vue d'ensemble"""
    objs = {o.path_id: o for o in env.objects}
    ens = None
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() == ENSEMBLE:
                ens = o.read_typetree()
                break
        except Exception:
            continue
    out = {}
    for e in (ens or {}).get("m_gridBreakpointCompositionData", {}).get("m_values", []):
        for r in e["m_value"]:
            if r["m_FileID"] == 0 and r["m_PathID"] in objs:
                o = objs[r["m_PathID"]]
                tt = o.read_typetree()
                out[tt["m_Name"]] = (o, tt)
    return out


def origine():
    """compositions d'origine (sauvegarde si le bundle a déjà été modifié)"""
    src = backup.backup_path(TUILES)
    return compositions(UnityPy.load(src if os.path.exists(src) else TUILES))


def places(tt):
    """{tuile: location}"""
    return {c["m_elementID"]: dict(c["m_location"]) for c in tt["m_gridComponents"]}


def voulu(orig_tt):
    """{tuile: location} : tuiles de la rangée du bas dans l'ORDRE, mêmes largeurs (+ ELARGIR), à partir de la 1re
    colonne de la rangée ; None si la rangée n'a pas la forme attendue (une seule rangée, rien d'autre que ORDRE)"""
    plus = ELARGIR.get(orig_tt.get("m_Name"), {})
    fixe = LARGEUR.get(orig_tt.get("m_Name"), {})
    p = places(orig_tt)
    bas = [k for k in p if k in ORDRE]
    if len(bas) < 2 or set(p) - set(ORDRE) - {k for k, l in p.items() if l["y"] == 0}:
        return None
    ys = {p[k]["y"] for k in bas}
    if len(ys) != 1:
        return None
    x = min(p[k]["x"] for k in bas)
    out = {}
    voulu_ordre = ordre()
    for k in sorted(bas, key=voulu_ordre.index):
        l = dict(p[k])
        l["x"] = x
        l["width"] = fixe.get(k, l["width"] + plus.get(k, 0))
        x += l["width"]
        out[k] = l
    return out


def run(retirer):
    env = UnityPy.load(TUILES)
    actuels, orig = compositions(env), origine()
    if not actuels:
        print(f"{ENSEMBLE} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    change = 0
    g = guru() and not retirer
    eff = description_efficacite(env) if g else None
    if g:
        print("mode FM Guru : ordre de FM, Efficacité tactique à la place d'Entraînement" if eff else
              "mode FM Guru : Efficacité tactique introuvable dans le jeu de tuiles (le jeu a changé ?), ordre de FM seul")
    bles = description_blessures(env) if not retirer and not g else None
    if not retirer and not g:
        print("Historique des blessures à la place d'Entraînement (Entraînement au ⌄)" if bles else
              "Historique des blessures introuvable (le jeu a changé ?), Entraînement gardé")
    elig = description_blessures(env, DESC_ELIGIBILITE) if bles is not None else None
    if bles is not None and elig is None:
        print("Éligibilité (statut formé au club) introuvable (le jeu a changé ?) : Blessures aussi pour les autres clubs")
    # v9 : jeu de tuiles de la page = celui de FM (+ Historique des blessures si choisi : dans le ⌄ aussi)
    js = jeu_tuiles(env)
    src = backup.backup_path(TUILES)
    js_orig = jeu_tuiles(UnityPy.load(src if os.path.exists(src) else TUILES))
    if js is not None and js_orig is not None:
        tt_js = js.read_typetree()
        voulu_js = [dict(d) for d in js_orig.read_typetree()["m_gridElementDescriptions"]]
        if bles is not None and bles not in voulu_js:
            voulu_js.append(dict(bles))
        if tt_js["m_gridElementDescriptions"] != voulu_js:
            tt_js["m_gridElementDescriptions"] = voulu_js
            js.save_typetree(tt_js)
            change += 1
            print(f"{JEU_TUILES} : " + ("+ Historique des blessures" if bles else "d'origine"))
    for nom, (o, tt) in actuels.items():
        if nom not in orig or len(orig[nom][1]["m_gridComponents"]) < 2:   # Phone_Landscape : bloc du haut seul
            continue
        cible = places(orig[nom][1]) if retirer or g else voulu(orig[nom][1])
        if cible is None:
            print(f"{nom} : disposition inattendue (le jeu a changé ?), ignorée")
            continue
        fait = []
        orig_comp = {c["m_elementID"]: c for c in orig[nom][1]["m_gridComponents"]}
        for c in tt["m_gridComponents"]:
            l = cible.get(c["m_elementID"])
            if l is not None and c["m_location"] != l:
                c["m_location"].update(l)
                fait.append(c["m_elementID"])
            # v5 : mini (et maxi) de largeur suivent une largeur imposée ; remis d'origine sinon
            o_c = orig_comp.get(c["m_elementID"])
            if o_c is not None:
                t = None if (retirer or g) else TAILLES.get(nom, {}).get(c["m_elementID"])
                mini = t[1] if t is not None else o_c["m_minSize"]["x"]
                maxi = t[2] if t is not None else o_c["m_maxSize"]["x"]
                if (c["m_minSize"]["x"], c["m_maxSize"]["x"]) != (mini, maxi):
                    c["m_minSize"]["x"], c["m_maxSize"]["x"] = mini, maxi
                    fait.append(c["m_elementID"] + " (taille)")
                # v8 : configs de FM (remet celles changées par v6 / v7)
                confs = json.loads(json.dumps(o_c["m_gridElementConfigs"]))
                if c["m_elementID"] != SLOT_ENTRAINEMENT and c["m_gridElementConfigs"] != confs:
                    c["m_gridElementConfigs"] = confs
                    fait.append(c["m_elementID"] + " (config)")
            if c["m_elementID"] == SLOT_ENTRAINEMENT and c["m_elementID"] in orig_comp:
                descs, confs = configs_voulues(orig_comp[c["m_elementID"]], c["m_location"], eff, bles, elig)
                if c["m_configDescriptions"] != descs or c["m_gridElementConfigs"] != confs:
                    c["m_configDescriptions"], c["m_gridElementConfigs"] = descs, confs
                    fait.append(c["m_elementID"] + (" (Historique des blessures)" if bles else
                                                    " (Efficacité tactique)" if eff else " (d'origine)"))
        if fait:
            o.save_typetree(tt)
            change += 1
            rangee = sorted((k for k in cible if k in ORDRE), key=lambda k: cible[k]["x"])
            print(f"{nom} : " + " | ".join(rangee))
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
    for nom, (_, tt) in actuels.items():
        if nom not in orig or len(orig[nom][1]["m_gridComponents"]) < 2:
            continue
        p, v = places(tt), voulu(orig[nom][1])
        etat = "appliqué" if v and all(p.get(k) == l for k, l in v.items()) else \
            ("d'origine" if p == places(orig[nom][1]) else "autre disposition")
        print(f"{nom} : {etat}")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a not in ("--dry-run", "--blessures")]   # --blessures : ancien essai (v9), sans effet
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
            print("ordre des tuiles de la fiche : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
