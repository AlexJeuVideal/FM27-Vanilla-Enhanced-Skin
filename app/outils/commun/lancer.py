"""Lanceur du skin : menu par catégories de Outils FM.bat, choix 1, changement de langue, rangement des marqueurs.

Usage (Outils FM.bat) :
  lancer.py migrer                         anciens marqueurs (avant le rangement du 2026-11-12) -> nouveaux, une fois
  lancer.py menu <fr|en>                   liste des catégories (menu principal)
  lancer.py est_categorie <n>              code 0 si n est un numéro de catégorie
  lancer.py categorie <n> <fr|en>          fonctions de la catégorie n, avec leur état
  lancer.py verifier <n> <f>               code 0 si la fonction f existe dans la catégorie n
  lancer.py fonction <n> <f> <fr|en>       fiche de la fonction + ses actions
  lancer.py faire <n> <f> <action> <fr|en> action 1 appliquer, 2 retirer, 3 état, 4 essai à blanc (FM fermé pour 1 / 2)
  lancer.py skin <fr|en>                   choix 1 : essais retirés, textes, puis « si-actif » de chaque fonction
  lancer.py desinstaller <fr|en>           toutes les fonctions coupées, fichiers du jeu remis d'origine (l'app)
  lancer.py essais                         retire les zones d'essai
  lancer.py langue <fr|en>                 refait les fonctions à textes fixes (après un changement de langue)
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import catalogue as cat  # noqa: E402
import langue  # noqa: E402

LG = "fr"
DEPART_ORIGINE = "UIPICKER_DEPART_ORIGINE"   # variable posée par options.choisir après lancer.tout_d_origine()
# test par moitiés (124 du .bat, outil de Claude) : « groupe » remet tout d'origine puis ne pose que ces fonctions
SEULEMENT = set(filter(None, os.environ.get("UIPICKER_SEULEMENT", "").split(",")))


def T(fr, en):
    return langue.journal(fr, en, LG)


def chemin_script(nom):
    f = cat.FONCTIONS.get(nom)
    dossier = f["cat"] if f else ("essais" if nom in cat.ESSAIS else
                                  cat.AUTRES.get(nom) or cat.ABANDONNES.get(nom, "commun"))
    return os.path.join(chemins.OUTILS, dossier, nom + ".py")


def marqueur(nom):
    return os.path.join(backup.BACKUP_DIR, cat.FONCTIONS[nom].get("marqueur", nom) + ".actif")


def actif(nom):
    return os.path.exists(marqueur(nom))


def hors_guru(nom):
    """mode FM Guru (le joueur, 2026-11-10 : « full vanilla ») : seulement la fiche joueur et ce qui va avec
    (catalogue.AVEC_GURU) ; toute autre fonction n'est jamais posée, même activée"""
    import options
    return options.get("fiche_fmguru") == "guru" and nom not in cat.AVEC_GURU


def restes_guru():
    """mode FM Guru : autres fonctions activées quand même (la MAJ auto de l'app posait le marqueur des fonctions
    nouvelles de base avant v1.75 : salle des trophées, vue d'ensemble du club... chez FM Guru, 2026-11-10)"""
    return [n for n in cat.FONCTIONS if hors_guru(n) and actif(n)]


def nettoyer_guru():
    """mode FM Guru : marqueurs des autres fonctions retirés ; True s'il y en avait (fichiers à remettre d'origine)"""
    restes = restes_guru()
    for n in restes:
        os.remove(marqueur(n))
    if restes:
        print(T(f"mode FM Guru : {len(restes)} fonction(s) hors de la fiche joueur coupée(s), le reste du jeu redevient "
                "celui de FM", f"FM Guru mode: {len(restes)} feature(s) outside the player profile turned off, the "
                "rest of the game is FM's again"))
    return bool(restes)


def lancer(nom, *args):
    """lance un script dans son propre processus (un passage par modèle) ; renvoie son code"""
    sys.stdout.flush()
    return subprocess.run([sys.executable, chemin_script(nom)] + list(args)).returncode


def titre(fr, en):
    print(f"=== {T(fr, en)} ===", flush=True)


# ---------- catégories ----------
def categorie(n):
    """(dossier, titre fr, titre en) de la catégorie numéro n, ou None"""
    try:
        i = int(n) - cat.PREMIER_NUMERO
    except ValueError:
        return None
    return cat.CATEGORIES[i] if 0 <= i < len(cat.CATEGORIES) else None


def fonctions(dossier):
    return [nom for nom, f in cat.FONCTIONS.items() if f["cat"] == dossier]


def fonction(n, f):
    c = categorie(n)
    if c is None:
        return None
    lst = fonctions(c[0])
    try:
        i = int(f) - 1
    except ValueError:
        return None
    return lst[i] if 0 <= i < len(lst) else None


def etat_court(nom):
    if actif(nom):
        return T("[activé]", "[on]")
    return T("[pas activé]", "[off]")


def options_de(nom):
    """options (choix 500) qui changent cette fonction"""
    import options
    return [o for o, d in options.OPTIONS.items() if d["script"] == nom]


def ecarts(nom):
    """ce qui n'est pas le choix de base pour cette fonction : options changées, fonction pas activée (sauf
    facultative) ; liste de textes courts"""
    import options
    out = []
    if not actif(nom) and not cat.FONCTIONS[nom].get("facultatif"):
        out.append(T("pas activée", "off"))
    for o in options_de(nom):
        v = options.get(o)
        if v != options.defaut(o):
            fr, en = dict(options.OPTIONS[o]["valeurs"])[v]
            out.append(f"{T(*options.OPTIONS[o]['titre'])} : {T(fr, en)}")
    return out


def cmd_menu():
    for i, (dossier, fr, en) in enumerate(cat.CATEGORIES):
        noms = fonctions(dossier)
        on = sum(actif(x) for x in noms)
        n = sum(len([e for e in ecarts(x) if e != T("pas activée", "off")]) for x in noms)
        print(f"   {cat.PREMIER_NUMERO + i:>3}. {T(fr, en):<52} {on}/{len(noms)} " + T("activées", "on")
              + (T(f"   <== {n} option(s) pas de base", f"   <== {n} option(s) not default") if n else ""))


def cmd_categorie(n):
    c = categorie(n)
    if c is None:
        print(T("Catégorie inconnue.", "Unknown category."))
        sys.exit(1)
    print("==============================================")
    print(f"  {T(c[1], c[2])}")
    print("==============================================")
    print()
    for i, nom in enumerate(fonctions(c[0]), 1):
        f = cat.FONCTIONS[nom]
        print(f"   {i:>2}. {etat_court(nom):<14} {T(f['fr'], f['en'])}")
        for e in ecarts(nom):
            if e == T("pas activée", "off"):   # déjà dit par [pas activé]
                continue
            print(" " * 21 + T("<== pas le choix de base : ", "<== not the default: ") + e)
    print()
    print(T("   Tape le numéro d'une fonction pour l'appliquer / la retirer / voir son état.",
            "   Type a feature number to apply / remove it / see its status."))
    print(T("    0. Retour au menu", "    0. Back to the menu"))
    print()


def cmd_fonction(n, f):
    nom = fonction(n, f)
    c = categorie(n)
    fo = cat.FONCTIONS[nom]
    print("==============================================")
    print(f"  {T(c[1], c[2])}")
    print(f"  {T(fo['fr'], fo['en'])}")
    print("==============================================")
    print()
    print("   " + (T("Activée : remise automatiquement par le choix 1 (après une mise à jour de FM).",
                      "On: reapplied automatically by choice 1 (after an FM update).") if actif(nom) else
                    T("Pas activée : le choix 1 ne la pose pas.", "Off: choice 1 does not install it.")))
    print("   " + T("Réglages : en haut de ", "Settings: at the top of ")
          + os.path.relpath(chemin_script(nom), os.path.dirname(chemins.OUTILS)))
    print()
    if nom == "theme_fond":
        print(T("    1. Appliquer (couleur demandée)   2. Retirer (fond d'origine)   3. État   4. Aperçu",
                "    1. Apply (colour asked)   2. Remove (original background)   3. Status   4. Preview"))
    elif nom == "couleurs_interface":
        print(T("    1. Appliquer (couleurs demandées)   2. Retirer (couleurs de FM)   3. État   4. Essai à blanc",
                "    1. Apply (colours asked)   2. Remove (FM colours)   3. Status   4. Dry run"))
    else:
        print(T("    1. Appliquer      2. Retirer      3. État      4. Essai à blanc (rien n'est écrit)",
                "    1. Apply          2. Remove       3. Status    4. Dry run (nothing is written)"))
    print(T("    0. Retour", "    0. Back"))
    print()


def cmd_faire(n, f, action, args):
    nom = fonction(n, f)
    if nom == "couleurs_interface" and action in ("1", "4"):
        if not args:
            print(T("Couleurs (vide = garder ; fm = couleur de FM ; texte=auto = blanc sauf barre claire), ex. :",
                    "Colours (empty = keep; fm = FM colour; texte=auto = white unless the bar is light), e.g.:"))
            print("   barre=#1D3B57 texte=auto barre2=#2B2F36 accent=#B145E3")
            args = input(T("Couleurs : ", "Colours: ")).split()
            if not args:
                print(T("Rien de changé.", "Nothing changed."))
                return
        return lancer(nom, "appliquer", *args, *(["--dry-run"] if action == "4" else []))
    if nom == "theme_fond" and action in ("1", "4"):
        if not args:
            lancer(nom, "liste")
            args = input(T("Couleur : ", "Colour: ")).split()
            if not args:
                print(T("Aucune couleur : rien n'a été changé.", "No colour: nothing was changed."))
                return
        return lancer(nom, "appliquer" if action == "1" else "apercu", *args)
    op = {"1": ["appliquer"], "2": ["retirer"], "3": ["etat"], "4": ["appliquer", "--dry-run"]}.get(action)
    if op is None:
        print(T("Action inconnue.", "Unknown action."))
        return
    backup.rafraichir()   # sauvegardes périmées (MAJ de FM) refaites d'abord, comme dans l'app
    code = lancer(nom, *op)
    if action in ("1", "2"):   # fonctions qui retouchent ses modèles : relancées après elle
        for s in cat.SUIVANTS.get(nom, []):
            lancer(s, "si-actif")
    if action == "1" and code == 0:
        import versions_posees
        versions_posees.noter([nom])
    return code


# ---------- choix 1, langue, essais ----------
def cmd_essais():
    for nom in cat.ESSAIS + list(cat.ABANDONNES):
        lancer(nom, "retirer")


def fin(debut):
    """barre de chargement jusqu'à être sûr que les fichiers du jeu sont écrits (fin_ecriture.py)"""
    import fin_ecriture
    sys.stdout.flush()
    if not fin_ecriture.verifier(debut, LG):
        sys.exit(1)


def cmd_skin():
    import time
    debut = time.time()
    titre("Sauvegarde des fichiers d'origine", "Backing up the original files")
    import chemin_jeu
    compat = backup.compatibilite(chemin_jeu.AA)   # autre mise à jour de FM : on prévient, on n'arrête pas
    if compat["etat"] == "different":
        print(backup.MESSAGE_AUTRE_MAJ + "".join(f"\n  - {n}" for n in compat["fichiers"]) + "\n")
    backup.tout()   # jeu déjà modifié sans sauvegarde propre : arrêt ici (code 2), rien n'est écrit
    print()
    import options
    options.appliquer_forces()   # une fois par option de options.FORCES (v1.62 : grande tuile de l'en-tête)
    marqueurs_de_base()
    activer_notes_staff()
    activer_offres()
    if nettoyer_guru() and not os.environ.get(DEPART_ORIGINE):   # mode Guru : retirées en remettant les originaux
        tout_d_origine()
        os.environ[DEPART_ORIGINE] = "1"
    os.environ[backup.SANS_COMPRESSION] = "1"   # scripts : bundles écrits sans compression, recompressés une fois à la fin
    try:
        posees = _skin_fonctions()
    finally:
        os.environ.pop(backup.SANS_COMPRESSION, None)
        titre("Compression des fichiers du jeu", "Compressing the game files")
        backup.recompresser(chemin_jeu.AA)
        print()
    fin(debut)
    import versions_posees
    versions_posees.noter(posees)
    oublier_jeu_mis_a_jour()


def _skin_fonctions():
    depart_origine = bool(os.environ.get(DEPART_ORIGINE))
    if not depart_origine:   # fichiers d'origine : aucune zone d'essai à retirer
        titre("Retrait des essais - zones de test", "Removing tests - test zones")
        cmd_essais()
        print()
    import options
    # recette des textes = installations seulement : avec leur fonction (posée d'office, elle restait fonction coupée,
    # 2026-10-31) ; mode FM Guru : rien d'autre que la fiche joueur (demande du joueur)
    if options.get("fiche_fmguru") != "guru" and actif("notes_installations") and (
            not SEULEMENT or "notes_installations" in SEULEMENT):
        titre("Textes - notes au lieu des libellés", "Texts - ratings instead of labels")
        lancer("notes_au_lieu_des_libelles", "apply")
        print()
    # fichiers tout juste remis d'origine (changement de mode Guru) : les fonctions coupées n'ont rien à faire, on ne
    # les lance pas (un processus Python par fonction : c'était l'essentiel du temps, 2026-11-12)
    posees = []   # versions_posees : bouton « Réinstaller » de l'app
    for nom in cat.ORDRE_SKIN:
        if depart_origine and not actif(nom):
            continue
        if hors_guru(nom):   # mode FM Guru : jamais rien d'autre que la fiche joueur
            continue
        if SEULEMENT and nom not in SEULEMENT:   # test par moitiés (124) : les autres restent d'origine
            continue
        f = cat.FONCTIONS[nom]
        c = next(x for x in cat.CATEGORIES if x[0] == f["cat"])
        titre(f"{c[1]} - {f['fr']}", f"{c[2]} - {f['en']}")
        if lancer(nom, "si-actif") == 0 and actif(nom):
            posees.append(nom)
        print()
    if SEULEMENT:
        return posees
    titre("Joueur : fiche - vue FM Guru (si choisie)", "Player: profile - FM Guru view (if chosen)")
    # en dernier : par-dessus toutes les fonctions de la fiche
    if lancer("fiche_fmguru", "si-actif") == 0 and options.get("fiche_fmguru") == "guru":
        posees.append("fiche_fmguru")
    print()
    return posees


def oublier_jeu_mis_a_jour():
    """skin réinstallé (ou tout retiré) : plus de page « Une mise à jour du jeu a été détectée » dans l'app"""
    try:
        os.remove(backup.JEU_MIS_A_JOUR)
    except OSError:
        pass


def cmd_langue():
    import time
    debut = time.time()
    titre("Textes du skin en français", f"Skin texts: {langue.NOMS.get(LG, LG)}")
    for nom in cat.ORDRE_SKIN:
        if cat.FONCTIONS[nom].get("textes"):
            lancer(nom, "si-actif")
    fin(debut)


def marqueurs_de_base():
    """aucune fonction activée (après « Désinstaller tout ») : le choix 1 remet celles du skin de base (comme le partage,
    maj_partage.py), sinon il n'installerait rien"""
    if not os.path.isdir(backup.BACKUP_DIR) or any(actif(n) for n in cat.FONCTIONS):
        return
    import options
    guru = options.get("fiche_fmguru") == "guru"   # mode FM Guru : seulement ce que garde la fiche
    for n, f in cat.FONCTIONS.items():
        if (n in cat.AVEC_GURU) if guru else not f.get("facultatif"):
            with open(marqueur(n), "w", encoding="utf-8") as fi:
                json.dump({"actif": True}, fi)
    print(T("aucune fonction activée : celles du skin de base sont remises", "no feature enabled: the default skin ones are back"))


def cmd_desinstaller():
    """« Désinstaller tout » de l'app (2026-11-12) : toutes les fonctions coupées (marqueurs retirés, réglages et
    sauvegardes gardés) et chaque fichier du jeu modifié remis d'origine ; on active ensuite seulement ce qu'on veut"""
    titre("Désinstaller tout le skin", "Uninstall the whole skin")
    n = 0
    for nom, f in cat.FONCTIONS.items():
        if actif(nom):
            if f.get("hors_jeu"):   # fichiers hors du jeu (vues) : pas remis par tout_d_origine, son script les retire
                lancer(nom, "retirer")
            if os.path.exists(marqueur(nom)):
                os.remove(marqueur(nom))
            n += 1
    print(T(f"{n} fonction(s) coupée(s)", f"{n} feature(s) turned off"))
    tout_d_origine()
    oublier_jeu_mis_a_jour()


def tout_d_origine():
    """chaque fichier du jeu différent de sa sauvegarde remis d'origine (Désinstaller tout, changement de mode Guru)"""
    import chemin_jeu
    remis = 0
    for f in backup.FICHIERS:
        p = os.path.join(chemin_jeu.AA, f)
        if not os.path.exists(backup.backup_path(p)) or not os.path.exists(p):
            continue
        if backup._sha(p) == backup._sha(backup.backup_path(p)):
            continue   # déjà d'origine
        try:
            backup.restore(p)
            remis += 1
        except SystemExit as e:   # jeu mis à jour depuis : le fichier du jeu est déjà le nouvel original
            print(f"{f} : {e}")
    print(T(f"\n{remis} fichier(s) du jeu remis d'origine : FM est comme sans le skin",
            f"\n{remis} game file(s) put back to original: FM is as without the skin"))


def retirer_par_restauration(marker):
    """pour les ajouts qui ne se retirent qu'en remettant les modèles d'origine (bundles de modèles) : marqueur
    retiré, modèles d'origine remis, puis tout le reste du skin refait (choix 1)"""
    import notes_au_lieu_des_libelles as nb
    if os.path.exists(marker) and not nb.DRY_RUN:
        os.remove(marker)
    if not any(os.path.exists(backup.backup_path(b)) for b in nb.BUNDLES):
        sys.exit("aucun modèle n'a été modifié : rien à retirer")
    if nb.DRY_RUN:
        print("(essai à blanc : rien retiré)")
        return
    nb.cmd_restore()
    print("\nmodèles d'origine remis : le reste du skin est refait (comme le choix 1)\n")
    subprocess.run([sys.executable, os.path.abspath(__file__), "skin", langue.LANGUE])


def activer_notes_staff():
    """notes du staff : appliquées d'office jusqu'au 2026-11-12, puis fonction avec interrupteur (notes_staff). Une
    fois : marqueur posé pour ne rien perdre chez ceux qui avaient le skin (ensuite, l'interrupteur décide)"""
    fait = os.path.join(backup.BACKUP_DIR, "notes_staff_v1.fait")
    # marqueur posé par les anciennes versions sous un autre nom (notes_staff_<date>.fait) : retrouvé par le motif
    if glob.glob(os.path.join(backup.BACKUP_DIR, "notes_staff_*.fait")) or not os.path.isdir(backup.BACKUP_DIR):
        return
    m = marqueur("notes_staff")
    if not os.path.exists(m):
        with open(m, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
    with open(fait, "w", encoding="utf-8") as f:
        f.write("notes du staff passées en fonction (marqueur posé une fois)\n")


def activer_offres():
    """club_infobulle_offres : de base, mais livrée sans marqueur en v1.18 (oubli). Une fois : marqueur posé chez ceux
    qui l'ont eue désactivée par erreur (ensuite, l'interrupteur décide)"""
    fait = os.path.join(backup.BACKUP_DIR, "club_infobulle_offres_v1.19.fait")
    if os.path.exists(fait) or not os.path.isdir(backup.BACKUP_DIR):
        return
    m = marqueur("club_infobulle_offres")
    if not os.path.exists(m):
        with open(m, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
    with open(fait, "w", encoding="utf-8") as f:
        f.write("club_infobulle_offres activée une fois (oubli du marqueur en v1.18)\n")


# ---------- rangement du 2026-11-12 ----------
def cmd_migrer():
    fait = os.path.join(backup.BACKUP_DIR, "rangement_v1.fait")
    # marqueur des anciennes versions sous un autre nom (rangement_<date>.fait) : retrouvé par le motif
    if glob.glob(os.path.join(backup.BACKUP_DIR, "rangement_*.fait")) or not os.path.isdir(backup.BACKUP_DIR):
        return
    for ancien, nouveaux in cat.MIGRATION.items():
        p = os.path.join(backup.BACKUP_DIR, ancien + ".actif")
        if not os.path.exists(p):
            continue
        for n in nouveaux:
            q = os.path.join(backup.BACKUP_DIR, cat.FONCTIONS[n].get("marqueur", n) + ".actif")
            if not os.path.exists(q):
                with open(q, "w", encoding="utf-8") as f:
                    json.dump({"actif": True}, f)
        if ancien not in nouveaux:
            os.remove(p)
    with open(fait, "w", encoding="utf-8") as f:
        f.write("anciens marqueurs passés au rangement par catégories\n")


def main(argv):
    global LG
    op = argv[0] if argv else ""
    if len(argv) > 1 and argv[-1] in langue.LANGUES and op not in ("faire",):
        LG = argv[-1]
    if op == "migrer":
        cmd_migrer()
    elif op == "menu":
        cmd_menu()
    elif op == "est_categorie" and len(argv) > 1:
        sys.exit(0 if categorie(argv[1]) else 1)
    elif op == "categorie" and len(argv) > 1:
        cmd_categorie(argv[1])
    elif op == "verifier" and len(argv) > 2:
        sys.exit(0 if fonction(argv[1], argv[2]) else 1)
    elif op == "fonction" and len(argv) > 2:
        cmd_fonction(argv[1], argv[2])
    elif op == "faire" and len(argv) > 4:
        LG = argv[4]
        cmd_faire(argv[1], argv[2], argv[3], argv[5:])
    elif op == "skin":
        cmd_skin()
    elif op == "desinstaller":
        cmd_desinstaller()
    elif op == "groupe" and SEULEMENT:
        tout_d_origine()
        os.environ[DEPART_ORIGINE] = "1"
        cmd_skin()
    elif op == "essais":
        cmd_essais()
    elif op == "langue":
        cmd_langue()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
