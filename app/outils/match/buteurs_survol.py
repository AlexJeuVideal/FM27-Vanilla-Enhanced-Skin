"""Buteurs au survol (demande Discord 2026-11-13) : le nom d'un buteur (ou d'un joueur averti / expulsé) des listes de
résultats ouvre l'infobulle du joueur au survol (et sa fiche au clic), comme un nom de joueur ailleurs dans FM.

Méthode (celle des cartes jeunes de Kinito) : le texte de FM reste tel quel (police, couleur, coupure « … ») ; il est
mis dans une copie du BindingRemapper de PlayerNameWNationalityCell (binding = le joueur, primarytext = son nom), dont le
bouton de nom de FM (PlayerNameButton, infobulle PlayerReportPreviewTooltip) est posé PAR-DESSUS le texte, invisible
(opacité 0 : il reçoit quand même survol et clic). PlayerNameButton lui-même jamais modifié (Kinito vise son chemin).

Modèles (seul propriétaire : appliquer repart de l'original, retirer le remet) : CIBLES. Écran de match (LatestScore*,
MatchEvents*, Timeline*) : pas touché (autre bundle).

Usage (jeu fermé) : buteurs_survol.py appliquer [--dry-run] | retirer [--dry-run] | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (original d'un modèle)
import moteur_photos as mp  # noqa: E402  (ouvrir : modèle + sa feuille, depuis l'original)
from elements import first, typ, move  # noqa: E402
from club_histoire import Source, copier  # noqa: E402

for _k, _v in {"position": (131102, 7), "left": (131089, 3), "top": (131104, 3), "right": (131103, 3),
               "bottom": (131080, 3), "opacity": (458767, 2)}.items():
    sm.PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
CIBLES = [   # modèles où un SIText affiche le nom du joueur d'un incident de match (but, carton...)
    "CompetitionFixturesToolBlock_Row_Child_HomeEventInfos_Row",   # autres matchs du jour, résultats d'une compétition
    "CompetitionFixturesToolBlock_Row_Child_AwayEventInfos_Row",
    "CalendarFixturePlayerEvent_MaxRes",                           # calendrier / rencontres
    "CalendarFixturePlayerEvent_MinRes",
    "MatchReportGoalRow",                                          # résumé d'un match joué
]
FINS = (".player.initialsurname", ".player.name")   # chemin du texte du nom (minuscules)
# =====================================================================================================

VERSION = "1"
NOM = f"UIPickerButeurSurvol-v{VERSION}"
PREFIXE = "UIPickerButeurSurvol"
CLASSE = f"uipicker-buteur-survol-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "buteurs_survol.actif")
SOURCE = "PlayerNameWNationalityCell"
TYPE_PERSONNE = 1145176065
PLEIN = {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0}


def marque(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def chemin_texte(t, r):
    tb = t.sd(r).get("TextBinding") or {}
    if tb.get("m_kind") != 1:
        return ""
    return ((tb.get("m_direct") or {}).get("Path") or {}).get("m_path") or ""


def poser(t, src, rm):
    textes = [r for r in t.walk() if typ(t, r).endswith("SIText") and chemin_texte(t, r).lower().endswith(FINS)]
    if not textes:
        return None, "nom du joueur introuvable"
    for txt in textes:
        chemin = chemin_texte(t, txt)
        joueur = chemin.rsplit(".", 1)[0]
        parent = t.parent[txt]
        # enveloppe = copie du BindingRemapper (avec le bouton de nom FM) à la place du texte, texte dedans en premier
        env = copier(t, src, rm, parent, t.children(parent).index(txt))
        t.elem(env)["m_RuleIndex"] = -1
        t.elem(env)["m_Classes"] = [CLASSE]
        t.sd(env)["name"], t.sd(env)["name_UxmlAttributeFlags"] = NOM, 1
        t.sd(env)["Mappings"] = [
            {"m_serialisedType": 0, "from": "binding", "to": {"m_path": joueur}, "type": {"id": TYPE_PERSONNE}},
            {"m_serialisedType": 0, "from": "primarytext", "to": {"m_path": chemin}, "type": {"id": 0}}]
        # le texte de FM rétrécit comme avant (coupure « … ») : l'enveloppe peut rétrécir, sans largeur mini
        t.styles.style(t, env, {"flex-shrink": 1, "min-width": 0})
        bouton = [k for k in t.children(env) if t.elem(k).get("m_TemplateAlias") == "PlayerNameButton"]
        if len(bouton) != 1:
            return None, "bouton de nom FM inattendu dans la source"
        for k in list(t.children(env)):   # rien d'autre que le bouton (relais de fiche_contexte_equipe : bouton seul)
            if k != bouton[0]:
                t.remove(k)
        move(t, txt, env, 0)
        t.elem(bouton[0])["m_RuleIndex"] = -1
        t.styles.style(t, bouton[0], {**PLEIN, "opacity": 0.0, "overflow": "hidden"})
    return f"{len(textes)} nom(s) : infobulle du joueur au survol", None


def cmd_appliquer():
    src = Source(SOURCE)
    rm = src.t and first(src.t, lambda r: typ(src.t, r).endswith("BindingRemapper") and any(
        src.t.elem(k).get("m_TemplateAlias") == "PlayerNameButton" for k in src.t.children(r)))
    if rm is None:
        print("bouton de nom FM (PlayerNameWNationalityCell) introuvable : rien fait")
        return
    a_enregistrer = []
    for modele in CIBLES:
        o = mp.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if any(o[3].name(r) == NOM for r in marque(o[3])):
            print(f"{modele} : déjà appliqué")
            continue
        o = mp.ouvrir(modele, depart_original=True)
        bundle, obj, tt, t = o
        if marque(t):
            print(f"{modele} : pas de sauvegarde d'origine propre, rien fait")
            continue
        msg, err = poser(t, src, rm)
        if err:
            print(f"{modele} : {err}, rien enregistré")
            continue
        a_enregistrer.append(o)
        print(f"{modele} : {msg}")
    for bundle, obj, tt, t in a_enregistrer:
        t.finish()
        t.styles.save()
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    if a_enregistrer:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rien = True
    for modele in CIBLES:
        o = mp.ouvrir(modele)
        if o is None or not marque(o[3]):
            continue
        rien = False
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{modele} : pas de sauvegarde d'origine")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        print(f"{modele} : remis d'origine")
    nb.save_all()
    if rien:
        print("rien à retirer")


def cmd_etat():
    for modele in CIBLES:
        o = mp.ouvrir(modele)
        m = o and marque(o[3])
        print(f"{modele} :", "introuvable" if o is None else (
            ("à jour" if any(o[3].name(r) == NOM for r in m) else "ANCIENNE version") if m else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("buteurs au survol : non activé, rien à faire")
        return
    {"appliquer": cmd_appliquer, "retirer": cmd_retirer, "etat": cmd_etat}.get(op, lambda: sys.exit(__doc__))()


if __name__ == "__main__":
    sys.modules.setdefault("buteurs_survol", sys.modules[__name__])
    main(sys.argv[1:])
