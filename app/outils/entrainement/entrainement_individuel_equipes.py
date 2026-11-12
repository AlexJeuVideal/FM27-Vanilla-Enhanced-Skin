"""Boutons des AUTRES équipes du club sur l'écran Entraînement > Entraînement individuel.

En haut de la liste des joueurs (vue Détaillée et vue Résumé), après « Détaillé | Résumé » : un bouton FM par équipe
du club (`team.Club.Teams`, liste FM : seulement les équipes qui existent), SAUF celle affichée (UniqueId différent).
Clic = entraînement individuel de cette équipe (même événement que les tuiles FM « Entraînement individuel » :
écran TeamIndividualTrainingTool, team = l'équipe, selectedplayer = null).
Ex. : sur l'équipe première -> « Réserve » « U19 » ; sur la réserve -> « équipe première » « U19 ».

Modèles touchés (ce script est leur seul propriétaire, appliquer repart toujours des originaux sauvegardés) :
- TeamIndividualTrainingBlock : écran de l'entraînement individuel (rangée ajoutée dans #Header et #TopPanel) ;
- TeamCell_IconOutside_20px-height : cellule FM inutilisée (citée par aucun bundle), réécrite en bouton d'équipe.
Morceaux recopiés de FM : liste horizontale de ClubInfoReportBlock (comme entrainement_equipes), bouton
« Demander à l'adjoint… » de l'écran lui-même (SIButton + SIText) en style bouton normal (celui de « Filtre »).

Depuis le 2026-11-12 (fusion demandée par le joueur) : les ajouts Kinito 26.14 (kinito_rapport_entrainement : onglet
Rapport d'entraînement, pouces, équipes en liens en affichage Large, nos boutons d'équipes en Medium / Small) puis
26.15 (kinito_largeur_liste : liste de gauche plus large en Large) sont lancés après ce script, chacun dans son
processus (scripts outils\\kinito\\ ; 26.14 modifié par nous, v27 / v28). Ce script passe après
entrainement_individuel_boutons, entrainement_pouces et moral_icone_seule (ORDRE_SKIN) : 26.14 doit passer après eux.
Retirer cette fonction les retire aussi (26.15, puis 26.14, puis ce script).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_individuel_equipes.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_individuel_equipes.py retirer
  .venv\\Scripts\\python.exe outils\\entrainement\\entrainement_individuel_equipes.py etat
"""
import copy
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402
from hierarchie_pyramide import typ, ouvrir, path_arg  # noqa: E402
from notes_installations import first, make_binding, new_visible  # noqa: E402
import entrainement_equipes as ee  # noqa: E402  (événement « ouvrir un écran », morceaux de FM)
import arbre as sm  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
#  "segmente" : boutons collés du calendrier d'entraînement, toutes les équipes, celle affichée surlignée (choix du
#               joueur, v2) ; "separe" : boutons séparés style « Filtre », équipe affichée cachée (v1)
STYLE_BOUTONS = "segmente"
LISTE = "team.Club.Teams"   # équipes proposées (celles du club de l'équipe affichée)
HAUTEUR = 32                # px, hauteur de la rangée (= boutons FM « medium »)
MARGE = 16                  # px, écart après « Détaillé | Résumé »
ECART = 8                   # px, écart entre deux boutons
DESCENDRE = 0               # px, + = plus bas
OP_DIFFERENT = 5            # opérateur FM « ≠ » (ComparisonOperator)
CLASSES_BOUTON = ["buttons-button-base-default", "button-size-medium"]   # comme le bouton « Filtre »
# =====================================================================================================

VERSION = 3   # v2 : boutons segmentés du calendrier (v1 : boutons séparés, équipe affichée cachée : « moins fluide ») ;
              # v3 : bouton seul (club à une équipe) arrondi des deux côtés (entrainement_equipes v6)
MODELE = "TeamIndividualTrainingBlock"
BOUTON = "TeamCell_IconOutside_20px-height"
GUID_BOUTON = "8e1743d159b522542b5635f1a5a045f1"
ECRAN = "41012275212b88b46957d71fc17c5876"      # TeamIndividualTrainingTool (ui-panelids)
PREFIXE = "UIPickerIndivEquipes"
NOM_RACINE = f"{PREFIXE}-v{VERSION}"
NOM_BOUTON = f"UIPickerBoutonIndiv-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "entrainement_individuel_equipes.actif")
ZONES = [("Header", "DetailedViewTabs"), ("TopPanel", "ListViewTabs")]   # (rangée FM, onglets Détaillé | Résumé)

for k, v in {"width": (131105, 3), "height": (131087, 3), "margin-left": (131091, 3), "margin-right": (131092, 3),
             "top": (131104, 3), "position": (131102, 7)}.items():
    sm.PROPRIETES.setdefault(k, v)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE) or t.name(r).startswith("UIPickerBoutonIndiv")]


# ---------- le bouton (cellule réécrite) ----------
def construire_bouton_segmente(t, src_onglet):
    """même bouton que la rangée du calendrier (entrainement_equipes : boutons segmentés, équipe affichée surlignée),
    clic = entraînement individuel de l'équipe"""
    msgs = ee.construire_bouton(t, src_onglet)
    if any("introuvable" in m for m in msgs):
        return msgs
    racine = t.tt["m_VisualTree"]["rid"]
    c = t.children(racine)[0]
    t.sd(c)["name"] = NOM_BOUTON
    ev = ee.evenement_ecran(ECRAN, [("team", "row"), ("selectedplayer", "null")])
    for r in t.walk(c):
        if typ(t, r) == "SIButton":
            t.sd(r)["Events"]["m_bytes"] = list(ev)
    return ["bouton d'équipe : celui du calendrier (segmenté, équipe affichée surlignée), "
            "clic = son entraînement individuel"]


def construire_bouton(t, src_onglet, src_ecran, mx):
    racine = t.tt["m_VisualTree"]["rid"]
    s_racine = src_onglet.tt["m_VisualTree"]["rid"]
    comp = next((r for r in src_onglet.children(s_racine) if typ(src_onglet, r) == "ComponentElement"), None)
    adjoint = first(src_ecran, lambda r: typ(src_ecran, r) == "SIButton"
                    and any(typ(src_ecran, k) == "SIText" for k in src_ecran.children(r)))
    if comp is None or adjoint is None:
        return ["bouton d'équipe / bouton de l'écran FM introuvable"]
    for k in list(t.children(racine)):
        t.remove(k)

    # composant : seulement le BindingExpect (row = équipe de la liste, uipickerequipe = équipe affichée)
    c = t.clone(comp, racine, src=src_onglet)
    for k in list(t.children(c)):
        t.remove(k)
    sm.no_styles(t, c)
    t.elem(c)["m_Classes"] = []
    t.sd(c)["name"], t.sd(c)["name_UxmlAttributeFlags"] = NOM_BOUTON, 1
    composants = [x["rid"] for x in t.sd(c).get("m_components") or []]
    attente = next((x for x in composants if "BindingExpect" in t.refs[x]["type"]["class"]), None)
    if attente is None:
        return ["composant BindingExpect du bouton FM introuvable"]
    autres = set(composants) - {attente}
    t.sd(c)["m_components"] = [{"rid": attente}]
    t.tt["references"]["RefIds"] = [r for r in t.tt["references"]["RefIds"] if r["rid"] not in autres]
    for x in autres:
        t.refs.pop(x, None)
    params = t.refs[attente]["data"]["Parameters"]
    row = next(p for p in params if p["name"] == "row")
    equipe = copy.deepcopy(row)
    equipe["name"], equipe["type"]["id"], equipe["isOptional"] = ee.PARAM_EQUIPE, ee.TYPE_EQUIPE, 1
    params[:] = [row, equipe]
    for e in (t.elem(r) for r in t.walk(c)):
        for prop in e.get("m_Properties") or []:
            if prop["name"] == "params":
                prop["value"] = f"row:team:False,{ee.PARAM_EQUIPE}:team:True"

    # visible seulement si ce n'est pas l'équipe affichée
    b = make_binding(mx.s_vis.sd(mx.vis)["Binding"], OP_DIFFERENT, ["row.UniqueId", f"{ee.PARAM_EQUIPE}.UniqueId"])
    vis = new_visible(t, mx.s_vis, mx.vis, c, None, f"{PREFIXE}-autre", b)
    t.sd(vis)["name_UxmlAttributeFlags"] = 1
    t.styles.style(t, vis, {"margin-right": ECART, "flex-shrink": 0})

    # bouton FM (SIButton + SIText) : nom de l'équipe, clic = son entraînement individuel
    x = t.clone(adjoint, vis, src=src_ecran)
    sm.no_styles(t, x)
    t.elem(x)["m_Classes"] = list(CLASSES_BOUTON)
    sd = t.sd(x)
    sd["name"], sd["name_UxmlAttributeFlags"] = f"{PREFIXE}-bouton", 1
    sd["Events"]["m_bytes"] = ee.evenement_ecran(ECRAN, [("team", "row"), ("selectedplayer", "null")])
    txt = next(k for k in t.children(x) if typ(t, k) == "SIText")
    tb = t.sd(txt)["TextBinding"]
    tb["m_kind"] = 1
    tb["m_direct"]["Path"]["m_path"] = "row.TeamTypeStringTypeOnly"
    tb["m_visualFunction"]["m_target"]["m_guid"] = ""
    tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = []
    t.sd(txt)["DebugDisplay"] = "UIPicker team"
    return ["bouton d'équipe : bouton FM normal, nom de l'équipe, caché pour l'équipe affichée, "
            "clic = son entraînement individuel"]


# ---------- les rangées ----------
def construire_ecran(t, mx):
    msgs = []
    for zone, onglets in ZONES:
        z = first(t, lambda r: t.name(r) == zone)
        o = z and first(t, lambda r: t.name(r) == onglets, z)
        if o is None or t.parent.get(o) != z:
            return [f"#{zone} / #{onglets} de l'entraînement individuel introuvable"]
        c = t.clone(mx.remap, z, t.children(z).index(o) + 1, src=mx.ent)
        ee._vide(t, c)
        sd = t.sd(c)
        sd["name"], sd["name_UxmlAttributeFlags"] = f"{NOM_RACINE}-{zone}", 1
        m = copy.deepcopy(sd["Mappings"][0])
        m["from"], m["to"]["m_path"], m["type"]["id"] = ee.PARAM_EQUIPE, "team", ee.TYPE_EQUIPE
        sd["Mappings"] = [m]
        t.styles.style(t, c, {"height": HAUTEUR, "margin-left": MARGE, "top": DESCENDRE, "flex-grow": 1,
                              "flex-shrink": 1, "min-width": 0})

        w = t.clone(mx.liste, c, src=mx.lst)
        ee._vide(t, w)
        wd = t.sd(w)
        wd["RowTemplate"] = {"m_AssetGUID": GUID_BOUTON, "m_SubObjectName": "", "m_SubObjectType": ""}
        wd["Binding"]["m_visualFunction"] = path_arg(wd["Binding"]["m_visualFunction"], LISTE)
        t.styles.style(t, w, {"flex-grow": 1})
        msgs.append(f"#{zone} : rangée des autres équipes ({LISTE}) après « Détaillé | Résumé »")
    return msgs


# ---------- commandes ----------
def a_jour(t, cible):
    return any(t.name(r) == cible or t.name(r).startswith(cible + "-") for r in marques(t))


def cmd_appliquer():
    actuels = {m: ouvrir(m) for m in (MODELE, BOUTON)}
    if None in actuels.values():
        print("modèles de l'entraînement individuel introuvables (renommés par une mise à jour ?), ignoré")
        return
    # 2026-10-30 : liens de Kinito (26.15, rangee(meme_club=True)) encore sur l'ancienne condition « même club » ->
    # écran refait depuis l'original (Kinito est relancé après, comme d'habitude)
    if a_jour(actuels[MODELE][3], NOM_RACINE) and a_jour(actuels[BOUTON][3], NOM_BOUTON) \
            and not ee.ancienne_condition(actuels[MODELE][3]):
        print("équipes de l'entraînement individuel : déjà appliqué")
    else:
        ancien = any(marques(v[3]) for v in actuels.values())
        travail = {m: ouvrir(m, depart_original=True) for m in (MODELE, BOUTON)}
        if any(marques(v[3]) for v in travail.values()):
            print("équipes de l'entraînement individuel : pas de sauvegarde d'origine propre, ignoré")
            return
        src_o, mx = ouvrir(ee.BOUTON_SOURCE), ee.Morceaux()
        if src_o is None or not mx.ok():
            print("équipes de l'entraînement individuel : morceaux de FM introuvables, rien enregistré")
            return
        src_e = hp.Tree(copy.deepcopy(travail[MODELE][2]))   # l'écran d'origine (bouton « Demander à l'adjoint »)
        if STYLE_BOUTONS == "segmente":
            msgs = construire_bouton_segmente(travail[BOUTON][3], src_o[3])
        else:
            msgs = construire_bouton(travail[BOUTON][3], src_o[3], src_e, mx)
        msgs += construire_ecran(travail[MODELE][3], mx)
        msgs += ["ancienne version remplacée"] if ancien else []
        for m in msgs:
            print(f"équipes de l'entraînement individuel : {m}")
        if any("introuvable" in m for m in msgs):
            print("équipes de l'entraînement individuel : rien enregistré")
            return
        for bundle, obj, tt, t in travail.values():
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
    fait = False
    for m in (MODELE, BOUTON):
        o = ouvrir(m)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = o
        orig = hp.original(bundle, obj)
        if orig is None:
            print(f"{m} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
            continue
        obj.save_typetree(orig)
        sheet = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        nb._dirty.add(bundle)
        fait = True
        print(f"{m} : remis d'origine")
    if fait:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for m, cible in ((MODELE, NOM_RACINE), (BOUTON, NOM_BOUTON)):
        o = ouvrir(m)
        if o is None:
            print(f"{m} : introuvable")
            continue
        t = o[3]
        etat = "à jour" if a_jour(t, cible) else "ANCIENNE version"
        print(f"{m} : " + (f"appliqué ({etat}, v{VERSION})" if marques(t) else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


# ajouts Kinito fusionnés le 2026-11-12, dans l'ordre où ils passent (26.14 puis 26.15)
KINITO = [os.path.join(chemins.OUTILS, "kinito", n + ".py") for n in ("kinito_rapport_entrainement",
                                                                     "kinito_largeur_liste")]


def _kinito(script, *args):
    sys.stdout.flush()
    return subprocess.run([sys.executable, script, *args, *(["--dry-run"] if nb.DRY_RUN else [])]).returncode


def _kinito_actif(script):
    return os.path.exists(os.path.join(backup.BACKUP_DIR, os.path.basename(script)[:-3] + ".actif"))


# bouton « Féliciter les cochés » de entrainement_pouces : dans l'écran que cmd_appliquer refait depuis l'original,
# donc reposé après (et après Kinito : il se range avant sa roue Actions)
FELICITER = os.path.join(chemins.OUTILS, "entrainement", "feliciter_coches.py")
# pouces du message Rapport d'entraînement (entrainement_pouces) : gabarits de Kinito, posés juste avant
POUCES_RAPPORT = os.path.join(chemins.OUTILS, "entrainement", "pouces_rapport.py")


def _feliciter():
    if os.path.exists(os.path.join(backup.BACKUP_DIR, "entrainement_pouces.actif")):
        _kinito(FELICITER, "appliquer")
        _kinito(POUCES_RAPPORT, "appliquer")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        cmd_appliquer()
        for k in KINITO:
            _kinito(k, "appliquer")   # déjà appliqué s'il est à jour
        _feliciter()
    elif op == "retirer":
        _kinito(POUCES_RAPPORT, "retirer")   # avant Kinito : ses gabarits partent
        for k in reversed(KINITO):
            if _kinito_actif(k):
                _kinito(k, "retirer")
        cmd_retirer()
    elif op == "etat":
        cmd_etat()
        for k in KINITO:
            if _kinito_actif(k):
                _kinito(k, "etat")
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
            for k in KINITO:
                _kinito(k, "appliquer")
            _feliciter()
        else:
            print("équipes de l'entraînement individuel : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
