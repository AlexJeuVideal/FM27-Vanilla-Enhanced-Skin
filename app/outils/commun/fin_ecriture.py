"""Fin de l'installation (choix 1, changement de langue) : barre de chargement jusqu'à être SÛR que les fichiers du jeu
sont bien écrits, au lieu de « attends une dizaine de secondes ».

Pour chaque bundle du jeu modifié depuis le début de l'installation :
  1. écriture forcée sur le disque (fsync : plus rien en attente dans le cache de Windows) ;
  2. contenu = celui qu'on a écrit (empreinte SHA-256 mémorisée par sauvegarde_originaux ; pour un bundle remis
     d'origine : celle de l'original sauvegardé) ;
  3. fichier libre (ouvrable en lecture / écriture : pas bloqué par l'antivirus ou un autre programme) ;
  4. bundle lisible (ouvert par UnityPy comme le ferait le jeu : il contient bien ses objets).
Puis plus aucun changement de taille / date pendant STABLE secondes. Chaque étape est réessayée jusqu'à ATTENTE_MAX
secondes ; « C'est bon » seulement si tout est passé, sinon le fichier en cause est nommé.

Usage : appelé par lancer.py (verifier(debut)) ; seul : fin_ecriture.py <fr|en> [depuis_secondes]
"""
import hashlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401
import sauvegarde_originaux as backup  # noqa: E402
from chemin_jeu import AA  # noqa: E402
import langue  # noqa: E402

ATTENTE_MAX = 60    # s, par étape, avant de dire qu'il y a un problème
STABLE = 3          # s sans aucun changement à la fin
LARGEUR = 40        # caractères de la barre

LG = "fr"


def T(fr, en):
    return langue.journal(fr, en, LG)


def barre(fait, total, texte):
    p = fait / total if total else 1
    n = int(p * LARGEUR)
    ligne = f"\r  [{'#' * n}{'-' * (LARGEUR - n)}] {int(p * 100):>3} %  {texte}"
    sys.stdout.write(ligne[:110].ljust(110))
    sys.stdout.flush()


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def attendu(nom):
    """empreinte que le fichier du jeu doit avoir, ou None si inconnue"""
    sauvegarde, ecrit = backup._paths(nom)
    if os.path.exists(ecrit):
        return open(ecrit).read().strip()
    if os.path.exists(sauvegarde):   # remis d'origine (restore efface l'empreinte écrite)
        return _sha(sauvegarde)
    return None


def _forcer(path):
    with open(path, "r+b") as f:
        os.fsync(f.fileno())
    return True


def _contenu(path, sha):
    return sha is None or _sha(path) == sha


def _libre(path):
    with open(path, "r+b"):
        return True


def _lisible(path):
    import UnityPy
    env = UnityPy.load(path)
    return len(env.objects) > 0


ETAPES = [(_forcer, "écriture sur le disque", "writing to disk"),
          (_contenu, "contenu vérifié", "content check"),
          (_libre, "fichier libre", "file not locked"),
          (_lisible, "bundle lisible", "bundle readable")]


def _essayer(etape, path, sha):
    fin = time.time() + ATTENTE_MAX
    while True:
        try:
            if etape(path, sha) if etape is _contenu else etape(path):
                return True
        except Exception:
            pass
        if time.time() > fin:
            return False
        time.sleep(0.5)


def verifier(debut, lg="fr"):
    """True si tous les bundles écrits depuis debut (time.time()) sont sûrs ; affiche la barre et le verdict"""
    global LG
    LG = lg
    print()
    print("=== " + T("Fin de l'écriture des fichiers du jeu", "Finishing writing the game files") + " ===")
    fichiers = sorted(os.path.join(AA, f) for f in os.listdir(AA)
                      if f.startswith("ui-") and f.endswith(".bundle")
                      and os.path.getmtime(os.path.join(AA, f)) >= debut - 2)
    total = len(fichiers) * len(ETAPES) + STABLE * 2
    fait = 0
    for path in fichiers:
        nom = os.path.basename(path)
        sha = attendu(nom)
        for etape, fr, en in ETAPES:
            barre(fait, total, f"{nom[:40]} : {T(fr, en)}")
            if not _essayer(etape, path, sha):
                print()
                print(T(f"PROBLÈME : {nom} ({fr}). NE LANCE PAS FM : relance le choix 1.",
                        f"PROBLEM: {nom} ({en}). DO NOT START FM: run choice 1 again."))
                return False
            fait += 1
    # plus aucun changement pendant STABLE secondes (rien d'autre n'écrit encore dedans)
    etat = None
    calme = 0.0
    fin = time.time() + ATTENTE_MAX
    while calme < STABLE:
        maintenant = [(os.path.getsize(p), os.path.getmtime(p)) for p in fichiers]
        calme = calme + 0.5 if maintenant == etat else 0.0
        etat = maintenant
        barre(fait + int(calme * 2), total, T("plus aucun changement…", "no more changes…"))
        if time.time() > fin:
            print()
            print(T("PROBLÈME : les fichiers changent encore. NE LANCE PAS FM : relance le choix 1.",
                    "PROBLEM: files are still changing. DO NOT START FM: run choice 1 again."))
            return False
        time.sleep(0.5)
    barre(total, total, T(f"{len(fichiers)} fichier(s) vérifié(s)", f"{len(fichiers)} file(s) checked"))
    print()
    print()
    print(T("C'EST BON : tout est écrit et vérifié, tu peux lancer FM.",
            "ALL GOOD: everything is written and checked, you can start FM."))
    return True


if __name__ == "__main__":
    lg = sys.argv[1] if len(sys.argv) > 1 else "fr"
    depuis = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    sys.exit(0 if verifier(time.time() - depuis, lg) else 1)
