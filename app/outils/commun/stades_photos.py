"""Photos des stades de la page club (club_page_bas, toujours depuis la v18) : dossier graphics de FM.

v1.73 (2026-11-10) : photos rangées par ID DE STADE, format des packs d'internet (sortitoutsi, FM Scout, FM24...) :
  config.xml `from="..." to="graphics/pictures/stadium/<id du stade>/background"`.
Notre pack FMVE Stadium : STADIUM<id du stade>.png / .jpg, 1280 x 720 (16:9), dans
  Documents\\Sports Interactive\\Football Manager 27\\graphics\\FMVE Stadium
  (Mac : ~/Library/Application Support/Sports Interactive/Football Manager 27/graphics/FMVE Stadium)
(dossier graphics choisi dans l'app s'il est ailleurs : backups\\dossier_graphics.txt ; ancien nom « UIPicker
Stades » renommé tout seul) ; son config.xml est refait d'après les images présentes.
FM ne donne pas l'id du stade aux modèles (essais v20 / v21 / v34 ratés) : lier() lit les config.xml de TOUS les
packs de graphics, passe par la table stade -> équipes de FM27 (stades_clubs.txt.gz, ids_fm) et range un lien
physique par club (copie si impossible) dans « FMVE Stadium Links » : STDM<id du club>.<ext> ->
graphics/pictures/comp/<id du club>/logo, que le bloc Stade lit avec l'id du club (validé en jeu le 2026-11-10).
Ordre : packs d'autres sites d'abord, FMVE Stadium ensuite. Ancien pack (STDM<id du club> / <id du club>, jusqu'à
la v1.72) : encore lié tel quel en dernier, et migrer() (alerte obligatoire de l'app) le convertit par id de stade.
Une photo au numéro d'une compétition remplacerait son logo : ces ids (competitions.txt.gz) ne vont jamais dans
le config.xml des liens (seuls clubs concernés : sélections 106-122, sans page club).

Bibliothèque standard seulement (appelé aussi par l'app au démarrage).
Usage : stades_photos.py   -> (dossier, nombre de photos), à blanc
"""
import ctypes
import os
import plistlib
import re
import sys
import threading
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemin_jeu  # noqa: E402  (Linux : profil Windows du préfixe Proton)

DOSSIER = "FMVE Stadium"
ANCIEN = "UIPicker Stades"   # nom jusqu'à la v1.12
LIENS = "FMVE Stadium Links"   # v1.73 : refait par lier() (un lien par club), jamais à la main
CIBLE = "graphics/pictures/comp/{id}/logo"   # liens : emplacement lu par le bloc Stade (id du club)
CIBLE_STADE = "graphics/pictures/stadium/{id}/background"   # format des packs d'internet (id du stade)
# v1.53 : noms STDM<id du club> (comme TCM1_<id> des logos TCM actuels ; l'ancien TCM aux noms = id nu bloquait nos
# photos). v1.73 : FMVE Stadium par id de STADE, STADIUM<id> ; STDM<id du club> = ancien pack (ou les liens).
PREFIXE = "STDM"
PREFIXE_STADE = "STADIUM"
IMAGE = re.compile(r"^(?:" + PREFIXE + r")?(\d+)\.(png|jpe?g)$", re.I)   # ancien pack (id du club) / liens
IMAGE_STADE = re.compile(r"^" + PREFIXE_STADE + r"(\d+)\.(png|jpe?g)$", re.I)
TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stades_clubs.txt.gz")   # ids_fm (base FM27)
EXTS = (".png", ".jpg", ".jpeg")


def image(f):
    """photo du dossier FMVE Stadium, ancien ou nouveau nom"""
    return bool(IMAGE_STADE.match(f) or IMAGE.match(f))
BACKUP_DIR = os.environ.get("UIPICKER_BACKUPS") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backups")   # variable : banc d'essai
FICHIER = os.path.join(BACKUP_DIR, "dossier_graphics.txt")   # dossier graphics choisi dans l'app (sinon celui de base)


def ancien_nom(f):
    """photo de l'ancien pack, rangée par id de CLUB (STDM<id> ou <id> nu) : à convertir par id de stade"""
    return bool(IMAGE.match(f))


def documents():
    """dossier Documents de Windows (même déplacé, par ex. dans OneDrive) ; Linux : celui du préfixe Proton de FM"""
    if not chemin_jeu.WINDOWS:
        return os.path.join(chemin_jeu.profil(), "Documents")
    try:
        class GUID(ctypes.Structure):
            _fields_ = [("d1", ctypes.c_ulong), ("d2", ctypes.c_ushort), ("d3", ctypes.c_ushort),
                        ("d4", ctypes.c_ubyte * 8)]
        u = uuid.UUID("FDD39AD0-238F-46AF-ADB4-6C85480369C7")   # FOLDERID_Documents
        g = GUID(u.fields[0], u.fields[1], u.fields[2], (ctypes.c_ubyte * 8)(*u.bytes[8:]))
        p = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(g), 0, None, ctypes.byref(p)) == 0:
            chemin = p.value
            ctypes.windll.ole32.CoTaskMemFree(p)
            return chemin
    except (AttributeError, OSError):
        pass
    return os.path.join(os.path.expanduser("~"), "Documents")


def dossier_fm():
    """dossier FM 27 qui contient graphics : Documents\\Sports Interactive\\Football Manager 27 ; Mac : celui des
    données de FM (~/Library/Application Support/Sports Interactive/Football Manager 27)"""
    if chemin_jeu.MAC:
        return chemin_jeu.donnees_fm()
    return os.path.join(documents(), "Sports Interactive", "Football Manager 27")


def graphics_de_base():
    return os.path.join(dossier_fm(), "graphics")


def nettoyer(chemin):
    """guillemets, espaces, dossier des photos ou dossier FM 27 (qui contient graphics) -> dossier graphics.
    2026-11-12 (page Dossier du jeu) : aussi un dossier DANS graphics (pack), le dossier Documents ou « Sports
    Interactive » déplacés, ou un dossier FM 27 sans graphics (créé par enregistrer)"""
    c = (chemin or "").strip().strip('"').strip().rstrip("\\/")
    if os.path.basename(c).lower() in (DOSSIER.lower(), ANCIEN.lower()):
        c = os.path.dirname(c)
    morceaux = re.split(r"[\\/]", c)
    bas = [m.lower() for m in morceaux]
    if "graphics" in bas[:-1]:   # dossier d'un pack choisi au lieu de graphics : on remonte
        i = len(bas) - 1 - bas[::-1].index("graphics")
        c = os.sep.join(morceaux[:i + 1]) if i else c
    if os.path.basename(c).lower() != "graphics":
        for sous in (os.path.join("Sports Interactive", "Football Manager 27"), "Football Manager 27", ""):
            fm = os.path.join(c, sous) if sous else c
            if os.path.exists(os.path.join(fm, chemin_jeu.PROGRAMME)):
                continue   # dossier du JEU (Steam) : pas celui de Documents
            if os.path.isdir(os.path.join(fm, "graphics")) or (sous and os.path.isdir(fm)) or dossier_fm_de(fm):
                return os.path.join(fm, "graphics")
    return c


def dossier_fm_de(d):
    """d ressemble au dossier de FM 27 de Documents (sans graphics) : games, preferences, skins, tactics…"""
    try:
        noms = {n.lower() for n in os.listdir(d)}
    except OSError:
        return False
    return len(noms & {"games", "preferences", "skins", "tactics", "views", "editor data", "shortlists"}) >= 2


def choisi():
    """dossier graphics enregistré dans l'app ('' : aucun)"""
    try:
        with open(FICHIER, encoding="utf-8-sig") as f:
            return f.read().strip()
    except OSError:
        return ""


def graphics():
    """dossier graphics utilisé : celui choisi dans l'app s'il existe encore, sinon celui de base"""
    c = choisi()
    return c if c and os.path.isdir(c) else graphics_de_base()


def dossier():
    return os.path.join(graphics(), DOSSIER)


def dossier_liens():
    return os.path.join(graphics(), LIENS)


def nombre():
    return compte()[0]


_COMPTE = {}   # {dossier: (date de modif du dossier, résultat)}


def compte():
    """(photos, photos de l'ancien pack par id de club) de FMVE Stadium. Gardé tant que le dossier ne change pas
    (ajout / suppression / renommage changent sa date) : lire ~15 000 noms prenait ~4,5 s à chaque /api/etat (4 s)"""
    d = dossier()
    try:
        cle = os.stat(d).st_mtime_ns
    except OSError:
        return 0, 0
    if d in _COMPTE and _COMPTE[d][0] == cle:
        return _COMPTE[d][1]
    liste = [f for f in os.listdir(d) if image(f)]
    res = (len(liste), sum(1 for f in liste if ancien_nom(f)))
    _COMPTE[d] = (cle, res)
    return res


def enregistrer(chemin):
    """chemin vide : retour au dossier de base ; renvoie le dossier graphics enregistré, ou None s'il n'existe pas"""
    c = nettoyer(chemin)
    if c and not os.path.isdir(c) and os.path.basename(c).lower() == "graphics" and os.path.isdir(os.path.dirname(c)):
        os.makedirs(c, exist_ok=True)   # dossier FM 27 choisi, graphics pas encore créé par FM
    if c and not os.path.isdir(c):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not c or os.path.normcase(os.path.abspath(c)) == os.path.normcase(os.path.abspath(graphics_de_base())):
        if os.path.exists(FICHIER):
            os.remove(FICHIER)
        return graphics_de_base()
    with open(FICHIER, "w", encoding="utf-8") as f:
        f.write(c)
    return c


COMPETITIONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "competitions.txt.gz")   # ids_fm\exporter_app.py
_comps = None


def competitions():
    """ids des compétitions de FM 27 : jamais dans config.xml (leur logo serait remplacé par la photo)"""
    global _comps
    if _comps is None:
        import gzip
        try:
            with gzip.open(COMPETITIONS, "rt", encoding="utf-8") as f:
                _comps = {int(x) for x in f.read().split() if x.isdigit()}
        except OSError:
            _comps = set()
    return _comps


_table = None


def equipes_par_stade():
    """{id du stade : [ids des équipes qui y jouent]} (base FM27, ids_fm ; la 1re équipe = le club du stade)"""
    global _table
    if _table is None:
        import gzip
        _table = {}
        try:
            with gzip.open(TABLE, "rt", encoding="utf-8") as h:
                for ligne in h:
                    if ligne.startswith("#") or ":" not in ligne:
                        continue
                    s, equipes = ligne.strip().split(":", 1)
                    if s.isdigit():
                        _table[int(s)] = [int(e) for e in equipes.split(",") if e.isdigit()]
        except OSError:
            pass
    return _table


def stade_du_club():
    """{id d'équipe : (id du stade, rang de l'équipe dans ce stade)} (0 = le club du stade)"""
    return {e: (s, i) for s, equipes in equipes_par_stade().items() for i, e in enumerate(equipes)}


def noms(uid):
    """noms possibles de la photo d'un stade dans FMVE Stadium"""
    return [f"{PREFIXE_STADE}{uid}.{e}" for e in ("png", "jpg", "jpeg")]


def _deplacer_cote(src, sous, dossier_nom=DOSSIER):
    """photo sortie de FMVE Stadium (rien n'est supprimé) : « graphics (mis de côté)\\FMVE Stadium - <sous> »"""
    cote = os.path.join(os.path.dirname(graphics()), COTE, f"{dossier_nom} - {sous}")
    os.makedirs(cote, exist_ok=True)
    nom = os.path.basename(src)
    dst, i = os.path.join(cote, nom), 2
    while os.path.exists(dst):
        base, ext = os.path.splitext(nom)
        dst, i = os.path.join(cote, f"{base} ({i}){ext}"), i + 1
    os.replace(src, dst)


def _identique(a, b):
    """même fichier au bit près (taille puis contenu)"""
    import filecmp
    try:
        return os.path.getsize(a) == os.path.getsize(b) and filecmp.cmp(a, b, shallow=False)
    except OSError:
        return False


def ecarter(existant, nouveau, dossier_nom=DOSSIER):
    """image `existant` sur le point d'être remplacée par `nouveau` (même id) : supprimée seulement si copie au bit
    près, sinon mise de côté (2026-11-10, demande du joueur : jamais d'image perdue) ; aussi pour les trophées"""
    if not os.path.exists(existant):
        return
    if _identique(existant, nouveau):
        os.remove(existant)
    else:
        _deplacer_cote(existant, "remplacées", dossier_nom)


def migrer():
    """bouton « Convertir mes photos » (obligatoire si l'ancien pack est là, v1.73) : photos par id de CLUB
    (STDM<id> / <id>) renommées STADIUM<id du stade> d'après la table de FM27. Club du stade d'abord (rang 0) ; une
    2e photo du même stade : supprimée si copie au bit près, sinon mise de côté ; club absent de la table : mis de côté.
    Renvoie (photos converties, échecs, clubs liés)."""
    d = dossier()
    try:
        liste = [f for f in os.listdir(d) if ancien_nom(f)]
    except OSError:
        return 0, 0, ecrire()[1]
    table = stade_du_club()
    pris = {int(m.group(1)): f for f in os.listdir(d) for m in [IMAGE_STADE.match(f)] if m}   # stade -> photo gardée
    rang = lambda f: (table.get(int(IMAGE.match(f).group(1)), (0, 99))[1], not f.upper().startswith(PREFIXE))  # noqa: E731
    n = rates = 0
    for f in sorted(liste, key=rang):
        uid, ext = int(IMAGE.match(f).group(1)), IMAGE.match(f).group(2).lower()
        src = os.path.join(d, f)
        try:
            if uid not in table:
                _deplacer_cote(src, "sans stade")
            elif table[uid][0] in pris:
                if _identique(src, os.path.join(d, pris[table[uid][0]])):
                    os.remove(src)   # copie au bit près de la photo gardée (2026-11-10, accord du joueur)
                else:
                    _deplacer_cote(src, "doublons")   # vraie autre photo : jamais supprimée
            else:
                nom = f"{PREFIXE_STADE}{table[uid][0]}.{ext}"
                os.replace(src, os.path.join(d, nom))
                pris[table[uid][0]] = nom
                n += 1
        except OSError:
            rates += 1
    return n, rates, ecrire()[1]


def _entete(commentaire):
    return ("<record>\n\t<!-- resource manager options -->\n\n\t<!-- don't preload anything in this folder -->\n"
            '\t<boolean id="preload" value="false"/>\n\n\t<!-- turn off auto mapping -->\n'
            '\t<boolean id="amap" value="false"/>\n\n'
            f"\t<!-- {commentaire} -->\n")


def config(noms_par_id):
    """liens : {id du club : nom du fichier sans extension}"""
    lignes = "\n".join(f'\t\t<record from="{noms_par_id[i]}" to="{CIBLE.format(id=i)}"/>' for i in sorted(noms_par_id))
    return (_entete("photos des stades par club (FM27 Vanilla Enhanced Skin) : liens vers les photos de tes packs,\n"
                    "\t     dossier refait par le skin a chaque verification, ne pas modifier")
            + f'\t<list id="maps">\n{lignes}\n\t</list>\n</record>\n')


def config_stades(noms_par_id):
    """FMVE Stadium : {id du stade : nom du fichier sans extension}, format des packs d'internet"""
    lignes = "\n".join(f'\t\t<record from="{noms_par_id[i]}" to="{CIBLE_STADE.format(id=i)}"/>'
                       for i in sorted(noms_par_id))
    return (_entete("photos des stades (FMVE Stadium) : STADIUM<id du stade>.jpg ; fichier refait par le skin\n"
                    "\t     d'apres les images du dossier, ne pas modifier")
            + f'\t<list id="maps">\n{lignes}\n\t</list>\n</record>\n')


def _ecrire_si_change(f, texte):
    try:
        with open(f, encoding="utf-8") as h:
            if h.read() == texte:
                return False
    except OSError:
        pass
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w", encoding="utf-8", newline="\n") as h:   # UTF-8 sans BOM (lu par FM)
        h.write(texte)
    return True


RECORD = re.compile(r"<record\b[^>]*>", re.I)
FROM = re.compile(r'\bfrom\s*=\s*"([^"]*)"', re.I)
TO_STADE = re.compile(r'\bto\s*=\s*"[^"]*pictures/stadium/(\d+)/background"', re.I)
PROFONDEUR = 3   # config.xml lus jusqu'à graphics\<pack>\<sous-dossier>\<sous-dossier> (packs de visages énormes)


def _configs(g):
    """config.xml de graphics, PROFONDEUR niveaux au plus, sans nos dossiers de liens (stades, trophées)"""
    exclus = {os.path.normcase(os.path.join(g, n)) for n in (LIENS, "FMVE Trophies Links")}
    pile = [(g, 0)]
    while pile:
        d, n = pile.pop()
        try:
            entrees = list(os.scandir(d))
        except OSError:
            continue
        for e in entrees:
            if e.name.lower() == "config.xml" and n:
                yield e.path
            elif n < PROFONDEUR and e.is_dir() and os.path.normcase(e.path) not in exclus:
                pile.append((e.path, n + 1))


def photos_des_packs():
    """{id du stade : chemin de la photo}, d'après les config.xml de tous les packs de graphics ; packs d'autres
    sites d'abord, FMVE Stadium ensuite. Renvoie (photos, {nom du pack : nombre de photos})"""
    return images_des_packs(TO_STADE, "pictures/stadium/", dossier())


def images_des_packs(to, indice, notre):
    """{id : chemin de l'image} d'après les lignes `to` (regex, groupe 1 = id) des config.xml de graphics qui
    contiennent `indice` ; packs d'autres sites d'abord, notre dossier `notre` ensuite (stades, trophées).
    Renvoie (images, {nom du pack : nombre d'images retenues})"""
    g, d = graphics(), os.path.normcase(notre)
    sources = []
    for c in _configs(g):
        racine = os.path.dirname(c)
        try:
            with open(c, encoding="utf-8", errors="replace") as h:
                texte = h.read()
        except OSError:
            continue
        if indice not in texte:
            continue
        trouvees = {}
        for rec in RECORD.findall(texte):
            m, f = to.search(rec), FROM.search(rec)
            if not (m and f):
                continue
            base = os.path.join(racine, *f.group(1).replace("\\", "/").split("/"))
            photo = base if base.lower().endswith(EXTS) and os.path.isfile(base) else \
                next((base + e for e in EXTS if os.path.isfile(base + e)), None)
            if photo:
                trouvees.setdefault(int(m.group(1)), photo)
        if trouvees:
            rel = os.path.relpath(racine, g)
            sources.append((os.path.normcase(racine) == d, rel.split(os.sep)[0], trouvees))
    photos, packs = {}, {}
    for _, pack, trouvees in sorted(sources, key=lambda x: x[0]):   # False (autres sites) avant True (FMVE)
        n = 0
        for s, p in trouvees.items():
            if s not in photos:
                photos[s] = p
                n += 1
        packs[pack] = packs.get(pack, 0) + n
    return photos, packs


def _meme(a, b):
    try:
        if os.path.samefile(a, b):
            return True
        sa, sb = os.stat(a), os.stat(b)   # copie (lien impossible) : même taille et même date
        return sa.st_size == sb.st_size and int(sa.st_mtime) == int(sb.st_mtime)
    except OSError:
        return False


def config_seul():
    """v1.74 (idée du joueur, VALIDÉ en jeu 2026-11-10 : Arsenal + Arsenal féminin, même photo) : FMVE Stadium sans
    liens, son config.xml envoie la même photo à tous les clubs du stade (FM accepte un même from sur plusieurs
    lignes). Liens seulement pour les packs d'autres sites. False = ancien fonctionnement (tout en liens)."""
    return True


def config_clubs(noms_par_club):
    """config.xml de FMVE Stadium, {id du club : nom de la photo} -> comp/<club>/logo"""
    lignes = "\n".join(f'\t\t<record from="{noms_par_club[i]}" to="{CIBLE.format(id=i)}"/>' for i in sorted(noms_par_club))
    return (_entete("photos des stades (FMVE Stadium) : STADIUM<id du stade>.jpg, une ligne par club du stade ;\n"
                    "\t     fichier refait par le skin d'apres les images du dossier, ne pas modifier")
            + f'\t<list id="maps">\n{lignes}\n\t</list>\n</record>\n')


def lier(a_blanc=False):
    """« FMVE Stadium Links » refait : un lien physique (copie si impossible) par club dont le stade a une photo
    dans un pack, STDM<id du club>.<ext> + config.xml -> comp/<id du club>/logo ; ancien pack FMVE Stadium (par
    club, pas encore converti) lié tel quel pour les clubs restants. Seulement ce qui change est réécrit.
    Renvoie {"photos": stades, "clubs": n, "packs": {pack : n}, "anciens": n}.
    config_seul() (v1.74) : FMVE Stadium n'a plus de liens, son config.xml vise directement chaque club
    (« fmve_clubs » : {id du club : nom de la photo}, écrit par ecrire()) ; liens seulement pour les autres packs."""
    photos, packs = photos_des_packs()
    table, comps = equipes_par_stade(), competitions()
    d = dossier()
    seul = config_seul()
    fmve = {}
    if seul:   # photos de FMVE Stadium lues dans le dossier (son config.xml n'est plus au format des packs)
        nd = os.path.normcase(d) + os.sep
        photos = {s: p for s, p in photos.items() if not os.path.normcase(p).startswith(nd)}
        packs.pop(DOSSIER, None)
        for f in sorted(os.listdir(d) if os.path.isdir(d) else []):
            m = IMAGE_STADE.match(f)
            if m and int(m.group(1)) not in photos:
                fmve.setdefault(int(m.group(1)), os.path.splitext(f)[0])
    voulu = {}   # nom du lien -> photo
    par_club = {}
    for s, p in photos.items():
        for uid in table.get(s, []):
            if uid not in comps and uid not in par_club:
                par_club[uid] = p
    fmve_clubs = {}
    for s, nom in fmve.items():
        for uid in table.get(s, []):
            if uid not in comps and uid not in par_club:
                fmve_clubs.setdefault(uid, nom)
    if fmve:
        packs[DOSSIER] = len(fmve)
    anciens = 0
    for f in (sorted(os.listdir(d), key=lambda x: not x.upper().startswith(PREFIXE)) if os.path.isdir(d) else []):
        m = IMAGE.match(f)
        if m and int(m.group(1)) not in comps and int(m.group(1)) not in par_club and int(m.group(1)) not in fmve_clubs:
            par_club[int(m.group(1))] = os.path.join(d, f)
            anciens += 1
    for uid, p in par_club.items():
        voulu[f"{PREFIXE}{uid}{os.path.splitext(p)[1].lower()}"] = p
    r = {"photos": len(photos) + len(fmve), "clubs": len(par_club) + len(fmve_clubs), "packs": packs,
         "anciens": anciens, "fmve_clubs": fmve_clubs}
    if a_blanc:
        return r
    remplir_liens(dossier_liens(), voulu)
    _ecrire_si_change(os.path.join(dossier_liens(), "config.xml"),
                      config({uid: os.path.splitext(n)[0] for n in voulu for uid in [int(IMAGE.match(n).group(1))]}))
    return r


def _lien(chemin):
    """fichier qui est un lien physique (l'image existe encore ailleurs) : le supprimer ne perd rien"""
    try:
        return os.stat(chemin).st_nlink > 1   # os.stat (pas scandir : st_nlink à 0 sous Windows)
    except OSError:
        return False


def sauver_des_liens(L, notre, motif):
    """images posées à la main dans un dossier de liens (2026-11-10 : un joueur a décompressé FMVE Stadium dans
    « FMVE Stadium Links », la vérification a supprimé ses 15 053 photos) : avant de refaire les liens, chaque vraie
    image (pas un lien) au format du pack (`motif`) va dans notre dossier si elle n'y est pas déjà. Renvoie le nombre."""
    n = 0
    try:
        liste = [e for e in os.scandir(L) if e.is_file() and motif.match(e.name)]
    except OSError:
        return 0
    for e in liste:
        dst = os.path.join(notre, e.name)
        if os.path.exists(dst) or _lien(e.path):
            continue
        try:
            os.makedirs(notre, exist_ok=True)
            os.replace(e.path, dst)
            n += 1
        except OSError:
            pass
    return n


def remplir_liens(L, voulu, garder=(), dossier_nom=DOSSIER):
    """dossier de liens L = exactement {nom : image source} (+ config.xml et `garder`) : liens physiques (copie si
    impossible), seulement ce qui change ; aussi pour les trophées. Seuls les liens sont supprimés : un fichier qui
    n'existe nulle part ailleurs (posé à la main) est mis de côté, jamais perdu."""
    import shutil
    os.makedirs(L, exist_ok=True)
    garder = {x.lower() for x in garder} | {"config.xml"}
    for f in os.listdir(L):
        p = os.path.join(L, f)
        if f.lower() not in garder and os.path.isfile(p) and (f not in voulu or not _meme(voulu[f], p)):
            try:
                if _lien(p):
                    os.remove(p)
                else:
                    _deplacer_cote(p, "sortis des liens", dossier_nom)
            except OSError:
                pass
    for nom, p in voulu.items():
        dst = os.path.join(L, nom)
        if os.path.exists(dst):
            continue
        try:
            os.link(p, dst)
        except OSError:
            try:
                shutil.copy2(p, dst)
            except OSError:
                pass


DERNIER = {}   # dernier lier() : affiché par la page Stades


VERROU = threading.RLock()   # un seul ecrire() à la fois (app : auto toutes les 2 min + bouton « Vérifier »)


def ecrire(a_blanc=False):
    with VERROU:
        return _ecrire(a_blanc)


def _ecrire(a_blanc=False):
    """FMVE Stadium (créé si le dossier graphics choisi existe, ou si FM 27 a déjà son dossier Documents) : config.xml
    refait (format des packs d'internet), puis « FMVE Stadium Links » refait d'après tous les packs. Renvoie
    (dossier des liens, nombre de clubs liés) ou (None, 0)"""
    c = choisi()
    if not (c and os.path.isdir(c)) and not os.path.isdir(dossier_fm()):
        return None, 0
    d = dossier()
    ancien = os.path.join(os.path.dirname(d), ANCIEN)
    if not a_blanc and os.path.isdir(ancien) and not os.path.exists(d):
        try:   # photos posées avec l'ancien nom : le dossier prend son nouveau nom
            os.rename(ancien, d)
        except OSError:
            pass
    if not a_blanc:   # pack décompressé dans « FMVE Stadium Links » par erreur : photos remises dans FMVE Stadium
        sauver_des_liens(dossier_liens(), d, IMAGE_STADE)
    noms_par_id = {}
    for f in sorted(os.listdir(d) if os.path.isdir(d) else []):
        m = IMAGE_STADE.match(f)
        if m:
            noms_par_id.setdefault(int(m.group(1)), os.path.splitext(f)[0])
    if not a_blanc and (noms_par_id or os.path.isdir(d)) and not config_seul():
        _ecrire_si_change(os.path.join(d, "config.xml"), config_stades(noms_par_id))
    R = lier(a_blanc)
    if not a_blanc and config_seul() and os.path.isdir(d):   # la même photo pour chaque club du stade
        _ecrire_si_change(os.path.join(d, "config.xml"), config_clubs(R["fmve_clubs"]))
    DERNIER.clear()
    DERNIER.update(R)
    return dossier_liens(), R["clubs"]


def _images(d):
    try:
        return sum(1 for f in os.listdir(d) if image(f))
    except OSError:
        return 0


def _sous_dossiers(d):
    try:
        return [e.path for e in os.scandir(d) if e.is_dir()]
    except OSError:
        return []


def pack_complet(s, indice, notre):
    """dossier `s` (ou un dossier au-dessus, jusqu'à graphics ou notre dossier `notre` exclus) avec un config.xml qui
    contient `indice` : pack lu tel quel par lier(), jamais déplacé ni renommé"""
    g, notre = os.path.normcase(graphics()), os.path.normcase(notre)
    while os.path.normcase(s).startswith(g + os.sep) and os.path.normcase(s) != notre:
        try:
            with open(os.path.join(s, "config.xml"), encoding="utf-8", errors="replace") as h:
                if indice in h.read():
                    return True
        except OSError:
            pass
        s = os.path.dirname(s)
    return False


def egares():
    """dossiers de photos mal placés (cause n° 1 des stades qui ne chargent pas, 2026-10-30) : photos un niveau trop
    bas (« Extraire vers FMVE Stadium\\ » -> FMVE Stadium\\FMVE Stadium) ou dossier « FMVE… » au mauvais nom /
    au mauvais niveau dans graphics (2 niveaux max : jamais tout graphics, les packs de visages y sont énormes).
    Renvoie [(chemin, nombre de photos)], le plus fourni d'abord. Un dossier qui a son config.xml au format des packs
    d'internet (pictures/stadium/) n'est jamais égaré : lier() le lit tel quel (2026-11-10 : rien d'autre touché)."""
    g, d = graphics(), dossier()
    vus = set()
    for s in _sous_dossiers(d):   # dans FMVE Stadium (« a verifier » : photos mises de côté exprès)
        if not os.path.basename(s).lower().startswith("a verifier"):
            vus.add(s)
            vus.update(_sous_dossiers(s))
    for s in _sous_dossiers(g):   # ailleurs dans graphics : seulement un nom « FMVE… » (pas d'autre pack touché)
        if os.path.normcase(s) in (os.path.normcase(d), os.path.normcase(dossier_liens())) \
                or "troph" in os.path.basename(s).lower():   # nos liens, FMVE Trophies : pas des photos égarées
            continue
        if "fmve" in os.path.basename(s).lower():
            vus.add(s)
            vus.update(_sous_dossiers(s))
        else:
            vus.update(x for x in _sous_dossiers(s) if "fmve" in os.path.basename(x).lower())
    r = [(s, _images(s)) for s in vus if not pack_complet(s, "pictures/stadium/", d)]
    return sorted([x for x in r if x[1]], key=lambda x: -x[1])


def preparer():
    """FM 27 ne crée pas toujours graphics : on le crée si son dossier Documents existe ; True si graphics existe"""
    if not os.path.isdir(graphics()) and not (choisi() and os.path.isdir(choisi())) and os.path.isdir(dossier_fm()):
        os.makedirs(graphics_de_base(), exist_ok=True)
    return os.path.isdir(graphics())


def lignes_config():
    """nombre de clubs annoncés dans le config.xml des liens (None : pas de config.xml)"""
    try:
        with open(os.path.join(dossier_liens(), "config.xml"), encoding="utf-8") as h:
            return h.read().count("<record from=")
    except OSError:
        return None


CLE_FM = r"Software\Sports Interactive\Football Manager 27"   # réglages Unity de FM (noms suivis de _h<hash>)


def fm_registre():
    """ce que FM a noté à son dernier lancement (2026-10-30) : taille de grille (`grid.breakpoint` : la photo n'existe
    qu'en « Large », MidRes / LowRes abandonnés) et nombre d'images perso « comp » chargées (nos photos y sont).
    {} si FM n'a rien noté"""
    if chemin_jeu.MAC:
        return _registre_mac()
    if not chemin_jeu.WINDOWS:
        return _registre_wine()
    r = {}
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLE_FM)
    except (ImportError, OSError):
        return r
    i = 0
    while True:
        try:
            n, v, _ = winreg.EnumValue(k, i)
        except OSError:
            break
        i += 1
        if isinstance(v, bytes):
            v = v.rstrip(b"\0").decode("utf-8", "replace")
        if n.startswith("bt-grid.breakpoint_h"):
            r["grille"] = str(v).strip()
        elif n.startswith("bt-resources.custom_assets_breakdown_h"):
            m = re.search(r"^comp:\s*(\d+)", str(v), re.M)
            r["comp"] = int(m.group(1)) if m else 0
            r["detail"] = {a: int(b) for a, b in re.findall(r"^(\w+):\s*(\d+)", str(v), re.M)}   # tous les types
    try:   # dernière écriture de FM dans le registre (à sa fermeture, vu le 2026-10-30)
        r["date"] = winreg.QueryInfoKey(k)[2] / 1e7 - 11644473600
    except OSError:
        pass
    winreg.CloseKey(k)
    return r


def _lire_valeurs(r, valeurs):
    """mêmes repères que fm_registre, depuis {nom : texte} (noms avec _h<hash> sous Windows / Proton, sans sur Mac)"""
    for n, v in valeurs.items():
        n = re.sub(r"_h\d+$", "", n)
        if n == "bt-grid.breakpoint":
            r["grille"] = v.strip()
        elif n == "bt-resources.custom_assets_breakdown":
            m = re.search(r"^comp:\s*(\d+)", v, re.M)
            r["comp"] = int(m.group(1)) if m else 0
            r["detail"] = {a: int(b) for a, b in re.findall(r"^(\w+):\s*(\d+)", v, re.M)}


def _registre_wine():
    """Linux : registre de l'utilisateur du préfixe Proton (pfx/user.reg, texte) ; section
    [Software\\\\Sports Interactive\\\\Football Manager 27] <date unix>, valeurs "nom"=hex:… (octets UTF-8)"""
    r = {}
    pfx = os.path.dirname(os.path.dirname(os.path.dirname(chemin_jeu.profil())))   # pfx/drive_c/users/steamuser
    try:
        with open(os.path.join(pfx, "user.reg"), encoding="utf-8", errors="replace") as f:
            texte = f.read()
    except OSError:
        return r
    cle = re.escape(CLE_FM.replace("\\", "\\\\"))
    m = re.search(r"^\[" + cle + r"\]\s*(\d*)[^\n]*\n(.*?)(?=^\[|\Z)", texte, re.M | re.S | re.I)
    if not m:
        return r
    if m.group(1):
        r["date"] = int(m.group(1))
    corps = m.group(2).replace("\\\n", "")   # valeurs hex sur plusieurs lignes (« \ » en fin de ligne)
    valeurs = {}
    for n, v in re.findall(r'^"([^"]+)"=(.*)$', corps, re.M):
        v = v.strip()
        if v.startswith("hex"):
            octets = bytes(int(x, 16) for x in re.findall(r"[0-9a-fA-F]{2}", v.split(":", 1)[1]))
            valeurs[n] = octets.rstrip(b"\0").decode("utf-8", "replace")
        elif v.startswith('"'):
            valeurs[n] = v.strip('"')
    _lire_valeurs(r, valeurs)
    return r


PLIST_FM = os.path.join(os.path.expanduser("~"), "Library", "Preferences", "com.SportsInteractive.FootballManager27.plist")


def _registre_mac():
    """Mac : réglages Unity de FM dans ~/Library/Preferences/com.SportsInteractive.FootballManager27.plist (texte
    ou octets UTF-8) ; date = dernière écriture du fichier"""
    r = {}
    try:
        with open(PLIST_FM, "rb") as f:
            donnees = plistlib.load(f)
        r["date"] = os.path.getmtime(PLIST_FM)
    except (OSError, ValueError, plistlib.InvalidFileException):
        return r
    valeurs = {}
    for n, v in donnees.items():
        if isinstance(v, bytes):
            v = v.rstrip(b"\0").decode("utf-8", "replace")
        valeurs[str(n)] = str(v)
    _lire_valeurs(r, valeurs)
    return r


LOGS_FM = chemin_jeu.logs_fm()
# fichiers « en ligne seulement » (OneDrive à la demande…) : hors ligne / rappel à l'ouverture / à l'accès
NUAGE = 0x1000 | 0x40000 | 0x400000


def _date(chemin):
    try:
        return os.path.getmtime(chemin)
    except OSError:
        return None


def lancements():
    """encadre le dernier lancement de FM (v1.46, joueurs « tout vert mais pas de photo ») : il a démarré après la
    fin du précédent (Player-prev.log) et fini (ou écrit en dernier) à Player.log. La date de création de Player.log
    ne sert pas : Windows la garde quand Unity le recrée au même nom."""
    return {"avant": _date(os.path.join(LOGS_FM, "Player-prev.log")), "fin": _date(os.path.join(LOGS_FM, "Player.log"))}


def fichiers(entetes=False):
    """état des photos de FMVE Stadium : arrivée (date de création la plus récente : décompression / copie), vides,
    restées en ligne (OneDrive), lecture seule, n° en double (png + jpg) ; entetes=True : aussi les images dont le
    contenu ne correspond pas à l'extension (lit 4 octets par photo, jamais celles restées en ligne : seulement pour
    le diagnostic copié ; 3 s au plus, l'antivirus ralentit chaque ouverture : jusqu'à 13 s pour tout le pack)"""
    import time
    r = {"arrivee": None, "png": 0, "jpg": 0, "vides": [], "nuage": 0, "lecture_seule": 0, "doubles": 0, "faux": [],
         "lues": 0}
    fin = time.time() + 3
    try:
        liste = list(os.scandir(dossier()))
    except OSError:
        return r
    vus = set()
    r["en_trop"] = sorted(e.name + ("\\" if e.is_dir() else "") for e in liste   # tout sauf photos + config.xml
                          if not image(e.name) and e.name.lower() != "config.xml")
    for e in liste:
        m = IMAGE_STADE.match(e.name) or IMAGE.match(e.name)
        if not m:
            continue
        try:
            st = e.stat()
        except OSError:
            continue
        png = m.group(2).lower() == "png"
        r["png" if png else "jpg"] += 1
        r["doubles"] += m.group(1) in vus
        vus.add(m.group(1))
        ne = getattr(st, "st_birthtime", st.st_ctime)
        r["arrivee"] = max(r["arrivee"] or 0, ne)
        attr = getattr(st, "st_file_attributes", 0)
        r["lecture_seule"] += bool(attr & 1)
        if attr & NUAGE:
            r["nuage"] += 1
            continue
        if not st.st_size:
            r["vides"].append(e.name)
            continue
        if entetes and time.time() < fin:
            r["lues"] += 1
            try:
                with open(e.path, "rb") as h:
                    tete = h.read(4)
            except OSError:
                r["faux"].append(e.name + " (illisible / unreadable)")
                continue
            if not tete.startswith(b"\x89PNG" if png else b"\xff\xd8"):
                vrai = "png" if tete.startswith(b"\x89PNG") else "jpg" if tete.startswith(b"\xff\xd8") else "?"
                r["faux"].append(f"{e.name} (= {vrai})")
    c = _date(os.path.join(dossier_liens(), "config.xml"))   # liens refaits après coup : FM doit aussi les relire
    if r["arrivee"] and c:
        r["arrivee"] = max(r["arrivee"], c)
    return r


def relance(arrivee, fm_ouvert=False):
    """FM relancé depuis l'arrivée des photos ? 'non' (pas relancé), 'pendant' (installées pendant qu'il tournait),
    'oui' (lancé après : s'il ne les a pas chargées, c'est un vrai souci) ou None (on ne sait pas)"""
    L = lancements()
    if not arrivee or not L["fin"]:
        return None
    if L["avant"] and arrivee <= L["avant"]:
        return "oui"
    if fm_ouvert or arrivee <= L["fin"]:
        return "pendant" if L["avant"] else None
    return "non"


def config_lisible():
    """'' si le config.xml des liens se lit comme FM l'attend, sinon la raison"""
    f = os.path.join(dossier_liens(), "config.xml")
    try:
        with open(f, "rb") as h:
            brut = h.read()
    except OSError as e:
        return e.strerror or str(e)
    if brut.startswith(b"\xef\xbb\xbf"):
        return "BOM UTF-8"
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(brut)
    except Exception as e:   # noqa: BLE001 (toute erreur de lecture = config illisible)
        return f"XML : {e}"
    return ""


def autres_packs():
    """autres dossiers de graphics (packs de logos, visages…) : nom + config.xml à leur racine ; et config.xml posé
    directement dans graphics. Rien n'est parcouru en profondeur (les packs de visages sont énormes)."""
    g = graphics()
    r = {"racine_config": os.path.exists(os.path.join(g, "config.xml")), "dossiers": []}
    for s in sorted(_sous_dossiers(g), key=lambda x: os.path.basename(x).lower()):
        if os.path.normcase(s) not in (os.path.normcase(dossier()), os.path.normcase(dossier_liens())):
            r["dossiers"].append((os.path.basename(s), os.path.exists(os.path.join(s, "config.xml"))))
    return r


VISE = re.compile(rb'to="graphics/pictures/comp/(\d+)/logo"')


def _nos_ids():
    """ids des clubs liés (emplacements comp/<id>/logo que nos liens ET le config.xml de FMVE Stadium occupent), en
    octets"""
    L = dossier_liens()
    ids = {m.group(1).encode() for f in (os.listdir(L) if os.path.isdir(L) else []) for m in [IMAGE.match(f)] if m}
    try:
        with open(os.path.join(dossier(), "config.xml"), "rb") as h:
            ids |= set(VISE.findall(h.read()))
    except OSError:
        pass
    return ids
# v1.49 : logos « par défaut » des compétitions (comp/none…) repérés et retirés : PAS la cause (même joueur, rien de
# changé après « Corriger ») -> retiré en v1.50. Cause vue par le joueur : logos TCM de FM 26 (réglé en v1.53 par les
# noms STDM<id> ; conseils TCM retirés de la page).
COTE = "graphics (mis de côté)"   # dans le dossier FM 27, à côté de graphics : FM ne le lit pas


def scan_configs():
    """tous les config.xml de graphics (v1.47 : chez des joueurs, photos chargées seulement une fois les autres packs
    retirés -> un autre pack bloque). Lit les config.xml, jamais les images (~7 s pour 370 000 fichiers chez nous).
    Suspects : config.xml illisible (XML cassé, BOM), config.xml posé directement dans graphics, config qui vise
    les emplacements de nos photos (graphics/pictures/comp/<id du club>/logo : autre copie du pack, autre pack de
    stades). Renvoie {"configs": n, "suspects": [{pack, relatif, raison, n}]}, un suspect par pack (le 1er trouvé) ;
    « vise » : un seul suspect par pack qui réunit tous ses config.xml concernés (`fichiers`, `n` lignes)."""
    import xml.etree.ElementTree as ET
    g, d = graphics(), os.path.normcase(dossier())
    L = os.path.normcase(dossier_liens())
    nos_ids = _nos_ids()
    r = {"configs": 0, "suspects": []}
    vus = set()
    corrigibles = {}   # pack -> son suspect « vise » (des dizaines de config.xml dans un pack de logos)
    for racine, dirs, files in os.walk(g):
        nom = next((f for f in files if f.lower() == "config.xml"), None)
        if not nom:
            continue
        r["configs"] += 1
        rel = os.path.relpath(racine, g)
        pack = "" if rel == "." else rel.split(os.sep)[0]   # "" : config.xml directement dans graphics
        if os.path.normcase(racine) in (d, L) or pack in vus:   # les nôtres : vérifiés à part (config_lisible)
            continue
        raison, n = "", 0
        if os.path.normcase(racine).startswith(d + os.sep):   # 2e config DANS FMVE Stadium (vieille copie, « a verifier »…)
            vus.add(pack)   # 2026-10-30 : chez un joueur, seul un FMVE Stadium redécompressé propre a marché
            r["suspects"].append({"pack": pack, "relatif": "graphics\\" + rel + "\\" + nom, "raison": "dans_fmve", "n": 0})
            continue
        try:
            with open(os.path.join(racine, nom), "rb") as h:
                brut = h.read()
        except OSError as e:
            brut, raison = b"", "illisible : " + (e.strerror or str(e))
        if not raison and not pack:
            raison = "racine"
        relatif = "graphics" + ("\\" + rel if pack else "") + "\\" + nom
        if not raison:
            n = sum(1 for m in VISE.finditer(brut) if m.group(1) in nos_ids)
            if n:
                s = corrigibles.get(pack)
                if not s:
                    s = corrigibles[pack] = {"pack": pack, "relatif": relatif, "raison": "vise", "n": 0, "fichiers": []}
                    r["suspects"].append(s)
                s["n"] += n
                s["fichiers"].append(relatif)
                continue
        if not raison:
            try:
                ET.fromstring(brut)
            except Exception as e:   # noqa: BLE001 (toute erreur = FM ne le lit sans doute pas)
                raison = "xml : " + str(e)[:80]
        if raison:
            vus.add(pack)
            r["suspects"].append({"pack": pack, "relatif": relatif, "raison": raison, "n": n})
    return r


def nettoyer_fmve():
    """FMVE Stadium : photos d'un sous-dossier (double décompression) remontées, config.xml refait. 2026-11-10
    (demande du joueur) : plus rien d'autre n'est sorti du dossier, et aucun autre pack n'est déplacé ni réécrit
    (mettre_de_cote / corriger_config retirés) : lier() lit chaque pack tel quel. Renvoie le nombre de photos remontées."""
    d = dossier()
    n = 0
    for c, _ in egares():
        if os.path.normcase(c).startswith(os.path.normcase(d) + os.sep):
            n += reparer(c)
    ecrire()
    return n

def reconfigurer():
    """bouton « Reconfigurer FMVE Stadium » (v1.48, idée du joueur) : FMVE Stadium seul remis au propre + config.xml
    refait ; les autres packs sont seulement LUS (scan, affiché pour info, jamais modifiés). Renvoie
    {"sortis": n, "photos": n, "scan": scan_configs()}"""
    sortis = nettoyer_fmve()
    _, n = ecrire()
    return {"sortis": sortis, "photos": n, "scan": scan_configs()}


def autres_dossiers_fm():
    """autres dossiers « Football Manager 27 » possibles (Documents dans OneDrive, ancien Documents…) : FM en lit
    peut-être un autre que celui de l'app. Renvoie [(chemin, a FMVE Stadium, dernière modif de son contenu)]"""
    bases = {documents(), os.path.join(os.path.expanduser("~"), "Documents")}
    for v in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        if os.environ.get(v):
            for n in ("Documents", "Documenti", "Dokumente", "Documentos", "Belgeler", "Dokumenty"):
                bases.add(os.path.join(os.environ[v], n))
    r = []
    for b in sorted(bases):
        p = os.path.join(b, "Sports Interactive", "Football Manager 27")
        if os.path.isdir(p) and os.path.normcase(os.path.abspath(p)) != os.path.normcase(os.path.abspath(dossier_fm())):
            dates = [_date(x) for x in _sous_dossiers(p)] or [_date(p)]
            r.append((p, os.path.isdir(os.path.join(p, "graphics", DOSSIER)), max(x or 0 for x in dates)))
    return r


def diagnostic(fm_ouvert=False):
    """état de l'installation des photos, pour la page Stades de l'app (appelé à l'ouverture de la page et par
    « Vérifier », jamais à chaque /api/etat : parcourt les dossiers)"""
    g = graphics()
    d = dossier()
    if not DERNIER and os.path.isdir(g):   # pas encore de lier() dans cette app : packs relus (sans rien écrire)
        DERNIER.update(lier(a_blanc=True))
    L = dossier_liens()
    liens = sum(1 for f in (os.listdir(L) if os.path.isdir(L) else []) if IMAGE.match(f))
    photos, anciens = compte()
    r = {"graphics": g, "graphics_ok": os.path.isdir(g), "dossier": d, "photos": DERNIER.get("photos", 0),
         "fmve": photos, "clubs": DERNIER.get("clubs", 0),
         "packs": sorted(DERNIER.get("packs", {}).items(), key=lambda x: -x[1]),
         "config": lignes_config(), "config_attendu": liens, "egares": [], "rar": [],
         "skin": os.path.exists(os.path.join(BACKUP_DIR, "club_page_bas.actif")), "fm_lu": fm_registre(),
         "anciens": anciens}
    r["photos"] += anciens   # ancien pack pas encore converti : ses photos comptent aussi (liées par club)
    if not r["graphics_ok"]:
        return r
    F = fichiers()
    r["fichiers"] = {"arrivee": F["arrivee"], "vides": len(F["vides"]), "nuage": F["nuage"], "en_trop": F.get("en_trop", [])}
    r["fm_lu"]["relance"] = relance(F["arrivee"], fm_ouvert)
    r["config_erreur"] = config_lisible() if r["config"] else ""
    r["egares"] = [{"chemin": c, "photos": n, "relatif": os.path.relpath(c, g)} for c, n in egares()]
    for base in (g, dossier()):   # pack téléchargé et posé là, mais pas décompressé
        try:
            r["rar"] += [os.path.join(base, f) for f in os.listdir(base)
                         if f.lower().endswith((".rar", ".zip", ".7z")) and "fmve" in f.lower()]
        except OSError:
            pass
    return r


def reparer(source):
    """photos de `source` (un dossier rendu par egares()) remontées dans FMVE Stadium, dossier vide supprimé,
    config.xml refait ; renvoie le nombre de photos déplacées"""
    d = dossier()
    if os.path.normcase(os.path.abspath(source)) not in {os.path.normcase(os.path.abspath(c)) for c, _ in egares()}:
        raise ValueError(source)
    os.makedirs(d, exist_ok=True)
    n = 0
    for f in os.listdir(source):
        m = IMAGE_STADE.match(f) or IMAGE.match(f)
        if not m:
            continue
        nom = f if IMAGE_STADE.match(f) else f"{PREFIXE}{m.group(1)}.{m.group(2)}"   # ancien : converti ensuite
        autres = noms(m.group(1)) if IMAGE_STADE.match(f) else \
            [f"{p}{m.group(1)}.{e}" for p in (PREFIXE, "") for e in ("png", "jpg", "jpeg")]
        for vieux in autres:   # une seule image par stade (ou par club) : l'ancienne mise de côté si différente
            ecarter(os.path.join(d, vieux), os.path.join(source, f))
        os.replace(os.path.join(source, f), os.path.join(d, nom))
        n += 1
    vieux_config = os.path.join(source, "config.xml")   # celui d'une ancienne copie : ne doit plus rien annoncer
    if os.path.exists(vieux_config):
        _deplacer_cote(vieux_config, "configs")
    p = source
    while os.path.normcase(p) != os.path.normcase(d) and os.path.normcase(p) != os.path.normcase(graphics()):
        try:
            os.rmdir(p)   # seulement s'il est vide
        except OSError:
            break
        p = os.path.dirname(p)
    ecrire()
    return n


if __name__ == "__main__":
    print(ecrire(a_blanc=True))
