"""Sauvegarde des bundles d'origine, robuste aux mises à jour du jeu.

Après chaque écriture on mémorise l'empreinte (SHA-256) du fichier écrit. À l'écriture suivante :
- fichier du jeu == empreinte mémorisée -> c'est encore notre version, la sauvegarde d'origine reste valable ;
- sinon -> FM a été mis à jour (ou vérifié par Steam) : le fichier actuel est le nouvel original, on le sauvegarde.
Ainsi "restore" ne remet jamais un bundle d'une ancienne version du jeu.

« Fichier propre » (2026-11-12) : un fichier n'est sauvegardé comme original que s'il ne contient pas déjà le skin
(sinon, sur un jeu déjà modifié sans backups\\, l'original serait faux pour toujours). Propre =
- empreinte dans EMPREINTES_ORIGINE (fichiers d'origine connus de la version de FM27 du joueur), ou = sauvegarde ;
- sinon, bundles de MARQUABLES : aucun « uipicker » dans les données (tout ajout du skin s'appelle UIPicker… /
  uipicker-…) ; autres bundles (tuiles, fonds, styles : modifiés sans nom) : aucun bundle marquable du jeu ne
  contient d'ajout inconnu (le skin pose toujours des marques dans les modèles d'écran en même temps).
Pas propre -> refus : Steam « Vérifier l'intégrité des fichiers du jeu », puis recommencer.

Usage : sauvegarde_originaux.py tout        -> sauvegarde tout de suite les originaux manquants (code 2 si pas propre)
        sauvegarde_originaux.py empreintes  -> écrit EMPREINTES_ORIGINE d'après les sauvegardes (propres) de backups\\
        sauvegarde_originaux.py rafraichir  -> sauvegardes périmées (MAJ de FM) refaites si le jeu est propre ; lancé par
                                               l'app avant chaque action (2026-11-12 : avant, seule l'installation
                                               complète le faisait -> plantage en activant une fonction seule)
"""
import hashlib
import os
import shutil
import sys

BACKUP_DIR = os.environ.get("UIPICKER_BACKUPS") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backups")   # variable : banc d'essai (copies)
# Mac (2026-11-06) : les bundles StandaloneOSX ne sont pas ceux de Windows (autres empreintes, autre catalog.hash) :
# fichier à part, absent au départ -> compatibilité « inconnu » (n'empêche rien) ; « empreintes » le crée sur le Mac
EMPREINTES_ORIGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "empreintes_origine_mac.txt" if sys.platform == "darwin" else "empreintes_origine.txt")
MESSAGE_MAC_ECRITURE = (
    "macOS refuse d'écrire dans fm.app. Réglages Système > Confidentialité et sécurité > Gestion des apps : autorise "
    "Terminal (ou l'app qui lance le skin), puis recommence.\n"
    "macOS refuses to write into fm.app. System Settings > Privacy & Security > App Management: allow Terminal (or the "
    "app that runs the skin), then try again.")

# seuls fichiers du jeu que le skin a le droit d'écrire (write_bundle refuse les autres : en ajouter un = l'écrire ici)
FICHIERS = [
    "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle",
    "ui-tileslayouts_assets_all.bundle",
    "ui-backgrounds_assets_.bundle",
    "ui-styles_assets_common.bundle",
    "ui-styles_assets_default.bundle",
    "ui-tableviews_assets_all.bundle",
    "ui-tablefactories_assets_all.bundle",
    "ui-datacollections_assets_all.bundle",   # club_amical v19 (table UniqueId -> n° du moteur)
    "gamemodules_assets_gameworld.bundle",    # Kinito : kinito_calendrier_rencontres (menu du Portail)
    "ui-panelids_assets_all.bundle",          # Kinito : kinito_vacances_jour (panneau des vacances)
    "ui-globalnavigation_assets_all.bundle",  # Kinito : kinito_calendrier_rencontres v3 (menu du Portail, déplacé là)
    "ui-visualfunctions_assets_all.bundle",   # club_amical v14 (fonction FM inutilisée réécrite, UIPickerSoustraction)
]
# ceux où chaque ajout du skin laisse le mot « uipicker » (noms, classes, debug_name)
# par nom, pas par rang : le partage n'a pas la ligne datacollections (rang 13 hors liste là-bas, 2026-11-12)
MARQUABLES = [f for f in FICHIERS if f.startswith(("ui-visualtreeassets_", "ui-tableviews_", "ui-tablefactories_",
                                                    "ui-visualfunctions_"))]
MARQUE = b"uipicker"


class PasPropre(SystemExit):
    pass


MESSAGE_PAS_PROPRE = (
    "Ton jeu contient déjà des modifications du skin (fichiers ci-dessous) : impossible de sauvegarder les "
    "originaux.\nSteam > clic droit sur Football Manager 27 > Propriétés > Fichiers installés > Vérifier "
    "l'intégrité des fichiers du jeu, puis recommence.\n"
    "Your game already contains skin changes (files below): the originals can't be backed up.\n"
    "Steam > right-click Football Manager 27 > Properties > Installed Files > Verify integrity of game files, "
    "then try again.")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _nom(bundle):
    return os.path.basename(bundle)


def version_fm(dossier_bundles):
    """repère de la version des fichiers de FM : aa\\catalog.hash (change à chaque mise à jour des bundles)"""
    try:
        with open(os.path.join(os.path.dirname(dossier_bundles), "catalog.hash"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def empreintes_origine():
    """(version de FM, {nom: sha}) des fichiers d'origine connus"""
    version, connues = "", {}
    try:
        with open(EMPREINTES_ORIGINE, encoding="utf-8") as f:
            for ligne in f:
                p = ligne.split()
                if len(p) == 3 and p[0] == "version":
                    version = p[2]
                elif len(p) == 2 and not ligne.startswith("#"):
                    connues[p[0]] = p[1].lower()
    except OSError:
        pass
    return version, connues


def contient_marques(path):
    """le mot « uipicker » dans les données décompressées du bundle (≈ 0,5 s pour le plus gros)"""
    import UnityPy   # ici seulement : l'app importe ce module avec le Python de Windows, sans UnityPy
    env = UnityPy.load(path)
    for f in env.file.files.values():
        r = getattr(f, "reader", None)
        donnees = r.bytes if r is not None and hasattr(r, "bytes") else getattr(f, "bytes", b"")
        if MARQUE in bytes(donnees).lower():
            return True
    return False


_suspect = {}


def _jeu_suspect(dossier):
    """un bundle marquable du jeu contient des ajouts du skin qui ne sont pas les nôtres (empreinte écrite) ?"""
    if dossier not in _suspect:
        _suspect[dossier] = False
        for n in MARQUABLES:
            p = os.path.join(dossier, n)
            if not os.path.exists(p):
                continue
            ecrit = _paths(p)[1]
            if os.path.exists(ecrit) and open(ecrit).read().strip() == _sha(p):
                continue   # notre version, connue
            if contient_marques(p):
                _suspect[dossier] = True
                break
    return _suspect[dossier]


def propre(bundle):
    """le fichier du jeu peut-il servir d'original ?"""
    version, connues = empreintes_origine()
    if version and version == version_fm(os.path.dirname(bundle)) and _nom(bundle) in connues:
        return _sha(bundle) == connues[_nom(bundle)]   # même version de FM : seule l'empreinte d'origine fait foi
    if _nom(bundle) in MARQUABLES:
        return not contient_marques(bundle)
    return not _jeu_suspect(os.path.dirname(bundle))


def _paths(bundle):
    name = os.path.basename(bundle)
    return os.path.join(BACKUP_DIR, name), os.path.join(BACKUP_DIR, name + ".written.sha256")


def backup_path(bundle):
    return _paths(bundle)[0]


def sauvegarde_valable(bundle):
    """backups\\ a déjà le bon original (rien à copier)"""
    backup, written = _paths(bundle)
    if not os.path.exists(backup):
        return False
    version, connues = empreintes_origine()
    if version and version == version_fm(os.path.dirname(bundle)) and connues.get(_nom(bundle)) == _sha(backup):
        return True   # sauvegarde = original connu de cette version de FM (même si un autre outil a réécrit le jeu)
    ours = open(written).read().strip() if os.path.exists(written) else None
    sha = _sha(bundle)
    if ours is None:
        return sha == _sha(backup)   # jeu d'origine (sauvegardé à l'étape 3, ou remis par restore)
    return sha == ours   # le jeu contient encore notre version : l'original sauvegardé reste le bon


def ensure_original(bundle):
    """à appeler AVANT d'écrire : garantit que backups\\ contient l'original de la version actuelle du jeu"""
    if _nom(bundle) not in FICHIERS:
        raise SystemExit(f"{_nom(bundle)} : fichier absent de sauvegarde_originaux.FICHIERS (l'y ajouter)")
    backup = _paths(bundle)[0]
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if sauvegarde_valable(bundle):
        return
    if not propre(bundle):
        raise PasPropre(f"{MESSAGE_PAS_PROPRE}\n  - {_nom(bundle)}")
    if os.path.exists(backup):
        print("le jeu a changé depuis la dernière modification (mise à jour ?) : nouvel original sauvegardé")
    shutil.copy2(bundle, backup)
    print(f"original sauvegardé : {backup}")


def write_bundle(bundle, data):
    """écrit le bundle modifié et mémorise son empreinte"""
    ensure_original(bundle)
    try:
        f = open(bundle, "wb")
    except PermissionError:
        if sys.platform == "darwin":   # protection des apps de macOS (Gestion des apps), pas un problème de droits
            raise SystemExit(MESSAGE_MAC_ECRITURE)
        raise
    with f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())   # vraiment sur le disque avant de continuer
    _, written = _paths(bundle)
    with open(written, "w") as f:
        f.write(hashlib.sha256(data).hexdigest())   # ce qu'on voulait écrire (vérifié à la fin : fin_ecriture.py)
    print(f"bundle écrit : {bundle} ({len(data) / 1e6:.2f} Mo)")


def restore(bundle):
    backup, written = _paths(bundle)
    if not os.path.exists(backup):
        raise SystemExit("pas de sauvegarde : ce bundle n'a jamais été modifié par ces outils")
    ours = open(written).read().strip() if os.path.exists(written) else None
    if ours is not None and _sha(bundle) != ours:
        raise SystemExit("le bundle du jeu a changé depuis la dernière modification (mise à jour ?) : "
                         "il est déjà d'origine, rien à restaurer")
    shutil.copy2(backup, bundle)
    if os.path.exists(written):
        os.remove(written)
    print(f"original remis en place : {bundle}")


def compatibilite(dossier_bundles):
    """le jeu est-il de la mise à jour de FM pour laquelle le skin a été préparé (EMPREINTES_ORIGINE) ?
    {"etat": "ok" | "different" | "inconnu", "fichiers": [fichiers du skin changés par la mise à jour]}
    Même catalog.hash -> ok. Sinon, l'original de chaque fichier (sauvegarde valable, sinon fichier du jeu) est comparé
    à son empreinte : une mise à jour de FM qui ne touche aucun des 9 fichiers reste « ok »."""
    version, connues = empreintes_origine()
    if not version or not connues:
        return {"etat": "inconnu", "fichiers": []}
    if version == version_fm(dossier_bundles):
        return {"etat": "ok", "fichiers": []}
    changes = []
    for n in FICHIERS:
        p = os.path.join(dossier_bundles, n)
        if not os.path.exists(p):
            changes.append(n)
            continue
        original = _paths(p)[0] if sauvegarde_valable(p) else p
        if _sha(original) != connues.get(n):
            changes.append(n)
    return {"etat": "different" if changes else "ok", "fichiers": changes}


MESSAGE_AUTRE_MAJ = (
    "ATTENTION : ton FM27 n'est pas de la même mise à jour que ce skin (fichiers changés ci-dessous). "
    "L'installation peut quand même marcher, mais certaines parties risquent de manquer.\n"
    "WARNING: your FM27 is not on the same update as this skin (changed files below). "
    "The install may still work, but some parts may be missing.")


def tout():
    """sauvegarde dès l'installation (étape 3 de l'app) : chaque fichier de FICHIERS sans sauvegarde valable est
    copié s'il est propre ; rien n'est copié si l'un d'eux ne l'est pas (code 2)"""
    import chemin_jeu
    os.makedirs(BACKUP_DIR, exist_ok=True)
    a_copier, sales = [], []
    for i, n in enumerate(FICHIERS, 1):
        p = os.path.join(chemin_jeu.AA, n)
        if not os.path.exists(p):
            raise SystemExit(f"fichier du jeu introuvable / game file not found : {p}")
        if sauvegarde_valable(p):
            abimee = n in MARQUABLES and contient_marques(_paths(p)[0])
            print(f"[{i}/{len(FICHIERS)}] {n} : " + ("SAUVEGARDE ABÎMÉE (contient le skin) / damaged backup"
                                                    if abimee else "déjà sauvegardé / already backed up"))
            if abimee:
                sales.append(n)
        elif propre(p):
            print(f"[{i}/{len(FICHIERS)}] {n} : d'origine / original")
            a_copier.append(p)
        else:
            print(f"[{i}/{len(FICHIERS)}] {n} : DÉJÀ MODIFIÉ / ALREADY MODIFIED")
            sales.append(n)
    if sales:
        print("\n" + MESSAGE_PAS_PROPRE + "".join(f"\n  - {n}" for n in sales))
        sys.exit(2)
    for p in a_copier:
        if os.path.exists(_paths(p)[1]):
            os.remove(_paths(p)[1])   # ancienne empreinte (jeu mis à jour) : le nouvel original fait foi
        shutil.copy2(p, _paths(p)[0])
    print(f"\noriginaux sauvegardés / originals backed up : {len(a_copier)} (déjà / already : "
          f"{len(FICHIERS) - len(a_copier)})")


def rafraichir():
    """avant chaque action (activer / retirer une fonction, options, couleurs, langue, vérification) : chaque sauvegarde
    périmée (le jeu a changé, ex. mise à jour de FM) est remplacée par le fichier du jeu s'il est propre. Silencieux sinon,
    n'arrête jamais rien (un fichier pas propre garde sa sauvegarde ; l'installation complète, elle, prévient)"""
    import chemin_jeu
    if not os.path.isdir(BACKUP_DIR):
        return
    for n in FICHIERS:
        p = os.path.join(chemin_jeu.AA, n)
        bk, written = _paths(p)
        if not os.path.exists(p) or not os.path.exists(bk) or sauvegarde_valable(p) or not propre(p):
            continue
        if os.path.exists(written):
            os.remove(written)   # ancienne empreinte (jeu mis à jour) : le nouvel original fait foi
            with open(JEU_MIS_A_JOUR, "w", encoding="utf-8") as f:   # l'app garde sa page « réinstalle le skin »
                f.write(version_fm(chemin_jeu.AA))
        shutil.copy2(p, bk)
        print(f"{n} : jeu mis à jour, nouvel original sauvegardé / game updated, new original backed up")


# v1.25 (le joueur) : page « Une mise à jour du jeu a été détectée » de l'app. Le skin est installé mais FM (mise à jour,
# vérification Steam) a remplacé des fichiers qu'il avait écrits : il n'y est plus, à réinstaller. rafraichir() efface
# l'empreinte écrite de ces fichiers : il laisse ce repère, que l'app retire après une installation complète réussie.
JEU_MIS_A_JOUR = os.path.join(BACKUP_DIR, "jeu_mis_a_jour.txt")


def fichiers_remplaces(dossier_bundles):
    """fichiers écrits par le skin (empreinte écrite) que le jeu a remplacés depuis (≈ 0,3 s : sha des 12 fichiers).
    Bundle marquable qui contient encore le skin : pas compté (réécrit par une autre copie de l'app, avec ses propres
    sauvegardes : vu chez nous le 2026-11-12, le jeu n'a rien remplacé). Python de l'app sans UnityPy (anciennes
    installations, sans le Python du Setup) : pas de contrôle des marques"""
    try:
        import UnityPy  # noqa: F401
        marques = True
    except ImportError:
        marques = False
    out = []
    for n in FICHIERS:
        p = os.path.join(dossier_bundles, n)
        written = _paths(p)[1]
        if os.path.exists(written) and os.path.exists(p) and open(written).read().strip() != _sha(p) \
                and not (marques and n in MARQUABLES and contient_marques(p)):
            out.append(n)
    return out


def ecrire_empreintes():
    """empreintes des sauvegardes de backups\\ (vérifiées sans marque) -> EMPREINTES_ORIGINE, à refaire après une MAJ
    de FM une fois les sauvegardes propres"""
    import chemin_jeu
    version = version_fm(chemin_jeu.AA)
    if not version:
        raise SystemExit("catalog.hash introuvable : version de FM inconnue")
    lignes = [f"version = {version}"]
    for n in FICHIERS:
        p = os.path.join(BACKUP_DIR, n)
        if not os.path.exists(p):
            raise SystemExit(f"pas de sauvegarde : {n}")
        if n in MARQUABLES and contient_marques(p):
            raise SystemExit(f"sauvegarde abîmée (contient le skin) : {n}")
        lignes.append(f"{n} {_sha(p)}")
    with open(EMPREINTES_ORIGINE, "w", encoding="utf-8") as f:
        f.write("# fichiers d'origine de FM27 (sauvegarde_originaux.py empreintes) : nom sha256\n" + "\n".join(lignes) + "\n")
    print(f"{len(lignes) - 1} empreintes écrites (version {version}) : {EMPREINTES_ORIGINE}")


# v1.33 (le joueur, 2026-11-12) : « Installer tout le skin » plus rapide. Chaque fonction recompressait le bundle entier
# à chaque écriture (≈ 2 s pour le plus gros, 135 s sur 340 au banc). Pendant le choix 1 (variable SANS_COMPRESSION,
# posée par lancer.cmd_skin pour ses scripts), packer="original" écrit sans compression ; recompresser() remet la
# compression d'origine à la fin, une seule fois (fichiers identiques à l'octet près à l'ancienne méthode, banc).
# Fonctions seules, retrait, essais à blanc : inchangés.
SANS_COMPRESSION = "UIPICKER_SANS_COMPRESSION"


def _sans_compression():
    try:
        from UnityPy.files import BundleFile
    except ImportError:
        return
    save = BundleFile.save
    if getattr(save, "_uipicker", False):
        return

    def sans(self, packer=None):
        return save(self, "none" if packer == "original" else packer)
    sans._uipicker = True
    BundleFile.save = sans


if os.environ.get(SANS_COMPRESSION):
    _sans_compression()


def recompresser(dossier_bundles):
    """fin du choix 1 : chaque bundle écrit sans compression reprend celle de son original (sauvegarde)"""
    import UnityPy
    for n in FICHIERS:
        p = os.path.join(dossier_bundles, n)
        bk = _paths(p)[0]
        if not os.path.exists(p) or not os.path.exists(bk):
            continue
        env = UnityPy.load(p)
        if int(env.file.dataflags) & 0x3F:   # déjà compressé : rien à faire
            continue
        orig = UnityPy.load(bk).file
        data = env.file.save(packer=(int(orig.dataflags), orig._block_info_flags))
        del env
        write_bundle(p, data)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    op = sys.argv[1] if len(sys.argv) > 1 else ""
    if op == "tout":
        tout()
    elif op == "empreintes":
        ecrire_empreintes()
    elif op == "rafraichir":
        rafraichir()
    else:
        sys.exit(__doc__)
