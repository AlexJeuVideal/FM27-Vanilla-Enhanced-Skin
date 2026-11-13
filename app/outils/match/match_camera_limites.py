"""Match : limites de la Hauteur et du Zoom de la caméra élargies, par mode de caméra (curseurs ET molette).

FM range les limites de chaque mode dans ses données : MonoBehaviours `<Mode>CameraModeData` de
match-assets_assets_all.bundle (m_enableCameraHeight / m_cameraHeightMin / Max / Step, idem Zoom). Le menu Caméra
(settings.MatchCameraHeightMin...) et la molette les lisent. Ici : min / max de LIMITES pour chaque mode réglé dans
MODES, et activation de la hauteur / du zoom là où FM les coupe (Caméras TV). Seul écrivain de ce bundle.

v1-v3 changeaient le curseur du menu (CameraBlock) : la molette restait 0-10 ; ces changements sont retirés.

Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from notes_installations import decode_args, encode_args  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
LIMITES = (-60, 60, 1)   # min, max, pas (FM : 0, 10, 1) ; v9 : -60..60 (le joueur)
# modes réglés : nom de l'objet -> (hauteur, zoom) ; True = activé avec LIMITES, False = laissé comme FM
MODES = {
    "TacticalCameraModeData": (True, True),          # Tactique
    "AerialCameraModeData": (True, True),            # Aérienne
    "VerticalScrollingCameraModeData": (True, True),  # Défilement vertical
    "BehindGoalCameraModeData": (True, False),       # Derrière le but (zoom coupé par FM)
    "DynamicSidelineCameraModeData": (True, False),  # Ligne de touche dynamique (zoom coupé par FM)
    "2DCameraModeData": (False, True),               # 2D classique (zoom seul)
    "BroadcastCameraModeData": (True, False),        # Caméras TV : coupé par FM ; hauteur activée (marche en jeu),
                                                     # zoom laissé coupé (v4 : curseur sans effet en jeu)
}
# =====================================================================================================

VERSION = 9   # v9 : -60..60 ; v8 : -40..40 ; v7 : -30..30 ; v6 : minimum -30 ; v1 : curseur 0-20 ; v2 : min -1 ; v3 : -20..20 par variables du menu (molette restée 0-10) ;
              # v4 : limites dans les données des modes de caméra (curseur + molette), Caméras TV activée ;
              # v5 : Caméras TV, zoom recoupé (sans effet en jeu), hauteur gardée
BUNDLE = "match-assets_assets_all.bundle"
CHAMPS = {"hauteur": ("m_enableCameraHeight", "m_cameraHeightMin", "m_cameraHeightMax", "m_cameraHeightStep"),
          "zoom": ("m_enableCameraZoom", "m_cameraZoomMin", "m_cameraZoomMax", "m_cameraZoomStep")}
# valeurs de FM (pour retirer) : objet -> {champ: valeur}
FM = {}
for _m in MODES:
    FM[_m] = {}
for _m, (_h, _z) in {"TacticalCameraModeData": (1, 1), "AerialCameraModeData": (1, 1),
                     "VerticalScrollingCameraModeData": (1, 1), "BehindGoalCameraModeData": (1, 0),
                     "DynamicSidelineCameraModeData": (1, 0), "2DCameraModeData": (0, 1),
                     "BroadcastCameraModeData": (0, 0)}.items():
    for _k, _on in (("hauteur", _h), ("zoom", _z)):
        e, mi, ma, st = CHAMPS[_k]
        FM[_m].update({e: _on, mi: 0, ma: 10 if _on else 0, st: 1 if _on else 0})
MARKER = os.path.join(backup.BACKUP_DIR, "match_camera_limites.actif")

# --- anciennes versions (v1-v3) : curseur du menu CameraBlock, remis comme FM ---
MODELE_MENU = "CameraBlock"
FONCTION_CURSEUR = "8810e03b9bbaba0418a30670d8ea838e"
TYPE_CHEMIN = b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"
PREFIXE_VAR = "uipcam"
CLASSES_VAR = ("BindingVariablesComponent/UxmlSerializedData", "BindingVariables/UxmlSerializedData")


def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _chemin(val):
    return val[2:2 + val[1]].decode("ascii", "replace") if len(val) > 2 and val[0] == 1 else None


def nettoyer_menu():
    """retire les changements v1-v3 du curseur (chemins settings.MatchCamera… remis, variables uipcam* retirées)"""
    bundle, obj, tt = nb.find_vta(MODELE_MENU)
    if tt is None:
        return []
    msgs = []
    for r in tt["references"]["RefIds"]:
        if (r.get("type") or {}).get("class") in CLASSES_VAR:
            vv = r["data"].get("ValueVariables") or []
            garde = [v for v in vv if not v["m_name"].startswith(PREFIXE_VAR)]
            if garde != vv:
                r["data"]["ValueVariables"] = garde
                msgs.append("variables du menu retirées")

    def walk(x):
        if isinstance(x, dict):
            f = x.get("InitialiseBindingFunc")
            if isinstance(f, dict) and (f.get("m_target") or {}).get("m_guid") == FONCTION_CURSEUR:
                args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                pas = _chemin(args[2][1]) if len(args) == 3 else None
                if pas and pas.startswith("settings.MatchCamera") and pas.endswith("Step"):
                    change = False
                    for i, bout in ((0, "Min"), (1, "Max")):
                        fm = pas[:-4] + bout
                        if _chemin(args[i][1]) != fm:
                            p = fm.encode()
                            args[i][1] = b"\x01" + _varint(len(p)) + p
                            change = True
                    if change:
                        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
                        msgs.append(f"curseur du menu remis ({pas[len('settings.MatchCamera'):-4]})")
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(tt)
    if msgs:
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    return msgs


def modes():
    """[(nom, objet, typetree)] des données de modes de caméra de MODES"""
    p = os.path.join(nb.AA, BUNDLE)
    out = []
    for o in nb.env_of(p).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            nom = o.peek_name()
        except Exception:
            continue
        if nom in MODES:
            out.append((nom, o, o.read_typetree()))
    return p, out


def voulues(nom, avec):
    if not avec:
        return FM[nom]
    v = dict(FM[nom])
    for k, actif in zip(("hauteur", "zoom"), MODES[nom]):
        if actif:
            e, mi, ma, st = CHAMPS[k]
            v.update({e: 1, mi: LIMITES[0], ma: LIMITES[1], st: LIMITES[2]})
    return v


def regler(avec):
    p, liste = modes()
    msgs = []
    manquants = [m for m in MODES if m not in [n for n, _, _ in liste]]
    if manquants:
        msgs.append(f"modes introuvables : {', '.join(manquants)}")
    for nom, o, tt in liste:
        v = voulues(nom, avec)
        if any(c not in tt for c in v):
            msgs.append(f"{nom} : champs introuvables (mise à jour du jeu ?), laissé")
            continue
        diff = {c: x for c, x in v.items() if tt[c] != x}
        if not diff:
            continue
        tt.update(diff)
        o.save_typetree(tt)
        nb._dirty.add(p)
        h = "hauteur %s..%s" % (tt[CHAMPS["hauteur"][1]], tt[CHAMPS["hauteur"][2]]) if tt[CHAMPS["hauteur"][0]] else "hauteur coupée"
        z = "zoom %s..%s" % (tt[CHAMPS["zoom"][1]], tt[CHAMPS["zoom"][2]]) if tt[CHAMPS["zoom"][0]] else "zoom coupé"
        msgs.append(f"{nom[:-len('CameraModeData')]} : {h}, {z}")
    return msgs


def cmd(avec):
    if not avec and os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    msgs = regler(avec) + nettoyer_menu()
    for m in msgs or (["déjà appliqué"] if avec else ["rien à retirer"]):
        print(f"caméra : {m}")
    nb.save_all()
    if avec and not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True, "version": VERSION}, f)


def cmd_etat():
    _, liste = modes()
    for nom, _, tt in liste:
        print(nom, {c: tt[c] for k in CHAMPS.values() for c in k})
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
            print("limites de la caméra : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
