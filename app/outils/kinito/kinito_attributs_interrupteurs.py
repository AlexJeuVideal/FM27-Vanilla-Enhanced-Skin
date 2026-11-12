"""[AJOUT KINITO] Fiche joueur > Formation > Progression, onglet Attributs : un interrupteur à la place de « Sel. » en
tête de chaque tableau d'attributs (coche / décoche toute la colonne), et un interrupteur agrandi en haut à droite, sous
le menu « Meilleur poste + rôle », qui coche / décoche les quatre colonnes. Les boutons « Tout cocher / Tout décocher »
d'Alex disparaissent de cet écran.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu (outils\\commun\\catalogue.py, voir « AJOUTS KINITO.md »).

Demande de Kinito (2026-11-12) : « le même bouton que pour chaque note », placé « à la place de Sel. dans chaque
colonne », et un bouton qui coche / décoche tous les attributs « en dessous de la colonne Coups de pied arrêtés »
(gardien : sous Gardiens - Technique). Ses choix : les boutons d'Alex remplacés sur cet écran ; l'interrupteur global
seul, sans texte ; le nom de chaque interrupteur au survol. Version 1 (son choix) : l'interrupteur a sa propre
position, il ne lit pas les notes (il repart éteint à l'ouverture de l'écran ; cocher les notes une à une ne l'allume
pas). L'interrupteur global allume / éteint aussi ceux des quatre colonnes. Après essais en jeu : v3 le global
« agrandi » ; v4 « en haut à droite », « juste en dessous du menu Meilleur poste + rôle et au-dessus de la ligne 20 »,
« aligné à droite avec le menu ». Kinito a proposé qu'il « clique sur les 4 boutons des colonnes » : c'est ce qu'il
fait, en envoyant lui-même leurs événements (une variable liée qui change ne fait pas cliquer un interrupteur).

Comment (tout mesuré le 2026-11-12, code du jeu et données) :
- EN-TÊTE : celui de FM est masqué (classe FM streamed-table__header-hide, que FM pose lui-même sur trois tableaux) ;
  à sa place, une rangée à nous faite des morceaux de l'en-tête de FM (StandardHeaderCellGrow, le HeaderCellAsset des
  six tableaux) : mêmes classes, même hauteur, même trait, titre = le n° de traduction de la colonne (fabrique).
- LARGEURS : FM répartit la largeur du tableau proportionnellement aux largeurs par défaut de ses colonnes, une colonne
  ne descendant pas sous son minimum, plafonné à 44 (StreamedTable.DistributeColumnWidths et
  BuildColumnWidthDistribution, constante 44.0 de GameAssembly) = une rangée flexible : flex-basis 0, flex-grow =
  largeur par défaut, min-width = min(minimum, 44) ; chaque colonne est une boîte sans marge (la case de FM dedans),
  sinon la rangée compte les marges en plus. Largeurs lues dans la vue de chaque tableau et sa fabrique. La colonne du
  nom change avec le point de rupture de l'écran (masques des vues = SI.UI.ApplicableBreakpoints : Small 128,
  Standard 192, Large 289 ; Large en 1920x1080 chez Kinito) : une variante par point de rupture, chacune dans un
  SIVisible sur app.GridBreakpointIsSmall / IsStandard / IsLarge (chemins que FM utilise ; un SIVisible caché passe en
  display: none, il ne prend pas de place).
- INTERRUPTEUR : le SICheckBox de FM de la case « Sel. » (modèle inclus inputs-switch-toggle-default de
  AttributeSelectorTableItem), dans une case qui porte la classe ET le style intégré de cette case FM (width 56,
  l'interrupteur centré dedans), sans son fond, sans rétrécir et calée à gauche : dans le tableau, cette case de 56
  déborde d'une colonne de 49 (rectangles de la sonde, 10/10) ; rétrécie à 49, l'interrupteur serait 3,5 plus à gauche
  (v2, vu en jeu). Le global : en absolu en haut à droite du cadre du graphique (réglages ANCRE_GLOBAL et suivants,
  mesurés), agrandi (scale 1.5), un SIVisible par mode sur player.isgoalkeeper. Lié à une variable Bool déclarée au
  plus haut du modèle, avec selectedtab de FM (vue par les colonnes et par le global) ; sans liaison, il écrirait sa
  valeur dans la portée elle-même (SICheckBox.SICheckBox_OnValueChanged : Bindings.Set puis Checked / UncheckedEvents). Ses événements sont
  ceux des boutons d'Alex (Enable / DisableTrainingAttribute, player.PlayerTraining, n° de l'attribut dans une variable
  Int kinitoattr<n>), avec ses numéros relevés en jeu (TABLEAUX de son attributs_tout_cocher, lus). Le global envoie
  ceux de ses quatre tableaux et copie vrai / faux (const.True / const.False) dans les variables des quatre colonnes.
- INFOBULLE : Tooltip > SIText de RoleLabelwIcon (comme 26.3, 26.4, 26.10), texte fixe FR / EN (textes=True).
- BOUTONS D'ALEX : sa fonction appliquée (ses enveloppes UIPickerToutCocher-… dans le modèle), on repart de l'original,
  on refait SA fonction en mémoire (son poser, non modifié), puis ses rangées de boutons sont masquées (display: none
  ajouté à leur règle) ; ses noms restent, son script se voit « à jour ». Sa fonction absente : nos propres enveloppes,
  faites comme les siennes. Retirer : sa fonction refaite sur l'original (ses boutons reviennent), ou l'original.

Touché : PlayerReportDevelopmentProgressReportBlock (gameworld), le modèle de l'écran ; aussi réécrit par
attributs_tout_cocher d'Alex (qui repart de l'original : le choix 1 relance cet ajout après lui). PAS
PlayerReportAttributesProgressReportBlock, que sa fonction traite aussi : ses vues n'ont de colonnes qu'au format
téléphone (masque 16 = PhoneLandscape), il ne s'affiche pas sur PC. Lus seulement : AttributeSelectorTableItem,
StandardHeaderCellGrow, RoleLabelwIcon, la fabrique et les vues des six tableaux.

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_attributs_interrupteurs.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_attributs_interrupteurs.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_attributs_interrupteurs.py etat
"""
import bisect
import copy
import json
import os
import re
import struct
import sys

import UnityPy

# outils\kinito\ -> commun\ (chemins.py : tous les dossiers des outils d'Alex)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import hierarchie_pyramide as hp  # noqa: E402  (ouverture des modèles depuis les originaux)
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles  # noqa: E402
import elements as el  # noqa: E402
import langue  # noqa: E402  (textes fixes en français ou en anglais, choix 106)
import attributs_tout_cocher as atc  # noqa: E402  (outil d'AlexJeuVideal : numéros, événements, sa fonction ; non modifié)

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
MODELE = "PlayerReportDevelopmentProgressReportBlock"   # Formation > Progression (onglets Niveau / Attributs)
CELLULE = atc.CELLULE                                  # AttributeSelectorTableItem : la case « Sel. » de FM
ALIAS_INTERRUPTEUR = "inputs-switch-toggle-default"    # son interrupteur (modèle inclus, SICheckBox)
ENTETE = "StandardHeaderCellGrow"                      # l'en-tête de FM des six tableaux (leur HeaderCellAsset)
GUID_ENTETE = "23aecb489b191134f8d5da376ca87691"
CELLULE_ENTETE = "data_display-table-heading-default-default"   # dans ENTETE : la case (hauteur, trait, marges)
SOURCE_BULLE = "RoleLabelwIcon"                        # infobulle FM : Tooltip > SIText
FN_TRADUCTION = "eae2be94"                             # fonction FM « texte n° de traduction »
COLONNE_SEL = "attribute-selector"                     # colonne de l'interrupteur dans la fabrique
GLOBAL_SOUS = {"NonGk": "SetPiecesTable", "Goalkeeper": "TechGkTable"}   # les deux modes du tableau de FM (joueur de
                                                                          # champ, gardien) et leur 2e tableau
COMMUNS = ("Mental", "Physical")                       # tableaux des deux modes
# point de rupture : (chemin FM, drapeau de m_applicableBreakpoints = énumération SI.UI.ApplicableBreakpoints, pas
# GridBreakpoint : Small 1, Standard 2, Large 4). v1 prenait 1 << GridBreakpoint : un cran de trop (Large -> 128 au lieu
# de 289), vu en jeu par la sonde (case « Sel. » de 77,9 au lieu de 49)
POINTS = (("app.GridBreakpointIsSmall", 1), ("app.GridBreakpointIsStandard", 2), ("app.GridBreakpointIsLarge", 4))
MIN_PLAFOND = 44.0     # FM : minimum d'une colonne = min(minimum, 44) (constante de BuildColumnWidthDistribution)
# L'INTERRUPTEUR GLOBAL (v4, demande de Kinito) : en haut à droite, sous le menu « Meilleur poste + rôle », au-dessus
# de la ligne « 20 » du graphique, aligné à droite sur le menu. Posé en absolu dans le cadre du graphique et des
# tableaux (AttributesPanelRemapper : visible sur l'onglet Attributs, avec des données ; son bord droit = celui du menu,
# rectangles de la sonde) et en dernier, pour passer devant le graphique au clic. Mesures (unités du jeu, capture
# 1920x1080 à 1,142857 px par unité, sonde du 11/10) : bas du menu 161, ligne « 20 » 201,25, haut du cadre 186,4 ;
# gabarit de l'interrupteur 42,9 x 21, bord droit de sa pastille à 37,7.
ANCRE_GLOBAL = "AttributesPanelRemapper"
ECHELLE_GLOBAL = 1.5   # l'interrupteur global agrandi (propriété scale, autour de son centre : ne déplace rien)
GABARIT = (42.9, 21.0, 37.7)   # largeur, hauteur du gabarit inputs-switch-toggle-default ; bord droit de la pastille
CENTRE_VIDE = (161.0 + 201.25) / 2 - 186.4   # milieu entre le menu et la ligne « 20 », depuis le haut du cadre
HAUT_GLOBAL = round(CENTRE_VIDE - GABARIT[1] / 2, 1)                                     # top (négatif : au-dessus)
DROITE_GLOBAL = round(ECHELLE_GLOBAL * (GABARIT[2] - GABARIT[0] / 2) - GABARIT[0] / 2, 1)  # right : pastille agrandie
                                                                                         # alignée sur le menu
GARDIEN = "player.isgoalkeeper"   # le chemin du tableau de FM (IsGoalkeeperSwitch) : un interrupteur par mode
SCALE = 327681         # StylePropertyId.Scale (deux nombres x, y, comme les feuilles de FM)
BULLE_COLONNE = langue.texte("Cocher / décocher toute la colonne", "Select / deselect the whole column")
BULLE_TOUT = langue.texte("Cocher / décocher tous les attributs", "Select / deselect all attributes")
CLASSE_SANS_ENTETE = "streamed-table__header-hide"     # classe FM : en-tête d'un tableau masqué
CLASSE_ENTETE = "streamed-table__header"               # classe FM de l'en-tête (police, couleur)
DISPLAY, AUCUN = 131081, 6                             # StylePropertyId.Display ; StyleValueKeyword.None (comme FM)
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
# =====================================================================================================
VERSION = f"4{langue.SUFFIXE}"   # v2 : points de rupture, colonnes sans marge ; v3 : case de FM à 56 calée à gauche,
                                 # global agrandi ; v4 : global en haut à droite, sous le menu des rôles (vus en jeu)
PREFIXE = "UIPickerKinito-attributs"
NOM_ENTETE = f"{PREFIXE}-entete-v{VERSION}"            # la rangée d'en-tête de chaque tableau
NOM_TOUT = f"{PREFIXE}-tout-v{VERSION}"                # l'interrupteur global (en haut à droite du cadre)
NOM_COLONNE = f"{PREFIXE}-colonne"                     # notre enveloppe (tableau + rangées), sans la fonction d'Alex
VAR_ATTR = "kinitoattr{}"
VAR_COCHE = "kinitocoche-{}"
VAR_TOUT = "kinitocoche-tout"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_attributs_interrupteurs.actif")
for _k, _v in {"flex-direction": (131083, 7), "justify-content": (131088, 7), "align-items": (131073, 7),
               "align-self": (131074, 7), "margin-top": (131093, 3), "height": (131087, 3),
               "padding-left": (131099, 3), "padding-right": (131100, 3), "padding-top": (131101, 3),
               "padding-bottom": (131098, 3), "position": (131102, 7), "right": (131103, 3),
               "top": (131104, 3)}.items():
    sm.PROPRIETES.setdefault(_k, _v)


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def enveloppes_alex(t):
    return [r for r in t.walk() if t.name(r).startswith(atc.PREFIXE)]


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone() ne refait que m_Parent : l'identifiant du parent aussi, s'il existe"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def nouveau(t, parent, index, classes, nom=""):
    """VisualElement vide, sans style recopié"""
    v = el.plain(t, parent, index, classes, nom)
    t.elem(v)["m_RuleIndex"] = -1
    recaler_parent(t, v)
    if nom:
        nommer(t, v, nom)
    return v


def surcharges(t, r):
    return [t.refs[ov["m_SerializedData"]["rid"]]["data"] for ov in t.elem(r).get("m_SerializedDataOverride") or []]


def declarer_modele(t, s, alias):
    """déclare le modèle inclus <alias> (m_Usings de s), à sa place dans l'ordre des noms (comme FM)"""
    u = next((u for u in s.tt.get("m_Usings") or [] if u.get("alias") == alias), None)
    if u is None:
        return False
    usings = t.tt.setdefault("m_Usings", [])
    if not any(x.get("alias") == alias for x in usings):
        cles = [x.get("alias") or "" for x in usings]
        usings.insert(bisect.bisect_left(cles, alias) if cles == sorted(cles) else len(usings), copy.deepcopy(u))
    return True


def cle_tableau(t, tableau):
    """la clé d'Alex (TABLEAUX) : le nom du tableau, sinon celui du premier parent nommé (pas une enveloppe)"""
    n, p = t.name(tableau), t.parent.get(tableau)
    while not n and p is not None:
        n = "" if t.name(p).startswith("UIPicker") else t.name(p)
        p = t.parent.get(p)
    return n


def mode_tableau(t, tableau):
    p = t.parent.get(tableau)
    while p is not None:
        if t.name(p) in GLOBAL_SOUS:
            return t.name(p)
        p = t.parent.get(p)
    return None


# ---------- événements (formats de FM, refaits à l'octet près) ----------
def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def copier(source, destination):
    """contenu d'un événement « copier la valeur de <source> dans <destination> » (format de 26.4 / 26.9)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([1, 0])


def liste(contenus):
    """liste d'événements : [1,1,1,N] puis [1] + longueur + contenu pour chacun"""
    assert len(contenus) < 128, "trop d'événements pour un seul octet de nombre"
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def attribut(src, ident, n):
    """contenu d'un événement Enable / DisableTrainingAttribute (celui des boutons d'Alex) pour l'attribut n° n"""
    return src.tete + atc._arg("player.PlayerTraining") + atc._arg(VAR_ATTR.format(n)) + ident


def formats_ok(src):
    """nos listes = celles d'Alex (son _evenements) et la copie = celle de FM (ClubNationInfoTabButton)"""
    ids = atc.TABLEAUX["Mental"]
    ok = liste([attribut(src, src.id_c, n) for n in ids]) == atc._evenements(
        src.tete, src.id_c, [["player.PlayerTraining", VAR_ATTR.format(n)] for n in ids])
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return ok and liste([copier("rowindex", "selected-tab")]) == attendu


# ---------- colonnes des tableaux (vue + fabrique, lues dans le jeu) ----------
class Colonnes:
    def __init__(self):
        self.vues = self._par_guid(VUES)
        self.fabriques = self._par_guid(FABRIQUES)

    @staticmethod
    def _par_guid(bundle):
        env = UnityPy.load(bundle)
        par_pid = {o.path_id: o for o in env.objects if o.type.name == "MonoBehaviour"}
        out = {}
        for o in env.objects:
            if o.type.name == "AssetBundle":
                for k, v in o.read_typetree()["m_Container"]:
                    if v["asset"]["m_PathID"] in par_pid:
                        out[k] = par_pid[v["asset"]["m_PathID"]]
        return out

    def de(self, t, tableau):
        """[{id, titre, largeur: {point: (défaut, minimum)}}] dans l'ordre de la vue, ou None"""
        sd = t.sd(tableau)
        g_fab = (sd.get("FactoryAsset") or {}).get("m_AssetGUID")
        g_vue = None
        for a in decode_args(sd["InitFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]):
            if b"AssetReferenceVisualArg" in bytes(a[0]):
                m = re.search(rb"[0-9a-f]{32}", bytes(a[1]))
                g_vue = m.group().decode() if m else None
        if g_fab not in self.fabriques or g_vue not in self.vues:
            return None
        fab = {c["m_id"]: c for c in self.fabriques[g_fab].read_typetree()["m_rowData"]}
        out = {}
        for c in self.vues[g_vue].read_typetree()["m_tableView"]["m_tableConfig"]:
            f = fab.get(c["m_columnID"])
            if f is None:
                return None
            m = c["m_columnMetadata"]
            col = out.setdefault(c["m_columnID"], {"id": c["m_columnID"], "titre": f["m_translationID"]["GameID"],
                                                   "largeur": {}})
            if m["m_titleTranslationIdOverride"]["GameID"] > 0:
                col["titre"] = m["m_titleTranslationIdOverride"]["GameID"]
            defaut = m["m_widthOverride"] if m["m_widthOverride"] > 0 else f["m_defaultWidth"]
            minimum = m["m_minWidthOverride"] if m["m_minWidthOverride"] > 0 else f["m_minimumWidth"]
            masque = m["m_applicableBreakpoints"]
            for _, drapeau in POINTS:
                if masque == -1 or masque & drapeau:
                    col["largeur"].setdefault(drapeau, (defaut, min(minimum, MIN_PLAFOND)))
        return list(out.values())


# ---------- morceaux de FM recopiés ----------
class Sources:
    def __init__(self, t):
        c = ouvrir(CELLULE, depart_original=True)
        self.tc = c[3] if c else None
        self.interrupteur = self.case = self.style_case = None
        if self.tc is not None:
            self.interrupteur = first(self.tc, lambda r: self.tc.elem(r).get("m_TemplateAlias") == ALIAS_INTERRUPTEUR)
            racine = first(self.tc, lambda r: typ(self.tc, r) == "ComponentElement")
            if racine is not None:   # la case FM : sa classe et son style intégré (width 56 : relevé le 11/10)
                self.case = list(self.tc.elem(racine)["m_Classes"])
                idx = self.tc.elem(racine).get("m_RuleIndex", -1)
                self.style_case = copy.deepcopy(self.tc.styles.values(idx)) if idx >= 0 else []
        h = ouvrir(ENTETE, depart_original=True)
        self.th = h[3] if h else None
        self.cellule = None if self.th is None else first(self.th, lambda r: self.th.name(r) == CELLULE_ENTETE)
        u = ouvrir(SOURCE_BULLE, depart_original=True)
        self.tu = u[3] if u else None
        self.bulle = None if self.tu is None else first(
            self.tu, lambda r: typ(self.tu, r) == "Tooltip" and len(self.tu.children(r)) == 1
            and typ(self.tu, self.tu.children(r)[0]) == "SIText")
        self.visible = el.visible_model(t)
        self.texte = self._texte_traduit(t)
        self.tete, self.id_c, self.id_d = atc.sources_evenements()
        self.colonnes = Colonnes()

    @staticmethod
    def _texte_traduit(t):
        """liaison de texte d'un SIText du modèle : « texte n° de traduction », argument constant (n° + 0)"""
        for r in t.walk():
            if typ(t, r) != "SIText":
                continue
            tb = t.sd(r).get("TextBinding") or {}
            if tb.get("m_kind") != 2 or not tb["m_visualFunction"]["m_target"]["m_guid"].startswith(FN_TRADUCTION):
                continue
            octets = tb["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"]
            args = decode_args(octets)
            if (len(args) == 1 and bytes(args[0][0]).endswith(b"TranslationID]") and len(bytes(args[0][1])) == 5
                    and bytes(args[0][1])[4:] == b"\x00" and encode_args(args) == list(octets)):
                return copy.deepcopy(tb)
        return None

    def ok(self):
        return (None not in (self.interrupteur, self.case, self.cellule, self.bulle, self.visible, self.texte)
                and formats_ok(self))

    def titre(self, numero):
        b = copy.deepcopy(self.texte)
        args = decode_args(b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"])
        args[0][1] = struct.pack("<i", numero) + b"\x00"
        b["m_visualFunction"]["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
        return b


# ---------- construction ----------
def flex(defaut, minimum):
    """la colonne dans notre rangée, comme FM la calcule : sa part de la largeur au prorata de sa largeur par défaut,
    jamais sous son minimum"""
    return {"flex-grow": defaut, "flex-shrink": 1, "flex-basis": 0, "min-width": minimum}


def completer(t, r, css):
    """style de l'élément complété par css : sa règle réécrite à sa place si elle est à lui seul (copie d'un autre
    modèle), sinon une règle neuve (style d'Alex) ; aucune règle orpheline"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx < 0 or sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        t.styles.style(t, r, css)
        return
    neuves = {sm.PROPRIETES[k][0]: (sm.PROPRIETES[k][0], "", [(sm.PROPRIETES[k][1], v)]) for k, v in css.items()}
    t.styles.add_rule([p for p in t.styles.values(idx) if p[0] not in neuves] + list(neuves.values()))
    t.styles.sh["m_Rules"][idx] = t.styles.sh["m_Rules"].pop()


def case_entete(t, src, parent, avec_titre, numero=None):
    """une case de l'en-tête de FM (hauteur, marges, trait du bas) ; avec son titre, ou vide"""
    c = t.clone(src.cellule, parent, src=src.th)
    t.styles.copy_from(src.th.styles, t, c)
    recaler_parent(t, c)
    if not avec_titre:
        for k in list(t.children(c)):
            t.remove(k)
        return c
    a_retirer = [r for r in t.walk(c) if r != c and (t.name(r) == "SortIcon" or t.elem(r).get("m_TemplateAlias"))]
    for r in a_retirer:
        if r in t.refs:
            t.remove(r)
    textes = [r for r in t.walk(c) if typ(t, r) == "SIText"]
    if len(textes) != 1:
        return None
    t.sd(textes[0])["TextBinding"] = src.titre(numero)
    t.sd(textes[0])["TextBinding_UxmlAttributeFlags"] = 1
    return c


def mettre_echelle(t, r, f):
    """scale: f f ajouté à la règle de l'élément (la sienne seule), deux nombres comme dans les feuilles de FM"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    if idx < 0 or sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        return False
    v = {"m_ValueType": 2, "valueIndex": t.styles._index(2, f)}
    props = t.styles.sh["m_Rules"][idx]["m_Properties"]
    props[:] = [p for p in props if p["m_Id"] != SCALE] + [
        {"m_Id": SCALE, "m_CustomName": "", "m_Line": -1, "m_Values": [dict(v), dict(v)]}]
    t.styles.changed = True
    return True


def interrupteur(t, src, cellule, variable, coche, decoche, bulle, nom, avec_case=True):
    """dans <cellule> : l'interrupteur de FM, lié à <variable>, et l'infobulle <bulle> sur la cellule. avec_case : dans
    une case comme celle des lignes (classe ET style intégré de la case FM, AttributeSelectorTableItem : 56 de large,
    l'interrupteur centré dedans ; sans son fond, sans rétrécir) ; sinon posé tel quel (l'interrupteur global)"""
    case = cellule
    if avec_case:
        case = nouveau(t, cellule, None, src.case, nom + "-case")
        t.elem(case)["m_RuleIndex"] = t.styles.add_rule(copy.deepcopy(src.style_case))
        completer(t, case, {"background-color": (0, 0, 0, 0), "min-height": 0, "flex-grow": 0, "flex-shrink": 0,
                            "height": {"unit": 2, "value": 100.0}})
    b = t.clone(src.interrupteur, case, src=src.tc)
    t.styles.copy_from(src.tc.styles, t, b)
    recaler_parent(t, b)
    if not declarer_modele(t, src.tc, ALIAS_INTERRUPTEUR):
        return False
    vus = 0
    for d in surcharges(t, b):
        if "CheckedEvents" in d and "UncheckedEvents" in d:
            d["CheckedEvents"] = {"m_bytes": liste(coche)}
            d["UncheckedEvents"] = {"m_bytes": liste(decoche)}
            d["SelectionBinding"] = {"m_path": variable}
            for k in ("CheckedEvents", "UncheckedEvents", "SelectionBinding"):
                d[k + "_UxmlAttributeFlags"] = 1
            vus += 1
    bul = t.clone(src.bulle, cellule, src=src.tu)
    t.styles.copy_from(src.tu.styles, t, bul)
    recaler_parent(t, bul)
    nommer(t, bul, nom + "-bulle")
    texte = t.children(bul)[0]
    recaler_parent(t, texte)
    nommer(t, texte, nom + "-bulle-texte")
    ts = t.sd(texte)
    ts.update(text=bulle, text_UxmlAttributeFlags=1)
    ts["TextBinding"]["m_kind"] = 0
    ts["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
    return vus == 1


def rangee(t, src, parent, index, colonnes, nom, sel):
    """la rangée d'en-tête, aux colonnes du tableau (cases de FM, titres) ; sel(cellule) remplit la case de la colonne
    « Sel. ». Renvoie la rangée, ou None."""
    r = nouveau(t, parent, index, ["row-direction-normal", CLASSE_ENTETE], nom)
    t.styles.style(t, r, {"flex-shrink": 0})
    for col in colonnes:
        largeurs = {point: col["largeur"].get(point) for _, point in POINTS}
        if not any(largeurs.values()):
            continue
        avec_titre = col["id"] != COLONNE_SEL and col["titre"] > 0
        variantes = [(None, next(iter(largeurs.values())))] if len(set(largeurs.values())) == 1 else \
            [(chemin, largeurs[point]) for chemin, point in POINTS if largeurs[point]]
        for chemin, (defaut, minimum) in variantes:
            # la colonne : une boîte SANS marge ni bordure, sinon la rangée flexible les compte en plus de sa part
            # (v1 : les cases d'en-tête vides, avec leurs marges, poussaient « Sel. » et le titre vers la droite)
            if chemin is None:
                hote = nouveau(t, r, None, [])
            else:   # largeur selon le point de rupture de l'écran : visible dans le sien seulement
                hote = sm.make_visible(t, src.visible, r, None, chemin, "", [])
                t.elem(hote)["m_RuleIndex"] = -1
                recaler_parent(t, hote)
                nommer(t, hote, f"{nom}-{col['id']}-{chemin.split('Is')[-1]}")
                if "VisibilityType" in t.sd(hote):
                    t.sd(hote)["VisibilityType"] = 0   # display: none quand caché : ne prend pas de place
            t.styles.style(t, hote, flex(defaut, minimum))
            # dedans, la case de FM (toute la largeur de la colonne : hauteur, marges, trait du bas)
            c = case_entete(t, src, hote, avec_titre, col["titre"])
            if c is None:
                return None
            if col["id"] == COLONNE_SEL:
                # la case des lignes, posée dedans, porte ses marges ; calée à gauche comme dans la cellule de FM (sa
                # case de 56 y déborde d'une colonne de 49 : sonde du 10/10, Mental), pas centrée
                completer(t, c, {"padding-left": 0, "padding-right": 0, "justify-content": "flex-start"})
                if not sel(c):
                    return None
    return r


def place_globale(t, src, par_mode):
    """l'interrupteur global : en absolu en haut à droite du cadre du graphique (ANCRE_GLOBAL), agrandi ; dedans, un
    SIVisible par mode (gardien / joueur de champ, sur GARDIEN), chacun avec son interrupteur (par_mode[mode] = sel)"""
    ancre = first(t, lambda r: t.name(r) == ANCRE_GLOBAL)
    if ancre is None:
        return None
    z = nouveau(t, ancre, None, [], NOM_TOUT)   # en dernier : devant le graphique au clic
    t.styles.style(t, z, {"position": "absolute", "right": DROITE_GLOBAL, "top": HAUT_GLOBAL})
    if not mettre_echelle(t, z, ECHELLE_GLOBAL):
        return None
    for mode, sel in par_mode.items():
        v = sm.make_visible(t, src.visible, z, None, GARDIEN, "", [])
        t.elem(v)["m_RuleIndex"] = -1
        recaler_parent(t, v)
        nommer(t, v, f"{NOM_TOUT}-{mode}")
        t.sd(v)["InvertDirectBinding"] = 0 if mode == "Goalkeeper" else 1   # NonGk : quand ce n'est pas un gardien
        t.sd(v)["InvertDirectBinding_UxmlAttributeFlags"] = 1
        if "VisibilityType" in t.sd(v):
            t.sd(v)["VisibilityType"] = 0
        if not sel(v):
            return None
    return ancre


def masquer(t, r):
    """display: none ajouté à la règle de style de l'élément (la sienne seule)"""
    idx = t.elem(r).get("m_RuleIndex", -1)
    prop = {"m_Id": DISPLAY, "m_CustomName": "", "m_Line": -1, "m_Values": [{"m_ValueType": 1, "valueIndex": AUCUN}]}
    if idx < 0:
        t.elem(r)["m_RuleIndex"] = t.styles.add_rule([(DISPLAY, "", [(1, AUCUN)])])
        return True
    if sum(1 for x in t.walk() if t.elem(x).get("m_RuleIndex", -1) == idx) != 1:
        return False
    props = t.styles.sh["m_Rules"][idx]["m_Properties"]
    props[:] = [p for p in props if p["m_Id"] != DISPLAY] + [prop]
    t.styles.changed = True
    return True


def envelopper(t, tableau):
    """notre colonne (tableau puis rangées), faite comme celle d'Alex : sa largeur et ses marges lui passent"""
    parent = t.parent[tableau]
    col = nouveau(t, parent, t.children(parent).index(tableau), [], NOM_COLONNE)
    t.styles.style(t, col, {"flex-grow": 1, "flex-direction": "column"})
    el.move(t, tableau, col)
    classes = t.elem(tableau).get("m_Classes") or []
    place = [c for c in classes if c.startswith(("width-", "margin-"))]
    t.elem(col)["m_Classes"] = list(place)
    t.elem(tableau)["m_Classes"] = [c for c in classes if c not in place]
    t.styles.style(t, tableau, {"flex-grow": 0})
    return col


def porteurs_variables(t, r):
    """[(élément, données)] des variables (BindingVariables, ou composant BindingVariablesComponent) au-dessus de r,
    du plus proche au plus haut"""
    out, p = [], t.parent.get(r)
    while p is not None:
        if typ(t, p) == "BindingVariables":
            out.append((p, t.sd(p)))
        for k in t.children(p):
            if typ(t, k) == "BindingVariablesComponent":
                out.append((p, t.sd(k)))
        p = t.parent.get(p)
    return out


def construire(t, src):
    tableaux = {}
    for r in t.walk():
        if typ(t, r) == "StreamedTable" and cle_tableau(t, r) in atc.TABLEAUX:
            tableaux[cle_tableau(t, r)] = r
    if set(tableaux) != set(atc.TABLEAUX):
        return [f"tableaux attendus {sorted(atc.TABLEAUX)}, trouvés {sorted(tableaux)} (introuvable)"]
    # variables : chez le porteur le plus proche qui soit au-dessus des six tableaux ET de l'interrupteur global (les
    # variables de position doivent être les mêmes pour les colonnes et pour le global) ; comme selectedtab de FM
    ancre = first(t, lambda r: t.name(r) == ANCRE_GLOBAL)
    if ancre is None:
        return [f"cadre du graphique ({ANCRE_GLOBAL}) introuvable"]
    communs = [p for p in porteurs_variables(t, ancre)
               if all(any(e[0] == p[0] for e in porteurs_variables(t, r)) for r in tableaux.values())]
    if not communs:
        return ["variables du modèle (au-dessus des tableaux et du cadre du graphique) introuvables"]
    porteur = communs[0][1]
    modes = {mode: [k for k, r in tableaux.items() if mode_tableau(t, r) == mode] + list(COMMUNS) for mode in GLOBAL_SOUS}
    msgs, alex = [], 0
    for cle, tableau in tableaux.items():
        if (t.sd(tableau).get("HeaderCellAsset") or {}).get("m_AssetGUID") != GUID_ENTETE:
            return [f"{cle} : en-tête qui n'est pas {ENTETE} (introuvable)"]
        colonnes = src.colonnes.de(t, tableau)
        if not colonnes or COLONNE_SEL not in [c["id"] for c in colonnes]:
            return [f"{cle} : colonnes (vue, fabrique) ou colonne « Sel. » introuvables"]
        enveloppe = t.parent[tableau]
        if t.name(enveloppe).startswith(atc.PREFIXE):   # fonction d'Alex : ses boutons masqués, son enveloppe gardée
            for k in t.children(enveloppe):
                if k != tableau and any(typ(t, x) == "SIButton" for x in t.walk(k)):
                    if not masquer(t, k):
                        return [f"{cle} : rangée de boutons d'Alex au style partagé (introuvable)"]
                    alex += 1
        else:
            enveloppe = envelopper(t, tableau)
        ids = atc.TABLEAUX[cle]
        var = VAR_COCHE.format(cle.lower())

        def sel(c, ids=ids, var=var):
            return interrupteur(t, src, c, var, [attribut(src, src.id_c, n) for n in ids],
                                [attribut(src, src.id_d, n) for n in ids], BULLE_COLONNE, f"{NOM_ENTETE}-{cle}")
        if rangee(t, src, enveloppe, 0, colonnes, NOM_ENTETE, sel) is None:
            return [f"{cle} : en-tête (morceaux de FM) introuvable"]
        t.elem(tableau)["m_Classes"] = list(t.elem(tableau).get("m_Classes") or []) + [CLASSE_SANS_ENTETE]
    # l'interrupteur global : il envoie ce qu'enverraient les quatre interrupteurs de colonne de son mode, et les met
    # dans la même position (une variable liée qui change ne fait pas « cliquer » l'interrupteur : SICheckBox
    # .OnBindingValueChanged met à jour sans envoyer ses événements)
    par_mode = {}
    for mode, cles in modes.items():
        coche = [attribut(src, src.id_c, n) for k in cles for n in atc.TABLEAUX[k]] + [
            copier("const.True", VAR_COCHE.format(k.lower())) for k in cles]
        decoche = [attribut(src, src.id_d, n) for k in cles for n in atc.TABLEAUX[k]] + [
            copier("const.False", VAR_COCHE.format(k.lower())) for k in cles]

        def sel_tout(v, coche=coche, decoche=decoche, mode=mode):
            return interrupteur(t, src, v, VAR_TOUT, coche, decoche, BULLE_TOUT, f"{NOM_TOUT}-{mode}", avec_case=False)
        par_mode[mode] = sel_tout
        msgs.append(f"interrupteur global, mode {mode} : {len(cles)} colonnes ({', '.join(cles)})")
    if place_globale(t, src, par_mode) is None:
        return ["interrupteur global (cadre du graphique, SIVisible) introuvable"]
    msgs.append(f"interrupteur global en haut à droite du cadre du graphique (x{ECHELLE_GLOBAL}, right "
                f"{DROITE_GLOBAL}, top {HAUT_GLOBAL})")
    # variables : n° des attributs (Int) et position des interrupteurs (Bool)
    nums = sorted({n for ids in atc.TABLEAUX.values() for n in ids})
    garde = [v for v in porteur.get("ValueVariables") or []
             if not v["m_name"].startswith(("kinitoattr", "kinitocoche-"))]
    porteur["ValueVariables"] = garde + [
        {"m_name": VAR_ATTR.format(n), "m_scopeValue": {"m_serializedData": f"Int|{n}|"}} for n in nums] + [
        {"m_name": VAR_COCHE.format(k.lower()), "m_scopeValue": {"m_serializedData": "Bool|0|"}} for k in tableaux] + [
        {"m_name": VAR_TOUT, "m_scopeValue": {"m_serializedData": "Bool|0|"}}]
    porteur["ValueVariables_UxmlAttributeFlags"] = 1
    return [f"en-tête de FM masqué, interrupteur à la place de « Sel. » : {', '.join(tableaux)} "
            f"(bulle « {BULLE_COLONNE} »)"] + msgs + [
        f"boutons d'Alex masqués ({alex} rangées)" if alex else "fonction d'Alex absente : nos propres colonnes"]


def refaire_alex(t):
    """SA fonction (attributs_tout_cocher.poser, non modifiée) sur l'arbre t, en mémoire"""
    tete, id_c, id_d = atc.sources_evenements()
    bundle_b, _, tt_b = nb.find_vta(atc.BOUTON)
    if tt_b is None:
        return [f"bouton d'Alex ({atc.BOUTON}) introuvable"]
    b_src = Tree(tt_b)
    b_src.styles = Styles(bundle_b, tt_b)
    msg = atc.poser(t, b_src, tete, id_c, id_d)
    return [f"fonction d'Alex refaite : {msg}" + (" (introuvable)" if "introuvable" in msg or "aucun" in msg else "")]


def a_jour(t):
    noms = [t.name(r) for r in marques(t)]
    return noms.count(NOM_ENTETE) == len(atc.TABLEAUX) and noms.count(NOM_TOUT) == 1


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre_original(o):
    bundle, obj, tt, t = o
    orig = hp.original(bundle, obj)
    if orig is None:
        print(f"{MODELE} : pas de sauvegarde d'origine, rien fait (utiliser la vérification des fichiers Steam)")
        return False
    obj.save_typetree(orig)
    feuille = hp.original(bundle, obj, orig["inlineSheet"]["m_PathID"])
    if feuille is not None:
        t.styles.sh, t.styles.changed = feuille, True
        t.styles.save()
    nb._dirty.add(bundle)
    print(f"{MODELE} : remis d'origine")
    return True


# ---------- commandes ----------
def cmd_appliquer():
    o = ouvrir(MODELE)
    if o is None:
        print(f"[Kinito] Attributs : {MODELE} introuvable (renommé par une mise à jour ?), ignoré")
        return
    if a_jour(o[3]):
        print("[Kinito] Attributs : déjà appliqué")
    else:
        alex = bool(enveloppes_alex(o[3]))
        travail = ouvrir(MODELE, depart_original=True)
        if marques(travail[3]) or enveloppes_alex(travail[3]):
            print("[Kinito] Attributs : pas de sauvegarde d'origine propre du modèle, rien enregistré")
            return
        msgs = refaire_alex(travail[3]) if alex else []
        src = Sources(travail[3])
        if not src.ok():
            print("[Kinito] Attributs : morceaux de FM (interrupteur, en-tête, infobulle, texte, SIVisible) ou format "
                  "des événements d'Alex inattendus, rien enregistré")
            return
        if not any("introuvable" in m for m in msgs):
            msgs += construire(travail[3], src)
        msgs += ["ancienne version remplacée"] if marques(o[3]) else []
        for m in msgs:
            print(f"[Kinito] Attributs : {m}")
        if any("introuvable" in m for m in msgs):
            print("[Kinito] Attributs : rien enregistré")
            return
        enregistrer(*travail)
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    o = ouvrir(MODELE)
    if o is None or not marques(o[3]):
        print("rien à retirer")
        return
    if enveloppes_alex(o[3]):   # sa fonction appliquée : refaite sur l'original, ses boutons reviennent
        travail = ouvrir(MODELE, depart_original=True)
        msgs = refaire_alex(travail[3])
        if any("introuvable" in m for m in msgs) or marques(travail[3]):
            print(f"{MODELE} : {msgs[0]} ; rien fait (réappliquer sa fonction remettra ses boutons)")
            return
        enregistrer(*travail)
        print(f"{MODELE} : éléments Kinito retirés, boutons d'Alex rendus ({msgs[0]})")
    elif not remettre_original(o):
        return
    nb.save_all()


def cmd_etat():
    o = ouvrir(MODELE)
    if o is None:
        print(f"{MODELE} introuvable")
        return
    t = o[3]
    print(f"{MODELE} : " + ("à jour (v" + VERSION + ")" if a_jour(t) else
                            "ANCIENNE version ou incomplet" if marques(t) else "d'origine")
          + " — fonction d'Alex : " + ("appliquée" if enveloppes_alex(t) else "absente"))
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
            print("[Kinito] Attributs : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
