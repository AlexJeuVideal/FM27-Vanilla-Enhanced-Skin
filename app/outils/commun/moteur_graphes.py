"""Points des courbes de FM (moteur commun) : modèle de point posé sur les courbes financières (DataPointTemplate),
points rapetissés / zones de survol (POINTS), repères (REPERES).

Toutes les courbes de FM sont des FMLineChart ; leur champ DataPointTemplate dit quel petit modèle dessiner à chaque
point. Le graphique Finances > Dépenses utilise FinancesReportLineChartPoint (point gris, dernier en violet, infobulle
« [%cash#1] » sur binding.GraphPointY). Ailleurs ce champ est vide, ou pointe vers LineChartGeometry (rien dessiné) ou
ClubFinancesLineChartPoint (points invisibles sauf le dernier) : on y met FinancesReportLineChartPoint (COURBES).
Utilisé par finances\\graphes_finances.py (COURBES + point des finances) et
joueur_progression\\graphes_attributs.py (point de la progression des attributs + repères) : chacun donne ses
réglages (POINTS, REPERES, COURBES) et son marqueur. Les points suivent les données du jeu : rien n'est inventé.
(Avant le rangement du 2026-11-12 : graphes_points.py, les deux ensemble.)
"""
import json
import os
import re
import sys

import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402

POINT = "FinancesReportLineChartPoint"   # modèle de point de FM à poser
REMPLACES = {"", "LineChartGeometry", "ClubFinancesLineChartPoint"}   # modèles de point remplacés ("" = aucun)
DONNEES = re.compile(r"financ|expenditure|income|projection", re.I)   # courbes concernées (chemin des données)
EXCLURE = set()   # noms de modèles d'écran à laisser tels quels (ex. {"ClubFinancesSummaryTile_2x2"})
MARKER = None                 # donnés par le script appelant
POINTS, REPERES, COURBES = [], [], False
TYPE = "FM.UI.FMLineChart"
# Zone de survol : rectangle transparent centré sur le point (enfant en position absolue ; le survoler = survoler le
# point, donc infobulle). Les points sont dessinés dans l'ordre des mois : là où deux zones se recouvrent, le mois
# suivant gagne. Largeur = écart entre deux mois -> le passage d'un mois à l'autre tombe au milieu.
ZONE_NOM = "UIPickerZoneSurvol"
TRAIT_NOM = "UIPickerTrait"
VERSION_POINTS = 4   # v1 : zone 40 x 40 ; v2 : points finances invisibles, colonnes de survol, traits d'essai ;
#                      v3 : traits retirés (FM ne coupe pas au cadre ; points != mois sur les attributs) ;
#                      v4 : points finances visibles mais discrets (5 px, opacité 0.6), zone 70 x 260
# Modèles de point modifiés (seul script à les toucher : repartent toujours de l'original) :
#   modele / nom : modèle FM et nom du point (None = le VisualElement sous le SIStyleSetter) ; taille : px du point FM
#   opacite : None = celle de FM, 0 = point invisible (fond et bordure retirés ; le survol et le trait restent)
#   zone    : (largeur, hauteur) px de la zone de survol, ou None
#   trait   : (px au-dessus, px en dessous, couleur rvba) trait vertical de 1 px passant par le point, ou None
# - progression des attributs : point 10 px par mois (#PointColor, couleur de l'attribut, infobulle nom + note), en
#   opacité 0 chez FM (USS .player-attribute-line-chart-color-point ; 1 au survol).
# - finances : point 8 px (USS data_display-graphs-data_points-medium-circle-grey / -purple), infobulle sur la racine.
# Traits : essai v2 vu en jeu (2026-11-12) -> FM ne coupe rien au cadre des finances (traits sur toute la page) ; sur
# les attributs il coupe au cadre, mais le cadre comprend les noms des mois, et les points ne tombent que les mois où
# FM a enregistré les attributs (pas tous les mois). Un point ne connaît ni l'axe ni les mois : traits retirés.
# discret : (px, opacité) point FM rapetissé (centré au même endroit par des marges) et atténué ; la zone de survol
# (enfant du point) est transparente, l'opacité ne la gêne pas. v4 : points finances revenus, discrets (5 px, 0.6)
# Repères verticaux à chaque mois (ESSAI v1, attributs seulement) : FM fabrique les noms des mois (et les valeurs de
# l'axe Y) comme textes enfants directs de la courbe, sans classe à lui, placés en position absolue, largeur et
# hauteur fixées par le code. Une règle de style (feuille intégrée du modèle, rattachée à la courbe) les vise :
# « .classe > .unity-text-element ». Le trait = leur bordure gauche ; padding-top énorme + translate vers le haut
# (le texte reste en place, la boîte monte jusqu'en haut, FM coupe au cadre) ; padding-right = largeur du libellé +
# translate 50 % -> bordure et texte centrés sur le mois. Effet de bord possible sur les valeurs de l'axe Y.
# Essai v1 vu en jeu : la règle s'applique bien (feuille rattachée par m_Stylesheets = OK), mais TOUS les libellés
# (mois ET valeurs Y) ont disparu : FM les place d'après leur taille (padding 2000 -> sortis du cadre). Désactivé
# (actif=False : appliquer le retire).
VERSION_REPERES = 1
REPERE_MARQUE = "--uipicker-reperes"   # propriété perso posée dans la règle : sa valeur = VERSION_REPERES
sm.PROPRIETES.setdefault("opacity", (458767, 2))    # StylePropertyId Opacity
sm.PROPRIETES.setdefault("width", (131105, 3))
sm.PROPRIETES.setdefault("height", (131087, 3))
sm.PROPRIETES.setdefault("left", (131089, 3))
sm.PROPRIETES.setdefault("top", (131104, 3))
sm.PROPRIETES.setdefault("position", (131102, 7))   # "absolute"
sm.PROPRIETES.setdefault("margin-left", (131091, 3))
sm.PROPRIETES.setdefault("margin-top", (131093, 3))
sm.PROPRIETES.setdefault("border-radius", (262147, 3))


def guid_noms():
    """{GUID Addressables: nom du modèle} pour les deux bundles de modèles"""
    out = {}
    for bundle in nb.BUNDLES:
        env = nb.env_of(bundle)
        # m_Container de l'AssetBundle : GUID -> plage de m_PreloadTable (le modèle et sa feuille inlineStyle ;
        # env.container ne garde qu'un des deux objets)
        ab = next(o for o in env.objects if o.type.name == "AssetBundle").read_typetree()
        objets = {o.path_id: o for o in env.objects}
        for guid, info in ab["m_Container"]:
            for p in ab["m_PreloadTable"][info["preloadIndex"]:info["preloadIndex"] + info["preloadSize"]]:
                o = objets.get(p["m_PathID"])
                if o is None or o.type.name != "MonoBehaviour":
                    continue
                try:
                    tt = o.read_typetree()
                except Exception:
                    continue
                if "m_VisualTree" in tt:
                    out[guid] = tt["m_Name"]
                    break
    return out


def chemin_donnees(sd):
    """chemin des données de la courbe (1er argument BindingPath de BindDataPointsFunction)"""
    octets = bytes((sd.get("BindDataPointsFunction") or {}).get("m_inputs", {}).get("m_variable", {})
                   .get("m_argumentBytes") or [])
    m = re.search(rb"BindingPath\]\x01.([A-Za-z_][\w.]*)", octets, re.S)
    return m.group(1).decode() if m else ""


def courbes(tt):
    """[(élément, données sérialisées)] des FMLineChart d'un modèle"""
    refs = {r["rid"]: r for r in tt["references"]["RefIds"]}
    out = []
    for r in refs.values():
        e = r.get("data") or {}
        if e.get("m_FullTypeName") == TYPE:
            sd = (refs.get((e.get("m_SerializedData") or {}).get("rid")) or {}).get("data")
            if sd is not None:
                out.append((e, sd))
    return out


def modeles():
    """[(bundle, objet, typetree)] des modèles d'écran qui contiennent une courbe"""
    out = []
    for bundle in nb.BUNDLES:
        for o in nb.env_of(bundle).objects:
            if o.type.name != "MonoBehaviour":
                continue
            try:
                tt = o.read_typetree()
            except Exception:
                continue
            if "m_VisualTree" in tt and any(courbes(tt)):
                out.append((bundle, o, tt))
    return out


def opacite(t, sh, rid):
    """opacité du style intégré de rid, ou None"""
    if t.elem(rid).get("m_RuleIndex", -1) < 0:
        return None
    return next((v[0][1] for pid, _, v in sh.values(t.elem(rid)["m_RuleIndex"]) if pid == 458767), None)


def trouver_point(t, nom):
    """élément point du modèle : #nom, ou (nom None) le VisualElement enfant du SIStyleSetter"""
    for r in t.walk():
        if nom is not None:
            if t.name(r) == nom:
                return r
        elif (t.elem(r).get("m_FullTypeName") == "UnityEngine.UIElements.VisualElement"
              and (t.elem(t.parent.get(r, r)).get("m_FullTypeName") or "").endswith("SIStyleSetter")):
            return r
    return None


def marque_version(t, rid):
    """version de nos ajouts sous le point (nom de la zone / du trait), ou None"""
    for r in t.children(rid):
        n = t.name(r)
        if n.startswith(ZONE_NOM) or n.startswith(TRAIT_NOM):
            return n.rsplit("-v", 1)[-1] if "-v" in n else "1"
    return None


def enfant_absolu(t, sh, rid, nom, gauche, haut, largeur, hauteur, couleur=None, survol=True):
    """VisualElement en position absolue sous le point (copie sans classes ni règle FM)"""
    z = t.clone_shallow(rid, rid, 0)
    sd = t.sd(z)
    sd.update(name=f"{nom}-v{VERSION_POINTS}", name_UxmlAttributeFlags=1,
              pickingMode=0 if survol else 1, pickingMode_UxmlAttributeFlags=1)   # 0 Position, 1 Ignore
    t.elem(z)["m_Classes"] = []
    t.elem(z)["m_RuleIndex"] = -1
    css = {"position": "absolute", "left": gauche, "top": haut, "width": largeur, "height": hauteur}
    if couleur is not None:
        css["background-color"] = couleur
    sh.style(t, z, css)
    return z


def agrandir_point(p):
    """point invisible / zone de survol / trait vertical ; renvoie un message ou None. Repart toujours de l'original."""
    modele, nom, taille_fm, opac = p["modele"], p["nom"], p["taille"], p["opacite"]
    if opac is None and p["zone"] is None and p["trait"] is None and not p.get("discret"):
        return retirer_point(modele, nom)
    bundle, o, tt = nb.find_vta(modele)
    if tt is None:
        return f"{modele} introuvable, ignoré"
    t, sh = Tree(tt), Styles(bundle, tt)
    rid = trouver_point(t, nom)
    if rid is None:
        return f"{modele} : point introuvable, ignoré"
    if marque_version(t, rid) == str(VERSION_POINTS):
        return None
    orig = original(bundle, o)
    if orig is not None:   # repartir de l'origine (sinon chaque réglage s'empilerait)
        tt = orig
        t = Tree(tt)
        sh.sh = original(bundle, o, tt["inlineSheet"]["m_PathID"]) or sh.sh
        rid = trouver_point(t, nom)
    msgs = []
    if opac == 0:   # rond effacé (fond / bordure) : une opacité 0 cacherait aussi le trait, enfant du point
        sh.style(t, rid, sm.SANS_CADRE)
        msgs.append("points invisibles")
    elif opac is not None:
        sh.style(t, rid, {"opacity": opac})
        msgs.append(f"opacité des points {opac}")
    centre = taille_fm / 2
    if p.get("discret"):   # point FM (8 px, flex-grow 1 dans sa case) rapetissé, même centre
        px, op = p["discret"]
        marge = (taille_fm - px) / 2
        sh.style(t, rid, {"flex-grow": 0, "width": px, "height": px, "border-radius": px / 2,
                          "margin-left": marge, "margin-top": marge, "opacity": op})
        msgs.append(f"points {px:g} px, opacité {op:g}")
        centre = px / 2
    if p["trait"] is not None:   # avant la zone : la zone (index 0 ensuite) reste au-dessus pour le survol
        haut, bas, couleur = p["trait"]
        # attributs : FM laisse le point à opacité 0 hors survol (USS) -> trait sur son parent (même taille), sinon
        # il serait invisible avec lui
        support = t.parent[rid] if p.get("trait_sur_parent") else rid
        enfant_absolu(t, sh, support, TRAIT_NOM, centre - 0.5, centre - haut, 1, haut + bas, couleur, survol=False)
        msgs.append(f"trait vertical {haut} px au-dessus, {bas} px en dessous")
    if p["zone"] is not None:
        w, h = p["zone"]
        enfant_absolu(t, sh, rid, ZONE_NOM, centre - w / 2, centre - h / 2, w, h)
        msgs.append(f"zone de survol {w} x {h} px")
    t.finish()
    sh.changed = True
    sh.save()
    o.save_typetree(tt)
    nb._dirty.add(bundle)
    return f"{modele} : " + ", ".join(msgs)


def original(bundle, obj, path_id=None):
    """typetree d'origine (sauvegarde des originaux) de obj (ou de l'objet path_id), ou None"""
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    pid = obj.path_id if path_id is None else path_id
    o = next((x for x in UnityPy.load(backup.backup_path(bundle)).objects if x.path_id == pid), None)
    return o.read_typetree() if o is not None else None


def retirer_point(modele, nom):
    """remet le modèle de point et sa feuille de style intégrée d'origine (seul script à les toucher)"""
    bundle, o, tt = nb.find_vta(modele)
    if tt is None or not os.path.exists(backup.backup_path(bundle)):
        return None
    t, sh = Tree(tt), Styles(bundle, tt)
    rid = trouver_point(t, nom)
    if rid is None or (opacite(t, sh, rid) is None and marque_version(t, rid) is None):
        return None
    orig = original(bundle, o)
    feuille = original(bundle, o, sh.obj.path_id)
    if orig is None or feuille is None:
        return None
    o.save_typetree(orig)
    sh.obj.save_typetree(feuille)
    nb._dirty.add(bundle)
    return f"{modele} : points d'origine remis"


def version_reperes(sh):
    """version de notre règle de repères dans la feuille intégrée, ou None"""
    for rule in sh["m_Rules"]:
        for p in rule["m_Properties"]:
            if p["m_CustomName"] == REPERE_MARQUE:
                return int(sh["floats"][p["m_Values"][0]["valueIndex"]])
    return None


def poser_reperes(r):
    """règle « .classe > .unity-text-element » (trait = bordure gauche des libellés) dans la feuille intégrée du
    modèle, feuille rattachée à la courbe. Seul script sur ce modèle : repart toujours de l'original."""
    if not r.get("actif", True):
        return retirer_reperes(r)
    bundle, o, tt = nb.find_vta(r["modele"])
    if tt is None:
        return f"{r['modele']} introuvable, ignoré"
    sh = Styles(bundle, tt)
    if version_reperes(sh.sh) == VERSION_REPERES:
        return None
    orig = original(bundle, o)
    if orig is not None:
        tt = orig
        sh.sh = original(bundle, o, tt["inlineSheet"]["m_PathID"]) or sh.sh
    t = Tree(tt)
    courbe = next((x for x in t.walk() if t.name(x) == r["nom"]), None)
    if courbe is None:
        return f"{r['modele']} : courbe #{r['nom']} introuvable, ignoré"
    px = lambda v: (3, {"unit": 1, "value": float(v)})   # noqa: E731
    idx = sh.add_rule([
        (131077, "", [px(1)]),                                       # border-left-width
        (458761, "", [(4, r["couleur"])]),                           # border-left-color
        (131101, "", [px(r["haut"])]),                               # padding-top
        (131100, "", [px(r["largeur"])]),                            # padding-right
        (131087, "", [px(0)]),                                       # height (contenu nul : texte sous la boîte)
        (65552, "", [(7, "nowrap")]),                                # white-space
        (327683, "", [(3, {"unit": 2, "value": 50.0}), px(-r["haut"])]),   # translate
        (-1, REPERE_MARQUE, [(2, VERSION_REPERES)]),
    ])
    sh.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{
        "m_Specificity": 21,   # comme FM : 10 par classe + 1
        "m_Selectors": [{"m_Parts": [{"m_Value": r["classe"], "m_Type": 3}], "m_PreviousRelationship": 0},
                        {"m_Parts": [{"m_Value": "unity-text-element", "m_Type": 3}], "m_PreviousRelationship": 1}],
        "ruleIndex": idx}]
    t.elem(courbe)["m_Stylesheets"] = [{"m_FileID": 0, "m_PathID": tt["inlineSheet"]["m_PathID"]}]
    sh.save()
    o.save_typetree(tt)
    nb._dirty.add(bundle)
    return f"{r['modele']} : repères verticaux à chaque mois (essai v{VERSION_REPERES})"


def retirer_reperes(r):
    """remet le modèle et sa feuille intégrée d'origine"""
    bundle, o, tt = nb.find_vta(r["modele"])
    if tt is None or not os.path.exists(backup.backup_path(bundle)):
        return None
    sh = Styles(bundle, tt)
    if version_reperes(sh.sh) is None:
        return None
    orig, feuille = original(bundle, o), original(bundle, o, sh.obj.path_id)
    if orig is None or feuille is None:
        return None
    o.save_typetree(orig)
    sh.obj.save_typetree(feuille)
    nb._dirty.add(bundle)
    return f"{r['modele']} : repères retirés"


def cmd_appliquer():
    noms = guid_noms()
    cible = next((g for g, n in noms.items() if n == POINT), None)
    if cible is None:
        sys.exit(f"{POINT} introuvable : rien fait")
    faits = []
    for bundle, o, tt in (modeles() if COURBES else []):
        if tt["m_Name"] in EXCLURE:
            continue
        change = False
        for e, sd in courbes(tt):
            actuel = [x.get("m_AssetGUID") for x in sd.get("DataPointTemplate") or []]
            nom = noms.get(actuel[0], actuel[0]) if len(actuel) == 1 else ("" if not actuel else None)
            if nom not in REMPLACES or not DONNEES.search(chemin_donnees(sd)):
                continue
            sd["DataPointTemplate"] = [{"m_AssetGUID": cible, "m_SubObjectName": "", "m_SubObjectType": ""}]
            sd["DataPointTemplateBinding"] = "binding"
            if "DataPointTemplate_UxmlAttributeFlags" in sd:
                sd["DataPointTemplate_UxmlAttributeFlags"] = 1
            if "DataPointTemplateBinding_UxmlAttributeFlags" in sd:
                sd["DataPointTemplateBinding_UxmlAttributeFlags"] = 1
            faits.append(f"{tt['m_Name']} {sd.get('name') or ''} ({nom or 'aucun'} -> points) : {chemin_donnees(sd)}")
            change = True
        if change:
            o.save_typetree(tt)
            nb._dirty.add(bundle)
    for p in POINTS:
        msg = agrandir_point(p)
        if msg:
            faits.append(msg)
    for r in REPERES:
        msg = poser_reperes(r)
        if msg:
            faits.append(msg)
    print("\n".join(faits) if faits else "déjà appliqué (aucune courbe à changer)")
    if faits:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    """remet DataPointTemplate / DataPointTemplateBinding d'origine (les autres scripts ne sont pas touchés)"""
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    origines = {}
    remis = []
    for bundle, o, tt in (modeles() if COURBES else []):
        if not os.path.exists(backup.backup_path(bundle)):
            continue
        if bundle not in origines:
            origines[bundle] = {x.path_id: x for x in UnityPy.load(backup.backup_path(bundle)).objects}
        src = origines[bundle].get(o.path_id)
        if src is None:
            continue
        avant = {e["m_Id"]: sd for e, sd in courbes(src.read_typetree())}
        change = False
        for e, sd in courbes(tt):
            a = avant.get(e["m_Id"])
            if a is None:
                continue
            for k in ("DataPointTemplate", "DataPointTemplateBinding", "DataPointTemplate_UxmlAttributeFlags",
                      "DataPointTemplateBinding_UxmlAttributeFlags"):
                if k in a and sd.get(k) != a[k]:
                    sd[k] = a[k]
                    change = True
        if change:
            o.save_typetree(tt)
            nb._dirty.add(bundle)
            remis.append(f"{tt['m_Name']} : points d'origine remis")
    for p in POINTS:
        msg = retirer_point(p["modele"], p["nom"])
        if msg:
            remis.append(msg)
    for r in REPERES:
        msg = retirer_reperes(r)
        if msg:
            remis.append(msg)
    print("\n".join(remis) if remis else "rien à retirer")
    if remis:
        nb.save_all()


def cmd_etat():
    noms = guid_noms()
    for bundle, o, tt in (modeles() if COURBES else []):
        for e, sd in courbes(tt):
            g = [noms.get(x.get("m_AssetGUID"), x.get("m_AssetGUID")) for x in sd.get("DataPointTemplate") or []]
            if DONNEES.search(chemin_donnees(sd)):
                print(f"{tt['m_Name']} {sd.get('name') or ''} : {', '.join(g) or 'aucun point'}")
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
            print("points des graphiques : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

