"""ESSAI : valeur 1-20 tapée pour les attributs du staff (Recrutement > Modifier recherche, Conditions / Attributs)
(2026-11-12, le joueur : go pour « la boîte 1-20 »).

notes_staff v4 met dans les menus min / max des attributs du staff une copie de la zone des joueurs (chiffre + / -),
mais FM n'y propose que ses 8 niveaux (rule.Items ; + / - = évènement MinValueSelection, côté code). La ligne a aussi
une boîte entière (#intValueType : BindableIntEditBox, DataLink rule.FilterValue, évènement « valeur changée » ->
rule.FilterValue), et #cash-list-remapper écrit rule.MinValue lui-même : un modèle peut donc écrire rule.MinValue.
L'essai ajoute, à droite de notre zone (boîte « note » de notes_staff), une copie de cette boîte entière :
affichage rule.minvalue.id / maxvalue.id, évènement vers rule.MinValue / rule.MaxValue, sans plage (InitialiseRange
de FM lit MinValue / MaxValue comme des entiers). À voir en jeu : taper 13 + Entrée -> la zone affiche-t-elle 13
(FM accepte un entier hors niveaux), un niveau (ramené), ou rien ne change (refusé) ? Et la liste de résultats ?
(Ancien essai du même fichier, v1-v6 : pavés de couleur, puis liste uimanager.AttributesItemsList : vide, défait ici.)

Menu Outils FM.bat (jeu fermé) : 65 appliquer, 66 retirer. notes_staff doit être appliqué avant.
Usage : essai_valeurs_criteres.py appliquer [--dry-run] | retirer [--dry-run]
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
from arbre import Tree  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402

MODELES = ["PlayerSearchConditionFilterItem", "RecruitmentConditionFilterItem", "FilterRow",
           "PlayerSearchConditionFilterItemPhone"]
SOURCE = "PlayerSearchConditionFilterItem"     # modèle où prendre la boîte entière si la ligne n'en a pas
PREFIXE_BOITE = "UIPickerNotesStaff-"         # nos boîtes « note » (notes_staff)
NOM = "UIPickerEssaiBoite1-20-v1"
PREFIXE_NOM = "UIPickerEssaiBoite"
# boîte « note » du menu min / max -> (texte affiché, propriété écrite)
CIBLES = {"min": ("rule.minvalue.id", "rule.MinValue"), "max": ("rule.maxvalue.id", "rule.MaxValue")}
ANCIENS = ("UIPickerEssaiValeur",)            # pavés des v1-v5
LISTE_FM, LISTE_ESSAI_V6 = "rule.items", "uimanager.AttributesItemsList"


def boite_entiere(t):
    """l'élément BindableIntEditBox de #intValueType (DataLink rule.FilterValue)"""
    iv = next((r for r in t.walk() if t.name(r) == "intValueType"), None)
    if iv is None:
        return None
    return next((r for r in t.walk(iv) if isinstance(t.sd(r).get("InputChangedEvents"), dict)
                 and (t.sd(r).get("DataLink") or {}).get("m_path") == "rule.FilterValue"), None)


def evenement(octets, chemin):
    """évènement « valeur changée » de FM : remplace rule.FilterValue (dernier chemin) par chemin
    format vu : 01×5, longueur totale (int32), id (int32), 01, [longueur int32, 01 01 len 'rule'],
    [longueur int32, 01 01 len 'rule.FilterValue'], 'leov'"""
    b = bytes(octets)
    vieux = b"rule.FilterValue"
    i = b.find(vieux)
    if i < 0 or b[i - 1] != len(vieux) or b[:5] != b"\x01" * 5:
        return None
    nv = chemin.encode()
    d = len(nv) - len(vieux)
    bloc = i - 3 - 4                                      # int32 de longueur du bloc du chemin
    lb = struct.unpack_from("<i", b, bloc)[0]
    tot = struct.unpack_from("<i", b, 5)[0]
    out = bytearray(b[:i - 1]) + bytes([len(nv)]) + nv + b[i + len(vieux):]
    struct.pack_into("<i", out, bloc, lb + d)
    struct.pack_into("<i", out, 5, tot + d)
    return list(out)


def defaire_v6(t):
    """liste de choix de la v6 (uimanager.AttributesItemsList) remise à rule.items"""
    n = 0
    for b in [r for r in t.walk() if t.name(r).startswith(PREFIXE_BOITE) and t.name(r).endswith("-note")]:
        for r in t.walk(b):
            for o in t.elem(r).get("m_SerializedDataOverride") or []:
                f = (t.refs[o["m_SerializedData"]["rid"]].get("data") or {}).get("BindChoicesFunction")
                if not isinstance(f, dict):
                    continue
                args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
                for a in args:
                    if a[1][1:].endswith(LISTE_ESSAI_V6.encode()):
                        a[1] = b"\x01" + _enc_varint(len(LISTE_FM)) + LISTE_FM.encode()
                        n += 1
                f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return n


def retirer(t):
    n = defaire_v6(t)
    for r in [r for r in t.walk() if t.name(r).startswith(PREFIXE_NOM) or t.name(r) in ANCIENS]:
        if r in t.refs:
            t.remove(r)
            n += 1
    return n


def appliquer(t, src):
    if any(t.name(r) == NOM for r in t.walk()):
        return 0
    n = retirer(t)
    s = t if boite_entiere(t) is not None else src
    modele = boite_entiere(s) if s is not None else None
    if modele is None:
        return n
    for cle, (texte, ecrit) in CIBLES.items():
        note = next((r for r in t.walk() if t.name(r).startswith(PREFIXE_BOITE)
                     and t.name(r).endswith(f"dropdown-value-{cle}-visible-note")), None)
        if note is None:
            continue
        cadre = t.children(note)[0] if t.children(note) else note   # #combobox-frame : zone + / -
        b = t.clone(modele, cadre, src=None if s is t else s)
        if s is not t:
            for r in t.walk(b):
                t.elem(r)["m_RuleIndex"] = -1
        sd = t.sd(b)
        sd["name"], sd["name_UxmlAttributeFlags"] = NOM, 1
        sd["DataLink"]["m_path"] = texte
        ev = evenement(sd["InputChangedEvents"]["m_bytes"], ecrit)
        if ev is None:
            print("  évènement de la boîte : format inattendu, ignoré")
            t.remove(b)
            continue
        sd["InputChangedEvents"]["m_bytes"] = ev
        sd["InitialiseRangeFunc_UxmlAttributeFlags"] = 0   # pas de plage (MinValue / MaxValue = objets ici)
        cls = t.elem(b).get("m_Classes") or []
        t.elem(b)["m_Classes"] = cls + ["margin-left-global-gap-small"]
        n += 1
    return n


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op not in ("appliquer", "retirer"):
        sys.exit(__doc__)
    _, _, stt = nb.find_vta(SOURCE)
    src = Tree(stt) if stt is not None else None
    for modele in MODELES:
        bundle, obj, tt = nb.find_vta(modele)
        if tt is None:
            print(f"{modele} introuvable")
            continue
        t = Tree(tt)
        n = appliquer(t, src) if op == "appliquer" else retirer(t)
        if op == "appliquer":
            msg = (f"boîte 1-20 ajoutée ({n} changement(s))" if n else
                   "rien à faire (déjà fait, ou notes_staff pas appliqué)")
        else:
            msg = f"essai retiré ({n})" if n else "rien à retirer"
        print(f"{modele} : {msg}")
        if n:
            t.finish()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
    nb.save_all()


if __name__ == "__main__":
    main(sys.argv[1:])
