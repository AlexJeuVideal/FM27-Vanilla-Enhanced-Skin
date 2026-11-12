"""Vrais noms (licences) : le « Real Names Licence Fix » de FM SCOUT (fmscout.com), PAS un travail du skin.

L'app ne livre AUCUN fichier de FM Scout : le joueur télécharge leur zip sur fmscout.com, l'app le trouve
(Téléchargements / Bureau, ou choisi à la main) et fait ce que fait leur auto-install.bat, avec en plus une sauvegarde
des fichiers supprimés (backups\\noms_reels) pour pouvoir tout remettre.

Leur fix, pour chaque base de <jeu>\\shared\\data\\database\\db\\<n°> qui a un dossier lnc (2700 = nouvelles parties,
2600, 2400… = parties importées) : supprime les fichiers de licence (A_SUPPRIMER, liste de leur auto-install.bat
v261110) et copie leurs deux .lnc dans lnc\\all. Une MAJ de FM ou « Vérifier l'intégrité » (Steam) remet les fichiers
supprimés : il faut alors réappliquer.

Usage : noms_reels.py                       -> diagnostic (lecture seule)
        noms_reels.py appliquer [--dry-run] -> zip trouvé automatiquement
        noms_reels.py retirer [--dry-run]
"""
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemin_jeu  # noqa: E402

BACKUP = os.path.join(chemin_jeu.BACKUP_DIR, "noms_reels")
MANIFESTE = os.path.join(BACKUP, "manifeste.json")
LNC = ("FM27 Fix by FMScout.lnc", "FM27 Club Names by FMScout.lnc")
TAILLE_MAX = 30 * 1024 * 1024   # un .lnc de FM Scout fait ~0,5 Mo
_LNC_ALL = [f"lnc/all/{n}.lnc" for n in (
    "fake", "ac milan (wom)", "acc Inter unlic 24", "acmilan unlic 24", "inter (wom)", "inter unlic 24", "japanese names",
    "lazio (wom)", "lic_dan_swe_fra", "licensing club name_fm24", "men lazio", "men.atalanta", "inter u23 (men)",
    "atalanta u23 (men)")]
_DBC = [f"dbc/permanent/{n}.dbc" for n in (
    "1_japan_removed_clubs", "j_league_non_player_random_names_fm27 1", "shonan_randomised_names", "brazil_kits",
    "brazil_wf_random kits_fm27", "fm_27_italy_kits", "fm27_remove_players ars", "japan_fake")]
_LANGUE = [f"dbc/permanent/{s}{n}.dbc" for n in ("Licensing2", "Licensing2_chn") for s in ("language/", "")]
A_SUPPRIMER = _LNC_ALL + ["edt/permanent/fake.edt", "dbc/germany.dbc"] + _DBC + _LANGUE


# Mac (leur mac-install.sh) : même liste de fichiers et mêmes .lnc, seule la base est rangée dans fm.app
INTERIEUR_MAC = os.path.join("fm.app", "Contents", "PlugIns", "game_plugin.bundle", "Contents", "Resources")


def racine_db(jeu):
    """<jeu>\\shared\\data\\database\\db (Windows, Linux par Proton) ; Mac : dans fm.app"""
    for base in (jeu or "", os.path.join(jeu or "", INTERIEUR_MAC)):
        d = os.path.join(base, "shared", "data", "database", "db")
        if os.path.isdir(d):
            return d
    return os.path.join(jeu or "", "shared", "data", "database", "db")


def bases(jeu):
    """[(n°, dossier)] des bases qui ont un dossier lnc (2700, 2600, 2400…)"""
    r = racine_db(jeu)
    try:
        noms = sorted(os.listdir(r), reverse=True)
    except OSError:
        return []
    return [(n, os.path.join(r, n)) for n in noms if os.path.isdir(os.path.join(r, n, "lnc"))]


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _sha_fichier(p):
    try:
        with open(p, "rb") as f:
            return _sha(f.read())
    except OSError:
        return ""


# ---------- le zip / dossier de FM Scout ----------
def lire_source(chemin):
    """{nom .lnc: octets} depuis un zip ou un dossier de FM Scout ; ValueError si ce n'est pas leur fix"""
    res = {}
    if os.path.isfile(chemin) and chemin.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(chemin) as z:
                for i in z.infolist():
                    n = os.path.basename(i.filename.replace("\\", "/"))
                    if n in LNC and n not in res and i.file_size <= TAILLE_MAX:
                        res[n] = z.read(i)
        except (OSError, zipfile.BadZipFile) as e:
            raise ValueError(f"zip illisible / unreadable zip ({e})")
    elif os.path.isdir(chemin):
        try:   # le dossier lui-même ou un sous-dossier direct (zip extrait dans un dossier du même nom)
            sous = [os.path.join(chemin, x) for x in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, x))]
        except OSError:
            sous = []
        for racine in [chemin] + sous:
            for n in LNC:
                p = os.path.join(racine, n)
                if n not in res and os.path.isfile(p) and os.path.getsize(p) <= TAILLE_MAX:
                    with open(p, "rb") as f:
                        res[n] = f.read()
    if set(res) != set(LNC):
        raise ValueError("pas le fix de FM Scout / not the FM Scout fix")
    return res


def dossiers_recherche():
    h = os.path.expanduser("~")
    ds = [os.path.join(h, "Downloads"), os.path.join(h, "Téléchargements"), os.path.join(h, "Desktop"),
          os.path.join(h, "Bureau"), os.path.join(h, "OneDrive", "Desktop"), os.path.join(h, "OneDrive", "Bureau")]
    return [d for d in dict.fromkeys(ds) if os.path.isdir(d)]


def trouver():
    """zips / dossiers du fix de FM Scout dans Téléchargements et Bureau, le plus récent d'abord : [(chemin, date)]"""
    res = []
    for d in dossiers_recherche():
        try:
            noms = os.listdir(d)
        except OSError:
            continue
        for n in noms:
            b = n.lower()
            if "real-names" not in b and "real names" not in b and "fmscout" not in b:
                continue
            p = os.path.join(d, n)
            if (os.path.isfile(p) and b.endswith(".zip")) or os.path.isdir(p):
                try:
                    lire_source(p)
                except (ValueError, OSError):
                    continue
                res.append((p, os.path.getmtime(p)))
    return sorted(res, key=lambda x: -x[1])


# ---------- état ----------
def manifeste():
    try:
        with open(MANIFESTE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def diagnostic(jeu, source=None):
    """état de chaque base : fix posé (les 2 .lnc), fichiers de licence encore là (remis par une MAJ de FM)"""
    m = manifeste()
    src = source or (trouver()[:1] or [(None, 0)])[0][0]
    shas = {}
    if src:
        try:
            shas = {n: _sha(b) for n, b in lire_source(src).items()}
        except (ValueError, OSError):
            src = None
    liste = []
    for n, d in bases(jeu):
        lnc = [os.path.isfile(os.path.join(d, "lnc", "all", x)) for x in LNC]
        restes = [r for r in A_SUPPRIMER if os.path.isfile(os.path.join(d, *r.split("/")))]
        a_jour = all(lnc) and (not shas or all(_sha_fichier(os.path.join(d, "lnc", "all", x)) == shas[x] for x in LNC))
        liste.append({"base": n, "lnc": all(lnc), "restes": restes, "a_jour": a_jour})
    pose = bool(liste) and all(b["lnc"] for b in liste)
    return {
        "db": racine_db(jeu), "db_ok": bool(liste), "bases": liste,
        "pose": pose,                                           # les 2 .lnc dans toutes les bases
        "complet": pose and not any(b["restes"] for b in liste),   # et plus aucun fichier de licence
        "a_jour": pose and all(b["a_jour"] for b in liste),     # mêmes .lnc que le zip trouvé
        "partiel": any(b["lnc"] for b in liste) and not pose,
        "source": src or "", "source_nom": os.path.basename(src) if src else "",
        "sauvegardes": sum(len(v) for v in m.get("sauves", {}).values()),
        "applique_le": m.get("date", ""), "source_posee": m.get("source", ""),
        "recherche": dossiers_recherche(),
    }


# ---------- écriture ----------
def appliquer(jeu, source, a_blanc=False):
    """sauvegarde + suppression des fichiers de licence, copie des 2 .lnc ; renvoie (supprimés, copiés)"""
    lnc = lire_source(source)
    bs = bases(jeu)
    if not bs:
        raise ValueError("base de données de FM introuvable / FM database not found")
    m = manifeste()
    sauves = m.get("sauves", {})
    supp = cop = 0
    for n, d in bs:
        for r in A_SUPPRIMER:
            p = os.path.join(d, *r.split("/"))
            if not os.path.isfile(p):
                continue
            supp += 1
            if a_blanc:
                print(f"  [{n}] supprimer / delete {r}")
                continue
            dst = os.path.join(BACKUP, n, *r.split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)   # remplace une vieille sauvegarde : le fichier du FM à jour est le bon
            os.remove(p)
            sauves.setdefault(n, [])
            if r not in sauves[n]:
                sauves[n].append(r)
        for x, b in lnc.items():
            p = os.path.join(d, "lnc", "all", x)
            if _sha_fichier(p) == _sha(b):
                continue
            cop += 1
            if a_blanc:
                print(f"  [{n}] copier / copy {x}")
                continue
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p + ".tmp", "wb") as f:
                f.write(b)
            os.replace(p + ".tmp", p)
        if not a_blanc:   # manifeste écrit base par base : une erreur au milieu laisse une sauvegarde juste
            _ecrire_manifeste(sauves, source)
    _sigles(jeu, a_blanc)
    return supp, cop


def _sigles(jeu, a_blanc):
    """sigles à 3 lettres du skin (sigles_clubs.py), s'ils sont posés : refaits avec / sans les sigles de FM Scout"""
    if a_blanc:
        return
    try:
        import sigles_clubs
        sigles_clubs.rafraichir(jeu)
    except (ImportError, ValueError, OSError):
        pass


def _ecrire_manifeste(sauves, source):
    os.makedirs(BACKUP, exist_ok=True)
    with open(MANIFESTE + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"date": time.strftime("%Y-%m-%d %H:%M"), "source": os.path.basename(source), "sauves": sauves},
                  f, ensure_ascii=False, indent=1)
    os.replace(MANIFESTE + ".tmp", MANIFESTE)


def retirer(jeu, a_blanc=False):
    """remet les fichiers sauvegardés (s'ils manquent) et enlève les 2 .lnc ; renvoie (remis, enlevés)"""
    sauves = manifeste().get("sauves", {})
    remis = enleves = 0
    for n, d in bases(jeu):
        for r in sauves.get(n, []):
            src, p = os.path.join(BACKUP, n, *r.split("/")), os.path.join(d, *r.split("/"))
            if os.path.isfile(src) and not os.path.exists(p):
                remis += 1
                if a_blanc:
                    print(f"  [{n}] remettre / restore {r}")
                    continue
                os.makedirs(os.path.dirname(p), exist_ok=True)
                shutil.copy2(src, p)
        for x in LNC:
            p = os.path.join(d, "lnc", "all", x)
            if os.path.isfile(p):
                enleves += 1
                if a_blanc:
                    print(f"  [{n}] enlever / remove {x}")
                    continue
                os.remove(p)
    if not a_blanc and os.path.isdir(BACKUP):
        shutil.rmtree(BACKUP)
    _sigles(jeu, a_blanc)
    return remis, enleves


def main(argv):
    jeu = os.environ.get("UIPICKER_JEU") or chemin_jeu.lire()
    a_blanc = "--dry-run" in argv
    op = (argv[0] if argv and argv[0] != "--dry-run" else "")
    if op == "appliquer":
        t = trouver()
        if not t:
            sys.exit("zip de FM Scout introuvable / FM Scout zip not found")
        print(t[0][0])
        print("supprimés / deleted %d, copiés / copied %d" % appliquer(jeu, t[0][0], a_blanc))
    elif op == "retirer":
        print("remis / restored %d, enlevés / removed %d" % retirer(jeu, a_blanc))
    elif not op:
        print(json.dumps(diagnostic(jeu), ensure_ascii=False, indent=1))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
