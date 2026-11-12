"""Carte du monde de la connaissance (2026-11-10, WIP) : Recrutement > tuile « Connaissance du monde » > fenêtre,
une carte au-dessus des onglets Régions / Pays ; chaque pays CONNU (liste Club.NationKnowledgeArray de FM) est
dessiné dans la couleur de son niveau (les mêmes que connaissance_couleurs : couleurs_interface.CONNAISSANCE).

Comment :
- FM n'affiche une image perso que par un NUMÉRO : chargeur d'images (type Continent) -> graphics/pictures/continent/
  <id du pays>/logo. Le skin pose les images (outils\\recrutement\\carte_monde\\<id>.png, fabriquées par notes_claude\\
  carte_monde_fabriquer.py : une par pays, toutes du même cadre, pays en blanc) dans graphics\\DOSSIER + config.xml.
- LIMITE : les pays dont le numéro est aussi celui d'une compétition ne sont pas dessinés (sinon le trophée / logo de
  cette compétition serait remplacé par le pays) : presque toute l'Afrique (ids 5-55) et 17 pays d'Asie (106-122 :
  Chine, Japon, Inde, Iran...). Pas de fond gris des pays inconnus (FM ne donne aucun numéro fixe pour une image de
  fond).
- Fenêtre (RecruitmentWorldKnowledgeTableBlock) : une liste (WrappedObjectList de TeamMeetingBlock) sur
  Club.NationKnowledgeArray, de taille fixe ; chaque pays = modèle LIBRE de FM réécrit (ClubSiteCompetitionsCard, jamais
  affiché par FM) : texte du niveau (fonction de couleur de FM, celle de ClubNationKnowledgeCell : pose la classe
  data_knowledge_level_N, texte rendu invisible) > image du pays (en absolu, au coin : toutes empilées) teintée par
  « .data_knowledge_level_N .CL_PAYS { -unity-background-image-tint-color } ».
- On repart toujours des originaux des 2 modèles (personne d'autre ne les écrit).

Menu Outils FM.bat : 124 (essais / WIP) ; réappliqué par le choix 1.
Usage : carte_monde.py appliquer | retirer | etat | si-actif [--dry-run]
"""
import json
import os
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(ICI), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, no_styles  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402
import stades_photos  # noqa: E402
import couleurs_interface as ci  # noqa: E402
import salle_trophees as st  # noqa: E402  (ouvrir / plain / path_arg / _arguments : mêmes outils)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
LARGEUR = 520            # px : la carte dans la fenêtre (les images font 640 x 249, même rapport)
MARGE_BAS = 12           # px sous la carte
FOND = (1.0, 1.0, 1.0, 0.04)   # fond de la carte (les mers) : blanc très léger
# =====================================================================================================

PAGE = "RecruitmentWorldKnowledgeTableBlock"
PAYS = "ClubSiteCompetitionsCard"                     # modèle libre (jamais affiché par FM)
GUID_PAYS = "5e0c6fe94723b7744876cbe5af98230e"        # son GUID Addressables (modeles_libres_2026-11-05.txt)
TYPE_LIGNE = 1097029710                                # type d'un élément de Club.NationKnowledgeArray
LISTE_FM = "Club.NationKnowledgeArray"
SOURCE_TEXTE = "ClubNationKnowledgeCell"               # SIText #text : fonction de couleur du niveau (classe)
SOURCE_LISTE = ("TeamMeetingBlock", "Players")         # WrappedObjectList de FM
SOURCE_LOGO = "CompetitionLogo"                        # SIImage du chargeur d'images (comp.ObjectLookupData)
TYPE_IMAGE = 11                                        # Continent : graphics/pictures/continent/<id>/logo
ID_MAX_CONTINENT = 7                                   # 1-7 = continents : FM garde ses logos
VERSION = 1
PREFIXE = "UIPickerCarteMonde"
NOM_CARTE = f"{PREFIXE}-v{VERSION}"
NOM_PAYS = f"{PREFIXE}Pays-v{VERSION}"
CL_PAYS = f"uipicker-carte-monde-pays-v{VERSION}"
TEINTE_ID = ci.TEINTE_ID                               # -unity-background-image-tint-color
IMAGES = os.path.join(ICI, "carte_monde")
DOSSIER = "UIPicker Carte du monde"                    # dans graphics
FICHIER = "UIPickerCarte_{id}"
CIBLE = "graphics/pictures/continent/{id}/logo"
MARKER = os.path.join(backup.BACKUP_DIR, "carte_monde.actif")
LARGEUR_IMG, HAUTEUR_IMG = 640, 249
HAUTEUR = round(LARGEUR * HAUTEUR_IMG / LARGEUR_IMG)
for _k, _v in {"width": (131105, 3), "height": (131087, 3), "min-width": (131096, 3), "min-height": (131097, 3),
               "max-width": (131095, 3), "max-height": (131094, 3), "position": (131102, 7), "left": (131089, 3),
               "top": (131104, 3), "color": (65536, 4), "align-self": (131074, 7), "flex-direction": (131083, 7),
               "flex-wrap": (131086, 7), "margin-bottom": (131090, 3), "font-size": (65537, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
typ, first = st.typ, st.first


def _cl(t, r, classes):
    t.elem(r)["m_Classes"] = list(classes)
    t.elem(r)["m_RuleIndex"] = -1


# ---------- un pays (modèle libre réécrit) ----------
def construire_pays(t):
    racine = t.children(t.tt["m_VisualTree"]["rid"])
    expect = next((r for r in racine if typ(t, r) in ("BindingRoot", "BindingExpect")), None)
    s_txt, _ = st.source(SOURCE_TEXTE)
    txt = s_txt and first(s_txt, lambda r: typ(s_txt, r) == "SIText" and b"KnowledgeLevelP" in bytes(
        ((((s_txt.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_inputs") or {})
         .get("m_variable") or {}).get("m_argumentBytes") or b""))
    s_img, _ = st.source(SOURCE_LOGO)
    img = s_img and first(s_img, lambda r: typ(s_img, r) == "SIImage" and any(
        b"comp.ObjectLookupData" in bytes(x["m_argumentBytes"]) for x in st._arguments(s_img.sd(r))))
    manque = [n for n, x in ((f"{PAYS} : paramètre", expect is not None and (t.sd(expect).get("Parameters"))),
                             (SOURCE_TEXTE, txt), (SOURCE_LOGO, img)) if not x]
    if manque:
        return [f"{', '.join(manque)} introuvable(s)"]
    params = t.sd(expect)["Parameters"]
    params[:] = [params[0]]
    params[0]["name"], params[0]["type"] = "binding", {"id": TYPE_LIGNE}
    for k in t.children(expect):
        t.remove(k)
    _cl(t, expect, [])
    # texte du niveau : FM lui pose la classe data_knowledge_level_N ; invisible, il porte l'image (même coin)
    niv = t.clone(txt, expect, None, src=s_txt)
    _cl(t, niv, [])
    t.sd(niv)["name"], t.sd(niv)["name_UxmlAttributeFlags"] = NOM_PAYS, 1
    case = {"position": "absolute", "left": 0, "top": 0, "width": LARGEUR, "height": HAUTEUR, "min-width": LARGEUR,
            "min-height": HAUTEUR}
    t.styles.style(t, niv, {**case, "color": (0, 0, 0, 0), "font-size": 1})
    ref = {"m_FileID": 0, "m_PathID": t.tt["inlineSheet"]["m_PathID"]}   # nos règles de teinte s'y appliquent
    t.elem(niv).setdefault("m_Stylesheets", []).append(ref)
    # image du pays : chargeur de FM, type Continent, sur binding.Nation
    im = t.clone(img, niv, None, src=s_img)
    for k in list(t.children(im)):
        t.remove(k)
    _cl(t, im, [CL_PAYS])
    for x in st._arguments(t.sd(im)):
        args = decode_args(x["m_argumentBytes"])
        for a in args:
            if a[0].endswith(b"GraphicsUtils+ResourceType]"):
                a[1] = TYPE_IMAGE.to_bytes(4, "little")
            elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
                ch = a[1][2:].decode()
                if ch.startswith("comp."):
                    ch = "binding.Nation." + ch[len("comp."):]
                    a[1] = b"\x01" + _enc_varint(len(ch)) + ch.encode()
        x["m_argumentBytes"] = encode_args(args)
    t.styles.style(t, im, case)
    # teinte par niveau : « .data_knowledge_level_N .CL_PAYS » (descendant, comme salle_trophees.regle)
    for classe, couleur in ci.CONNAISSANCE.items():
        idx = t.styles.add_rule([(TEINTE_ID, "", [(4, (*(v / 255 for v in ci.to_rgb(couleur)), 1.0))])])
        t.styles.sh["m_Rules"][idx]["m_ComplexSelectors"] = [{"m_Specificity": 20, "ruleIndex": idx, "m_Selectors": [
            {"m_Parts": [{"m_Value": classe, "m_Type": 3}], "m_PreviousRelationship": 0},
            {"m_Parts": [{"m_Value": CL_PAYS, "m_Type": 3}], "m_PreviousRelationship": 2}]}]
    return [f"pays : image {LARGEUR}x{HAUTEUR} teintée par niveau ({len(ci.CONNAISSANCE)} couleurs)"]


# ---------- la carte (fenêtre) ----------
def construire_carte(t):
    groupe = first(t, lambda r: typ(t, r) == "TabGroup")
    contenu = groupe is not None and first(t, lambda r: t.name(r) == "TabsContent", groupe)
    s_l, _ = st.source(SOURCE_LISTE[0])
    liste_src = s_l and first(s_l, lambda r: s_l.name(r) == SOURCE_LISTE[1] and typ(s_l, r) == "WrappedObjectList")
    manque = [n for n, x in (("TabGroup", groupe), ("#TabsContent", contenu),
                             (f"{SOURCE_LISTE[0]} #{SOURCE_LISTE[1]}", liste_src)) if not x]
    if manque:
        return [f"{PAGE} : {', '.join(manque)} introuvable(s)"]
    w = t.clone(liste_src, groupe, t.children(groupe).index(contenu), src=s_l)
    no_styles(t, w)
    sd = t.sd(w)
    sd["name"], sd["name_UxmlAttributeFlags"] = NOM_CARTE, 1
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_PAYS, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = st.path_arg(sd["VisualFuncBinding"], LISTE_FM)
    sd["ItemParamName"] = "binding"
    t.elem(w)["m_Classes"] = []
    # taille fixe ; les pays (taille 0, image en absolu au coin) sont tous au même point
    t.styles.style(t, w, {"width": LARGEUR, "height": HAUTEUR, "min-width": LARGEUR, "min-height": HAUTEUR,
                          "max-height": HAUTEUR, "flex-shrink": 0, "flex-grow": 0, "flex-direction": "row",
                          "flex-wrap": "nowrap", "overflow": "hidden", "align-self": "center",
                          "margin-bottom": MARGE_BAS, "background-color": FOND})
    return [f"carte {LARGEUR}x{HAUTEUR} au-dessus des onglets ({LISTE_FM})"]


# ---------- images (graphics) ----------
def _ids():
    comps = stades_photos.competitions()
    tous = sorted(int(f[:-4]) for f in os.listdir(IMAGES) if f.endswith(".png") and f[:-4].isdigit())
    return [i for i in tous if i > ID_MAX_CONTINENT and i not in comps], len(tous)


def dossier():
    return os.path.join(stades_photos.graphics(), DOSSIER)


def poser_images():
    g = stades_photos.graphics()
    if not os.path.isdir(g):
        print(f"carte du monde : dossier graphics absent ({g}), carte sans pays")
        return
    ids, total = _ids()
    d = dossier()
    lignes = "\n".join(f'\t\t<record from="{FICHIER.format(id=i)}" to="{CIBLE.format(id=i)}"/>' for i in ids)
    xml = ("<record>\n\t<boolean id=\"preload\" value=\"false\"/>\n\t<boolean id=\"amap\" value=\"false\"/>\n"
           "\t<!-- carte du monde de la connaissance (FM27 Vanilla Enhanced Skin) : refait par le skin -->\n"
           f"\t<list id=\"maps\">\n{lignes}\n\t</list>\n</record>\n")
    if not nb.DRY_RUN:
        os.makedirs(d, exist_ok=True)
        voulus = {FICHIER.format(id=i) + ".png" for i in ids}
        for f in os.listdir(d):
            if f.lower() != "config.xml" and f not in voulus:
                os.remove(os.path.join(d, f))
        for i in ids:
            src, dst = os.path.join(IMAGES, f"{i}.png"), os.path.join(d, FICHIER.format(id=i) + ".png")
            if not os.path.isfile(dst) or os.path.getsize(dst) != os.path.getsize(src):
                shutil.copyfile(src, dst)
        with open(os.path.join(d, "config.xml"), "w", encoding="utf-8") as h:
            h.write(xml)
    print(f"carte du monde : {len(ids)} pays dans {d} ({total - len(ids)} pas dessinés : numéro de compétition)"
          + (" [à blanc]" if nb.DRY_RUN else ""))


def retirer_images():
    d = dossier()
    if os.path.isdir(d):
        if not nb.DRY_RUN:
            shutil.rmtree(d)
        print(f"carte du monde : {d} supprimé" + (" [à blanc]" if nb.DRY_RUN else ""))


# ---------- commandes ----------
def marques(t):
    return [n for n in (t.name(r) for r in t.walk()) if n.startswith(PREFIXE)]


def cmd_appliquer():
    poser_images()
    actuels = [st.ouvrir(m, False) for m in (PAGE, PAYS)]
    if None in actuels:
        print(f"{PAGE} / {PAYS} : introuvable (renommé par une mise à jour ?), ignoré")
        return
    if NOM_CARTE in marques(actuels[0][3]) and NOM_PAYS in marques(actuels[1][3]):
        print(f"{PAGE} : déjà appliqué")
    else:
        travail = [st.ouvrir(m) for m in (PAGE, PAYS)]
        if None in travail:
            print(f"{PAGE} / {PAYS} : pas de sauvegarde d'origine, ignoré")
            return
        msgs = construire_pays(travail[1][3])
        if not any("introuvable" in m for m in msgs):
            msgs += construire_carte(travail[0][3])
        msgs += ["ancienne version remplacée"] if marques(actuels[0][3]) or marques(actuels[1][3]) else []
        for m in msgs:
            print(f"{PAGE} : {m}")
        if any("introuvable" in m for m in msgs):
            print(f"{PAGE} : rien enregistré")
            return
        st.enregistrer(travail)
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    retirer_images()
    actuels = [st.ouvrir(m, False) for m in (PAGE, PAYS)]
    if None in actuels or not (marques(actuels[0][3]) or marques(actuels[1][3])):
        print("carte du monde : rien à retirer")
        return
    travail = [st.ouvrir(m) for m in (PAGE, PAYS)]
    if None in travail:
        print(f"{PAGE} / {PAYS} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return
    st.enregistrer(travail)
    print(f"{PAGE} : carte du monde retirée")


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
        o = st.ouvrir(PAGE, False)
        m = marques(o[3]) if o else []
        print(f"{PAGE} : " + (f"carte du monde ({', '.join(m)})" if m else "sans carte du monde"))
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("carte du monde : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
