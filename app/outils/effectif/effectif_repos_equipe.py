"""Écran Effectif de chaque équipe du club (U19, U23, réserves compris) et Effectif > Vue d'ensemble : bouton icône
repos (icône FM du repos, bulle « Reposer l'équipe ») juste après le calendrier (« Programme des rencontres ») ; un clic
ouvre les jours de repos de FM (1 / 2 / 3 / 4 / 5 / 6 jours, 1 / 2 semaines), la durée choisie est posée à tous
les joueurs dispo pour l'entraînement (blessés sautés), sans rien cocher. Pas de bouton quand FM ne propose pas l'intensité (joueurs en vacances).

Né de l'essai essai_repos_effectif (v1 à v16, 2026-10-30, v15 / v16 validées en jeu ; historique dans l'essai).
Fonctionnement :
- boîte (rangée) après le calendrier (le nôtre, effectif_boutons_entrainement, ou celui de Kinito sur la Vue
  d'ensemble), dans leur condition « équipe du club » : bulle (copie de celle du calendrier, texte fixe) + copie TELLE
  QUELLE des boutons d'intensité de FM pour les cochés (Entraînement > Intensité : TrainingIntensityPlayerTableBlock_6x8,
  BindableSwitchElement team.IsClub > FMActionButton 1684363571 / 895695220) sur `team.FilteredPlayers`, gabarit
  GABARIT ;
- GABARIT (reçoit `action` comme ActionsListWidget) : 1er élément (« Intensité entraînement ») > liste (BindNItems)
  de ses choix, ligne ENFANT ;
- ENFANT (paramètre `item` SANS type : typé « élément d'action », il arrive vide) : commutateur de FM de
  GenericActionButtonWidget (a4dffe7b sur item.ChildList) : sans enfants = rien ; avec enfants (« Aucun travail sur le
  terrain ou en salle de gym ») = son menu de FM (#DropdownButton : les jours ; sa sélection = l'action de FM), au
  style des boutons voisins (buttons-button-base-default), libellé = icône repos.
Modèles de FM cités par rien, réécrits : CompetitionsLeagueTableStagesRow_Wide_WithoutColours (gabarit),
CompetitionsLeagueTableStagesRow_Wide_WithoutArrow (ligne). TeamSquadBlock (propriétaire effectif_boutons_entrainement)
et SquadOverviewTableBlock (effectif_equipes) repartent de l'original : ORDRE_SKIN après eux + SUIVANTS.
Option « repos_bouton » (v1.57 à v1.65, normal / diag) retirée en v1.66 : la zone de diagnostic de repos_diag
n'est plus posée, seulement enlevée chez ceux qui l'avaient (ses leçons sont dans LISTE et l'aide de la tuile).

Usage (jeu fermé) : appliquer [--dry-run] | retirer | etat | si-actif
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
import feliciter_coches as fc  # noqa: E402  (copie, vider, liste_n, parametre, nommer, sans_style, ouvrir…)
import repos_diag  # noqa: E402  (ancienne zone de diagnostic : retirée si elle traîne)
from elements import src_tree, first, typ, copy_usings  # noqa: E402
from notes_installations import decode_args, encode_args  # noqa: E402

MODELES = ["TeamSquadBlock", "SquadOverviewTableBlock"]   # écran Effectif, Effectif > Vue d'ensemble
VERSION = 2   # v2 : liste sans les blessés (avec team.FilteredPlayers, un blessé cachait le bouton)
NOM = "UIPickerReposEquipe"
CLASSE = f"uipicker-repos-equipe-v{VERSION}{langue.SUFFIXE}"   # autre langue : la bulle est refaite
ANCIENS_NOMS = ("UIPickerEssaiRepos",)                         # l'essai (retiré s'il traîne)
# calendrier « Programme des rencontres » : le nôtre (effectif_boutons_entrainement), ou celui de Kinito
APRES = ("UIPickerEquipesEntrainement-programme", "UIPickerKinito-effectif-vue-bouton-programme")
# joueurs dispo pour l'entraînement (sans les blessés : FM cache l'action d'une liste si un joueur ne peut pas) ;
# v1 : team.FilteredPlayers (liste du tableau)
LISTE = "team.PlayersAvailableForTraining"
ICONE = "game-concepts-training-rest_small"      # icône FM du repos (menu Entraînement)
STYLE_BOUTON = "buttons-button-base-default"     # style des boutons voisins
TEXTE_BOUTON = langue.texte("Reposer l'équipe", "Rest the team")
SOURCE_ACTIONS = "ActionsListWidget"             # racine (paramètres du FMActionButton), #ActionValid, #FirstRemapper
SOURCE_MENU = "GenericActionButtonWidget"        # commutateur bouton simple / menu (#DropdownButton)
SOURCE_INTENSITE = "TrainingIntensityPlayerTableBlock_6x8"   # Entraînement > Intensité : boutons pour les cochés
GABARIT, GUID_GABARIT = "CompetitionsLeagueTableStagesRow_Wide_WithoutColours", "27a23efade287344ba5d4f821e843daf"
ENFANT, GUID_ENFANT = "CompetitionsLeagueTableStagesRow_Wide_WithoutArrow", "0a124e8b0f25d324cb13132d9549ab9f"
NOM_GABARIT, NOM_ENFANT = f"{NOM}-gabarit-v{VERSION}", f"{NOM}-ligne-v{VERSION}"
TYPE_ACTION = 1633907817                         # paramètre `action` d'ActionsListWidget
MARKER = os.path.join(backup.BACKUP_DIR, "effectif_repos_equipe.actif")


def a_nous(nom):
    return nom.startswith((NOM,) + ANCIENS_NOMS)


class Morceaux:
    """morceaux de FM recopiés (modèles d'origine)"""

    def __init__(self):
        sa = self.sa = src_tree(SOURCE_ACTIONS)
        self.racine_actions = sa and next((k for k in sa.children(sa.tt["m_VisualTree"]["rid"])
                                           if typ(sa, k).endswith("BindingExpect")), None)
        self.valide = sa and first(sa, lambda r: sa.name(r) == "ActionValid")
        self.premier = sa and first(sa, lambda r: sa.name(r) == "FirstRemapper")
        sm = self.sm = src_tree(SOURCE_MENU)
        self.commutateur = sm and first(sm, lambda r: typ(sm, r).endswith("BindableSwitchElement"))
        sl = self.sl = src_tree(fc.SOURCE_LISTE)
        self.liste = sl and first(sl, lambda r: sl.name(r) == "SmalList")
        si = self.si = src_tree(SOURCE_INTENSITE)
        self.intensite = si and first(si, lambda r: si.name(r) == "BindableSwitchElement"
                                      and typ(si, r).endswith("BindableSwitchElement"))

    def ok(self):
        return None not in (self.racine_actions, self.valide, self.premier, self.commutateur, self.liste,
                            self.intensite)

    def visible(self, t, parent, chemin, inverse=False):
        """SIVisible si `chemin` (non nul / vrai), ou son contraire"""
        v = fc.copie(t, self.sa, self.valide, parent)
        sd = t.sd(v)
        sd["name"] = ""
        sd["Binding"] = copy.deepcopy(sd["Binding"])
        sd["Binding"]["m_direct"]["Path"]["m_path"] = chemin
        if inverse:
            sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
        t.elem(v)["m_Classes"] = []
        return v

    def premier_de(self, t, parent, liste, variable):
        """BindingSetter de FM : `variable` = 1er élément de `liste`"""
        b = fc.copie(t, self.sa, self.premier, parent)
        sd = t.sd(b)
        sd["name"] = ""
        f = sd["BindFunction"] = copy.deepcopy(sd["BindFunction"])
        args = decode_args(f[0]["m_inputs"]["m_variable"]["m_argumentBytes"])
        args[0][1], args[1][1] = fc.chemin_arg(liste), fc.chemin_arg(variable)
        f[0]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        sd["ReferenceVariables"] = copy.deepcopy(sd["ReferenceVariables"])
        sd["ReferenceVariables"][0]["m_name"] = variable
        t.elem(b)["m_Classes"] = []
        return b


def sans_regles(t, racine):
    """éléments copiés d'un autre modèle : leurs règles de style pointent vers une autre feuille"""
    for r in t.walk(racine):
        t.elem(r)["m_RuleIndex"] = -1


# ---------- modèles réécrits ----------
def construire_gabarit(t, mx):
    """reçoit `action` (comme ActionsListWidget) : une ligne ENFANT par choix de son 1er élément (« Intensité
    entraînement ») ; seul « Aucun travail » (qui a des enfants) s'affiche"""
    racine = fc.vider(t)
    a = fc.copie(t, mx.sa, mx.racine_actions, racine)
    t.elem(a)["m_Classes"] = []
    v = mx.visible(t, a, "action")
    p = mx.premier_de(t, v, "action.Items", "item")
    actif = mx.visible(t, p, "item.Disabled", inverse=True)
    lst = fc.liste_n(t, mx.sl, mx.liste, actif, "item.ChildList", "const.Ten", GUID_ENFANT, "item")
    t.elem(lst)["m_RuleIndex"] = -1
    fc.nommer(t, a, NOM_GABARIT)
    fc.sans_style(t, racine)
    return [f"gabarit posé ({GABARIT}) : choix d'intensité de FM"]


def construire_enfant(t, mx):
    """un choix d'intensité (`item`, sans type) : commutateur de FM ; sans enfants = rien, avec enfants (Aucun
    travail) = menu de FM des jours, au style bouton, libellé = icône repos"""
    racine = fc.vider(t)
    a = fc.copie(t, mx.sa, mx.racine_actions, racine)
    sd = t.sd(a)
    sd["Parameters"] = [fc.parametre(sd, "item", 0, 0), fc.parametre(sd, "action", TYPE_ACTION, 1)]
    t.elem(a)["m_Classes"] = []
    c = t.clone(mx.commutateur, a, src=mx.sm)
    copy_usings(t, mx.sm, mx.commutateur)
    t.sd(c)["name"] = ""
    simple = next(k for k in t.children(c) if t.name(k) == "SimpleButton")
    for k in list(t.children(simple)):   # sans enfants : rien
        t.remove(k)
    t.sd(simple)["name"] = ""
    menu = next(r for r in t.walk(c) if typ(t, r).endswith("SIDropdown"))
    style = t.parent[menu]                # SIStyleSetter : classes du menu -> style bouton des voisins
    f = t.sd(style)["BindFunction"] = copy.deepcopy(t.sd(style)["BindFunction"])
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    for x in args:
        if bytes(x[0]).endswith(b"StringVisualArg"):
            x[1] = b"\x01" + bytes([len(STYLE_BOUTON)]) + STYLE_BOUTON.encode()
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    t.elem(menu)["m_Classes"] = ["button-size-medium"]
    libelle = next((k for k in t.children(menu) if t.elem(k).get("m_TemplateAlias")), None)
    chevron = next((k for k in t.children(menu) if "chevron" in t.name(k)), None)
    if libelle is None or chevron is None:
        return ["libellé / chevron du menu de FM introuvables"]
    t.elem(chevron)["m_Classes"] = [ICONE]   # le chevron devient l'icône repos
    t.sd(chevron)["name"] = ""
    t.remove(libelle)
    fc.nommer(t, a, NOM_ENFANT)
    fc.sans_style(t, racine)
    return [f"ligne posée ({ENFANT}) : jours de repos de FM, bouton icône"]


# ---------- les écrans ----------
def retirer_ecran(t):
    old = [r for r in t.walk() if a_nous(t.name(r))]
    dedans = {k for r in old for k in t.walk(r) if k != r}   # enlevés avec leur parent
    for r in old:
        if r not in dedans:
            t.remove(r)
    return ["bouton repos retiré"] if old else []


def bulle_repos(t, modele, parent):
    """bulle « Reposer l'équipe » : copie de celle du calendrier, texte fixe"""
    src = next((k for k in t.children(modele) if typ(t, k).endswith("Tooltip")), None)
    if src is None:
        return None
    bulle = t.clone(src, parent)
    t.sd(bulle)["name"] = ""
    for x in t.walk(bulle):
        if typ(t, x).endswith("SIText"):
            xs = t.sd(x)
            xs["name"] = ""
            xs["TextBinding"] = copy.deepcopy(xs["TextBinding"])
            xs["TextBinding"]["m_kind"] = 0
            xs["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
            xs["text"], xs["text_UxmlAttributeFlags"], xs["DebugDisplay"] = TEXTE_BOUTON, 1, TEXTE_BOUTON
    return bulle


def construire_ecran(t, mx):
    if any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM):
        return []
    msgs = retirer_ecran(t)
    ref = first(t, lambda r: t.name(r) in APRES)
    if ref is None:
        return ["calendrier « Programme des rencontres » (effectif_boutons_entrainement / effectif_equipes) introuvable"]
    plain = first(t, lambda r: typ(t, r) == "UnityEngine.UIElements.VisualElement"
                  and not t.elem(r).get("m_TemplateAlias"))
    boite = t.clone_shallow(plain, t.parent[ref], t.children(t.parent[ref]).index(ref) + 1)
    fc.nommer(t, boite, NOM)
    t.elem(boite)["m_Classes"] = ["row-direction-normal", "align-items-center", CLASSE]
    t.elem(boite)["m_RuleIndex"] = -1
    b = t.clone(mx.intensite, boite, src=mx.si)   # boutons d'intensité de FM, sur tout l'effectif
    copy_usings(t, mx.si, mx.intensite)
    t.sd(b)["name"] = ""
    sans_regles(t, b)
    t.elem(b)["m_Classes"] = ["margin-left-global-gap-regular"]
    for r in t.walk(b):
        if typ(t, r) == "FM.UI.FMActionButton":
            sd = t.sd(r)
            sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": LISTE}, 1
            sd["ActionsListWidget"] = {"m_AssetGUID": GUID_GABARIT, "m_SubObjectName": "", "m_SubObjectType": ""}
            sd["ActionsListWidget_UxmlAttributeFlags"] = 1
            t.elem(r)["m_Classes"] = []
    bulle_repos(t, ref, boite)
    return msgs + [f"bouton repos posé après le calendrier, bulle « {TEXTE_BOUTON} »"]


# ---------- commandes ----------
def remettre(nom):
    """modèle remis d'origine s'il porte nos marques (feuille de style comprise) ; True si fait"""
    o = fc.ouvrir(nom)
    if o is None or not any(a_nous(o[3].name(r)) for r in o[3].walk()) \
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


def appliquer():
    mx = Morceaux()
    if not mx.ok():
        return ["morceaux de FM introuvables (mise à jour de FM ?), rien fait"]
    msgs, faits = [], 0
    for nom, marque, fn in ((GABARIT, NOM_GABARIT, construire_gabarit), (ENFANT, NOM_ENFANT, construire_enfant)):
        o = fc.ouvrir(nom)
        if o is None:
            return msgs + [f"{nom} introuvable"]
        if fc.a_jour(o, marque):
            continue
        if remettre(nom):
            o = fc.ouvrir(nom)
        m = fn(o[3], mx)
        msgs += m
        if any("introuvable" in x for x in m):
            return msgs
        fc.enregistrer(*o)
        faits += 1
    # ancien diagnostic (option « repos_bouton » retirée en v1.66) : enlevé s'il traîne
    m, n = repos_diag.enlever_modeles()
    msgs, faits = msgs + m, faits + n
    for modele in MODELES:
        o = fc.ouvrir(modele)
        m = construire_ecran(o[3], mx) if o else [f"{modele} introuvable"]
        # diag retiré sur le MÊME arbre (un modèle rouvert après enregistrement serait relu dans son ancien état)
        d = repos_diag.ecran(o[3], None) if o and modele == repos_diag.MODELE else []
        msgs += [f"{modele} : {x}" for x in m + d]
        if (m or d) and not any("introuvable" in x for x in m + d):
            fc.enregistrer(*o)
            faits += 1
    if faits:
        nb.save_all()
    return msgs


def retirer():
    msgs = []
    for modele in MODELES:
        o = fc.ouvrir(modele)
        if o is None:
            continue
        m = retirer_ecran(o[3]) + (repos_diag.ecran(o[3], None) if modele == repos_diag.MODELE else [])
        if m:
            fc.enregistrer(*o)
            msgs += [f"{modele} : {x}" for x in m]
    for nom in (GABARIT, ENFANT):
        if remettre(nom):
            msgs.append(f"{nom} remis d'origine")
    msgs += repos_diag.enlever_modeles()[0]
    if msgs:
        nb.save_all()
    return msgs


def etat():
    for modele in MODELES:
        o = fc.ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable")
            continue
        t = o[3]
        a_jour = any(CLASSE in (t.elem(r).get("m_Classes") or []) for r in t.walk() if t.name(r) == NOM)
        pose = any(a_nous(t.name(r)) for r in t.walk())
        print(f"{modele} : " + (f"appliqué ({'à jour' if a_jour else 'ANCIENNE version'}, v{VERSION})" if pose
                                else "d'origine"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    if "--dry-run" in argv:
        nb.DRY_RUN = True
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "si-actif" and not os.path.exists(MARKER):
        print("bouton repos : non activé, rien à faire")
        return
    if op in ("appliquer", "si-actif"):
        msgs = appliquer()
        print("\n".join(f"bouton repos : {m}" for m in msgs) or "bouton repos : déjà appliqué")
        if not nb.DRY_RUN and not any("introuvable" in m for m in msgs):
            with open(MARKER, "w", encoding="utf-8") as f:
                f.write('{"actif": true}')
    elif op == "retirer":
        if os.path.exists(MARKER) and not nb.DRY_RUN:
            os.remove(MARKER)
        print("\n".join(f"bouton repos : {m}" for m in retirer()) or "bouton repos : rien à retirer")
    elif op == "etat":
        etat()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
