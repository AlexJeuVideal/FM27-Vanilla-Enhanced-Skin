"""Dossier du jeu FM27 (celui qui contient fm.exe), commun à tous les scripts.

Gardé dans backups\\chemin_jeu.txt, demandé par Outils FM.bat au premier lancement (choix 107 pour le changer).
Sans fichier : premier chemin par défaut (PAR_DEFAUTS) qui existe.

Usage (Outils FM.bat) :
  chemin_jeu.py code                      -> chemin enregistré s'il est valide, sinon rien
  chemin_jeu.py detecter                  -> dossier trouvé (Steam, Epic, Xbox / Game Pass, Windows), sinon rien
  chemin_jeu.py enregistrer <fr|en> <dossier>   -> vérifie puis enregistre (code 1 si invalide)

Le nom du dossier ne compte pas : c'est fm_Data\\app.info qui dit que c'est FM27. Linux (v1.51) : FM27 lancé par
Proton (Steam), donc les mêmes fichiers que sous Windows ; dossiers de Steam pour Linux, et profil() = l'utilisateur
Windows du préfixe Proton (AppData, Documents de FM). Mac (2026-11-06, Steam) : le jeu est fm.app (bundles dans
fm.app/Contents/Resources/Data/StreamingAssets/aa/StandaloneOSX, app.info dans fm.app/Contents/Resources/Data), ses
données (vues, graphics, dispositions) dans ~/Library/Application Support/Sports Interactive/Football Manager 27,
ses logs dans ~/Library/Logs/Sports Interactive/Football Manager 27 : donnees_fm(), logs_fm().
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
BACKUP_DIR = os.environ.get("UIPICKER_BACKUPS") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backups")   # variable : banc d'essai (copies)
FICHIER = os.path.join(BACKUP_DIR, "chemin_jeu.txt")
WINDOWS = os.name == "nt"
MAC = sys.platform == "darwin"
_HOME = os.path.expanduser("~")
# Steam pour Linux : dossier normal, liens ~/.steam, Flatpak, Snap
STEAM_LINUX = [os.path.join(_HOME, ".local", "share", "Steam"), os.path.join(_HOME, ".steam", "steam"),
               os.path.join(_HOME, ".steam", "root"),
               os.path.join(_HOME, ".var", "app", "com.valvesoftware.Steam", ".local", "share", "Steam"),
               os.path.join(_HOME, "snap", "steam", "common", ".local", "share", "Steam")]
# Steam pour Mac : un seul dossier (bibliothèques en plus : libraryfolders.vdf)
STEAM_MAC = [os.path.join(_HOME, "Library", "Application Support", "Steam")]
STEAM = [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"] if WINDOWS else STEAM_MAC if MAC else STEAM_LINUX
PAR_DEFAUTS = [os.path.join(s, "steamapps", "common", "Football Manager 27") for s in STEAM]
# dossier des données Unity du jeu (app.info, StreamingAssets) et programme qui prouve que c'est le dossier du jeu
DONNEES_JEU = os.path.join("fm.app", "Contents", "Resources", "Data") if MAC else "fm_Data"
PROGRAMME = "fm.app" if MAC else "fm.exe"
SOUS_DOSSIER_AA = os.path.join(DONNEES_JEU, "StreamingAssets", "aa", "StandaloneOSX" if MAC else "StandaloneWindows64")
# textes de l'app (assistant, erreurs) : ce qui doit se trouver dans le dossier du jeu
CONTENU_JEU = "fm.app" if MAC else "fm.exe et fm_Data"
CONTENU_JEU_EN = "fm.app" if MAC else "fm.exe and fm_Data"
MARQUEUR_BUNDLE = "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle"


def nettoyer(chemin):
    """guillemets, espaces, fm.exe ou sous-dossier fm_Data collés au chemin -> dossier du jeu ; Mac : fm.app ou un
    dossier dedans (glissé depuis le Finder : « \\ » devant les espaces retirés)"""
    c = (chemin or "").strip().strip('"').strip("'").strip()
    if MAC:
        c = c.replace("\\ ", " ")
        if c.startswith("~"):
            c = os.path.expanduser(c)
    if c.lower().endswith("fm.exe"):
        c = os.path.dirname(c)
    m = re.search(r"[\\/]fm_data|/fm\.app(?:/|$)", c, re.I)
    if m:
        c = c[:m.start()]
    return c.rstrip("\\/")


def valide(chemin):
    """FM27 seulement : fm_Data\\app.info = « Football Manager 27 » (FM26 a aussi fm.exe / fm_Data) + bundle des
    modèles d'écran utilisé par les scripts"""
    programme = os.path.join(chemin or "", PROGRAMME)
    if not chemin or not (os.path.isdir(programme) if MAC else os.path.isfile(programme)):
        return False
    if not os.path.isfile(os.path.join(chemin, SOUS_DOSSIER_AA, MARQUEUR_BUNDLE)):
        return False
    try:
        with open(os.path.join(chemin, DONNEES_JEU, "app.info"), encoding="utf-8", errors="ignore") as f:
            return "football manager 27" in f.read().lower()
    except OSError:
        return True   # pas d'app.info : le bundle suffit


def lire():
    try:
        with open(FICHIER, encoding="utf-8") as f:
            c = nettoyer(f.read())
        if valide(c):
            return c
    except OSError:
        pass
    return next((c for c in PAR_DEFAUTS if valide(c)), "")


def _registre(cle, valeur, ruches=("HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE")):
    """valeur du registre Windows (texte) ou "" """
    try:
        import winreg
    except ImportError:   # pas Windows
        return ""
    for r in ruches:
        try:
            with winreg.OpenKey(getattr(winreg, r), cle) as k:
                v = winreg.QueryValueEx(k, valeur)[0]
                if isinstance(v, str) and v:
                    return os.path.normpath(v)
        except OSError:
            pass
    return ""


def _desinstallations():
    """dossiers d'install des programmes « Football Manager 27 » de Windows (Steam, Epic, autres)"""
    try:
        import winreg
    except ImportError:
        return []
    res = []
    for ruche, base in ((winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")):
        try:
            with winreg.OpenKey(ruche, base) as k:
                for i in range(winreg.QueryInfoKey(k)[0]):
                    try:
                        with winreg.OpenKey(k, winreg.EnumKey(k, i)) as s:
                            nom = str(winreg.QueryValueEx(s, "DisplayName")[0]).lower()
                            if "football manager 27" in nom:
                                res.append(str(winreg.QueryValueEx(s, "InstallLocation")[0]))
                    except OSError:
                        pass
        except OSError:
            pass
    return res


def _lecteurs():
    """lettres des disques présents (C:\\, D:\\…)"""
    return [f"{l}:\\" for l in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.isdir(f"{l}:\\")]


def _sous_dossiers(dossier):
    """sous-dossiers, ceux qui ressemblent à FM d'abord"""
    try:
        noms = os.listdir(dossier)
    except OSError:
        return []
    return [os.path.join(dossier, n) for n in
            sorted(noms, key=lambda n: ("football manager 27" not in n.lower(), n))]


def _steam():
    """steamapps\\common de chaque bibliothèque Steam (Steam trouvé par le registre, Program Files ou un disque)"""
    racines = [_registre(r"Software\Valve\Steam", "SteamPath"),
               _registre(r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath", ("HKEY_LOCAL_MACHINE",)),
               _registre(r"SOFTWARE\Valve\Steam", "InstallPath", ("HKEY_LOCAL_MACHINE",))] + STEAM
    for l in _lecteurs():
        racines += [l + r"Steam", l + r"SteamLibrary", l + r"Program Files (x86)\Steam", l + r"Program Files\Steam",
                    l + r"Games\Steam", l + r"Jeux\Steam"]
    biblios = []
    for s in racines:
        if not s:
            continue
        biblios.append(s)
        try:
            with open(os.path.join(s, "steamapps", "libraryfolders.vdf"), encoding="utf-8") as f:
                biblios += [p.replace("\\\\", "\\") for p in re.findall(r'"path"\s+"([^"]+)"', f.read())]
        except OSError:
            pass
    # Linux : ~/.steam/steam est un lien vers ~/.local/share/Steam -> realpath, une seule fois chaque bibliothèque
    return [os.path.join(b, "steamapps", "common") for b in dict.fromkeys(
        os.path.normcase(os.path.normpath(b if WINDOWS else os.path.realpath(b))) for b in biblios)]


def _epic():
    """dossiers d'install des jeux Epic (manifestes .item du lanceur Epic), FM d'abord"""
    dossier = os.path.join(os.environ.get("PROGRAMDATA") or r"C:\ProgramData",
                           r"Epic\EpicGamesLauncher\Data\Manifests")
    res = []
    try:
        noms = os.listdir(dossier)
    except OSError:
        noms = []
    for n in noms:
        if not n.lower().endswith(".item"):
            continue
        try:
            with open(os.path.join(dossier, n), encoding="utf-8", errors="ignore") as f:
                m = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(m, dict) and m.get("InstallLocation"):
            fm = "football manager" in str(m.get("DisplayName", "")).lower()
            res.append((not fm, os.path.normpath(m["InstallLocation"])))
    return [c for _, c in sorted(res)]


def candidats():
    """dossiers où FM27 peut être, du plus probable au moins probable"""
    yield from _desinstallations()
    for common in _steam():
        yield from _sous_dossiers(common)
    yield from _epic()
    for l in _lecteurs():
        for d in ("XboxGames", "Program Files\\Epic Games", "Epic Games", "Games", "Jeux",
                  "Program Files\\ModifiableWindowsApps"):
            yield from _sous_dossiers(l + d)
    if MAC:   # Epic (dossier partagé par défaut), Applications
        for d in ("/Users/Shared/Epic Games", "/Applications", os.path.join(_HOME, "Applications"),
                  os.path.join(_HOME, "Library", "Application Support", "Epic")):
            yield from _sous_dossiers(d)
    elif not WINDOWS:   # Heroic (Epic sous Linux), Lutris, dossier Games
        for d in (os.path.join("Games", "Heroic"), "Games", "Jeux"):
            yield from _sous_dossiers(os.path.join(_HOME, d))


def _steamapps_du_jeu(jeu):
    """dossier steamapps de la bibliothèque qui contient le jeu (<lib>/steamapps/common/<jeu>), sinon "" """
    common = os.path.dirname(os.path.normpath(jeu or ""))
    return os.path.dirname(common) if os.path.basename(common).lower() == "common" else ""


def prefixes_proton(jeu=None):
    """préfixes Proton (compatdata/<id>/pfx) où FM27 peut tourner, le plus probable d'abord : celui de l'id Steam
    du jeu (appmanifest_<id>.acf dont installdir = le dossier du jeu), puis tout préfixe qui a déjà un dossier
    LocalLow de FM 27 ; Mac : aucun (jeu natif)"""
    if MAC:
        return []
    jeu = jeu if jeu is not None else (os.environ.get("UIPICKER_JEU") or lire())
    bibs = [_steamapps_du_jeu(jeu)] + [os.path.dirname(c) for c in _steam()]
    bibs = [b for b in dict.fromkeys(os.path.realpath(b) for b in bibs if b) if os.path.isdir(b)]
    res = []
    nom = os.path.basename(os.path.normpath(jeu)) if jeu else ""
    for b in bibs:
        try:
            noms = os.listdir(b)
        except OSError:
            continue
        for n in noms:
            m = re.fullmatch(r"appmanifest_(\d+)\.acf", n)
            if not (m and nom):
                continue
            try:
                with open(os.path.join(b, n), encoding="utf-8", errors="ignore") as f:
                    if re.search(r'"installdir"\s+"' + re.escape(nom) + '"', f.read(), re.I):
                        res.append(os.path.join(b, "compatdata", m.group(1), "pfx"))
            except OSError:
                pass
    for b in bibs:
        for d in _sous_dossiers(os.path.join(b, "compatdata")):
            if os.path.isdir(os.path.join(d, "pfx", "drive_c", "users", "steamuser", "AppData", "LocalLow",
                                          "Sports Interactive", "Football Manager 27")):
                res.append(os.path.join(d, "pfx"))
    return [p for p in dict.fromkeys(res) if os.path.isdir(p)]


def profil():
    """dossier de l'utilisateur Windows vu par FM (AppData\\LocalLow, Documents) : le sien sous Windows ; sous Linux
    celui du préfixe Proton du jeu (pfx/drive_c/users/steamuser). Variable UIPICKER_PROFIL : banc d'essai"""
    if os.environ.get("UIPICKER_PROFIL"):
        return os.environ["UIPICKER_PROFIL"]
    if WINDOWS:
        return os.environ.get("USERPROFILE") or _HOME
    if MAC:   # jeu natif : pas de profil Windows (donnees_fm / logs_fm donnent ses dossiers)
        return _HOME
    for p in prefixes_proton():
        u = os.path.join(p, "drive_c", "users", "steamuser")
        if os.path.isdir(u):
            return u
    return _HOME   # FM jamais lancé : rien à trouver pour l'instant


def donnees_fm():
    """dossier des données de FM 27 (vues perso, CustomGridCompositions, Player.log sous Windows / Linux) :
    AppData\\LocalLow\\Sports Interactive\\Football Manager 27 ; Mac : ~/Library/Application Support/Sports
    Interactive/Football Manager 27 (le même dossier y contient aussi graphics)"""
    if MAC and not os.environ.get("UIPICKER_PROFIL"):
        return os.path.join(_HOME, "Library", "Application Support", "Sports Interactive", "Football Manager 27")
    return os.path.join(profil(), "AppData", "LocalLow", "Sports Interactive", "Football Manager 27")


def logs_fm():
    """dossier de Player.log de FM 27 : celui des données sauf sur Mac (~/Library/Logs/Sports Interactive/...)"""
    if MAC and not os.environ.get("UIPICKER_PROFIL"):
        return os.path.join(_HOME, "Library", "Logs", "Sports Interactive", "Football Manager 27")
    return donnees_fm()


def detecter():
    """premier dossier valide parmi Steam (toutes bibliothèques, tous disques), Epic, Xbox / Game Pass (dossier
    Content), et les programmes installés de Windows"""
    vus = set()
    for c in candidats():
        c = os.path.normpath(c) if c else ""
        for d in (c, os.path.join(c, "Content")):   # Xbox / Game Pass : <jeu>\Content\fm.exe
            if d and os.path.normcase(d) not in vus:
                vus.add(os.path.normcase(d))
                if valide(d):
                    return d
    return ""


GAME = os.environ.get("UIPICKER_JEU") or lire()   # variable : banc d'essai (faux dossier du jeu)
AA = os.path.join(GAME, SOUS_DOSSIER_AA)


def main(argv):
    op = argv[0] if argv else ""
    if op == "code":
        print(GAME if valide(GAME) and os.path.exists(FICHIER) else "")
    elif op == "detecter":
        print(detecter())
    elif op == "enregistrer" and len(argv) >= 2:
        en = argv[1] != "fr"
        c = nettoyer(" ".join(argv[2:]))
        if not valide(c):
            print((f"Dossier invalide : il faut le dossier de FM27 qui contient {CONTENU_JEU}. " if not en else
                   f"Invalid folder: it must be the FM27 folder containing {CONTENU_JEU_EN}. ") + f"({c or '-'})")
            sys.exit(1)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(FICHIER, "w", encoding="utf-8") as f:
            f.write(c)
        print(("Dossier du jeu enregistré : " if not en else "Game folder saved: ") + c)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
