"""Entraînement > Entraîn. individuel, vue Résumé : bouton « Féliciter les cochés » (à gauche de la roue / Filtre) qui
félicite les joueurs cochés un par un, d'un seul clic, puis se réarme seul.

Partie de entrainement_pouces (appelé par lui, comme pouces_reponse_auto qui répond et ferme chaque conversation) ;
entrainement_individuel_equipes, qui réécrit TeamIndividualTrainingBlock depuis l'original, le rappelle à la fin quand
les pouces sont actifs. Essai essai_feliciter_coches v1 à v6 (2026-10-30), v6 validé en jeu, passé ici en v7 (textes
FR + EN, diagnostic retiré).

Fonctionnement (v6) :
- #TopPanel de TeamIndividualTrainingBlock : BindingVariables (armé, compteur, vu, fini : entiers 0) ;
  · « Féliciter les cochés » (si armé 0) : fini = 0, vu = 1, armé = 1, compteur = 1 ;
  · « En cours… (arrêter) » (si armé 1) : tout à 0 ;
  · liste TICTAC (1 ligne si armé) : SIDelayEvent ; tictac k : vu = 1 puis compteur = k ; mi-tictac : fini = vu ;
  · liste JOUEURS (les `compteur` premiers cochés) : nouvelle ligne LIGNE = vu 0 + FMActionButton Féliciter du joueur,
    gabarit GABARIT = EventTrigger qui envoie l'action à l'affichage (sauf si item.Disabled : déjà félicité) ;
  · liste FIN (1 ligne si fini) : EventTrigger tout à 0 -> bouton réarmé.
- Une variable écrite depuis une ligne doit être un paramètre (facultatif) de son modèle, sinon rien n'est écrit.
- `selectedlist.Count` n'existe pas (vide en jeu) : d'où vu / fini.
Modèles de FM cités par rien, réécrits : DebugDisplayRow (gabarit), DebugNewsRow (ligne), CorruptedFileCell (tictac),
GenericDebugTable (fin).

Historique de l'essai :
v1 (2026-10-30) : FMActionButton Féliciter de FM avec `selectedlist` : le bouton DISPARAÎT dès 2 cochés (action
pour un seul joueur).
v2 : une action par coché, toutes lancées en même temps : FM ne garde qu'UNE conversation, les autres sont perdues.
Depuis, la conversation se répond et se ferme seule (entrainement_pouces > pouces_reponse_auto, ~1 s).
v3 : les cochés un par un, toutes les DELAI secondes.
- #TopPanel de TeamIndividualTrainingBlock : BindingVariables (`uipickerarme`, `uipickerfeliciter` : entiers 0) ;
  · « Féliciter les cochés » (si armé 0) : armé = 1, compteur = 1 ;
  · « Féliciter : fait (réarmer) » (si armé 1) : armé = 0, compteur = 0 ;
  · liste COMPTEUR (WrappedObjectList, 1 premier coché si armé) : sa ligne TICTAC porte 19 SIDelayEvent qui écrivent
    compteur = 2, 3… 20 toutes les DELAI secondes ;
  · liste JOUEURS (les `compteur` premiers cochés) : chaque nouvelle ligne LIGNE = FMActionButton Féliciter du joueur,
    gabarit GABARIT = EventTrigger qui envoie l'action à l'affichage (sauf si item.Disabled : déjà félicité).
v3 vu en jeu le 2026-10-30 : marche (petit chargement entre chaque joueur).
v4 : un seul clic, réarmement seul : sous la rangée, pour n = 0..19, SIVisible(selectedlist.Count == n) >
SIVisible(compteur == n + 1) > EventTrigger armé = 0, compteur = 0 ; + un dernier tictac à MAXI × DELAI (20 cochés et
plus). Le 2e bouton devient « En cours… (arrêter) ».
v4 vue : reste bloqué sur « En cours… ». v5 : paramètre `uipickerarme` ajouté au tictac (le tictac final à 50 s
n'écrivait rien) ; diagnostic « compteur / selectedlist.Count » à droite des boutons.
v5 vue : Count VIDE (n'existe pas sur la sélection), la série continue. v6 : fin sans compter : variables `vu` /
`fini` ; tictac k : vu = 1 puis compteur = k ; une nouvelle ligne joueur (k-ième coché existant) remet vu = 0 ; à
mi-tictac fini = vu ; liste FIN (GenericDebugTable réécrit, 1 ligne si fini = 1) = EventTrigger tout à 0.
Diagnostic « compteur / vu / fini ». v6 VUE : marche.
v9 (2026-10-30) : le bouton était passé à gauche (avant la cale de Kinito, qui pousse sa roue à droite) : posé juste
après la cale.
v10 (2026-10-30) : revenu à gauche en jeu : Kinito, réappliqué sur un écran où le bouton était déjà, repose sa cale
juste avant sa roue, donc après le bouton ; le bouton déjà posé (marque à jour) n'était plus revérifié. Désormais sa
place est revérifiée à chaque passage (placer).

Usage (jeu fermé, normalement par entrainement_pouces) : feliciter_coches.py appliquer [--dry-run] | retirer
"""
import copy
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import langue  # noqa: E402  (textes fixes en français ou en anglais, choix 106)
from arbre import Tree  # noqa: E402
from elements import src_tree, first, typ  # noqa: E402
from notes_installations import (decode_args, encode_args, _enc_varint, visible_model, new_visible,  # noqa: E402
                                 equal_binding, text_static)
from hierarchie_pyramide import evenement_copie  # noqa: E402

MODELE = "TeamIndividualTrainingBlock"
VERSION = 11
NOM = "UIPickerFeliciterCoches"
CLASSE = f"uipicker-feliciter-coches-v{VERSION}{langue.SUFFIXE}"   # autre langue : l'écran est refait
ARME, COMPTEUR = "uipickerarme", "uipickerfeliciter"
VU, FINI = "uipickervu", "uipickerfini"     # v6 : 1 = pas de nouveau joueur depuis le tictac ; copie de VU à mi-tictac
VARIABLES = (ARME, COMPTEUR, VU, FINI)
DELAI = 1.0                                 # secondes entre deux joueurs (v8, demande du joueur ; avant 2,5)
MAXI = 20                                   # const.Twenty : 20 cochés au plus
CONSTANTES = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven",
              "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]
RANGEE = "TopPanel"
SELECTION = "selectedlist"
AVANT = "-TopPanel-actions"                # roue Actions de Kinito (sinon : avant #Filter)
CALE = "-TopPanel-cale"                    # v9 : espace de Kinito qui pousse à droite : se mettre juste après
GABARIT, GUID_GABARIT = "DebugDisplayRow", "6067ae17813c39c4c90a0156afd71797"
LIGNE, GUID_LIGNE = "DebugNewsRow", "7ff681c74cf201743938ee26a042e544"
TICTAC, GUID_TICTAC = "CorruptedFileCell", "f6d899f5dfcdc3c4493ed90cc1e1a037"
FIN, GUID_FIN = "GenericDebugTable", "fbff9df68c88d9a488fae87aa0c19669"
NOM_GABARIT, NOM_LIGNE, NOM_TICTAC, NOM_FIN = (f"{NOM}-{x}-v{VERSION}" for x in ("gabarit", "ligne", "tictac", "fin"))
# v2 : modèles réécrits alors, repris depuis par pouces_reponse_auto : on n'y touche plus
TYPE_PERSONNE = 1145176065
SOURCE_BOUTON, BOUTON = "PlayerReportDevelopmentProgressReportBlock", "PraisePlayerButton"
SOURCE_LISTE_ACTIONS, SOURCE_BOUTON_ACTION = "ActionsListWidget", "GenericActionButtonWidget"
SOURCE_DECLENCHEUR = "SpeakToSidePanel"          # un EventTrigger de FM (événements lancés à l'affichage)
# un SIDelayEvent de FM (m_duration, TransitionEvents), seulement lu et recopié. v11 (MAJ de FM du 2026-11-10) :
# plus dans PlayerRecommendationsMainBlock -> GameCreationGameSummaryScreen (comme les scripts de Kinito) ; 1er trouvé
SOURCES_DELAI = ("GameCreationGameSummaryScreen", "PlayerRecommendationsMainBlock")
SOURCE_LISTE = "TrainingUnitInfo"                # WrappedObjectList #SmalList (liste, nombre)
SOURCE_VARIABLES = "SpeakToSenderMessageButtons"  # BindingVariables à variable entière
TEXTE_ARMER = langue.texte("Féliciter les cochés", "Praise selected")
TEXTE_EN_COURS = langue.texte("En cours… (arrêter)", "Running… (stop)")


def sans_style(t, racine):
    for r in t.walk(racine):
        t.elem(r)["m_RuleIndex"] = -1


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


def chemin_arg(chemin):
    b = chemin.encode()
    return b"\x01" + _enc_varint(len(b)) + b


def copie(t, s, r, parent, index=None):
    """élément r du modèle s recopié sous parent, sans ses enfants"""
    c = t.clone(r, parent, index, src=s)
    for k in list(t.children(c)):
        t.remove(k)
    return c


def vider(t):
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    return racine


def evenements(modele, *copies):
    """événements FM « copier source dans cible » à la suite (un seul champ Events)"""
    corps = b""
    for source, cible in copies:
        corps += bytes(evenement_copie(modele, source, cible)["m_bytes"])[4:]
    ev = copy.deepcopy(modele)
    ev["m_bytes"] = list(bytes([1, 1, 1, len(copies)]) + corps)
    return ev


def liste_n(t, sl, liste, parent, source, nombre, guid, param):
    """liste non virtualisée des `nombre` premiers éléments de `source`, lignes = modèle guid"""
    lst = copie(t, sl, liste, parent)
    sd = t.sd(lst)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": guid, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["ItemParamName"] = param
    f = sd["VisualFuncBinding"] = copy.deepcopy(sd["VisualFuncBinding"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    args[0][1], args[1][1] = chemin_arg(source), chemin_arg(nombre)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.elem(lst)["m_Classes"], t.elem(lst)["m_RuleIndex"] = ["row-direction-normal"], -1
    return lst


def parametre(sd, nom, type_id, facultatif, defaut=""):
    p = copy.deepcopy(sd["Parameters"][0])
    p["name"], p["type"], p["isOptional"] = nom, {"id": type_id}, facultatif
    p["defaultValue"]["m_scopeValue"] = {"m_serializedData": defaut}
    return p


# ---------- les trois modèles réécrits ----------
def construire_gabarit(t):
    sa, sb, se = src_tree(SOURCE_LISTE_ACTIONS), src_tree(SOURCE_BOUTON_ACTION), src_tree(SOURCE_DECLENCHEUR)
    attente = sa and next((k for k in sa.children(sa.tt["m_VisualTree"]["rid"]) if typ(sa, k).endswith("BindingExpect")), None)
    valide = sa and first(sa, lambda r: sa.name(r) == "ActionValid")
    premier = sa and first(sa, lambda r: sa.name(r) == "FirstRemapper")
    bouton = sb and first(sb, lambda r: typ(sb, r).endswith("SIButton") and sb.sd(r).get("Events", {}).get("m_bytes"))
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if None in (attente, valide, premier, bouton, decl):
        return ["gabarit : morceaux de FM introuvables"]
    racine = vider(t)
    a = copie(t, sa, attente, racine)
    v = copie(t, sa, valide, a)
    p = copie(t, sa, premier, v)
    actif = copie(t, sa, valide, p)               # SIVisible « pas désactivée » (item.Disabled inversé)
    sd = t.sd(actif)
    sd["name"] = ""
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_direct"]["Path"]["m_path"] = "item.Disabled"
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
    d = copie(t, se, decl, actif)
    t.sd(d)["name"] = ""
    t.sd(d)["Events"] = copy.deepcopy(sb.sd(bouton)["Events"])
    t.sd(d)["Events_UxmlAttributeFlags"] = 1
    nommer(t, a, NOM_GABARIT)
    for r in (a, v, p, actif, d):
        t.elem(r)["m_Classes"] = []
    sans_style(t, racine)
    return [f"gabarit sans clic posé ({GABARIT})"]


def construire_ligne(t):
    s = src_tree(SOURCE_BOUTON)
    src = s and first(s, lambda r: s.name(r) == BOUTON and typ(s, r) == "FM.UI.FMActionButton")
    sv = src_tree(SOURCE_BOUTON)   # un BindingExpect de FM (racine du modèle source)
    attente = sv and next((k for k in sv.children(sv.tt["m_VisualTree"]["rid"]) if typ(sv, k).endswith("BindingExpect")), None)
    if src is None or attente is None:
        return ["ligne : morceaux de FM introuvables"]
    se = src_tree(SOURCE_DECLENCHEUR)
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if decl is None:
        return ["ligne : déclencheur de FM introuvable"]
    racine = vider(t)
    a = copie(t, sv, attente, racine)
    t.sd(a)["Parameters"] = [parametre(t.sd(a), "player", TYPE_PERSONNE, 0), parametre(t.sd(a), VU, 0, 1, "Int|0|")]
    t.elem(a)["m_Classes"] = []
    nommer(t, a, NOM_LIGNE)
    d = copie(t, se, decl, a)          # v6 : nouvelle ligne = un joueur de plus -> vu = 0
    t.sd(d)["name"] = ""
    t.sd(d)["Events"] = evenements(se.sd(decl)["Events"], ("const.Zero", VU))
    t.sd(d)["Events_UxmlAttributeFlags"] = 1
    t.elem(d)["m_Classes"] = []
    b = t.clone(src, a, src=s)
    sb = t.sd(b)
    sb["name"] = ""
    sb["RecordsBinding"], sb["RecordsBinding_UxmlAttributeFlags"] = {"m_path": "player"}, 1
    sb["ActionsListWidget"] = {"m_AssetGUID": GUID_GABARIT, "m_SubObjectName": "", "m_SubObjectType": ""}
    sb["ActionsListWidget_UxmlAttributeFlags"] = 1
    t.elem(b)["m_Classes"] = []
    sans_style(t, racine)
    return [f"ligne posée ({LIGNE}) : Féliciter de FM pour le joueur de la ligne, gabarit sans clic"]


def construire_tictac(t):
    sd_ = delai = None
    for source in SOURCES_DELAI:
        sd_ = src_tree(source)
        delai = sd_ and first(sd_, lambda r: typ(sd_, r).endswith("SIDelayEvent"))
        if delai is not None:
            break
    sv = src_tree(SOURCE_BOUTON)
    attente = sv and next((k for k in sv.children(sv.tt["m_VisualTree"]["rid"]) if typ(sv, k).endswith("BindingExpect")), None)
    se = src_tree(SOURCE_DECLENCHEUR)
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if None in (delai, attente, decl):
        return ["tictac : SIDelayEvent ou paramètres de FM introuvables"]
    racine = vider(t)
    a = copie(t, sv, attente, racine)
    sd = t.sd(a)
    # v5 : les variables écrites doivent être des paramètres (sinon rien n'est écrit)
    sd["Parameters"] = [parametre(sd, "player", TYPE_PERSONNE, 0)] + [parametre(sd, n, 0, 1, "Int|0|") for n in VARIABLES]
    t.elem(a)["m_Classes"] = []
    nommer(t, a, NOM_TICTAC)
    modele = se.sd(decl)["Events"]

    def retard(secondes, *copies):
        d = copie(t, sd_, delai, a)
        t.sd(d)["name"] = ""
        t.sd(d)["m_duration"], t.sd(d)["m_duration_UxmlAttributeFlags"] = float(secondes), 1
        t.sd(d)["TransitionEvents"] = evenements(modele, *copies)
        t.sd(d)["TransitionEvents_UxmlAttributeFlags"] = 1
    for k in range(1, MAXI + 1):
        if k > 1:   # tictac k : vu = 1 puis compteur = k (la ligne du k-ième coché, s'il existe, remet vu à 0)
            retard((k - 1) * DELAI, ("const.One", VU), (f"const.{CONSTANTES[k]}", COMPTEUR))
        retard((k - 0.5) * DELAI, (VU, FINI))   # mi-tictac : fini = vu
    # 20 cochés ou plus : fin de série après le dernier
    retard(MAXI * DELAI, *(("const.Zero", n) for n in VARIABLES))
    sans_style(t, racine)
    return [f"tictac posé ({TICTAC}) : compteur +1 toutes les {DELAI} s"]


def construire_fin(t):
    """v6 : ligne de la liste « fini » (1 ligne si fini = 1) : tout remis à 0 -> bouton réarmé"""
    sv = src_tree(SOURCE_BOUTON)
    attente = sv and next((k for k in sv.children(sv.tt["m_VisualTree"]["rid"]) if typ(sv, k).endswith("BindingExpect")), None)
    se = src_tree(SOURCE_DECLENCHEUR)
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if None in (attente, decl):
        return ["fin : morceaux de FM introuvables"]
    racine = vider(t)
    a = copie(t, sv, attente, racine)
    sd = t.sd(a)
    sd["Parameters"] = [parametre(sd, "player", TYPE_PERSONNE, 0)] + [parametre(sd, n, 0, 1, "Int|0|") for n in VARIABLES]
    t.elem(a)["m_Classes"] = []
    nommer(t, a, NOM_FIN)
    d = copie(t, se, decl, a)
    t.sd(d)["name"] = ""
    t.sd(d)["Events"] = evenements(se.sd(decl)["Events"], *(("const.Zero", n) for n in VARIABLES))
    t.sd(d)["Events_UxmlAttributeFlags"] = 1
    t.elem(d)["m_Classes"] = []
    sans_style(t, racine)
    return [f"fin de série posée ({FIN})"]


# ---------- l'écran ----------
def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r) == NOM]
    for r in old:
        t.remove(r)
    return ["Féliciter des cochés retiré"] if old else []


def placer(t, rangee, v):
    """v10 : juste après la cale de Kinito (sinon avant sa roue / Filtre) ; True si déplacé"""
    kids = t.elem(rangee)["m_Children"]
    enfants = t.children(rangee)
    cale = next((r for r in enfants if t.name(r).endswith(CALE)), None)
    ref = next((r for r in enfants if t.name(r).endswith(AVANT)), None) \
        or next((r for r in enfants if t.name(r) == "Filter"), None)
    if cale is not None:
        voulu = enfants.index(cale) + 1
    elif ref is not None:
        voulu = enfants.index(ref)
    else:
        return False
    i = enfants.index(v)
    if i == voulu or i == voulu - 1 and cale is None:
        return False
    k = kids.pop(i)
    kids.insert(voulu - (1 if i < voulu else 0), k)
    return True


def construire_ecran(t):
    deja = next((r for r in t.walk() if t.name(r) == NOM and CLASSE in (t.elem(r).get("m_Classes") or [])), None)
    if deja is not None:   # v10 : Kinito, réappliqué après nous, repose sa cale après le bouton -> le remettre
        return ["bouton remis juste après la cale de Kinito"] if placer(t, t.parent[deja], deja) else []
    msgs = retirer_ecran(t)
    rangee = first(t, lambda r: t.name(r) == RANGEE)
    btn = first(t, lambda r: typ(t, r).endswith("SIButton") and "buttons-button-secondary-default"
                in (t.elem(r).get("m_Classes") or []))
    txt = btn and next((k for k in t.children(btn) if typ(t, k).endswith("SIText")), None)
    sv, sl = src_tree(SOURCE_VARIABLES), src_tree(SOURCE_LISTE)
    var = sv and first(sv, lambda r: typ(sv, r).endswith("BindingVariables")
                       and any("Int|" in (x.get("m_scopeValue") or {}).get("m_serializedData", "")
                               for x in sv.sd(r).get("ValueVariables") or []))
    liste = sl and first(sl, lambda r: sl.name(r) == "SmalList")
    vs, vis = visible_model()
    if None in (rangee, btn, txt, var, liste, vis):
        return ["rangée, bouton, variables, liste ou visibilité de FM introuvable, ignoré"]
    v = copie(t, sv, var, rangee)
    placer(t, rangee, v)   # juste après la cale de Kinito (sinon le bouton reste à gauche)
    nommer(t, v, NOM)
    t.elem(v)["m_Classes"] = ["row-direction-normal", "align-items-center", CLASSE]
    t.elem(v)["m_RuleIndex"] = -1
    t.sd(v)["ValueVariables"] = [{"m_name": n, "m_scopeValue": {"m_serializedData": "Int|0|"}} for n in VARIABLES]
    t.sd(v)["ValueVariables_UxmlAttributeFlags"] = 1
    modele_b = vs.sd(vis)["Binding"]
    lancer = [("const.Zero", FINI), ("const.One", VU), ("const.One", ARME), ("const.One", COMPTEUR)]
    arreter = [("const.Zero", n) for n in VARIABLES]
    for valeur, texte, copies in ((0, TEXTE_ARMER, lancer), (1, TEXTE_EN_COURS, arreter)):
        boite = new_visible(t, vs, vis, v, None, "", equal_binding(modele_b, ARME, valeur))
        t.elem(boite)["m_RuleIndex"] = -1
        b = t.clone_shallow(btn, boite)
        t.sd(b)["name"] = ""
        t.sd(b)["Events"] = evenements(t.sd(btn)["Events"], *copies)
        t.elem(b)["m_Classes"] = ["buttons-button-primary-default" if valeur == 0 else "buttons-button-secondary-default",
                                  "margin-right-global-gap-regular"]
        x = text_static(t, txt, b, texte)
        t.sd(x)["name"] = ""
    liste_n(t, sl, liste, v, SELECTION, ARME, GUID_TICTAC, "player")
    liste_n(t, sl, liste, v, SELECTION, COMPTEUR, GUID_LIGNE, "player")
    # v6, fin de série : mi-tictac sans nouveau joueur -> fini = 1 -> 1 ligne FIN -> tout à 0
    # (v4 / v5 : `selectedlist.Count` n'existe pas, vide en jeu)
    liste_n(t, sl, liste, v, SELECTION, FINI, GUID_FIN, "player")
    return msgs + [f"bouton « {TEXTE_ARMER} » à côté de Filtre (vue Résumé) : un coché toutes les {DELAI} s "
                   f"({MAXI} au plus)"]


# ---------- commandes ----------
def ouvrir(nom):
    bundle, obj, tt = nb.find_vta(nom)
    return (bundle, obj, tt, Tree(tt)) if tt is not None else None


def enregistrer(bundle, obj, tt, t):
    t.finish()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def a_jour(o, nom):
    return any(o[3].name(r) == nom for r in o[3].walk())


def appliquer():
    msgs, faits = [], 0
    for nom, marque, fn in ((GABARIT, NOM_GABARIT, construire_gabarit), (LIGNE, NOM_LIGNE, construire_ligne),
                            (TICTAC, NOM_TICTAC, construire_tictac), (FIN, NOM_FIN, construire_fin)):
        o = ouvrir(nom)
        if o is None:
            return [f"{nom} introuvable"]
        if a_jour(o, marque):
            continue
        m = fn(o[3])
        msgs += m
        if any("introuvable" in x for x in m):
            return msgs
        enregistrer(*o)
        faits += 1
    o = ouvrir(MODELE)
    m = construire_ecran(o[3]) if o else [f"{MODELE} introuvable"]
    msgs += m
    if m and not any("introuvable" in x for x in m):
        enregistrer(*o)
        faits += 1
    if faits:
        nb.save_all()
    return msgs


def retirer():
    msgs = []
    o = ouvrir(MODELE)
    if o and retirer_ecran(o[3]):
        enregistrer(*o)
        msgs.append("bouton retiré de l'écran")
    for nom in (GABARIT, LIGNE, TICTAC, FIN):
        o = ouvrir(nom)
        if o is None or not any(o[3].name(r).startswith(NOM) for r in o[3].walk()) \
                or not os.path.exists(backup.backup_path(o[0])):
            continue
        orig = next((x for x in UnityPy.load(backup.backup_path(o[0])).objects if x.path_id == o[1].path_id), None)
        if orig is not None:
            o[1].save_typetree(orig.read_typetree())
            nb._dirty.add(o[0])
            msgs.append(f"{nom} remis d'origine")
    if msgs:
        nb.save_all()
    return msgs


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    print("\n".join(fn()) or "déjà appliqué")


if __name__ == "__main__":
    main(sys.argv[1:])
