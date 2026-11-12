"""Colonnes « Stade » et « Spectateurs » à droite du programme des rencontres (Calendrier > Rencontres).

Cet écran n'est pas un tableau FM à colonnes réglables : chaque ligne est un modèle (CalendarFixtureRow_*), l'en-tête
un autre (CalendarFixtureListHeader_*), d'où « Modifier les colonnes » bloqué en jeu. On ajoute donc deux cases à
droite dans la ligne ET dans l'en-tête, aux mêmes largeurs :
- Stade : fixture.Stadium.Name ;
- Spectateurs : fixture.Attendance, seulement pour les matchs joués (fixture.HasResult, comme le panneau de FM).
Titres = textes traduits de FM. La colonne Compétition est rétrécie pour faire la place ; sa règle d'origine est
notée sur l'élément (classe uipicker-regle-origine-<n>) et remise par retirer.
Fenêtre petite (MinRes) : pas touchée.

Porte l'option « rencontres » (options.py) : version Kinito de l'onglet (commun\\rencontres_version.py), appliquée ou
retirée après les colonnes. D'où sa place à la fin du choix 1 (après entrainement_equipes, dont Kinito réutilise la
rangée).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\calendrier\\rencontres_stade_spectateurs.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\calendrier\\rencontres_stade_spectateurs.py retirer [--dry-run]
  .venv\\Scripts\\python.exe outils\\calendrier\\rencontres_stade_spectateurs.py etat
"""
import copy
import json
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint, new_visible, src_tree  # noqa: E402
import rencontres_version  # noqa: E402  (option « rencontres » : version Kinito de l'onglet)

# =====================================================================================================
#  RÉGLAGES (changer un réglage → augmenter VERSION)
# =====================================================================================================
STADE = True
SPECTATEURS = True
SPECTATEURS_SI_JOUE = True     # spectateurs seulement pour les matchs joués (sinon FM affiche 0)
# largeurs en px, par taille de fenêtre : (compétition, stade, spectateurs)
# compétition et stade se partagent la place restante (flex-grow 1) et peuvent rétrécir
LARGEURS = {
    "MaxRes": (260, 260, 110),        # grande fenêtre (FM : compétition 480)
    "StandardRes": (180, 180, 90),    # fenêtre moyenne (FM : compétition 218)
}
VERSION = 2
# =====================================================================================================

LIGNE = "CalendarFixtureRow_{}"
ENTETE = "CalendarFixtureListHeader_{}"
TRAD_STADE = 18770                     # « Stadium » : titre de la colonne stade des tableaux de rencontres FM
TRAD_SPECTATEURS = 43782               # « Attendance » : compte-rendu de match (MatchReportDetailsBlock)
CHEMIN_STADE = "fixture.Stadium.Name"      # v1 NameForComp : vide en jeu (lu sous une liaison competition chez FM)
CHEMIN_SPECTATEURS = "fixture.Attendance"
CHEMIN_JOUE = "fixture.HasResult"
SOURCE_VISIBLE = ("CalendarFixtureCard_MaxRes", "AttendanceVisible")   # SIVisible direct de FM, recopié
NOM_STADE = "UIPickerStade"
NOM_SPECTATEURS = "UIPickerSpectateurs"
CLASSE_VERSION = f"uipicker-stade-spectateurs-v{VERSION}"
CLASSE_REGLE = "uipicker-regle-origine-"
MARKER = os.path.join(backup.BACKUP_DIR, "rencontres_stade_spectateurs.actif")

sm.PROPRIETES.setdefault("width", (131105, 3))


def named(t, nom):
    return [r for r in t.walk() if t.name(r) == nom]


def competition(t):
    """case Compétition, enfant direct de la rangée (la ligne a aussi un #Competition intérieur)"""
    return next((r for r in t.walk() if t.name(r) == "Competition"
                 and (r not in t.parent or t.name(t.parent[r]) != "Competition")), None)


def regle_origine(t, rid):
    for c in t.elem(rid).get("m_Classes") or []:
        if c.startswith(CLASSE_REGLE):
            return int(c[len(CLASSE_REGLE):])
    return None


def retrecir(t, rid, largeur):
    """Compétition : largeur réduite, partage la place ; règle d'origine notée sur l'élément"""
    e = t.elem(rid)
    if regle_origine(t, rid) is None:
        e["m_Classes"] = list(e.get("m_Classes") or []) + [f"{CLASSE_REGLE}{e.get('m_RuleIndex', -1)}"]
    else:   # déjà rétrécie (autre version) : on repart de la règle d'origine
        e["m_RuleIndex"] = regle_origine(t, rid)
    t.styles.style(t, rid, {"width": largeur, "flex-grow": 1, "flex-shrink": 1, "min-width": 0, "overflow": "hidden"})


def remettre(t, rid):
    n = regle_origine(t, rid)
    if n is None:
        return False
    e = t.elem(rid)
    e["m_RuleIndex"] = n
    e["m_Classes"] = [c for c in e["m_Classes"] if not c.startswith(CLASSE_REGLE)]
    return True


def titre(t, cell, trad, texte):
    """texte de l'en-tête recopié : identifiant de traduction FM (et texte de secours) remplacés"""
    for o in t.elem(cell).get("m_SerializedDataOverride") or []:
        sd = t.refs[o["m_SerializedData"]["rid"]]["data"]
        vf = (sd.get("TextBinding") or {}).get("m_visualFunction")
        if not vf:
            continue
        args = decode_args(vf["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"TranslationID]"):
                a[1] = struct.pack("<i", trad) + b"\x01" + _enc_varint(len(texte)) + texte.encode()
        vf["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd["DebugDisplay"] = texte
        return True
    return False


def ajouter(t, modele_ligne, ligne, nom, largeur, chemin, grandit, joue=None):
    """case recopiée de modele_ligne (rangée), liaison binding → chemin ; joue = SIVisible (source, rid)"""
    rangee = t.parent[modele_ligne]
    r = t.clone(modele_ligne, rangee)
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1
    t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or [] if not c.startswith(CLASSE_REGLE)] \
        + [CLASSE_VERSION]
    css = {"width": largeur, "flex-grow": 1 if grandit else 0, "flex-shrink": 1 if grandit else 0}
    if grandit:
        css.update({"min-width": 0, "overflow": "hidden"})
    t.styles.style(t, r, css)
    if ligne:
        maps = t.sd(r).get("Mappings") or []
        if not maps:
            return None
        maps[0]["to"]["m_path"] = chemin
        del maps[1:]
        if joue:
            s, vis = joue
            b = copy.deepcopy(s.sd(vis)["Binding"])
            b["m_kind"], b["m_direct"]["Path"]["m_path"] = 1, CHEMIN_JOUE
            v = new_visible(t, s, vis, r, 0, nom + "SiJoue", b)
            for k in t.children(r):
                if k != v:   # la cellule passe dans le SIVisible
                    t.elem(r)["m_Children"] = [c for c in t.elem(r)["m_Children"] if c["rid"] != k]
                    t.elem(v)["m_Children"].append({"rid": k})
                    t.elem(k)["m_Parent"] = {"rid": v}
                    t.parent[k] = v
    return r


def retirer_modele(t):
    faits = 0
    for nom in (NOM_STADE, NOM_SPECTATEURS):
        for r in named(t, nom):
            t.remove(r)
            faits += 1
    comp = competition(t)
    if comp is not None and remettre(t, comp):
        faits += 1
    return faits


def appliquer_modele(t, taille, ligne, joue):
    """renvoie un message, ou None si déjà appliqué"""
    deja = named(t, NOM_STADE) + named(t, NOM_SPECTATEURS)
    if deja and all(CLASSE_VERSION in (t.elem(r).get("m_Classes") or []) for r in deja) \
            and len(deja) == STADE + SPECTATEURS:
        return None
    retirer_modele(t)
    comp = competition(t)
    modele = next((r for r in t.walk() if t.name(r) == "Time"), None)
    if comp is None or modele is None:
        return "cases Compétition / Heure introuvables (le jeu a changé ?), ignoré"
    l_comp, l_stade, l_spect = LARGEURS[taille]
    retrecir(t, comp, l_comp)
    quoi = []
    if STADE:
        r = ajouter(t, modele if ligne else comp, ligne, NOM_STADE, l_stade, CHEMIN_STADE, True)
        if r is None or (not ligne and not titre(t, r, TRAD_STADE, "Stadium")):
            return "case Stade impossible à construire, ignoré"
        quoi.append("Stade")
    if SPECTATEURS:
        r = ajouter(t, modele if ligne else comp, ligne, NOM_SPECTATEURS, l_spect, CHEMIN_SPECTATEURS, False,
                    joue if SPECTATEURS_SI_JOUE else None)
        if r is None or (not ligne and not titre(t, r, TRAD_SPECTATEURS, "Attendance")):
            return "case Spectateurs impossible à construire, ignoré"
        quoi.append("Spectateurs" + (" (matchs joués)" if ligne and SPECTATEURS_SI_JOUE else ""))
    return " + ".join(quoi) + f" ajouté(s) à droite, Compétition {l_comp} px"


def run(retirer):
    joue = None
    if not retirer and SPECTATEURS and SPECTATEURS_SI_JOUE:
        s, _ = src_tree(SOURCE_VISIBLE[0])
        vis = next((r for r in s.walk() if s.name(r) == SOURCE_VISIBLE[1]), None) if s else None
        if vis is None:
            sys.exit(f"SIVisible {SOURCE_VISIBLE[1]} de {SOURCE_VISIBLE[0]} introuvable (le jeu a changé ?)")
        joue = (s, vis)
    changed = 0
    for taille in LARGEURS:
        for modele, ligne in ((LIGNE.format(taille), True), (ENTETE.format(taille), False)):
            bundle, obj, tt = nb.find_vta(modele)
            if tt is None:
                print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
                continue
            t = sm.Tree(tt)
            t.styles = sm.Styles(bundle, tt)
            if retirer:
                msg = "retiré" if retirer_modele(t) else None
            else:
                msg = appliquer_modele(t, taille, ligne, joue)
            if msg is None:
                print(f"{modele} : " + ("rien à retirer" if retirer else "déjà appliqué"))
                continue
            print(f"{modele} : {msg}")
            if "ignoré" in msg:
                continue
            t.finish()
            t.styles.save()
            obj.save_typetree(tt)
            nb._dirty.add(bundle)
            changed += 1
    if changed:
        nb.save_all()
    if not nb.DRY_RUN:
        if retirer and os.path.exists(MARKER):
            os.remove(MARKER)
        elif not retirer:
            with open(MARKER, "w", encoding="utf-8") as f:
                json.dump({"actif": True}, f)
    rencontres_version.accorder(nb.DRY_RUN)   # après le marqueur : retirée = version du skin


def cmd_etat():
    for taille in LARGEURS:
        for modele in (LIGNE.format(taille), ENTETE.format(taille)):
            _, _, tt = nb.find_vta(modele)
            if tt is None:
                print(f"{modele} : introuvable")
                continue
            t = sm.Tree(tt)
            cases = [(n, r) for n in (NOM_STADE, NOM_SPECTATEURS) for r in named(t, n)]
            versions = {c for _, r in cases for c in t.elem(r).get("m_Classes") or [] if c.startswith("uipicker-stade")}
            print(f"{modele} : " + (", ".join(n[len('UIPicker'):] for n, _ in cases) + f" ({', '.join(versions)})"
                                    if cases else "non"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")
    print("onglet Rencontres :", "version Kinito (option)" if rencontres_version.kinito() else "version du skin")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True   # (avant : ignoré, l'essai à blanc écrivait)
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        run(retirer=False)
    elif op == "retirer":
        run(retirer=True)
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            run(retirer=False)
        else:
            print("stade / spectateurs des rencontres : non activé, rien à faire")
            rencontres_version.accorder(nb.DRY_RUN)   # version Kinito encore posée : retirée
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
