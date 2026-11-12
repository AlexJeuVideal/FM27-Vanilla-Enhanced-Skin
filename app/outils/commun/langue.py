"""Langue des textes fixes écrits par les scripts (ceux que FM ne traduit pas lui-même) : fr, en, de, es, it, pt,
tr, pl, el, ko, ja ou zh (v1.31 : traductions du fichier de la langue, anglais si un texte manque).

Réglage gardé dans backups\\langue.txt (fr par défaut). Les scripts concernés lisent `texte(fr, en)` et ajoutent
`SUFFIXE` à leur version : changer de langue change les noms des ajouts, donc l'appliquer suivant les refait.
Scripts concernés : ceux marqués textes=True dans catalogue.py (club_bandeau_installations, club_page_bas,
attributs_tout_cocher, staff_fm24, prochain_match_domicile).

Menu Outils FM.bat : choix de la langue au lancement (et 106 pour changer) ; si elle change, ces scripts sont
réappliqués s'ils sont actifs.
Usage : langue.py fr | en | de | es | it | pt | tr | pl | el | ko | ja | zh | etat | code
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402

FICHIER = os.path.join(backup.BACKUP_DIR, "langue.txt")
# fr / en écrits dans le code ; les autres : traductions\<code>.json (numéro -> texte), numéros de textes.json
# (numéro -> texte anglais, tenu par notes_claude\traductions_relever.py). Texte pas traduit : l'anglais.
LANGUES = ("fr", "en", "de", "es", "it", "pt", "tr", "pl", "el", "ko", "ja", "zh")
NOMS = {"fr": "Français", "en": "English", "de": "Deutsch", "es": "Español", "it": "Italiano", "pt": "Português",
        "tr": "Türkçe", "pl": "Polski", "el": "Ελληνικά", "ko": "한국어", "ja": "日本語", "zh": "简体中文"}
TRADUCTIONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "traductions")


def lire():
    try:
        with open(FICHIER, encoding="utf-8") as f:
            v = f.read().strip().lower()
        return v if v in LANGUES else "fr"
    except OSError:
        return "fr"


_tables = {}


def table(lg):
    """{texte anglais: traduction} de la langue lg (vide pour fr / en ou fichier absent)."""
    if lg not in _tables:
        _tables[lg] = {}
        if lg in LANGUES and lg not in ("fr", "en"):
            try:
                with open(os.path.join(TRADUCTIONS, "textes.json"), encoding="utf-8") as f:
                    source = json.load(f)
                with open(os.path.join(TRADUCTIONS, lg + ".json"), encoding="utf-8") as f:
                    tr = json.load(f)
                _tables[lg] = {source[k]: v for k, v in tr.items() if k in source and v}
            except (OSError, ValueError):
                pass
    return _tables[lg]


def traduire(fr, en, lg):
    if lg == "fr":
        return fr
    return en if lg == "en" else table(lg).get(en, en)


LANGUE = lire()
SUFFIXE = "" if LANGUE == "fr" else "-" + LANGUE   # fr : noms d'avant (rien à refaire chez le joueur)


def texte(fr, en):
    return traduire(fr, en, LANGUE)


def journal(fr, en, lg=None):
    """messages des logs (détail des tâches, Journal - Log.txt) : français, sinon anglais pour toutes les autres
    langues (v1.33, le joueur : pas de traduction des logs)"""
    return fr if (lg or LANGUE) == "fr" else en


def main(argv):
    op = argv[0].lower() if argv else ""
    if op in LANGUES:
        with open(FICHIER, "w", encoding="utf-8") as f:
            f.write(op)
        print("langue des textes fixes : français" if op == "fr" else f"fixed texts language: {op}")
    elif op == "etat":
        print(f"langue des textes fixes : {LANGUE}" if LANGUE == "fr" else f"fixed texts language: {LANGUE}")
    elif op == "code":   # pour Outils FM.bat : fr ou en, rien d'autre
        print(LANGUE)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
