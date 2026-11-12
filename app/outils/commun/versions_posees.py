"""Version posée de chaque fonction (bouton « Réinstaller » de l'app, 2026-11-12, demande du joueur).

Empreinte d'une fonction = sha256 de son script et des modules du skin dont il se sert (imports, et noms de scripts
cités entre guillemets : scripts Kinito lancés par rencontres_version…), sans la boîte à outils générale (GENERAUX :
une retouche de lecture / écriture des bundles ne veut pas dire que la fonction a changé) ni les autres fonctions. Notée dans
backups\\versions_posees.json à chaque application réussie (choix 1, Activer, Réinstaller, option). Fonction activée
dont l'empreinte du dossier diffère (mise à jour de l'app) ou jamais notée (installé avant v1.24) : à réinstaller.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import catalogue as cat  # noqa: E402

FICHIER = os.path.join(backup.BACKUP_DIR, "versions_posees.json")
GENERAUX = {"chemins", "chemin_jeu", "sauvegarde_originaux", "catalogue", "options", "lancer", "langue",
            "fin_ecriture", "mise_a_jour", "statut", "voir_contenu_ecran", "versions_posees",
            "notes_au_lieu_des_libelles", "arbre", "elements"}
# les autres fonctions ne sont pas suivies : un script se sert souvent d'un autre comme bibliothèque (quelques petites
# fonctions), les suivre marquait presque tout le skin pour une retouche de club_page_bas
AUTRES_FONCTIONS = set(cat.FONCTIONS) | set(cat.AUTRES)
_IMPORT = re.compile(r"^\s*(?:from\s+(\w+)\s+import|import\s+([\w ,]+?)(?:\s+as\s+\w+)?\s*(?:#|$))", re.M)
_CITE = re.compile(r"[\"'](\w+)[\"']")
_index = {}
_cache = {}   # chemin -> ((taille, date), contenu normalisé, modules cités)


def _modules():
    """nom de module -> fichier, pour tous les scripts de outils\\<dossier>\\"""
    if not _index:
        for d in sorted(os.listdir(chemins.OUTILS)):
            p = os.path.join(chemins.OUTILS, d)
            if os.path.isdir(p) and not d.startswith(("_", ".")):
                for f in os.listdir(p):
                    if f.endswith(".py"):
                        _index.setdefault(f[:-3], os.path.join(p, f))
    return _index


def _lire(chemin):
    st = os.stat(chemin)
    cle = (st.st_size, st.st_mtime)
    c = _cache.get(chemin)
    if c and c[0] == cle:
        return c[1], c[2]
    with open(chemin, "rb") as f:
        brut = f.read().replace(b"\r\n", b"\n")
    texte = brut.decode("utf-8", "replace")
    noms = set()
    for a, b in _IMPORT.findall(texte):
        noms.update(x.strip() for x in (a or b).split(","))
    noms.update(_CITE.findall(texte))
    mods = _modules()
    cites = sorted(n for n in noms if n in mods and n not in GENERAUX and n not in AUTRES_FONCTIONS)
    _cache[chemin] = (cle, brut, cites)
    return brut, cites


def empreinte(nom):
    """sha256 du script de la fonction nom et des modules du skin qu'il utilise (de proche en proche), ou None"""
    mods = _modules()
    if nom not in mods:
        return None
    vus, a_voir, h = set(), [nom], hashlib.sha256()
    while a_voir:
        n = a_voir.pop()
        if n in vus:
            continue
        vus.add(n)
        try:
            brut, cites = _lire(mods[n])
        except OSError:
            continue
        a_voir.extend(cites)
    for n in sorted(vus):
        h.update(n.encode() + b"\0" + _cache[mods[n]][1] + b"\0")
    return h.hexdigest()


def lire():
    try:
        with open(FICHIER, encoding="utf-8-sig") as f:   # -sig : fichier retouché à la main (BOM)
            return json.load(f)
    except (OSError, ValueError):
        return {}


def noter(noms):
    """noms : fonctions tout juste appliquées avec succès (leur empreinte actuelle est gardée)"""
    if not os.path.isdir(backup.BACKUP_DIR):
        return
    d = lire()
    for n in noms:
        e = empreinte(n)
        if e:
            d[n] = e
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, sort_keys=True)


def a_reinstaller(nom, posees=None):
    """la fonction (activée) a changé depuis qu'elle a été posée dans le jeu"""
    posees = lire() if posees is None else posees
    return posees.get(nom) != empreinte(nom)


if __name__ == "__main__":   # essai : empreinte et modules suivis d'une fonction
    for n in sys.argv[1:]:
        print(n, empreinte(n), "à réinstaller" if a_reinstaller(n) else "à jour")
