"""ESSAI : écran Effectif, bouton « Reposer l'équipe » (icône repos de FM) à droite de « Programme des rencontres » :
un clic coche tout l'effectif et ouvre le menu des durées de FM (1 / 2 / 3 / 4 / 5 / 6 jours, 1 / 2 semaines) pour
les joueurs cochés : FM pose la durée choisie à chacun (comme son clic droit sur plusieurs joueurs cochés).

Historique (2026-10-30) :
v1 : FMActionButton #RestAction de PortalPlayerReportFitnessBlock (action 1265842037, gabarit d'actions 23461237…)
  sur `team.FilteredPlayers` : bouton invisible. v2 : sur `selectedPlayers` : jamais vu (personne n'était coché).
v3 (diagnostic) : par joueur UNE action « Reposer le joueur » + 8 sous-éléments (item.ChildList) ; joueurs sans
  action (FM ne propose pas le repos) : rien.
v4 / v5 : liste de tout l'effectif (WrappedObjectList sans limite, fonction 36a81e80 de FMpediaSectionElement), 1er
  sous-élément lancé seul : nul (ChildList ne se lit que par le SIDropdown de FM, fonction de choix 0f43f251).
v6 : menu de FM (#DropdownButton de GenericActionButtonWidget) avec TriggerSelectionEventOnInit : rien choisi seul ;
  un choix à la main = repos posé.
v7 : diagnostic des codes du choix (pas vu). Le joueur : « un bouton reposer l'équipe et les jours qui pop ».
v8 : bouton icône (copie du bouton « Programme des rencontres », icône FM game-concepts-training-rest_small, bulle
  « Reposer l'équipe »), menus des joueurs empilés (position absolue) : beau rendu mais menu sans réponse ; v9
  (pickingMode Ignore) : idem. v10 : menu du 1er joueur seul + lignes invisibles relançant le choix (variable
  référence `uipickerjour`) : seul le 1er joueur reposé ; et une fois au repos, plus d'action donc plus de menu.
  Leçon : éléments copiés d'autres modèles = m_RuleIndex à -1 (sinon mise en page cassée).
v11 : plus de liste. Clic (fermé) : copie `team.FilteredPlayers` -> `selectedPlayers` (variable de sélection de
  TeamSquadBlock : tout est coché) et repos 1 ; ouvert : FMActionButton Repos sur `selectedPlayers`, gabarit
  GABARIT_MENU = action > 1er élément > pas désactivé > menu de FM (sa sélection = le repos de FM pour les cochés,
  puis repos 0 : refermé ; `uipickerrepos` paramètre facultatif du gabarit). Clic (ouvert) : refermé sans rien.
  À voir : FM accepte-t-il l'action sur tous (joueurs déjà au repos / blessés compris) ?
v11 vue : tout coché, mais PAS de menu (FM refuse dès qu'un coché ne peut pas être reposé : Riemann déjà au repos).
v12 : on coche `team.PlayersAvailableForTraining` (nom trouvé dans global-metadata.dat, avec IsBeingRested,
  FirstTeamPlayersCountAvailableForTraining ; propriétaire à vérifier) : seulement les joueurs reposables, en
  principe (ni blessés, ni absents, ni déjà au repos).
v12 vue : tout coché quand même (la liste garde le joueur au repos : Medioub, repos = « Intensité d'entraînement »
  pour FM). Le joueur : passer par le menu Intensité (Automatique / Semi / Normale / Double / Aucun travail > 1 jour…
  2 semaines / Vacances), modifiable même au repos. v13 : on recopie TEL QUEL le bloc de boutons de FM sous le
  tableau « Intensité individuelle » (TrainingIntensityPlayerTableBlock_6x8 : BindableSwitchElement sur team.IsClub >
  FMActionButton 1684363571 / 895695220 sur `selectedlist`, gabarit ActionsListWidget de FM 3ed4b9e4), branché sur
  `selectedPlayers` ; on coche de nouveau `team.FilteredPlayers`. Notre gabarit de menu n'est plus utilisé.
v13 vue : MARCHE (menu FM « Intensité entraînement » > Aucun travail > 1 jour… posé à tous les cochés). Le joueur :
  aller direct. Sous-menu impossible à ouvrir seul (ChildList illisible hors menu). v14 : plus de bouton à bascule ni
  de cases cochées : les FMActionButton d'intensité (switch team.IsClub) directement sur `team.FilteredPlayers`, gabarit
  GABARIT_MENU = action > 1er élément (« Intensité entraînement ») > menu de FM (#DropdownButton) dont le libellé est
  remplacé par l'icône repos (+ chevron) : clic sur l'icône = le menu d'intensité de FM. Le joueur veut l'icône =
  « Aucun travail » (les jours direct) : sous-menu inatteignable ; donc, AVANT, 2e essai : FMActionButton Repos
  (1265842037, jours directement sous « Reposer le joueur ») sur team.FilteredPlayers, même gabarit (peut-être caché
  par FM si un joueur ne peut pas être reposé).
v14 vue : l'icône intensité marche sans cocher ; l'icône « jours direct » cachée (Medioub au repos). Le joueur : les
  jours au 1er clic, design d'avant (bouton icône carré comme les voisins). v15 : gabarit = action > 1er élément
  (« Intensité entraînement ») > liste (BindNItems, comme la v3) de ses enfants, ligne ENFANT (paramètre `item` SANS
  type : en v3, typé élément d'action, il arrivait vide) = commutateur de FM de GenericActionButtonWidget (fonction
  a4dffe7b sur item.ChildList : 0 = bouton simple, vidé ; 1 = #DropdownButton) : seul « Aucun travail » (enfants =
  les jours) donne un menu, au style bouton (SIStyleSetter : classes buttons-button-base-default), libellé = icône
  repos, sans chevron. Icône « jours direct » retirée.
v15 VUE : MARCHE (jours au 1er clic, tout l'effectif). v16 (demande du joueur) : aussi sur Effectif > Vue
  d'ensemble (SquadOverviewTableBlock), au même endroit : après le calendrier de Kinito
  (#UIPickerKinito-effectif-vue-bouton-programme, dans sa condition « équipe du club »), ou le nôtre (boutons écrits).
  Toutes les équipes du club (U19, U23, réserves) : même condition que les boutons des équipes.

Modèle de FM cité par rien, réécrit : CompetitionsLeagueTableStagesRow_Wide_WithoutColours (gabarit du menu) ;
anciens (remis d'origine) : DebugNewsSocialReaction, CompetitionsLeagueTableStagesRow_Default_WithoutArrow,
…_Wide_WithoutArrow. TeamSquadBlock : propriétaire effectif_boutons_entrainement (repart de l'original : relancer
l'essai après lui) ; icônes / bulles des boutons voisins : Kinito 26.10.
Menu Outils FM.bat (jeu fermé) : 124 ; retiré par 105 / choix 1.
Usage : essai_repos_effectif.py appliquer [--dry-run] | retirer
"""
import copy
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import feliciter_coches as fc  # noqa: E402  (copie, vider, parametre, nommer, sans_style, evenements, ouvrir…)
from elements import src_tree, first, typ, copy_usings  # noqa: E402
from notes_installations import visible_model, new_visible, equal_binding, decode_args, encode_args  # noqa: E402

MODELES = ["TeamSquadBlock", "SquadOverviewTableBlock"]   # écran Effectif, Effectif > Vue d'ensemble (v16)
VERSION = 16
NOM = "UIPickerEssaiRepos"
CLASSE = f"uipicker-essai-repos-v{VERSION}"
# bouton « Programme des rencontres » : le nôtre (effectif_boutons_entrainement), ou celui de Kinito (Vue d'ensemble)
APRES = ("UIPickerEquipesEntrainement-programme", "UIPickerKinito-effectif-vue-bouton-programme")
LISTE = "team.FilteredPlayers"                   # liste du tableau (v12 : team.PlayersAvailableForTraining, idem)
SOURCE_INTENSITE = "TrainingIntensityPlayerTableBlock_6x8"   # Entraînement > Intensité : boutons pour les cochés
CHOIX_INTENSITE = "BindableSwitchElement"                    # son #BindableSwitchElement (team.IsClub)
SELECTION = "selectedPlayers"                    # joueurs cochés (variable de TeamSquadBlock, lue par son clic droit)
ARME = "uipickerrepos"                           # 1 = menu des durées ouvert
ICONE = "game-concepts-training-rest_small"      # icône FM du repos (menu Entraînement)
TEXTE_BOUTON = "Reposer l'équipe"
SOURCE_BOUTON, BOUTON = "PortalPlayerReportFitnessBlock", "RestAction"
SOURCE_ACTIONS = "ActionsListWidget"             # racine (paramètres du FMActionButton), #ActionValid, #FirstRemapper
SOURCE_MENU = "GenericActionButtonWidget"        # #DropdownButton (selecteditem + SIDropdown)
GABARIT_MENU, GUID_GABARIT_MENU = ("CompetitionsLeagueTableStagesRow_Wide_WithoutColours",
                                   "27a23efade287344ba5d4f821e843daf")
ENFANT, GUID_ENFANT = ("CompetitionsLeagueTableStagesRow_Wide_WithoutArrow",
                       "0a124e8b0f25d324cb13132d9549ab9f")   # v15 : ligne = un choix d'intensité
ANCIENS = ["DebugNewsSocialReaction", "CompetitionsLeagueTableStagesRow_Default_WithoutArrow"]
NOM_GABARIT = f"{NOM}-gabarit-menu-v{VERSION}"
NOM_ENFANT = f"{NOM}-enfant-v{VERSION}"
TYPE_ACTION = 1633907817                         # paramètre `action` d'ActionsListWidget
STYLE_BOUTON = "buttons-button-base-default"     # style des boutons voisins (design d'avant)


class Morceaux:
    """morceaux de FM recopiés (modèles d'origine)"""

    def __init__(self):
        sa = self.sa = src_tree(SOURCE_ACTIONS)
        self.racine_actions = sa and next((k for k in sa.children(sa.tt["m_VisualTree"]["rid"])
                                           if typ(sa, k).endswith("BindingExpect")), None)
        self.valide = sa and first(sa, lambda r: sa.name(r) == "ActionValid")
        self.premier = sa and first(sa, lambda r: sa.name(r) == "FirstRemapper")
        sm_ = self.sm = src_tree(SOURCE_MENU)
        self.menu = sm_ and first(sm_, lambda r: typ(sm_, r).endswith("SIDropdown"))
        self.bloc_menu = sm_ and first(sm_, lambda r: sm_.name(r) == "DropdownButton")
        sb = self.sb = src_tree(SOURCE_BOUTON)
        self.bouton = sb and first(sb, lambda r: sb.name(r) == BOUTON and typ(sb, r) == "FM.UI.FMActionButton")
        self.commutateur = sm_ and first(sm_, lambda r: typ(sm_, r).endswith("BindableSwitchElement"))
        sl = self.sl = src_tree(fc.SOURCE_LISTE)
        self.liste = sl and first(sl, lambda r: sl.name(r) == "SmalList")
        si = self.si = src_tree(SOURCE_INTENSITE)
        self.intensite = si and first(si, lambda r: si.name(r) == CHOIX_INTENSITE
                                      and typ(si, r).endswith("BindableSwitchElement"))

    def ok(self):
        return None not in (self.racine_actions, self.valide, self.premier, self.menu, self.bloc_menu, self.bouton,
                            self.intensite, self.commutateur, self.liste)

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


# ---------- gabarit du menu (v14) ----------
def construire_gabarit_menu(t, mx):
    """reçoit `action` (comme ActionsListWidget) : la liste des choix de son 1er élément (« Intensité entraînement »),
    une ligne ENFANT par choix (seul « Aucun travail », qui a des enfants, s'affiche : le menu des jours)"""
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
    return [f"gabarit posé ({GABARIT_MENU}) : un menu par choix d'intensité qui a des enfants (Aucun travail)"]


def construire_enfant(t, mx):
    """un choix d'intensité (`item`, sans type) : commutateur de FM ; sans enfants = rien, avec enfants (Aucun
    travail) = menu de FM de ses enfants (les jours), au style bouton, libellé = icône repos"""
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
    return [f"ligne posée ({ENFANT}) : menu des jours de FM au style bouton, icône repos"]


# ---------- l'écran ----------
def retirer_ecran(t):
    old = [r for r in t.walk() if t.name(r).startswith(NOM)]
    dedans = {k for r in old for k in t.walk(r) if k != r}   # enlevés avec leur parent
    for r in old:
        if r not in dedans:
            t.remove(r)
    return ["essai Repos retiré de l'écran Effectif"] if old else []


def bulle_repos(t, modele, parent):
    """bulle « Reposer l'équipe » : copie de celle (Kinito) du bouton « Programme des rencontres », texte fixe"""
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
        return ["« Programme des rencontres » (effectif_boutons_entrainement / Kinito) introuvable"]
    plain = first(t, lambda r: typ(t, r) == "UnityEngine.UIElements.VisualElement"
                  and not t.elem(r).get("m_TemplateAlias"))
    # v14 : une boîte (rangée) : action Repos (jours direct), boutons d'intensité de FM, bulle sur le tout
    boite = t.clone_shallow(plain, t.parent[ref], t.children(t.parent[ref]).index(ref) + 1)
    fc.nommer(t, boite, NOM)
    t.elem(boite)["m_Classes"] = ["row-direction-normal", "align-items-center", CLASSE]
    t.elem(boite)["m_RuleIndex"] = -1
    parent = boite
    # les boutons d'intensité de FM (switch team.IsClub) sur tout l'effectif, menu = icône repos
    b = t.clone(mx.intensite, parent, src=mx.si)
    copy_usings(t, mx.si, mx.intensite)
    t.sd(b)["name"] = ""
    sans_regles(t, b)
    t.elem(b)["m_Classes"] = ["margin-left-global-gap-regular"]
    for r in t.walk(b):
        if typ(t, r) == "FM.UI.FMActionButton":
            sd = t.sd(r)
            sd["RecordsBinding"], sd["RecordsBinding_UxmlAttributeFlags"] = {"m_path": LISTE}, 1
            sd["ActionsListWidget"] = {"m_AssetGUID": GUID_GABARIT_MENU, "m_SubObjectName": "", "m_SubObjectType": ""}
            sd["ActionsListWidget_UxmlAttributeFlags"] = 1
            t.elem(r)["m_Classes"] = []
    bulle_repos(t, ref, boite)
    return msgs + [f"bouton icône repos à droite de « Programme des rencontres » = menu des jours de « Aucun "
                   f"travail » (intensité de FM) pour tout l'effectif, bulle « {TEXTE_BOUTON} »"]


# ---------- commandes ----------
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


def appliquer():
    mx = Morceaux()
    if not mx.ok():
        return ["morceaux de FM introuvables, rien fait"]
    msgs, faits = [], 0
    for nom in ANCIENS:   # modèles des versions précédentes
        if remettre(nom):
            msgs.append(f"{nom} remis d'origine (ancienne version)")
            faits += 1
    for nom, marque, fn in ((GABARIT_MENU, NOM_GABARIT, construire_gabarit_menu),
                            (ENFANT, NOM_ENFANT, construire_enfant)):
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
    for modele in MODELES:
        o = fc.ouvrir(modele)
        m = construire_ecran(o[3], mx) if o else [f"{modele} introuvable"]
        msgs += [f"{modele} : {x}" for x in m]
        if m and not any("introuvable" in x for x in m):
            fc.enregistrer(*o)
            faits += 1
    if faits:
        nb.save_all()
    return msgs


def retirer():
    msgs = []
    for modele in MODELES:
        o = fc.ouvrir(modele)
        if o and retirer_ecran(o[3]):
            fc.enregistrer(*o)
            msgs.append(f"{modele} : essai Repos retiré")
    for nom in [GABARIT_MENU, ENFANT] + ANCIENS:
        if remettre(nom):
            msgs.append(f"{nom} remis d'origine")
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
