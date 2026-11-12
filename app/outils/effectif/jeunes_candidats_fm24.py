"""Jeunes à l'essai comme FM24 : message « De jeunes pousses à ... » de la boîte de réception et écran Effectif >
Jeunes candidats (le même bloc de FM). Tailles de FM27 gardées, seul le design change :

  [■ Candidats d'élite (2)               ]   (barre verte FM24, catégorie vide cachée)   | ★★★★★ Excellente      |
  [terrain] MO (G)      [photo] Nom          ★★  ★★★★★  [Offrir]                         | promotion + texte      |
            Ailier              ▪ Brésil                                                 | Potentiel des nouveaux |
                                                                                         | jeunes : poste / note  |

Modèles touchés (seul propriétaire, refaits depuis l'original à chaque version) :
- YouthCandidatesCategoryTable (une catégorie) : titre en barre de couleur selon le potentiel (CATEGORIES : vert, jaune, orange..., texte sombre, sans icône), mis dans le
  SIVisible « liste non vide » de FM (catégorie vide = rien du tout), en-tête du tableau caché (classe FM
  `streamed-table__header-hide`), lignes un peu plus hautes (mini-terrain).
  Écart entre catégories réduit à ECART_CATEGORIES (FM : 16 px de marge haut / bas même pour une catégorie vide).
- SquadYouthCandidatesTableBlock (#ActiveState) : traits entre catégories retirés (écart à la place), panneau à
  droite (note de la promo : étoiles, statut, texte = club.YouthCandidatesPreview, morceaux recopiés de
  YouthCandidatesTile_4x4 ; « Potentiel des nouveaux jeunes » = tableau des postes de l'aperçu de FM). Panneau caché
  si l'aperçu n'existe pas.
- Vue YouthCandidatesPortalTable (ui-tableviews, utilisée par ce seul tableau) : colonnes dans l'ordre FM24
  (COLONNES) ; retirer remet les colonnes d'origine (le reste du bundle n'est pas touché).
- PlayerScoutedBestPositionAndRoleAndWidgetCell (1re colonne ; ailleurs seulement dans la liste des joueurs libérés
  « waivers », ligues US) : terrain de FM réduit dans un cadre (comme la variante « rôle court » de FM, qui avait la
  place de 138 px de haut et débordait), à droite : poste (POSTE), rôle de prédilection dessous.

Usage : .venv\\Scripts\\python.exe outils\\effectif\\jeunes_candidats_fm24.py appliquer|retirer|etat|si-actif [--dry-run]
"""
import copy
import json
import os
import sys

import UnityPy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from langue import texte as L, SUFFIXE  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, Styles, make_visible  # noqa: E402
from elements import move, copy_usings  # noqa: E402
from notes_installations import decode_args, encode_args, _enc_varint  # noqa: E402


def _chaine(s):
    """chaîne telle que rangée dans les octets d'arguments (longueur en varint + texte)"""
    return _enc_varint(len(s.encode())) + s.encode()

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
# barre de chaque catégorie, du meilleur potentiel au moins bon (élite = vert mesuré sur FM24 : #0CF169)
CATEGORIES = [("EliteProspectsBinder", "#0CF169"), ("TopProspectsBinder", "#9BE22D"),
              ("GoodProspectsBinder", "#F2D33A"), ("DecentProspectsBinder", "#F0952E"),
              ("PoorProspectsBinder", "#E8503A")]
TEXTE_BARRE = (0.11, 0.11, 0.11, 1)                  # texte de la barre
# fond des 2 cadres du panneau de droite = celui des tuiles de FM (classe du fond d'une tuile sans clic, variable
# --layout-ui-tiles-interaction-surface-light-default, transparence comprise : se fond dans le skin, v9). v10 : pas
# « layout-tile-interaction-none » (même fond, mais aussi largeur / hauteur 100 % : le panneau sortait de sa tuile)
CLASSE_FOND_TUILE = "layout-tile-interaction-button-background"
COLONNES = ["scouted-best-position-and-role-and-widget", "player-portrait-name-nationality",
            "current-ability-stars", "potential-ability-stars", "contract-negotiation-link"]
HAUTEUR_LIGNE = 52        # px (36 dans FM27 : le mini-terrain de la 1re colonne n'y rentre pas)
TERRAIN = (34, 46)        # px, cadre du mini-terrain (largeur, hauteur)
ECHELLE_TERRAIN = 0.37    # terrain de FM (90 x 120 px) réduit pour tenir dans le cadre
POSTE = "binding.bestpositionshortstring"   # texte à côté du terrain (ex. « AT (C) »)
ROLE = "binding.coachbestrole"   # dessous : meilleur rôle selon l'adjoint (FM : binding.ScoutedBestRole = « Joueur »)
ROLE_FM = "binding.ScoutedBestRole"
LARGEUR_PANNEAU = 300     # px, panneau de droite (le tableau des postes de FM fait 288 px)
ECART = 12                # px, avant le panneau
ECART_CATEGORIES = 24    # px, entre deux catégories (FM : 16 px de marge haut / bas par catégorie, même vide)
TITRE_POTENTIEL = L("Potentiel des nouveaux jeunes", "Youth intake potential")
SOUS_TITRE_POTENTIEL = L("Poste de prédilection", "Preferred position")
# =====================================================================================================

MODELE_BLOC = "SquadYouthCandidatesTableBlock"
MODELE_CAT = "YouthCandidatesCategoryTable"
MODELE_CELLULE = "PlayerScoutedBestPositionAndRoleAndWidgetCell"
SOURCE_TUILE = "YouthCandidatesTile_4x4"
VUE = "YouthCandidatesPortalTable"
BUNDLE_VUES = os.path.join(nb.AA, "ui-tableviews_assets_all.bundle")
APERCU = "club.YouthCandidatesPreview"
COULEUR_CAT = "uipickercouleurcategorie"   # repère <i> : vrai seulement dans la catégorie i (barre de sa couleur)
TYPE_ETOILES = 1398035015          # type « starrange » (BindingRemapperComponent de la tuile)
VERSION = f"10{SUFFIXE}"          # à augmenter à chaque changement (langue : suffixe -en)
PREFIXE = "UIPickerJeunesFM24"


def rgba(h, k=1.0):
    return tuple(int(h[i:i + 2], 16) / 255 * k for i in (1, 3, 5)) + (1,)


NOM = f"{PREFIXE}-v{VERSION}"
MARKER = os.path.join(backup.BACKUP_DIR, "jeunes_candidats_fm24.actif")
for _nom, _id, _type in (("height", 131087, 3), ("width", 131105, 3), ("margin-left", 131091, 3),
                         ("margin-bottom", 131090, 3), ("margin-top", 131093, 3), ("padding-left", 131099, 3),
                         ("padding-right", 131100, 3), ("padding-top", 131101, 3), ("padding-bottom", 131098, 3),
                         ("border-radius", 262147, 3), ("color", 65536, 4), ("align-self", 131074, 7),
                         ("align-items", 131073, 7), ("flex-direction", 131083, 7), ("justify-content", 131088, 7),
("-unity-text-align", 65546, 7), ("white-space", 65552, 7),
("position", 131102, 7), ("left", 131089, 3), ("top", 131104, 3), ("right", 131103, 3), ("bottom", 131080, 3)):
    sm.PROPRIETES.setdefault(_nom, (_id, _type))


def typ(t, r):
    return (t.elem(r).get("m_FullTypeName") or "").split(".")[-1]


def first(t, pred, root=None):
    return next((r for r in t.walk(root) if pred(r)), None)


def plain(t, model, parent, cls, index=None, name=""):
    """conteneur vide copié de model (sans enfants, sans style intégré)"""
    r = t.clone_shallow(model, parent, index)
    t.elem(r)["m_Classes"] = list(cls)
    t.elem(r)["m_RuleIndex"] = -1
    t.sd(r)["name"] = name
    t.sd(r)["name_UxmlAttributeFlags"] = 1 if name else 0
    return r


def nommer(t, r, nom):
    t.sd(r)["name"], t.sd(r)["name_UxmlAttributeFlags"] = nom, 1


# ---------- une catégorie ----------
def construire_categorie(t):
    titre = first(t, lambda r: t.name(r) == "Frame_TItle")
    icone = titre and first(t, lambda r: "game-concepts-idolise_small" in (t.elem(r).get("m_Classes") or []), titre)
    texte = titre and first(t, lambda r: typ(t, r) == "SIText", titre)
    vis = first(t, lambda r: t.name(r) == "SIVisibleTable")
    table = first(t, lambda r: typ(t, r) == "StreamedTable")
    if None in (titre, icone, texte, vis, table):
        return ["repères introuvables (catégorie de FM changée ?), ignoré"]
    t.remove(icone)
    # barre dans le SIVisible « liste non vide » : une catégorie vide ne montre plus son titre
    move(t, titre, vis, 0)
    nommer(t, titre, NOM)
    t.elem(titre)["m_Classes"] = list(t.elem(titre)["m_Classes"]) + ["align-self-stretch-class"]
    t.styles.style(t, titre, {"border-radius": 3, "padding-left": 8, "padding-right": 8,
                              "padding-top": 4, "padding-bottom": 4, "margin-bottom": 4})
    t.styles.style(t, texte, {"color": TEXTE_BARRE})
    # fond de la barre : un calque par catégorie, posé derrière le texte, visible seulement dans la sienne (repère
    # COULEUR_CAT<i> relié par le bloc). Une seule barre : FM écrit le titre dans le 1er #text qu'il trouve
    for i, (_, couleur) in enumerate(CATEGORIES):
        v = make_visible(t, vis, titre, i, f"{COULEUR_CAT}{i}", f"couleur{i}", [])
        t.elem(v)["m_RuleIndex"] = -1
        t.styles.style(t, v, {"position": "absolute", "left": 0, "top": 0, "right": 0, "bottom": 0})
        # couleur sur un enfant qui remplit le SIVisible (le fond du SIVisible lui-même n'est pas dessiné en jeu, v7)
        fond = plain(t, titre, v, [])
        t.styles.style(t, fond, {"flex-grow": 1, "align-self": "stretch", "background-color": rgba(couleur),
                                 "border-radius": 3})
    # écart entre catégories : porté par le SIVisible seul (FM : 16 px haut / bas sur le cadre, même catégorie vide)
    t.styles.style(t, t.parent[vis], {"padding-top": 0, "padding-bottom": 0})
    t.styles.style(t, vis, {"margin-bottom": ECART_CATEGORIES, "align-self": "stretch"})
    # tableau : sans en-tête (Joueur / Nation / ...), lignes à la hauteur du mini-terrain
    t.elem(table)["m_Classes"] = list(t.elem(table).get("m_Classes") or []) + ["streamed-table__header-hide"]
    t.sd(table)["FixedElementSize"] = float(HAUTEUR_LIGNE)
    return ["barres de couleur selon le potentiel, catégorie vide cachée, tableau sans en-tête, écart réduit"]


# ---------- le bloc ----------
def construire_bloc(t):
    actif = first(t, lambda r: t.name(r) == "ActiveState")
    scroll = actif and first(t, lambda r: typ(t, r) == "SIScrollView", actif)
    binder = first(t, lambda r: t.name(r) == "EliteProspectsBinder")
    texte = first(t, lambda r: typ(t, r) == "SIText")
    modele_vis = first(t, lambda r: t.name(r) == "PreviewState")
    s, s_bundle = None, None
    b, _, stt = nb.find_vta(SOURCE_TUILE)
    if stt is not None:
        s, s_bundle = Tree(stt), b
    if None in (actif, scroll, binder, texte, modele_vis, s):
        return ["repères introuvables (bloc de FM changé ?), ignoré"]
    st = Styles(s_bundle, s.tt)
    preview = first(s, lambda r: s.name(r) == "Preview")
    cadre = preview and first(s, lambda r: s.name(r) == "main-frame", preview)
    statut = cadre and first(s, lambda r: typ(s, r) == "SIText", cadre)
    etoiles = cadre and first(s, lambda r: s.elem(r).get("m_TemplateAlias") == "stats-star-ratings", cadre)
    desc = cadre and next((r for r in s.walk(cadre) if typ(s, r) == "SIText" and r != statut), None)
    postes = preview and [r for r in s.walk(preview) if typ(s, r) == "StreamedTable"]
    if None in (cadre, statut, etoiles, desc) or not postes:
        return [f"morceaux de {SOURCE_TUILE} introuvables, ignoré"]

    def copie(rid, parent):
        r = t.clone(rid, parent, None, src=s)
        copy_usings(t, s, rid)
        t.styles.copy_from(st, t, r)
        return r

    # couleur de la barre : chaque catégorie allume son repère COULEUR_CAT<i> (= sa liste, non nulle) ; les autres
    # repères ne sont pas reliés (nuls) -> une seule barre visible
    for i, (nom_binder, _) in enumerate(CATEGORIES):
        rb = first(t, lambda r: t.name(r) == nom_binder)
        maps = rb and t.sd(rb)["Mappings"]
        liste = maps and next((m for m in maps if m["from"] == "playerlist"), None)
        if liste is None:
            return [f"{nom_binder} introuvable (bloc de FM changé ?), ignoré"]
        m = copy.deepcopy(liste)
        m["from"] = f"{COULEUR_CAT}{i}"
        maps.append(m)
    # traits de FM entre les catégories retirés (l'écart est porté par chaque catégorie non vide)
    for r in list(t.children(scroll)):
        if t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal":
            t.remove(r)
    # rangée : catégories | panneau
    rangee = plain(t, actif, actif, ["row-direction-normal", "flex-grow-class"], t.children(actif).index(scroll),
                   name=NOM)
    move(t, scroll, rangee)
    t.styles.style(t, scroll, {"flex-grow": 1, "flex-shrink": 1})
    panneau = make_visible(t, modele_vis, rangee, None, APERCU, f"{PREFIXE}-panneau", [])
    t.elem(panneau)["m_RuleIndex"] = -1
    t.styles.style(t, panneau, {"width": LARGEUR_PANNEAU, "min-width": LARGEUR_PANNEAU, "flex-shrink": 0,
                                "margin-left": ECART})
    # note de la promo : étoiles, statut (« Excellente promotion »), texte
    note = plain(t, actif, panneau, ["align-items-center", "padding-horizontal-global-padding-regular",
                                     "padding-vertical-global-padding-regular", CLASSE_FOND_TUILE])
    t.styles.style(t, note, {"border-radius": 3})
    remap = t.clone_shallow(binder, note)
    t.elem(remap)["m_RuleIndex"] = -1
    t.elem(remap)["m_Classes"] = ["align-items-center"]
    t.sd(remap)["name"], t.sd(remap)["name_UxmlAttributeFlags"] = "", 0
    t.sd(remap)["Mappings"] = [{"m_serialisedType": 0, "from": "starrating",
                                "to": {"m_path": APERCU + ".YouthIntakeRating"}, "type": {"id": TYPE_ETOILES}}]
    e = copie(etoiles, remap)
    t.elem(e)["m_Classes"] = []
    for r, cls in ((copie(statut, note), ["heading-md", "global-text-primary"]),
                   (copie(desc, note), ["body-sm", "global-text-secondary"])):
        t.elem(r)["m_Classes"] = cls
        t.elem(r)["m_RuleIndex"] = -1
        t.styles.style(t, r, {"-unity-text-align": "middle-center", "white-space": "normal", "margin-top": 4})
    # potentiel des nouveaux jeunes : tableau des postes de l'aperçu de FM (mini-terrain + note par poste)
    pot = plain(t, actif, panneau, ["padding-horizontal-global-padding-regular",
                                    "padding-vertical-global-padding-regular", "flex-grow-class", CLASSE_FOND_TUILE])
    t.styles.style(t, pot, {"border-radius": 3, "margin-top": 8})
    for txt, cls in ((TITRE_POTENTIEL, ["body-sm-strong", "global-text-primary"]),
                     (SOUS_TITRE_POTENTIEL, ["body-sm", "global-text-secondary"])):
        r = t.clone(texte, pot)
        sd = t.sd(r)
        sd["text"], sd["text_UxmlAttributeFlags"], sd["DebugDisplay"] = txt, 1, txt
        sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
        sd["TextBinding"]["m_kind"] = 0
        sd["TextBinding"]["m_direct"]["Path"]["m_path"] = ""
        t.elem(r)["m_Classes"] = cls
        t.elem(r)["m_RuleIndex"] = -1
    tab = copie(postes[-1], pot)
    # toute la liste des postes (la tuile n'en montre que quelques-uns)
    t.sd(tab)["Binding"] = {"m_kind": 1, "m_direct": {"Path": {"m_path": APERCU + ".YouthIntakePositionPreviews"},
                                                      "Nullable": 0},
                            "m_visualFunction": {"m_target": {"m_guid": ""},
                                                 "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                 "m_outputs": {"m_variable": {"m_argumentBytes": []}}}}
    t.elem(tab)["m_Classes"] = ["flex-grow-class", "margin-top-global-gap-small"]
    t.elem(tab)["m_RuleIndex"] = -1
    return ["traits retirés, panneau de droite (note de la promo, potentiel par poste)"]


# ---------- 1re colonne : mini-terrain + poste ----------
def construire_cellule(t):
    ligne = first(t, lambda r: t.name(r).startswith("data_display-cell-combo"))
    cadre = first(t, lambda r: t.name(r) == "role_selector-standard")
    terrain = cadre and first(t, lambda r: t.name(r) == "Frame", cadre)
    textes = first(t, lambda r: t.name(r) == "frame")
    vide = textes and first(t, lambda r: t.name(r) == "data_display-cell-standard-small", textes)
    role = textes and first(t, lambda r: typ(t, r) == "SIText", textes)
    if None in (ligne, cadre, terrain, textes, vide, role):
        return ["repères introuvables (cellule de FM changée ?), ignoré"]
    # en ligne (FM : colonne, le texte passait sous le terrain), centré en hauteur
    t.styles.style(t, ligne, {"height": HAUTEUR_LIGNE, "flex-direction": "row", "align-items": "center"})
    # cadre fixe (fond sombre et bord du petit terrain de FM), terrain réduit centré dedans
    t.elem(cadre)["m_Classes"] = ["data_display-positions-suitability-extra-small-pitch",
                                  "center-align-and-justify-children"]
    t.elem(cadre)["m_RuleIndex"] = -1
    t.styles.style(t, cadre, {"width": TERRAIN[0], "height": TERRAIN[1], "flex-shrink": 0, "overflow": "hidden"})
    t.elem(terrain)["m_RuleIndex"] = t.styles.add_rule([
        (131105, "", [(3, 90)]), (131087, "", [(3, 120)]), (131085, "", [(2, 0)]),
        (327681, "", [(2, ECHELLE_TERRAIN), (2, ECHELLE_TERRAIN)])])   # scale
    # à droite du terrain : poste, rôle de prédilection dessous (copie du texte du rôle de FM)
    t.remove(vide)
    move(t, textes, ligne, t.children(ligne).index(cadre) + 1)   # FM : sous la ligne du terrain (bloc voisin)
    nommer(t, textes, NOM)
    t.styles.style(t, textes, {"flex-direction": "column", "margin-left": 8, "align-items": "flex-start",
                               "justify-content": "center", "flex-shrink": 1, "min-width": 0})
    ligne_role = t.parent[role]
    copie = t.clone(ligne_role, textes, t.children(textes).index(ligne_role) + 1)
    # rôle « recruteurs » (ScoutedBestRole) = « Joueur » pour un jeune pas encore observé -> meilleur rôle selon
    # l'adjoint (colonne FM assistant-opinion-best-role)
    texte_role = first(t, lambda r: typ(t, r) == "SIText", copie)
    b = copy.deepcopy(t.sd(texte_role)["TextBinding"])
    vf = b["m_visualFunction"]["m_inputs"]["m_variable"]
    args = decode_args(vf["m_argumentBytes"])
    for a in args:
        a[1] = a[1].replace(_chaine(ROLE_FM), _chaine(ROLE))
    vf["m_argumentBytes"] = encode_args(args)
    t.sd(texte_role)["TextBinding"] = b
    sd = t.sd(role)
    sd["TextBinding"] = copy.deepcopy(sd["TextBinding"])
    sd["TextBinding"]["m_kind"] = 1
    sd["TextBinding"]["m_direct"]["Path"]["m_path"] = POSTE
    sd["DebugDisplay"] = "Position"
    for r in (role, t.parent[role]):
        t.elem(r)["m_Classes"] = [c for c in t.elem(r)["m_Classes"] if c not in ("global-text-secondary", "body-sm")]
    t.elem(role)["m_Classes"] = t.elem(role)["m_Classes"] + ["body-md"]
    return ["mini-terrain dans un cadre, poste et rôle à droite"]


# ---------- ouverture / enregistrement des modèles ----------
def original(bundle, path_id):
    if not os.path.exists(backup.backup_path(bundle)):
        return None
    o = next((x for x in UnityPy.load(backup.backup_path(bundle)).objects if x.path_id == path_id), None)
    return o.read_typetree() if o is not None else None


def ouvrir(modele, depart_original=False):
    bundle, obj, tt = nb.find_vta(modele)
    if tt is None:
        return None
    sheet = None
    if depart_original:
        orig = original(bundle, obj.path_id)
        if orig is not None:
            tt = orig
            sheet = original(bundle, tt["inlineSheet"]["m_PathID"])
    t = Tree(tt)
    t.styles = Styles(bundle, tt)
    if sheet is not None:   # feuille d'origine aussi : les règles des versions précédentes ne s'empilent pas
        t.styles.sh, t.styles.changed = sheet, True
    return bundle, obj, tt, t


def blocs(t):
    return [t.name(r) for r in t.walk() if t.name(r).startswith(PREFIXE) and not t.name(r).endswith("-panneau")]


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


# ---------- vue du tableau (ui-tableviews) ----------
def vue(env):
    for o in env.objects:
        if o.type.name == "MonoBehaviour":
            try:
                if o.peek_name() == VUE:
                    return o, o.read_typetree()
            except Exception:
                continue
    return None, None


def colonnes(tt):
    return [c["m_columnID"] for c in tt["m_tableView"]["m_tableConfig"]]


def poser_colonnes():
    env = nb.env_of(BUNDLE_VUES)
    o, tt = vue(env)
    if tt is None:
        return f"{VUE} : introuvable, ignoré"
    if colonnes(tt) == COLONNES:
        return None
    orig = original(BUNDLE_VUES, o.path_id) or tt
    par_id = {c["m_columnID"]: c for c in orig["m_tableView"]["m_tableConfig"] + tt["m_tableView"]["m_tableConfig"]}
    modele = orig["m_tableView"]["m_tableConfig"][0]
    config = []
    for cid in COLONNES:
        c = copy.deepcopy(par_id.get(cid) or modele)
        c["m_columnID"] = cid
        if cid not in par_id:   # colonne absente de la vue de FM : métadonnées neutres
            m = c["m_columnMetadata"]
            m.update(m_widthOverride=0.0, m_minWidthOverride=0.0, m_applicableBreakpoints=-1, m_sortingDisabled=0)
            m["m_titleTranslationIdOverride"] = {"GameID": 0}
        config.append(c)
    tt["m_tableView"]["m_tableConfig"] = config
    o.save_typetree(tt)
    nb._dirty.add(BUNDLE_VUES)
    return f"{VUE} : colonnes dans l'ordre FM24"


def remettre_colonnes():
    env = nb.env_of(BUNDLE_VUES)
    o, tt = vue(env)
    if tt is None or colonnes(tt) != COLONNES:
        return None
    orig = original(BUNDLE_VUES, o.path_id)
    if orig is None:
        return f"{VUE} : pas d'original, colonnes laissées"
    tt["m_tableView"]["m_tableConfig"] = orig["m_tableView"]["m_tableConfig"]
    o.save_typetree(tt)
    nb._dirty.add(BUNDLE_VUES)
    return f"{VUE} : colonnes d'origine remises"


# ---------- commandes ----------
TRAVAUX = [(MODELE_CAT, construire_categorie), (MODELE_BLOC, construire_bloc), (MODELE_CELLULE, construire_cellule)]


def cmd_appliquer():
    for modele, construire in TRAVAUX:
        x = ouvrir(modele)
        if x is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        old = blocs(x[3])
        if old == [NOM]:
            print(f"{modele} : déjà appliqué")
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if blocs(t):   # pas de sauvegarde d'origine : on ne relance pas par-dessus
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        msgs = construire(t)
        for m in msgs + (["ancienne version remplacée"] if old else []):
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
    m = poser_colonnes()
    print(m or f"{VUE} : déjà appliqué")
    nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    rien = True
    for modele, _ in TRAVAUX:
        x = ouvrir(modele)
        if x is None or not blocs(x[3]):
            continue
        bundle, obj, tt, t = x
        orig = original(bundle, obj.path_id)
        if orig is None:
            print(f"{modele} : pas d'original, impossible de le remettre (Steam : vérifier l'intégrité)")
            continue
        sheet = original(bundle, orig["inlineSheet"]["m_PathID"])
        if sheet is not None:
            t.styles.sh, t.styles.changed = sheet, True
            t.styles.save()
        obj.save_typetree(orig)
        nb._dirty.add(bundle)
        rien = False
        print(f"{modele} : remis d'origine")
    m = remettre_colonnes()
    if m:
        print(m)
        rien = False
    if rien:
        print("rien à retirer")
        return
    nb.save_all()


def cmd_etat():
    for modele, _ in TRAVAUX:
        x = ouvrir(modele)
        if x is None:
            print(f"{modele} : introuvable")
            continue
        old = blocs(x[3])
        print(f"{modele} : " + (f"appliqué ({', '.join(old)} ; version actuelle v{VERSION})" if old else "d'origine"))
    _, tt = vue(nb.env_of(BUNDLE_VUES))
    print(f"{VUE} : " + ("introuvable" if tt is None else
                         "colonnes FM24" if colonnes(tt) == COLONNES else "colonnes d'origine"))
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
            print("jeunes à l'essai FM24 : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
