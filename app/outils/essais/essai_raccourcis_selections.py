"""ESSAI : raccourcis vers les sélections d'équipe sauvegardées (2026-11-13, demande de Guy / Kinito sur Discord).

But : à droite de « Sélect. rapide », 5 boutons « 1 » à « 5 » = les 5 premières sélections sauvegardées (souhait du
joueur : rien au-delà de 5), sans passer par Sélect. rapide > Gérer sélection d'équipe > Utiliser sélection X.

Lu au mod diag (`selrapide <n> detail`, 2026-11-13) : les choix du menu sont des DynamicReference (RowD = l'action,
4E3T = ses enfants, chargés en code : aucune liaison ne les donne, d'où les v1 / v2 vides). Toutes les entrées
« Utiliser sélection X » ont Event = 1349539155 et ActionResponseValue = leur rang 0..4 (M, M1, M2, 1, 2 chez le
joueur), ActionResponseId -1, ActionID 0, NewsAction -1, DynamicCardId -1, le reste vide / faux.
v3 : dans TacticalPlannerSpeakToActions (bouton Sélect. rapide de l'écran Tactiques, cité par TacticalPlannerHeader),
après le bouton, 5 boutons ; chacun dans un BindingVariables à valeurs fixes (événement, rang N-1, -1, 0, faux) et son
clic = l'événement du menu (SelectionEvents) réécrit vers ces variables.
v4 : v3 = boutons grisés (mod : événement « Initialising », 1 dépendance en attente) ; champs vides -> chemin « null ».
À voir en jeu : un clic sur « 1 » charge-t-il la sélection M (la 1re) ? « 5 » la 5e ? Rien de cassé ?
(v1 / v2 : sonde écran Effectif, PastDraftDropdownRow / AwardDropdownRow réécrits : retirés ici s'ils sont là.)

Outils FM.bat : 124 (essais pas validés, 125 à blanc) ; retrait : 105 / début du choix 1 (catalogue.ESSAIS).
Usage : essai_raccourcis_selections.py appliquer [--dry-run] | retirer [--dry-run]
"""
import copy
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import feliciter_coches as fc  # noqa: E402  (copie, nommer, ouvrir, enregistrer)
from elements import src_tree, first, typ  # noqa: E402
from notes_installations import text_static  # noqa: E402

VERSION = 4
NOM = "UIPickerEssaiRaccourcisSel"
CLASSE = f"uipicker-essai-raccourcis-sel-v{VERSION}"
MODELE = "TacticalPlannerSpeakToActions"     # bouton Sélect. rapide (écran Tactiques), personne d'autre n'y écrit
NOMBRE = 5
EVENEMENT_UTILISER = 1349539155               # Event de « Utiliser sélection X » (lu en jeu)
SOURCE_VARIABLES = "SpeakToSenderMessageButtons"   # un BindingVariables de FM à variable entière
# variables posées sur chaque bouton
V_EV, V_RANG, V_MOINS1, V_ZERO, V_FAUX = "uipselev", "uipselrang", "uipselmoins1", "uipselzero", "uipselfaux"
# champs vides (titre, données, sous-menu…) : chemin « null » de FM (dépendance déjà présente dans l'événement du menu).
# v3 : une variable « Unset » -> l'événement restait « Initialising » (1 dépendance jamais résolue), bouton grisé.
V_VIDE = "null"
# champ de l'action (SelectedAction.X dans l'événement du menu) -> notre variable
CHAMPS = {"event": V_EV, "actionresponsevalue": V_RANG, "actionresponseid": V_MOINS1, "newsaction": V_MOINS1,
          "dynamiccardid": V_MOINS1, "rejectconfirmationevent": V_ZERO, "actionid": V_ZERO,
          "isexitbutton": V_FAUX, "iscontinuematchflowbutton": V_FAUX}
# v1 / v2 (écran Effectif) : à retirer
ANCIEN_ECRAN = "TeamSquadBlock"
ANCIENS_MODELES = ("PastDraftDropdownRow", "AwardDropdownRow")


def reecrire_evenement(ev, renommer):
    """chaînes de l'événement FM réécrites par renommer(s) -> s' (None = inchangée).
    Blocs de chaîne : int32 L, 01 01, n, chaîne (L = n + 3) ; int32 en 5 = longueur totale."""
    b = bytes(ev["m_bytes"])
    if b[:5] != b"\x01" * 5:
        return None
    out, i, delta = bytearray(b[:13]), 13, 0
    while i < len(b):
        if i + 7 <= len(b):
            L = struct.unpack_from("<i", b, i)[0]
            n = b[i + 6]
            if b[i + 4] == 1 and b[i + 5] == 1 and L == n + 3 and i + 7 + n <= len(b) \
                    and all(0x20 <= c < 0x7f for c in b[i + 7:i + 7 + n]):
                s = b[i + 7:i + 7 + n].decode()
                s2 = renommer(s)
                nv = (s if s2 is None else s2).encode()
                out += struct.pack("<i", len(nv) + 3) + b"\x01\x01" + bytes([len(nv)]) + nv
                delta += len(nv) - n
                i += 7 + n
                continue
        out.append(b[i])
        i += 1
    struct.pack_into("<i", out, 5, struct.unpack_from("<i", b, 5)[0] + delta)
    nouveau = copy.deepcopy(ev)
    nouveau["m_bytes"] = list(out)
    return nouveau


def vers_variables(s):
    bas = s.lower()
    if not bas.startswith("selectedaction."):
        return None
    return CHAMPS.get(bas.split(".", 1)[1], V_VIDE)


def evenement_menu(t):
    """SelectionEvents du menu Sélect. rapide (override du dropdown de ce modèle)"""
    for r in t.walk():
        for o in t.elem(r).get("m_SerializedDataOverride") or []:
            d = t.refs[o["m_SerializedData"]["rid"]].get("data") or {}
            ev = d.get("SelectionEvents")
            if isinstance(ev, dict) and b"SelectedAction.Event" in bytes(ev.get("m_bytes") or []):
                return ev
    return None


# ---------- l'écran ----------
def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}
    for r in old:
        if r not in dedans:
            t.remove(r)
    return bool(old)


def construire(t):
    if any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM):
        return []
    retirer_ecran(t)
    rangee = first(t, lambda r: t.name(r) == "DropdownMode")
    btn = first(t, lambda r: t.name(r) == "button" and typ(t, r).endswith("SIButton"))
    txt = btn and next((k for k in t.children(btn) if typ(t, k).endswith("SIText")), None)
    ev = evenement_menu(t)
    sv = src_tree(SOURCE_VARIABLES)
    var = sv and first(sv, lambda r: typ(sv, r).endswith("BindingVariables")
                       and any("Int|" in (x.get("m_scopeValue") or {}).get("m_serializedData", "")
                               for x in sv.sd(r).get("ValueVariables") or []))
    if None in (rangee, btn, txt, ev, var):
        return ["morceaux de FM introuvables (rangée, bouton, texte, événement du menu ou variables)"]
    ev2 = reecrire_evenement(ev, vers_variables)
    if ev2 is None or b"electedAction" in bytes(ev2["m_bytes"]) or b"electedaction" in bytes(ev2["m_bytes"]):
        return ["événement du menu : format inattendu"]
    zone = fc.copie(t, sv, var, rangee)            # dernier de la rangée : à droite de Sélect. rapide
    fc.nommer(t, zone, NOM)
    t.sd(zone)["ValueVariables"] = [{"m_name": V_EV, "m_scopeValue": {"m_serializedData": f"Int|{EVENEMENT_UTILISER}|"}},
                                    {"m_name": V_MOINS1, "m_scopeValue": {"m_serializedData": "Int|-1|"}},
                                    {"m_name": V_ZERO, "m_scopeValue": {"m_serializedData": "Int|0|"}},
                                    {"m_name": V_FAUX, "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
    t.sd(zone)["ValueVariables_UxmlAttributeFlags"] = 1
    t.sd(zone)["ReferenceVariables"] = []
    t.elem(zone)["m_Classes"] = ["row-direction-normal", "align-items-center", "margin-left-global-gap-small", CLASSE]
    t.elem(zone)["m_RuleIndex"] = -1
    for k in range(NOMBRE):
        v = fc.copie(t, sv, var, zone)           # le rang de ce bouton
        t.sd(v)["name"] = ""
        t.sd(v)["ValueVariables"] = [{"m_name": V_RANG, "m_scopeValue": {"m_serializedData": f"Int|{k}|"}}]
        t.sd(v)["ValueVariables_UxmlAttributeFlags"] = 1
        t.sd(v)["ReferenceVariables"] = []
        t.elem(v)["m_Classes"] = ["row-direction-normal"]
        t.elem(v)["m_RuleIndex"] = -1
        b = t.clone_shallow(btn, v)
        t.sd(b)["name"] = ""
        t.sd(b)["Events"], t.sd(b)["Events_UxmlAttributeFlags"] = copy.deepcopy(ev2), 1
        t.elem(b)["m_Classes"] = ["buttons-button-secondary-default", "button-size-medium", "align-items-center",
                                  "margin-left-global-gap-small"]
        t.elem(b)["m_RuleIndex"] = -1
        x = text_static(t, txt, b, str(k + 1))
        t.sd(x)["name"] = ""
    return [f"{NOMBRE} boutons « 1 » à « {NOMBRE} » posés à droite de Sélect. rapide (écran Tactiques)"]


# ---------- v1 / v2 ----------
def remettre(nom):
    o = fc.ouvrir(nom)
    if o is None or not any(o[3].name(r).startswith(NOM) for r in o[3].walk()) \
            or not os.path.exists(backup.backup_path(o[0])):
        return False
    env = UnityPy.load(backup.backup_path(o[0]))
    orig = next((x for x in env.objects if x.path_id == o[1].path_id), None)
    if orig is None:
        return False
    tt = orig.read_typetree()
    o[1].save_typetree(tt)
    pid = tt["inlineSheet"]["m_PathID"]
    feuille = next((x for x in env.objects if x.path_id == pid), None)
    cible = next((x for x in nb.env_of(o[0]).objects if x.path_id == pid), None)
    if feuille is not None and cible is not None:
        cible.save_typetree(feuille.read_typetree())
    nb._dirty.add(o[0])
    return True


def retirer_anciens():
    msgs = []
    o = fc.ouvrir(ANCIEN_ECRAN)
    if o and retirer_ecran(o[3]):
        fc.enregistrer(*o)
        msgs.append("zone d'essai v1 / v2 retirée de l'écran Effectif")
    msgs += [f"{nom} remis d'origine" for nom in ANCIENS_MODELES if remettre(nom)]
    return msgs


# ---------- commandes ----------
def appliquer():
    msgs = retirer_anciens()
    o = fc.ouvrir(MODELE)
    if o is None:
        return msgs + [f"{MODELE} introuvable"]
    m = construire(o[3])
    msgs += m
    if m and not any("introuvable" in x or "inattendu" in x for x in m):
        fc.enregistrer(*o)
    if msgs:
        nb.save_all()
    return msgs


def retirer():
    msgs = retirer_anciens()
    o = fc.ouvrir(MODELE)
    if o and retirer_ecran(o[3]):
        fc.enregistrer(*o)
        msgs.append("boutons retirés de Sélect. rapide")
    if msgs:
        nb.save_all()
    return msgs


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    fn = {"appliquer": appliquer, "retirer": retirer}.get(argv[0] if argv else "")
    if fn is None:
        sys.exit(__doc__)
    print("\n".join(fn()) or "rien à faire")


if __name__ == "__main__":
    main(sys.argv[1:])
