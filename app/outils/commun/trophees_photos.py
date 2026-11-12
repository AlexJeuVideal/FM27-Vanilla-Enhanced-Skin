"""Images des trophées (salle des trophées, 2026-11-09) : dossier graphics de FM, comme les photos des stades.

Le joueur pose TROPHY<id de la compétition>.png dans
  Documents\\Sports Interactive\\Football Manager 27\\graphics\\FMVE Trophies
(même dossier graphics que les stades : stades_photos.graphics()). Ici : le config.xml du dossier est refait d'après
les images présentes. FM ne connaît pas de type « trophée » : chaque image est rangée à un emplacement libre,
graphics/pictures/continent/<id de la compétition>/logo, que le skin lit avec le chargeur d'images en type Continent
(essai validé en jeu le 2026-11-09). Rien d'existant n'est remplacé :
- ids 1-7 jamais dans config.xml (ceux des continents : leur logo serait remplacé) ;
- ids qui ne sont pas des compétitions de FM 27 (competitions.txt.gz) : ignorés.
Pack de base : celui de FM 24 (<id>.png, mêmes ids, 2 175 / 2 180 dans FM 27) -> installer() le copie en TROPHY<id>.
Crédit : ces images viennent à l'origine de FM Scout (à citer dans les crédits de l'app et des NOTES).
v1.73 (2026-11-10, comme les stades) : FMVE Trophies au format des packs d'internet (sortitoutsi Trophies Megapack :
`to="graphics/pictures/comp/<id>/trophy"`, même id de compétition). lier() lit les config.xml de TOUS les packs
(autres sites d'abord, FMVE Trophies ensuite) et range un lien physique par compétition dans « FMVE Trophies Links »
-> continent/<id>/logo (+ image VIDE pour les autres). Ancien FMVE Trophies (config.xml vers continent/) : gardé tel
quel jusqu'à migrer() (alerte obligatoire de l'app, avec celle des stades).

Bibliothèque standard seulement.
Usage : trophees_photos.py                          -> à blanc (dossier, nombre d'images dans config.xml)
        trophees_photos.py installer "<pack>" [--dry-run]
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stades_photos  # noqa: E402  (dossier graphics, ids des compétitions)

DOSSIER = "FMVE Trophies"
LIENS = "FMVE Trophies Links"   # v1.73 : refait par lier(), jamais à la main (exclu de stades_photos._configs)
PREFIXE = "TROPHY"
CIBLE = "graphics/pictures/continent/{id}/logo"   # liens : lu par la salle des trophées ET le palmarès « Honneurs » de FM
CIBLE_PACK = "graphics/pictures/comp/{id}/trophy"   # format des packs d'internet
TO_PACK = re.compile(r'\bto\s*=\s*"[^"]*pictures/comp/(\d+)/trophy"', re.I)
CREDIT = "images des trophees : pack de FM Scout (fmscout.com) a l'origine"   # crédits (app plus tard)
# ids des continents : FM garde SES logos dans continent/<id>/logo (essai du 2026-11-09 : nos TROPHY1-7 chargés par FM,
# 2 182 images « continent », mais la Jupiler Pro League affiche toujours la CAF) -> jamais visés ; la carte de la
# salle des trophées cache son image pour ces compétitions (salle_trophees.ID_MAX_CONTINENT)
CONTINENTS = range(1, 8)   # (essai 2026-11-10 : 1-7 liés -> encore CAF / AFC ; les images TROPHY1-7 restent, pas liées)
IMAGE = re.compile(r"^" + PREFIXE + r"(\d+)\.(png|jpe?g)$", re.I)
PACK = re.compile(r"^(?:" + PREFIXE + r")?(\d+)\.(png|jpe?g)$", re.I)   # pack FM 24 (<id>.png) ou déjà renommé


def dossier():
    return os.path.join(stades_photos.graphics(), DOSSIER)


def dossier_liens():
    return os.path.join(stades_photos.graphics(), LIENS)


MARQUE = "format v1.74"   # config.xml de FMVE Trophies sans liens (continent/<id>/logo direct) : pas l'ancien v1.72


def converti():
    """FMVE Trophies plus à l'ancien format v1.72 (continent + TROPHY_VIDE dans le dossier) : format des packs
    d'internet (v1.73), format v1.74 (MARQUE), ou pas de config.xml"""
    try:
        with open(os.path.join(dossier(), "config.xml"), encoding="utf-8", errors="replace") as h:
            t = h.read()
        return "pictures/continent/" not in t or MARQUE in t
    except OSError:
        return True


def anciens():
    """images de FMVE Trophies encore à l'ancien format (0 si converti) : alerte obligatoire de l'app"""
    return 0 if converti() else _images(dossier())


def utilisable(i):
    return i not in CONTINENTS and i in stades_photos.competitions()


# compétitions de FM 27 sans image dans le pack : sans rien à continent/<id>/logo, FM montre le LOGO de la compétition
# dans la carte (vu en jeu le 2026-11-09) -> une image transparente (VIDE.png, écrite par le skin) y est posée : place
# vide. Une vraie image TROPHY<id> ajoutée plus tard passe devant (config.xml refait).
VIDE = PREFIXE + "_VIDE"


def _png_transparent():
    """PNG 1x1 transparent (bibliothèque standard)"""
    import struct
    import zlib

    def bloc(typ, data):
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
            + bloc(b"IDAT", zlib.compress(b"\x00\x00\x00\x00\x00")) + bloc(b"IEND", b""))


def config(noms_par_id, cible=CIBLE, quoi="liens vers les images de tes packs, refaits par le skin"):
    """{id de la compétition : nom du fichier sans extension}"""
    lignes = "\n".join(f'\t\t<record from="{noms_par_id[i]}" to="{cible.format(id=i)}"/>' for i in sorted(noms_par_id))
    return ("<record>\n\t<!-- resource manager options -->\n\n\t<!-- don't preload anything in this folder -->\n"
            '\t<boolean id="preload" value="false"/>\n\n\t<!-- turn off auto mapping -->\n'
            '\t<boolean id="amap" value="false"/>\n\n'
            f"\t<!-- trophees (FM27 Vanilla Enhanced Skin) : {quoi} ;\n"
            "\t     fichier refait par le skin d'apres les images du dossier, ne pas modifier ;\n"
            f"\t     {CREDIT} -->\n"
            f'\t<list id="maps">\n{lignes}\n\t</list>\n</record>\n')


def config_fmve(noms_par_id):
    """config.xml de FMVE Trophies (v1.74, sans liens) : {id : nom} -> continent/<id>/logo ; MARQUE = pas l'ancien"""
    return config(noms_par_id, quoi=f"TROPHY<id>.png -> continent/<id>/logo, {MARQUE}, sans liens")


def _noms(d):
    """{id : nom sans extension} ; TROPHY<id> d'abord, puis <id>.png du pack FM 24 tel quel (2026-11-10 : plus
    renommé, le config.xml le vise sous son nom)"""
    noms_par_id = {}
    liste = sorted(os.listdir(d) if os.path.isdir(d) else [])
    for f in [x for x in liste if IMAGE.match(x)] + [x for x in liste if BRUT.match(x)]:
        m = IMAGE.match(f) or BRUT.match(f)
        noms_par_id.setdefault(int(m.group(1)), os.path.splitext(f)[0])
    return noms_par_id


def _ancien_ecrire(a_blanc):
    """avant la conversion (v1.72) : config.xml de FMVE Trophies vers continent/<id>/logo, comme avant"""
    d = dossier()
    noms_par_id = {i: n for i, n in _noms(d).items() if utilisable(i)}
    n = len(noms_par_id)
    vides = [i for i in stades_photos.competitions() if utilisable(i) and i not in noms_par_id]
    if vides:
        noms_par_id.update({i: VIDE for i in vides})
        f = os.path.join(d, VIDE + ".png")
        if not a_blanc and not os.path.isfile(f):
            with open(f, "wb") as h:
                h.write(_png_transparent())
    if not a_blanc:
        stades_photos._ecrire_si_change(os.path.join(d, "config.xml"),
                                        config(noms_par_id, quoi="TROPHY<id>.png -> emplacement libre"))
    return d, n


DERNIER = {}   # dernier lier() : affiché par la page des trophées


def lier(a_blanc=False):
    """« FMVE Trophies Links » refait : un lien physique par compétition de FM 27 (sauf 1-7) dont un pack d'un AUTRE
    site a l'image, TROPHY<id>.<ext> -> continent/<id>/logo ; les compétitions sans image nulle part -> image
    transparente (VIDE). v1.74 (comme les stades, 2026-11-10) : FMVE Trophies n'a plus de liens, son config.xml vise
    continent/<id>/logo lui-même (« fmve » : {id : nom}, écrit par _ecrire()).
    Renvoie {"images": n, "competitions": n liées, "packs": {pack : n}, "fmve": {id : nom}}"""
    d = dossier()
    images, packs = stades_photos.images_des_packs(TO_PACK, "/trophy", d)
    nd = os.path.normcase(d) + os.sep
    images = {i: p for i, p in images.items() if not os.path.normcase(p).startswith(nd)}   # autres sites seulement
    packs.pop(DOSSIER, None)
    tous = _noms(d)
    fmve = {i: n for i, n in tous.items() if utilisable(i) and i not in images}
    if tous:
        packs[DOSSIER] = sum(1 for i in tous if i not in images)
    voulu = {f"{PREFIXE}{i}{os.path.splitext(p)[1].lower()}": p for i, p in images.items() if utilisable(i)}
    r = {"images": len(set(images) | set(tous)), "competitions": len(voulu) + len(fmve), "packs": packs, "fmve": fmve}
    if a_blanc:
        return r
    L = dossier_liens()
    stades_photos.remplir_liens(L, voulu, garder=[VIDE + ".png"], dossier_nom=DOSSIER)
    if not os.path.isfile(os.path.join(L, VIDE + ".png")):
        with open(os.path.join(L, VIDE + ".png"), "wb") as h:
            h.write(_png_transparent())
    noms_par_id = {int(IMAGE.match(n).group(1)): os.path.splitext(n)[0] for n in voulu}
    noms_par_id.update({i: VIDE for i in stades_photos.competitions()
                        if utilisable(i) and i not in noms_par_id and i not in fmve})
    stades_photos._ecrire_si_change(os.path.join(L, "config.xml"), config(noms_par_id))
    return r


def ecrire(a_blanc=False, forcer=False):
    with stades_photos.VERROU:   # même verrou que les stades (même dossier graphics)
        return _ecrire(a_blanc, forcer)


def _ecrire(a_blanc=False, forcer=False):
    """FMVE Trophies : config.xml au format des packs d'internet (comp/<id>/trophy), puis « FMVE Trophies Links »
    refait d'après tous les packs. Ancien FMVE Trophies pas encore converti (et pas forcer) : ancien config.xml gardé
    à jour, rien d'autre. Renvoie (dossier, images liées) ou (None, 0)"""
    d = dossier()
    if not forcer and not converti():
        return _ancien_ecrire(a_blanc)
    if not os.path.isdir(stades_photos.graphics()):
        return None, 0
    if not a_blanc:   # pack décompressé dans « FMVE Trophies Links » par erreur : images remises dans FMVE Trophies
        stades_photos.sauver_des_liens(dossier_liens(), d, re.compile(r"^(?:" + PREFIXE + r")?\d+\.(png|jpe?g)$", re.I))
    if not a_blanc and os.path.isdir(d):
        vide = os.path.join(d, VIDE + ".png")   # l'image transparente vit maintenant dans les liens
        if os.path.isfile(vide):
            try:
                os.remove(vide)
            except OSError:
                pass
    R = lier(a_blanc)
    if not a_blanc and os.path.isdir(d):   # v1.74 : FMVE Trophies vise continent/<id>/logo lui-même (pas de liens)
        stades_photos._ecrire_si_change(os.path.join(d, "config.xml"), config_fmve(R["fmve"]))
    DERNIER.clear()
    DERNIER.update(R)
    return dossier_liens(), R["competitions"]


def migrer():
    """bouton « Convertir mes trophées » (obligatoire, avec celui des stades) : FMVE Trophies passe au format des
    packs d'internet (seul son config.xml change, les images gardent leur nom). Renvoie (images, 0, liées)"""
    n = _images(dossier())
    return n, 0, ecrire(forcer=True)[1]


def installer(source, a_blanc=False):
    """images <id>.png d'un pack (FM 24) copiées en TROPHY<id>.<ext> dans FMVE Trophies, puis config.xml refait.
    Renvoie un résumé (dict) : copiées, hors FM 27 (noms), continents (noms), autres fichiers (noms)."""
    source = (source or "").strip().strip('"')
    if not os.path.isdir(source):
        raise FileNotFoundError(source)
    d = dossier()
    if os.path.normcase(os.path.abspath(source)) == os.path.normcase(os.path.abspath(d)):
        raise ValueError("source = dossier des trophées")
    r = {"copiees": 0, "hors_fm27": [], "continents": [], "autres": []}
    if not a_blanc:
        os.makedirs(d, exist_ok=True)
    for f in sorted(os.listdir(source)):
        m = PACK.match(f)
        if not m:
            if f.lower() not in ("config.xml", "desktop.ini", "thumbs.db"):
                r["autres"].append(f)
            continue
        i = int(m.group(1))
        if i in CONTINENTS:
            r["continents"].append(f)
            continue
        if i not in stades_photos.competitions():
            r["hors_fm27"].append(f)
            continue
        if not a_blanc:
            for e in ("png", "jpg", "jpeg"):   # une seule image par compétition (l'ancienne mise de côté si différente)
                stades_photos.ecarter(os.path.join(d, f"{PREFIXE}{i}.{e}"), os.path.join(source, f), DOSSIER)
            shutil.copyfile(os.path.join(source, f), os.path.join(d, f"{PREFIXE}{i}.{m.group(2).lower()}"))
        r["copiees"] += 1
    r["dossier"], r["config"] = (d, r["copiees"]) if a_blanc else ecrire()
    return r


# ---------- app : page « Images des trophées » (comme la page des stades, en plus simple) ----------
BRUT = re.compile(r"^(\d+)\.(png|jpe?g)$", re.I)   # pack FM 24 décompressé tel quel (<id>.png) : gardé sous ce nom
MARKER_SKIN = os.path.join(stades_photos.BACKUP_DIR, "salle_trophees.actif")
CONTINENTS_FM = 7   # logos de continents de FM comptés avec nos images (registre, « continent: »)


def preparer():
    return stades_photos.preparer()


def _images(d, brut=True):
    try:
        return sum(1 for f in os.listdir(d) if IMAGE.match(f) or (brut and BRUT.match(f)))
    except OSError:
        return 0


def egares():
    """dossiers d'images de trophées mal placés : sous-dossiers de FMVE Trophies seulement (« Extraire vers… »), sauf
    un pack avec son config.xml au format des packs d'internet (lu tel quel par lier()). 2026-11-10 (demande du
    joueur) : les autres dossiers de graphics (« trophies » d'un autre site…) ne sont jamais touchés. [(chemin, images)]"""
    d = dossier()
    vus = set()
    for s in stades_photos._sous_dossiers(d):
        vus.add(s)
        vus.update(stades_photos._sous_dossiers(s))
    r = [(s, _images(s)) for s in vus if not stades_photos.pack_complet(s, "/trophy", d)]
    return sorted([x for x in r if x[1]], key=lambda x: -x[1])


def reparer(source):
    """images de `source` (un dossier rendu par egares()) remontées dans FMVE Trophies sous leur nom (TROPHY<id> ou
    <id> du pack FM 24) ; image du même id déjà là : mise de côté si différente ; config.xml de `source` mis de côté,
    dossiers vides supprimés, config.xml refait ; renvoie le nombre d'images déplacées"""
    d = dossier()
    if os.path.normcase(os.path.abspath(source)) not in {os.path.normcase(os.path.abspath(c)) for c, _ in egares()}:
        raise ValueError(source)
    os.makedirs(d, exist_ok=True)
    n = 0
    for f in os.listdir(source):
        m = IMAGE.match(f) or BRUT.match(f)
        if not m:
            continue
        for p in (PREFIXE, ""):
            for e in ("png", "jpg", "jpeg"):
                stades_photos.ecarter(os.path.join(d, f"{p}{m.group(1)}.{e}"), os.path.join(source, f), DOSSIER)
        os.replace(os.path.join(source, f), os.path.join(d, f))
        n += 1
    if os.path.exists(os.path.join(source, "config.xml")):
        stades_photos._deplacer_cote(os.path.join(source, "config.xml"), "configs", DOSSIER)
    if os.path.exists(os.path.join(source, "desktop.ini")):
        os.remove(os.path.join(source, "desktop.ini"))
    p = source
    while os.path.normcase(p) not in (os.path.normcase(d), os.path.normcase(stades_photos.graphics())):
        try:
            os.rmdir(p)   # seulement s'il est vide
        except OSError:
            break
        p = os.path.dirname(p)
    ecrire()
    return n

def config_lisible():
    """'' si le config.xml lu par FM (liens, ou FMVE Trophies avant conversion) se lit comme FM l'attend"""
    try:
        with open(os.path.join(dossier_liens() if converti() else dossier(), "config.xml"), "rb") as h:
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


def fichiers():
    """images de FMVE Trophies : arrivée (création la plus récente), vides, restées en ligne (OneDrive), en trop"""
    r = {"arrivee": None, "vides": 0, "nuage": 0, "en_trop": []}
    try:
        liste = list(os.scandir(dossier()))
    except OSError:
        return r
    for e in liste:
        if not IMAGE.match(e.name):
            if e.name.lower() not in ("config.xml", "desktop.ini", VIDE.lower() + ".png") and not BRUT.match(e.name):
                r["en_trop"].append(e.name + ("\\" if e.is_dir() else ""))
            continue
        try:
            st = e.stat()
        except OSError:
            continue
        r["arrivee"] = max(r["arrivee"] or 0, getattr(st, "st_birthtime", st.st_ctime))
        if getattr(st, "st_file_attributes", 0) & stades_photos.NUAGE:
            r["nuage"] += 1
        elif not st.st_size:
            r["vides"] += 1
    c = stades_photos._date(os.path.join(dossier_liens() if converti() else dossier(), "config.xml"))
    if r["arrivee"] and c:
        r["arrivee"] = max(r["arrivee"], c)
    r["en_trop"].sort()
    return r


def diagnostic(fm_ouvert=False):
    """état de l'installation des images, pour la page « Images des trophées » de l'app"""
    g, d = stades_photos.graphics(), dossier()
    ids = set(_noms(d))
    conv = converti()
    if conv:   # v1.73 : ce que FM lit = les liens (images de tous les packs)
        if not DERNIER and os.path.isdir(g):
            DERNIER.update(lier(a_blanc=True))
        L = dossier_liens()
        attendu = sum(1 for f in (os.listdir(L) if os.path.isdir(L) else []) if IMAGE.match(f))
        images = DERNIER.get("images", len(ids))
    else:
        L, attendu, images = d, sum(1 for i in ids if utilisable(i)), len(ids)
    try:
        with open(os.path.join(L, "config.xml"), encoding="utf-8") as h:
            brut = h.read()
        vides = brut.count(f'<record from="{VIDE}"')
        lignes = brut.count("<record from=") - vides
    except OSError:
        lignes, vides = None, 0
    fm = stades_photos.fm_registre()
    r = {"graphics": g, "graphics_ok": os.path.isdir(g), "dossier": d, "images": images, "config": lignes,
         "config_attendu": attendu, "hors_fm": max(0, len(ids) - sum(1 for i in ids if utilisable(i))),
         "skin": os.path.exists(MARKER_SKIN), "anciens": 0 if conv else len(ids),
         "packs": sorted(DERNIER.get("packs", {}).items(), key=lambda x: -x[1]) if conv else [],
         "fm_lu": {k: fm[k] for k in ("grille", "date") if k in fm}, "egares": [], "rar": []}
    if "detail" in fm:   # images « continent » chargées par FM à son dernier lancement (les nôtres + ses 7 logos)
        # (+ les pays de la carte du monde, recrutement\carte_monde : aussi des images « continent »)
        try:
            with open(os.path.join(g, "UIPicker Carte du monde", "config.xml"), encoding="utf-8") as h:
                carte = h.read().count("<record from=")
        except OSError:
            carte = 0
        r["fm_lu"]["charge"] = max(0, fm["detail"].get("continent", 0) - CONTINENTS_FM - vides - carte)
    if not r["graphics_ok"]:
        return r
    F = fichiers()
    r["fichiers"] = F
    r["fm_lu"]["relance"] = stades_photos.relance(F["arrivee"], fm_ouvert)
    r["config_erreur"] = config_lisible() if lignes else ""
    r["egares"] = [{"chemin": c, "images": n, "relatif": os.path.relpath(c, g)} for c, n in egares()]
    for base in (g, d):   # pack téléchargé et posé là, mais pas décompressé
        try:
            r["rar"] += [os.path.join(base, f) for f in os.listdir(base)
                         if f.lower().endswith((".rar", ".zip", ".7z")) and "troph" in f.lower()]
        except OSError:
            pass
    return r


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if args[:1] == ["installer"] and len(args) == 2:
        res = installer(args[1], a_blanc="--dry-run" in sys.argv)
        print(f"{res['dossier']} : {res['copiees']} copiées, config.xml {res['config']}"
              + (" [à blanc : rien écrit]" if "--dry-run" in sys.argv else ""))
        for k in ("hors_fm27", "continents", "autres"):
            print(f"  {k} : {', '.join(res[k]) or '-'}")
    else:
        print(ecrire(a_blanc=True))
