"""Logs de l'app en anglais pour toutes les langues sauf le français (v1.33, le joueur, 2026-11-12).

Les scripts écrivent leurs messages en français ; l'app (serveur.py) passe chaque ligne affichée (détail d'une tâche,
Journal - Log.txt) par en() quand la langue n'est pas « fr ». Table : journal_en.json {modèle français: modèle anglais},
« {} » = morceau variable (nom de modèle, nombre, chemin…), relevée par notes_claude\\journal_relever.py.
Ligne inconnue : gardée telle quelle. Morceau variable lui-même connu de la table (ex. « déjà appliqué ») : traduit aussi.
"""
import json
import os
import re

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal_en.json")
_regles = None
_JETONS = re.compile(r"(\{\{|\}\}|\{\})")


def _modele(fr):
    """regex d'une ligne française (morceaux variables = groupes)"""
    out = ""
    for j in _JETONS.split(fr):
        out += "(.*?)" if j == "{}" else re.escape("{" if j == "{{" else "}" if j == "}}" else j)
    return re.compile(r"^(\s*)" + out + r"(\s*)$", re.S)


def _remplir(en, valeurs):
    it = iter(valeurs)
    return "".join(next(it, "") if j == "{}" else "{" if j == "{{" else "}" if j == "}}" else j
                   for j in _JETONS.split(en))


def _charger():
    global _regles
    if _regles is None:
        try:
            with open(TABLE, encoding="utf-8") as f:
                table = json.load(f)
        except (OSError, ValueError):
            table = {}
        # le plus précis d'abord : plus de texte fixe, moins de morceaux variables. Modèle gardé tel quel (texte du jeu,
        # déjà anglais) : sert quand même, ses morceaux variables sont traduits. Sans lettres (« {} : {} ») : non
        cles = sorted((k for k, v in table.items() if v and any(c.isalpha() for c in k.replace("{}", ""))),
                      key=lambda k: (-len(k.replace("{}", "")), k.count("{}")))
        _regles = [(_modele(k), table[k], len(k.replace("{}", ""))) for k in cles]
    return _regles


def _connu(ligne, profondeur):
    """(traduction, longueur du texte fixe du modèle) ou (None, 0)"""
    for rx, modele, fixe in _charger():
        m = rx.match(ligne)
        if m:
            g = m.groups()
            valeurs = [en(v, profondeur + 1) if profondeur < 3 else v for v in g[1:-1]]
            return g[0] + _remplir(modele, valeurs) + g[-1], fixe
    return None, 0


def en(ligne, _profondeur=0):
    """la ligne en anglais si la table la connaît, sinon telle quelle. Ligne inconnue : découpée sur « ; » puis sur
    « : » (« Modèle : message », « bandeau : a ; b »), chaque morceau traduit à part"""
    if not ligne or not ligne.strip() or not any(c.isalpha() for c in ligne):
        return ligne
    t, fixe = _connu(ligne, _profondeur)
    if _profondeur < 4 and " : " in ligne:
        # « Modèle : message connu en entier » : gagne sur un modèle plus vague de toute la ligne (« {} : bouton {} »)
        a, b = ligne.split(" : ", 1)
        tb, fixe_b = _connu(b, _profondeur + 1)
        if tb is not None and fixe_b + 3 > fixe:
            return _prefixe(a, _profondeur) + ": " + tb
    if t is not None:
        return t
    if _profondeur < 4:
        if " ; " in ligne:
            return "; ".join(en(x, _profondeur + 1) for x in ligne.split(" ; "))
        if " : " in ligne:
            a, b = ligne.split(" : ", 1)
            return en(a, _profondeur + 1) + ": " + en(b, _profondeur + 1)
        for sep in (", ", " + "):   # listes faites morceau par morceau (« photo 44 px, par-dessus le maillot… »)
            parts = _couper(ligne, sep)
            if len(parts) > 1:
                return sep.join(en(x, _profondeur + 1) for x in parts)
    return ligne


def _prefixe(a, profondeur):
    """« équipes à l'entraînement » d'après le modèle « équipes à l'entraînement : {} » (sinon traduit seul)"""
    t, _ = _connu(a + " : \x00", profondeur + 1)
    if t is not None and t.endswith("\x00"):
        return t[:-1].rstrip().rstrip(":").rstrip()
    return en(a, profondeur + 1)


def _couper(ligne, sep):
    """coupe sur sep hors parenthèses (« carte (#x, 22 px), centrés » -> 2 morceaux)"""
    parts, prof, debut, i = [], 0, 0, 0
    while i < len(ligne):
        c = ligne[i]
        prof += (c == "(") - (c == ")")
        if prof == 0 and ligne.startswith(sep, i):
            parts.append(ligne[debut:i])
            i += len(sep)
            debut = i
            continue
        i += 1
    return parts + [ligne[debut:]]


def traduire_lignes(lignes, lg):
    return list(lignes) if lg == "fr" else [en(x) for x in lignes]
