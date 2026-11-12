"""[AJOUT KINITO] Entraînement > Vue d'ensemble : les boutons des équipes du club à côté du mois (rendu d'Alex).

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : sur Entraînement > Vue d'ensemble, un raccourci vers l'entraînement des autres équipes du
club (Réserve, U19…), « à côté des mois », avec « le même rendu » que la rangée d'équipes d'Alex : « reprends son build
et mets-le en ajout pour moi ».

Ce que fait le clic : l'écran Entraînement > Vue d'ensemble ne peut PAS s'ouvrir pour une autre équipe (mesuré : son
panneau TrainingScreen n'a aucun paramètre ; l'entrée « Overview » de TrainingSubtabs ne passe aucun argument). L'écran
d'entraînement d'une équipe précise est Portail > Calendrier > Entraînement (CalendarTool, calendartab = 1, team) : c'est
lui qu'ouvre le lien « Programme d'entraînement » de ce bloc, et la rangée d'Alex. Le bouton de l'équipe affichée (ici
l'équipe première) est surligné, comme chez Alex.

Comment : on réutilise, SANS les modifier, les outils d'AlexJeuVideal (outils\\entrainement\\entrainement_equipes.py) :
sa fonction rangee() (liste FM horizontale de ses boutons d'équipe, mêmes réglages que dans son calendrier :
EMPLACEMENTS["calendrier"], marge 8 px) dans le SIVisible « équipe du club du joueur » de son calendrier, et son bouton
d'équipe (TeamIconAndNameCell, qu'il réécrit). L'ajout refuse donc de s'installer si sa fonction « boutons des équipes »
(entrainement_equipes) n'est pas appliquée. Seule différence : l'onglet ouvert, que sa rangée reprend de l'onglet affiché
(calendartab), est ici l'onglet Entraînement (const.one, celui du lien « Programme d'entraînement »).

Touché : TrainingOverviewCalendarBlock (bundle gameworld), après #NextEnabled (mois < >). PARTAGÉ avec l'ajout 26.6
(mémoire de l'échange de séances, choix de Kinito du 10/10) : on part du modèle ACTUEL, on n'ajoute / retire que notre
rangée (élément UIPickerKinito-vue-equipes-v*), jamais le bloc d'origine ; au retrait, les règles de style que la rangée
avait ajoutées sont retirées aussi (feuille d'origine remise si plus aucune règle ajoutée n'est utilisée).

Vu en jeu et validé par Kinito (v1, 2026-11-12).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vue_equipes.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vue_equipes.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_vue_equipes.py etat
"""
import json
import os
import sys

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, make_binding, new_visible  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (outil d'AlexJeuVideal : sa rangée et son bouton d'équipe, non modifiés)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
REGLAGE = dict(ee.EMPLACEMENTS["calendrier"], marge=8)   # comme sa rangée du calendrier ; 8 px après « > »
ONGLET = "const.one"   # onglet Entraînement du calendrier (celui du lien « Programme d'entraînement » de FM)
# =====================================================================================================

VERSION = 1
BLOC = "TrainingOverviewCalendarBlock"   # partagé avec 26.6 : on n'y ajoute / retire que notre rangée
APRES = "NextEnabled"                    # le bouton « > » du mois : la rangée se pose juste après
PREFIXE = "UIPickerKinito-vue-equipes"
NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_vue_equipes.actif")
MARQUEUR_ALEX = os.path.join(backup.BACKUP_DIR, "entrainement_equipes.actif")


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def bouton_alex():
    """vrai si la fonction « boutons des équipes » d'Alex est appliquée (son bouton d'équipe réécrit, dans le jeu)"""
    o = ouvrir(ee.BOUTON)
    return (os.path.exists(MARQUEUR_ALEX) and o is not None
            and any(o[3].name(r) == ee.NOM_BOUTON for r in ee.marques(o[3])))


def construire(t, mx):
    suivant = first(t, lambda r: t.name(r) == APRES)
    if suivant is None or suivant not in t.parent:
        return ["bouton « > » du mois (#NextEnabled) introuvable"]
    zone = t.parent[suivant]
    index = t.children(zone).index(suivant) + 1
    # comme le calendrier d'Alex : un SIVisible « équipe du club du joueur », puis sa rangée
    b = make_binding(mx.s_vis.sd(mx.vis)["Binding"], 2, ["team.Club.UniqueId", "human.Club.UniqueId"])
    club = new_visible(t, mx.s_vis, mx.vis, zone, index, NOM, b, ["row-direction-normal", "align-items-center"])
    t.sd(club)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, club, {"flex-shrink": 1, "min-width": 0})
    c = ee.rangee(t, mx, club, None, REGLAGE, nom=f"{PREFIXE}-rangee")
    onglet = [m for m in t.sd(c).get("Mappings") or [] if m.get("from") == ee.PARAM_ONGLET]
    if len(onglet) != 1:
        return ["renvoi de l'onglet du calendrier (rangée d'Alex) introuvable"]
    onglet[0]["to"]["m_path"] = ONGLET
    return [f"rangée des équipes d'Alex ({REGLAGE['liste']}) après « mois < > », clic = calendrier d'entraînement de "
            f"l'équipe ({ONGLET}), équipes du club du joueur seulement"]


def retirer_rangee(o):
    """retire notre rangée du bloc, et les règles de style qu'elle avait ajoutées à sa feuille"""
    bundle, obj, tt, t = o
    racines = [r for r in marques(t) if r in t.parent and not t.name(t.parent[r]).startswith(PREFIXE)]
    for r in racines:   # chacune avec tout ce qu'elle contient
        t.remove(r)
    orig = hp.original(bundle, obj)
    feuille = orig and hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is None:
        return
    n0 = len(feuille["m_Rules"])
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    if not any(i >= n0 for i in utilisees):
        t.styles.sh, t.styles.changed = feuille, True   # plus aucune règle ajoutée utilisée : la feuille d'origine
        return
    regles = t.styles.sh["m_Rules"]
    garder = list(range(n0)) + [i for i in range(n0, len(regles)) if i in utilisees]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    t.styles.changed = True


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


# ---------- commandes ----------
def cmd_appliquer():
    if not bouton_alex():
        print("[Kinito] Équipes (vue d'ensemble) : la fonction « boutons des équipes » d'Alex (entrainement_equipes) "
              "n'est pas appliquée, son bouton d'équipe manque : rien fait (l'appliquer d'abord)")
        return
    o = ouvrir(BLOC)
    if o is None:
        print(f"[Kinito] Équipes (vue d'ensemble) : {BLOC} introuvable (renommé par une mise à jour ?), ignoré")
        return
    if any(o[3].name(r) == NOM for r in marques(o[3])):
        print("[Kinito] Équipes (vue d'ensemble) : déjà appliqué")
    else:
        mx = ee.Morceaux()
        if not mx.ok():
            print("[Kinito] Équipes (vue d'ensemble) : morceaux de la rangée d'Alex introuvables, rien enregistré")
            return
        retirer_rangee(o)   # une ancienne version, s'il y en a une
        msgs = construire(o[3], mx)
        for m in msgs:
            print(f"[Kinito] Équipes (vue d'ensemble) : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Équipes (vue d'ensemble) : rien enregistré")
            return
        enregistrer(*o)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    o = ouvrir(BLOC)
    if o is None or not marques(o[3]):
        print("rien à retirer")
        return
    retirer_rangee(o)
    enregistrer(*o)
    nb.save_all()
    print(f"{BLOC} : rangée des équipes retirée (le reste du bloc n'est pas touché)")


def cmd_etat():
    o = ouvrir(BLOC)
    if o is None:
        print(f"{BLOC} : introuvable")
    else:
        t = o[3]
        print(f"{BLOC} : " + (f"rangée des équipes présente (à jour, v{VERSION})" if any(t.name(r) == NOM for r in marques(t))
                              else ("ANCIENNE version" if marques(t) else "pas de rangée")))
    print("bouton d'équipe d'Alex (entrainement_equipes) :", "appliqué" if bouton_alex() else "ABSENT (nécessaire)")
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
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
            print("[Kinito] Équipes (vue d'ensemble) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
