"""Ajouts affichés seulement quand il y a la place (en pratique : Détaillé / Condensé, pas en Défaut).

Chaque ajout est posé dans un conteneur affiché seulement quand FM affiche la colonne du polygone (Pour / Contre) :
même mécanisme que le bouton polygone de FM, sans le mod. Ancienne version : classe "uipicker-si-place", masquée
par le mod (Fit.cs) ; elle est remplacée à la prochaine application.
(La condition settings.AdaptiveScalingLevelIndex n'est pas lisible depuis la fiche joueur : essayée, sans effet.)

Ajouts actuels :
1. Gros bloc d'attributs (Rapport joueur) : options d'entraînement individuel sous le tableau d'attributs
   (seulement pour les joueurs de ton club).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\hors_defaut.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\hors_defaut.py retirer [--dry-run]
  .venv\\Scripts\\python.exe outils\\joueur_fiche\\hors_defaut.py etat
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402  (lecture / écriture des modèles d'écrans)
import sauvegarde_originaux as backup  # noqa: E402
from arbre import (Tree, named, make_visible, polygon_visible,  # noqa: E402
                                               CLASSE_SI_POLYGONE, Styles, SANS_CADRE)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES (True = activé, False = désactivé)
# =====================================================================================================
ENTRAINEMENT_SOUS_ATTRIBUTS = True           # gros bloc : options d'entraînement individuel sous les attributs
                                             # (seulement pour les joueurs de ton club)
ENTRAINEMENT_TAILLE = "8x1"                  # "8x1" : une ligne   |   "8x2" : version plus haute
ENTRAINEMENT_CADRE = False                   # False : seulement les menus et leurs titres (pas de bordure)
# =====================================================================================================

MARKER = os.path.join(backup.BACKUP_DIR, "hors_defaut.actif")
CLASSE_SI_PLACE = "uipicker-si-place"        # ancienne version, lue par le mod (Fit.cs)
CONDITION_MON_CLUB = "person.Team.IsHuman"   # vrai si le joueur est dans une équipe que tu diriges
GROS_BLOC = "PlayerAttributesLargeBlock"
NOM_ENTRAINEMENT = "UIPickerEntrainementPerso"
NOM_ENTRAINEMENT_MODE = "UIPickerEntrainementPasEnDefaut"
ENTRAINEMENT_DESCRIPTION = "PlayerIndividualTrainingOptionsBlockDescription"   # liste les modèles du bloc par taille
ENTRAINEMENT_MODELE = "PlayerIndividualTrainingOptionsBlock_{}"
CLASSE_SANS_CADRE = "uipicker-sans-cadre"   # ancienne version, lue par le mod (Fit.cs)
# sans cadre, sans mod : le modèle d'options est recopié dans la fiche (au lieu d'être inclus) et son cadre reçoit
# un style intégré (bordure 0, fond transparent) ; repères (sans effet en jeu) : classes du conteneur
CLASSE_RECOPIE = "uipicker-recopie-"         # + nom du modèle recopié
CLASSE_CADRE = "individual-training-block"   # classe FM du cadre (bordure + fond)


# ---------- options d'entraînement sous les attributs ----------
def training_guid(size):
    """identifiant du modèle d'options d'entraînement de cette taille, lu dans les fichiers du jeu"""
    import UnityPy
    path = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")
    for o in UnityPy.load(path).objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            if o.peek_name() != ENTRAINEMENT_DESCRIPTION:
                continue
        except Exception:
            continue
        tt = o.read_typetree()
        for c in tt.get("<Configurations>k__BackingField") or []:
            if f"{c['Size']['x']}x{c['Size']['y']}" == size:
                return c["AssetRef"]["m_AssetGUID"]
    return None


def training_shape(t, wrap):
    """(taille, version, cadre) du bloc déjà en place ; version : "polygone", "place", "mode" ou "toujours" (anciennes)"""
    kids = t.children(wrap)
    if not kids:
        return None
    cls = t.elem(kids[0]).get("m_Classes") or []
    if CLASSE_SI_POLYGONE in cls:
        kind = "polygone"
    elif CLASSE_SI_PLACE in cls:
        kind = "place"
    elif t.name(kids[0]) == NOM_ENTRAINEMENT_MODE:
        kind = "mode"
    else:
        return t.elem(kids[0]).get("m_TemplateAlias"), "toujours", True
    # le modèle d'options (fiches_plus.py pose un séparateur avant lui), inclus ou recopié
    alias = next((a for a in (t.elem(k).get("m_TemplateAlias") or "" for k in t.children(kids[0]))
                  if a.startswith(ENTRAINEMENT_MODELE.format(""))), None)
    copied = next((c[len(CLASSE_RECOPIE):] for c in cls if c.startswith(CLASSE_RECOPIE)), None)
    cadre = "mod" if CLASSE_SANS_CADRE in cls else (False if copied else True)
    return alias or copied, kind, cadre


def remove_training(t):
    existing = named(t, NOM_ENTRAINEMENT)
    for r in existing:
        t.remove(r)
    still = {t.elem(r).get("m_TemplateAlias") for r in t.walk()}
    t.tt["m_Usings"] = [u for u in t.tt["m_Usings"]
                        if not (u.get("alias", "").startswith(ENTRAINEMENT_MODELE.format("")) and u["alias"] not in still)]
    return ["options d'entraînement retirées"] if existing else []


def training_under_attributes(t):
    """options d'entraînement sous le tableau d'attributs : joueurs de ton club, seulement s'il y a la place"""
    alias = ENTRAINEMENT_MODELE.format(ENTRAINEMENT_TAILLE)
    existing = named(t, NOM_ENTRAINEMENT)
    if existing:
        if training_shape(t, existing[0]) == (alias, "polygone", ENTRAINEMENT_CADRE):
            return []
        remove_training(t)   # autre taille, autre cadre, ou ancienne version : on remplace
    table = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias") == "AttributesTableTemplate"), None)
    any_template = next((r for r in t.walk() if t.elem(r).get("m_TemplateAlias") and r != table), None)
    visible = next((r for r in t.walk() if (t.elem(r).get("m_FullTypeName") or "").endswith("SIVisible")
                    and isinstance(t.sd(r).get("Binding"), dict)), None)
    plain = next((r for r in t.walk() if t.elem(r).get("m_FullTypeName") == "UnityEngine.UIElements.VisualElement"
                  and not t.elem(r).get("m_TemplateAlias") and t.elem(r).get("m_SerializedData")), None)
    guid = training_guid(ENTRAINEMENT_TAILLE)
    if None in (table, any_template, visible, plain) or not guid:
        return ["éléments ou modèle d'entraînement introuvables (le jeu a changé ?), ignoré"]

    parent = t.parent[table]
    # condition : le joueur est dans une équipe que tu diriges
    wrap = make_visible(t, visible, parent, t.children(parent).index(table) + 1, CONDITION_MON_CLUB, NOM_ENTRAINEMENT,
                        ["align-self-stretch"])
    src_bundle, _, src_tt = nb.find_vta(alias) if not ENTRAINEMENT_CADRE else (None, None, None)
    if not ENTRAINEMENT_CADRE and src_tt is None:
        return [f"modèle {alias} introuvable (le jeu a changé ?), ignoré"]
    # conteneur affiché seulement quand FM affiche la colonne du polygone (donc pas en Défaut)
    holder = t.clone_shallow(plain, wrap)
    t.sd(holder)["name"] = ""
    t.elem(holder)["m_Classes"] = ["align-self-stretch",
                                   "margin-top-global-gap-regular", "margin-bottom-global-gap-regular"] \
        + ([] if ENTRAINEMENT_CADRE else [CLASSE_RECOPIE + alias])
    if not polygon_visible(t, holder):
        return ["bouton du polygone introuvable (le jeu a changé ?), ignoré"]
    if ENTRAINEMENT_CADRE:
        # le bloc tel quel : un modèle inclus, déclaré par son identifiant
        tpl = t.clone_shallow(any_template, holder)
        t.elem(tpl)["m_TemplateAlias"] = alias
        t.elem(tpl)["m_Classes"] = ["align-self-stretch"]
        t.sd(tpl)["templateId"] = alias
        t.sd(tpl)["name"] = ""
        if not any(u.get("alias") == alias for u in t.tt.get("m_Usings") or []):
            t.tt["m_Usings"].append({"alias": alias, "path": guid, "asset": {"m_FileID": 0, "m_PathID": 0}})
    else:
        # sans cadre : le bloc est recopié (même arbre que l'instance du modèle), ses styles intégrés aussi, puis
        # son cadre reçoit bordure 0 et fond transparent ; la mise en page de FM reste intacte
        s = Tree(src_tt)
        top = s.children(s.tt["m_VisualTree"]["rid"])[0]
        copy_ = t.clone(top, holder, src=s)
        t.styles.copy_from(Styles(src_bundle, src_tt), t, copy_)
        used = {s.elem(r).get("m_TemplateAlias") for r in s.walk(top)} - {None, ""}
        for u in s.tt.get("m_Usings") or []:
            if u.get("alias") in used and not any(v.get("alias") == u["alias"] for v in t.tt["m_Usings"]):
                t.tt["m_Usings"].append(dict(u))
        frames = [r for r in t.walk(copy_) if CLASSE_CADRE in (t.elem(r).get("m_Classes") or [])]
        if not frames:
            return [f"cadre de {alias} introuvable (le jeu a changé ?), ignoré"]
        for r in frames:
            t.styles.style(t, r, SANS_CADRE)
    return [f"options d'entraînement ({ENTRAINEMENT_TAILLE}{'' if ENTRAINEMENT_CADRE else ', sans cadre'}) "
            "sous les attributs, joueurs de ton club, quand la colonne du polygone est là (pas en Défaut)"]


# ---------- liste des ajouts : (modèle, appliquer, retirer) ----------
def ajouts():
    lst = []
    if ENTRAINEMENT_SOUS_ATTRIBUTS:
        lst.append((GROS_BLOC, training_under_attributes, remove_training))
    return lst


def run(retirer):
    changed = 0
    for model, apply_fn, remove_fn in ajouts():
        bundle, obj, tt = nb.find_vta(model)
        if tt is None:
            print(f"{model} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        t = Tree(tt)
        t.styles = Styles(bundle, tt)
        msgs = remove_fn(t) if retirer else apply_fn(t)
        for m in msgs:
            print(f"{model} : {m}")
        if not [m for m in msgs if "introuvable" not in m]:
            if not msgs:
                print(f"{model} : " + ("rien à retirer" if retirer else "déjà appliqué"))
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


def cmd_etat():
    _, _, tt = nb.find_vta(GROS_BLOC)
    if tt is None:
        print(f"{GROS_BLOC} : introuvable")
    else:
        t = Tree(tt)
        tr = named(t, NOM_ENTRAINEMENT)
        shape = training_shape(t, tr[0]) if tr else None
        print(f"{GROS_BLOC} : options d'entraînement : "
              + ((shape[0] or "?").split("_")[-1] + {"polygone": ", seulement si la colonne du polygone est là (sans mod)",
                                                     "place": ", ANCIENNE version (masquée par le mod)",
                                                     "mode": ", ANCIENNE version (condition de mode, sans effet)",
                                                     "toujours": ", ANCIENNE version (toujours visibles)"}[shape[1]]
                 + {True: ", avec cadre", False: ", sans cadre (style intégré, sans mod)",
                    "mod": ", sans cadre (ANCIENNE version, par le mod)"}[shape[2]]
                 if shape else "non"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
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
            print("ajouts hors mode Défaut : non activés, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
