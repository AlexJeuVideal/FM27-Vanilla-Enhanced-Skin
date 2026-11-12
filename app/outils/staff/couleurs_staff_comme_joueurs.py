"""Couleurs des notes du STAFF = mêmes couleurs et mêmes seuils que les attributs des JOUEURS.

Les notes des joueurs ne contiennent aucune couleur figée : elles appellent des fonctions du jeu qui lisent
TES réglages (Préférences > couleurs des attributs : texte, fond, bordure, seuils). Le staff, lui, utilise
une table de couleurs fixe. Ce script fait appeler aux cellules du staff les mêmes fonctions que les joueurs,
avec la note du staff en entrée.

=> Les couleurs et les seuils se changent DANS LE JEU, dans l'écran des couleurs d'attributs,
   et s'appliquent aux joueurs ET au staff. Rien à modifier ici pour changer une couleur.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\staff\\couleurs_staff_comme_joueurs.py appliquer
  .venv\\Scripts\\python.exe outils\\staff\\couleurs_staff_comme_joueurs.py retirer
  .venv\\Scripts\\python.exe outils\\staff\\couleurs_staff_comme_joueurs.py appliquer --dry-run   (montre sans écrire)
  .venv\\Scripts\\python.exe outils\\staff\\couleurs_staff_comme_joueurs.py etat
"""
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
#  Pour chaque cellule du staff : quelle couleur de TES réglages joueurs elle doit prendre.
#    "texte"   -> couleur du texte        "fond" -> couleur de fond        "bordure" -> couleur de bordure
#    None      -> ne pas toucher (garde la couleur d'origine du staff)
#  (le nom entre guillemets à droite du modèle = la colonne de couleurs d'origine que la cellule utilisait)
# =====================================================================================================
CELLULES = {
    # profil d'un membre du staff, bloc Attributs (avec et sans icône)
    ("NonPlayerAttributeCell", "StyleColumn"): "texte",
    ("NonPlayerAttributeWithIconCell", "StyleColumn"): "texte",
    # tableaux : liste du staff du club
    ("NonPlayerAttributeTableCell", "ColourColumn"): "texte",
    # recherche de staff
    ("NonPlayerAttributeStyledNotGenderedCell", "ColourColumn"): "texte",
    ("NonPlayerAttributeStyledNotGenderedCell", "StyleColumn"): "fond",
}
# =====================================================================================================

STAFF_TABLE = "6ca49d57d37736844bf51500ea465cca"     # table de couleurs d'origine du staff (coaching-rating-...)
SOURCE_MODEL = "AttributeBadge"                      # note d'attribut d'un joueur
SOURCE_SETTERS = {"texte": "text-setter", "fond": "background-setter", "bordure": "border-setter"}
SOURCE_INPUT = "minValue"                            # entrée "valeur" des fonctions joueurs
# fonctions FM (ui-visualfunctions) : depuis la MAJ du 2026-11-12, les SIStyleSetter d'AttributeBadge n'ont plus de nom
SOURCE_GUIDS = {"texte": "66502b8d6c631534f95880510ff55a92",      # BindAttributeTextColour
                "fond": "169015bd63bc02246ae464e9259a7814",       # BindAttributeBackgroundColour
                "bordure": "259790cd976a15b4580a275db535ebf6"}    # BindAttributeBorderColour
MARKER = os.path.join(backup.BACKUP_DIR, "couleurs_staff.actif")


# ---------- arguments sérialisés d'une fonction visuelle ----------
# [nombre d'arguments] puis pour chacun : [taille int32][type (chaîne)][valeur]
def read_varint(b, i):
    n = shift = 0
    while True:
        c = b[i]
        i += 1
        n |= (c & 0x7F) << shift
        if c < 0x80:
            return n, i
        shift += 7


def write_varint(n):
    out = bytearray()
    while True:
        c = n & 0x7F
        n >>= 7
        out.append(c | (0x80 if n else 0))
        if not n:
            return bytes(out)


def parse_args(raw):
    b = bytes(raw)
    count, i = read_varint(b, 0)
    args = []
    for _ in range(count):
        size = struct.unpack_from("<i", b, i)[0]
        i += 4
        args.append(b[i:i + size])
        i += size
    if i != len(b):
        raise ValueError("arguments inattendus")
    return args


def build_args(args):
    out = bytearray(write_varint(len(args)))
    for a in args:
        out += struct.pack("<i", len(a)) + a
    return list(out)


def arg_type(a):
    n, j = read_varint(a, 0)
    return a[j:j + n].decode("ascii", "replace"), j + n


def arg_string(a):
    """valeur d'un argument chaîne / chemin (None si ce n'en est pas un)"""
    typ, j = arg_type(a)
    if not ("BindingPath" in typ or "StringVisualArg" in typ) or j >= len(a) or a[j] != 1:
        return None
    n, k = read_varint(a, j + 1)
    if k + n != len(a):
        return None
    return a[k:k + n].decode("ascii", "replace")


def with_string(a, value):
    typ, j = arg_type(a)
    v = value.encode("ascii")
    return a[:j] + b"\x01" + write_varint(len(v)) + v


# ---------- modèles ----------
def bind_fn(d):
    fn = d.get("BindFunction")
    if isinstance(fn, list):
        fn = fn[0] if fn else None
    return fn if fn and "m_target" in fn else None


def source_functions():
    """fonctions de couleur des joueurs (texte / fond / bordure), lues dans le jeu actuel"""
    _, _, tt = nb.find_vta(SOURCE_MODEL)
    if tt is None:
        sys.exit(f"modèle joueur {SOURCE_MODEL} introuvable (mise à jour du jeu ?)")
    out = {}
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        fn = bind_fn(d)
        if not fn:
            continue
        for kind, name in SOURCE_SETTERS.items():
            if d.get("name") == name or fn["m_target"]["m_guid"] == SOURCE_GUIDS[kind]:
                args = parse_args(fn["m_inputs"]["m_variable"]["m_argumentBytes"])
                if not any(arg_string(a) == SOURCE_INPUT for a in args):
                    sys.exit(f"{SOURCE_MODEL}/{name} : entrée '{SOURCE_INPUT}' introuvable (le jeu a changé)")
                out[kind] = (fn["m_target"]["m_guid"], args)
    missing = set(SOURCE_SETTERS) - set(out)
    if missing:
        sys.exit(f"{SOURCE_MODEL} : couleurs introuvables : {', '.join(missing)}")
    return out


def staff_setters(tt):
    """[(rid, data, colonne, chemin de la note)] : réglages de couleur d'origine du staff dans ce modèle"""
    res = []
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        fn = bind_fn(d)
        if not fn:
            continue
        try:
            args = parse_args(fn["m_inputs"]["m_variable"]["m_argumentBytes"])
        except Exception:
            continue
        strings = [arg_string(a) for a in args]
        raw = b"".join(args).decode("latin1")
        if STAFF_TABLE not in raw:
            continue
        column = next((s for s in strings if s in ("ColourColumn", "StyleColumn")), None)
        paths = [s for a, s in zip(args, strings) if s and "BindingPath" in arg_type(a)[0]]
        if column and paths:
            res.append((r["rid"], d, column, paths[-1]))
    return res


def already_done(tt, guids):
    return any((bind_fn(r.get("data") or {}) or {}).get("m_target", {}).get("m_guid") in guids
               for r in tt["references"]["RefIds"])


# ---------- commandes ----------
def cmd_appliquer():
    src = source_functions()
    guids = {g for g, _ in src.values()}
    changed = 0
    for model in sorted({m for m, _ in CELLULES}):
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        setters = staff_setters(tt)
        if not setters:
            print(f"{model} : " + ("déjà appliqué" if already_done(tt, guids) else "aucune couleur staff trouvée, ignoré"))
            continue
        touched = False
        for rid, d, column, path in setters:
            kind = CELLULES.get((model, column))
            if kind is None:
                print(f"{model} rid {rid} ({column}) : laissé tel quel (réglage None)")
                continue
            guid, args = src[kind]
            new_args = [with_string(a, path) if arg_string(a) == SOURCE_INPUT else a for a in args]
            fn = bind_fn(d)
            fn["m_target"]["m_guid"] = guid
            fn["m_inputs"]["m_variable"]["m_argumentBytes"] = build_args(new_args)
            print(f"{model} rid {rid} : couleurs staff ({column})  ->  couleur de {kind} des joueurs, note = {path}")
            changed += 1
            touched = True
        if touched:
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
    if changed:
        nb.save_all()
        if not nb.DRY_RUN:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
            print("\nCouleurs du staff = couleurs des joueurs. Elles se règlent dans le jeu (couleurs des attributs).")
    else:
        print("rien à changer")


def cmd_retirer():
    """remet les modèles d'origine puis refait tout le reste du skin (qui touche les mêmes fichiers)"""
    import lancer
    lancer.retirer_par_restauration(MARKER)
    print("\nCouleurs d'origine du staff remises.")


def cmd_etat():
    guids = {g for g, _ in source_functions().values()}
    for model in sorted({m for m, _ in CELLULES}):
        _, _, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable")
        else:
            print(f"{model} : " + ("couleurs des joueurs" if already_done(tt, guids) else "couleurs d'origine du staff"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
    elif op == "retirer":
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":   # utilisé par le menu après une mise à jour
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("couleurs du staff : non activées, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
