"""Application du skin : tout le skin dans une fenêtre, installation comprise (assistant en étapes).

Dossier de partage : seule interface (lanceur « Lancer - Launch.bat », sans Outils FM.bat). UI PICKER : choix 600 de
Outils FM.bat.

Petit serveur local (127.0.0.1, bibliothèque standard de Python seulement : il démarre avec le Python de Windows
AVANT que les modules des outils existent) + page.html. Assistant au 1er lancement : langue, modules Python (.venv,
UnityPy + Pillow), dossier du jeu, couleur du fond (facultatif), installation du skin. Ensuite : la même chose que le
menu (fonctions par endroit du jeu, options, fond, statut), en lançant les MÊMES scripts (.venv, un à la fois,
journal en direct). Fenêtre : Edge / Chrome / Brave / Vivaldi en mode application (NAVIGATEURS_APP), sinon le
navigateur par défaut. Arrêt : bouton
Quitter, ou ARRET_SANS_PAGE secondes sans nouvelle de la page.

Mise à jour de l'app (commun\\mise_a_jour.py, en sommeil tant que son DEPOT est vide) : vérifiée au lancement, bandeau
sur l'accueil ; installée par une tâche, puis l'app redémarre sur le même port (--port) et la page se recharge.

Usage : serveur.py [--sans-fenetre] [--port N]
"""
import codecs
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import catalogue as cat  # noqa: E402
import lancer  # noqa: E402
import options  # noqa: E402
import langue  # noqa: E402
import chemin_jeu  # noqa: E402
import stades_photos  # noqa: E402
import trophees_photos  # noqa: E402  (salle des trophées : images, même dossier graphics que les stades)
import packs_graphics  # noqa: E402  (logos / visages d'autres sites : décompressés et rangés dans graphics)
import noms_reels  # noqa: E402  (vrais noms : fix de FM SCOUT, pas un travail du skin ; leur zip, jamais livré)
import sigles_clubs  # noqa: E402  (sigles à 3 lettres des clubs dans toutes les langues : .lnc du skin)
import mise_a_jour  # noqa: E402
import versions_posees  # noqa: E402
import journal as journal_en  # noqa: E402  (logs en anglais hors français)

RACINE = os.path.dirname(chemins.OUTILS)
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "page.html")
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")   # police FM27 GT America Black
# icône de fenêtre : sans liseré, dessinée à chaque taille (16 à 256) pour rester nette dans la barre des tâches
ICONE = os.path.join(os.path.dirname(LOGO), "icone.ico")
COMMUN = os.path.join(chemins.OUTILS, "commun")
VENV = os.path.join(RACINE, ".venv")
# Python des scripts (UnityPy, Pillow) : celui livré par le Setup (python\, 3.14 figé, v1.21) sinon le .venv créé
# à l'étape Outils (installations d'avant, ou zip sans Setup)
EMBARQUE = os.path.join(RACINE, "python")
WINDOWS = os.name == "nt"   # Linux (v1.51) : FM27 par Proton ; même app, .venv/bin, lanceur « Lancer - Launch.sh »
MAC = sys.platform == "darwin"   # Mac (2026-11-06) : FM27 natif (fm.app) ; .venv/bin, lanceur « Lancer - Launch.command »
SYSTEME = "macOS" if MAC else "Windows"   # libellé du journal et des diagnostics
# Mac (v1.87) : python/ = Python 3.14.8 autonome (python-build-standalone) préparé par « Lancer - Launch.command »
_PY_EMB = os.path.join(EMBARQUE, "bin", "python3") if MAC else os.path.join(EMBARQUE, "python.exe")
PY_OUTILS = _PY_EMB if (WINDOWS or MAC) and os.path.exists(_PY_EMB) else \
    os.path.join(VENV, "Scripts", "python.exe") if WINDOWS else os.path.join(VENV, "bin", "python")
# zstandard : sigles à 3 lettres (lecture de la base de FM) sur un Python sans compression.zstd (< 3.14 : Linux / Mac)
MODULES = ["UnityPy==1.25.4", "Pillow", "zstandard; python_version < '3.14'"]
ARRET_SANS_PAGE = 180   # s sans nouvelle de la page -> arrêt (les onglets cachés ne donnent signe de vie qu'1 fois / min)
JETON = secrets.token_hex(16)   # la page le renvoie à chaque action : un autre site ne peut rien lancer
SANS_FENETRE = 0x08000000 if WINDOWS else 0   # CREATE_NO_WINDOW (ailleurs : creationflags interdit)


# moteur Rust (v1.62, d'après fm27-turbo) : paquet UnityPy de même API, ~9× plus rapide ; mis en tête du chemin des
# scripts s'il se charge avec le Python des scripts, sinon le vrai UnityPy (Linux, Python sans le moteur...).
# UIPICKER_MOTEUR=unitypy : forcer UnityPy (dépannage). 2026-11-05 : PYTHONPATH ne marchait pas avec python\ -> .pth
MOTEUR_RUST = os.path.join(chemins.OUTILS, "moteur_rust")
_moteur = None
# le Python embarqué du Setup (python\, fichier ._pth) ignore PYTHONPATH : ce .pth du site-packages met le moteur en
# tête du chemin quand la variable UIPICKER_MOTEUR_RUST est posée (posée par l'app seulement si le moteur se charge)
PTH = "uipicker_moteur_rust.pth"
PTH_TEXTE = "import os, sys; p = os.environ.get('UIPICKER_MOTEUR_RUST'); p and sys.path.insert(0, p)\n"


def _poser_pth():
    try:
        f = os.path.join(site_outils(), PTH)
        if os.path.isdir(os.path.dirname(f)) and not (os.path.exists(f) and open(f).read() == PTH_TEXTE):
            with open(f, "w") as o:
                o.write(PTH_TEXTE)
    except OSError:
        pass


def moteur_rust():
    """dossier du moteur Rust s'il se charge, sinon "" (UnityPy) ; testé une fois (le Python des scripts existe)"""
    global _moteur
    if _moteur is not None:
        return _moteur
    if os.environ.get("UIPICKER_MOTEUR", "").lower() == "unitypy" \
            or not os.path.isdir(os.path.join(MOTEUR_RUST, "UnityPy")):
        _moteur = ""
        return _moteur
    if not os.path.exists(PY_OUTILS):
        return ""   # étape Outils pas encore faite : on reteste plus tard
    _poser_pth()
    try:
        r = subprocess.run([PY_OUTILS, "-c", "import UnityPy, UnityPy._core; print(UnityPy.__version__)"],
                           env=dict(os.environ, UIPICKER_MOTEUR_RUST=MOTEUR_RUST), capture_output=True, text=True,
                           timeout=30, creationflags=SANS_FENETRE)
        _moteur = MOTEUR_RUST if r.returncode == 0 and "fm27turbo" in r.stdout else ""
    except (OSError, subprocess.SubprocessError):
        _moteur = ""
    print(f"moteur : {'Rust' if _moteur else 'UnityPy'}", flush=True)
    return _moteur


def site_outils():
    """site-packages du Python des scripts (Linux : lib/python3.X/site-packages, X connu une fois le .venv créé)"""
    if WINDOWS:
        return os.path.join(EMBARQUE if PY_OUTILS == _PY_EMB else VENV, "Lib", "site-packages")
    import glob
    base = EMBARQUE if PY_OUTILS == _PY_EMB else VENV   # Mac : python/ embarqué
    return next(iter(sorted(glob.glob(os.path.join(base, "lib", "python3*", "site-packages")))),
                os.path.join(base, "lib", "site-packages"))

# lancé par pythonw (lanceur du partage, ou redémarrage après une mise à jour : là, sys.stdout existe mais écrire
# dedans plante, OSError 22) : messages et erreurs dans un fichier
if sys.stderr is None or os.path.basename(sys.executable).lower().startswith("pythonw"):
    os.makedirs(backup.BACKUP_DIR, exist_ok=True)
    sys.stderr = sys.stdout = open(os.path.join(backup.BACKUP_DIR, "app.log"), "a", encoding="utf-8", buffering=1)


# journal à la racine (v1.30) : clic droit sur le raccourci > Ouvrir l'emplacement du fichier ; le joueur l'envoie
# quand il a un souci. En-tête à chaque ouverture (versions, jeu, fonctions), puis chaque action et son résultat.
# Gardé par le Setup et la MAJ auto (ils ne remplacent que outils\) ; jamais dans le partage (maj_partage).
JOURNAL = os.path.join(RACINE, "Journal - Log.txt")
JOURNAL_MAX, JOURNAL_GARDE = 500 * 1024, 300 * 1024   # au-delà : on ne garde que la fin
_VERROU_JOURNAL = threading.Lock()


def journal(*lignes):
    """ajoute des lignes datées (la 1re) au journal ; jamais d'erreur (journal impossible : tant pis)"""
    texte = time.strftime("[%Y-%m-%d %H:%M:%S] ") + "\n".join(str(x) for x in lignes) + "\n"
    with _VERROU_JOURNAL:
        try:
            with open(JOURNAL, "a", encoding="utf-8") as f:
                f.write(texte)
        except OSError:
            pass


def _journal_raccourcir():
    try:
        if os.path.getsize(JOURNAL) <= JOURNAL_MAX:
            return
        with open(JOURNAL, "rb") as f:
            f.seek(-JOURNAL_GARDE, os.SEEK_END)
            fin = f.read()
        fin = fin[fin.find(b"\n") + 1:]   # à partir d'une ligne entière
        with open(JOURNAL, "wb") as f:
            f.write("(début du journal effacé : trop long / start of the log removed: too long)\n".encode("utf-8") + fin)
    except OSError:
        pass


def journal_entete():
    """bloc d'ouverture de l'app : tout ce qu'il faut pour comprendre un souci sans poser de questions"""
    _journal_raccourcir()
    try:
        import platform
        g = jeu()
        aa = os.path.join(g or "", chemin_jeu.SOUS_DOSSIER_AA)
        valide = bool(chemin_jeu.valide(g))
        bas = (g or "").lower()
        boutique = ("Steam" if "steamapps" in bas else "Epic" if "epic games" in bas
                    else "Xbox / Game Pass" if "xboxgames" in bas or "windowsapps" in bas else "?")
        actives = [n for n in cat.FONCTIONS if lancer.actif(n)]
        choisies = [f"{o}={options.get(o)}" for o in options.OPTIONS if options.get(o) != options.defaut(o)]
        lignes = [
            "=" * 70,
            "App ouverte / App opened : " + appnom(),
            f"{SYSTEME} : {platform.mac_ver()[0] + ' ' + platform.machine() if MAC else platform.platform()}",
            f"Python : {'embarqué (Setup) / bundled' if PY_OUTILS == _PY_EMB else '.venv'} "
            f"({'ok' if python_ok() else 'UnityPy MANQUANT / MISSING'}) ; app : {sys.version.split()[0]}",
            f"Langue / Language : {langue.lire()}",
            f"Jeu / Game : {g or '(pas choisi / not set)'} ({boutique}) ; valide / valid : {'oui / yes' if valide else 'NON / NO'}",
            f"FM ouvert / FM running : {'oui / yes' if fm_ouvert() else 'non / no'}",
        ]
        if valide:
            c = compat(g)
            lignes.append(f"Version de FM / FM version : {backup.version_fm(aa)} ; compatibilité / compatibility : "
                          f"{c['etat']}" + (" (risque accepté / risk accepted)" if autre_maj_acceptee(g) else ""))
            m = maj_jeu(g)
            if m:
                lignes.append(f"Fichiers remplacés par FM / Files replaced by FM : {', '.join(m['fichiers'])}")
        lignes += [
            f"Skin installé / Skin installed : {'oui / yes' if installe() else 'non / no'}",
            f"Fonctions actives / Enabled features ({len(actives)}) : {', '.join(actives) or '-'}",
            f"Options : {', '.join(choisies) or '(par défaut / default)'}",
            f"Fond / Background : {fond() or '-'} ; couleurs / colours : {couleurs() or '-'}",
            "=" * 70,
        ]
        journal(*lignes)
    except Exception as e:   # noqa: BLE001 (en-tête incomplet plutôt qu'une app qui ne s'ouvre pas)
        journal(f"App ouverte / App opened : {appnom()} (en-tête incomplet / partial header : {type(e).__name__}: {e})")


def stades_diag():
    """v1.46 : diagnostic des photos de stades copié par le joueur (page Photos des stades) : tout ce qu'il faut pour
    trouver pourquoi les photos ne s'affichent pas quand la vérif est toute verte"""
    import platform
    g = jeu()
    valide = bool(chemin_jeu.valide(g))
    ouvert = fm_ouvert()
    D = stades_photos.diagnostic(ouvert)
    F = D["fm_lu"]
    P = stades_photos.fichiers(entetes=True) if D["graphics_ok"] else {}
    oui = lambda b: "oui / yes" if b else "NON / NO"   # noqa: E731
    quand = lambda t: time.strftime("%Y-%m-%d %H:%M", time.localtime(t)) if t else "-"   # noqa: E731
    peu = lambda l: ", ".join(l[:5]) + (f" (+{len(l) - 5})" if len(l) > 5 else "")   # noqa: E731
    lignes = ["```", "Diagnostic photos des stades / stadium photos : " + appnom(),
              f"{SYSTEME} : {platform.platform()} ; langue / language : {langue.lire()}",
              f"Jeu / Game : {g or '-'} ; valide / valid : {oui(valide)} ; FM ouvert / running : {oui(ouvert)}"]
    if valide:
        lignes.append(f"Version de FM / FM version : {backup.version_fm(os.path.join(g, chemin_jeu.SOUS_DOSSIER_AA))}")
        m = maj_jeu(g)
        lignes.append(f"Fichiers remis par FM / Files put back by FM : {', '.join(m['fichiers']) if m else '-'}")
    lignes += [
        f"Page club du skin (marqueur) / Skin club page (marker) : {oui(D['skin'])} ; skin installé / installed : {oui(installe())}",
        f"Documents : {stades_photos.documents()}",
        f"Dossier FM 27 / FM 27 folder : {oui(os.path.isdir(stades_photos.dossier_fm()))} ; "
        f"graphics choisi / picked : {stades_photos.choisi() or '-'}",
        f"graphics : {D['graphics']} ({oui(D['graphics_ok'])})",
        f"Photos de stades / Stadium photos : {D['photos']} (FMVE Stadium {D['fmve']}, ancien format / old format "
        f"{D['anciens']}) ; clubs liés / linked : {D['clubs']} ; config.xml des liens / links : {D['config']} / "
        f"{D['config_attendu']} attendues / expected"
        + (f" ; ILLISIBLE / UNREADABLE : {D['config_erreur']}" if D.get("config_erreur") else ""),
        "Packs : " + (", ".join(f"{p} ({n})" for p, n in D["packs"]) or "-"),
    ]
    if P:
        lignes += [
            f"  png {P['png']} / jpg {P['jpg']} ; arrivées / added : {quand(P['arrivee'])} ; "
            f"en double / duplicates : {P['doubles']} ; lecture seule / read-only : {P['lecture_seule']}",
            f"  en ligne seulement (OneDrive) / online-only : {P['nuage']} ; vides / empty : {peu(P['vides']) or '0'} ; "
            f"mauvais format / wrong format : {peu(P['faux']) or '0'} (sur / of {P['lues']} lues / read)",
            f"  en trop dans FMVE Stadium / extra in FMVE Stadium : {peu(P.get('en_trop', [])) or '-'}",
        ]
    lignes += [
        "Mal placées / Misplaced : " + (", ".join(f"{e['relatif']} ({e['photos']})" for e in D["egares"]) or "-"),
        f"Archives : {', '.join(D['rar']) or '-'}",
    ]
    if D["graphics_ok"]:   # un autre pack peut gêner : noms seulement (+ « c » = config.xml à sa racine)
        A = stades_photos.autres_packs()
        lignes.append(f"Autres dossiers de graphics / Other graphics folders ({len(A['dossiers'])}) : "
                      + (", ".join(n + (" [config.xml]" if c else "") for n, c in A["dossiers"][:25]) or "-")
                      + (" ..." if len(A["dossiers"]) > 25 else "")
                      + (" ; config.xml DANS graphics / IN graphics : oui / yes" if A["racine_config"] else ""))
        S = stades_photos.scan_configs()   # tous les config.xml : celui qui bloque nos photos
        lignes.append(f"config.xml lus / read : {S['configs']} ; suspects : " + ("; ".join(
            f"{s['relatif']} = {s['raison']}" + (f" ({s['n']})" if s["n"] else "") for s in S["suspects"][:10]) or "-"))
        cote = os.path.join(stades_photos.dossier_fm(), stades_photos.COTE)
        if os.path.isdir(cote):
            lignes.append(f"Mis de côté / Set aside : {', '.join(os.listdir(cote)) or '-'}")
    autres = stades_photos.autres_dossiers_fm()
    lignes.append("Autres dossiers FM 27 / Other FM 27 folders : " + ("; ".join(
        f"{p} (FMVE Stadium : {oui(s)}, modifié / changed {quand(t)})" for p, s, t in autres) or "-"))
    L = stades_photos.lancements()
    rel = {"non": "NON, pas relancé depuis / NOT restarted since", "pendant": "installées PENDANT qu'il tournait / "
           "added WHILE it was running", "oui": "oui, lancé après / yes, started after", None: "?"}[F.get("relance")]
    comp, attendu = F.get("comp"), D["config_attendu"]
    lignes += [
        f"FM (dernier lancement / last run) : grille / grid = {F.get('grille', '?')} ; "
        f"images comp chargées / loaded = {comp if comp is not None else '?'}"
        + (f" (photos attendues / expected {attendu}, écart / gap {comp - attendu:+d})" if comp is not None else ""),
        f"  lancement précédent fini / previous run ended : {quand(L['avant'])} ; dernier fini / last ended : "
        f"{quand(L['fin'])} ; registre / registry : {quand(F.get('date'))}",
        f"  FM relancé depuis l'arrivée des photos / FM restarted since the photos were added : {rel}",
        "  tout / all : " + (", ".join(f"{a} {b}" for a, b in F.get("detail", {}).items()) or "-"),
    ]
    log = os.path.join(stades_photos.LOGS_FM, "Player.log")
    try:
        lignes.append("Player.log : " + time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(log))))
        erreurs = []   # messages de FM (lignes JSON « Message ») + en-têtes d'exception ; pas les piles d'appels
        with open(log, encoding="utf-8", errors="replace") as f:
            for x in f:
                m = re.search(r'"LogLevel":"(Error|Critical)".*?"Message":"(.*?)"', x)
                x = (m.group(1) + " : " + m.group(2)) if m else x.strip() if (
                    re.match(r"[\w.]*Exception\b", x.strip()) or re.search(r"fmve|graphics|uipicker|config\.xml", x, re.I)) else ""
                if x and x[:200] not in erreurs:
                    erreurs.append(x[:200])
        lignes += ["  " + x for x in erreurs[-10:]]
    except OSError:
        lignes.append("Player.log : -")
    try:   # dispositions perso de FM (passent avant le skin)
        grilles = os.listdir(os.path.join(chemin_jeu.donnees_fm(), "CustomGridCompositions"))
        lignes.append(f"Dispositions perso / Custom layouts : {', '.join(x for x in grilles if 'club' in x.lower()) or '-'}")
    except OSError:
        lignes.append("Dispositions perso / Custom layouts : -")
    return "\n".join(lignes + ["```"])


def appnom():
    try:
        with open(os.path.join(COMMUN, "version.txt"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return os.environ.get("APPNOM") or "FM27 Vanilla Enhanced Skin by AlexJeuVideal x Kinito"


# versions de Python où UnityPy (et lz4, brotli) s'installent sans compilateur (roues Windows publiées) ; 3.15 : pas
# encore de roues (vu le 2026-11-12 chez un joueur : étape Outils impossible) -> on prend un autre Python installé
PY_OUTILS_MIN, PY_OUTILS_MAX = (3, 8), (3, 14)


def _version_python(exe):
    try:
        r = subprocess.run([exe, "-c", "import sys; print(sys.version_info[0], sys.version_info[1])"],
                           capture_output=True, timeout=15, creationflags=SANS_FENETRE)
        a, b = r.stdout.split()[:2]
        return int(a), int(b)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def python_base():
    """python.exe de Windows pour créer le .venv : celui du serveur s'il convient, sinon le plus récent des Python
    installés qui convient (lanceur py, dossiers d'installation habituels) ; None s'il n'y en a aucun.
    Linux : python3.14 … python3.8 / python3 du PATH ; Mac : aussi python.org, Homebrew et celui d'Apple (lancé par
    double-clic, le PATH ne contient pas toujours Homebrew)"""
    import glob
    if not WINDOWS:
        candidats = [sys.executable] + [shutil.which(f"python3.{m}") for m in range(PY_OUTILS_MAX[1], 7, -1)] \
            + [shutil.which("python3")]
        if MAC:
            for m in range(PY_OUTILS_MAX[1], 7, -1):
                candidats += [f"/Library/Frameworks/Python.framework/Versions/3.{m}/bin/python3",
                              f"/opt/homebrew/bin/python3.{m}", f"/usr/local/bin/python3.{m}"]
            candidats += ["/opt/homebrew/bin/python3", "/usr/local/bin/python3", "/usr/bin/python3"]
            candidats = [c for c in candidats if c and os.path.exists(c)]
        meilleur, vmax = None, None
        for exe in dict.fromkeys(c for c in candidats if c):
            v = _version_python(exe)
            if v and PY_OUTILS_MIN <= v <= PY_OUTILS_MAX and (vmax is None or v > vmax):
                meilleur, vmax = exe, v
                if exe == sys.executable:
                    break
        return meilleur
    base = sys.base_prefix if sys.prefix != sys.base_prefix else os.path.dirname(sys.executable)
    p = os.path.join(base, "python.exe")
    candidats = [p if os.path.exists(p) else sys.executable]
    try:
        r = subprocess.run(["py", "-0p"], capture_output=True, timeout=15, creationflags=SANS_FENETRE)
        candidats += re.findall(r"[A-Za-z]:\\[^\r\n*]*?python\.exe", r.stdout.decode("utf-8", "replace"), re.I)
    except (OSError, subprocess.SubprocessError):
        pass
    loc = os.environ.get("LOCALAPPDATA", "")
    for motif in (r"Python\pythoncore-3.*\python.exe", r"Programs\Python\Python3*\python.exe"):
        candidats += glob.glob(os.path.join(loc, motif))
    candidats += glob.glob(os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Python3*", "python.exe"))
    meilleur, vmax = None, None
    for exe in dict.fromkeys(os.path.normcase(c) for c in candidats):
        v = _version_python(exe)
        if v and PY_OUTILS_MIN <= v <= PY_OUTILS_MAX and (vmax is None or v > vmax):
            meilleur, vmax = exe, v
            if exe == os.path.normcase(candidats[0]):
                break   # celui du serveur convient : on le garde
    return meilleur


def python_ok():
    return os.path.exists(PY_OUTILS) and os.path.isdir(os.path.join(site_outils(), "UnityPy"))


# ---------- état ----------
_fm = {"t": 0, "ouvert": False}


def fm_ouvert():
    if time.time() - _fm["t"] > 2:
        if MAC:
            _fm["ouvert"], _fm["t"] = _fm_ouvert_mac(), time.time()
            return _fm["ouvert"]
        if not WINDOWS:
            _fm["ouvert"], _fm["t"] = _fm_ouvert_linux(), time.time()
            return _fm["ouvert"]
        try:
            # en octets : tasklist écrit dans l'encodage de la console (cp850…), pas en UTF-8 ; Python 3.15 lit le
            # texte en UTF-8 par défaut -> plantage (octet 0xff du « 12 345 Ko »), page de l'app vide (2026-11-12)
            r = subprocess.run(["tasklist", "/fi", "imagename eq fm.exe", "/nh"], capture_output=True,
                               creationflags=SANS_FENETRE)
            _fm["ouvert"] = b"fm.exe" in (r.stdout or b"").lower()
        except OSError:
            _fm["ouvert"] = False
        _fm["t"] = time.time()
    return _fm["ouvert"]


def _fm_ouvert_mac():
    """Mac : programme fm.app/Contents/MacOS/Football Manager 27 (lu avec ps, chemins complets)"""
    try:
        # ligne de commande entière (-ww : pas coupée) : le chemin du programme contient des espaces
        r = subprocess.run(["ps", "-axww", "-o", "command="], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    for ligne in (r.stdout or b"").decode("utf-8", "replace").splitlines():
        if "/fm.app/contents/macos/" in ligne.lower():
            return True
    return False


def _fm_ouvert_linux():
    """Proton : fm.exe est un processus Wine (nom « fm.exe », ou 1er argument …\\fm.exe) ; lu dans /proc"""
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return False
    for p in pids:
        try:
            with open(f"/proc/{p}/comm", encoding="utf-8", errors="replace") as f:
                if f.read().strip().lower() == "fm.exe":
                    return True
            with open(f"/proc/{p}/cmdline", "rb") as f:
                arg0 = f.read().split(b"\0")[0].decode("utf-8", "replace")
            if re.split(r"[\\/]", arg0)[-1].lower() == "fm.exe":
                return True
        except OSError:
            pass
    return False


def jeu():
    """dossier du jeu (relu à chaque fois : l'assistant peut le changer)"""
    return os.environ.get("UIPICKER_JEU") or chemin_jeu.lire()


_detecte = {"fait": False, "chemin": ""}


def detecte():
    if not _detecte["fait"]:
        _detecte["chemin"] = chemin_jeu.detecter()
        _detecte["fait"] = True
    return _detecte["chemin"]


def installe():
    """le skin a déjà été écrit dans le jeu (empreintes de sauvegarde_originaux)"""
    try:
        return any(f.endswith(".written.sha256") for f in os.listdir(backup.BACKUP_DIR))
    except OSError:
        return False


def fond():
    """couleur du fond choisie (marqueur de theme_fond), ou None"""
    try:
        with open(os.path.join(backup.BACKUP_DIR, "theme_fond.actif"), encoding="utf-8") as f:
            m = json.load(f)
        return {"couleur": m.get("couleur"), "nom": m.get("nom"), "infobulle": m.get("infobulle"),
                "lisse": bool(m.get("lisse"))}
    except (OSError, ValueError):
        return None


HEXA = r"#?[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?"   # #RRGGBB, ou #RRGGBBAA (opacité)
COULEURS_TACTIQUES = ("tac_barre", "tac_panneau", "tac_terrain")   # verts de l'écran Tactiques (couleurs_interface)
# fond des tuiles, tableau de score de base en match (couleurs_interface, 2026-11-06) ; dans les thèmes depuis le 2026-11-09
COULEURS_AUTRES = ("tuiles", "score_fond", "score_bande",
                   "match_boutons", "match_effectif", "commentaire",   # + match (2026-11-07)
                   "menus", "boutons",   # + menus / fenêtres, boutons d'action (2026-11-08)
                   "panneaux", "fiche")   # + grands panneaux, grande tuile de la fiche joueur (2026-11-09)
# couleurs des postes de l'écran Tactiques (2026-11-09) : page Couleurs seulement, PAS dans les thèmes (le joueur)
COULEURS_POSTES = ("poste_gb", "poste_d", "poste_dm", "poste_mc", "poste_mo", "poste_bt")
# bouton Continuer en alerte / pendant le traitement / les jours de match (2026-11-11) : page Couleurs (Barre du
# haut) et thèmes (un thème sauvegardé avant ne les a pas : laissées absentes, celles en cours gardées)
COULEURS_CONTINUER = ("continuer_alerte", "continuer_traitement", "continuer_match")


# bouton Continuer (2026-11-11, couleurs_interface clé « continuer ») : bouton de FM / couleur du thème / du club, ""
# = auto (couleur du thème si boutons / accent choisis) ; dans les thèmes, pas une couleur
CONTINUER = tuple("fm theme club".split())   # (écrit ainsi : traductions_relever ne le prend pas pour un texte)


def continuer_arg(d):
    """argument « continuer=… » pour couleurs_interface (absent de la demande = rien envoyé, valeur gardée)"""
    if "continuer" not in d:
        return []
    v = d.get("continuer") or ""
    return [f"continuer={v if v in CONTINUER else 'auto'}"]


# touche de couleur du club sur une barre unie (2026-11-11, ESSAI, couleurs_interface clés « touche* ») : style, "" =
# aucune ; longueur et force en %
TOUCHES = tuple("net doux halo liseret deux".split())


def touche_arg(d):
    """arguments « touche=… touche_long=… touche_force=… » (absents de la demande = rien envoyé, valeurs gardées)"""
    if "touche" not in d:
        return []
    v = d.get("touche") or ""
    out = [f"touche={v if v in TOUCHES else 'aucune'}"]
    for k, lo, hi in (("touche_long", 10, 90), ("touche_force", 10, 90)):
        n = d.get(k)
        if isinstance(n, (int, float)) and not isinstance(n, bool):
            out.append(f"{k}={max(lo, min(hi, int(n)))}")
    return out


def ombrage_arg(d):
    """argument « ombrage=… » (2026-11-14) : opacité en % du fond sombre derrière les fenêtres par-dessus le jeu
    (Traitement entre les jours) ; vide / 65 = celle de FM ; absent de la demande = rien envoyé, valeur gardée"""
    if "ombrage" not in d:
        return []
    n = d.get("ombrage")
    if isinstance(n, (int, float)) and not isinstance(n, bool):
        return [f"ombrage={max(0, min(100, int(n)))}"]
    return ["ombrage=fm"]


def polygone_arg(d):
    """argument « polygone=… » (2026-11-14) : couleur du polygone de la fiche joueur (#RRGGBB / #RRGGBBAA) ; vide =
    celui de FM ; absent de la demande = rien envoyé, valeur gardée. Clé des thèmes (CLES_THEME)"""
    if "polygone" not in d:
        return []
    v = (d.get("polygone") or "").strip() if isinstance(d.get("polygone"), str) else ""
    return [f"polygone={v}" if re.fullmatch(HEXA, v) else "polygone=fm"]


def couleur_ok(cle, v):
    """#RRGGBB ou #RRGGBBAA (avec opacité) ; tuiles : aussi « panneau » (comme le grand panneau des fiches,
    couleurs_interface.TUILES_PANNEAU)"""
    return bool(re.fullmatch(HEXA, v)) or (cle == "tuiles" and v == "panneau")


# thèmes complets sauvegardés par le joueur (page Couleurs, « Mes thèmes ») : dans backups\, gardé par la MAJ auto
MES_THEMES = os.path.join(backup.BACKUP_DIR, "mes_themes.json")
# + Match, menus, boutons dans les thèmes (2026-11-09) ; un thème sauvegardé avant n'a pas ces clés : laissées absentes
# (l'app garde alors celles en cours)
CLES_THEME = ("fond", "info", "barre", "texte", "barre2", "accent", *COULEURS_TACTIQUES, *COULEURS_AUTRES,
              *COULEURS_CONTINUER, "polygone")   # + polygone (2026-11-14)


def themes_propres(liste):
    """[{nom, clés de CLES_THEME : "#RRGGBB" ou None}] ; tout le reste écarté"""
    out = []
    for th in liste if isinstance(liste, list) else []:
        if not isinstance(th, dict) or not isinstance(th.get("nom"), str) or not th["nom"].strip():
            continue
        p = {"nom": th["nom"].strip()[:40]}
        for k in CLES_THEME:
            if k in (*COULEURS_AUTRES[1:], *COULEURS_CONTINUER, "polygone") and k not in th:
                continue
            v = th.get(k)
            p[k] = (v if v == "panneau" else ("#" + v.lstrip("#")).upper()) if isinstance(v, str) and couleur_ok(k, v) else None
        if "continuer" in th:   # bouton Continuer (2026-11-11) : absent = celui en cours gardé par l'app
            p["continuer"] = th["continuer"] if th["continuer"] in CONTINUER else None
        out.append(p)
    return out[:1000]


def mes_themes():
    try:
        with open(MES_THEMES, encoding="utf-8") as f:
            return themes_propres(json.load(f))
    except (OSError, ValueError):
        return []


def couleurs():
    """couleurs de l'interface choisies (marqueur de couleurs_interface : barre, texte, barre2, accent, verts des
    Tactiques ; liseret = « cache » si le trait entre les deux barres est caché), ou None"""
    try:
        with open(os.path.join(backup.BACKUP_DIR, "couleurs_interface.actif"), encoding="utf-8") as f:
            m = json.load(f)
        return {k: m.get(k) for k in ("barre", "texte", "barre2", "accent", "liseret", *COULEURS_TACTIQUES,
                                      *COULEURS_AUTRES, *COULEURS_POSTES, "continuer", *COULEURS_CONTINUER,
                                      "touche", "touche_long", "touche_force", "ombrage", "polygone")}
    except (OSError, ValueError):
        return None


_compat = {"cle": None, "valeur": None}


def compat(g):
    """même mise à jour de FM que le skin ? (sauvegarde_originaux.compatibilite, gardé tant que rien ne change :
    l'empreinte des 9 bundles prend ~1 s)"""
    aa = os.path.join(g, chemin_jeu.SOUS_DOSSIER_AA)
    cle = [backup.version_fm(aa)]
    for n in backup.FICHIERS:
        for p in (os.path.join(aa, n), backup.backup_path(n)):
            try:
                st = os.stat(p)
                cle.append((st.st_size, st.st_mtime))
            except OSError:
                cle.append(None)
    if cle != _compat["cle"]:
        try:
            _compat["valeur"] = backup.compatibilite(aa) if chemin_jeu.valide(g) else {"etat": "inconnu", "fichiers": []}
        except OSError:
            _compat["valeur"] = {"etat": "inconnu", "fichiers": []}
        _compat["cle"] = cle
    return _compat["valeur"]


# jeu d'une autre mise à jour de FM que le skin (compat « different ») : tout ce qui écrit est bloqué, sauf si le
# joueur a accepté le risque POUR CETTE version de FM (catalog.hash gardé ici ; une nouvelle MAJ de FM redemande)
ACCEPTE = os.path.join(backup.BACKUP_DIR, "autre_maj_acceptee.txt")


def autre_maj_acceptee(g):
    try:
        with open(ACCEPTE, encoding="utf-8") as f:
            return f.read().strip() == backup.version_fm(os.path.join(g, chemin_jeu.SOUS_DOSSIER_AA))
    except OSError:
        return False


def autre_maj_bloque(g):
    return compat(g)["etat"] == "different" and not autre_maj_acceptee(g)


_remplaces = {"cle": None, "valeur": []}


def maj_jeu(g):
    """v1.25 : page « Une mise à jour du jeu a été détectée » : le skin était installé mais FM (mise à jour, vérification
    Steam) a remplacé des fichiers qu'il avait écrits. None si rien ; sinon {"cas": "ok" (skin à jour pour ce FM :
    réinstaller) | "different" (pas à jour : risque), "fichiers": [...]}. Repère de rafraichir() : la page reste après
    une action, jusqu'à une installation complète réussie."""
    aa = os.path.join(g, chemin_jeu.SOUS_DOSSIER_AA)
    if not chemin_jeu.valide(g):
        return None
    cle = []
    for n in backup.FICHIERS:
        for p in (os.path.join(aa, n), backup.backup_path(n) + ".written.sha256"):
            try:
                st = os.stat(p)
                cle.append((st.st_size, st.st_mtime))
            except OSError:
                cle.append(None)
    if cle != _remplaces["cle"]:
        try:
            _remplaces["valeur"] = backup.fichiers_remplaces(aa)
        except OSError:
            _remplaces["valeur"] = []
        _remplaces["cle"] = cle
    remplaces = _remplaces["valeur"]
    if not remplaces and not os.path.exists(backup.JEU_MIS_A_JOUR):
        return None
    c = compat(g)
    return {"cas": "different" if c["etat"] == "different" else "ok", "fichiers": remplaces or c["fichiers"]}


def bloque_guru(nom):
    """raison (fr, en) si la vue FM Guru est choisie et prend le dessus sur cette fonction, sinon None"""
    if nom in cat.BLOQUES_GURU and options.get("fiche_fmguru") == "guru":
        return list(cat.BLOQUES_GURU[nom])
    if lancer.hors_guru(nom):   # 2026-11-10 (le joueur) : mode Guru = seulement la fiche, le reste du jeu reste de FM
        return ["Mode FM Guru (choisi dans Features additionnelles) : seulement la fiche joueur, le reste du jeu reste "
                "celui de FM. Désactivée tant qu'il est choisi.",
                "FM Guru mode (chosen in Additional features): only the player profile, the rest of the game stays "
                "FM's. Disabled while it is chosen."]
    return None


def suivants_poses(nom):
    """fonctions relancées après nom (catalogue.SUIVANTS) qui sont vraiment posées (activées, vue Guru choisie)"""
    return [s for s in cat.SUIVANTS.get(nom, [])
            if (options.get("fiche_fmguru") == "guru" if s == "fiche_fmguru" else lancer.actif(s))]


def guru_a_reinstaller(posees=None):
    """fonctions de la vue FM Guru (catalogue.AVEC_GURU, activées) qui ont changé depuis leur pose, dans l'ordre du skin"""
    posees = versions_posees.lire() if posees is None else posees
    return [n for n in cat.ORDRE_SKIN if n in cat.AVEC_GURU and lancer.actif(n)
            and versions_posees.a_reinstaller(n, posees)]


def notes_de_mise_a_jour():
    """le fichier des notes de toutes les versions : dans partage\\ chez nous (d'abord : notre racine en a un vieux), à la
    racine de l'app installée ; "" s'il manque"""
    for chemin in (os.path.join(RACINE, "partage", "NOTES DE MISE A JOUR.md"),
                   os.path.join(RACINE, "NOTES DE MISE A JOUR.md")):
        try:
            with open(chemin, encoding="utf-8") as f:
                return f.read()
        except OSError:
            continue
    return ""


def etat():
    # fonction activée qui a changé depuis qu'elle a été posée (mise à jour de l'app) : bouton « Réinstaller »
    posees = versions_posees.lire()
    skin = installe()
    fonctions = []
    for nom in cat.FONCTIONS:
        f = cat.FONCTIONS[nom]
        actif = lancer.actif(nom)
        fonctions.append({"nom": nom, "cat": f["cat"], "fr": f["fr"], "en": f["en"], "actif": actif,
                          "facultatif": bool(f.get("facultatif")),
                          # + options d'une autre fonction affichées aussi ici (afficher_aussi, 2026-11-07)
                          "options": lancer.options_de(nom) + [o for o, d in options.OPTIONS.items()
                                                               if d.get("afficher_aussi") == nom],
                          "aide": f.get("aide"), "ou": cat.OU.get(nom), "bloqueGuru": bloque_guru(nom),
                          "avecGuru": nom in cat.AVEC_GURU and options.get("fiche_fmguru") == "guru",
                          "reinstaller": skin and actif and not bloque_guru(nom)
                          and versions_posees.a_reinstaller(nom, posees)})
    opts = [{"nom": o, "titre": d["titre"], "aide": d.get("aide"), "valeurs": d["valeurs"], "actuelle": options.get(o),
             "defaut": options.defaut(o), "script": d["script"], "kinito": bool(d.get("kinito")),
             "fmguru": bool(d.get("fmguru")), "bloque": d.get("bloque"),
             # sans effet tant qu'une autre option a telle valeur (grande tuile de l'en-tête) : note grise dans l'app
             "sansEffet": bool(d.get("sans_effet")) and options.get(d["sans_effet"][0]) == d["sans_effet"][1],
             "dependEntete": bool(d.get("sans_effet")),   # groupe « Seulement avec l'en-tête de FM » de l'app
             # option qui est un mode (vue FM Guru) : interrupteur actif / inactif, « Réinstaller » si sa vue a changé
             # 2026-11-07 (le joueur) : aussi quand une fonction qui va avec la vue (AVEC_GURU) a changé
             "reinstaller": bool(d.get("bloque")) and skin and options.get(o) == d["bloque"]
             and (versions_posees.a_reinstaller(d["script"], posees) or bool(guru_a_reinstaller(posees))
                  or bool(lancer.restes_guru())),   # 2026-11-10 : autres fonctions posées par une MAJ (avant v1.75)
             "bloquees": [[cat.FONCTIONS[n]["fr"], cat.FONCTIONS[n]["en"]] for n in cat.BLOQUES_GURU]
             if d.get("bloque") else [],
             "avec": [[cat.FONCTIONS[n]["fr"], cat.FONCTIONS[n]["en"]] for n in cat.AVEC_GURU] if d.get("bloque") else []}
            for o, d in options.OPTIONS.items()]
    g = jeu()
    photos, anciens = stades_photos.compte()   # anciens : photos de l'ancien pack (alerte « Mettre à jour mes photos »)
    return {
        "appnom": appnom(),
        "langue": langue.lire(),
        "jeu": g,
        "jeu_ok": bool(chemin_jeu.valide(g)),
        "compat": dict(compat(g), accepte=autre_maj_acceptee(g)),
        "maj_jeu": maj_jeu(g),
        "fm_ouvert": fm_ouvert(),
        "installation": {
            "langue": os.path.exists(langue.FICHIER),
            "python": python_ok(),
            "embarque": PY_OUTILS == _PY_EMB and python_ok(),   # Python du Setup : pas d'étape Outils
            "jeu": bool(os.environ.get("UIPICKER_JEU")) or (os.path.exists(chemin_jeu.FICHIER) and chemin_jeu.valide(g)),
            "installe": installe(),
        },
        "categories": [{"id": c, "fr": fr, "en": en} for c, fr, en in cat.CATEGORIES],
        "fonctions": fonctions,
        "options": opts,
        # section Joueur (2026-11-11) : ce qu'elle règle, et ce que la vue FM Guru garde
        "joueur": {"fonctions": JOUEUR_FONCTIONS, "options": JOUEUR_OPTIONS, "avec_guru": cat.AVEC_GURU,
                   "ordre_tuiles": options.ordre_tuiles() if sorted(options.ordre_tuiles() or []) == sorted(TUILES_BAS) else None},
        "fond": fond(),
        "couleurs": couleurs(),
        "mes_themes": mes_themes(),
        "liens": LIENS,
        "tache": tache_etat(),
        # « verif » tant que la recherche du lancement n'a pas répondu (écran de chargement de la page)
        "maj": dict(MAJ["info"] or {"etat": "verif"}, fait=mise_a_jour.fait()),
        "lance": LANCE,
        "stades": {"graphics": stades_photos.graphics(), "base": stades_photos.graphics_de_base(),
                   "choisi": stades_photos.choisi(), "ok": os.path.isdir(stades_photos.graphics()),
                   "dossier": stades_photos.dossier(), "photos": photos, "anciens": anciens},
        "trophees": {"dossier": trophees_photos.dossier(), "images": trophees_photos._images(trophees_photos.dossier(), False),
                     "anciens": trophees_photos.anciens()},   # v1.73 : conversion obligatoire, avec les stades
    }


# ---------- mise à jour de l'app ----------
MAJ = {"info": None}
LANCE = time.time()   # la page se recharge quand il change (app redémarrée après une mise à jour)


def maj_verifier():
    MAJ["info"] = mise_a_jour.verifier()


# ---------- tâches (un script à la fois, journal en direct) ----------
TACHE = {"id": 0, "titre": None, "type": None, "lignes": [], "courante": "", "fini": True, "code": None,
         "debut": 0, "fin": 0}
VERROU = threading.Lock()
# tâche en cours, vue par les AUTRES fenêtres de l'app (v1.30) : app fermée pendant une installation (le serveur
# finit la tâche) puis relancée -> 2e serveur ; sans ça, deux scripts écriraient les mêmes fichiers en même temps
EN_COURS = os.path.join(backup.BACKUP_DIR, "tache_en_cours.txt")


def _vivant(pid):
    """processus Windows encore en vie (OpenProcess + GetExitCodeProcess = STILL_ACTIVE) ; Linux : kill 0"""
    if not WINDOWS:
        try:
            os.kill(pid, 0)
            return True
        except PermissionError:
            return True
        except OSError:
            return False
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return bool(ok) and code.value == 259
    except (OSError, AttributeError):
        return False


def tache_ailleurs():
    """une autre fenêtre de l'app (autre serveur) a une tâche en cours"""
    try:
        with open(EN_COURS, encoding="utf-8") as f:
            pid, debut = f.read().split()[:2]
        pid = int(pid)
        return pid != os.getpid() and time.time() - float(debut) < 3 * 3600 and _vivant(pid)
    except (OSError, ValueError):
        return False


def _python(script, *args):
    return [PY_OUTILS, script] + list(args)


def _executer(commandes, apres):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    if moteur_rust():   # lue par le .pth (PTH) ; héritée par les scripts que lancer.py relance (sys.executable)
        env["UIPICKER_MOTEUR_RUST"] = MOTEUR_RUST
    code = 0
    TACHE["echec"] = None   # commande qui a échoué (retirer : marqueur remis si c'est celle du retrait)
    for cmd in commandes:
        try:
            p = subprocess.Popen(cmd, cwd=RACINE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, creationflags=SANS_FENETRE)
        except OSError as e:
            with VERROU:
                TACHE["lignes"].append(str(e))
            code = 1
            TACHE["echec"] = cmd
            break
        decodeur = codecs.getincrementaldecoder("utf-8")(errors="replace")   # caractère coupé : attend la suite
        while True:
            bloc = p.stdout.read1(4096)
            if not bloc:
                break
            texte = decodeur.decode(bloc)
            with VERROU:
                for morceau in re.split(r"(\r\n|\n|\r)", texte):
                    if morceau in ("\n", "\r\n"):
                        TACHE["lignes"].append(TACHE["courante"])
                        TACHE["courante"] = ""
                    elif morceau == "\r":   # barre de chargement : la ligne est réécrite
                        TACHE["courante"] = ""
                    else:
                        TACHE["courante"] += morceau
        code = p.wait()
        if code:
            TACHE["echec"] = cmd
            break
    if apres:
        try:
            apres(code)
        except Exception as e:   # noqa: BLE001
            with VERROU:
                TACHE["lignes"].append(str(e))
    with VERROU:
        if TACHE["courante"]:
            TACHE["lignes"].append(TACHE["courante"])
            TACHE["courante"] = ""
        TACHE["fini"] = True
        TACHE["code"] = code
        TACHE["fin"] = time.time()
        lignes, duree = list(TACHE["lignes"]), round(TACHE["fin"] - TACHE["debut"])
    if code:   # échec : explication + fin du journal de la tâche
        c = conseil(lignes)
        journal(f"ÉCHEC / FAILED (code {code}, {duree} s)", *(["  -> " + c[0]] if c else []),
                *("    " + x for x in journal_en.traduire_lignes(lignes[-40:], langue.lire())))
    else:
        journal(f"OK ({duree} s)")
    try:
        os.remove(EN_COURS)
    except OSError:
        pass


def demarrer(titre, type_, commandes, apres=None):
    with VERROU:
        if not TACHE["fini"]:
            return False
        TACHE.update(id=TACHE["id"] + 1, titre=titre, type=type_, lignes=[], courante="", fini=False, code=None,
                     debut=time.time(), fin=0)
    try:
        os.makedirs(backup.BACKUP_DIR, exist_ok=True)
        with open(EN_COURS, "w", encoding="utf-8") as f:
            f.write(f"{os.getpid()} {time.time()}")
    except OSError:
        pass
    journal(f"Action : {titre} [{type_}]")
    threading.Thread(target=_executer, args=(commandes, apres), daemon=True).start()
    return True


# ---------- avant d'écrire, et après un échec (v1.30) ----------
PLACE_MIN = 200 * 1024 * 1024   # bundles réécrits + sauvegardes des originaux : ~50 Mo, marge large


class AutorisationMac(str):
    """message de probleme_ecriture : Gestion des apps de macOS (la page affiche le bouton « Ouvrir les Réglages »)"""


# Réglages Système > Confidentialité et sécurité > Gestion des apps (Ventura et après ; sinon la page Confidentialité)
REGLAGES_MAC = ["x-apple.systempreferences:com.apple.preference.security?Privacy_AppBundles",
                "x-apple.systempreferences:com.apple.preference.security?Privacy"]


def probleme_ecriture(g, T):
    """raison (texte) pour laquelle on ne pourra pas écrire, sinon None : place sur le disque du jeu et de l'app,
    bundles du jeu ouvrables en écriture (lecture seule, antivirus, fichier pris par Steam / FM), dossier backups"""
    aa = os.path.join(g, chemin_jeu.SOUS_DOSSIER_AA)
    for dossier in (aa, backup.BACKUP_DIR):
        try:
            libre = shutil.disk_usage(dossier).free
        except OSError:
            continue
        if libre < PLACE_MIN:
            disque = os.path.splitdrive(dossier)[0] or dossier
            return T(f"Plus assez de place sur le disque {disque} ({libre // 2**20} Mo libres, il en faut "
                     f"{PLACE_MIN // 2**20}) : libère de la place puis recommence.",
                     f"Not enough space on drive {disque} ({libre // 2**20} MB free, {PLACE_MIN // 2**20} needed): "
                     "free some space then try again.")
    for n in backup.FICHIERS:
        p = os.path.join(aa, n)
        if not os.path.exists(p):
            continue
        try:
            with open(p, "r+b"):   # rien n'est écrit : on regarde seulement si Windows le permet
                pass
        except PermissionError:   # (open() ne dit pas si le fichier est pris ou interdit : même erreur)
            if MAC:   # protection « Gestion des apps » : la page propose d'ouvrir le bon réglage (bouton)
                return AutorisationMac(T(
                    "macOS bloque l'écriture dans FM (fm.app). Clique « Ouvrir les Réglages » : dans « Gestion des "
                    "apps », active Terminal. Si macOS propose de quitter le Terminal, accepte, puis relance « Lancer "
                    "- Launch.command » et recommence.",
                    "macOS blocks writing into FM (fm.app). Click « Open Settings »: in « App Management », turn on "
                    "Terminal. If macOS offers to quit Terminal, accept, then start « Lancer - Launch.command » again "
                    "and retry."))
            if getattr(os.stat(p), "st_file_attributes", 0) & 1:   # FILE_ATTRIBUTE_READONLY
                return T("Des fichiers du jeu sont en lecture seule : vérifie les fichiers du jeu dans Steam (clic "
                         "droit sur FM 27 > Propriétés > Fichiers installés), puis recommence.",
                         "Some game files are read-only: verify the game files in Steam (right-click FM 27 > "
                         "Properties > Installed Files), then try again.")
            return T("Windows refuse d'écrire dans les fichiers du jeu : fichier utilisé par un autre programme "
                     "(Steam en train de mettre à jour ou de vérifier le jeu, FM) ou bloqué par l'antivirus "
                     "(« Dispositif d'accès contrôlé aux dossiers » de Windows Defender). Attends que Steam ait fini, "
                     "autorise l'app dans l'antivirus, puis recommence.",
                     "Windows refuses to write the game files: file used by another program (Steam updating or "
                     "verifying the game, FM) or blocked by the antivirus (Windows Defender \"Controlled folder "
                     "access\"). Wait for Steam to finish, allow the app in the antivirus, then try again.")
        except OSError:
            pass
    try:
        os.makedirs(backup.BACKUP_DIR, exist_ok=True)
        essai = os.path.join(backup.BACKUP_DIR, "essai_ecriture.tmp")
        with open(essai, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(essai)
    except OSError:
        return T("L'app ne peut pas écrire dans son propre dossier (backups) : antivirus ou dossier en lecture "
                 "seule. Réinstalle l'app avec le Setup, puis recommence.",
                 "The app cannot write in its own folder (backups): antivirus or read-only folder. Reinstall the "
                 "app with the Setup, then try again.")
    return None


# messages de Python ou de Windows dans le journal d'une tâche ratée -> explication simple (fr, en) ; 1er trouvé
CONSEILS = [
    (r"WinError 32|being used by another process|utilisé par un autre processus",
     ("Un fichier était utilisé par un autre programme (Steam, FM, antivirus). Ferme FM, attends que Steam ait fini, "
      "puis recommence.",
      "A file was used by another program (Steam, FM, antivirus). Close FM, wait for Steam to finish, then try "
      "again.")),
    (r"Errno 28|WinError 112|No space left|not enough space|espace (disque )?insuffisant",
     ("Le disque est plein : libère de la place puis recommence.", "The drive is full: free some space then try "
      "again.")),
    (r"PermissionError|WinError 5\b|Access is denied|Accès refusé",
     ("Windows a refusé l'écriture (antivirus ou fichier en lecture seule). Autorise l'app dans ton antivirus, ou "
      "vérifie les fichiers du jeu dans Steam, puis recommence.",
      "Windows refused to write (antivirus or read-only file). Allow the app in your antivirus, or verify the game "
      "files in Steam, then try again.")),
    (r"MemoryError",
     ("Pas assez de mémoire : ferme les autres programmes (FM, navigateur…) puis recommence.",
      "Not enough memory: close other programs (FM, browser…) then try again.")),
    (r"ModuleNotFoundError|No module named|ImportError",
     ("Les outils de l'app sont abîmés : réinstalle l'app avec le Setup (tes réglages sont gardés).",
      "The app's tools are damaged: reinstall the app with the Setup (your settings are kept).")),
    (r"URLError|timed out|getaddrinfo|ConnectionError|ConnectionReset|HTTP Error|SSL",
     ("Problème de connexion internet : vérifie ta connexion puis recommence.",
      "Internet connection problem: check your connection then try again.")),
    (r"FileNotFoundError.*\.bundle|No such file.*\.bundle",
     ("Un fichier du jeu est introuvable (jeu déplacé, désinstallé ou en cours de mise à jour). Vérifie le dossier "
      "du jeu dans l'app et les fichiers du jeu dans Steam.",
      "A game file was not found (game moved, uninstalled or updating). Check the game folder in the app and verify "
      "the game files in Steam.")),
    (r"struct\.error|EOFError|UnityPy|lz4|[Dd]ecompress|Traceback",
     ("Un fichier du jeu n'a pas pu être lu ou écrit. Vérifie les fichiers du jeu dans Steam (clic droit sur FM 27 > "
      "Propriétés > Fichiers installés), puis réinstalle le skin. Si ça recommence : copie le détail et envoie-le "
      "sur le Discord.",
      "A game file could not be read or written. Verify the game files in Steam (right-click FM 27 > Properties > "
      "Installed Files), then reinstall the skin. If it happens again: copy the details and send them on the "
      "Discord.")),
]


def conseil(lignes):
    texte = "\n".join(lignes[-80:])
    for motif, msg in CONSEILS:
        if re.search(motif, texte):
            return list(msg)
    return None


def tache_etat(depuis=0):
    with VERROU:
        t = dict(TACHE)
        t["lignes"] = TACHE["lignes"][depuis:]
        t["total"] = len(TACHE["lignes"])
        lignes = list(TACHE["lignes"])
    # tâche ratée : explication simple sous le titre (code 2 de la sauvegarde : encadré « pas propre » de la page)
    t["conseil"] = conseil(lignes) if t["fini"] and t["code"] and not (
        t["code"] == 2 and t["type"] in ("sauvegarde", "skin")) else None
    if t["type"] == "skin":   # avancement : titres « === » des fonctions, puis la barre de fin_ecriture
        titres = sum(1 for x in lignes if x.startswith("=== "))
        n = len(cat.ORDRE_SKIN) + 3   # + sauvegarde, essais, textes
        p = 0.92 * min(1, titres / n)
        m = re.search(r"\]\s+(\d+) %", t["courante"])
        if m and titres > n:
            p = 0.92 + 0.08 * int(m.group(1)) / 100
        t["avancement"] = 1.0 if t["fini"] else p
    elif t["type"] == "sauvegarde":   # sauvegarde_originaux.py tout : « [i/n] » par fichier
        fichiers = [m for x in lignes for m in re.findall(r"^\[(\d+)/(\d+)\]", x)]
        p = int(fichiers[-1][0]) / int(fichiers[-1][1]) if fichiers else 0
        t["avancement"] = 1.0 if t["fini"] else p
    elif t["type"] == "statut":   # statut.py écrit un point par fonction vérifiée
        t["avancement"] = 1.0 if t["fini"] else min(1, t["courante"].count(".") / len(cat.ORDRE_SKIN))
    elif t["type"] == "packs":   # packs_graphics.py : « [1/2] Décompression … NN % » (85 %), « [2/2] Rangement … NN % »
        m = re.search(r"\[(\d)/2\][^%]*?(\d+) %", t["courante"] or (lignes[-1] if lignes else ""))
        p = (0 if m.group(1) == "1" else 0.85) + (0.85 if m.group(1) == "1" else 0.15) * int(m.group(2)) / 100 if m else 0
        t["avancement"] = 1.0 if t["fini"] else p
    elif t["type"] == "maj":   # téléchargement « … 45 % » (90 %), puis la copie
        m = re.search(r"(\d+) %", t["courante"])
        p = 0.9 if any("sha256" in x or "Empreinte" in x or "Hash" in x for x in lignes) else (0.9 * int(m.group(1)) / 100 if m else 0)
        t["avancement"] = 1.0 if t["fini"] else p
    # v1.33 : détail en anglais pour toutes les langues sauf le français (les lignes gardées restent brutes : conseils,
    # avancement)
    lg = langue.lire()
    t["lignes"] = journal_en.traduire_lignes(t["lignes"], lg)
    t["courante"] = journal_en.traduire_lignes([t["courante"]], lg)[0]
    return t


# ---------- actions ----------
ECRIT = {"skin", "desinstaller", "appliquer", "reinstaller", "retirer", "option", "fond", "fond_retirer", "couleurs", "couleurs_retirer",
         "theme", "langue", "joueur_lot"}   # FM doit être fermé
# section Joueur de l'app (2026-11-11, le joueur : toute la fiche joueur en un endroit, maquette + « Appliquer »)
JOUEUR_CATS = ("joueur_entete", "joueur_fiche", "joueur_infobulle", "joueur_progression")
# (vue FM Guru et fiche Kinito 1080p : exclusives, restent dans Features additionnelles, pas ici — le joueur)
JOUEUR_FONCTIONS = [n for n, f in cat.FONCTIONS.items() if f["cat"] in JOUEUR_CATS]
JOUEUR_OPTIONS = ["entete_vue", "pour_contre_lignes", "fiche_large_colonne", "fiche_medium_colonne"]
# tuiles du bas de la fiche (noms de FM, = fiche_ordre_tuiles.ORDRE) : ordre au glisser-déposer (options.ordre_tuiles)
TUILES_BAS = ["Happiness", "FItness", "PlayerSeasonStats", "CareerStats", "PlayerForm", "PlayerTrainingOverview"]
SANS_OUTILS = {"langue_choisir", "python_installer", "jeu_enregistrer", "jeu_parcourir", "jeu_detecter", "lien",
               "maj_verifier", "maj", "maj_oublier", "autre_maj_accepter", "stades_parcourir", "stades_enregistrer",
               "stades_ouvrir", "stades_actualiser", "stades_verifier", "stades_reparer", "stades_ouvrir_graphics",
               "stades_diag", "stades_reconfigurer",
               "stades_migrer", "mes_themes", "journal_ouvrir", "app_ouvrir", "logs_fm_ouvrir",
               "noms_verifier", "noms_choisir", "noms_appliquer", "noms_retirer", "noms_ouvrir",
               "sigles_verifier", "sigles_poser", "sigles_retirer", "packs_etat", "packs_choisir", "packs",
               "packs_ouvrir"}
# réseaux de l'auteur (carte « Me retrouver » de l'accueil) + Kinito (titre de sa section dans Options) + pack de
# photos de stades (page Dossier du jeu) : seuls liens que la page peut faire ouvrir
LIENS = {
    "youtube": "https://www.youtube.com/@AlexJeuVideal",
    "twitch": "https://www.twitch.tv/alexjeuvideal",
    "discord": "https://discord.com/invite/tuADR5ZE2X",
    "x": "https://x.com/AlexJeuVideal",
    "dons": "https://streamlabs.com/alexjeuvideal/tip",   # v1.63 : carte « Me retrouver », bouton Donations
    "kinito": "https://linktr.ee/kiniitooo",
    "pack_stades": "https://mega.nz/file/aNhU1IqB#55xZ55vz7lXzWv4S9Qirttrikg6GGER1OtRnzj6_DGo",   # v1.73 : STADIUM<id du stade>
    "pack_trophees": "https://mega.nz/file/jYhT1KjC#AABqXRwAEABTofRe5_OluAAAAAAAAAAAFe67CqWy24w",   # v1.73 : TROPHY + comp/trophy
    # v1.78 : page « Vrais noms » = fix de FM Scout (pas notre travail) : leur page + leur X
    "fmscout_fix": "https://www.fmscout.com/a-fm27-real-names-license-fix.html#instructions",
    "fmscout_x": "https://x.com/fmscout",
    # 2026-11-12 : pages « Logos » / « Visages » = packs d'autres sites (pas notre travail), l'app les range seulement
    "tcm_logos": "https://www.tcmlogos.com/fr/tcm27-logos-fm27/",
    "df11_faces": "https://www.df11faces.com/post/df11-faces-classic-megapack-fm27",
    "7zip": "https://www.7-zip.org/",
}
_noms_source = {"chemin": ""}   # zip / dossier de FM Scout choisi à la main (sinon : trouvé dans Téléchargements / Bureau)
COULEUR = HEXA + r"|[A-Za-zéè\- ]{2,30}"


def parcourir(titre):
    """fenêtre de choix d'un dossier (tkinter ; Linux : zenity / kdialog d'abord ; Mac : fenêtre du Finder par
    osascript, tkinter ne marche pas hors du fil principal) ; renvoie le chemin ou ''"""
    if MAC:
        titre_as = titre.replace("\\", "\\\\").replace('"', '\\"')
        # « me » = osascript lui-même (pas d'autorisation d'automatisation) ; invisibles : ~/Library est caché
        script = (f'tell me to activate\n'
                  f'POSIX path of (choose folder with prompt "{titre_as}" '
                  f'default location (path to home folder) with invisibles)')
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            return r.stdout.strip().rstrip("/") if r.returncode == 0 else ""
        except OSError:
            return ""
    if not WINDOWS:
        for cmd in (["zenity", "--file-selection", "--directory", f"--title={titre}"],
                    ["kdialog", "--getexistingdirectory", os.path.expanduser("~"), "--title", titre]):
            if shutil.which(cmd[0]):
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    return r.stdout.strip() if r.returncode == 0 else ""
                except OSError:
                    pass
    try:
        import tkinter
        from tkinter import filedialog
        racine = tkinter.Tk()
    except Exception:   # tkinter absent (Linux : paquet python3-tk) ou pas d'écran
        return ""
    racine.withdraw()
    racine.attributes("-topmost", True)
    try:
        return filedialog.askdirectory(parent=racine, title=titre, mustexist=True) or ""
    finally:
        racine.destroy()


def parcourir_fichier(titre, dossier="", archives=False):
    """fenêtre de choix d'un fichier .zip (archives : aussi .rar / .7z / morceaux) (tkinter ; Linux : zenity /
    kdialog d'abord) ; renvoie le chemin ou ''"""
    exts = ["zip", "rar", "7z", "001"] if archives else ["zip"]
    if MAC:   # Finder par osascript (comme parcourir)
        titre_as = titre.replace("\\", "\\\\").replace('"', '\\"')
        lieu = "(path to downloads folder)"
        if dossier and os.path.isdir(dossier):
            lieu = '(POSIX file "' + dossier.replace("\\", "\\\\").replace('"', '\\"') + '")'
        types = "" if archives else ' of type {"zip", "public.zip-archive"}'   # .rar / .7z : pas d'UTI sûr
        script = (f'tell me to activate\n'
                  f'POSIX path of (choose file with prompt "{titre_as}"{types} '
                  f'default location {lieu})')
        try:
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            return r.stdout.strip() if r.returncode == 0 else ""
        except OSError:
            return ""
    if not WINDOWS:
        motif = " ".join("*." + e for e in exts)
        for cmd in (["zenity", "--file-selection", f"--title={titre}", f"--file-filter={motif}"],
                    ["kdialog", "--getopenfilename", dossier or os.path.expanduser("~"), motif, "--title", titre]):
            if shutil.which(cmd[0]):
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    return r.stdout.strip() if r.returncode == 0 else ""
                except OSError:
                    pass
    try:
        import tkinter
        from tkinter import filedialog
        racine = tkinter.Tk()
    except Exception:
        return ""
    racine.withdraw()
    racine.attributes("-topmost", True)
    try:
        return filedialog.askopenfilename(parent=racine, title=titre, initialdir=dossier or None,
                                          filetypes=[(" / ".join(exts), " ".join("*." + e for e in exts)),
                                                     ("*", "*.*")]) or ""
    finally:
        racine.destroy()


def ouvrir_dossier(d):
    """explorateur de fichiers sur un dossier (Linux : xdg-open ; Mac : open, Finder ou l'app du fichier)"""
    if WINDOWS:
        os.startfile(d)
    elif MAC:
        subprocess.Popen(["open", d], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    else:
        subprocess.Popen(["xdg-open", d], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)


def action(d):
    """renvoie (code http, réponse)"""
    typ = d.get("type")
    lg = langue.lire()
    T = (lambda fr, en: langue.traduire(fr, en, lg))
    if typ not in SANS_OUTILS and not python_ok():
        return 409, {"message": T("Les outils ne sont pas encore installés (étape 2 de l'installation).",
                                  "The tools are not installed yet (step 2 of the setup).")}
    if typ in ECRIT and fm_ouvert():
        return 409, {"message": T("FM est ouvert : ferme le jeu puis recommence.",
                                  "FM is running: close the game and try again.")}
    if typ in ECRIT and autre_maj_bloque(jeu()):
        return 409, {"message": T("Ton FM a été mis à jour mais pas encore le skin : mets le skin à jour, ou accepte "
                                  "le risque sur l'Accueil.",
                                  "Your FM was updated but the skin not yet: update the skin, or accept the risk on "
                                  "the Home page.")}
    nom = d.get("nom")
    if typ in ("appliquer", "retirer", "etat_fonction") and nom not in cat.FONCTIONS:
        return 400, {"message": "fonction inconnue"}
    lancer_py = os.path.join(COMMUN, "lancer.py")
    apres = None

    # --- assistant : sans tâche ---
    if typ == "langue_choisir":
        nl = d.get("langue")
        if nl not in langue.LANGUES:
            return 400, {"message": "langue inconnue"}
        if installe() and nl != lg:   # skin déjà posé : ses textes doivent suivre (tâche « langue » ci-dessous)
            if fm_ouvert() or autre_maj_bloque(jeu()):
                return 409, {"message": T("Impossible maintenant (FM ouvert, ou skin pas à jour pour ton FM).",
                                          "Not possible now (FM running, or skin not up to date for your FM).")}
            typ = "langue"
            d["langue"] = nl
        else:
            os.makedirs(backup.BACKUP_DIR, exist_ok=True)
            with open(langue.FICHIER, "w", encoding="utf-8") as f:
                f.write(nl)
            return 200, {"message": "ok"}
    if typ == "mes_themes":   # page Couleurs : la liste entière des thèmes du joueur (sauvegarde, renommage, import...)
        themes = themes_propres(d.get("themes"))
        os.makedirs(backup.BACKUP_DIR, exist_ok=True)
        with open(MES_THEMES + ".tmp", "w", encoding="utf-8") as f:
            json.dump(themes, f, ensure_ascii=False, indent=1)
        os.replace(MES_THEMES + ".tmp", MES_THEMES)
        return 200, {"themes": themes}
    if typ == "lien":   # navigateur par défaut (pas la fenêtre de l'app)
        if d.get("nom") not in LIENS:
            return 400, {"message": "lien inconnu"}
        if not LIENS[d["nom"]]:
            return 400, {"message": T("Lien pas encore disponible : il arrive dans une prochaine mise à jour.",
                                      "Link not available yet: it comes in a next update.")}
        webbrowser.open(LIENS[d["nom"]])
        return 200, {"message": "ok"}
    if typ == "jeu_detecter":
        _detecte["fait"] = False
        return 200, {"chemin": detecte()}
    if typ == "jeu_parcourir":
        return 200, {"chemin": chemin_jeu.nettoyer(parcourir(T(f"Dossier de FM27 (celui qui contient {chemin_jeu.PROGRAMME})",
                                                                 f"FM27 folder (the one containing {chemin_jeu.PROGRAMME})")))}
    if typ == "jeu_enregistrer":
        c = chemin_jeu.nettoyer(d.get("chemin") or "")
        if not chemin_jeu.valide(c):
            return 400, {"message": T(f"Ce n'est pas le dossier de FM27 : il faut celui qui contient {chemin_jeu.CONTENU_JEU}.",
                                      f"This is not the FM27 folder: it must be the one containing {chemin_jeu.CONTENU_JEU_EN}.")}
        os.makedirs(backup.BACKUP_DIR, exist_ok=True)
        with open(chemin_jeu.FICHIER, "w", encoding="utf-8") as f:
            f.write(c)
        return 200, {"message": "ok", "chemin": c}
    if typ == "stades_parcourir":
        ou_fm = stades_photos.dossier_fm() if MAC else "Documents\\Sports Interactive\\Football Manager 27"
        return 200, {"chemin": stades_photos.nettoyer(parcourir(T(f"Dossier graphics de FM 27 (dans {ou_fm})",
                                                                    f"FM 27 graphics folder (in {ou_fm})")))}
    if typ == "stades_enregistrer":   # chemin vide : dossier de base
        c = stades_photos.enregistrer(d.get("chemin") or "")
        if c is None:
            return 400, {"message": T("Ce dossier n'existe pas.", "This folder does not exist.")}
        if os.path.exists(os.path.join(backup.BACKUP_DIR, "club_page_bas.actif")):
            try:   # dossier des photos + config.xml tout de suite (rien à faire dans les bundles)
                stades_photos.ecrire()
            except OSError:
                pass
        try:   # même dossier graphics pour les trophées
            trophees_photos.ecrire()
        except OSError:
            pass
        return 200, {"message": "ok", "chemin": c}
    if typ == "stades_actualiser":   # bouton « Mettre à jour les photos » : config.xml refait sans relancer l'app
        if not os.path.isdir(stades_photos.graphics()):
            return 400, {"message": T("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le ci-dessous.",
                                      "graphics folder not found: start FM 27 once, or pick it below.")}
        _, n = stades_photos.ecrire()
        return 200, {"message": "ok", "photos": n}
    if typ == "stades_verifier":   # page Stades : config.xml refait + état complet (dossier en double, pack pas décompressé…)
        bloque = ""
        try:   # écriture refusée : souvent « Dossiers protégés » de Windows Defender ou un antivirus (Documents)
            if stades_photos.preparer():
                stades_photos.ecrire()
        except OSError as e:
            bloque = e.strerror or str(e)
        py = [p for p in (os.path.join(os.path.dirname(sys.executable), x) for x in ("python.exe", "pythonw.exe"))
              if os.path.exists(p)] or [sys.executable]   # à autoriser dans l'antivirus (app = pythonw, skin = python)
        g = jeu()   # marqueur posé mais fichiers remis par FM (MAJ, vérification Steam) : la page club n'est plus là
        D = stades_photos.diagnostic(fm_ouvert())
        comp = D["fm_lu"].get("comp")   # FM n'a pas tout chargé : un autre pack bloque peut-être (scan ~7 s)
        if D["graphics_ok"] and D["photos"] and comp is not None and comp < D["config_attendu"]:
            D["scan"] = stades_photos.scan_configs()
        return 200, dict(D, message="ok", bloque=bloque, python=py,
                         fm=os.path.isdir(stades_photos.dossier_fm()), remplaces=bool(g and maj_jeu(g)))
    if typ == "stades_reconfigurer":   # FMVE Stadium seul refait + scan des autres (lus seulement), FM fermé
        if fm_ouvert():
            return 409, {"message": T("Ferme FM avant de reconfigurer FMVE Stadium.", "Close FM before reconfiguring FMVE Stadium.")}
        if not stades_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable.", "graphics folder not found.")}
        try:
            R = stades_photos.reconfigurer()
        except OSError as e:
            return 500, {"message": T("Impossible de reconfigurer FMVE Stadium : ", "Couldn't reconfigure FMVE Stadium: ") + (e.strerror or str(e))}
        journal(f"FMVE Stadium reconfiguré / reconfigured : {R['sortis']} sortis, {R['photos']} photos, "
                f"{len(R['scan']['suspects'])} conflit(s)")
        g = jeu()
        return 200, dict(stades_photos.diagnostic(False), message="ok", scan=R["scan"], reconfig=R["sortis"],
                         fm=os.path.isdir(stades_photos.dossier_fm()), remplaces=bool(g and maj_jeu(g)))
    if typ == "stades_migrer":   # v1.73 : ancien pack (par id de club) -> STADIUM<id du stade> (obligatoire, alerte au démarrage)
        if fm_ouvert():
            return 409, {"message": T("Ferme FM avant de mettre à jour les photos.", "Close FM before updating the photos.")}
        if not stades_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable.", "graphics folder not found.")}
        try:
            n, rates, photos = stades_photos.migrer()
        except OSError as e:
            return 500, {"message": T("Impossible de renommer les photos : ", "Couldn't rename the photos: ") + (e.strerror or str(e))}
        journal(f"Photos des stades converties par stade / Stadium photos converted by stadium : {n} photos, "
                f"{rates} échec(s) / failed, {photos} clubs")
        if rates:
            return 500, {"message": T(f"{rates} photo(s) n'ont pas pu être renommées (FM ou un autre programme les "
                                      "utilise ?) : ferme-le et réessaie.",
                                      f"{rates} photo(s) couldn't be renamed (FM or another program using them?): "
                                      "close it and try again.")}
        g = jeu()
        return 200, dict(stades_photos.diagnostic(False), message="ok", renommees=n,
                         fm=os.path.isdir(stades_photos.dossier_fm()), remplaces=bool(g and maj_jeu(g)))
    if typ == "trophees_migrer":   # v1.73 : FMVE Trophies au format des packs d'internet (obligatoire, avec les stades)
        if fm_ouvert():
            return 409, {"message": T("Ferme FM avant de convertir les trophées.", "Close FM before converting the trophies.")}
        if not stades_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable.", "graphics folder not found.")}
        try:
            n, _, liees = trophees_photos.migrer()
        except OSError as e:
            return 500, {"message": T("Impossible de convertir les trophées : ", "Couldn't convert the trophies: ") + (e.strerror or str(e))}
        journal(f"Images des trophées converties / Trophy images converted : {n} images, {liees} compétitions / competitions")
        return 200, {"message": "ok", "renommees": n, "liees": liees}
    if typ == "stades_diag":   # bouton « Copier le diagnostic » : texte à coller sur Discord
        return 200, {"message": "ok", "texte": stades_diag()}
    if typ == "stades_reparer":   # photos d'un dossier mal placé (n° de la liste « egares ») remontées dans FMVE Stadium
        liste = stades_photos.egares()
        i = d.get("n")
        if not isinstance(i, int) or not 0 <= i < len(liste):
            return 400, {"message": T("Dossier introuvable : clique « Vérifier » puis réessaie.",
                                      "Folder not found: click « Check » and try again.")}
        try:
            n = stades_photos.reparer(liste[i][0])
        except OSError as e:
            return 400, {"message": T(f"Déplacement impossible ({e.strerror}) : ferme FM et l'explorateur, puis réessaie.",
                                      f"Could not move the photos ({e.strerror}): close FM and File Explorer, then try again.")}
        return 200, dict(stades_photos.diagnostic(), message="ok", deplacees=n,
                         fm=os.path.isdir(stades_photos.dossier_fm()))
    if typ == "stades_ouvrir_graphics":   # tuto, étape « décompresse dans graphics » (créé au besoin)
        if not stades_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le ci-dessous.",
                                      "graphics folder not found: start FM 27 once, or pick it below.")}
        ouvrir_dossier(stades_photos.graphics())
        return 200, {"message": "ok"}
    if typ == "stades_ouvrir":   # explorateur Windows sur le dossier des photos (créé au besoin)
        d_ = stades_photos.dossier()
        if not stades_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le ci-dessous.",
                                      "graphics folder not found: start FM 27 once, or pick it below.")}
        stades_photos.ecrire()
        os.makedirs(d_, exist_ok=True)
        ouvrir_dossier(d_)
        return 200, {"message": "ok"}
    # ---------- page « Images des trophées » (2026-11-09, comme les stades) ----------
    if typ == "trophees_verifier":   # config.xml refait + état complet (aucune image renommée : 2026-11-10)
        bloque = ""
        try:
            if trophees_photos.preparer():
                trophees_photos.ecrire()
        except OSError as e:
            bloque = e.strerror or str(e)
        py = [p for p in (os.path.join(os.path.dirname(sys.executable), x) for x in ("python.exe", "pythonw.exe"))
              if os.path.exists(p)] or [sys.executable]
        g = jeu()
        return 200, dict(trophees_photos.diagnostic(fm_ouvert()), message="ok", bloque=bloque, python=py,
                         fm=os.path.isdir(stades_photos.dossier_fm()),
                         remplaces=bool(g and maj_jeu(g)))
    if typ == "trophees_reparer":   # images d'un dossier mal placé (n° de la liste « egares ») -> FMVE Trophies
        liste = trophees_photos.egares()
        i = d.get("n")
        if not isinstance(i, int) or not 0 <= i < len(liste):
            return 400, {"message": T("Dossier introuvable : clique « Vérifier » puis réessaie.",
                                      "Folder not found: click « Check » and try again.")}
        try:
            n = trophees_photos.reparer(liste[i][0])
        except OSError as e:
            return 400, {"message": T(f"Déplacement impossible ({e.strerror}) : ferme FM et l'explorateur, puis réessaie.",
                                      f"Could not move the images ({e.strerror}): close FM and File Explorer, then try again.")}
        journal(f"Images des trophées réparées / Trophy images fixed : {n} ({liste[i][0]})")
        g = jeu()
        return 200, dict(trophees_photos.diagnostic(), message="ok", deplacees=n,
                         fm=os.path.isdir(stades_photos.dossier_fm()), remplaces=bool(g and maj_jeu(g)))
    if typ in ("trophees_ouvrir_graphics", "trophees_ouvrir"):   # explorateur sur graphics / sur FMVE Trophies
        if not trophees_photos.preparer():
            return 400, {"message": T("Dossier graphics introuvable : lance FM 27 une fois, ou choisis-le sur la page des stades.",
                                      "graphics folder not found: start FM 27 once, or pick it on the stadiums page.")}
        cible = stades_photos.graphics()
        if typ == "trophees_ouvrir":
            cible = trophees_photos.dossier()
            os.makedirs(cible, exist_ok=True)
            trophees_photos.ecrire()
        ouvrir_dossier(cible)
        return 200, {"message": "ok"}
    # ---------- page « Vrais noms » (v1.78) : fix de FM SCOUT, pas notre travail ; on n'en livre aucun fichier ----------
    if typ in ("noms_verifier", "noms_choisir", "noms_appliquer", "noms_retirer", "noms_ouvrir"):
        g = jeu()
        if typ == "noms_choisir":   # « Choisir le fichier… » : le zip téléchargé sur fmscout.com
            p = parcourir_fichier(T("Zip du fix de FM Scout (fm27-real-names-fix…zip)",
                                    "FM Scout fix zip (fm27-real-names-fix…zip)"),
                                  (noms_reels.dossiers_recherche() or [""])[0])
            if not p:
                return 200, dict(noms_reels.diagnostic(g, _noms_source["chemin"] or None), message="annule")
            try:
                noms_reels.lire_source(p)
            except (ValueError, OSError):
                return 400, {"message": T("Ce fichier n'est pas le fix de FM Scout : il faut leur zip (avec « FM27 Fix "
                                          "by FMScout.lnc » et « FM27 Club Names by FMScout.lnc »).",
                                          "This file is not the FM Scout fix: pick their zip (with « FM27 Fix by "
                                          "FMScout.lnc » and « FM27 Club Names by FMScout.lnc »).")}
            _noms_source["chemin"] = p
        if typ == "noms_ouvrir":   # explorateur sur le dossier de la base (2700)
            d_ = noms_reels.racine_db(g)
            if not os.path.isdir(d_):
                return 404, {"message": T("Introuvable : ", "Not found: ") + d_}
            ouvrir_dossier(d_)
            return 200, {"message": "ok"}
        if typ in ("noms_appliquer", "noms_retirer"):
            if fm_ouvert():
                return 409, {"message": T("FM est ouvert : ferme le jeu puis recommence.",
                                          "FM is running: close the game and try again.")}
            if not chemin_jeu.valide(g):
                return 400, {"message": T("Dossier du jeu pas trouvé : choisis-le dans « Dossier du jeu ».",
                                          "Game folder not found: pick it in « Game folder ».")}
            try:
                if typ == "noms_appliquer":
                    src = _noms_source["chemin"] or (noms_reels.trouver()[:1] or [("", 0)])[0][0]
                    if not src:
                        return 400, {"message": T("Zip de FM Scout pas trouvé : télécharge-le sur leur page, puis "
                                                  "« Choisir le fichier… ».",
                                                  "FM Scout zip not found: download it from their page, then « Pick "
                                                  "the file… ».")}
                    supp, cop = noms_reels.appliquer(g, src)
                    journal(f"Vrais noms (fix FM Scout) appliqué / Real names (FM Scout fix) applied : {supp} supprimés / "
                            f"deleted, {cop} copiés / copied ({os.path.basename(src)})")
                else:
                    remis, enl = noms_reels.retirer(g)
                    journal(f"Vrais noms (fix FM Scout) retiré / Real names (FM Scout fix) removed : {remis} remis / "
                            f"restored, {enl} enlevés / removed")
            except ValueError as e:
                return 400, {"message": str(e)}
            except OSError as e:
                return 400, {"message": T(f"Fichier du jeu bloqué ({e.strerror}) : ferme FM, puis relance l'app en "
                                          f"administrateur (clic droit sur le lanceur).",
                                          f"Game file locked ({e.strerror}): close FM, then run the app as "
                                          f"administrator (right-click the launcher).")}
        return 200, dict(noms_reels.diagnostic(g, _noms_source["chemin"] or None), message="ok",
                         fm_ouvert=bool(fm_ouvert()), jeu_ok=bool(chemin_jeu.valide(g)))
    # ---------- sigles à 3 lettres (2026-11-12) : .lnc du skin, avec ou sans le fix de FM Scout ----------
    if typ in ("sigles_verifier", "sigles_poser", "sigles_retirer"):
        g = jeu()
        if typ != "sigles_verifier":
            if fm_ouvert():
                return 409, {"message": T("FM est ouvert : ferme le jeu puis recommence.",
                                          "FM is running: close the game and try again.")}
            if not chemin_jeu.valide(g):
                return 400, {"message": T("Dossier du jeu pas trouvé : choisis-le dans « Dossier du jeu ».",
                                          "Game folder not found: pick it in « Game folder ».")}
            try:
                if typ == "sigles_poser":
                    ecr, clubs = sigles_clubs.poser(g)
                    journal(f"Sigles à 3 lettres posés / 3-letter names set : {clubs} clubs, {ecr} fichiers / files")
                else:
                    enl = sigles_clubs.retirer(g)
                    journal(f"Sigles à 3 lettres retirés / 3-letter names removed : {enl} fichiers / files")
            except ImportError:   # Linux / Mac, Python < 3.14 installé avant v1.85 : zstandard ajouté au .venv
                if not WINDOWS and os.path.exists(PY_OUTILS):
                    subprocess.run([PY_OUTILS, "-m", "pip", "install", "--disable-pip-version-check", "--no-input",
                                    "zstandard"], cwd=RACINE, stdin=subprocess.DEVNULL, capture_output=True)
                    return 400, {"message": T("Module de lecture de la base installé : ferme l'app, relance-la, puis "
                                              "clique encore sur ce bouton.",
                                              "Database reading module installed: close the app, start it again, "
                                              "then click this button again.")}
                return 400, {"message": T("Python de l'app sans zstd : réinstalle l'app.",
                                          "The app's Python has no zstd: reinstall the app.")}
            except ValueError as e:
                return 400, {"message": str(e)}
            except OSError as e:
                return 400, {"message": T(f"Fichier du jeu bloqué ({e.strerror}) : ferme FM, puis relance l'app en "
                                          f"administrateur (clic droit sur le lanceur).",
                                          f"Game file locked ({e.strerror}): close FM, then run the app as "
                                          f"administrator (right-click the launcher).")}
        return 200, dict(sigles_clubs.diagnostic(g), message="ok", fm_ouvert=bool(fm_ouvert()))
    # ---------- pages « Logos » / « Visages » (2026-11-12) : packs d'autres sites, rangés dans graphics ----------
    if typ == "packs_etat":
        return 200, dict(packs_graphics.etat(), message="ok")
    if typ == "packs_choisir":   # fichier téléchargé (.zip / .rar / .7z) ou dossier (déjà décompressé, plusieurs archives)
        if d.get("dossier"):
            p = parcourir(T("Dossier du pack (décompressé, ou qui contient les archives)",
                            "Pack folder (extracted, or containing the archives)"))
        else:
            p = parcourir_fichier(T("Fichier du pack téléchargé (.zip, .rar, .7z)",
                                    "Downloaded pack file (.zip, .rar, .7z)"),
                                  (noms_reels.dossiers_recherche() or [""])[0], archives=True)
        return 200, {"chemin": p or ""}
    if typ == "packs_ouvrir":   # explorateur sur graphics (créé au besoin)
        try:
            ouvrir_dossier(packs_graphics.graphics_pret())
        except packs_graphics.Erreur as e:
            return 400, {"message": T(str(e), "graphics folder not found: start FM 27 once, or pick your graphics "
                                              "folder on the « Game folder » page.")}
        return 200, {"message": "ok"}
    if typ in ("journal_ouvrir", "app_ouvrir", "logs_fm_ouvrir", "licence_ouvrir"):   # page Dépannage (v1.53)
        cible = {"journal_ouvrir": JOURNAL, "app_ouvrir": RACINE, "logs_fm_ouvrir": stades_photos.LOGS_FM,
                 "licence_ouvrir": os.path.join(RACINE, "LICENSE.txt")}[typ]
        if typ == "licence_ouvrir" and not os.path.exists(cible):   # UI PICKER : celle du partage
            cible = os.path.join(RACINE, "partage", "LICENSE.txt")
        if not os.path.exists(cible):
            return 404, {"message": T("Introuvable : ", "Not found: ") + cible}
        ouvrir_dossier(cible)
        return 200, {"message": "ok"}
    if typ == "maj_verifier":
        maj_verifier()
        return 200, {"message": "ok"}
    if typ == "autre_maj_accepter":   # « je comprends » : débloqué pour cette version de FM seulement
        os.makedirs(backup.BACKUP_DIR, exist_ok=True)
        with open(ACCEPTE, "w", encoding="utf-8") as f:
            f.write(backup.version_fm(os.path.join(jeu(), chemin_jeu.SOUS_DOSSIER_AA)))
        return 200, {"message": "ok"}
    if typ == "mac_reglages":   # bouton de la fenêtre « macOS bloque l'écriture » : le bon réglage, ouvert
        if not MAC:
            return 400, {"message": "Mac seulement / Mac only"}
        for url in REGLAGES_MAC:
            try:
                if subprocess.run(["open", url], capture_output=True, timeout=10).returncode == 0:
                    return 200, {"message": "ok"}
            except (OSError, subprocess.SubprocessError):
                pass
        return 400, {"message": T("Ouvre Réglages Système > Confidentialité et sécurité > Gestion des apps.",
                                  "Open System Settings > Privacy & Security > App Management.")}
    if typ == "maj_oublier":   # bandeau « réinstalle le skin » fermé
        mise_a_jour.oublier_fait()
        return 200, {"message": "ok"}

    # --- tâches ---
    if typ == "python_installer" and PY_OUTILS == _PY_EMB:   # Mac : python/ là, modules pas (internet coupé avant)
        cmds = [[PY_OUTILS, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", *MODULES]]
        titre = T("Installation des outils (UnityPy + Pillow)", "Installing the tools (UnityPy + Pillow)")
        apres = None
    elif typ == "python_installer":
        base = python_base()
        if not base and MAC:
            return 400, {"message": T(
                "Python n'a pas pu être préparé : vérifie ta connexion internet, ferme l'app et relance « Lancer - "
                "Launch.command » (il prépare Python tout seul). Sinon, installe Python 3.14 depuis python.org "
                "(« macOS 64-bit universal2 installer »), puis réessaie.",
                "Python could not be set up: check your internet connection, close the app and start « Lancer - "
                "Launch.command » again (it sets Python up by itself). Otherwise install Python 3.14 from python.org "
                "(« macOS 64-bit universal2 installer »), then try again.")}
        if not base and not WINDOWS:
            return 400, {"message": T(
                "Il faut Python 3.8 à 3.14 pour les outils du skin (pas 3.15, trop récent) : installe python3.14 et "
                "python3.14-venv avec le gestionnaire de paquets de ta distribution (tu peux garder l'autre), puis "
                "réessaie.",
                "The skin's tools need Python 3.8 to 3.14 (not 3.15, too new): install python3.14 and python3.14-venv "
                "with your distribution's package manager (you can keep the other one), then try again.")}
        if not base:
            return 400, {"message": T(
                "Ta version de Python est trop récente (ou trop ancienne) pour les outils du skin. Installe aussi "
                "Python 3.14 depuis python.org (tu peux garder l'autre), puis réessaie.",
                "Your Python version is too new (or too old) for the skin's tools. Also install Python 3.14 from "
                "python.org (you can keep the other one), then try again.")}
        cmds = [[base, "-m", "venv", VENV],
                [PY_OUTILS, "-m", "pip", "install", "--disable-pip-version-check", "--no-input", *MODULES]]
        titre = T("Installation des outils (UnityPy + Pillow)", "Installing the tools (UnityPy + Pillow)")

        def apres(code):
            if code and os.path.isdir(VENV):   # à moitié installé : on repart de zéro la prochaine fois
                shutil.rmtree(VENV, ignore_errors=True)
    elif typ == "sauvegarde":   # étape 3 de l'assistant : originaux sauvegardés tout de suite, s'ils sont propres
        cmds = [_python(os.path.join(COMMUN, "sauvegarde_originaux.py"), "tout")]
        titre = T("Sauvegarde des fichiers d'origine du jeu", "Backing up the game's original files")
    elif typ == "skin":
        cmds = []
        couleur = (d.get("couleur") or "").strip()
        infobulle = (d.get("infobulle") or "").strip()   # couleur secondaire : fond des infobulles seulement
        # thème choisi dans l'assistant : fond (+ infobulles) puis barres / accent posés d'abord, le choix 1 les garde
        vals = {k: (d.get(k) or "").strip() for k in ("barre", "barre2", "accent", *COULEURS_TACTIQUES,
                                                      *COULEURS_AUTRES)}
        vals.update({k: (d.get(k) or "").strip() for k in COULEURS_CONTINUER if k in d})   # (2026-11-11)
        if any(v and not couleur_ok(k, v) for k, v in vals.items()):
            return 400, {"message": T("Couleur pas comprise.", "Colour not understood.")}
        if couleur:
            if not re.fullmatch(COULEUR, couleur) or (infobulle and not re.fullmatch(COULEUR, infobulle)):
                return 400, {"message": T("Couleur pas comprise.", "Colour not understood.")}
            cmds.append(_python(lancer.chemin_script("theme_fond"), "appliquer", couleur,
                                *([infobulle] if infobulle else []),
                                *(["--lisse" if d["lisse"] else "--motifs"] if isinstance(d.get("lisse"), bool) else [])))
        if any(vals.values()) or d.get("continuer") in CONTINUER[1:]:   # theme / club   # texte des barres auto, trait auto (caché)
            cmds.append(_python(lancer.chemin_script("couleurs_interface"), "appliquer",
                                *(f"{k}={v or 'fm'}" for k, v in vals.items()), "texte=fm", "liseret=auto",
                                *continuer_arg(d)))
        cmds.append(_python(lancer_py, "skin", lg))
        titre = T("Installation de tout le skin", "Installing the whole skin")

        def apres(code):
            if not code:   # skin réinstallé : plus besoin du bandeau d'après mise à jour
                mise_a_jour.oublier_fait()   # (repère de la page « MAJ du jeu » : retiré par lancer.cmd_skin)
    elif typ == "packs":   # Python de l'app (bibliothèque standard) : décompresse et range dans graphics
        sorte, src = d.get("sorte"), (d.get("chemin") or "").strip()
        if sorte not in ("logos", "faces") or not src or not os.path.exists(src):
            return 400, {"message": T("Choisis d'abord le fichier téléchargé.", "Pick the downloaded file first.")}
        cmds = [[sys.executable, os.path.join(COMMUN, "packs_graphics.py"), "installer", sorte, src]]
        titre = (T("Installation des logos : ", "Installing the logos: ") if sorte == "logos"
                 else T("Installation des visages : ", "Installing the faces: ")) + os.path.basename(src)
    elif typ == "desinstaller":   # tout coupé + fichiers d'origine remis ; ensuite, activer une par une
        cmds = [_python(lancer_py, "desinstaller", lg)]
        titre = T("Désinstaller tout le skin", "Uninstall the whole skin")
    elif typ == "maj":   # Python de l'app (pas le .venv) : bibliothèque standard seulement
        if (MAJ["info"] or {}).get("etat") != "dispo":
            return 409, {"message": T("Pas de mise à jour à installer.", "No update to install.")}
        script = os.path.join(COMMUN, "mise_a_jour.py")
        cmds = [[sys.executable, script, "telecharger"], [sys.executable, script, "installer"]]
        titre = T("Mise à jour de l'app : ", "App update: ") + MAJ["info"]["distante"]
    elif typ == "appliquer" and bloque_guru(nom):
        return 409, {"message": T(*bloque_guru(nom))}
    elif typ in ("appliquer", "retirer"):   # + les fonctions qui retouchent ses modèles (catalogue.SUIVANTS)
        cmds = [_python(lancer.chemin_script(nom), typ)] + [_python(lancer.chemin_script(s), "si-actif")
                                                            for s in cat.SUIVANTS.get(nom, [])]
        titre = (T("Activer : ", "Enable: ") if typ == "appliquer" else T("Retirer : ", "Remove: ")) \
            + T(cat.FONCTIONS[nom]["fr"], cat.FONCTIONS[nom]["en"])
        if typ == "appliquer":
            def apres(code):
                if not code:
                    versions_posees.noter([nom] + suivants_poses(nom))
        elif lancer.actif(nom):
            # les scripts effacent leur marqueur AVANT d'écrire le jeu : retrait échoué (jeu pas propre, fichier
            # verrouillé...) = tuile éteinte mais fonction encore en jeu (vu chez un joueur, 2026-10-31) -> remis
            with open(lancer.marqueur(nom), "rb") as f:
                contenu = f.read()
            cmd_retrait = cmds[0]

            def apres(code):
                if code and TACHE.get("echec") == cmd_retrait and not lancer.actif(nom):
                    with open(lancer.marqueur(nom), "wb") as f:
                        f.write(contenu)
                    with VERROU:
                        TACHE["lignes"].append(T("Retrait échoué : la fonction reste activée (voir l'erreur au-dessus).",
                                                 "Removal failed: the feature stays enabled (see the error above)."))
    elif typ == "reinstaller":   # fonction activée (ou vue FM Guru choisie) qui a changé : reposée, interrupteur gardé
        if nom in cat.FONCTIONS:
            if not lancer.actif(nom) or bloque_guru(nom):
                return 409, {"message": T("Cette fonction n'est pas activée.", "This feature is not enabled.")}
            nom_t = T(cat.FONCTIONS[nom]["fr"], cat.FONCTIONS[nom]["en"])
        elif nom == "fiche_fmguru" and options.get("fiche_fmguru") == "guru":
            nom_t = "FM Guru"
        else:
            return 400, {"message": "fonction inconnue"}
        if nom == "fiche_fmguru" and lancer.restes_guru():
            # 2026-11-10 : autres fonctions posées en mode Guru (MAJ auto d'avant v1.75) : le choix 1 les coupe, remet
            # les fichiers d'origine et ne pose que la fiche (lancer.nettoyer_guru) ; il note lui-même ce qu'il pose
            avec = []
            cmds = [_python(lancer_py, "skin", lg)]
        elif nom == "fiche_fmguru":
            # 2026-11-07 : la carte FM Guru réinstalle aussi les fonctions de la vue qui ont changé (en-tête,
            # tuiles…), leurs suivants de la vue, puis la vue Guru elle-même en dernier
            avec = guru_a_reinstaller()
            for n in list(avec):
                avec += [s for s in cat.SUIVANTS.get(n, []) if s in cat.AVEC_GURU and lancer.actif(s) and s not in avec]
            avec = [n for n in cat.ORDRE_SKIN if n in avec]
            cmds = [_python(lancer.chemin_script(n), "si-actif") for n in avec + ["fiche_fmguru"]]
        else:
            avec = []
            cmds = [_python(lancer.chemin_script(nom), "si-actif")] + [_python(lancer.chemin_script(s), "si-actif")
                                                                       for s in cat.SUIVANTS.get(nom, [])]
        titre = T("Réinstaller : ", "Reinstall: ") + nom_t

        def apres(code):
            if not code:
                versions_posees.noter(avec + [nom] + suivants_poses(nom))
    elif typ == "joueur_lot":
        # section Joueur : tout le brouillon en une tâche, avec les commandes existantes (options.py choisir, scripts
        # appliquer / retirer + leurs SUIVANTS) ; vue FM Guru / Kinito 1080p pas ici (exclusives, Features additionnelles)
        fs, os_ = d.get("fonctions") or {}, d.get("options") or {}
        if not isinstance(fs, dict) or not isinstance(os_, dict) or any(n not in JOUEUR_FONCTIONS for n in fs) \
                or any(o not in JOUEUR_OPTIONS or v not in dict(options.OPTIONS[o]["valeurs"]) for o, v in os_.items()):
            return 400, {"message": "fonction ou option inconnue"}
        choix = lambda o, v: _python(os.path.join(COMMUN, "options.py"), "choisir", o, v)
        cmds = [choix(o, v) for o, v in os_.items() if v != options.get(o)]
        # ordre des tuiles du bas (glisser-déposer) : "skin" ou la liste ; posé en premier (lu si la fonction est activée ici)
        ordre = d.get("ordre_tuiles")
        if ordre is not None:
            if ordre != "skin" and not (isinstance(ordre, list) and sorted(ordre) == sorted(TUILES_BAS)):
                return 400, {"message": "ordre des tuiles inconnu"}
            if ordre == TUILES_BAS:
                ordre = "skin"
            if ordre != ("skin" if options.ordre_tuiles() in (None, TUILES_BAS) else options.ordre_tuiles()):
                cmds.insert(0, _python(os.path.join(COMMUN, "options.py"), "ordre_tuiles",
                                       ordre if ordre == "skin" else ",".join(ordre)))
        mettre = [n for n in cat.ORDRE_SKIN if n in fs and fs[n] and not lancer.actif(n)]
        retirer = [n for n in reversed(cat.ORDRE_SKIN) if n in fs and not fs[n] and lancer.actif(n)]
        if any(bloque_guru(n) for n in mettre):   # mode Guru choisi : seulement ce que la vue garde
            return 409, {"message": T(*bloque_guru(next(n for n in mettre if bloque_guru(n))))}
        for n, a in [(n, "retirer") for n in retirer] + [(n, "appliquer") for n in mettre]:
            cmds += [_python(lancer.chemin_script(n), a)] + [_python(lancer.chemin_script(s), "si-actif")
                                                            for s in cat.SUIVANTS.get(n, [])]
        if not cmds:
            return 400, {"message": T("Rien à appliquer : la fiche est déjà comme ça.", "Nothing to apply: the profile is already like this.")}
        titre = T("Fiche joueur : ", "Player profile: ") + str(len(cmds)) + T(" étape(s)", " step(s)")
        options_scripts = [options.OPTIONS[o]["script"] for o in os_]

        def apres(code):
            if not code:
                faits = [n for n in mettre + options_scripts if n in cat.FONCTIONS and lancer.actif(n)]
                versions_posees.noter([x for n in faits for x in [n] + suivants_poses(n)])
    elif typ == "etat_fonction":
        cmds = [_python(lancer.chemin_script(nom), "etat")]
        titre = T("État : ", "Status: ") + T(cat.FONCTIONS[nom]["fr"], cat.FONCTIONS[nom]["en"])
    elif typ == "option":
        o, v = d.get("nom"), d.get("valeur")
        if o not in options.OPTIONS or v not in dict(options.OPTIONS[o]["valeurs"]):
            return 400, {"message": "option inconnue"}
        cmds = [_python(os.path.join(COMMUN, "options.py"), "choisir", o, v)]
        titre = T("Option : ", "Option: ") + T(*options.OPTIONS[o]["titre"])

        def apres(code):   # (refaire_tout : le choix 1 lancé par options.py note lui-même ce qu'il pose)
            s = options.OPTIONS[o]["script"]
            if not code and not options.OPTIONS[o].get("refaire_tout") and s in cat.FONCTIONS and lancer.actif(s):
                versions_posees.noter([s] + suivants_poses(s))
    elif typ == "fond":
        couleur = (d.get("couleur") or "").strip()
        infobulle = (d.get("infobulle") or "").strip()
        if not re.fullmatch(COULEUR, couleur) or (infobulle and not re.fullmatch(COULEUR, infobulle)):
            return 400, {"message": T("Couleur pas comprise.", "Colour not understood.")}
        # fond lisse (case facultative de la page Couleurs) : envoyé à chaque fois, décoché = dessin de FM
        cmds = [_python(lancer.chemin_script("theme_fond"), "appliquer", couleur, *([infobulle] if infobulle else []),
                        "--lisse" if d.get("lisse") is True else "--motifs")]
        titre = T("Couleur du fond : ", "Background colour: ") + couleur + (T(" (lisse)", " (plain)") if d.get("lisse") is True else "")
    elif typ == "fond_retirer":
        cmds = [_python(lancer.chemin_script("theme_fond"), "retirer")]
        titre = T("Fond d'origine remis", "Original background back")
    elif typ == "couleurs":   # barres, texte, accent, Tactiques, tuiles, tableau de score : "" = FM (texte : auto)
        vals = {k: (d.get(k) or "").strip() for k in ("barre", "texte", "barre2", "accent", *COULEURS_TACTIQUES,
                                                      *COULEURS_AUTRES, *COULEURS_POSTES, *COULEURS_CONTINUER)}
        if any(v and not couleur_ok(k, v) for k, v in vals.items()):
            return 400, {"message": T("Couleur pas comprise.", "Colour not understood.")}
        liseret = d.get("liseret") if d.get("liseret") in ("cache", "fm") else "auto"   # trait entre les deux barres
        script = lancer.chemin_script("couleurs_interface")   # auto = caché dès qu'une couleur est choisie
        if (any(vals.values()) or liseret == "cache" or d.get("continuer") in CONTINUER
                or ombrage_arg(d) not in ([], ["ombrage=fm"]) or polygone_arg(d) not in ([], ["polygone=fm"])):
            cmds = [_python(script, "appliquer", *(f"{k}={v or 'fm'}" for k, v in vals.items()), f"liseret={liseret}",
                            *continuer_arg(d), *touche_arg(d), *ombrage_arg(d), *polygone_arg(d))]
        else:
            cmds = [_python(script, "retirer")]
        titre = T("Couleurs de l'interface", "Interface colours")
    elif typ == "couleurs_retirer":
        script = lancer.chemin_script("couleurs_interface")
        if any((couleurs() or {}).get(k) for k in COULEURS_POSTES):   # postes : changés seulement à la main (joueur)
            cmds = [_python(script, "appliquer", *(f"{k}=fm" for k in ("barre", "texte", "barre2", "accent",
                                                                        *COULEURS_TACTIQUES, *COULEURS_AUTRES,
                                                                        *COULEURS_CONTINUER)),
                            "liseret=fm", "continuer=auto", "ombrage=fm", "polygone=fm")]
        else:
            cmds = [_python(script, "retirer")]
        titre = T("Couleurs de FM remises", "FM colours back")
    elif typ == "theme":   # thème complet de la page Couleurs : fond (+ infobulles) puis barres / accent / Tactiques
        fond_c, info = (d.get("couleur") or "").strip(), (d.get("infobulle") or "").strip()
        vals = {k: (d.get(k) or "").strip() for k in ("barre", "texte", "barre2", "accent", *COULEURS_TACTIQUES,
                                                      *COULEURS_AUTRES)}
        # bouton Continuer en alerte… (2026-11-11) : seulement si la page les envoie (sinon celles en cours gardées)
        vals.update({k: (d.get(k) or "").strip() for k in COULEURS_CONTINUER if k in d})
        if (any(v and not re.fullmatch(HEXA, v) for v in (fond_c, info))
                or any(v and not couleur_ok(k, v) for k, v in vals.items())
                or (info and not fond_c)):
            return 400, {"message": T("Couleur pas comprise.", "Colour not understood.")}
        liseret = d.get("liseret") if d.get("liseret") in ("cache", "fm") else "auto"   # trait entre les barres
        script = lancer.chemin_script("couleurs_interface")
        fond_s = lancer.chemin_script("theme_fond")   # fond vide = fond de FM remis (thème « FM d'origine »)
        # fond lisse : celui du thème / de la case (2026-11-10) ; absent = celui déjà posé
        plat = ["--lisse" if d["lisse"] else "--motifs"] if isinstance(d.get("lisse"), bool) else []
        cmds = [_python(fond_s, "appliquer", fond_c, *([info] if info else []), *plat) if fond_c
                else _python(fond_s, "retirer"),
                # toujours « appliquer » (verts des Tactiques compris) ; rien de choisi du tout -> le script retire
                # de lui-même
                _python(script, "appliquer", *(f"{k}={v or 'fm'}" for k, v in vals.items()), f"liseret={liseret}",
                        *continuer_arg(d), *touche_arg(d), *ombrage_arg(d), *polygone_arg(d))]
        titre = T("Thème : ", "Theme: ") + (d.get("titre") or "").strip()[:40]
    elif typ == "statut":
        cmds = [_python(os.path.join(COMMUN, "statut.py"))]
        titre = T("Vérification de tout le skin", "Checking the whole skin")
    elif typ == "langue":
        nl = d.get("langue")
        if nl not in langue.LANGUES:
            return 400, {"message": "langue inconnue"}
        cmds = [_python(os.path.join(COMMUN, "langue.py"), nl), _python(lancer_py, "langue", nl)]
        titre = "Textes du skin en français" if nl == "fr" else f"Skin texts: {langue.NOMS[nl]}"
    else:
        return 400, {"message": "action inconnue"}
    if typ in ("fond", "couleurs", "theme"):   # couleurs reposées : leur version aussi
        def apres(code):
            if not code:
                versions_posees.noter([n for n in ("theme_fond", "couleurs_interface") if lancer.actif(n)])
    if typ in ECRIT or typ == "sauvegarde":   # place sur le disque, droits d'écriture (v1.30)
        probleme = probleme_ecriture(jeu(), T)
        if probleme:
            return 409, {"message": str(probleme), "mac_autorisation": isinstance(probleme, AutorisationMac)}
    if tache_ailleurs():   # app fermée pendant une tâche, puis rouverte : l'ancienne fenêtre écrit encore
        return 409, {"message": T("Une installation tourne encore (lancée avant de fermer l'app) : attends une "
                                  "minute qu'elle finisse, puis recommence.",
                                  "An installation is still running (started before the app was closed): wait a "
                                  "minute for it to finish, then try again.")}
    if typ in ECRIT - {"skin"} or typ == "statut":   # sauvegardes périmées (MAJ de FM) refaites d'abord (le skin
        cmds = [_python(os.path.join(COMMUN, "sauvegarde_originaux.py"), "rafraichir")] + cmds   # : tout() le fait)
    if not demarrer(titre, typ, cmds, apres):
        return 409, {"message": T("Une action est déjà en cours : attends qu'elle finisse.",
                                  "Something is already running: wait for it to finish.")}
    return 200, {"message": "ok"}


# ---------- serveur ----------
VU = {"t": time.time(), "ferme": 0}   # ferme : fenêtre fermée (signal de la page, 2026-11-05)
FERME_DELAI = 8   # s après la fermeture de la fenêtre sans nouvelle requête (rechargement = requêtes, page : 1 / 4 s)


class Gestion(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _envoyer(self, code, corps, type_="application/json; charset=utf-8"):
        if isinstance(corps, (dict, list)):
            corps = json.dumps(corps, ensure_ascii=False)
        data = corps if isinstance(corps, bytes) else corps.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        VU["t"] = time.time()
        VU["ferme"] = 0   # la page est (r)ouverte : annule un signal de fermeture
        if self.path in ("/", "/index.html"):
            with open(PAGE, encoding="utf-8") as f:
                page = f.read().replace("__JETON__", JETON)
            if MAC:   # textes de la page qui ne parlent que de Windows (fr / en ; les autres langues gardent les leurs)
                for avant, apres in TEXTES_MAC:
                    page = page.replace(avant, apres)
            self._envoyer(200, page, "text/html; charset=utf-8")
        elif self.path in ("/logo.png", "/icone.ico"):   # logo (barre du haut) ; icône (fenêtre, barre des tâches)
            fichier, typ = (LOGO, "image/png") if self.path == "/logo.png" else (ICONE, "image/x-icon")
            try:
                with open(fichier, "rb") as f:
                    self._envoyer(200, f.read(), typ)
            except OSError:
                self._envoyer(404, {"erreur": "introuvable"})
        elif self.path == "/api/etat":
            try:
                self._envoyer(200, etat())
            except Exception as e:   # la page affiche l'erreur au lieu de rester vide (détail dans app.log)
                import traceback
                traceback.print_exc()
                journal("Erreur de l'app / App error :", *traceback.format_exc().rstrip().splitlines())
                self._envoyer(500, {"message": f"{type(e).__name__}: {e}"})
        elif self.path == "/api/detecte":
            self._envoyer(200, {"chemin": detecte()})
        elif self.path == "/api/notes":   # bouton « Notes de mise à jour » de l'accueil (2026-11-12)
            self._envoyer(200, {"texte": notes_de_mise_a_jour()})
        elif self.path.startswith("/api/traduction"):   # v1.31 : {anglais: traduction} d'une langue (ni fr ni en)
            m = re.search(r"lg=([a-z]{2})", self.path)
            self._envoyer(200, langue.table(m.group(1)) if m else {})
        elif self.path.startswith("/api/tache"):
            m = re.search(r"depuis=(\d+)", self.path)
            self._envoyer(200, tache_etat(int(m.group(1)) if m else 0))
        else:
            self._envoyer(404, {"erreur": "introuvable"})

    def do_POST(self):
        VU["t"] = time.time()
        if self.path == "/api/fermee":   # sendBeacon de la page (pagehide) : pas d'en-tête possible, jeton dans le corps
            corps = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            if corps.decode("utf-8", "replace").strip() == JETON:
                VU["ferme"] = time.time()
            return self._envoyer(200, {"ok": True})
        if self.headers.get("X-Jeton") != JETON:
            return self._envoyer(403, {"erreur": "jeton"})
        VU["ferme"] = 0
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self._envoyer(400, {"erreur": "json"})
        if self.path == "/api/quitter":
            if not TACHE["fini"]:   # le script écrit dans le jeu : l'arrêter au milieu laisserait un fichier abîmé
                return self._envoyer(409, {"erreur": "tache"})
            self._envoyer(200, {"ok": True})
            threading.Thread(target=_arreter, daemon=True).start()
            return
        if self.path == "/api/redemarrer":   # après une mise à jour : nouvelle app sur le même port
            if not TACHE["fini"]:
                return self._envoyer(409, {"erreur": "tache"})
            self._envoyer(200, {"ok": True})
            threading.Thread(target=_redemarrer, daemon=True).start()
            return
        if self.path == "/api/action":
            try:
                code, rep = action(d)
            except Exception as e:   # noqa: BLE001
                import traceback
                journal(f"Erreur de l'app / App error ({d.get('type')}) :", *traceback.format_exc().rstrip().splitlines())
                code, rep = 500, {"message": f"{type(e).__name__}: {e}"}
            if code >= 400:   # refus (FM ouvert, disque plein…) : utile pour comprendre « ça ne fait rien »
                journal(f"Refusé / Refused [{d.get('type')} {d.get('nom') or ''}] : {rep.get('message')}")
            return self._envoyer(code, rep)
        self._envoyer(404, {"erreur": "introuvable"})


SERVEUR = None


def _arreter():
    time.sleep(0.3)
    SERVEUR.shutdown()


def _redemarrer():
    """lance la nouvelle app (elle attend que ce port se libère), puis s'arrête ; la page garde sa fenêtre"""
    time.sleep(0.3)
    port = str(SERVEUR.server_address[1])
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--sans-fenetre", "--port", port], cwd=RACINE,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=SANS_FENETRE, start_new_session=not WINDOWS)
    SERVEUR.shutdown()


def _port_demande():
    """--port N (redémarrage) : attend que l'ancienne app l'ait libéré (20 s au plus) ; 0 = n'importe lequel"""
    if "--port" not in sys.argv:
        return 0
    try:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    except (IndexError, ValueError):
        return 0
    import socket
    for _ in range(80):
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", port)):
                return port
        time.sleep(0.25)
    return 0


PACKS_AUTO = 120   # s : packs de stades / trophées posés pendant que l'app est ouverte -> pris tout seuls (FM fermé)


def _packs_auto():
    """config.xml de FMVE Stadium / Trophies + liens des autres packs refaits sans clic (2026-11-10, comme
    l'installation de Heffem mais sans réinstaller) ; seulement nos dossiers, seuls nos liens sont supprimés"""
    if fm_ouvert() or not TACHE["fini"]:
        return
    for actif, f in ((os.path.join(backup.BACKUP_DIR, "club_page_bas.actif"), stades_photos.ecrire),
                     (trophees_photos.MARKER_SKIN, trophees_photos.ecrire)):
        if os.path.exists(actif):
            try:
                f()
            except OSError:
                pass


def _surveiller():
    dernier = time.time()
    while True:
        time.sleep(1)
        if time.time() - dernier > PACKS_AUTO:
            dernier = time.time()
            threading.Thread(target=_packs_auto, daemon=True).start()
        # fenêtre fermée et pas rouverte / rechargée depuis : arrêt rapide (jamais pendant qu'un script écrit)
        fermee = VU["ferme"] and time.time() - VU["ferme"] > FERME_DELAI
        if TACHE["fini"] and (fermee or time.time() - VU["t"] > ARRET_SANS_PAGE):
            print("page fermée : arrêt de l'app / page closed: app stopped")
            SERVEUR.shutdown()
            return


# navigateurs qui savent ouvrir une fenêtre d'application (--app, sans barre d'adresse), dans cet ordre
NAVIGATEURS_APP = [
    os.path.join("Microsoft", "Edge", "Application", "msedge.exe"),
    os.path.join("Google", "Chrome", "Application", "chrome.exe"),
    os.path.join("BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
    os.path.join("Vivaldi", "Application", "vivaldi.exe"),
]


# Linux : les mêmes (et Chromium), trouvés dans le PATH ; Firefox n'a plus de mode application -> onglet
NAVIGATEURS_APP_LINUX = ["microsoft-edge", "microsoft-edge-stable", "google-chrome", "google-chrome-stable",
                         "chromium", "chromium-browser", "brave-browser", "brave", "vivaldi", "vivaldi-stable"]


# Mac : les mêmes navigateurs, en mode application (sans barre d'adresse) ; sinon le navigateur par défaut (Safari)
NAVIGATEURS_APP_MAC = ["Google Chrome", "Microsoft Edge", "Brave Browser", "Vivaldi", "Chromium"]

# textes de page.html propres à Windows, remplacés sur Mac (exacts, échappements JavaScript compris)
TEXTES_MAC = [
    ('"Le dossier de Football Manager 27 : celui qui contient fm.exe et fm_Data."',
     '"Le dossier de Football Manager 27 : celui qui contient fm.app (Steam : ~/Library/Application Support/Steam/'
     'steamapps/common/Football Manager 27)."'),
    ('"The Football Manager 27 folder: the one containing fm.exe and fm_Data."',
     '"The Football Manager 27 folder: the one containing fm.app (Steam: ~/Library/Application Support/Steam/'
     'steamapps/common/Football Manager 27)."'),
    ('placeholder: "C:\\\\…\\\\steamapps\\\\common\\\\Football Manager 27"',
     'placeholder: "~/Library/Application Support/Steam/steamapps/common/Football Manager 27"'),
    ("(fenêtre du .bat fermée ?)", "(fenêtre du Terminal fermée ?)"),
    ("(.bat window closed?)", "(Terminal window closed?)"),
    ("FM écrit les siens dans AppData\\\\LocalLow\\\\Sports Interactive\\\\Football Manager 27 :",
     "FM écrit les siens dans ~/Library/Logs/Sports Interactive/Football Manager 27 :"),
    ("FM writes its own in AppData\\\\LocalLow\\\\Sports Interactive\\\\Football Manager 27:",
     "FM writes its own in ~/Library/Logs/Sports Interactive/Football Manager 27:"),
    ("Si Windows ou ton antivirus bloque l'app ou Python", "Si macOS bloque l'app ou Python"),
]


def ouvrir(url):
    if MAC:
        for nom in NAVIGATEURS_APP_MAC:
            for base in ("/Applications", os.path.expanduser("~/Applications")):
                exe = os.path.join(base, nom + ".app", "Contents", "MacOS", nom)
                if os.path.exists(exe):
                    try:
                        subprocess.Popen([exe, f"--app={url}", "--window-size=1320,880"], stdin=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                        return
                    except OSError:
                        pass
        webbrowser.open(url)
        return
    if not WINDOWS:
        for nav in NAVIGATEURS_APP_LINUX:
            exe = shutil.which(nav)
            if exe:
                try:
                    subprocess.Popen([exe, f"--app={url}", "--window-size=1320,880"], stdin=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                    return
                except OSError:
                    pass
        webbrowser.open(url)
        return
    bases = [os.environ.get(v) for v in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA")]   # LOCALAPPDATA :
    for nav in NAVIGATEURS_APP:                                                                # installé pour 1 compte
        for base in bases:
            exe = os.path.join(base or "", nav)
            if base and os.path.exists(exe):
                try:
                    subprocess.Popen([exe, f"--app={url}", "--window-size=1320,880"], creationflags=SANS_FENETRE)
                    return
                except OSError:
                    pass
    webbrowser.open(url)   # sinon le navigateur par défaut (Firefox…), dans un onglet


def main():
    global SERVEUR
    try:   # options remises une fois après une MAJ (options.FORCES) : aussi pour un « Réinstaller » tuile par tuile
        options.appliquer_forces()
    except OSError:
        pass
    port = _port_demande()
    try:
        SERVEUR = ThreadingHTTPServer(("127.0.0.1", port), Gestion)
    except OSError:   # port pris : nouveau port, donc nouvelle fenêtre
        port = 0
        SERVEUR = ThreadingHTTPServer(("127.0.0.1", 0), Gestion)
    url = f"http://127.0.0.1:{SERVEUR.server_address[1]}/"
    fr = langue.lire() == "fr"
    print(("L'app est ouverte (" if fr else "The app is open (") + url + ")")
    print("Pour revenir au menu : bouton Quitter de l'app." if fr else "To go back to the menu: Quit button in the app.",
          flush=True)
    if "--sans-fenetre" not in sys.argv or ("--port" in sys.argv and not port):
        ouvrir(url)
    threading.Thread(target=journal_entete, daemon=True).start()   # (compat : ~1 s, pas avant la fenêtre)
    threading.Thread(target=detecte, daemon=True).start()   # recherche du jeu prête pour l'assistant
    threading.Thread(target=maj_verifier, daemon=True).start()   # rien (DEPOT vide) ou une requête à GitHub
    threading.Thread(target=stades_photos.compte, daemon=True).start()   # 1er comptage des photos (~5 s) en avance
    if os.path.exists(os.path.join(backup.BACKUP_DIR, "club_page_bas.actif")):
        def _stades():   # photos / packs de stades ajoutés depuis : liens par club refaits (rien dans les bundles)
            try:
                stades_photos.ecrire()
            except OSError:
                pass
        threading.Thread(target=_stades, daemon=True).start()   # v1.73 : lit les packs, pas avant la fenêtre
    if os.path.exists(trophees_photos.MARKER_SKIN):
        def _trophees():   # images / packs de trophées ajoutés depuis : liens refaits (v1.73 : lit les packs)
            try:
                trophees_photos.ecrire()
            except OSError:
                pass
        threading.Thread(target=_trophees, daemon=True).start()
    threading.Thread(target=_surveiller, daemon=True).start()
    SERVEUR.serve_forever()
    SERVEUR.server_close()   # port libéré tout de suite (redémarrage après une mise à jour)
    # 2026-11-05 (le joueur : plus aucun python après la fermeture) : fin nette du processus, même si un fil traîne
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except (OSError, ValueError):
        pass
    os._exit(0)


if __name__ == "__main__":
    main()
