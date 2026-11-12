"""[AJOUT KINITO] 26.17 — Effectif > Enregistrement de l'effectif (listes d'enregistrement) :
1. la colonne des règles (à gauche) assez large pour que ses tuiles s'affichent en entier, en affichage Large ;
2. les interrupteurs « Enr. » réduits (le même interrupteur de FM, sa couleur, à l'échelle), leur colonne à leur
   largeur, pas plus ;
3. ESSAI (v1) : un interrupteur dans l'en-tête de la colonne « Enr. », à la place du titre, qui active / désactive
   l'enregistrement de TOUS les joueurs cochés (case « Sél. ») de la liste.
Demande de Kinito (12/11/2026, sur sa capture). Ses choix : 5 colonnes de grille pour les règles ; interrupteurs et
bouton dans TOUTES les listes d'enregistrement (la cellule de FM est commune) ; un interrupteur à sa propre position ;
« le même interrupteur que ceux de la colonne, la même couleur » ; un essai du bouton d'abord.

Ajout de la version Kinito (pas du skin d'AlexJeuVideal) : tous les ajouts Kinito sont dans outils\\kinito\\,
fichiers kinito_*.py, marqueurs backups\\kinito_*.actif, catégorie 26 « Ajouts Kinito » du menu.

Comment (tout mesuré le 12/11/2026 : journal de la sonde clics_20261112_123858.log, règles USS lues avec
outils-analyse\\regle_exacte.py, capture de Kinito, objets lus avec le Python du skin) :
1. LES RÈGLES : le bloc SquadRegistrationRulesBlock a la classe de FM .rules-all---ucl (align-items flex-start) : son
   contenu garde sa largeur naturelle (335,1 unités : tuiles de 266 + rond + marges) dans une colonne de 312,4
   (4 colonnes de grille sur 20 dans la composition SquadRegistrationCardComposition-Large) : la droite des tuiles
   est coupée. Dans la composition « Large » (seule celle-ci : affichage Large, ce seul écran ; la liste finale
   internationale a ses propres compositions), les règles passent à 5 colonnes (~394 unités, comme FM dans sa
   composition par défaut : 5 sur 16) et le tableau à 15 (~1214 au lieu de 1296).
2. LES INTERRUPTEURS : la cellule de FM PlayerSquadRegistrationSelectionRow (citée par la seule colonne
   « squad-registration-selection » de PlayerTableFactory, donc par toutes les listes d'enregistrement) :
   BindingExpect > #content (rangée) > SIEnabled > modèle inclus inputs-switch-toggle-large-default (48 × 28 unités,
   mesuré : 55 × 32 px). On le réduit À L'ÉCHELLE (scale : une transformation, la place qu'il prend ne change pas ;
   comme FM 7 fois et 26.13 v22) : même dessin, même couleur. Pour qu'il reste centré dans une case plus étroite que
   sa place : #content justify-content center, SIEnabled et le modèle inclus sans rétrécir (flex-shrink 0 : sinon
   l'élément se tasserait à gauche). La colonne : largeur fixe (m_allowWidthAutoResizing 0 : sans élargissement
   automatique, comme la colonne de sélection de 26.14 v15, vue en jeu) = l'interrupteur réduit + LARGEUR_MARGE,
   dans la fabrique et dans les vues qui la surchargent (une surcharge à 0 = la largeur de la fabrique : gardée).
3. L'ESSAI DU BOUTON D'EN-TÊTE (aucune action de FM ne traite les joueurs cochés : texte « Register Selected »
   seulement dans « Register Selected Squad[…] » ; le tableau n'expose même pas sa sélection, SelectedItemsBinding
   vide) :
   - la sélection des 4 tableaux du bloc (SelectionMode 3) écrite dans une variable du bloc (SelectedItemsBinding,
     comme le tableau Résumé de l'Entraîn. individuel avec « selectedlist », variable de référence) ;
   - nos variables AJOUTÉES au composant de variables que le bloc a déjà (celui de « selectedview » et
     « playerstatsscope ») : rien de plus dans l'arbre ;
   - l'en-tête de la colonne (m_headerUxmlRef de la fabrique ; les en-têtes de FM n'ont ni BindingExpect ni
     m_headerValueBindings) = un modèle de FM cité par RIEN, réécrit (v2) : une copie exacte de l'en-tête de FM
     SOURCE_ENTETE (bouton header-button, titre, icône de tri : FM les cherche, la v1 sans eux faisait PLANTER le jeu),
     titre masqué, et par-dessus le même interrupteur (modèle inclus, réduit), sa case liée à V_VALEUR ; cocher /
     décocher allume V_ACTIF ;
   - dans le bloc, une zone cachée (SIVisible de FM sur V_ACTIF : il ne relie ses enfants que visible) : une liste
     non virtualisée de FM (WrappedObjectList, comme 26.14) sur la sélection, dont chaque ligne (un autre modèle de FM
     cité par RIEN, réécrit) copie V_VALEUR dans squadreg.Selected (la propriété que l'interrupteur de la ligne écrit)
     quand elle apparaît (SIDelayEvent de FM, recette de 26.4 / 26.5 / 26.8 / 26.9) ; puis un SIDelayEvent de la zone
     éteint V_ACTIF : la zone disparaît, cocher un joueur ensuite ne change rien. La ligne attend les mêmes paramètres
     que la cellule de FM (person, squadreg) plus V_VALEUR : FM fait pareil (12 listes de FM dont la ligne attend aussi
     une valeur du bloc, ex. SquadHierarchyTableBlock -> PlayerHierarchyCell attend « team » ; 163 variables de blocs
     redemandées ainsi en paramètre, type 0).
   À VOIR EN JEU : que l'en-tête atteigne les variables du bloc, que la ligne écrive squadreg.Selected. Si un maillon
   manque, la sonde (F7) dira lequel ; rien d'autre n'en dépend (parties 1 et 2).

Touché : ui-tileslayouts : SquadRegistrationCardComposition-Large (deux emplacements ; Alex écrit ce bundle avec
d'autres compositions, jamais celle-ci). ui-tablefactories : PlayerTableFactory, la seule colonne
squad-registration-selection (largeurs, élargissement, en-tête) ; propriétaire du bundle : moral_icone_seule d'Alex
(repart de l'original) : cet ajout passe après lui, comme 26.14. ui-tableviews : les vues qui ont cette colonne (sa
largeur). gameworld : PlayerSquadRegistrationSelectionRow (styles de #content, SIEnabled et du modèle inclus),
SquadRegistrationSelectionTableBlock (nos variables dans son composant, SelectedItemsBinding des 4 tableaux, notre
zone par son nom), et deux modèles de FM cités par RIEN, réécrits (à nous seuls) : MODELE_ENTETE, MODELE_LIGNE.
Personne d'autre (Alex, ajouts Kinito) ne touche ces objets (cherché par leur nom dans les outils, 15/10).
Lus seulement : PersonSearchMainContentBlock (SIVisible), GameCreationGameSummaryScreen (SIDelayEvent),
TrainingUnitInfo (WrappedObjectList), StandardHeaderCellCentered (l'en-tête de FM recopié, v2).

Usage (jeu fermé) :
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_enregistrement.py appliquer [--dry-run]
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_enregistrement.py retirer
  .venv\\Scripts\\python.exe outils\\kinito\\kinito_enregistrement.py etat
"""
import copy
import json
import os
import struct
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (v1.04 d'Alex : ses outils rangés par catégorie, tous trouvés par chemins)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from hierarchie_pyramide import typ, ouvrir  # noqa: E402
from notes_installations import first, decode_args, encode_args  # noqa: E402

# =====================================================================================================
#  RÉGLAGES (changer un réglage -> augmenter VERSION)
# =====================================================================================================
COMPOSITION = "SquadRegistrationCardComposition-Large"   # affichage Large (m_gridBreakpoint 3), ce seul écran
REGLES, TABLEAU = "Rules", "SelectionTable"               # m_elementID des deux emplacements
COLONNES_REGLES = 5        # FM : 4 sur 20 en Large (5 sur 16 dans sa composition par défaut)
CELLULE = "PlayerSquadRegistrationSelectionRow"          # la cellule de FM de la colonne « Enr. »
MODELE_INTERRUPTEUR = "inputs-switch-toggle-large-default"
LARGEUR_INTERRUPTEUR = 48.0   # unités (mesuré : 55 px sur la capture de Kinito, 1 u = 1,1428 px)
ECHELLE = 2 / 3            # réduction de l'interrupteur (même dessin, même couleur) : 48 -> 32 unités
LARGEUR_MARGE = 2          # unités en tout autour de l'interrupteur réduit dans la colonne
FABRIQUE = "PlayerTableFactory"
COLONNE = "squad-registration-selection"
ESSAI_BOUTON = True        # v1 : l'interrupteur d'en-tête (essai)
BLOC = "SquadRegistrationSelectionTableBlock"
MODELE_ENTETE = "WaiverListActionDropdownRow"     # gameworld, cité par RIEN (modeles_libres.py, 15/10) : réécrit
MODELE_LIGNE = "TransferWindowCardDropdownRow"    # gameworld, cité par RIEN (modeles_libres.py, 15/10) : réécrit
V_VALEUR = "kinitoenrvaleur"      # Bool : la position de l'interrupteur d'en-tête
V_ACTIF = "kinitoenractif"        # Bool : la zone cachée est montrée (le temps d'écrire)
V_MAX = "kinitoenrmax"            # Int : nombre maximum de lignes de la liste cachée
V_SELECTION = "kinitoenrselection"   # référence : les joueurs cochés (SelectedItemsBinding des tableaux)
MAX_LIGNES = 99
PARAM_LIGNE = "person"            # le joueur dans une ligne de la liste cachée (comme la cellule de FM)
CHEMIN_CIBLE = "squadreg.Selected"   # ce que l'interrupteur de FM de la ligne écrit
DELAI_LIGNE = 0.05                # s : chaque ligne écrit ce temps après être apparue
DELAI_ZONE = 0.5                  # s : la zone se referme ce temps après être apparue (mesuré en jeu le 15/10 avec la
# v4 : 25 joueurs cochés tous écrits en 0,5 s ; un essai à 0,3 s, jamais vu en jeu, a été abandonné avant installation)
REGLES_BLOC = "SquadRegistrationRulesBlock"   # v3 : le bloc des règles (cité par les seules compositions de
# l'enregistrement : club et liste finale nationale)
CONDITION_MLS = "Team.UsesMlsStyleRegistration"   # repère : la boîte des tuiles a deux SIVisible sur ce chemin
GAUCHE_ENTETE = 44.0       # v3 : unités du bord du tableau à l'en-tête « Enr. » = la colonne de sélection de FM
# (« multi-selection-column » de PlayerTableFactory : 44 ; mesuré 43,8) : « Enr. » est la 1re colonne des 14 vues
HAUT_ENTETE = 24.0         # v3 : la ligne d'en-têtes de FM (.data-display-…-table-heading… : 24 ; mesuré 23,6)
# v4 : déplacer une colonne fait PLANTER FM sur ces deux tableaux (OnEndReorder -> SaveAndApplyCustomView : le tableau
# du club n'a pas de collection de vues, celui de la sélection nationale une collection sans nom de vue personnalisée ;
# aucune collection libre pour faire comme 26.8). Choix de Kinito (15/10) : bloquer le déplacement, comme FM le fait
# déjà sur les tableaux MLS et A-League du même bloc (AllowColumnReordering 0). Le redimensionnement reste (il vérifie
# la collection avant d'enregistrer : pas de plantage)
SANS_DEPLACEMENT = ("Standardplayertable-club", "playertable-nation")
# =====================================================================================================

VERSION = 5   # v5 (15/10) : v4 VUE EN JEU (Kinito : colonne de gauche « mieux » ; l'interrupteur « fonctionne » mais
# « réagit parfois avec pas mal de latence », capture : en-tête allumé, 12 joueurs cochés tous éteints). Cause : un clic
# pendant que la zone est ouverte (V_ACTIF déjà vrai) n'ouvre rien de neuf, les lignes ont déjà écrit : l'en-tête change,
# les joueurs non. v5 : l'interrupteur dans un SIEnabled de FM (celui de la cellule, sur V_ACTIF inversé) : désactivé
# tant que la zone est ouverte (un clic y est ignoré, pas perdu) ; zone toujours refermée après 0,5 s (la durée vue en
# jeu avec 25 joueurs cochés).
# v1 (12/11/2026) : première version (colonne des règles, interrupteurs réduits, essai du bouton) :
# le jeu PLANTAIT en ouvrant l'écran (Player.log de Kinito, 13:50 : NullReferenceException dans
# SI.Bindable.StreamedTable+Header..ctor, appelé par MakeColumnHeader : notre en-tête n'avait pas le bouton
# « header-button » que FM y cherche). v2 (15/10) : l'en-tête = une copie EXACTE d'un en-tête de FM (SOURCE_ENTETE :
# bouton header-button, titre, icône de tri), le titre masqué (display: none, sa place gardée par FM), l'interrupteur
# posé par-dessus (boîte absolue dans le bouton). Vu en jeu (14:07) : plus de plantage, l'interrupteur bascule mais
# n'enregistre personne ; relevés F7 de la sonde (arbre_20261112_141312/141349/141403) : la sélection arrive bien dans
# kinitoenrselection (0 puis 3 joueurs), mais kinitoenrvaleur reste False : désassemblé, Header::Bind ne relie que le
# titre, l'aide et l'infobulle (BindHierarchy sur l'infobulle) : le CONTENU d'un en-tête n'est jamais relié aux données.
# Et les tuiles des règles restaient coupées : la boîte des tuiles de SquadRegistrationRulesBlock (seule enfant du bloc
# sans align-self: stretch, ses deux voisines l'ont) prend toujours la largeur du bloc + 22,7 (mesuré : 335,1 / 312,4
# en 4 colonnes, 416,5 / 393,8 en 5). v3 (15/10) : cette boîte en align-self: stretch ; l'en-tête = celui de FM, titre
# masqué, SANS interrupteur ; l'interrupteur (choix de Kinito : « par-dessus l'en-tête Enr. ») dans le BLOC (relié
# aux données) : une enveloppe autour du conteneur des tableaux (RegType : mêmes réglages, align-self stretch,
# flex-grow 1), et en dernier dans l'enveloppe (dessiné par-dessus le tableau) une boîte absolue à GAUCHE_ENTETE du
# bord, en haut, de la taille de l'en-tête, avec l'interrupteur
PREFIXE = "UIPickerKinito-enregistrement"
MARKER = os.path.join(backup.BACKUP_DIR, "kinito_enregistrement.actif")
COMPOSITIONS = os.path.join(nb.AA, "ui-tileslayouts_assets_all.bundle")    # (redirigé par essai_copies : copies)
FABRIQUES = os.path.join(nb.AA, "ui-tablefactories_assets_all.bundle")    # (idem)
VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")             # (idem)
SOURCE_VISIBLE = ("PersonSearchMainContentBlock", "position-view-visible")   # SIVisible de FM sur un booléen (26.8)
SOURCE_DELAI = "GameCreationGameSummaryScreen"    # SIDelayEvent de FM sans enfant (26.5, 26.8, 26.9)
SOURCE_LISTE = ("TrainingUnitInfo", "SmalList")   # WrappedObjectList de FM (26.14)
# v2 : un en-tête de colonne de FM, recopié tel quel dans le nôtre (10 colonnes de FM s'en servent ; sans modèle inclus).
# TOUS les en-têtes de FM (12 modèles, ~900 tableaux) : racine > Button « unity-button header-button » > titre (SIText
# « text ») et icône de tri (« SortIcon ») : StreamedTable.Header les attend
SOURCE_ENTETE = "StandardHeaderCellCentered"
FONCTION_LISTE = "f6846cfec20d41e4081482c40b6ce861"   # BindNItemsFromListWrappedList : [liste, nombre]
# GUID des deux modèles à nous (catalogue du jeu ; vérifiés dans outils-analyse\\guid_noms.json le 15/10)
GUIDS = {MODELE_ENTETE: "cc78b7d63978f5b48a6fb8b7c99b6b5e", MODELE_LIGNE: "9973f4aef5cf14349a99c29f59019fe5"}
LARGEUR_COLONNE = round(LARGEUR_INTERRUPTEUR * ECHELLE + LARGEUR_MARGE, 2)
NOM_ZONE = f"{PREFIXE}-zone-v{VERSION}"
NOM_LISTE = f"{PREFIXE}-liste-v{VERSION}"
NOM_FERMER = f"{PREFIXE}-fermer-v{VERSION}"
NOM_ENTETE = f"{PREFIXE}-entete-v{VERSION}"
NOM_ECRIRE = f"{PREFIXE}-ecrire-v{VERSION}"
NOM_ENVELOPPE = f"{PREFIXE}-enveloppe-v{VERSION}"
NOM_SUPERPOSE = f"{PREFIXE}-interrupteur-v{VERSION}"
VALEURS = [(V_VALEUR, "Bool|0|"), (V_ACTIF, "Bool|0|"), (V_MAX, f"Int|{MAX_LIGNES}|")]
REFERENCE = f"{V_SELECTION}:invalid:True"   # comme « selectedlist:invalid:True » de TeamIndividualTrainingBlock

for _k, _v in {"position": (131102, 7), "width": (131105, 3), "height": (131087, 3), "justify-content": (131088, 7),
               "align-items": (131073, 7), "flex-direction": (131083, 7), "flex-grow": (131084, 2),
               "left": (131089, 3), "top": (131104, 3), "right": (131103, 3), "bottom": (131080, 3),
               "align-self": (131074, 7)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
ID_SCALE = 327681    # StylePropertyId Scale d'Unity 6 (deux flottants, comme 26.13 v22)
ID_SHRINK = 131085   # flex-shrink
ID_DISPLAY, AUCUN = 131081, 6   # StylePropertyId Display ; StyleValueKeyword None (comme 26.13)
ECHELLE_REGLE = [(2, float(ECHELLE)), (2, float(ECHELLE))]


# ---------- outils ----------
def _bloc(b):
    return struct.pack("<i", len(b)) + b


def _texte(s):
    s = s.encode()
    return bytes([1, 1, len(s)]) + s


def copier(source, destination, drapeau=1):
    """événement de FM « copier la valeur de <source> dans <destination> » (format de 26.9 ; drapeau = ForceUpdate)"""
    return bytes([217, 15, 225, 87, 1]) + _bloc(_texte(source)) + _bloc(_texte(destination)) + bytes([drapeau, 0])


def liste(contenus):
    return list(bytes([1, 1, 1, len(contenus)]) + b"".join(b"\x01" + _bloc(c) for c in contenus))


def evenements_ok():
    """le format écrit ici = celui de FM, refait à l'octet près (copie de ClubNationInfoTabButton, comme 26.9)"""
    attendu = [1, 1, 1, 1, 1, 41, 0, 0, 0, 217, 15, 225, 87, 1, 11, 0, 0, 0, 1, 1, 8, 114, 111, 119, 105, 110, 100, 101,
               120, 15, 0, 0, 0, 1, 1, 12, 115, 101, 108, 101, 99, 116, 101, 100, 45, 116, 97, 98, 1, 0]
    return liste([copier("rowindex", "selected-tab")]) == attendu


def chemin_arg(s):
    b = s.encode("utf-8")
    return bytes([1, len(b)]) + b


def marques(t):
    return [r for r in t.walk() if (t.name(r) or "").startswith(PREFIXE)]


def ancetres(t, r):
    p = t.parent.get(r)
    while p is not None:
        yield p
        p = t.parent.get(p)


def nommer(t, r, nom):
    sd = t.sd(r)
    sd["name"], sd["name_UxmlAttributeFlags"] = nom, 1


def recaler_parent(t, r):
    """clone ne refait que m_Parent : l'identifiant du parent aussi (s'il est noté)"""
    if "m_ParentId" in t.elem(r):
        t.elem(r)["m_ParentId"] = t.elem(t.parent[r]).get("m_Id", t.elem(r)["m_ParentId"])


def style_brut(t, r, props):
    """complète le style intégré de r avec des propriétés brutes [(id, [(type, valeur)])]"""
    e = t.elem(r)
    old = t.styles.values(e["m_RuleIndex"]) if e.get("m_RuleIndex", -1) >= 0 else []
    ids = {pid for pid, _ in props}
    e["m_RuleIndex"] = t.styles.add_rule([p for p in old if p[0] not in ids] + [(pid, "", vals) for pid, vals in props])


def regle(t, r):
    """{StylePropertyId: valeurs} du style intégré de r"""
    i = t.elem(r).get("m_RuleIndex", -1)
    return {pid: v for pid, _, v in t.styles.values(i)} if i >= 0 else {}


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def retirer_regles(t, enlever):
    """les règles de la feuille intégrée (numéros dans enlever) que plus rien n'utilise, et les valeurs qu'elles avaient
    ajoutées en fin de table (comme 26.14 / 26.15 / 26.16)"""
    utilisees = {(r.get("data") or {}).get("m_RuleIndex", -1) for r in t.tt["references"]["RefIds"] if r}
    enlever = set(enlever) - utilisees - {-1}
    if not enlever:
        return
    regles = t.styles.sh["m_Rules"]
    garder = [i for i in range(len(regles)) if i not in enlever]
    nouvel = {ancien: neuf for neuf, ancien in enumerate(garder)}
    t.styles.sh["m_Rules"] = [regles[i] for i in garder]
    for r in t.tt["references"]["RefIds"]:
        d = (r or {}).get("data") or {}
        if d.get("m_RuleIndex", -1) >= 0:
            d["m_RuleIndex"] = nouvel[d["m_RuleIndex"]]
    tables = {2: "floats", 3: "dimensions", 4: "colors", 7: "strings", 8: "strings", 9: "strings"}
    servies = {}
    for rg in t.styles.sh["m_Rules"]:
        for p in rg["m_Properties"]:
            for v in p["m_Values"]:
                if v["m_ValueType"] in tables:
                    servies.setdefault(tables[v["m_ValueType"]], set()).add(v["valueIndex"])
    for nom in set(tables.values()):
        vals = t.styles.sh.get(nom) or []
        while vals and len(vals) - 1 not in servies.get(nom, set()):
            vals.pop()
    t.styles.changed = True


def monos(env, noms):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            n = o.peek_name()
        except Exception:
            continue
        if n in noms:
            yield o, o.read_typetree()


def ecrire_bundle(env, chemin):
    data = env.file.save(packer="original")
    if nb.DRY_RUN:
        print(f"(essai à blanc : rien écrit, {os.path.basename(chemin)} ferait {len(data) / 1e6:.2f} Mo)")
    else:
        backup.write_bundle(chemin, data)


def original(chemin):
    """l'original d'un bundle : sa sauvegarde (backups\\) s'il a déjà été modifié, sinon lui-même (comme
    dynamique_vue_ensemble d'Alex)"""
    p = backup.backup_path(chemin)
    return UnityPy.load(p if os.path.exists(p) else chemin)


# ---------- 1. la composition (règles à COLONNES_REGLES colonnes de grille) ----------
def composition_origine():
    return next((tt for _, tt in monos(original(COMPOSITIONS), {COMPOSITION})), None)


def composition_voulue(to):
    """les emplacements d'origine, réglés (copie) ; None si la forme a changé"""
    if to is None:
        return None
    comps = {c["m_elementID"]: c for c in to["m_gridComponents"]}
    if set(comps) != {REGLES, TABLEAU}:
        return None
    r, s = copy.deepcopy(comps[REGLES]), copy.deepcopy(comps[TABLEAU])
    if r["m_location"]["x"] != 0 or s["m_location"]["x"] != r["m_location"]["width"]:
        return None
    total = r["m_location"]["width"] + s["m_location"]["width"]
    for c, x, w in ((r, 0, COLONNES_REGLES), (s, COLONNES_REGLES, total - COLONNES_REGLES)):
        c["m_location"]["x"], c["m_location"]["width"], c["m_minSize"]["x"] = x, w, w
        for g in c["m_gridElementConfigs"]:
            g["Size"]["x"] = w
    return [r if c["m_elementID"] == REGLES else s for c in to["m_gridComponents"]]


def composition_poser(env):
    """True si changé ; None si introuvable / inattendue"""
    voulue = composition_voulue(composition_origine())   # depuis l'original : jamais deux fois
    trouves = list(monos(env, {COMPOSITION}))
    if voulue is None or len(trouves) != 1:
        return None
    o, tt = trouves[0]
    if tt["m_gridComponents"] == voulue:
        return False
    tt["m_gridComponents"] = voulue
    o.save_typetree(tt)
    return True


def composition_retirer(env):
    to = composition_origine()
    if to is None:
        return False
    for o, tt in monos(env, {COMPOSITION}):
        if tt["m_gridComponents"] != to["m_gridComponents"]:
            tt["m_gridComponents"] = copy.deepcopy(to["m_gridComponents"])
            o.save_typetree(tt)
            return True
    return False


def composition_a_jour(env):
    voulue = composition_voulue(composition_origine())
    return voulue is not None and any(tt["m_gridComponents"] == voulue for _, tt in monos(env, {COMPOSITION}))


# ---------- 2. la colonne (fabrique et vues) ----------
def colonne(tt):
    return next((c for c in (tt or {}).get("m_rowData") or [] if c.get("m_id") == COLONNE), None)


def colonne_origine():
    return colonne(next((tt for _, tt in monos(original(FABRIQUES), {FABRIQUE})), None))


def colonne_voulue(co):
    v = copy.deepcopy(co)
    v["m_defaultWidth"] = v["m_minimumWidth"] = float(LARGEUR_COLONNE)
    v["m_allowWidthAutoResizing"] = 0
    if ESSAI_BOUTON:
        v["m_headerUxmlRef"] = {"m_AssetGUID": GUIDS[MODELE_ENTETE], "m_SubObjectName": "", "m_SubObjectType": ""}
    return v


def fabrique_poser(env):
    """True si changé ; None si introuvable"""
    co = colonne_origine()
    trouves = list(monos(env, {FABRIQUE}))
    if co is None or len(trouves) != 1 or colonne(trouves[0][1]) is None:
        return None
    o, tt = trouves[0]
    voulue = colonne_voulue(co)
    i = [k for k, c in enumerate(tt["m_rowData"]) if c.get("m_id") == COLONNE][0]
    if tt["m_rowData"][i] == voulue:
        return False
    tt["m_rowData"][i] = voulue
    o.save_typetree(tt)
    return True


def fabrique_retirer(env):
    co = colonne_origine()
    if co is None:
        return False
    for o, tt in monos(env, {FABRIQUE}):
        idx = [k for k, c in enumerate(tt.get("m_rowData") or []) if c.get("m_id") == COLONNE]
        if idx and tt["m_rowData"][idx[0]] != co:
            tt["m_rowData"][idx[0]] = copy.deepcopy(co)
            o.save_typetree(tt)
            return True
    return False


def fabrique_a_jour(env):
    co = colonne_origine()
    return co is not None and any(colonne(tt) == colonne_voulue(co) for _, tt in monos(env, {FABRIQUE}))


def vues_avec_colonne(env):
    for o in env.objects:
        if o.type.name != "MonoBehaviour":
            continue
        try:
            tt = o.read_typetree()
        except Exception:
            continue
        tv = tt.get("m_tableView")
        if tv and any(c.get("m_columnID") == COLONNE for c in tv.get("m_tableConfig") or []):
            yield o, tt


def meta(tt):
    return next(c for c in tt["m_tableView"]["m_tableConfig"] if c["m_columnID"] == COLONNE)["m_columnMetadata"]


def surcharges_voulues(m_orig):
    """les surcharges de largeur d'une vue : celles posées par FM (non nulles) passent à LARGEUR_COLONNE ; 0 = la
    largeur de la fabrique (déjà la bonne) : gardé"""
    return {k: (float(LARGEUR_COLONNE) if m_orig[k] else m_orig[k]) for k in ("m_widthOverride", "m_minWidthOverride")}


def vues_origine():
    return {tt["m_Name"]: meta(tt) for _, tt in vues_avec_colonne(original(VUES))}


def vues_poser(env):
    origines = vues_origine()
    change, n = False, 0
    for o, tt in vues_avec_colonne(env):
        m = meta(tt)
        voulu = surcharges_voulues(origines.get(tt["m_Name"], m))
        if any(m[k] != v for k, v in voulu.items()):
            m.update(voulu)
            o.save_typetree(tt)
            change, n = True, n + 1
    return change, n


def vues_retirer(env):
    origines = vues_origine()
    change = False
    for o, tt in vues_avec_colonne(env):
        m, mo = meta(tt), origines.get(tt["m_Name"])
        if mo is not None and any(m[k] != mo[k] for k in ("m_widthOverride", "m_minWidthOverride")):
            for k in ("m_widthOverride", "m_minWidthOverride"):
                m[k] = mo[k]
            o.save_typetree(tt)
            change = True
    return change


def vues_a_jour(env):
    origines = vues_origine()
    vues = list(vues_avec_colonne(env))
    return bool(vues) and all(
        all(meta(tt)[k] == v for k, v in surcharges_voulues(origines.get(tt["m_Name"], meta(tt))).items())
        for _, tt in vues)


# ---------- 2. la cellule (interrupteur réduit, centré) ----------
def instance_interrupteur(t):
    return first(t, lambda r: t.elem(r).get("m_TemplateAlias") == MODELE_INTERRUPTEUR)


def elements_cellule(t):
    """[#content, SIEnabled, modèle inclus] de la cellule ; [] si la forme a changé"""
    inst = instance_interrupteur(t)
    if inst is None:
        return []
    sie = t.parent[inst]
    contenu = t.parent.get(sie)
    if typ(t, sie) != "SIEnabled" or contenu is None or t.name(contenu) != "content":
        return []
    return [contenu, sie, inst]


def cellule_poser(t):
    els = elements_cellule(t)
    if not els:
        return [f"{CELLULE} : #content > SIEnabled > {MODELE_INTERRUPTEUR} introuvable"]
    contenu, sie, inst = els
    t.styles.style(t, contenu, {"justify-content": "center"})
    style_brut(t, sie, [(ID_SHRINK, [(2, 0.0)])])
    style_brut(t, inst, [(ID_SCALE, ECHELLE_REGLE), (ID_SHRINK, [(2, 0.0)])])
    return [f"interrupteurs « Enr. » réduits à {ECHELLE:.2f} (même modèle de FM, même couleur), centrés"]


def proche(valeurs, attendues):
    """mêmes valeurs à l'arrondi près (la feuille garde des flottants 32 bits : 2/3 y devient 0,66666669)"""
    return (valeurs is not None and len(valeurs) == len(attendues)
            and all(a[0] == b[0] and abs(a[1] - b[1]) < 1e-5 for a, b in zip(valeurs, attendues)))


def cellule_a_jour(t):
    els = elements_cellule(t)
    return (bool(els) and proche(regle(t, els[2]).get(ID_SCALE), ECHELLE_REGLE)
            and proche(regle(t, els[1]).get(ID_SHRINK), [(2, 0.0)]))


def cellule_rendre(t):
    return rendre_elements(t, CELLULE, elements_cellule)


# ---------- 1 bis (v3). la boîte des tuiles des règles : align-self stretch, comme ses deux voisines ----------
def elements_regles(t):
    """[la boîte des tuiles] : l'enfant de #rules dont les enfants sont les deux SIVisible sur CONDITION_MLS ; [] si
    la forme a changé"""
    regles = [r for r in t.walk() if t.name(r) == "rules"]
    if len(regles) != 1:
        return []
    boites = [k for k in t.children(regles[0]) if [typ(t, x) for x in t.children(k)] == ["SIVisible", "SIVisible"]
              and all(t.binding(x) == CONDITION_MLS for x in t.children(k))]
    return boites if len(boites) == 1 else []


def regles_poser(t):
    els = elements_regles(t)
    if not els:
        return [f"{REGLES_BLOC} : boîte des tuiles introuvable"]
    t.styles.style(t, els[0], {"align-self": "stretch"})
    return ["règles : la boîte des tuiles prend la largeur de la colonne (align-self: stretch, comme ses voisines)"]


def regles_a_jour(t):
    els = elements_regles(t)
    return bool(els) and regle(t, els[0]).get(131074) == [(7, "stretch")]


def regles_rendre(t):
    return rendre_elements(t, REGLES_BLOC, elements_regles)


def rendre_elements(t, modele, elements_fn):
    """classes et règles des éléments (elements_fn(t), même ordre dans l'original) rendues d'après l'original, nos
    règles retirées ; True si changé"""
    o = ouvrir(modele, depart_original=True)
    if o is None:
        return False
    to = o[3]
    n0 = len(to.styles.sh["m_Rules"])
    ici, la = elements_fn(t), elements_fn(to)
    if not ici or len(ici) != len(la):
        return False
    fait, enlever = False, set()
    for r, ro in zip(ici, la):
        e, eo = t.elem(r), to.elem(ro)
        cl, ri = list(eo.get("m_Classes") or []), eo.get("m_RuleIndex", -1)
        if list(e.get("m_Classes") or []) != cl or e.get("m_RuleIndex", -1) != ri:
            if e.get("m_RuleIndex", -1) >= n0:
                enlever.add(e["m_RuleIndex"])
            e["m_Classes"], e["m_RuleIndex"] = cl, ri
            fait = True
    retirer_regles(t, enlever)
    return fait


# ---------- 3. l'essai du bouton : morceaux de FM ----------
class Sources:
    def __init__(self):
        o = ouvrir(SOURCE_VISIBLE[0], depart_original=True)
        self.tvi = o and o[3]
        self.visible = self.tvi and first(self.tvi, lambda r: self.tvi.name(r) == SOURCE_VISIBLE[1]
                                          and typ(self.tvi, r) == "SIVisible")
        o = ouvrir(SOURCE_DELAI, depart_original=True)
        self.td = o and o[3]
        self.delai = self.td and first(self.td, lambda r: self.td.elem(r).get("m_FullTypeName") == "FM.UI.SIDelayEvent"
                                       and not self.td.children(r))
        o = ouvrir(SOURCE_LISTE[0], depart_original=True)
        self.tl = o and o[3]
        self.liste = self.tl and first(self.tl, lambda r: self.tl.name(r) == SOURCE_LISTE[1]
                                       and typ(self.tl, r) == "WrappedObjectList")
        o = ouvrir(CELLULE, depart_original=True)
        self.tc = o and o[3]
        self.ttc = o and o[2]
        els = elements_cellule(self.tc) if self.tc else []
        self.contenu, self.actif, self.interrupteur = (els[0], els[1], els[2]) if els else (None, None, None)
        attente = self.tc and first(self.tc, lambda r: typ(self.tc, r) == "BindingExpect")
        self.parametres = attente and self.tc.sd(attente).get("Parameters")
        o = ouvrir(SOURCE_ENTETE, depart_original=True)
        self.th = o and o[3]
        self.ttth = o and o[2]
        boutons = self.th.children(self.th.tt["m_VisualTree"]["rid"]) if self.th else []
        self.bouton = boutons[0] if len(boutons) == 1 and typ(self.th, boutons[0]) == "Button" and "header-button" in (
            self.th.elem(boutons[0]).get("m_Classes") or []) else None
        textes = [r for r in self.th.walk(self.bouton) if typ(self.th, r) == "SIText" and self.th.name(r) == "text"] \
            if self.bouton else []
        self.texte = textes[0] if len(textes) == 1 else None
        if self.ttth is not None and self.ttth.get("m_Usings"):
            self.bouton = None   # un en-tête qui inclut un autre modèle : forme inattendue

    def manque(self):
        out = [k for k in ("visible", "delai", "liste", "contenu", "actif", "interrupteur", "parametres", "bouton",
                           "texte")
               if getattr(self, k) is None]
        return out + ([] if evenements_ok() else ["format d'événement"])


def recopier(t, s, rid, parent, nom=None, garder_enfants=False):
    """un élément de FM recopié d'un autre modèle (sans enfants sauf garder_enfants) ; classes et règles ôtées (elles
    pointeraient dans une autre feuille)"""
    r = t.clone(rid, parent, src=s)
    recaler_parent(t, r)
    if not garder_enfants:
        for k in list(t.children(r)):
            t.remove(k)
    for x in t.walk(r):
        if "m_RuleIndex" in t.elem(x):
            t.elem(x)["m_RuleIndex"] = -1
    t.elem(r)["m_Classes"] = []
    if nom:
        nommer(t, r, nom)
    return r


def a_zero(t, r):
    """sans place ni clics"""
    t.styles.style(t, r, {"position": "absolute", "width": 0, "height": 0})
    sd = t.sd(r)
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore


def delai(t, src, parent, nom, duree, evenement):
    dl = recopier(t, src.td, src.delai, parent, nom)
    a_zero(t, dl)
    d = t.sd(dl)
    d["m_duration"], d["m_duration_UxmlAttributeFlags"] = float(duree), 1
    d["TransitionEvents"] = {"m_bytes": liste([evenement])}
    d["TransitionEvents_UxmlAttributeFlags"] = 1
    return dl


# ---------- 3. le bloc (variables, sélection, zone cachée) ----------
def variables(t):
    """(élément, données) du composant de variables du bloc (celui de FM) ; (None, None) s'il n'est pas unique"""
    els = [r for r in t.walk() if typ(t, r) == "BindingVariablesComponent"]
    if len(els) != 1:
        return None, None
    v = els[0]
    ident = t.elem(v)["m_Id"]
    ds = [t.refs[c["rid"]]["data"] for c in t.sd(t.parent[v]).get("m_components") or []
          if ((t.refs.get(c["rid"]) or {}).get("data") or {}).get("uxmlAssetId") == ident]
    return (v, ds[0]) if len(ds) == 1 else (None, None)


def variables_poser(t):
    v, d = variables(t)
    if v is None or not d.get("ValueVariables") or "ReferenceVariables" not in d:
        return False
    props = {p["name"]: p for p in t.elem(v).get("m_Properties") or []}
    if set(props) != {"value-vars", "reference-vars"}:
        return False
    for nom, val in VALEURS:
        x = copy.deepcopy(d["ValueVariables"][0])
        x["m_name"], x["m_scopeValue"]["m_serializedData"] = nom, val
        d["ValueVariables"].append(x)
        props["value-vars"]["value"] += ",{" + nom + "}{" + val + "}"
    d["ReferenceVariables"].append({"m_type": {"id": 0}, "m_initToNull": 1, "m_name": V_SELECTION})
    props["reference-vars"]["value"] += "," + REFERENCE
    d["ValueVariables_UxmlAttributeFlags"] = d["ReferenceVariables_UxmlAttributeFlags"] = 1
    return True


def variables_a_jour(t):
    v, d = variables(t)
    return v is not None and {n for n, _ in VALEURS} <= {x["m_name"] for x in d.get("ValueVariables") or []} and any(
        x["m_name"] == V_SELECTION for x in d.get("ReferenceVariables") or [])


def tableaux(t):
    return [r for r in t.walk() if typ(t, r) == "StreamedTable"]


def interrupteur_poser(t, src, parent, nom_boite, css):
    """une boîte (nom_boite, style css, sans clics) dans parent, avec le MÊME interrupteur que la cellule de FM (son
    modèle inclus recopié, réduit, sans rétrécir) : sa case liée à V_VALEUR ; cocher / décocher allume V_ACTIF ;
    v5 : comme dans la cellule de FM, l'interrupteur est dans un SIEnabled (le sien, recopié), ici sur V_ACTIF
    inversé : désactivé tant que la zone écrit ; None si la surcharge de FM a changé"""
    boite = recopier(t, src.tc, src.contenu, parent, nom_boite)
    t.styles.style(t, boite, css)
    sd = t.sd(boite)
    sd["pickingMode"], sd["pickingMode_UxmlAttributeFlags"] = 1, 1   # PickingMode.Ignore : seul l'interrupteur
    actif = recopier(t, src.tc, src.actif, boite, f"{nom_boite}-actif")
    sd = t.sd(actif)
    if (sd.get("Binding") or {}).get("m_kind") != 1 or "InvertDirectBinding" not in sd:
        return None
    sd["Binding"]["m_direct"]["Path"]["m_path"] = V_ACTIF
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 1, 1
    style_brut(t, actif, [(ID_SHRINK, [(2, 0.0)])])
    inst = recopier(t, src.tc, src.interrupteur, actif, garder_enfants=True)
    t.elem(inst)["m_Classes"] = list(src.tc.elem(src.interrupteur).get("m_Classes") or [])
    style_brut(t, inst, [(ID_SCALE, ECHELLE_REGLE), (ID_SHRINK, [(2, 0.0)])])
    ovr = t.elem(inst).get("m_SerializedDataOverride") or []
    d = (t.refs.get((ovr[0].get("m_SerializedData") or {}).get("rid")) or {}).get("data") if len(ovr) == 1 else None
    if d is None or (d.get("SelectionBinding") or {}).get("m_path") != CHEMIN_CIBLE:
        return None
    d["SelectionBinding"] = {"m_path": V_VALEUR}
    d["CheckedEvents"] = {"m_bytes": liste([copier("const.True", V_ACTIF)])}
    d["UncheckedEvents"] = {"m_bytes": liste([copier("const.True", V_ACTIF)])}
    d["CheckedEvents_UxmlAttributeFlags"] = d["UncheckedEvents_UxmlAttributeFlags"] = 1
    return boite


def envelopper(t, src, el, nom, css):
    """el (un élément de FM) mis dans une enveloppe à nous (nom, style css), à sa place (même parent, même rang),
    comme 26.9 avec les menus des vues"""
    p = t.parent[el]
    env = recopier(t, src.tc, src.contenu, p, nom)
    kids = [k for k in t.elem(p)["m_Children"] if k["rid"] != env]
    kids[[k["rid"] for k in kids].index(el)] = {"rid": env}
    t.elem(p)["m_Children"] = kids
    t.elem(env)["m_Children"] = [{"rid": el}]
    t.elem(el)["m_Parent"] = {"rid": env}
    t.parent[el] = env
    recaler_parent(t, el)
    t.styles.style(t, env, css)
    return env


def bloc_poser(t, tt, src):
    """(v3 : sur le bloc d'ORIGINE, enregistré tel quel ensuite)"""
    porteur = first(t, lambda r: typ(t, r) == "ComponentElement" and any(
        typ(t, k) == "BindingVariablesComponent" for k in t.children(r)))
    tabs = tableaux(t)
    regtype = [r for r in t.walk() if t.name(r) == "RegType" and typ(t, r) == "BindableSwitchElement"]
    if porteur is None or len(tabs) != 4 or any(t.sd(tb).get("SelectionMode") != 3 for tb in tabs) or len(
            regtype) != 1 or not all(regtype[0] in ancetres(t, tb) for tb in tabs):
        return [f"{BLOC} : forme inattendue (introuvable)"]
    if not variables_poser(t):
        return [f"{BLOC} : composant de variables de FM de forme inattendue (introuvable)"]
    for tb in tabs:
        sd = t.sd(tb)
        sd["SelectedItemsBinding"], sd["SelectedItemsBinding_UxmlAttributeFlags"] = {"m_path": V_SELECTION}, 1
    # v4 : plus de déplacement de colonne sur les deux tableaux où il fait planter FM
    sans = [tb for tb in tabs if t.name(tb) in SANS_DEPLACEMENT]
    if len(sans) != len(SANS_DEPLACEMENT) or any("AllowColumnReordering" not in t.sd(tb) for tb in sans):
        return [f"{BLOC} : tableaux {', '.join(SANS_DEPLACEMENT)} introuvables"]
    for tb in sans:
        sd = t.sd(tb)
        sd["AllowColumnReordering"], sd["AllowColumnReordering_UxmlAttributeFlags"] = 0, 1
    # la zone cachée : un SIVisible de FM sur V_ACTIF (enfants reliés seulement visible), sans place ni clics
    z = recopier(t, src.tvi, src.visible, porteur, NOM_ZONE)
    sd = t.sd(z)
    sd["Binding"]["m_kind"] = 1
    sd["Binding"]["m_direct"]["Path"]["m_path"] = V_ACTIF
    sd["InvertDirectBinding"], sd["InvertDirectBinding_UxmlAttributeFlags"] = 0, 1
    sd["AlwaysInstantiate"], sd["AlwaysInstantiate_UxmlAttributeFlags"] = 0, 1
    a_zero(t, z)
    li = recopier(t, src.tl, src.liste, z, NOM_LISTE)
    a_zero(t, li)
    sd = t.sd(li)
    f = sd["VisualFuncBinding"]
    if (f.get("m_target") or {}).get("m_guid") != FONCTION_LISTE:
        return ["liste de FM (WrappedObjectList) : fonction inattendue (introuvable)"]
    args = decode_args(f["m_inputs"]["m_variable"]["m_argumentBytes"])
    chemins = [a for a in args if bytes(a[0]).endswith(b"[SI.Bindable.BindingPath]")]
    if len(chemins) != 2:
        return ["liste de FM (WrappedObjectList) : arguments inattendus (introuvable)"]
    chemins[0][1], chemins[1][1] = chemin_arg(V_SELECTION), chemin_arg(V_MAX)
    f["m_inputs"]["m_variable"]["m_argumentBytes"] = encode_args(args)
    sd["ItemTemplate"]["m_AssetGUID"] = GUIDS[MODELE_LIGNE]
    sd["ItemParamName"] = PARAM_LIGNE
    sd["ItemTemplate_UxmlAttributeFlags"] = sd["ItemParamName_UxmlAttributeFlags"] = 1
    sd["VisualFuncBinding_UxmlAttributeFlags"] = 1
    delai(t, src, z, NOM_FERMER, DELAI_ZONE, copier("const.False", V_ACTIF))
    # v3 : l'interrupteur, par-dessus l'en-tête « Enr. » (le contenu d'un en-tête n'est jamais relié aux données) :
    # dans une enveloppe autour du conteneur des tableaux (mêmes réglages que lui), APRÈS lui (dessiné par-dessus)
    env = envelopper(t, src, regtype[0], NOM_ENVELOPPE, {"align-self": "stretch", "flex-grow": 1,
                                                         "flex-direction": "column"})
    if interrupteur_poser(t, src, env, NOM_SUPERPOSE, {
            "position": "absolute", "left": GAUCHE_ENTETE, "top": 0, "width": float(LARGEUR_COLONNE),
            "height": HAUT_ENTETE, "flex-direction": "row", "justify-content": "center",
            "align-items": "center"}) is None:
        return ["case de l'interrupteur de FM (surcharge) : forme inattendue (introuvable)"]
    usings = [u for u in src.ttc.get("m_Usings") or [] if u.get("alias") == MODELE_INTERRUPTEUR]
    if len(usings) != 1:
        return [f"{CELLULE} : déclaration du modèle inclus {MODELE_INTERRUPTEUR} introuvable"]
    tt["m_Usings"] = [u for u in tt.get("m_Usings") or [] if u.get("alias") != MODELE_INTERRUPTEUR] + [
        copy.deepcopy(usings[0])]
    return [f"{len(tabs)} tableaux : joueurs cochés dans {V_SELECTION} ; zone cachée (une ligne par joueur coché, qui "
            f"écrit {CHEMIN_CIBLE} ; refermée après {DELAI_ZONE} s)",
            "déplacement des colonnes bloqué (club, sélection nationale : il faisait planter FM), comme MLS et A-League",
            f"interrupteur des joueurs cochés par-dessus l'en-tête « Enr. » (à {GAUCHE_ENTETE} du bord du tableau), "
            f"lié à {V_VALEUR}"]


def bloc_rendre():
    """le bloc rendu d'origine (typetree et feuille de l'original : seul 26.17 le touche) ; True si changé"""
    o = ouvrir(BLOC)
    if o is None or not (marques(o[3]) or variables_a_jour(o[3])):
        return False
    oo = ouvrir(BLOC, depart_original=True)
    if oo is None:
        return False
    enregistrer(*oo)
    return True


def bloc_a_jour(t):
    noms = {t.name(r) for r in marques(t)}
    return ({NOM_ZONE, NOM_LISTE, NOM_FERMER, NOM_ENVELOPPE, NOM_SUPERPOSE, f"{NOM_SUPERPOSE}-actif"} <= noms
            and variables_a_jour(t)
            and all((t.sd(tb).get("SelectedItemsBinding") or {}).get("m_path") == V_SELECTION for tb in tableaux(t))
            and all(t.sd(tb).get("AllowColumnReordering") == 0 for tb in tableaux(t) if t.name(tb) in SANS_DEPLACEMENT))


# ---------- 3. les deux modèles à nous (refaits depuis leur original) ----------
def entete_poser(t, tt, src):
    """l'en-tête (v3) : l'en-tête de FM SOURCE_ENTETE recopié tel quel (bouton header-button, classes et styles
    intégrés compris), la boîte de son titre masquée (display: none : la hauteur de l'en-tête reste celle de FM) et
    nommée NOM_ENTETE (repère). L'interrupteur est dans le BLOC, posé par-dessus (v3 : le contenu d'un en-tête n'est
    jamais relié aux données)"""
    racine = t.tt["m_VisualTree"]["rid"]
    for k in list(t.children(racine)):
        t.remove(k)
    bouton = t.clone(src.bouton, racine, src=src.th)
    recaler_parent(t, bouton)
    t.styles.copy_from(src.th.styles, t, bouton)
    textes = [r for r in t.walk(bouton) if typ(t, r) == "SIText" and t.name(r) == "text"]
    if len(textes) != 1:
        return [f"{SOURCE_ENTETE} : titre de l'en-tête introuvable"]
    boite_titre = t.parent[textes[0]]
    style_brut(t, boite_titre, [(ID_DISPLAY, [(1, AUCUN)])])
    nommer(t, boite_titre, NOM_ENTETE)
    return ["en-tête « Enr. » : celui de FM, titre masqué (l'interrupteur est posé par-dessus, dans le bloc)"]


def ligne_poser(t, src):
    """la ligne de la liste cachée : la racine BindingExpect du modèle (gardée) attend les paramètres de la cellule de FM
    (person, squadreg) et V_VALEUR (comme FM redemande les variables d'un bloc) ; dedans, un SIDelayEvent de FM qui
    copie V_VALEUR dans squadreg.Selected DELAI_LIGNE s après son apparition"""
    attente = first(t, lambda r: typ(t, r) == "BindingExpect")
    if attente is None:
        return [f"{MODELE_LIGNE} : BindingExpect de FM introuvable"]
    for k in list(t.children(attente)):
        t.remove(k)
    params = copy.deepcopy(src.parametres)
    if [p["name"] for p in params] != [PARAM_LIGNE, "squadreg"]:
        return [f"{CELLULE} : paramètres inattendus (introuvable)"]
    v = copy.deepcopy(params[0])
    v["name"], v["type"] = V_VALEUR, {"id": 0}
    sd = t.sd(attente)
    sd["Parameters"], sd["Parameters_UxmlAttributeFlags"] = params + [v], 1
    t.elem(attente)["m_Classes"], t.elem(attente)["m_RuleIndex"] = [], -1
    nommer(t, attente, NOM_ECRIRE)
    delai(t, src, attente, f"{NOM_ECRIRE}-delai", DELAI_LIGNE, copier(V_VALEUR, CHEMIN_CIBLE))
    return [f"ligne de la liste cachée : écrit {V_VALEUR} dans {CHEMIN_CIBLE} ({DELAI_LIGNE} s après son apparition)"]


def modele_a_jour(nom, nom_marque):
    o = ouvrir(nom)
    return o is not None and any(o[3].name(r) == nom_marque for r in o[3].walk())


def modele_poser(nom, poser_fn):
    """un modèle à nous (cité par RIEN) refait depuis son original ; messages"""
    o = ouvrir(nom, depart_original=True)
    if o is None:
        return [f"{nom} introuvable"]
    msgs = poser_fn(o)
    if not any("introuvable" in m for m in msgs):
        enregistrer(*o)
    return msgs


def modele_rendre(nom):
    """le modèle à nous rendu d'origine (typetree et feuille de l'original) ; True si changé"""
    o = ouvrir(nom)
    if o is None or not marques(o[3]):
        return False
    oo = ouvrir(nom, depart_original=True)
    if oo is None:
        return False
    enregistrer(*oo)
    return True


# ---------- commandes ----------
def cmd_appliquer():
    fait, msgs = [], []
    # 1. composition
    ec = UnityPy.load(COMPOSITIONS)
    c = composition_poser(ec)
    if c is None:
        msgs.append(f"composition {COMPOSITION} introuvable ou changée : colonne des règles laissée")
    elif c:
        ecrire_bundle(ec, COMPOSITIONS)
        fait.append(f"affichage Large : règles sur {COLONNES_REGLES} colonnes de grille (FM : 4)")
    # 2. fabrique et vues
    ef = UnityPy.load(FABRIQUES)
    f = fabrique_poser(ef)
    if f is None:
        msgs.append(f"colonne {COLONNE} de {FABRIQUE} introuvable : colonne laissée")
    elif f:
        ecrire_bundle(ef, FABRIQUES)
        fait.append(f"colonne « Enr. » à {LARGEUR_COLONNE} unités, fixe"
                    + (" ; en-tête = celui de FM, titre masqué" if ESSAI_BOUTON else ""))
    ev = UnityPy.load(VUES)
    v, n = vues_poser(ev)
    if v:
        ecrire_bundle(ev, VUES)
        fait.append(f"{n} vues : colonne « Enr. » à {LARGEUR_COLONNE} unités")
    # 3. modèles (gameworld)
    o = ouvrir(CELLULE)
    if o is None:
        msgs.append(f"{CELLULE} introuvable")
    elif not cellule_a_jour(o[3]):
        cellule_rendre(o[3])
        m = cellule_poser(o[3])
        (msgs if any("introuvable" in x for x in m) else fait).extend(m)
        if not any("introuvable" in x for x in m):
            enregistrer(*o)
    o = ouvrir(REGLES_BLOC)
    if o is None:
        msgs.append(f"{REGLES_BLOC} introuvable")
    elif not regles_a_jour(o[3]):
        regles_rendre(o[3])
        m = regles_poser(o[3])
        (msgs if any("introuvable" in x for x in m) else fait).extend(m)
        if not any("introuvable" in x for x in m):
            enregistrer(*o)
    if ESSAI_BOUTON:
        src = Sources()
        if src.manque():
            msgs.append(f"morceaux de FM introuvables : {', '.join(src.manque())} : bouton d'en-tête laissé")
        else:
            if not modele_a_jour(MODELE_ENTETE, NOM_ENTETE):
                m = modele_poser(MODELE_ENTETE, lambda oo: entete_poser(oo[3], oo[2], src))
                (msgs if any("introuvable" in x for x in m) else fait).extend(m)
            if not modele_a_jour(MODELE_LIGNE, NOM_ECRIRE):
                m = modele_poser(MODELE_LIGNE, lambda oo: ligne_poser(oo[3], src))
                (msgs if any("introuvable" in x for x in m) else fait).extend(m)
            ob = ouvrir(BLOC)
            if ob is None:
                msgs.append(f"{BLOC} introuvable")
            elif not bloc_a_jour(ob[3]):
                oo = ouvrir(BLOC, depart_original=True)   # v3 : refait depuis l'original (seul 26.17 le touche)
                m = bloc_poser(oo[3], oo[2], src)
                (msgs if any("introuvable" in x for x in m) else fait).extend(m)
                if not any("introuvable" in x for x in m):
                    enregistrer(*oo)
    for m in fait + msgs:
        print(f"[Kinito] Enregistrement : {m}")
    if nb._dirty:
        nb.save_all()
    if not fait and not msgs:
        print("[Kinito] Enregistrement : déjà appliqué")
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as fh:
            json.dump({"actif": True}, fh)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    fait = False
    ec = UnityPy.load(COMPOSITIONS)
    if composition_retirer(ec):
        ecrire_bundle(ec, COMPOSITIONS)
        print(f"{COMPOSITION} : colonnes de FM rendues")
        fait = True
    ef = UnityPy.load(FABRIQUES)
    if fabrique_retirer(ef):
        ecrire_bundle(ef, FABRIQUES)
        print(f"{FABRIQUE} : colonne {COLONNE} rendue")
        fait = True
    ev = UnityPy.load(VUES)
    if vues_retirer(ev):
        ecrire_bundle(ev, VUES)
        print("vues : largeur de la colonne « Enr. » rendue")
        fait = True
    o = ouvrir(CELLULE)
    if o is not None and cellule_rendre(o[3]):
        enregistrer(*o)
        print(f"{CELLULE} : interrupteur de FM rendu")
        fait = True
    o = ouvrir(REGLES_BLOC)
    if o is not None and regles_rendre(o[3]):
        enregistrer(*o)
        print(f"{REGLES_BLOC} : boîte des tuiles de FM rendue")
        fait = True
    if bloc_rendre():
        print(f"{BLOC} : rendu d'origine (variables, sélection, zone cachée, interrupteur retirés)")
        fait = True
    for nom in (MODELE_ENTETE, MODELE_LIGNE):
        if modele_rendre(nom):
            print(f"{nom} : modèle de FM rendu d'origine")
            fait = True
    if nb._dirty:
        nb.save_all()
    if not fait:
        print("rien à retirer")


def cmd_etat():
    ec, ef, ev = UnityPy.load(COMPOSITIONS), UnityPy.load(FABRIQUES), UnityPy.load(VUES)
    print(f"{COMPOSITION} : " + (f"règles à {COLONNES_REGLES} colonnes (à jour)" if composition_a_jour(ec)
                                 else "de FM ou ANCIENNE"))
    print(f"{FABRIQUE} : colonne {COLONNE} " + ("réglée (à jour)" if fabrique_a_jour(ef) else "de FM ou ANCIENNE"))
    print("vues de la colonne « Enr. » : " + ("à jour" if vues_a_jour(ev) else "de FM ou ANCIENNES"))
    o = ouvrir(CELLULE)
    print(f"{CELLULE} : " + (f"interrupteur réduit (à jour, v{VERSION})" if o and cellule_a_jour(o[3])
                             else "de FM ou ANCIENNE"))
    o = ouvrir(REGLES_BLOC)
    print(f"{REGLES_BLOC} : " + ("boîte des tuiles en stretch (à jour)" if o and regles_a_jour(o[3])
                                 else "de FM ou ANCIENNE"))
    if ESSAI_BOUTON:
        ob = ouvrir(BLOC)
        print(f"{BLOC} : " + ("variables, sélection, zone cachée, interrupteur (à jour)" if ob and bloc_a_jour(ob[3])
                              else "de FM ou ANCIENNE"))
        print(f"{MODELE_ENTETE} : " + ("notre en-tête (à jour)" if modele_a_jour(MODELE_ENTETE, NOM_ENTETE)
                                       else "de FM ou ANCIEN"))
        print(f"{MODELE_LIGNE} : " + ("notre ligne (à jour)" if modele_a_jour(MODELE_LIGNE, NOM_ECRIRE)
                                      else "de FM ou ANCIENNE"))
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
            print("[Kinito] Enregistrement : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
