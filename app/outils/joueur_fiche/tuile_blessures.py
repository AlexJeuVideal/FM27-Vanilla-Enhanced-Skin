"""Tuile Historique des blessures de FM (InjuryHistoryTile_4x2, mise à la place d'Entraînement dans la fiche par
fiche_ordre_tuiles v10) : sous le % manqué, la liste de TOUTES les blessures du joueur (au lieu de la dernière seule),
chaque ligne = la ligne « Dernière blessure » de FM (date | blessure | pastille de durée). Aussi visible dans
Condition physique (même tuile de FM). v5 : pastille orange / rouge selon la durée ; v6 : pas en mode Large.
(2026-11-13, le joueur ; ex-essais\\essai_tuile_blessures v3, VALIDÉ en jeu Medium + Small, Large pas vu.)

v1 : tableau de l'historique complet de FM recopié -> colonnes à largeurs de FM, tout coupé (« 24/0… », vu en jeu).
v2 : liste (StreamedObjectList de la tuile Carrière) + modèle de ligne = MedicalCentreSeasonSummaryInjuryHistoryTable
Block réécrit (tuile « Injury History iOS » de FM : seulement dans le jeu de tuiles du Centre médical, sans nom ni
place dans une composition PC) : ligne de la tuile, chemins player.LastInjury.X -> injury.X.

Usage (jeu fermé) : tuile_blessures.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import PROPRIETES  # noqa: E402
from elements import first, typ, copy_usings, move  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402  (modèle d'origine + sa feuille de style)
from notes_installations import decode_args, encode_args, make_binding  # noqa: E402

for _k, _v in {"height": (131087, 3), "margin-top": (131093, 3), "text-overflow": (196609, 7),
               "white-space": (65552, 7), "font-size": (65537, 3), "color": (65536, 4)}.items():
    PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES
# =====================================================================================================
H_LIGNE = 26      # px : ligne de blessure
MAX_ECART = 2     # px : espace au-dessus de la liste
# v4 (2026-11-13, le joueur, capture Medium : « % matchs manqu… », « Une blessur… » ; « réduis la taille pour que ça
# rentre ») : tailles de texte en px, par classe de FM (en-tête : heading-md / body-md ; lignes : body-sm)
TAILLE_ENTETE = {"heading-md": 14, "body-md": 11, "body-sm": 11}
TAILLE_LIGNE = 11     # date, blessure
TAILLE_PASTILLE = 10  # durée
# v5 (2026-11-13, le joueur : « couleur très légère sur l'encadré des jours, orange pour les petites, rouge pour les
# grosses ») : pastille aux teintes « soft » de FM selon injury.InjuryDurationDays (colonne Temps d'arrêt de FM)
SEUIL_ROUGE_JOURS = 28   # jours : < seuil = orange, >= seuil = rouge
# v7 (vu en jeu : « trop rouge, galère à voir » -> « le texte en blanc ») : texte blanc, fond = teinte légère (style
# intégré, passe avant la classe soft de FM) ; le bord garde la couleur de FM
TEXTE_PASTILLE = (1, 1, 1, 1)
FOND_PASTILLE = {"orange": (0.95, 0.55, 0.15, 0.22), "red": (0.90, 0.22, 0.22, 0.22)}
# v8 (vu en jeu : « 4 semaines » sur 2 lignes, « 9 jour(s) (Blessure en cours) » qui déborde) : pastille sur 1 ligne,
# largeur max, coupée en « … »
LARGEUR_PASTILLE = 76  # px
# v9 (le joueur : « met la plus récente en haut ») : FM ne donne la liste que de la plus ancienne à la plus récente
# (pas de liste inverse, SortBinding = objet de tri des recherches) -> liste retournée (scale 1 -1) et chaque ligne
# aussi (texte à l'endroit). Défauts possibles : peu de blessures = collées en bas, molette inversée
RETOURNER = True
ID_SCALE = 327681      # StylePropertyId Scale (lu dans les feuilles de FM : « 1.5 1.5 »)
# v10 (vu en jeu : 3 blessures collées en bas, « cale ça sous le séparateur ») : hauteur de la liste = nombre de
# blessures (copies de la liste dans des SIVisible sur player.InjuriesHistoryCount) jusqu'à LIGNES_FIXES, au-delà toute
# la place ; liste amenée sur la dernière blessure (ScrollToElementBinding player.LastInjury, ScrollToMode Bottom =
# en haut une fois retournée), sinon la plus récente serait cachée quand ça défile. ListDirection de FM : 0 / 1
# seulement (vertical / horizontal), pas de sens inverse.
LIGNES_FIXES = 4
NOMBRE = "player.InjuriesHistoryCount"
DERNIERE = "player.LastInjury"
SCROLL_BAS = 1         # SI.UI.ScrollToMode : 0 Top, 1 Bottom, 2 Center
# v11 (vu en jeu : barre de défilement même avec 1 blessure) : UnityEngine ScrollerVisibility 0 Auto, 1 Toujours,
# 2 Cachée -> copies à hauteur exacte : cachée ; liste de 5 et plus : auto
BARRE_AUTO, BARRE_CACHEE = 0, 2
# v12 (vu en jeu : « le scroll est à l'envers », liste retournée) : MouseWheelScrollSize négatif (0 de FM = défaut) ;
# une ligne par cran de molette
MOLETTE = -float(H_LIGNE)
# =====================================================================================================

TUILE = "InjuryHistoryTile_4x2"
LIGNE = "MedicalCentreSeasonSummaryInjuryHistoryTableBlock"   # modèle « iOS » de FM réécrit en ligne
GUID_LIGNE = "c33f49b1eb5de344ba42d7072cf1ad89"
SOURCE_LISTE = "CareerStatsTile_4x2"
LISTE = "player.InjuriesHistory"
PARAM = "injury"
TYPE_BLESSURE = 929975417            # type des éléments de la liste (fabrique PlayerInjuryTableFactory)
ANCIEN, NOUVEAU = b"player.lastinjury.", b"injury."
FN_VISIBLE = "d52cf0b2ba55c764b9ecda52092aa257"   # BindIntToVisible (opérateur, entier, clé, chemin)
OP_INF, OP_SUP_EGAL = 0, 3                        # ComparisonOperator de FM (<, >=)
DUREE_JOURS = "injury.InjuryDurationDays"         # colonne « time-out » de PlayerInjuryTableFactory
ORANGE, ROUGE = "orange", "red"                   # badges-*-color-<couleur>-soft de FM
# v6 (2026-11-13, le joueur : « en Large tu laisses juste Entraînement, tu la mets pas par-dessus ») : les modes
# d'affichage ne changent pas de composition (même grille) -> règle de visibilité de la fiche (PlayerReport,
# m_gridElementVisiblityFunctions, comme Éligibilité / Prêt de FM) : Blessures visible si
# settings.AdaptiveScalingLevelIndex != 0 (0 = Large) ; cachée, FM montre la config suivante (Entraînement).
# PlayerReport est aussi réécrit par Kinito (révélation des jeunes) : retouché sur place, jamais depuis l'original ;
# relancé après lui (catalogue : ORDRE_SKIN + SUIVANTS)
FICHE = "PlayerReport"
ELEMENT_BLESSURES = "InjuryHistory"               # <ID> de InjuryHistoryTileDescription
MODELE_VISIBILITE = "PlayerTrainingOverview"      # sa règle de FM (d1ea93e2 : opérateur, entier, chemin, nom)
FN_REGLE = "d1ea93e235f63f14ba63dcd5b8ca43e3"
MODE_AFFICHAGE = "settings.AdaptiveScalingLevelIndex"
MODE_LARGE, OP_DIFFERENT = 0, 5
PREFIXE = "UIPickerBlessures"
VERSION = "uipicker-blessures-v12"  # v12 : molette dans le bon sens ; v11 : barre cachée (1-4) / auto ; v10 : hauteur selon le nombre, liste amenée sur la dernière ; v9 : liste retournée (plus récente en haut) ; v8 : pastille sur 1 ligne, largeur max, « … » ; v7 : texte blanc, fond léger ; v5 : pastille orange / rouge selon la durée ; v4 : textes plus petits (voir TAILLE_*) ; v3 (vu en jeu, Medium : « % matchs manqués » sur 2 lignes par-dessus le
                                    # titre, nom de la blessure sous la pastille) : textes sur 1 ligne coupés en « … »,
                                    # pastille jamais rétrécie
COUPE = {"flex-shrink": 1, "min-width": 0, "overflow": "hidden", "text-overflow": "ellipsis", "white-space": "nowrap"}
RETRECIT = {"flex-grow": 1, "flex-shrink": 1, "min-width": 0, "overflow": "hidden"}
MODELES = [TUILE, LIGNE]
MARKER = os.path.join(backup.BACKUP_DIR, "tuile_blessures.actif")
SANS_FONCTION = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                 "m_outputs": {"m_variable": {"m_argumentBytes": []}}}


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def a_jour(t):
    return any(VERSION in (t.elem(m).get("m_Classes") or []) for m in marques(t))


def _rechemine_octets(val):
    """chaînes préfixées par leur longueur (1 octet) : player.LastInjury.X -> injury.X"""
    out = bytearray(val)
    i = 0
    while True:
        j = bytes(out).lower().find(ANCIEN, i)
        if j < 1:
            return bytes(out)
        n = out[j - 1]
        s = bytes(out[j:j + n])
        s2 = NOUVEAU + s[len(ANCIEN):]
        out[j - 1:j + n] = bytes([len(s2)]) + s2
        i = j + len(s2)


def _rechemine(d):
    """tous les chemins d'une donnée sérialisée (direct et arguments des fonctions)"""
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "m_path" and isinstance(v, str) and v.lower().startswith(ANCIEN.decode()):
                d[k] = NOUVEAU.decode() + v[len(ANCIEN):]
            elif k == "m_argumentBytes" and v and ANCIEN in bytes(v).lower():
                args = decode_args(v)
                for a in args:
                    a[1] = _rechemine_octets(a[1])
                d[k] = encode_args(args)
            else:
                _rechemine(v)
    elif isinstance(d, list):
        for x in d:
            _rechemine(x)


def construire_ligne(t, s):
    """modèle iOS -> BindingExpect(injury) > ligne « Dernière blessure » de la tuile (copiée)"""
    attente = first(t, lambda r: typ(t, r).endswith("BindingExpect"))
    date = first(s, lambda r: s.name(r) == "Date_and_Injury")
    if attente is None or date is None:
        return ["modèle de ligne ou ligne de FM introuvable (le jeu a changé ?), ignoré"]
    rang_fm = s.parent[date]
    p = t.sd(attente)["Parameters"]
    if len(p) != 1:
        return ["modèle de ligne inattendu (le jeu a changé ?), ignoré"]
    p[0]["name"], p[0]["type"] = PARAM, {"id": TYPE_BLESSURE}
    p[0]["m_serialisedType"] = 0
    for k in list(t.children(attente)):
        t.remove(k)
    rang = t.clone(rang_fm, attente, src=s)
    copy_usings(t, s, rang_fm)
    t.styles.copy_from(s.styles, t, rang)
    for r in t.walk(rang):
        _rechemine(t.sd(r))
    t.sd(rang)["name"] = PREFIXE + "Ligne"
    t.elem(rang)["m_Classes"] = (t.elem(rang).get("m_Classes") or []) + ["align-items-center", VERSION]
    t.styles.style(t, rang, {"height": H_LIGNE, "min-height": H_LIGNE, "flex-shrink": 0})
    if RETOURNER:
        retourner(t, rang)
    # v3 : date et pastille entières, nom de la blessure coupé en « … »
    for r in list(t.walk(rang)):
        n = t.name(r)
        if n in ("Date_and_Injury", "Injury"):
            t.styles.style(t, r, RETRECIT)
        elif n in ("Date", "TimeMissed"):
            t.styles.style(t, r, {"flex-shrink": 0})
    injury = first(t, lambda r: t.name(r) == "Injury" and r in t.closure(rang))
    for r in t.walk(injury) if injury is not None else []:
        if typ(t, r).endswith("SIText"):
            t.styles.style(t, r, COUPE)
    # v4 : textes de la ligne plus petits (pastille de durée un cran de plus)
    for r in list(t.walk(rang)):
        if typ(t, r).endswith("SIText"):
            pastille = "badges-text-color-base" in (t.elem(r).get("m_Classes") or [])
            t.styles.style(t, r, {"font-size": TAILLE_PASTILLE if pastille else TAILLE_LIGNE})
            if pastille:   # v8 : une ligne, « … »
                t.styles.style(t, r, COUPE)
        elif "badges-background-color-base" in (t.elem(r).get("m_Classes") or []):
            t.styles.style(t, r, {"max-width": LARGEUR_PASTILLE, "min-width": 0, "overflow": "hidden"})
    msg_couleur = colorer_pastille(t, s, rang)
    racine = t.parent.get(attente)
    while racine is not None:   # #Block (et au-dessus) : rien de fixe de FM
        t.styles.style(t, racine, {"flex-grow": 1})
        racine = t.parent.get(racine)
    reste = [r for r in t.walk(rang) if ANCIEN.decode() in str(t.sd(r)).lower()]
    return ["ligne de blessure : date | blessure | durée (chemins injury.*)", msg_couleur] + \
        ([f"{len(reste)} chemin(s) player.LastInjury restant(s)"] if reste else [])


def colorer_pastille(t, s, rang):
    """v5 : pastille de durée -> 2 copies, chacune dans un SIVisible de FM (celui de la tuile, BindIntToVisible) :
    orange si injury.InjuryDurationDays < SEUIL_ROUGE_JOURS, rouge sinon"""
    pastille = first(t, lambda r: "badges-background-color-base" in (t.elem(r).get("m_Classes") or [])
                     and r in t.closure(rang))
    visible = first(s, lambda r: typ(s, r).endswith("SIVisible")
                    and t_guid(s.sd(r)) == FN_VISIBLE)
    if pastille is None or visible is None:
        return "pastille ou SIVisible de FM introuvable : pastille laissée grise"
    parent = t.parent[pastille]
    place = t.children(parent).index(pastille)
    for i, (couleur, op) in enumerate(((ORANGE, OP_INF), (ROUGE, OP_SUP_EGAL))):
        v = t.clone(visible, parent, place + i, src=s)
        copy_usings(t, s, visible)
        for k in list(t.children(v)):
            t.remove(k)
        t.sd(v)["Binding"] = make_binding(s.sd(visible)["Binding"], op, [DUREE_JOURS], SEUIL_ROUGE_JOURS)
        t.sd(v)["name"] = f"{PREFIXE}Duree{couleur.capitalize()}"
        t.elem(v)["m_Classes"] = (t.elem(v).get("m_Classes") or []) + [VERSION]
        t.styles.style(t, v, {"flex-shrink": 0})
        copie = t.clone(pastille, v)
        for r in t.walk(copie):
            e = t.elem(r)
            e["m_Classes"] = [c.replace("-color-base", f"-color-{couleur}-soft") if c.startswith("badges-") else c
                              for c in (e.get("m_Classes") or [])]
            if r == copie:
                t.styles.style(t, r, {"background-color": FOND_PASTILLE[couleur]})
            elif typ(t, r).endswith("SIText"):
                t.styles.style(t, r, {"color": TEXTE_PASTILLE})
    t.remove(pastille)
    return f"pastille de durée : orange < {SEUIL_ROUGE_JOURS} j, rouge au-delà (InjuryDurationDays)"


def retourner(t, rid):
    """v9 : style intégré scale: 1 -1 (retourné de haut en bas)"""
    e = t.elem(rid)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    e["m_RuleIndex"] = t.styles.add_rule([p for p in old if p[0] != ID_SCALE] +
                                         [(ID_SCALE, "", [(2, 1.0), (2, -1.0)])])


def t_guid(sd):
    return ((sd.get("Binding") or {}).get("m_visualFunction") or {}).get("m_target", {}).get("m_guid", "")


def construire_tuile(t, s):
    trait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal")
    liste_fm = first(s, lambda r: typ(s, r).endswith("StreamedObjectList"))
    if trait is None or liste_fm is None:
        return ["tuile ou liste de FM introuvable (le jeu a changé ?), ignoré"]
    cadre = t.parent[trait]
    enfants = t.children(cadre)
    apres = enfants[enfants.index(trait) + 1:]
    # [titre « Dernière blessure », dernière blessure (SIVisible), « - » sans blessure (SIVisible)]
    if len(apres) != 3:
        return [f"tuile de FM inattendue ({len(apres)} éléments sous le trait, le jeu a changé ?), ignoré"]
    titre, derniere, _aucune = apres
    liste = t.clone(liste_fm, cadre, enfants.index(trait) + 1, src=s)
    copy_usings(t, s, liste_fm)
    t.styles.copy_from(s.styles, t, liste)
    sd = t.sd(liste)
    sd["name"] = PREFIXE + "Liste"
    sd["Binding"] = {"m_kind": 1, "m_direct": {"Path": {"m_path": LISTE}, "Nullable": 0},
                     "m_visualFunction": SANS_FONCTION}
    sd["RowTemplate"] = {"m_AssetGUID": GUID_LIGNE, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["RowParamName"] = PARAM
    sd["FixedElementSize"] = float(H_LIGNE)
    sd["VerticalScrollerVisibility"], sd["VerticalScrollerVisibility_UxmlAttributeFlags"] = 1, 1
    t.elem(liste)["m_Classes"] = (t.elem(liste).get("m_Classes") or []) + [VERSION]
    e = t.elem(liste)
    if e.get("m_RuleIndex", -1) >= 0:   # hauteur fixe de FM retirée : la liste prend la place qui reste
        garde = [p for p in t.styles.values(e["m_RuleIndex"]) if p[0] != PROPRIETES["height"][0]]
        e["m_RuleIndex"] = t.styles.add_rule(garde)
    t.styles.style(t, liste, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0, "margin-top": MAX_ECART})
    msg_hauteur = []
    if RETOURNER:
        retourner(t, liste)
        sd["ScrollToElementBinding"] = {"m_path": DERNIERE}
        sd["ScrollToMode"] = SCROLL_BAS
        for k in ("ScrollToElementBinding_UxmlAttributeFlags", "ScrollToMode_UxmlAttributeFlags"):
            if k in sd:
                sd[k] = 1
        msg_hauteur = hauteur_selon_nombre(t, cadre, liste)
    t.styles.style(t, cadre, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    # v3 : en-tête (jauge + % manqué + temps total) sur une ligne chacun, coupé en « … » si la tuile est étroite
    entete = enfants[0] if enfants and enfants[0] != trait else None
    for r in (t.walk(entete) if entete is not None else []):
        if r == entete:
            continue
        if typ(t, r).endswith("SIText"):
            t.styles.style(t, r, COUPE)
            taille = next((v for k, v in TAILLE_ENTETE.items() if k in (t.elem(r).get("m_Classes") or [])), None)
            if taille:
                t.styles.style(t, r, {"font-size": taille})
        elif typ(t, r).endswith("SIRadialGauge"):
            t.styles.style(t, r, {"flex-shrink": 0})
        elif typ(t, r) == "UnityEngine.UIElements.VisualElement":
            t.styles.style(t, r, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden"})
    t.remove(titre)
    t.remove(derniere)
    return ["liste de toutes les blessures (ligne « Dernière blessure » de FM pour chacune)"] + msg_hauteur


def _visible(t, modele, parent, index, op, valeur, nom, css):
    """SIVisible (copie de celui de la tuile, vidé) : visible si NOMBRE <op> valeur"""
    v = t.clone(modele, parent, index)
    for k in list(t.children(v)):
        t.remove(k)
    t.sd(v)["Binding"] = make_binding(t.sd(modele)["Binding"], op, [NOMBRE], valeur)
    t.sd(v)["name"] = PREFIXE + nom
    t.elem(v)["m_Classes"] = (t.elem(v).get("m_Classes") or []) + [VERSION]
    t.styles.style(t, v, css)
    return v


def hauteur_selon_nombre(t, cadre, liste):
    """v10 : 1..LIGNES_FIXES blessures -> copie de la liste à la hauteur exacte ; au-delà, la liste prend la place"""
    modele = first(t, lambda r: typ(t, r).endswith("SIVisible") and t_guid(t.sd(r)) == FN_VISIBLE)
    if modele is None:
        return ["SIVisible de FM introuvable : liste en bas si peu de blessures"]
    place = t.children(cadre).index(liste)
    retrecit = {"flex-grow": 0, "flex-shrink": 1, "min-height": 0}
    for n in range(1, LIGNES_FIXES + 1):
        moins = _visible(t, modele, cadre, place + n - 1, OP_INF, n + 1, f"Nombre{n}", retrecit)
        pile = _visible(t, modele, moins, 0, OP_SUP_EGAL, n, f"Nombre{n}Exact", retrecit)
        copie = t.clone(liste, pile)
        t.sd(copie)["name"] = f"{PREFIXE}Liste{n}"
        t.sd(copie)["VerticalScrollerVisibility"] = BARRE_CACHEE
        t.styles.style(t, copie, {"flex-grow": 0, "flex-shrink": 1, "min-height": 0, "height": n * H_LIGNE})
        retourner(t, copie)
    plus = _visible(t, modele, cadre, place + LIGNES_FIXES, OP_SUP_EGAL, LIGNES_FIXES + 1, "NombrePlus",
                    {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    move(t, liste, plus, 0)
    t.sd(liste)["VerticalScrollerVisibility"] = BARRE_AUTO
    t.sd(liste)["MouseWheelScrollSize"] = MOLETTE
    if "MouseWheelScrollSize_UxmlAttributeFlags" in t.sd(liste):
        t.sd(liste)["MouseWheelScrollSize_UxmlAttributeFlags"] = 1
    return [f"hauteur de la liste = nombre de blessures jusqu'à {LIGNES_FIXES}, liste amenée sur la dernière"]


def reglages_fiche(tt):
    """listes de règles de visibilité de la fiche (une par jeu de compositions) qui ont celle d'Entraînement"""
    out = []

    def walk(x):
        if isinstance(x, dict):
            v = x.get("m_gridElementVisiblityFunctions")
            if isinstance(v, list) and any(e.get("m_itemA") == MODELE_VISIBILITE for e in v):
                out.append(v)
            for y in x.values():
                walk(y)
        elif isinstance(x, list):
            for y in x:
                walk(y)
    walk(tt)
    return out


def regle_blessures(modele):
    """règle « Blessures visible si mode d'affichage != Large », d'après celle d'Entraînement (None si inattendue)"""
    f = json.loads(json.dumps(modele["m_itemB"]))
    if f.get("m_target", {}).get("m_guid") != FN_REGLE:
        return None
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if [a[0].rsplit(b".", 1)[-1] for a in args] != [b"GeneralVisualFunction+ComparisonOperator]", b"Int32VisualArg",
                                                     b"BindingPath]", b"StringVisualArg"]:
        return None
    args[0][1] = OP_DIFFERENT.to_bytes(4, "little")
    args[1][1] = MODE_LARGE.to_bytes(4, "little")
    for i, s in ((2, MODE_AFFICHAGE), (3, ELEMENT_BLESSURES)):
        s = s.encode()
        args[i][1] = b"\x01" + bytes([len(s)]) + s
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return {"m_itemA": ELEMENT_BLESSURES, "m_itemB": f}


# 2026-11-19 (le joueur : hors club, « pas besoin de carrousel » à la place d'État d'esprit, où fiche_ordre_tuiles
# v12 met Éligibilité devant) : État d'esprit visible seulement si Éligibilité est cachée. Règle de FM d'Éligibilité
# (37341ce5 : 2 comparaisons ET, ReportMode != 0 et != 2) recopiée sur Happiness avec ReportMode != 1 et < 3 :
# toujours une seule des deux visible (0 / 2 : État d'esprit ; 1, 3+ : Éligibilité)
ELEMENT_ETAT = "Happiness"
ELEMENT_ELIG = "PlayerHomegrownStatus"
ELEMENT_AGENT = "AgentReport"   # <ID> de PlayerAgentReportTileDescription
OP_INF_STRICT = 0


def regle_etat_esprit(modele_elig):
    """règle « État d'esprit visible si ReportMode != 1 et < 3 » d'après celle d'Éligibilité (None si inattendue)"""
    f = json.loads(json.dumps(modele_elig["m_itemB"]))
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    if len(args) != 7 or not args[6][0].endswith(b"StringVisualArg"):
        return None
    args[0][1], args[1][1] = OP_DIFFERENT.to_bytes(4, "little"), (1).to_bytes(4, "little")
    args[3][1], args[4][1] = OP_INF_STRICT.to_bytes(4, "little"), (3).to_bytes(4, "little")
    s = ELEMENT_ETAT.encode()
    args[6][1] = b"\x01" + bytes([len(s)]) + s
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return {"m_itemA": ELEMENT_ETAT, "m_itemB": f}


def etat_esprit_hors_club(listes, retirer):
    """pose / retire la règle d'État d'esprit dans chaque liste ; True si changé"""
    import fiche_ordre_tuiles as fot
    change = False
    for v in listes:
        elig = next((e for e in v if e["m_itemA"] == ELEMENT_ELIG), None)
        etat = next((e for e in v if e["m_itemA"] == ELEMENT_ETAT), None)
        if elig is None or etat is None:
            continue
        voulu = None if (retirer or not fot.ELIG_A_LA_PLACE_ETAT_ESPRIT) else regle_etat_esprit(elig)
        if voulu is None:
            # FM : règle vide (toujours visible)
            voulu = {"m_itemA": ELEMENT_ETAT, "m_itemB": {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {
                "m_argumentBytes": []}}, "m_outputs": {"m_variable": {"m_argumentBytes": []}}}}
        if etat != voulu:
            etat.clear()
            etat.update(voulu)
            change = True
        # v14 de fiche_ordre_tuiles (Large, place du bas à droite) : tuile Agent visible comme Éligibilité (autres
        # clubs : ReportMode != 0 et != 2) ; règle d'Éligibilité recopiée avec le nom de la tuile
        voulu_a = None
        if not retirer and fot.ELIG_A_LA_PLACE_ETAT_ESPRIT:
            voulu_a = json.loads(json.dumps(elig))
            voulu_a["m_itemA"] = ELEMENT_AGENT
            ab = voulu_a["m_itemB"]["m_inputs"]["m_variable"]
            args = decode_args(ab["m_argumentBytes"])
            s = ELEMENT_AGENT.encode()
            args[-1][1] = b"\x01" + bytes([len(s)]) + s
            ab["m_argumentBytes"] = encode_args(args)
        actuel = [e for e in v if e["m_itemA"] == ELEMENT_AGENT]
        if actuel != ([voulu_a] if voulu_a else []):
            v[:] = [e for e in v if e["m_itemA"] != ELEMENT_AGENT] + ([voulu_a] if voulu_a else [])
            change = True
    return change


def fiche_large(retirer=False):
    """v6 : règle de visibilité des Blessures dans PlayerReport (posée / retirée sur place) ; True si changé"""
    o = ouvrir(FICHE)
    if o is None:
        print(f"{FICHE} : introuvable (le jeu a changé ?), Blessures aussi en Large")
        return False
    bundle, obj, tt, t = o
    listes = reglages_fiche(tt)
    if not listes:
        print(f"{FICHE} : règles de visibilité introuvables (le jeu a changé ?), Blessures aussi en Large")
        return False
    change = False
    for v in listes:
        voulu = None if retirer else regle_blessures(next(e for e in v if e["m_itemA"] == MODELE_VISIBILITE))
        if not retirer and voulu is None:
            print(f"{FICHE} : règle d'Entraînement inattendue (le jeu a changé ?), Blessures aussi en Large")
            return False
        actuel = [e for e in v if e["m_itemA"] == ELEMENT_BLESSURES]
        if actuel == ([voulu] if voulu else []):
            continue
        v[:] = [e for e in v if e["m_itemA"] != ELEMENT_BLESSURES] + ([voulu] if voulu else [])
        change = True
    if etat_esprit_hors_club(listes, retirer):
        change = True
        print(f"{FICHE} : État d'esprit " + ("toujours visible (FM)" if retirer else
                                              "caché pour les joueurs hors club (Éligibilité à sa place)"))
    if change:
        obj.save_typetree(tt)
        nb._dirty.add(bundle)
    print(f"{FICHE} : " + ("déjà " if not change else "") +
          ("Blessures aussi en Large (règle retirée)" if retirer else
           "Blessures cachée en mode Large (Entraînement à sa place)"))
    return change


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def cmd_appliquer():
    tuile_src = ouvrir(TUILE, depart_original=True)
    liste_src = ouvrir(SOURCE_LISTE, depart_original=True)
    if tuile_src is None or liste_src is None:
        print("tuile Historique des blessures ou tuile Carrière introuvable (le jeu a changé ?), ignoré")
        return
    travaux = [(LIGNE, lambda t: construire_ligne(t, tuile_src[3])),
               (TUILE, lambda t: construire_tuile(t, liste_src[3]))]
    change = False
    for modele, fn in travaux:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            return
        if a_jour(o[3]):
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            return
        msgs = fn(t)
        for m in msgs:
            print(f"{modele} : {m}")
        if any("ignoré" in m for m in msgs):
            return
        enregistrer(bundle, obj, tt, t)
        change = True
    change = fiche_large() or change
    if change:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    change = False
    for modele in MODELES:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        enregistrer(bundle, obj, tt, t)
        change = True
        print(f"{modele} : remis d'origine")
    change = fiche_large(retirer=True) or change
    if change:
        nb.save_all()
    else:
        print("rien à retirer")


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
        for modele in MODELES:
            o = ouvrir(modele)
            print(f"{modele} : " + ("introuvable" if o is None else "appliqué" if marques(o[3]) else "d'origine"))
        o = ouvrir(FICHE)
        regles = reglages_fiche(o[2]) if o else []
        print(f"{FICHE} : Blessures cachée en Large :",
              "oui" if regles and all(any(e["m_itemA"] == ELEMENT_BLESSURES for e in v) for v in regles) else "non")
        print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")
    elif op == "si-actif":
        if os.path.exists(MARKER):
            cmd_appliquer()
        else:
            print("tuile blessures : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
