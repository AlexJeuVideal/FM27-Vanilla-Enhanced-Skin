"""Moral et satisfaction (« État d'esprit ») en icône seule dans les tableaux de joueurs (listes, tactiques, match).

- Moral : FM a déjà une cellule sans texte (PlayerMoraleCellNoText : icône + texte au survol, colonnes
  « morale-icon-only ») ; les colonnes Moral normales de toutes les fabriques de tableaux pointent vers elle.
- Satisfaction : la cellule icône seule de FM (PlayerHappinessCellOnlyIcon) agrandissait la hauteur des lignes
  (vu en jeu, v1) ; on garde donc la cellule FM PlayerHappinessCell et on cache son texte (display: none). Cette
  cellule sert aussi aux colonnes satisfaction temps de jeu / prêt : elles perdent leur texte elles aussi.
Largeur des colonnes Moral / Satisfaction globale réduite. Le titre et le tri restent.

Seul script à toucher le bundle ui-tablefactories : appliquer repart de l'original, retirer le remet.
Dans le bundle de modèles, seul le style du texte de PlayerHappinessCell change (retirer l'enlève).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\tableaux\\moral_icone_seule.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\tableaux\\moral_icone_seule.py retirer
  .venv\\Scripts\\python.exe outils\\tableaux\\moral_icone_seule.py etat
"""
import hashlib
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (correctif UnityPy, chemins du jeu)
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
MORAL = True              # colonnes Moral : icône seule (texte au survol)
SATISFACTION = True       # colonnes Satisfaction / État d'esprit : icône seule
LARGEUR = 46              # largeur par défaut des colonnes (px) ; FM : moral 100, satisfaction 125
LARGEUR_MIN = 30          # largeur minimale ; FM : moral 46 à 320, satisfaction 125
# =====================================================================================================

BUNDLE = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
MARKER = os.path.join(backup.BACKUP_DIR, "moral_icone_seule.actif")
DRY_RUN = "--dry-run" in sys.argv

MORAL_TEXTE = "3f2c525b13fc1f141891bf0603e05b1d"      # PlayerMoraleCell
MORAL_ICONE = "84bb19cb8c00bea4c891811983c599eb"      # PlayerMoraleCellNoText (mêmes paramètres binding / team)
SATIS_TEXTE = "beff1ac88ec3f8f4590232b091c3ddd7"      # PlayerHappinessCell (paramètres level / player)
SATIS_MODELE = "PlayerHappinessCell"                  # son texte est caché (bundle de modèles)
SATIS_DONNEE = "hierarchyoverallhappinesslevel"       # colonnes rétrécies : satisfaction globale seulement
DISPLAY, AUCUN = 131081, 6                            # StylePropertyId Display, StyleValueKeyword None
sm.PROPRIETES.setdefault("display-mot-cle", (DISPLAY, 1))


def guid(r):
    return (r.get("m_uxmlRef") or {}).get("m_AssetGUID")


def liaison(r, nom):
    return next((b for b in r.get("m_valueBindings") or [] if b.get("from") == nom), None)


def satisfaction_globale(r):
    """colonne Satisfaction dont le niveau est la satisfaction globale (pas temps de jeu, prêt…)"""
    lvl = liaison(r, "level")
    return lvl is not None and lvl["to"]["m_path"].lower().endswith(SATIS_DONNEE) and liaison(r, "player")


def changer(r):
    """change une colonne ; renvoie son type ou None"""
    if MORAL and guid(r) == MORAL_TEXTE:
        r["m_uxmlRef"]["m_AssetGUID"] = MORAL_ICONE
        quoi = "moral"
    elif SATISFACTION and guid(r) == SATIS_TEXTE and satisfaction_globale(r):
        quoi = "satisfaction"   # cellule FM gardée, texte caché dans le modèle (texte_satisfaction)
    else:
        return None
    r["m_defaultWidth"] = float(LARGEUR)
    r["m_minimumWidth"] = float(LARGEUR_MIN)
    return quoi


def textes_satisfaction():
    """(bundle, objet, typetree, arbre, [(rid, texte caché ?)]) des textes de PlayerHappinessCell"""
    bundle, obj, tt = nb.find_vta(SATIS_MODELE)
    if tt is None:
        sys.exit(f"{SATIS_MODELE} introuvable")
    t = sm.Tree(tt)
    t.styles = sm.Styles(bundle, tt)
    out = []
    for rid in t.find(lambda r: "TextBinding" in t.sd(r)):
        e = t.elem(rid)
        old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
        out.append((rid, any(p[0] == DISPLAY for p in old)))
    return bundle, obj, tt, t, out


def texte_satisfaction(cacher):
    """texte de PlayerHappinessCell caché (display: none) ou remis ; True si le modèle a changé"""
    bundle, obj, tt, t, textes = textes_satisfaction()
    change = False
    for rid, cache in textes:
        e = t.elem(rid)
        if cacher and not cache:
            t.styles.style(t, rid, {"display-mot-cle": AUCUN})
        elif not cacher and cache:
            reste = [p for p in t.styles.values(e["m_RuleIndex"]) if p[0] != DISPLAY]
            e["m_RuleIndex"] = t.styles.add_rule(reste) if reste else -1
        else:
            continue
        t.styles.changed = change = True
    if change:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    return change


def fabriques(env):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        if tt.get("m_rowData"):
            yield o, tt


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def source():
    """bundle d'origine si le jeu contient encore notre version (réglages changés), sinon le bundle actuel"""
    orig = backup.backup_path(BUNDLE)
    written = orig + ".written.sha256"
    if os.path.exists(orig) and os.path.exists(written) and open(written).read().strip() == _sha(BUNDLE):
        return orig
    return BUNDLE


def cmd_appliquer():
    # 1. colonnes (ui-tablefactories, refait depuis l'original)
    src = source()
    env = UnityPy.load(src)
    total = 0
    # colonnes des autres scripts D'ABORD, puis rechargement : un 2e read_typetree ne voit pas le save_typetree
    # précédent (jusqu'au 2026-11-12, etat_esprit relisait PlayerTableFactory et effaçait le moral sans texte)
    neuf = colonnes_etat_esprit(env)   # repartir de l'original ne doit pas perdre les colonnes d'etat_esprit_fm24
    if neuf is not None:
        total = 1
        env = neuf
    if colonne_staff(env):   # rechargé avant : sa fabrique peut avoir été touchée par nation_drapeau_seul
        total = 1
        env = UnityPy.load(env.file.save(packer="original"))
    for o, tt in fabriques(env):
        faits = [(r["m_id"], changer(r)) for r in tt["m_rowData"]]
        faits = [(i, k) for i, k in faits if k]
        if faits:
            o.save_typetree(tt)
            total += len(faits)
            print(f"{tt['m_Name']} : " + ", ".join(f"{i} ({k})" for i, k in faits))
    if total:
        data = env.file.save(packer="original")
        if DRY_RUN:
            print(f"(essai à blanc : rien écrit, {os.path.basename(BUNDLE)} ferait {len(data) / 1e6:.2f} Mo)")
        else:
            backup.write_bundle(BUNDLE, data)
    # 2. texte de la cellule satisfaction (bundle de modèles)
    if SATISFACTION:
        if texte_satisfaction(True):
            print(f"{SATIS_MODELE} : texte caché")
            nb.save_all()
        else:
            print(f"{SATIS_MODELE} : texte déjà caché")
    if not DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)
        print(f"\n{total} colonne(s) Moral / Satisfaction en icône seule.")


def colonnes_etat_esprit(env):
    """colonnes des autres scripts actifs (etat_esprit_fm24, entrainement_pouces, tactiques_forme_valeur,
    nation_drapeau_seul, suspensions_noms_courts, saison_presentation, colonnes_separateur, colonne_temperament) ;
    renvoie l'env rechargé si des colonnes ont été ajoutées, sinon None.
    Rechargé après CHAQUE script : read_typetree rend l'ancien arbre, sans ça le suivant qui touche la même fabrique
    efface le précédent (2026-11-09 : colonnes_separateur effaçait les colonnes Nationalité en grand logo)."""
    import entrainement_pouces as ep
    import etat_esprit_fm24 as ee
    import tactiques_forme_valeur as tf
    import nation_drapeau_seul as nd
    import suspensions_noms_courts as sn
    import saison_presentation as sp   # colonne Cotes de la présentation de saison
    import colonnes_separateur as cs   # colonnes Séparateur (2026-11-07)
    import colonne_temperament as ct   # colonne Tempérament (logo) (2026-11-13)
    change = False
    for m, on in ((ee, ee.actif()), (ep, ep.actif()), (tf, tf.actif()), (nd, nd.actif()), (sn, sn.actif()),
                  (sp, sp.actif() or sp.EN_COURS), (cs, cs.actif()), (ct, ct.actif())):
        if on and m.fabrique_appliquer(env):
            change = True
            env = UnityPy.load(env.file.save(packer="original"))
    return env if change else None


def colonne_staff(env):
    """colonne de sélection invisible du mini-tableau du staff (staff_fm24) ; True si ajoutée"""
    import staff_fm24 as sf
    return sf.actif() and sf.fabrique_appliquer(env)


def cmd_retirer():
    if os.path.exists(backup.backup_path(BUNDLE)):
        backup.restore(BUNDLE)
        env = UnityPy.load(BUNDLE)
        neuf = colonnes_etat_esprit(env)
        if neuf is not None:
            env = neuf
            colonne_staff(env)
            backup.write_bundle(BUNDLE, env.file.save(packer="original"))
        elif colonne_staff(env):
            backup.write_bundle(BUNDLE, env.file.save(packer="original"))
    if texte_satisfaction(False):
        nb.save_all()
        print(f"{SATIS_MODELE} : texte remis")
    if os.path.exists(MARKER):
        os.remove(MARKER)
    print("Colonnes Moral / Satisfaction d'origine remises.")


def cmd_etat():
    env = UnityPy.load(BUNDLE)
    for _, tt in fabriques(env):
        icone = [r["m_id"] for r in tt["m_rowData"] if guid(r) == MORAL_ICONE]
        texte = [r["m_id"] for r in tt["m_rowData"] if guid(r) == MORAL_TEXTE]
        satis = [f"{r['m_id']} ({r['m_minimumWidth']:g} px min)" for r in tt["m_rowData"]
                 if guid(r) == SATIS_TEXTE and satisfaction_globale(r)]
        if icone or texte or satis:
            print(f"{tt['m_Name']} : moral icône {icone} | moral avec texte {texte} | satisfaction {satis}")
    caches = [c for _, c in textes_satisfaction()[4]]
    print(f"{SATIS_MODELE} : texte", "caché" if caches and all(caches) else "visible")
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
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("moral en icône seule : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
