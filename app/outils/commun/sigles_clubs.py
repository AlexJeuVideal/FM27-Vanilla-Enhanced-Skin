"""Sigles à 3 lettres des clubs (tableau de score) dans toutes les langues : fonction du skin, PAS FM Scout.

Dans la base de FM27 (lang_db.dat), seule la table de clubs anglaise a les sigles à 3 lettres (« PSG », « OM ») ; les
autres langues (français, allemand, espagnol…) n'en ont aucun, donc le tableau de score montre le nom à 6 lettres.
On relit les sigles anglais dans la base du jeu du joueur (rien de livré, toujours à jour après une MAJ de FM) et on
pose un .lnc à nous (CLUB_3LETTER_NAME_CHANGE, langue "" = toutes, même format que FM Scout) dans lnc\\all de chaque
base (2700 = nouvelles parties, 2600, 2400… = parties importées).

Avec ou sans le fix de FM Scout (noms_reels.py) : leurs fichiers ne sont jamais touchés. Pour les clubs dont leur .lnc
donne déjà le sigle, on écrit LEUR valeur (l'ordre de lecture des .lnc ne compte plus) ; noms_reels appelle
rafraichir() après avoir posé / retiré leur fix.

lang_db.dat : en-tête puis trames zstd (Python 3.14 : compression.zstd), une table par trame, 16 tables par langue.
Trame = "\\x03\\x01tad." + 2 octets + nombre u32 ; fiche de club = id u32, long, octet, court, octet, 6 lettres,
3 lettres, 3 lettres alt, octet, surnom, 4 octets, nom en plus (chaîne = longueur u32 + UTF-8).

Usage : sigles_clubs.py                       -> diagnostic (lecture seule)
        sigles_clubs.py poser [--dry-run]
        sigles_clubs.py retirer [--dry-run]
"""
import json
import os
import re
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemin_jeu  # noqa: E402
import noms_reels  # noqa: E402  (bases, racine_db, nom des .lnc de FM Scout)

NOM_LNC = "UIPicker sigles 3 lettres.lnc"
LNC_SCOUT = "FM27 Club Names by FMScout.lnc"
CACHE = os.path.join(chemin_jeu.BACKUP_DIR, "sigles_clubs")
CACHE_V = 3   # v2 : sigles des réserves (club de base + 2 / B) ; v3 : + U19 / U21…, nom long obligatoire
ZSTD = b"\x28\xb5\x2f\xfd"
TETE = b"\x03\x01tad."
SIGLE = re.compile(r"^[^\"\r\n\t]{1,6}$")
LIGNE_SCOUT = re.compile(r'^"CLUB_3LETTER_NAME_CHANGE"\s+(\d+)\s+"([^"]*)"', re.M)


# ---------- lecture de lang_db.dat ----------
def _chaine(b, p):
    n = struct.unpack_from("<I", b, p)[0]
    if n > 1000:
        raise ValueError
    return b[p + 4:p + 4 + n].decode("utf-8"), p + 4 + n


def _table_clubs(b):
    """{id: sigle} si la trame est une table de clubs lue jusqu'au dernier octet, sinon None"""
    if not b.startswith(TETE) or len(b) < 100_000:
        return None
    try:
        nb = struct.unpack_from("<I", b, 8)[0]
        p, res, fiches = 12, {}, []
        for _ in range(nb):
            cid = struct.unpack_from("<I", b, p)[0]
            p += 4
            lo, p = _chaine(b, p); p += 1         # nom long
            co, p = _chaine(b, p); p += 1         # nom court
            s6, p = _chaine(b, p)                 # 6 lettres
            s3, p = _chaine(b, p)                 # 3 lettres
            _, p = _chaine(b, p); p += 1          # 3 lettres alt
            _, p = _chaine(b, p); p += 4          # surnom
            _, p = _chaine(b, p)                  # nom en plus
            if s3:
                res[cid] = s3
            fiches.append((cid, lo, co, s6))
    except (ValueError, UnicodeDecodeError, struct.error):
        return None
    if p != len(b):
        return None
    res.update(_reserves(fiches, res))
    return res


# réserve (2 / 3 / B / C / II / III) ou équipe de jeunes (U19, U-21, Under 19s, Sub-17) en fin de nom
RESERVE = re.compile(r"^(.+?)[ /]+(2|3|B|C|II|III|(?:U|U-|Under |Sub-?)(\d{2})s?)$")
SUFFIXE = {"II": "2", "III": "3"}


def _reserves(fiches, res):
    """{id réserve / jeunes: 3 premiers caractères du sigle du club de base + 2 / 3 / B / C / 19 / 21…} (4 ou 5
    caractères) : FM montrait « 2 » seul au tableau de score pour une réserve (QRM 2 : sigle anglais « QUE »).
    Le NOM LONG doit finir par le suffixe (« Kolding Boldklub », court « Kolding B », n'est pas une réserve) ; club de
    base trouvé par le nom long sans suffixe, sinon le court, sinon le 6 lettres"""
    index = [{}, {}, {}]
    for cid, *noms in fiches:
        if cid in res:
            for k, n in enumerate(noms):
                index[k].setdefault(n.casefold(), res[cid])
    out = {}
    for cid, *noms in fiches:
        m = RESERVE.match(noms[0])
        if not m:
            continue
        suffixe = m.group(3) or SUFFIXE.get(m.group(2), m.group(2))
        for k, n in enumerate(noms):
            mk = RESERVE.match(n)
            base = mk and index[k].get(mk.group(1).casefold())
            if base:
                out[cid] = base[:3] + suffixe   # SRFC -> SRF2, Aarau U19 -> AAR19
                break
    return out


def longueur_trame(b, j):
    """octets de la trame zstd qui commence en j (format RFC 8878 : en-tête, blocs, somme de contrôle)"""
    fhd = b[j + 4]
    simple = fhd >> 5 & 1
    p = j + 5 + (0 if simple else 1) + (0, 1, 2, 4)[fhd & 3] + ((1 if simple else 0), 2, 4, 8)[fhd >> 6]
    while True:
        if p + 3 > len(b):
            raise ValueError("trame coupée")
        h = b[p] | b[p + 1] << 8 | b[p + 2] << 16
        p += 3 + (1 if (h >> 1 & 3) == 1 else h >> 3)   # bloc RLE : 1 octet
        if h & 1:
            break
    return p + (4 if fhd >> 2 & 1 else 0) - j


def decompresseur():
    """fonction trame entière -> octets : compression.zstd (Python 3.14 : Windows, Python embarqué) sinon le module
    zstandard (Linux / Mac avec Python 3.8-3.13 : MODULES de l'app) ; ImportError sinon"""
    try:
        from compression import zstd
        return zstd.decompress, zstd.ZstdError
    except ImportError:
        import zstandard
        d = zstandard.ZstdDecompressor()
        return (lambda t: d.decompress(t, max_output_size=256 << 20)), zstandard.ZstdError


def lire_sigles(lang_db):
    """{id club: sigle} de la table de clubs qui a des sigles (l'anglaise) ; s'arrête dès qu'elle est trouvée"""
    un, erreur = decompresseur()
    data = open(lang_db, "rb").read()
    pos = 0
    for _ in range(40):   # FM27 : 3e trame ; au-delà, autre format (vieille base) -> abandon rapide
        j = data.find(ZSTD, pos)
        if j < 0:
            break
        try:
            n = longueur_trame(data, j)
            trame = un(data[j:j + n])
        except (erreur, ValueError, IndexError):
            pos = j + 4
            continue
        pos = j + n
        t = _table_clubs(trame)
        if t and len(t) >= 1000:
            return t
    raise ValueError("sigles introuvables dans / no 3-letter names in " + lang_db)


def lang_db_de(jeu, base):
    """lang_db.dat de la base, sinon celui de la base la plus proche en dessous (2620 -> 2600), sinon 2700"""
    r = noms_reels.racine_db(jeu)
    try:
        nums = sorted((n for n in os.listdir(r) if n.isdigit()), key=int)
    except OSError:
        return None
    avec = [n for n in nums if os.path.isfile(os.path.join(r, n, f"{n}_fm", "lang_db.dat"))]
    choix = [n for n in avec if base.isdigit() and int(n) <= int(base)] or avec[-1:]
    return os.path.join(r, choix[-1], f"{choix[-1]}_fm", "lang_db.dat") if choix else None


def sigles_de(lang_db, cache_seul=False):
    """lire_sigles avec cache (backups\\sigles_clubs) tant que lang_db.dat ne change pas ;
    cache_seul : None au lieu de relire la base (diagnostic rapide)"""
    st = os.stat(lang_db)
    cle = re.sub(r"[^\w]+", "_", os.path.relpath(lang_db, os.path.dirname(os.path.dirname(os.path.dirname(lang_db)))))
    p = os.path.join(CACHE, f"cache_{cle}.json")
    try:
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
        if c["taille"] == st.st_size and c["date"] == int(st.st_mtime) and c.get("v") == CACHE_V:
            if c.get("echec"):
                raise ValueError(c["echec"])
            return {int(k): v for k, v in c["sigles"].items()}
    except (OSError, KeyError):
        pass
    except ValueError as e:
        if "sigles" in str(e) or "3-letter" in str(e):
            raise
    if cache_seul:
        return None
    try:
        s, echec = lire_sigles(lang_db), ""
    except ValueError as e:   # autre format (vieille base) : retenu pour ne pas tout relire à chaque fois
        s, echec = {}, str(e)
    os.makedirs(CACHE, exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"v": CACHE_V, "taille": st.st_size, "date": int(st.st_mtime), "sigles": s, "echec": echec}, f,
                  ensure_ascii=False)
    os.replace(p + ".tmp", p)
    if echec:
        raise ValueError(echec)
    return s


def sigles_pour(jeu, base, cache_seul=False):
    """(sigles, lang_db utilisé) : base elle-même / la plus proche, sinon la plus récente (ids des clubs stables)"""
    ld = lang_db_de(jeu, base)
    if not ld:
        raise ValueError("lang_db.dat introuvable / not found")
    try:
        return sigles_de(ld, cache_seul), ld
    except ValueError:
        recent = lang_db_de(jeu, "")
        if not recent or recent == ld:
            raise
        return sigles_de(recent, cache_seul), recent


def sigles_scout(d):
    """{id: sigle} du .lnc de FM Scout posé dans cette base (vide sans leur fix)"""
    p = os.path.join(d, "lnc", "all", LNC_SCOUT)
    try:
        with open(p, encoding="utf-8-sig", errors="replace") as f:
            return {int(i): s for i, s in LIGNE_SCOUT.findall(f.read())}
    except OSError:
        return {}


def contenu(sigles, scout):
    """texte du .lnc : sigle anglais de chaque club, celui de FM Scout pour leurs clubs"""
    tout = dict(sigles)
    tout.update(scout)
    lignes = ["# FM27 Vanilla Enhanced Skin by AlexJeuVideal x Kinito : sigles a 3 lettres des clubs (tableau de score)",
              "# dans toutes les langues, recopies de la base anglaise du jeu. Fichier refait par l'app, ne pas modifier.",
              f"# {len(tout)} clubs" + (f", dont {len(scout)} pris du fix de FM Scout" if scout else ""), ""]
    lignes += [f'"CLUB_3LETTER_NAME_CHANGE"\t{i}\t"{s}"\t""' for i, s in sorted(tout.items()) if SIGLE.match(s)]
    return ("\n".join(lignes) + "\n").encode("utf-8-sig")


# ---------- état ----------
def _lire(p):
    try:
        with open(p, "rb") as f:
            return f.read()
    except OSError:
        return None


def diagnostic(jeu):
    """par base : fichier posé, à jour (même contenu que s'il était refait maintenant), avec FM Scout ou pas.
    Rapide : ne relit jamais lang_db.dat (cache seul) ; base changée depuis (MAJ de FM) = pas à jour."""
    liste = []
    for n, d in noms_reels.bases(jeu):
        p = os.path.join(d, "lnc", "all", NOM_LNC)
        b = _lire(p)
        scout = sigles_scout(d)
        a_jour = False
        if b is not None:
            try:
                s = sigles_pour(jeu, n, cache_seul=True)[0]
                a_jour = s is not None and b == contenu(s, scout)
            except (OSError, ValueError):
                a_jour = False
        liste.append({"base": n, "pose": b is not None, "a_jour": a_jour, "scout": bool(scout)})
    pose = bool(liste) and all(x["pose"] for x in liste)
    return {"db": noms_reels.racine_db(jeu), "db_ok": bool(liste), "bases": liste, "pose": pose,
            "partiel": any(x["pose"] for x in liste) and not pose,
            "a_jour": pose and all(x["a_jour"] for x in liste), "scout": any(x["scout"] for x in liste)}


# ---------- écriture ----------
def poser(jeu, a_blanc=False):
    """écrit (ou refait) le .lnc dans chaque base ; renvoie (écrits, clubs)"""
    bs = noms_reels.bases(jeu)
    if not bs:
        raise ValueError("base de données de FM introuvable / FM database not found")
    ecrits = clubs = 0
    for n, d in bs:
        s, ld = sigles_pour(jeu, n)
        b = contenu(s, sigles_scout(d))
        clubs = max(clubs, b.count(b"\n\"CLUB_3LETTER"))
        p = os.path.join(d, "lnc", "all", NOM_LNC)
        if _lire(p) == b:
            continue
        ecrits += 1
        if a_blanc:
            print(f"  [{n}] écrire / write {NOM_LNC} ({len(b) // 1024} Ko, {os.path.basename(os.path.dirname(ld))})")
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p + ".tmp", "wb") as f:
            f.write(b)
        os.replace(p + ".tmp", p)
    return ecrits, clubs


def retirer(jeu, a_blanc=False):
    """enlève notre .lnc de chaque base (rien d'autre) ; renvoie le nombre enlevé"""
    n_ = 0
    for n, d in noms_reels.bases(jeu):
        p = os.path.join(d, "lnc", "all", NOM_LNC)
        if os.path.isfile(p):
            n_ += 1
            if a_blanc:
                print(f"  [{n}] enlever / remove {NOM_LNC}")
                continue
            os.remove(p)
    return n_


def rafraichir(jeu, a_blanc=False):
    """après pose / retrait du fix de FM Scout : refait notre .lnc s'il est posé (sinon rien)"""
    if any(os.path.isfile(os.path.join(d, "lnc", "all", NOM_LNC)) for _, d in noms_reels.bases(jeu)):
        return poser(jeu, a_blanc)
    return 0, 0


def main(argv):
    jeu = os.environ.get("UIPICKER_JEU") or chemin_jeu.lire()
    a_blanc = "--dry-run" in argv
    op = (argv[0] if argv and argv[0] != "--dry-run" else "")
    t0 = time.time()
    if op == "poser":
        print("écrits / written %d, clubs %d" % poser(jeu, a_blanc))
    elif op == "retirer":
        print("enlevés / removed %d" % retirer(jeu, a_blanc))
    elif not op:
        print(json.dumps(diagnostic(jeu), ensure_ascii=False, indent=1))
    else:
        sys.exit(__doc__)
    print(f"({time.time() - t0:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1:])
