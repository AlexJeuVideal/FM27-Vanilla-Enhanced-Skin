"""Mise à jour de l'app depuis GitHub (Releases) : vérifier, télécharger, installer. En sommeil tant que DEPOT est vide.

Une version = une Release GitHub au tag « v1.XX » avec, en pièce jointe, le zip du dossier de partage (n'importe quel
nom en .zip ; le dossier de partage peut être à la racine du zip ou dedans). Empreinte obligatoire : celle que GitHub
calcule pour chaque pièce jointe (« digest »), sinon un fichier « <zip>.sha256 » joint aussi.
Dépôt public (TOKEN vide) ou privé (TOKEN : lecture seule de ce dépôt, visible par qui a l'app ; pièces jointes
téléchargées par l'API, le token n'est jamais envoyé au lien signé de la redirection).

Installation (app fermée sur la même page, puis redémarrée) : tout le dossier est remplacé SAUF `backups\\` (réglages,
sauvegardes, marqueurs) et `.venv\\`. Seuls les marqueurs `.actif` des fonctions NOUVELLES sont posés (choix de base).
Fichiers de `outils\\` absents de la nouvelle version : supprimés. Ancienne version gardée dans backups\\maj\\ancienne
(remise toute seule si la copie échoue). Jamais dans le dossier de travail (UI PICKER : présence de « Outils FM.bat »).
Les bundles du jeu ne sont pas touchés : l'app propose ensuite de réinstaller le skin (FM fermé).

Essai sans GitHub : UIPICKER_MAJ_API=http://127.0.0.1:<port> + UIPICKER_MAJ_DEPOT=<compte/depot> (faux serveur).
Usage : mise_a_jour.py verifier | telecharger | installer
"""
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import langue  # noqa: E402

# ---------- réglages ----------
DEPOT = "AlexJeuVideal/FM27-Vanilla-Enhanced-Skin"   # « compte/depot » sur GitHub, ex. "AlexJeuVideal/FM27-Vanilla-Enhanced-Skin" ; "" = pas de mise à jour
# dépôt privé : token GitHub « fine-grained », CE dépôt seulement, droit Contents en lecture seule ; "" = dépôt public.
# Lisible par quiconque a l'app (Python en clair) : jamais un token avec d'autres droits.
TOKEN = ""   # dépôt public : pas de token
TAILLE_MAX = 200 * 1024 * 1024   # zip refusé au-delà
GARDES = ("backups", ".venv", "python")    # dossiers de la racine jamais touchés (python : livré par le Setup)

DEPOT = os.environ.get("UIPICKER_MAJ_DEPOT") or DEPOT
TOKEN = os.environ.get("UIPICKER_MAJ_TOKEN") or TOKEN
API = (os.environ.get("UIPICKER_MAJ_API") or "https://api.github.com").rstrip("/")
ESSAI = "UIPICKER_MAJ_API" in os.environ   # faux serveur local : http accepté
RACINE = os.path.dirname(chemins.OUTILS)
VERSION_TXT = os.path.join(chemins.OUTILS, "commun", "version.txt")
DOSSIER = os.path.join(backup.BACKUP_DIR, "maj")
ZIP = os.path.join(DOSSIER, "maj.zip")
NOUVELLE = os.path.join(DOSSIER, "nouvelle")
ANCIENNE = os.path.join(DOSSIER, "ancienne")
FAIT = os.path.join(DOSSIER, "fait.json")   # dernière mise à jour installée (l'app propose de réinstaller le skin)
T = langue.texte


def version_de(texte):
    """(1, 10) depuis « … v1.10 … » ou « v1.10 » ; None sinon"""
    m = re.search(r"v(\d+)\.(\d+)", texte or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def nom_version(v):
    return f"v{v[0]}.{v[1]:02d}" if v else "?"


def version_locale(fichier=VERSION_TXT):
    try:
        with open(fichier, encoding="utf-8") as f:
            return version_de(f.read())
    except OSError:
        return None


def dossier_de_travail():
    """UI PICKER (pas un dossier de partage) : jamais remplacé"""
    return os.path.exists(os.path.join(RACINE, "Outils FM.bat"))


def _get(url, timeout=15, binaire=False):
    """binaire : pièce jointe par l'API (dépôt privé) ; GitHub renvoie vers un lien signé, que l'on suit SANS le token
    (en-tête « unredirected » : urllib ne le recopie pas sur la redirection)"""
    if not (url.startswith("https://") or ESSAI):
        raise ValueError("adresse refusée : " + url)
    req = urllib.request.Request(url, headers={"User-Agent": "FM27-Vanilla-Enhanced-Skin",
                                               "Accept": "application/octet-stream" if binaire
                                               else "application/vnd.github+json"})
    if TOKEN and url.startswith(API + "/"):
        req.add_unredirected_header("Authorization", "Bearer " + TOKEN)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404) and url.startswith(API + "/"):
            raise ValueError(T(f"GitHub refuse l'accès ({e.code}) : dépôt introuvable, ou token expiré / sans droit",
                               f"GitHub denied access ({e.code}): repository not found, or token expired / no rights"))
        raise


def derniere():
    """dernière Release : {version, tag, notes, zip, url, taille, sha256 | sha256_url}"""
    with _get(f"{API}/repos/{DEPOT}/releases/latest") as r:
        d = json.load(r)
    v = version_de(d.get("tag_name"))
    if not v:
        raise ValueError("tag sans version : " + str(d.get("tag_name")))
    assets = d.get("assets") or []
    zips = [a for a in assets if a.get("name", "").lower().endswith(".zip")]
    if not zips:
        raise ValueError("pas de .zip dans la Release " + d["tag_name"])
    # v1.70 : la Release a aussi le zip Mac (« … - Mac.zip ») : jamais celui-là ; v1.87 (app unique) : sur Mac,
    # celui-là d'abord (même contenu que l'autre depuis la v1.87)
    est_mac = [x for x in zips if "mac" in re.findall(r"[a-z]+", x["name"].lower())]
    autres = [x for x in zips if x not in est_mac]
    a = ((est_mac or autres) if sys.platform == "darwin" else (autres or zips))[0]
    lien = (lambda x: x["url"]) if TOKEN else (lambda x: x["browser_download_url"])   # privé : par l'API
    info = {"version": v, "tag": d["tag_name"], "notes": d.get("body") or "", "zip": a["name"],
            "url": lien(a), "taille": a.get("size") or 0}
    dg = a.get("digest") or ""
    if dg.lower().startswith("sha256:"):
        info["sha256"] = dg.split(":", 1)[1].lower()
    else:
        s = [x for x in assets if x.get("name", "").lower() == a["name"].lower() + ".sha256"]
        if s:
            info["sha256_url"] = lien(s[0])
    return info


def verifier():
    """état pour l'app : {etat: off | travail | a_jour | dispo | erreur, locale, distante, notes, taille}"""
    loc = version_locale()
    out = {"etat": "off", "locale": nom_version(loc)}
    if not DEPOT:
        return out
    try:
        info = derniere()
    except Exception as e:   # noqa: BLE001  (pas d'internet, GitHub en panne… : l'app continue sans)
        out.update(etat="erreur", erreur=str(e))
        return out
    out.update(distante=nom_version(info["version"]), notes=info["notes"][:4000], taille=info["taille"])
    if not loc or info["version"] <= loc:
        out["etat"] = "a_jour"
    else:
        out["etat"] = "travail" if dossier_de_travail() else "dispo"
    return out


# ---------- téléchargement ----------
def _prefixe(noms):
    """dossier du zip qui contient outils/commun/version.txt ('' = racine du zip)"""
    for n in noms:
        if n.replace("\\", "/").endswith("outils/commun/version.txt"):
            return n.replace("\\", "/")[:-len("outils/commun/version.txt")]
    return None


def telecharger():
    info = derniere()
    loc = version_locale()
    if loc and info["version"] <= loc:
        print(T(f"Déjà à jour ({nom_version(loc)}).", f"Already up to date ({nom_version(loc)})."))
        return 0
    if info["taille"] > TAILLE_MAX:
        raise ValueError("zip trop gros")
    attendu = info.get("sha256")
    if not attendu and info.get("sha256_url"):
        with _get(info["sha256_url"], binaire=True) as r:
            attendu = r.read(4096).decode("utf-8", "replace").split()[0].lower()
    if not attendu or not re.fullmatch(r"[0-9a-f]{64}", attendu):
        raise ValueError(T("pas d'empreinte sha256 pour le zip : mise à jour refusée",
                           "no sha256 for the zip: update refused"))
    print(T(f"Téléchargement de {info['tag']} ({info['zip']})", f"Downloading {info['tag']} ({info['zip']})"))
    shutil.rmtree(DOSSIER, ignore_errors=True)
    os.makedirs(DOSSIER, exist_ok=True)
    h = hashlib.sha256()
    lu = 0
    with _get(info["url"], timeout=60, binaire=True) as r, open(ZIP, "wb") as f:
        total = int(r.headers.get("Content-Length") or info["taille"] or 0)
        while True:
            bloc = r.read(256 * 1024)
            if not bloc:
                break
            lu += len(bloc)
            if lu > TAILLE_MAX:
                raise ValueError("zip trop gros")
            h.update(bloc)
            f.write(bloc)
            if total:
                print(f"\r{T('Téléchargement', 'Download')} {min(100, lu * 100 // total)} %", end="", flush=True)
    print()
    if h.hexdigest() != attendu:
        os.remove(ZIP)
        raise ValueError(T("empreinte différente : fichier abîmé ou modifié, mise à jour refusée",
                           "hash mismatch: file damaged or altered, update refused"))
    print(T("Empreinte vérifiée.", "Hash checked."))
    with zipfile.ZipFile(ZIP) as z:
        noms = z.namelist()
        pre = _prefixe(noms)
        if pre is None:
            raise ValueError(T("ce zip n'est pas une version du skin", "this zip is not a skin release"))
        for n in noms:
            n2 = n.replace("\\", "/")
            if not n2.startswith(pre) or n2.endswith("/"):
                continue
            rel = n2[len(pre):]
            parties = rel.split("/")
            if rel.startswith("/") or ":" in rel or ".." in parties:
                raise ValueError("chemin refusé dans le zip : " + n)
            if parties[0] in GARDES and not (parties[0] == "backups" and rel.endswith(".actif") and len(parties) == 2):
                continue   # seuls les marqueurs du choix de base, rien d'autre de backups
            if "__pycache__" in parties:
                continue
            dest = os.path.join(NOUVELLE, *parties)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(n) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            if os.name != "nt" and dest.endswith((".sh", ".command")):   # Linux / Mac : lanceur exécutable
                os.chmod(dest, 0o755)
    os.remove(ZIP)
    v = version_locale(os.path.join(NOUVELLE, "outils", "commun", "version.txt"))
    if v != info["version"] or not os.path.exists(os.path.join(NOUVELLE, "outils", "app", "serveur.py")):
        raise ValueError(T(f"le zip contient {nom_version(v)}, pas {info['tag']}", f"the zip holds {nom_version(v)}, not {info['tag']}"))
    print(T(f"{info['tag']} prête à installer.", f"{info['tag']} ready to install."))
    return 0


# ---------- installation ----------
def _fichiers(base):
    for d, sous, fs in os.walk(base):
        sous[:] = [s for s in sous if s != "__pycache__"]
        for f in fs:
            yield os.path.relpath(os.path.join(d, f), base)


def _copier_ancienne():
    shutil.rmtree(ANCIENNE, ignore_errors=True)
    os.makedirs(ANCIENNE)
    for n in os.listdir(RACINE):
        p = os.path.join(RACINE, n)
        if n in GARDES:
            continue
        if os.path.isdir(p):
            shutil.copytree(p, os.path.join(ANCIENNE, n), ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(p, ANCIENNE)


def _remettre_ancienne():
    for n in os.listdir(ANCIENNE):
        src, dst = os.path.join(ANCIENNE, n), os.path.join(RACINE, n)
        if os.path.isdir(src):
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def installer():
    if dossier_de_travail():
        print(T("Dossier de travail : pas de mise à jour ici.", "Work folder: no update here."))
        return 1
    loc, nv = version_locale(), version_locale(os.path.join(NOUVELLE, "outils", "commun", "version.txt"))
    if not nv or (loc and nv <= loc):
        print(T("Rien à installer (télécharger d'abord).", "Nothing to install (download first)."))
        return 1
    import catalogue   # fonctions de la version actuelle : les nouvelles reçoivent leur marqueur (choix de base)
    connues = set(catalogue.FONCTIONS)
    # 2026-11-18 (chez FM Guru : match_tuile_banc pas posé) : liste AVEC_GURU de la NOUVELLE version (l'actuelle ne
    # connaît pas les fonctions nouvelles qui y sont ajoutées)
    avec_guru = set(catalogue.AVEC_GURU)
    try:
        import ast
        src = open(os.path.join(NOUVELLE, "outils", "commun", "catalogue.py"), encoding="utf-8").read()
        for n in ast.parse(src).body:
            if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "AVEC_GURU" for t in n.targets):
                avec_guru = set(ast.literal_eval(n.value))
    except Exception:
        pass
    # 2026-11-10 (le joueur, chez FM Guru : salle des trophées, vue du club posées) : mode FM Guru = seulement la
    # fiche joueur ; une fonction nouvelle n'y reçoit son marqueur que si elle va avec la vue (AVEC_GURU)
    try:
        import options
        guru = options.get("fiche_fmguru") == "guru"
    except Exception:
        guru = False
    print(T(f"Installation de {nom_version(nv)} (avant : {nom_version(loc)})",
            f"Installing {nom_version(nv)} (before: {nom_version(loc)})"))
    _copier_ancienne()
    nouveaux = set(_fichiers(NOUVELLE))
    try:
        for rel in sorted(nouveaux):
            parties = rel.split(os.sep)
            if parties[0] == "backups":   # marqueur .actif : seulement pour une fonction nouvelle
                if parties[-1][:-len(".actif")] in connues:
                    continue
                if guru and parties[-1][:-len(".actif")] not in avec_guru:
                    continue
                dest = os.path.join(backup.BACKUP_DIR, parties[-1])
            else:
                dest = os.path.join(RACINE, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(os.path.join(NOUVELLE, rel), dest)
        for rel in list(_fichiers(chemins.OUTILS)):   # scripts retirés de la nouvelle version
            if os.path.join("outils", rel) not in nouveaux:
                os.remove(os.path.join(chemins.OUTILS, rel))
        for d, sous, _ in list(os.walk(chemins.OUTILS, topdown=False)):
            for s in sous:
                p = os.path.join(d, s)
                if s == "__pycache__":
                    shutil.rmtree(p, ignore_errors=True)
                elif not os.listdir(p):
                    os.rmdir(p)
    except Exception:
        print(T("Erreur pendant la copie : ancienne version remise.", "Error while copying: old version put back."))
        _remettre_ancienne()
        raise
    with open(FAIT, "w", encoding="utf-8") as f:
        json.dump({"de": nom_version(loc), "vers": nom_version(nv), "quand": time.strftime("%Y-%m-%d %H:%M")}, f)
    shutil.rmtree(NOUVELLE, ignore_errors=True)
    print(T(f"{nom_version(nv)} installée. L'app redémarre.", f"{nom_version(nv)} installed. The app restarts."))
    return 0


def fait():
    """dernière mise à jour installée, pas encore suivie d'une réinstallation du skin : {de, vers} ou None"""
    try:
        with open(FAIT, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def oublier_fait():
    try:
        os.remove(FAIT)
    except OSError:
        pass


def main(argv):
    op = argv[0] if argv else ""
    if op == "verifier":
        print(json.dumps(verifier(), ensure_ascii=False, indent=1))
        return 0
    if op in ("telecharger", "installer"):
        if not DEPOT:
            print(T("Mises à jour pas encore activées (DEPOT vide).", "Updates not enabled yet (DEPOT empty)."))
            return 1
        try:
            return telecharger() if op == "telecharger" else installer()
        except Exception as e:   # noqa: BLE001
            print(T("Échec : ", "Failed: ") + str(e))
            return 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
