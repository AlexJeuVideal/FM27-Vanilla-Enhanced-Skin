"""Boutons « Tout cocher » / « Tout décocher » sous chaque tableau d'attributs de la progression (fiche joueur >
Formation > Progression, onglet Attributs ; joueurs de champ et gardiens).

Modèles : MODELES (seul script à les modifier : appliquer repart des originaux, retirer les remet). Chaque interrupteur « Sel. » (cellule AttributeSelectorTableItem) envoie un événement FM
(Enable / DisableTrainingAttribute) avec `player.PlayerTraining` et le numéro de l'attribut. Les boutons envoient le
même événement pour chaque attribut du tableau ; le numéro vient d'une variable entière posée sur le modèle
(`uipattr<n>`), les numéros ayant été relevés en jeu (essai_ids_attributs, 2026-11-12).

Depuis le 2026-11-12 (demande du joueur, ajout Kinito 26.12 : remplace complètement ces boutons sur l'écran de la
fiche) : le script de Kinito outils\\kinito\\kinito_attributs_interrupteurs.py (gardé tel quel) est lancé après ce
script, dans son propre processus (il relit le modèle écrit) : interrupteurs en tête des colonnes + un global, ces
boutons masqués (format téléphone, PlayerReportAttributesProgressReportBlock : boutons gardés). Retirer cette
fonction retire aussi les interrupteurs.

Menu Outils FM.bat : 14 (catégorie), puis la fonction ; réappliqué par le choix 1.
Usage : attributs_tout_cocher.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import struct
import subprocess
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
from elements import move, plain  # noqa: E402

# ============================== RÉGLAGES ==============================
# Development = page Progression de la fiche (onglets Niveau / Attributs, celle qu'on voit) ; Attributes = même
# tableaux ailleurs. Fiches_plus LIT Development (boutons Féliciter / Critiquer, retrouvés par nom) : sans effet.
MODELES = ["PlayerReportDevelopmentProgressReportBlock", "PlayerReportAttributesProgressReportBlock"]
CELLULE = "AttributeSelectorTableItem"          # cellule FM de l'interrupteur (source des événements)
BOUTON = "button-base-soft-label-small"        # petit bouton FM recopié
TEXTES = (L("Tout cocher", "Select all"), L("Tout décocher", "Deselect all"))   # langue.py, choix 106
# numéros des attributs par tableau (#nom du tableau, ou #nom de son parent), relevés en jeu
TABLEAUX = {
    "TechnicalTable": [11, 23, 12, 13, 14, 17, 18, 21, 22, 15],   # Technique
    "SetPiecesTable": [24, 20, 19, 16],                           # Coups de pied arrêtés
    "GkTable": [2, 23, 8, 5, 0, 3, 18, 4, 6, 9, 1, 7, 10],        # Gardien
    "TechGkTable": [20, 19, 22],                                  # Gardiens - Technique
    "Mental": [25, 26, 33, 38, 27, 29, 30, 31, 35, 32, 34, 37, 28, 36],
    "Physical": [39, 40, 45, 43, 41, 44, 46, 42],
}
# ======================================================================
VERSION = f"2{SUFFIXE}"   # langue : suffixe -en
PREFIXE = "UIPickerToutCocher"
NOM = f"{PREFIXE}-v{VERSION}"
VAR = "uipattr{}"
MARKER = os.path.join(backup.BACKUP_DIR, "attributs_tout_cocher.actif")
KINITO = os.path.join(chemins.OUTILS, "kinito", "kinito_attributs_interrupteurs.py")   # interrupteurs (26.12)
MARKER_KINITO = os.path.join(backup.BACKUP_DIR, "kinito_attributs_interrupteurs.actif")
for k, v in {"flex-direction": (131083, 7), "margin-right": (131092, 3), "margin-top": (131093, 3)}.items():
    sm.PROPRIETES.setdefault(k, v)


def typ(t, r):
    return t.elem(r).get("m_FullTypeName") or ""


def original(bundle, obj, path_id=None):
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    pid = obj.path_id if path_id is None else path_id
    o = next((x for x in UnityPy.load(backup.backup_path(bundle)).objects if x.path_id == pid), None)
    return o.read_typetree() if o is not None else None


def ouvrir(modele, depart_original=False):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    sheet = None
    if depart_original:
        orig = original(bundle, obj)
        if orig is not None:
            tt = orig
            sheet = original(bundle, obj, tt["inlineSheet"]["m_PathID"])
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    if sheet is not None:
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, tt, t


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


# ---------- événements ----------
def _arg(chemin):
    b = bytes([1, 1, len(chemin)]) + chemin.encode()
    return struct.pack("<i", len(b)) + b


def _decoupe(octets):
    """m_bytes d'un seul événement FM « envoi » -> (entête de fonction 5 octets, chemins, identifiant 4 octets)"""
    b = bytes(octets)
    assert b[:5] == bytes([1, 1, 1, 1, 1]), "format d'événement inattendu"
    taille = struct.unpack("<i", b[5:9])[0]
    c = b[9:9 + taille]
    tete, pos, chemins = c[:5], 5, []
    while pos < len(c) - 4:
        n = struct.unpack("<i", c[pos:pos + 4])[0]
        a = c[pos + 4:pos + 4 + n]
        chemins.append(a[3:3 + a[2]].decode())
        pos += 4 + n
    return tete, chemins, c[-4:]


def _evenements(tete, ident, chemins_par_evt):
    out = bytes([1, 1, 1, len(chemins_par_evt)])
    for chemins in chemins_par_evt:
        c = tete + b"".join(_arg(p) for p in chemins) + ident
        out += b"\x01" + struct.pack("<i", len(c)) + c
    return list(out)


def sources_evenements():
    """(tête, id « cocher », id « décocher ») lus dans la cellule FM ; vérifie qu'on sait les reconstruire"""
    _, _, tt = nb.find_vta(CELLULE)
    for r in tt["references"]["RefIds"]:
        d = r.get("data") or {}
        if "CheckedEvents" in d and "UncheckedEvents" in d:
            out = []
            for k in ("CheckedEvents", "UncheckedEvents"):
                tete, chemins, ident = _decoupe(d[k]["m_bytes"])
                assert _evenements(tete, ident, [chemins]) == list(bytes(d[k]["m_bytes"])), "reconstruction ratée"
                assert chemins[0].lower() == "player.playertraining", chemins
                out.append((tete, ident))
            return out[0][0], out[0][1], out[1][1]
    raise SystemExit(f"{CELLULE} : interrupteur introuvable (mise à jour du jeu ?)")


# ---------- pose ----------
def poser(t, src_bouton, tete, id_cocher, id_decocher):
    sh = t.styles
    # variables entières (une par numéro) sur chaque BindingVariablesComponent du modèle (noms propres à nous)
    bvcs = [r["data"] for r in t.tt["references"]["RefIds"]
            if (r.get("type") or {}).get("class") in ("BindingVariablesComponent/UxmlSerializedData",
                                                      "BindingVariables/UxmlSerializedData")]
    if not bvcs:
        return "variables du modèle introuvables"
    nums = sorted({n for ids in TABLEAUX.values() for n in ids})
    for bvc in bvcs:
        bvc["ValueVariables"] = [v for v in bvc.get("ValueVariables") or [] if not v["m_name"].startswith("uipattr")]
        bvc["ValueVariables"] += [{"m_name": VAR.format(n), "m_scopeValue": {"m_serializedData": f"Int|{n}|"}}
                                  for n in nums]
        bvc["ValueVariables_UxmlAttributeFlags"] = 1

    s = src_bouton
    bouton = next(r for r in s.walk() if typ(s, r).endswith("SIButton"))
    faits = []
    for table in [r for r in t.walk() if typ(t, r).endswith("StreamedTable")]:
        cle = t.name(table) or t.name(t.parent[table])
        ids = TABLEAUX.get(cle)
        if not ids:
            continue
        parent = t.parent[table]
        index = t.children(parent).index(table)
        # colonne : le tableau (taille de son contenu) puis la rangée de boutons
        col = plain(t, parent, index, [], name=NOM)
        t.sd(col)["name_UxmlAttributeFlags"] = 1
        t.elem(col)["m_RuleIndex"] = -1
        sh.style(t, col, {"flex-grow": 1, "flex-direction": "column"})
        move(t, table, col)
        # largeur / marge du tableau (width-50-percent…) -> la colonne, sinon % de la colonne au lieu de la rangée
        cls = t.elem(table).get("m_Classes") or []
        place = [c for c in cls if c.startswith(("width-", "margin-"))]
        t.elem(col)["m_Classes"] = list(place)
        t.elem(table)["m_Classes"] = [c for c in cls if c not in place]
        sh.style(t, table, {"flex-grow": 0})
        rang = plain(t, col, None, ["row-direction-normal"])
        t.elem(rang)["m_RuleIndex"] = -1
        sh.style(t, rang, {"margin-top": 8})
        for texte, ident in zip(TEXTES, (id_cocher, id_decocher)):
            b = t.clone(bouton, rang, None, src=s)
            sh.copy_from(s.styles, t, b)
            sd = t.sd(b)
            sd["name"] = ""
            sd["Events"] = {"m_bytes": _evenements(tete, ident, [["player.PlayerTraining", VAR.format(n)] for n in ids])}
            sd["Events_UxmlAttributeFlags"] = 1
            lab = next(r for r in t.walk(b) if typ(t, r).endswith("SIText"))
            ls = t.sd(lab)
            ls.update(text=texte, text_UxmlAttributeFlags=1)
            ls["TextBinding"]["m_kind"] = 0
            ls["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            sh.style(t, b, {"margin-right": 8})
        faits.append(f"{cle} ({len(ids)})")
    return "boutons sous " + ", ".join(faits) if faits else "aucun tableau reconnu"


def cmd_appliquer():
    tete, id_c, id_d = sources_evenements()
    _, _, tt_b = nb.find_vta(BOUTON)
    b_src = Tree(tt_b)
    b_src.styles = Styles(nb.find_vta(BOUTON)[0], tt_b)
    for modele in MODELES:
        actuel = ouvrir(modele)
        if actuel is None:
            print(f"{modele} : introuvable")
            continue
        if any(actuel[3].name(r) == NOM for r in marques(actuel[3])):
            print(f"{modele} : déjà appliqué")
            continue
        travail = ouvrir(modele, depart_original=True)
        if marques(travail[3]):
            print(f"{modele} : pas de sauvegarde d'origine propre, rien fait")
            continue
        bundle, obj, tt, t = travail
        msg = poser(t, b_src, tete, id_c, id_d)
        print(f"{modele} : {msg}")
        if "introuvable" in msg or "aucun" in msg:
            continue
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    for modele in MODELES:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            print(f"{modele} : rien à retirer")
            continue
        bundle, obj, tt, t = o
        orig = original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine, rien fait")
            continue
        obj.save_typetree(orig)
        sheet = original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        print(f"{modele} : remis d'origine")
    nb.save_all()


def cmd_etat():
    for modele in MODELES:
        o = ouvrir(modele)
        noms = sorted({o[3].name(r) for r in marques(o[3])}) if o else []
        print(f"{modele} : " + (f"boutons ({', '.join(noms)} ; version actuelle v{VERSION})" if noms else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def _kinito(*args):
    sys.stdout.flush()
    return subprocess.run([sys.executable, KINITO, *args, *(["--dry-run"] if nb.DRY_RUN else [])]).returncode


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
        _kinito("appliquer")   # interrupteurs (déjà appliqué s'il est à jour)
    elif op == "retirer":
        if os.path.exists(MARKER_KINITO):
            _kinito("retirer")
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
        if os.path.exists(MARKER_KINITO):
            _kinito("etat")
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
            _kinito("appliquer")
        else:
            print("tout cocher / décocher : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
