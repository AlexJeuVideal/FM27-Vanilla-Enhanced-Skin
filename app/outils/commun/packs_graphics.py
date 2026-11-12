"""Packs de logos / visages d'AUTRES SITES (2026-11-12) : le joueur choisit le fichier qu'il a téléchargé (ou le
dossier), l'app le décompresse et range le pack au bon endroit dans graphics (dossier choisi dans l'app compris :
stades_photos.graphics()). Pas notre travail : l'app ne livre aucun de leurs fichiers.
Conseillés par l'app : logos TCM27 (tcmlogos.com), visages DF11 Classic Megapack (df11faces.com).

Décompression : .zip par Python ; .rar / .7z par 7-Zip, WinRAR (UnRAR), sinon tar de Windows 10/11 (bsdtar) ou de
Mac / Linux (bsdtar). D'abord dans « graphics (installation en cours) » (à côté de graphics, même disque : FM ne le
lit pas), puis le dossier du pack (celui qui contient les config.xml, sans dossier en double) est déplacé dans
graphics\\<nom du pack> ; s'il existe déjà (mise à jour mensuelle) : fusion, fichiers remplacés.

Bibliothèque standard seulement (Python de l'app, sans les outils du skin).
Usage : packs_graphics.py installer <logos|faces> <fichier ou dossier>
        packs_graphics.py etat     -> json
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemin_jeu  # noqa: E402
import stades_photos  # noqa: E402  (dossier graphics, choisi dans l'app ou de base)

WINDOWS, MAC = chemin_jeu.WINDOWS, chemin_jeu.MAC
TEMP = "graphics (installation en cours)"   # à côté de graphics : FM ne le lit pas
SANS_FENETRE = 0x08000000 if WINDOWS else 0   # CREATE_NO_WINDOW : 7z / tar sans console
INUTILES = {"__macosx", ".ds_store", "thumbs.db", "desktop.ini"}
PACK_EXTS = (".png", ".jpg", ".jpeg", ".xml", ".txt", ".pdf", ".url", ".nfo", ".md", ".html", ".htm", ".rtf")
FOURRE_TOUT = {"downloads", "téléchargements", "telechargements", "desktop", "bureau", "documents", "onedrive"}
NOTRES = (stades_photos.DOSSIER.lower(), stades_photos.LIENS.lower(), "fmve trophies", "fmve trophies links")
PREMIERE = re.compile(r"\.(zip|rar|7z|tar|tgz|tar\.gz|001)$", re.I)
SUITE = re.compile(r"(\.part0*(?:[2-9]|\d{2,})\.rar|\.(?:7z|zip|rar)\.0*(?:[2-9]|\d{2,})|\.z\d\d|\.r\d\d)$", re.I)


class Erreur(Exception):
    """message pour le joueur (déjà en français ; le journal de l'app le traduit)"""


def ecrire(texte, fin="\n"):
    sys.stdout.write(texte + fin)
    sys.stdout.flush()


# ---------- fichier choisi ----------
def premiere_partie(p):
    """archive en plusieurs morceaux : x.part2.rar -> x.part1.rar ; x.7z.003 -> x.7z.001 ; x.z01 -> x.zip ;
    x.r00 -> x.rar (le premier morceau, s'il est à côté)"""
    d, n = os.path.split(p)
    essais = []
    m = re.match(r"^(.*\.part)(\d+)(\.rar)$", n, re.I)
    if m:
        essais = [m.group(1) + "1".zfill(len(m.group(2))) + m.group(3), m.group(1) + "1" + m.group(3)]
    m = re.match(r"^(.*\.(?:7z|zip|rar))\.(\d+)$", n, re.I)
    if m:
        essais = [m.group(1) + "." + "1".zfill(len(m.group(2)))]
    m = re.match(r"^(.*)\.(z|r)\d\d$", n, re.I)
    if m:
        essais = [m.group(1) + (".zip" if m.group(2).lower() == "z" else ".rar")]
    for e in essais:
        if os.path.isfile(os.path.join(d, e)):
            return os.path.join(d, e)
    return p


def archive(p):
    return os.path.isfile(p) and bool(PREMIERE.search(p)) and not SUITE.search(p)


def nom_archive(p):
    n = os.path.basename(p)
    n = re.sub(r"(\.part\d+)?\.(zip|rar|7z|tar|tgz|tar\.gz)(\.\d+)?$", "", n, flags=re.I)
    return re.sub(r"[<>:\"/\\|?*]", "_", n).strip(" .") or "Pack"


def morceaux(p):
    """taille de l'archive avec tous ses morceaux (x.part*.rar, x.7z.0*, x.z01…)"""
    d, n = os.path.split(p)
    base = re.sub(r"(\.part\d+\.rar|\.(?:7z|zip|rar)\.\d+|\.zip|\.rar|\.7z)$", "", n, flags=re.I).lower()
    total = 0
    for f in os.listdir(d):
        fl = f.lower()
        if fl == n.lower() or (fl.startswith(base) and (SUITE.search(fl) or PREMIERE.search(fl))):
            try:
                total += os.path.getsize(os.path.join(d, f))
            except OSError:
                pass
    return total or os.path.getsize(p)


# ---------- outils de décompression ----------
def outils():
    """[(sorte, chemin)] : 7z, unrar, winrar, bsdtar (dans cet ordre de préférence)"""
    r = []
    if WINDOWS:
        bases = [os.environ.get(v) for v in ("ProgramW6432", "ProgramFiles", "ProgramFiles(x86)")]
        for b in dict.fromkeys(x for x in bases if x):
            for sorte, rel in (("7z", r"7-Zip\7z.exe"), ("7z", r"7-Zip-Zstandard\7z.exe"),
                               ("unrar", r"WinRAR\UnRAR.exe"), ("winrar", r"WinRAR\WinRAR.exe")):
                if os.path.isfile(os.path.join(b, rel)):
                    r.append((sorte, os.path.join(b, rel)))
        tar = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "tar.exe")
        if os.path.isfile(tar):
            r.append(("bsdtar", tar))
    else:
        chemins = os.pathsep.join([os.environ.get("PATH", ""), "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"])
        for sorte, noms in (("7z", ("7zz", "7z", "7za")), ("unrar", ("unrar",)), ("bsdtar", ("bsdtar",))):
            for n in noms:
                w = shutil.which(n, path=chemins)
                if w:
                    r.append((sorte, w))
                    break
        if MAC and not any(s == "bsdtar" for s, _ in r) and os.path.isfile("/usr/bin/tar"):
            r.append(("bsdtar", "/usr/bin/tar"))   # tar de macOS = bsdtar (lit .rar et .7z)
    return r


def _commande(sorte, exe, arc, dest):
    if sorte == "7z":
        return [exe, "x", "-y", "-bso0", "-bsp0", "-o" + dest, arc]
    if sorte == "unrar":
        return [exe, "x", "-o+", "-y", "-idq", arc, dest + os.sep]
    if sorte == "winrar":
        return [exe, "x", "-ibck", "-y", "-o+", arc, dest + os.sep]
    return [exe, "-xf", arc, "-C", dest]


def _avancement(debut, attendu, libre0, dest, texte):
    """« NN % » d'après la place prise sur le disque (images : presque pas compressées dans l'archive)"""
    try:
        ecrit = max(0, libre0 - shutil.disk_usage(dest).free)
    except OSError:
        return
    p = min(99, int(100 * ecrit / attendu)) if attendu else 0
    ecrire(f"{texte} {p} % ({ecrit / 2**30:.1f} Go, {int(time.time() - debut)} s)", fin="\r")


def _externe(arc, dest, attendu, texte):
    """décompression par un outil du système ; essaie les suivants si l'un échoue. Renvoie True si réussi"""
    ext = arc.lower()
    vus = []
    for sorte, exe in outils():
        if sorte == "unrar" and not re.search(r"\.rar$", ext):
            continue
        if sorte == "bsdtar" and any(s in ("7z", "winrar") for s in vus):
            continue   # tar seulement si rien de mieux n'a marché
        vus.append(sorte)
        os.makedirs(dest, exist_ok=True)
        journal = os.path.join(os.path.dirname(dest), "decompression.log")
        libre0, debut = shutil.disk_usage(dest).free, time.time()
        with open(journal, "w", encoding="utf-8", errors="replace") as f:
            try:
                p = subprocess.Popen(_commande(sorte, exe, arc, dest), stdout=f, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, creationflags=SANS_FENETRE)
            except OSError as e:
                ecrire(f"{os.path.basename(exe)} : {e}")
                continue
            while p.poll() is None:
                time.sleep(1)
                _avancement(debut, attendu, libre0, dest, texte)
        if p.returncode == 0:
            ecrire(f"{texte} 100 %")
            os.remove(journal)
            return True
        try:
            with open(journal, encoding="utf-8", errors="replace") as f:
                fin = [x.strip() for x in f.read().splitlines() if x.strip()][-4:]
        except OSError:
            fin = []
        ecrire(f"{os.path.basename(exe)} : échec (code {p.returncode}) " + " | ".join(fin))
        os.remove(journal)
        shutil.rmtree(dest, ignore_errors=True)   # rien de mélangé avant l'essai suivant
    return False


def _zip(arc, dest, texte):
    with zipfile.ZipFile(arc) as z:
        infos = z.infolist()
        total = sum(i.file_size for i in infos) or 1
        fait, dernier = 0, 0
        for i in infos:
            z.extract(i, dest)
            fait += i.file_size
            if time.time() - dernier > 0.5:
                dernier = time.time()
                ecrire(f"{texte} {int(100 * fait / total)} %", fin="\r")
    ecrire(f"{texte} 100 %")


def decompresser(arc, dest, texte):
    ext = arc.lower()
    if ext.endswith(".zip"):
        try:
            _zip(arc, dest, texte)
            return
        except (NotImplementedError, RuntimeError, zipfile.BadZipFile) as e:   # chiffré, LZMA, zip64 abîmé…
            ecrire(f"zip : {e}")
            shutil.rmtree(dest, ignore_errors=True)
    elif re.search(r"\.(tar|tgz|tar\.gz)$", ext):
        with tarfile.open(arc) as t:
            try:
                t.extractall(dest, filter="data")
            except TypeError:   # Python < 3.12 (Linux : Python du système)
                t.extractall(dest)
        ecrire(f"{texte} 100 %")
        return
    if _externe(arc, dest, morceaux(arc), texte):
        return
    if not outils() or (re.search(r"\.(rar|7z|001)$", ext) and not any(s in ("7z", "unrar", "winrar") for s, _ in outils())):
        raise Erreur("Impossible de décompresser ce fichier : installe 7-Zip (gratuit, 7-zip.org) puis recommence. "
                     "Ou décompresse-le toi-même, puis choisis le dossier obtenu.")
    raise Erreur("Impossible de décompresser ce fichier (archive abîmée ou pas finie de télécharger, mot de passe ?). "
                 "Retélécharge-le, ou décompresse-le toi-même puis choisis le dossier obtenu.")


# ---------- rangement ----------
def _sous(d):
    """(sous-dossiers, fichiers) utiles de d (sans __MACOSX, Thumbs.db…)"""
    dossiers, fichiers = [], []
    for e in os.scandir(d):
        if e.name.lower() in INUTILES:
            continue
        (dossiers if e.is_dir() else fichiers).append(e.name)
    return dossiers, fichiers


def _meme_nom(a, b):
    return re.sub(r"[\s_\-.()]", "", a).lower() == re.sub(r"[\s_\-.()]", "", b).lower()


def racine_pack(base, base_possible):
    """dossier du pack, gardé ENTIER avec ses sous-dossiers de rangement (TCM : Men\\Europe\\<pays>\\config.xml ;
    DF11 : un dossier plat, config.xml à la racine) : le dossier du haut de base qui contient tous les config.xml.
    Plusieurs (ou config.xml directement dans base) : base lui-même si base_possible (dossier choisi), sinon None
    (dossier temporaire : nom de l'archive). Seul le vrai dossier en double est enlevé (« X\\X », même nom).
    Renvoie (dossier ou None, nombre de config.xml)"""
    configs = []
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if x.lower() not in INUTILES]
        if any(f.lower() == "config.xml" for f in files):
            configs.append(d)
    hauts = {os.path.relpath(c, base).split(os.sep)[0] for c in configs}
    dossiers, fichiers = _sous(base)
    # dossier choisi par le joueur : gardé entier (Logos TCM27 avec seulement Men\…), sauf dossier fourre-tout
    # (Téléchargements, Bureau, ou avec des programmes / archives) où l'on prend le seul dossier qui a les config.xml
    fourre_tout = os.path.basename(base).lower() in FOURRE_TOUT or any(
        not x.lower().endswith(PACK_EXTS) for x in fichiers)
    if base_possible and not fourre_tout and configs:
        r = base
    elif len(hauts) == 1 and "." not in hauts:
        r = os.path.join(base, hauts.pop())
    elif not configs and not base_possible and len(dossiers) == 1 and not fichiers:
        r = os.path.join(base, dossiers[0])
    elif base_possible:
        r = base
    else:
        return None, len(configs)
    while True:   # « Megapack TCM27\Megapack TCM27\… » (décompressé deux fois) : un seul niveau gardé
        dossiers, fichiers = _sous(r)
        if len(dossiers) == 1 and not fichiers and _meme_nom(dossiers[0], os.path.basename(r)):
            r = os.path.join(r, dossiers[0])
        else:
            return r, len(configs)


def _fichiers(d):
    for racine, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x.lower() not in INUTILES]
        for f in files:
            if f.lower() not in INUTILES:
                yield os.path.join(racine, f)


def ranger(src, dest, deplacer, texte):
    """src -> dest (créé ou fusionné, fichiers remplacés) ; deplacer : même disque (dossier temporaire), sinon copie.
    Renvoie (fichiers, remplacés)"""
    tous = list(_fichiers(src))
    n, remplaces, dernier = len(tous), 0, 0
    for i, f in enumerate(tous, 1):
        cible = os.path.join(dest, os.path.relpath(f, src))
        os.makedirs(os.path.dirname(cible), exist_ok=True)
        if os.path.exists(cible):
            remplaces += 1
        if deplacer:
            try:
                os.replace(f, cible)
            except OSError:   # autre disque (graphics = lien vers un autre disque) : copie
                shutil.copy2(f, cible)
        else:
            shutil.copy2(f, cible)
        if time.time() - dernier > 0.5:
            dernier = time.time()
            ecrire(f"{texte} {int(100 * i / max(n, 1))} %", fin="\r")
    ecrire(f"{texte} 100 %")
    return n, remplaces


def taille(d):
    return sum(os.path.getsize(f) for f in _fichiers(d))


def graphics_pret():
    """dossier graphics (créé si le dossier FM 27 existe) ; Erreur sinon"""
    g = stades_photos.graphics()
    if not os.path.isdir(g):
        fm = os.path.dirname(g)
        if os.path.isdir(fm):
            os.makedirs(g, exist_ok=True)
        else:
            raise Erreur(f"Dossier graphics introuvable ({g}) : lance FM 27 une fois, ou choisis ton dossier graphics "
                         "sur la page « Dossier du jeu ».")
    return g


def place(dossier, besoin):
    libre = shutil.disk_usage(dossier).free
    if libre < besoin:
        raise Erreur(f"Pas assez de place sur le disque : {libre / 2**30:.1f} Go libres, il en faut environ "
                     f"{besoin / 2**30:.1f} Go. Libère de la place puis recommence.")


def installer(sorte, source):
    source = os.path.abspath(source.strip().strip('"'))
    if not os.path.exists(source):
        raise Erreur(f"Introuvable : {source}")
    g = graphics_pret()
    gn = os.path.normcase(os.path.abspath(g))
    if os.path.normcase(source).startswith(gn + os.sep) or os.path.normcase(source) == gn:
        raise Erreur("Ce dossier est déjà dans graphics : rien à faire, relance FM 27.")
    tmp = os.path.join(os.path.dirname(g), TEMP)
    shutil.rmtree(tmp, ignore_errors=True)   # reste d'une installation coupée
    ecrire(f"Dossier graphics : {g}")
    try:
        if os.path.isfile(source):
            arcs = [premiere_partie(source)]
            if not archive(arcs[0]):
                raise Erreur("Ce fichier n'est pas une archive (.zip, .rar, .7z) : choisis le fichier téléchargé.")
        else:
            arcs = sorted(os.path.join(source, f) for f in os.listdir(source) if archive(os.path.join(source, f)))
            if arcs and racine_pack(source, True)[1]:   # dossier déjà décompressé (config.xml) : pas les archives
                arcs = []
        if arcs:
            besoin = sum(morceaux(a) for a in arcs)
            place(os.path.dirname(g), int(besoin * 1.15) + 500 * 2**20)
            for i, a in enumerate(arcs, 1):
                ecrire(f"Archive : {os.path.basename(a)} ({morceaux(a) / 2**30:.2f} Go)")
                decompresser(a, tmp, f"[1/2] Décompression{f' {i}/{len(arcs)}' if len(arcs) > 1 else ''} :")
            pack, configs = racine_pack(tmp, False)
            nom = os.path.basename(pack) if pack else nom_archive(arcs[0])
            pack = pack or tmp
            deplacer = True
        else:
            if os.path.isfile(source):
                raise Erreur("Ce fichier n'est pas une archive (.zip, .rar, .7z) : choisis le fichier téléchargé.")
            pack, configs = racine_pack(source, True)
            nom = os.path.basename(pack)
            place(os.path.dirname(g), taille(pack) + 200 * 2**20)
            deplacer = False
        if nom.lower() in NOTRES:
            raise Erreur(f"« {nom} » est un dossier de l'app (stades, trophées) : choisis le pack de logos ou de visages.")
        dest = g if nom.lower() == "graphics" else os.path.join(g, nom)   # archive qui contient déjà « graphics »
        maj = os.path.isdir(dest) and dest != g
        if not configs:
            ecrire("Attention : aucun config.xml dans ce pack (pas un pack pour FM ?). Rangé quand même.")
        ecrire(f"Pack : {nom} ({configs} config.xml)" + (" : déjà là, mis à jour" if maj else ""))
        n, remplaces = ranger(pack, dest, deplacer, "[2/2] Rangement dans graphics :")
        ecrire(f"Installé : {dest} ({n} fichiers, dont {remplaces} remplacés)")
        ecrire("Relance FM 27 pour voir les " + ("logos." if sorte == "logos" else "visages." if sorte == "faces"
                                                  else "images."))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------- état (page de l'app) ----------
def genre(nom):
    n = nom.lower()
    if "tcm" in n or "logo" in n:
        return "logos"
    if "df11" in n or "face" in n or "visage" in n or "portrait" in n:
        return "faces"
    return ""


def _configs(d, profondeur=8, dossiers_max=5000):
    """nombre de config.xml dans d et plus bas (TCM : un par pays / Clubs / Competitions, 4-5 niveaux ; DF11 : un
    seul à la racine d'un dossier plat énorme, listé une fois)"""
    file, vus, n_cfg = [(d, 0)], 0, 0
    while file and vus < dossiers_max:
        c, n = file.pop()
        vus += 1
        if os.path.isfile(os.path.join(c, "config.xml")):
            n_cfg += 1
        if n >= profondeur:
            continue
        try:
            with os.scandir(c) as it:
                file.extend((e.path, n + 1) for e in it if e.is_dir() and e.name.lower() not in INUTILES)
        except OSError:
            pass
    return n_cfg


def etat():
    g = stades_photos.graphics()
    packs = []
    if os.path.isdir(g):
        for e in sorted(os.scandir(g), key=lambda x: x.name.lower()):
            if e.is_dir() and e.name.lower() not in NOTRES:
                n = _configs(e.path)
                packs.append({"nom": e.name, "genre": genre(e.name), "config": n > 0, "configs": n})
    return {"graphics": g, "graphics_ok": os.path.isdir(g), "base": stades_photos.graphics_de_base(),
            "choisi": stades_photos.choisi(), "packs": packs, "outils": sorted({s for s, _ in outils()}),
            "reste": os.path.isdir(os.path.join(os.path.dirname(g), TEMP))}


def main(argv):
    if argv[:1] == ["etat"]:
        print(json.dumps(etat(), ensure_ascii=False, indent=1))
    elif argv[:1] == ["installer"] and len(argv) >= 3:
        try:
            installer(argv[1], " ".join(argv[2:]))
        except Erreur as e:
            ecrire(str(e))
            sys.exit(1)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
