"""Réponse automatique de la conversation Féliciter / Critiquer (sujet « Niveau d'entraînement »), partie de
entrainement_pouces (appelée par son appliquer / retirer). Ancien essai essai_reponse_auto (2026-10-30), validé en
jeu en v5 : la 1re réponse part seule, puis « Terminer la conversation » ; la fenêtre se voit ~1 s.
v7 : le titre du sujet reconnu dans les 21 langues du jeu (clé FM 509781 « Training Level », languages.fmf).

Quand on félicite un joueur, FM ouvre une conversation (SpeakToSidePanel > SpeakToSenderMessageButtons) et la
félicitation ne compte qu'à la réponse. On veut que la réponse parte seule, et SEULEMENT dans ce sujet.
v1 (2026-10-30, diagnostic) vu en jeu : les réponses sont des lignes SpeakToMeetingAnswerActionButton (B), sous le
titre de sujet « Niveau d'entraînement » (ligne-titre de SpeakToOptionalActionButton, A : #Header > #SubActions) ;
ActionID 0 et ActionResponseId -1 pour les deux réponses (pas de quoi les distinguer).
v2 (rang de ligne par RowIndexName) vue en jeu : la liste à nous s'affiche (titre reconnu) mais rien ne part (rang
pas transmis, sans doute).
v3 : dans A, après #SubActions (gardée telle quelle), si le titre du sujet (action.ActionTitle) vaut THEME : une liste
invisible (WrappedObjectList de TrainingUnitInfo, BindNItemsFromListWrappedList) des 1 premiers éléments de
action.SubmenuActionsList, lignes = C (modèle de FM cité par rien, réécrit) = paramètres de B (BindingExpect) >
EventTrigger qui envoie à l'affichage l'événement du bouton de B (33,189,103,95). B remis d'origine.
v3 vue en jeu : la réponse PART seule (« Merci de vos mots d'encouragement. »), reste « Terminer la conversation ».
v4 : avant la réponse, le déclencheur copie const.True dans SpeakTo.LaunchedFromQuickAction (ce que fait FM pour une
conversation lancée d'une action rapide, CalendarTool) : FM fermera-t-il seul après la réponse ?
v8 (2026-10-31, U19 : il fallait recliquer le pouce pour une 2e étape « Convaincre ») : le titre de réponse
« Convaincre » (clé FM 529060 « Convince ») reconnu aussi, 21 langues. Choix du joueur : partout où FM le montre.
v9 (2026-10-31) : « Convaincre » retiré (répondait aussi aux joueurs mécontents, prix fixé…) : retour à v7.

Usage seul (jeu fermé) : pouces_reponse_auto.py appliquer [--dry-run] | retirer
"""
import copy
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree  # noqa: E402
from elements import first, typ, src_tree  # noqa: E402
from hierarchie_pyramide import evenement_copie  # noqa: E402
from notes_installations import (decode_args, encode_args, _enc_varint, visible_model, new_visible,  # noqa: E402
                                 SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)

VERSION = 9
RAPIDE = "SpeakTo.LaunchedFromQuickAction"   # allumé par FM pour une conversation d'action rapide
# v5 : la sortie (« Terminer la conversation ») envoyée seule, seulement si la conversation porte cette marque ;
# v5 VUE en jeu : la conversation se ferme seule (visible ~1 s). v6 : sans la ligne de diagnostic « fin auto »
D, GUID_D = "TransferRoomResponsesCard", "5d7994e8af510c747aa2e2a456c2df61"   # cité par rien (2026-10-30)
E = "SpeakToSenderMessageButtons"
SORTIE = "speakto-button-interaction-button-exit"
SORTIES = "Actions.ExitActions"
MARQUE_RAPIDE = "speakto.LaunchedFromQuickAction"
NOM = "UIPickerReponseAuto"
NOM_LISTE, NOM_LIGNE = f"{NOM}-liste-v{VERSION}", f"{NOM}-ligne-v{VERSION}"
NOM_SORTIE, NOM_FIN = f"{NOM}-sortie-v{VERSION}", f"{NOM}-fin-v{VERSION}"
A, B = "SpeakToOptionalActionButton", "SpeakToMeetingAnswerActionButton"
C, GUID_C = "ConversationResponseButton", "fc5f597039a089a4d8d1acf5ee24f1ca"   # cité par rien (2026-10-30)
# titre du sujet (clé FM 509781 « Training Level ») dans les 21 langues du jeu, lu dans languages.fmf le 2026-10-30
# (chinois et japonais : avec leurs espaces de largeur nulle, tels quels)
THEMES = [
    'Antrenman Seviyesi', 'Level Latihan', 'Livello di allenamento', "Niveau d'entra\xeenement",
    'Nivel de entrenamiento', 'N\xedvel de treino', 'Poziom treningu', 'Training Level', 'Trainingsniveau',
    'Treningsniv\xe5', 'Tr\xe4ningsniv\xe5n', 'Tr\xe6ningsniveau',
    'Επίπεδο Προπόνησης',
    'Уровень тренировки',
    'مستوى التدريب',
    'ト​レーニング​レ​ベ​ル',
    '训​练水​平', '훈련 수준']
# v8 avait aussi « Convaincre » (clé FM 529060, 2e étape des U19) : retiré en v9, toute conversation qui le
# proposait (joueur mécontent du prix fixé…) répondait et se fermait seule (retour d'un joueur, 2026-10-31).
# Titres des 21 langues : 'Convaincre', 'Convince', 'Convencer', 'Convinci', 'Overbevis', 'Overtuigen', 'Przekonaj',
# 'Überzeugen', 'Övertyga', 'İkna Et', 'Yakinkan', 'Πειστικός', 'Πειστική', 'Убедить', 'إقناع', '説得す​る​', '说​服', '설득'
TITRE = "action.ActionTitle"
LISTE_REPONSES = "action.SubmenuActionsList"
SOURCE_DECLENCHEUR = "SpeakToSidePanel"
SOURCE_LISTE = "TrainingUnitInfo"   # WrappedObjectList #SmalList (liste, nombre)


# ---------- outils ----------
def original_tt(bundle, obj):
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    o = next((x for x in UnityPy.load(backup.backup_path(bundle)).objects if x.path_id == obj.path_id), None)
    return o.read_typetree() if o is not None else None


def ouvrir(modele, depart_original=False):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    if depart_original:
        tt = original_tt(bundle, obj) or tt
    return bundle, obj, tt, Tree(tt)


def enregistrer(bundle, obj, tt, t):
    t.finish()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def a_nous(t):
    return any(t.name(r).startswith(NOM) for r in t.walk())


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


def texte_visible(theme):
    """liaison « visible si action.ActionTitle == theme », d'après la fonction texte de FM"""
    s, vis = visible_model(SOURCE_TEXTE_EGAL, FN_TEXTE_EGAL)
    if vis is None:
        return None, None, None
    b = copy.deepcopy(s.sd(vis)["Binding"])
    args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a in args:
        if a[0] == b"SI.VisualScripting.StringVisualArg":
            v = theme.encode()
            a[1] = b"\x01" + _enc_varint(len(v)) + v
        elif a[0] == b"SI.VisualScripting.BooleanVisualArg":
            a[1] = b"\x00"   # FM : 1 = visible si différent
        elif a[0].startswith(b"SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]"):
            p = TITRE.encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
    b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    return s, vis, b


# ---------- C : paramètres de B > déclencheur (la réponse part dès que la ligne existe) ----------
def construire_c(t):
    ob = ouvrir(B, depart_original=True)   # B d'origine (pas une version retouchée)
    sb = ob and ob[3]
    se = src_tree(SOURCE_DECLENCHEUR)
    attente = sb and next((k for k in sb.children(sb.tt["m_VisualTree"]["rid"]) if typ(sb, k).endswith("BindingExpect")), None)
    bouton = sb and first(sb, lambda r: sb.name(r) == "StandardButton" and typ(sb, r).endswith("SIButton"))
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if None in (attente, bouton, decl):
        return ["ligne de réponse (B), bouton ou déclencheur de FM introuvable"]
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    a = t.clone(attente, racine, src=sb)
    for k in list(t.children(a)):
        t.remove(k)
    nommer(t, a, NOM_LIGNE)
    d = t.clone(decl, a, src=se)
    for k in list(t.children(d)):
        t.remove(k)
    t.sd(d)["name"] = ""
    reponse = bytes(sb.sd(bouton)["Events"]["m_bytes"])
    rapide = bytes(evenement_copie(sb.sd(bouton)["Events"], "const.True", RAPIDE)["m_bytes"])
    if reponse[:4] != b"\x01\x01\x01\x01" or rapide[:4] != b"\x01\x01\x01\x01":
        return ["événements de FM d'une autre forme : introuvable"]
    ev = copy.deepcopy(sb.sd(bouton)["Events"])
    ev["m_bytes"] = list(b"\x01\x01\x01\x02" + rapide[4:] + reponse[4:])   # 2 événements : action rapide, réponse
    t.sd(d)["Events"] = ev
    t.sd(d)["Events_UxmlAttributeFlags"] = 1
    for r in t.walk(racine):
        t.elem(r)["m_RuleIndex"] = -1
    return [f"ligne {C} : conversation marquée « action rapide », puis la réponse de la ligne part seule"]


# ---------- A : liste invisible de la 1re réponse, dans le sujet (un SIVisible par langue) ----------
def construire_a(t):
    sous = first(t, lambda r: t.name(r) == "SubActions" and typ(t, r).endswith("StreamedObjectList"))
    s_eq, vis_eq, _ = texte_visible(THEMES[0])
    sl = src_tree(SOURCE_LISTE)
    liste = sl and first(sl, lambda r: sl.name(r) == "SmalList")
    if None in (sous, vis_eq, liste):
        return ["liste des réponses (#SubActions), fonction texte ou liste de FM introuvable"]
    parent = t.parent[sous]
    i = t.children(parent).index(sous) + 1
    for n, theme in enumerate(THEMES):
        oui = new_visible(t, s_eq, vis_eq, parent, i + n, NOM_LISTE if n == 0 else "", texte_visible(theme)[2])
        t.elem(oui)["m_RuleIndex"] = -1
        lst = t.clone(liste, oui, src=sl)
        for k in list(t.children(lst)):
            t.remove(k)
        sd = t.sd(lst)
        sd["name"] = ""
        sd["ItemTemplate"] = {"m_AssetGUID": GUID_C, "m_SubObjectName": "", "m_SubObjectType": ""}
        sd["ItemParamName"] = "action"
        f = sd["VisualFuncBinding"] = copy.deepcopy(sd["VisualFuncBinding"])
        args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
        for a, chemin in zip(args, (LISTE_REPONSES, "const.One")):
            p = chemin.encode()
            a[1] = b"\x01" + _enc_varint(len(p)) + p
        f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        t.elem(lst)["m_Classes"], t.elem(lst)["m_RuleIndex"] = [], -1
    return ["sujet « Niveau d'entraînement » (toutes les langues du jeu) : 1re réponse envoyée seule (liste invisible)"]


# ---------- v5 : D = paramètres du bouton de sortie > déclencheur ; E : la 1re sortie envoyée si action rapide ----------
def construire_d(t):
    os_ = ouvrir(SORTIE, depart_original=True)
    ss = os_ and os_[3]
    se = src_tree(SOURCE_DECLENCHEUR)
    attente = ss and next((k for k in ss.children(ss.tt["m_VisualTree"]["rid"]) if typ(ss, k).endswith("BindingExpect")), None)
    bouton = ss and first(ss, lambda r: ss.name(r) == "StandardButton" and typ(ss, r).endswith("SIButton"))
    decl = se and first(se, lambda r: typ(se, r).endswith("EventTrigger"))
    if None in (attente, bouton, decl):
        return ["bouton de sortie ou déclencheur de FM introuvable"]
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    a = t.clone(attente, racine, src=ss)
    for k in list(t.children(a)):
        t.remove(k)
    nommer(t, a, NOM_SORTIE)
    d = t.clone(decl, a, src=se)
    for k in list(t.children(d)):
        t.remove(k)
    t.sd(d)["name"] = ""
    t.sd(d)["Events"] = copy.deepcopy(ss.sd(bouton)["Events"])
    t.sd(d)["Events_UxmlAttributeFlags"] = 1
    for r in t.walk(racine):
        t.elem(r)["m_RuleIndex"] = -1
    return [f"ligne {D} : « Terminer la conversation » part seul"]


def construire_e(t):
    sortie = first(t, lambda r: typ(t, r).endswith("StreamedObjectList")
                   and (t.binding(r) or "").lower() == SORTIES.lower())
    cache = first(t, lambda r: t.name(r) == "HideBubbles" and typ(t, r).endswith("SIVisible"))
    sl = src_tree(SOURCE_LISTE)
    liste = sl and first(sl, lambda r: sl.name(r) == "SmalList")
    if None in (sortie, cache, liste):
        return ["liste des sorties, SIVisible, texte ou liste de FM introuvable"]
    parent = t.parent[sortie]
    i = t.children(parent).index(sortie) + 1
    v = t.clone_shallow(cache, parent, i)
    nommer(t, v, NOM_FIN)
    sd = t.sd(v)
    sd["InvertDirectBinding"] = 0
    sd["Binding"] = copy.deepcopy(sd["Binding"])
    sd["Binding"]["m_direct"]["Path"]["m_path"] = MARQUE_RAPIDE
    t.elem(v)["m_Classes"], t.elem(v)["m_RuleIndex"] = [], -1
    lst = t.clone(liste, v, src=sl)
    for k in list(t.children(lst)):
        t.remove(k)
    sd = t.sd(lst)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_D, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["ItemParamName"] = "action"
    f = sd["VisualFuncBinding"] = copy.deepcopy(sd["VisualFuncBinding"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    for a, chemin in zip(args, (SORTIES, "const.One")):
        p = chemin.encode()
        a[1] = b"\x01" + _enc_varint(len(p)) + p
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.elem(lst)["m_Classes"], t.elem(lst)["m_RuleIndex"] = [], -1
    return ["fin de conversation : 1re sortie envoyée seule si la conversation est marquée « action rapide »"]


# ---------- commandes ----------
def appliquer():
    msgs, faits = [], 0
    ob = ouvrir(B)
    if ob and a_nous(ob[3]):   # diagnostic v1 : B remis d'origine
        o = ouvrir(B, depart_original=True)
        enregistrer(*o)
        msgs.append(f"{B} remis d'origine (diagnostic v1 retiré)")
        faits += 1
    for modele, marque, fn in ((C, NOM_LIGNE, construire_c), (A, NOM_LISTE, construire_a),
                               (D, NOM_SORTIE, construire_d), (E, NOM_FIN, construire_e)):
        o = ouvrir(modele)
        if o is None:
            return msgs + [f"{modele} introuvable"]
        if any(o[3].name(r) == marque for r in o[3].walk()):
            continue
        o = ouvrir(modele, depart_original=True)
        m = fn(o[3])
        msgs += m
        if any("introuvable" in x for x in m):
            break
        enregistrer(*o)
        faits += 1
    if faits:
        nb.save_all()
    return msgs


def retirer():
    msgs = []
    for modele in (A, B, C, D, E):
        o = ouvrir(modele)
        if o is None or not a_nous(o[3]):
            continue
        enregistrer(*ouvrir(modele, depart_original=True))
        msgs.append(f"{modele} remis d'origine")
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
