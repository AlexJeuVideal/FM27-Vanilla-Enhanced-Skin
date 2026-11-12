"""Diagnostic du bouton repos : pourquoi le bouton n'est pas là. Né de l'essai essai_repos_diag v1 (2026-11-01).
2026-11-07 (v1.66) : option « repos_bouton » retirée, la zone n'est PLUS posée ; effectif_repos_equipe n'appelle
plus qu'enlever_modeles() et ecran(t, None) (nettoyage chez ceux qui l'avaient). Le reste est gardé pour mémoire.

FM cache l'action d'intensité d'une liste (ou la grise) dès qu'un joueur de la liste ne peut pas la recevoir ; et il ne
la propose pas du tout quand l'entraînement est géré par le staff (U23 vu en jeu ; piste du joueur : responsabilités).
Écran Effectif (TeamSquadBlock), au-dessus du tableau, une zone de diagnostic :
- par liste (LISTES) : son nom + la même action d'intensité de FM que le bouton repos, gabarit DIAG : « OK »
  (proposée), « grisé » (proposée mais grisée : le bouton se cache aussi), rien (cachée par FM) ;
- joueur par joueur (tous les joueurs de PAR_JOUEUR, liste à la ligne de TeamMeetingBlock, sans limite) : nom +
  même action pour ce joueur seul.
Vu en jeu (2026-11-01) : 1re liste OK (blessés rouges et orange absents), les 3 autres « grisé » (blessés dedans) ;
U23 : rien nulle part. Rien n'est lancé (affichage seulement).
v3 : 4 listes de plus (capture de Caen : Freddy Bomo « Int », en sélection, seul « grisé » de la 1re liste).
Modèles de FM cités par rien, réécrits : CompetitionsLeagueTableStagesRow_Default_WithoutArrow (gabarit DIAG),
DebugNewsSocialReaction (ligne d'un joueur).
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
import feliciter_coches as fc  # noqa: E402  (copie, vider, parametre, nommer, sans_style, ouvrir…)
import hierarchie_pyramide as hp  # noqa: E402  (path_arg : liste à la ligne sur un autre chemin)
from elements import src_tree, first, typ, copy_usings  # noqa: E402

MODELE = "TeamSquadBlock"
VERSION = 3   # v2 : passé dans le skin (textes FR / EN) ; v3 : listes sans les internationaux ?
NOM = "UIPickerDiagRepos"
CLASSE = f"uipicker-diag-repos-v{VERSION}{langue.SUFFIXE}"   # autre langue : la zone est refaite
# listes essayées avec l'action d'intensité du bouton repos (la 1re = celle du bouton, v2)
# v3 (2026-11-01, capture de Caen) : un joueur en sélection (« Int ») est dans PlayersAvailableForTraining et grise
# l'action ; noms de global-metadata essayés (propriétaire pas sûr : pas une liste de team = rien d'affiché)
LISTES = ["team.PlayersAvailableForTraining", "team.FilteredPermanentPlayers", "team.FilteredPlayers",
          "team.TeamTraining.TrainingSquad", "team.AvailableFirstTeamPlayers", "team.PlayerListForTrainingChange",
          "team.PlayersAvailableForMentoring", "team.FilteredPlayersNoVirtuals"]
PAR_JOUEUR = "team.PlayersAvailableForTraining"
GABARIT, GUID_GABARIT = "CompetitionsLeagueTableStagesRow_Default_WithoutArrow", "8e0b406092f0df64396e6ead1babd6cf"
LIGNE, GUID_LIGNE = "DebugNewsSocialReaction", "389df3a93cdd24ad9a50c5a202104b14"
NOM_GABARIT, NOM_LIGNE = f"{NOM}-gabarit-v{VERSION}{langue.SUFFIXE}", f"{NOM}-ligne-v{VERSION}"
TYPE_PERSONNE, TYPE_EQUIPE = 1145176065, 1145176088
SOURCE_LISTE, LISTE_SOURCE = "TeamMeetingBlock", "Players"   # WrappedObjectList (à la ligne, sans limite)
LEGENDE = langue.texte(
    "Diagnostic du bouton repos : OK = FM propose l'intensité ; grisé = proposée mais grisée (un joueur ne peut pas) ; "
    "rien = cachée par FM (entraînement géré par le staff ?)",
    "Rest button diagnostic: OK = FM offers the intensity; greyed = offered but greyed out (a player can't); "
    "nothing = hidden by FM (training handled by staff?)")
TEXTE_OK, TEXTE_GRISE = "OK", langue.texte("grisé", "greyed")
TEXTE_JOUEURS = langue.texte("Joueur par joueur", "Player by player")


class Sources:
    def __init__(self, mx):
        self.mx = mx   # morceaux d'effectif_repos_equipe (racine d'actions, SIVisible, 1er élément, intensité)
        s = self.s = src_tree(MODELE)
        # texte de FM (nom de l'équipe, en-tête de l'écran) : modèle des textes
        self.texte = s and first(s, lambda r: typ(s, r).endswith("SIText") and s.binding(r, "TextBinding") == "team.Name")
        self.plain = s and first(s, lambda r: typ(s, r) == "UnityEngine.UIElements.VisualElement"
                                 and not s.elem(r).get("m_TemplateAlias"))
        sw = self.sw = src_tree(SOURCE_LISTE)
        self.liste = sw and first(sw, lambda r: sw.name(r) == LISTE_SOURCE and typ(sw, r).endswith("WrappedObjectList"))

    def ok(self):
        return self.mx.ok() and None not in (self.texte, self.plain, self.liste)


def sans_regles(t, racine):
    for r in t.walk(racine):
        t.elem(r)["m_RuleIndex"] = -1


def texte(t, so, parent, fixe=None, chemin=None):
    """texte de FM recopié : fixe, ou lié à `chemin`"""
    x = t.clone(so.texte, parent, src=so.s)
    xs = t.sd(x)
    xs["name"] = ""
    xs["TextBinding"] = copy.deepcopy(xs["TextBinding"])
    if chemin:
        xs["TextBinding"]["m_kind"] = 1
        xs["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
    else:
        xs["TextBinding"]["m_kind"] = 0
        xs["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        xs["text"], xs["text_UxmlAttributeFlags"], xs["DebugDisplay"] = fixe, 1, fixe
    t.elem(x)["m_Classes"] = ["margin-right-global-gap-small"]
    t.elem(x)["m_RuleIndex"] = -1
    return x


def rangee(t, so, parent):
    r = fc.copie(t, so.s, so.plain, parent)
    t.sd(r)["name"] = ""
    t.elem(r)["m_Classes"] = ["row-direction-normal", "align-items-center"]
    t.elem(r)["m_RuleIndex"] = -1
    return r


def intensite(t, so, parent, records):
    """boutons d'intensité de FM (switch team.IsClub, comme le bouton repos) sur `records`, gabarit DIAG"""
    mx = so.mx
    b = t.clone(mx.intensite, parent, src=mx.si)
    copy_usings(t, mx.si, mx.intensite)
    t.sd(b)["name"] = ""
    sans_regles(t, b)
    t.elem(b)["m_Classes"] = []
    for r in t.walk(b):
        if typ(t, r) == "FM.UI.FMActionButton":
            sd = t.sd(r)
            sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": records}, 1
            sd["ActionsListWidget"] = {"m_AssetGUID": GUID_GABARIT, "m_SubObjectName": "", "m_SubObjectType": ""}
            sd["ActionsListWidget_UxmlAttributeFlags"] = 1
            t.elem(r)["m_Classes"] = []
    return b


# ---------- modèles réécrits ----------
def construire_gabarit(t, so):
    """reçoit `action` : « OK » si son 1er élément (Intensité) est actif, « grisé » s'il est désactivé"""
    mx = so.mx
    racine = fc.vider(t)
    a = fc.copie(t, mx.sa, mx.racine_actions, racine)
    t.elem(a)["m_Classes"] = []
    v = mx.visible(t, a, "action")
    p = mx.premier_de(t, v, "action.Items", "item")
    texte(t, so, mx.visible(t, p, "item.Disabled", inverse=True), TEXTE_OK)
    texte(t, so, mx.visible(t, p, "item.Disabled"), TEXTE_GRISE)
    fc.nommer(t, a, NOM_GABARIT)
    fc.sans_style(t, racine)
    return [f"diagnostic : gabarit posé ({GABARIT})"]


def construire_ligne(t, so):
    """un joueur (`player`) : nom + action d'intensité pour lui seul"""
    mx = so.mx
    racine = fc.vider(t)
    a = fc.copie(t, mx.sa, mx.racine_actions, racine)
    sd = t.sd(a)
    sd["Parameters"] = [fc.parametre(sd, "player", TYPE_PERSONNE, 0), fc.parametre(sd, "team", TYPE_EQUIPE, 1)]
    t.elem(a)["m_Classes"] = []
    r = rangee(t, so, a)
    t.elem(r)["m_Classes"] += ["margin-right-global-gap-regular"]
    texte(t, so, r, chemin="player.Name")
    intensite(t, so, r, "player")
    fc.nommer(t, a, NOM_LIGNE)
    fc.sans_style(t, racine)
    return [f"diagnostic : ligne d'un joueur posée ({LIGNE})"]


# ---------- l'écran ----------
def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}
    for r in old:
        if r not in dedans:
            t.remove(r)
    return bool(old)


def construire_ecran(t, so):
    if any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM):
        return []
    retirer_ecran(t)
    table = first(t, lambda r: t.name(r) == "playertable")
    if table is None:
        return ["diagnostic : tableau des joueurs (#playertable) introuvable"]
    cadre = t.parent[table]
    boite = fc.copie(t, so.s, so.plain, cadre, t.children(cadre).index(table))
    fc.nommer(t, boite, NOM)
    t.elem(boite)["m_Classes"] = ["flex-no-shrink-class", "margin-bottom-16", CLASSE]
    t.elem(boite)["m_RuleIndex"] = -1
    texte(t, so, boite, LEGENDE)
    for chemin in LISTES:
        r = rangee(t, so, boite)
        texte(t, so, r, f"{chemin} :")
        intensite(t, so, r, chemin)
    texte(t, so, boite, f"{TEXTE_JOUEURS} ({PAR_JOUEUR}) :")
    w = t.clone(so.liste, boite, src=so.sw)
    sans_regles(t, w)
    sd = t.sd(w)
    sd["name"] = ""
    sd["ItemTemplate"] = {"m_AssetGUID": GUID_LIGNE, "m_SubObjectName": "", "m_SubObjectType": ""}
    sd["VisualFuncBinding"] = hp.path_arg(sd["VisualFuncBinding"], PAR_JOUEUR)
    sd["ItemParamName"] = "player"
    t.elem(w)["m_Classes"] = ["row-direction-normal", "flex-wrap-class"]
    return ["diagnostic posé au-dessus du tableau de l'écran Effectif"]


# ---------- appelés par effectif_repos_equipe (il enregistre : nb.save_all) ----------
# TeamSquadBlock est ouvert UNE fois, par lui (ecran / retirer_ecran sur son arbre) : un modèle rouvert dans le même
# passage après fc.enregistrer est relu dans son ancien état (vu au banc 2026-11-01 : le bouton retiré revenait)
def remettre(nom):
    """modèle remis d'origine s'il porte nos marques (feuille de style comprise) ; True si fait"""
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


def poser_modeles(so):
    """gabarit DIAG + ligne d'un joueur : (messages, nombre de modèles changés)"""
    msgs, faits = [], 0
    for nom, marque, fn in ((GABARIT, NOM_GABARIT, construire_gabarit), (LIGNE, NOM_LIGNE, construire_ligne)):
        o = fc.ouvrir(nom)
        if o is None:
            return msgs + [f"diagnostic : {nom} introuvable"], faits
        if fc.a_jour(o, marque):
            continue
        if remettre(nom):
            o = fc.ouvrir(nom)
        msgs += fn(o[3], so)
        fc.enregistrer(*o)
        faits += 1
    return msgs, faits


def enlever_modeles():
    """(messages, nombre de modèles changés)"""
    msgs = [f"diagnostic : {nom} remis d'origine" for nom in (GABARIT, LIGNE) if remettre(nom)]
    return msgs, len(msgs)


def ecran(t, so):
    """zone posée sur l'arbre t de TeamSquadBlock (so = Sources), ou retirée (so None) ; messages (vide = rien)"""
    if so is not None:
        return construire_ecran(t, so)
    return ["diagnostic retiré de l'écran Effectif"] if retirer_ecran(t) else []
