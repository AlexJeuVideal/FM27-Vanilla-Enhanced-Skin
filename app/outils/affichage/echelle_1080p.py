"""Affichages Moyen / Petit de FM en 1080p (et sous la 2K) : patch de GameAssembly.dll. FACULTATIF, à ses risques.

FM grise Moyen / Petit sous la 2K et ne réduit jamais l'interface sous sa taille naturelle (écran / résolution de
référence). Deux endroits du code de FM (GameAssembly.dll), trouvés le 2026-11-12 (FM 27.0.1) :
- AdaptiveLayoutsDataHandler.UpdateScreenScaling (FM.UI, token 0x06000467) : MediumOptionAvailable /
  SmallOptionAvailable = (échelle voulue - 1.0) > écart du mode (m_maxScaleSettings : Medium 0.25, Small 0.5), sinon
  retour à Large. Les deux `comiss xmm7, xmm9|8 ; seta dl` -> `mov dl, 1 ; nop5` : toujours permis (le test « mise en
  page adaptative active » juste avant est gardé).
- FMDocumentManager (calcul de la résolution de référence, RVA 0x842ec0) : taille = naturelle / (1 + écart du mode),
  appliquée seulement si naturelle > 1 + écart (`comiss xmm8,[rdi] ; jae`). `comiss` -> `stc ; nop3` : toujours
  appliquée. Grand (écart 0) ne change nulle part ; en 1080p : Moyen 80 %, Petit 67 %.
Chaque patch est trouvé par motif d'octets (unique), jamais par adresse : autre version de FM = « pas reconnu », rien
écrit. Retrait = octets d'origine remis (exact). Copie de l'original : backups\\GameAssembly.dll.original.
Pas fait pour Mac (autre binaire) ; Linux : même DLL (Proton).
Historique (essai_echelle_1080p, 2026-11-10 / 12) : v1 boutons seuls, v2 écarts de la scène à 0 (= taille de Grand),
v4 limite 1 - écart (interface 2x plus grande) : abandonnés ; v5 = cette fonction (validée en jeu le 2026-11-12).

Pas d'interrupteur actif = patch retiré au choix 1 (si-actif) ; « Désinstaller tout » : retirer (hors_jeu).
Usage (FM fermé) : echelle_1080p.py appliquer | retirer | etat | si-actif [--dry-run]
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
from chemin_jeu import GAME, MAC, BACKUP_DIR  # noqa: E402

DRY_RUN = "--dry-run" in sys.argv
DLL = os.path.join(GAME, "GameAssembly.dll")
SAUVEGARDE_DLL = os.path.join(BACKUP_DIR, "GameAssembly.dll.original")
MARKER = os.path.join(BACKUP_DIR, "echelle_1080p.actif")

MOV_DL_1 = b"\xb2\x01\x0f\x1f\x44\x00\x00"   # mov dl, 1 ; nop5
STC_NOP3 = b"\xf9\x0f\x1f\x00"               # stc ; nop dword [rax]
# (nom, octets d'origine, octets patchés, contexte avant (largeur fixe) ou b"", suite obligatoire)
PATCHS = [
    ("Moyen permis", b"\x41\x0f\x2f\xf9\x0f\x97\xc2", MOV_DL_1, b"", rb"\x4c\x8b\x05....\x48\x8d\x4f\x60"),
    ("Petit permis", b"\x41\x0f\x2f\xf8\x0f\x97\xc2", MOV_DL_1, b"", rb"\x4c\x8b\x05....\x48\x8d\x4f\x70"),
    ("taille", b"\x44\x0f\x2f\x07", STC_NOP3, rb"(?<=\xf3\x44\x0f\x58\x05....)", rb"\x0f\x83"),
]


def _trouve(data, orig, patch, avant, suite):
    """(position, patché ?) ; None si absent ou pas unique"""
    t = []
    for octets, patche in ((orig, False), (patch, True)):
        t += [(m.start(), patche) for m in re.finditer(avant + re.escape(octets) + b"(?=" + suite + b")", data, re.S)]
    return t[0] if len(t) == 1 else None


def lire_etat(data):
    """{nom: patché ?} ; None si le code n'est pas reconnu (autre version de FM)"""
    out = {}
    for nom, orig, patch, avant, suite in PATCHS:
        t = _trouve(data, orig, patch, avant, suite)
        if t is None:
            return None
        out[nom] = t[1]
    return out


def changer(patcher, discret=False):
    """discret : choix 1 avec la fonction coupée (tout le monde) : pas d'erreur si le code n'est pas reconnu"""
    if MAC:
        print("Mac : pas fait pour Mac, rien à faire")
        return
    if not os.path.exists(DLL):
        if discret:
            return
        sys.exit("GameAssembly.dll introuvable")
    data = bytearray(open(DLL, "rb").read())
    msgs = []
    for nom, orig, patch, avant, suite in PATCHS:
        t = _trouve(data, orig, patch, avant, suite)
        if t is None:
            if discret:
                print("affichages Moyen / Petit en 1080p : non activés, rien à faire")
                return
            sys.exit("GameAssembly.dll : code d'échelle pas reconnu (mise à jour de FM ?), rien n'est écrit")
        p, patche = t
        if patche == patcher:
            continue
        neuf = patch if patcher else orig
        data[p:p + len(neuf)] = neuf
        msgs.append(f"GameAssembly.dll : {nom} {'patché' if patcher else 'remis comme FM'} (0x{p:x})")
    if not msgs:
        print("affichages Moyen / Petit en 1080p : non activés, rien à faire" if discret else
              "GameAssembly.dll : déjà " + ("patché" if patcher else "d'origine") + ", rien à faire")
        return
    print("\n".join(msgs))
    if DRY_RUN:
        print(f"(essai à blanc : rien écrit, GameAssembly.dll ferait {len(data) / 1e6:.2f} Mo)")
        return
    if patcher and not os.path.exists(SAUVEGARDE_DLL):
        etat = lire_etat(open(DLL, "rb").read())
        if etat and not any(etat.values()):   # copie de l'original seulement s'il n'a aucun patch
            os.makedirs(BACKUP_DIR, exist_ok=True)
            shutil.copy2(DLL, SAUVEGARDE_DLL)
            print(f"original sauvegardé : {SAUVEGARDE_DLL}")
    try:
        f = open(DLL, "r+b")
    except PermissionError:
        sys.exit("GameAssembly.dll verrouillé : ferme FM puis recommence")
    with f:
        f.write(data)
        f.truncate()
        f.flush()
        os.fsync(f.fileno())
    print(f"écrit : {DLL}")


def cmd_appliquer():
    changer(True)
    if not DRY_RUN and not MAC:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not DRY_RUN:
        os.remove(MARKER)
    changer(False)


def cmd_etat():
    if MAC or not os.path.exists(DLL):
        print("GameAssembly.dll absent (Mac ?)")
        return
    etat = lire_etat(open(DLL, "rb").read())
    if etat is None:
        print("code d'échelle pas reconnu (mise à jour de FM ?)")
    for n, v in (etat or {}).items():
        print(f"{n} : " + ("patché" if v else "d'origine"))
    print("activée :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
        else:   # pas activée : un patch resté (ancien essai, retrait raté) est enlevé
            changer(False, discret=True)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
