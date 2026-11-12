"""Remplace l'affichage d'un texte de FM (libellé calculé) par la valeur brute qu'il convertit.

Dans les modèles d'écrans (VisualTreeAsset), un SIText affiche soit une valeur en direct (m_kind 1 : chemin
de donnée), soit le résultat d'une "fonction visuelle" (m_kind 2) qui transforme une valeur en libellé
(ex. 14 -> "Bon"). Passer le texte en direct sur le chemin de la valeur affiche le nombre.

Usage (jeu fermé pour "set" / "apply" / "restore") :
  list <Modèle>                          textes du modèle avec leur liaison et les données utilisées
  set <Modèle>:<cible>=<chemin> [...]    passe ces textes en affichage direct de <chemin>
                                         <cible> = numéro rid, ou @donnée affichée/convertie aujourd'hui
                                         (le @ reste valable après une mise à jour du jeu)
  apply [fichier]                        applique les lignes d'un fichier recette (défaut : RECETTES,
                                         club\\notes_installations_libelles.txt ; le staff = staff\\notes_staff.py)
  restore                                remet les bundles d'origine
  --dry-run                              (avec set / apply) montre ce qui serait fait sans rien écrire
Ex. : set YouthFacilitiesBlock_4x4:@club.YouthCoaching=club.YouthCoaching
"""
import copy
import os
import re
import sys

import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import sauvegarde_originaux as backup  # noqa: E402

from chemin_jeu import GAME, AA  # noqa: E402  (dossier du jeu demandé par Outils FM.bat)
BUNDLES = [os.path.join(AA, n) for n in (
    "ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle",
    "ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle",
)]
BUNDLE = BUNDLES[0]   # compatibilité
# recettes appliquées d'office (apply sans fichier, choix 1). La recette du staff a sa fonction avec interrupteur
# (staff\notes_staff.py, depuis le 2026-11-12) : elle n'est plus ici.
RECETTES = [os.path.join(chemins.OUTILS, "club", "notes_installations_libelles.txt")]
RECIPE = RECETTES   # compatibilité : cmd_apply(RECIPE) applique toutes les recettes
DRY_RUN = "--dry-run" in sys.argv

PATH_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")


# ---------- correctif UnityPy ----------
def _patch_unitypy():
    """UnityPy saute les références vides (rid -2, sans type) à la LECTURE mais plante en les RÉÉCRIVANT.
    Unity n'écrit aucune donnée pour elles : on fait pareil à l'écriture."""
    from UnityPy.helpers import TypeTreeHelper as T
    if getattr(T, "_uipicker_patched", False):
        return
    original = T.write_value

    def write_value(value, node, writer, config):
        if node.m_Type == "ReferencedObject":
            align = T.metaflag_is_aligned(node.m_MetaFlag)
            for child in node.m_Children:
                if child.m_Type == "ReferencedObjectData":
                    ref_nodes = T.get_ref_type_node(value, config.assetsfile)
                    if ref_nodes is None:
                        continue   # référence vide : pas de données
                    write_value(value[child.m_Name], ref_nodes, writer, config)
                else:
                    write_value(value[child.m_Name], child, writer, config)
            if align:
                writer.align_stream()
            return
        return original(value, node, writer, config)

    T.write_value = write_value   # les appels récursifs passent par le nom du module : ils prennent la version corrigée
    T._uipicker_patched = True


_patch_unitypy()


# ---------- lecture des arguments d'une fonction visuelle ----------
def strings_in(arg_bytes):
    """chaînes passées à une fonction visuelle ; chacune est précédée d'un octet donnant sa longueur"""
    data = bytes(arg_bytes)
    out = []
    for i, n in enumerate(data):
        if n < 3 or i + 1 + n > len(data):
            continue
        chunk = data[i + 1:i + 1 + n]
        if all(0x20 <= c < 0x7f for c in chunk):
            s = chunk.decode("ascii")
            if s not in out:
                out.append(s)
    return out


def paths_in(arg_bytes):
    """données (club.X, binding, attributebind.Y...) passées à une fonction visuelle"""
    return [s for s in strings_in(arg_bytes)
            if PATH_RE.fullmatch(s) and not s.startswith(("SI.", "System.", "UnityEngine."))
            and s not in ("Translation", "TranslationNonGendered", "TextColour", "TextColourStyle", "StyleClass",
                          "StyleColumn", "ColourColumn", "BackgroundStyle", "BorderColour", "IconStyle",
                          "TranslationDataSet")]


def describe(binding):
    if binding.get("m_kind") == 1:
        return f"DIRECT {binding['m_direct']['Path']['m_path']}"
    vf = binding["m_visualFunction"]
    return f"fonction {vf['m_target']['m_guid'][:8]}…  données : {', '.join(paths_in(vf['m_inputs']['m_variable']['m_argumentBytes'])) or '(aucune)'}"


# ---------- bundles ----------
_envs = {}
_dirty = set()
# 2026-11-06 : arbres déjà réécrits dans ce passage ((bundle, path_id) -> typetree). read_typetree relit l'objet
# d'avant save_typetree (UnityPy et moteur Rust) : sans ça, un job qui lit un modèle modifié par un job précédent
# (fiche_joueur_plus : copie Large du tableau d'attributs) recopiait l'ancienne version
_ecrits = {}


def env_of(bundle):
    if bundle not in _envs:
        _envs[bundle] = UnityPy.load(bundle)
    return _envs[bundle]


def find_vta(name):
    """(bundle, objet, typetree) du modèle, cherché dans les deux bundles de modèles"""
    for bundle in BUNDLES:
        for o in env_of(bundle).objects:
            if o.type.name != "MonoBehaviour":
                continue
            try:
                if o.peek_name() != name:
                    continue
            except Exception:
                continue
            deja = _ecrits.get((bundle, o.path_id))
            tt = copy.deepcopy(deja) if deja is not None else o.read_typetree()
            if "m_VisualTree" in tt:
                return bundle, o, tt
    return None, None, None


def save_all():
    for bundle in sorted(_dirty):
        data = _envs[bundle].file.save(packer="original")
        if DRY_RUN:
            print(f"(essai à blanc : rien écrit, {os.path.basename(bundle)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(bundle, data)


# ---------- commandes ----------
def cmd_list(name):
    bundle, _, tt = find_vta(name)
    if tt is None:
        sys.exit(f"modèle introuvable : {name}")
    print(f"{name}  ({os.path.basename(bundle)})")
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        if "TextBinding" in d:
            print(f"rid {r['rid']:<6} #{d.get('name', ''):<20} « {d.get('DebugDisplay') or ''} »  {describe(d['TextBinding'])}")


def targets(tt, target):
    """textes visés : un rid précis, ou "@donnée" = ceux qui affichent ou convertissent cette donnée"""
    out = []
    want = target[1:].lower() if target.startswith("@") else None
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        b = d.get("TextBinding")
        if b is None:
            continue
        # texte fixe (m_kind 0, ex. paliers « 10-11 » de notes_installations) : jamais converti, même si sa fonction
        # d'origine est restée dans les données (2026-11-12 : l'Entraînement affichait le code brut « 15 »)
        if b.get("m_kind") == 0:
            continue
        if want is None:
            if str(r["rid"]) == target:
                out.append((r["rid"], d))
            continue
        if b.get("m_kind") == 1:
            hit = b["m_direct"]["Path"]["m_path"].lower() == want
        else:
            args = b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]
            hit = want in (p.lower() for p in paths_in(args))
        if hit:
            out.append((r["rid"], d))
    return out


def already(tt, path):
    """True si un texte du modèle affiche déjà <path> en direct (recette déjà appliquée)"""
    for r in tt["references"]["RefIds"]:
        b = (r.get("data") or {}).get("TextBinding")
        if b and b.get("m_kind") == 1 and b["m_direct"]["Path"]["m_path"].lower() == path.lower():
            return True
    return False


def cmd_set(specs):
    by_vta = {}
    for spec in specs:
        m = re.fullmatch(r"([^:]+):(@?[^=]+)=(.+)", spec.strip())
        if not m:
            sys.exit(f"format attendu Modèle:cible=chemin, reçu : {spec}")
        by_vta.setdefault(m.group(1).strip(), []).append((m.group(2).strip(), m.group(3).strip()))

    changed = 0
    for name, items in by_vta.items():
        bundle, obj, tt = find_vta(name)
        if tt is None:
            print(f"{name} : modèle introuvable (renommé par une mise à jour ?), ignoré")
            continue
        touched = False
        for target, path in items:
            found = [(rid, d) for rid, d in targets(tt, target)
                     if not (d["TextBinding"].get("m_kind") == 1 and d["TextBinding"]["m_direct"]["Path"]["m_path"] == path)]
            if not found:
                print(f"{name} {target} : " + ("déjà appliqué" if already(tt, path) else
                                              "aucun texte correspondant (le modèle a peut-être changé), ignoré"))
                continue
            for rid, d in found:
                b = d["TextBinding"]
                before = describe(b)
                b["m_kind"] = 1
                b["m_direct"]["Path"]["m_path"] = path
                print(f"{name} rid {rid} #{d.get('name', '')} : {before}  ->  DIRECT {path}")
                changed += 1
                touched = True
        if touched:
            obj.save_typetree(tt)
            _dirty.add(bundle)
    if changed:
        save_all()
    else:
        print("rien à changer")


def cmd_apply(path):
    """path : un fichier recette, ou une liste (RECETTES : lignes mises bout à bout, un seul passage par modèle)"""
    specs = []
    for p in ([path] if isinstance(path, str) else path):
        if not os.path.exists(p):
            sys.exit(f"recette introuvable : {p}")
        specs += [l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    if not specs:
        sys.exit("recette vide")
    cmd_set(specs)


def cmd_restore():
    done = False
    for bundle in BUNDLES:
        if os.path.exists(backup.backup_path(bundle)):
            backup.restore(bundle)
            done = True
    if not done:
        print("aucun bundle de modèles n'a été modifié par cet outil")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    if not argv:
        sys.exit(__doc__)
    op, args = argv[0], argv[1:]
    if op == "restore":
        cmd_restore()
    elif op == "list" and len(args) == 1:
        cmd_list(args[0])
    elif op == "set" and args:
        cmd_set(args)
    elif op == "apply":
        cmd_apply(args[0] if args else RECIPE)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
