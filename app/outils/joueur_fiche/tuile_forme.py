"""Infobulle du joueur (survol, la « pop-out » du joueur), demande du joueur, 2026-11-12 :
- tuile « État d'esprit » (PlayerHappinessTooltipBlock) -> « État du joueur » : physique / mental, centrés ;
- Infos (PlayerAttributesTooltipBlock) : logos Hiérarchie / Groupe social à droite de Taille, plus petits.
Tuiles de la fiche normale (2026-11-12) : État d'esprit (PlayerHappinessTile_*) = le mental de l'infobulle, Condition
(PlayerFitnessTile_2x1 / 2x2 / 4x2) = le physique de l'infobulle (GRILLE_MENTAL / GRILLE_PHYSIQUE).

- en haut : physique = condition, forme de match, fatigue (icônes des tableaux de joueurs, comme celles d'Infos) ;
- trait de FM ;
- dessous : mental = état d'esprit (smiley) + moral (boussole) et le mot de FM (« Parfait »...), et à droite sur la
  même ligne les logos Hiérarchie / Groupe social (ceux de l'onglet Personnel, libellé au survol).
Points + / Points − de FM retirés (coupés dans la tuile). Pour / Contre, Infos : pas touchés.

Repart toujours du modèle d'origine (sauvegarde). Repérage par contenu (noms FM, chemins de données).
Usage (jeu fermé) : tuile_forme.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import Tree, Styles, FIXE  # noqa: E402
from elements import src_tree, first, typ, move, plain, copy_usings, set_text_binding  # noqa: E402,F401
from attributs_tout_cocher import ouvrir  # noqa: E402  (modèle d'origine + sa feuille de style)
import fiche_joueur_plus as fjp  # noqa: E402  (icônes et logos d'Infos : mêmes cellules / modèles de FM)
from langue import texte as L  # noqa: E402
from arbre import named, PROPRIETES  # noqa: E402

PROPRIETES.setdefault("align-self", (131074, 7))
PROPRIETES.setdefault("width", (131105, 3))
PROPRIETES.setdefault("height", (131087, 3))
PROPRIETES.setdefault("margin-left", (131091, 3))
PROPRIETES.setdefault("margin-right", (131092, 3))

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
ECART_GROUPES = 10         # px au-dessus et en dessous du trait entre physique et mental (v5 : 6 -> 10, mieux remplir)
LOGOS_TAILLE_INFOS = 18    # px des logos Hiérarchie / Groupe à droite de Taille dans l'infobulle (FM : 24, le joueur :
                           # « un peu plus petits seulement sur cette fiche »)
# =====================================================================================================

# tuile « État d'esprit » de la fiche en fenêtre pop-out (v2, le joueur : seulement celle-là ; console 2026-11-12 :
# la pop-out n'affiche pas les tuiles de grille)
MODELES = ["PlayerHappinessTooltipBlock"]
# tuiles de grille de la fiche normale (2026-11-12, le joueur : comme l'infobulle, moral et physique séparés) :
# État d'esprit = smiley + boussole du moral + mot de FM (Points + / − de FM gardés dessous) ; Condition = condition /
# forme / fatigue à la place de la grande icône (textes de FM gardés). Condition 4x4 / 8x4 : FM y montre déjà les
# trois avec leurs textes, pas touchées
GRILLE_MENTAL = ["PlayerHappinessTile_2x2", "PlayerHappinessTile_4x2", "PlayerHappinessTile_4x4"]
# grille-v5 (le joueur : « jamais demandé de modifier la tuile en Large », trop étroite) : Condition seulement en 4x2
# (celle du mode Small) ; grille-v8 (2026-11-01, le joueur : « inspire-toi de celle en Small pour les autres », « en
# Medium y a la place ») : 2x2 (Medium / Large) aussi ; en Large (étroite) : les icônes et le texte le plus petit
GRILLE_PHYSIQUE = ["PlayerFitnessTile_2x2", "PlayerFitnessTile_4x2"]
REMISES_FM = ["PlayerFitnessTile_2x1"]
ANCIENS = GRILLE_MENTAL + GRILLE_PHYSIQUE + REMISES_FM   # retirer : remises d'origine
VERSION_GRILLE = "uipicker-tuile-grille-v9"# changer le numéro refait les tuiles de grille (v2 : icônes en
                                               # grand avec leur texte, condition à gauche, forme / fatigue + statut ;
                                               # v7 : Small, forme / fatigue collées au texte, trait d'État d'esprit
                                               # au milieu ; v8 : Condition comme en Small dans tous les modes, 2x2 en
                                               # Large = icônes + petit texte ; v9 : logos Hiérarchie / Groupe social
                                               # dans État d'esprit, 2x2 en Large = 4 icônes sans texte)
LOGOS_ECART_LARGE = 20                         # px entre [smiley, boussole] et [logos] (2x2 en Large, sans texte)
LOGOS_ECART_TEXTE = 12                         # px minimum entre les textes et les logos (hors Large)
LOGOS_MARGE_DROITE = 20                        # px entre les logos et le bord droit de la tuile (hors Large)
TEXTE_LARGE = {"tifo-h": "body-sm", "heading-md": "body-sm", "tifo-p": "body-sm", "body-md": "body-sm"}
                                               # 2x2 en Large : classes de texte de FM -> la plus petite
SOURCE_STATUTS = "PlayerFitnessTile_4x4"       # grande tuile Condition de FM : textes de statut forme / fatigue
TAILLE_GRANDE = 24                             # px : condition, état d'esprit, moral (icônes FM des tableaux : 16)
TAILLE_PETITE = 18                             # px : forme et fatigue sous la condition
CASE_ICONE = 28                                # px : case commune des icônes (textes alignés les uns sous les autres)
MARKER = os.path.join(backup.BACKUP_DIR, "tuile_forme.actif")
PREFIXE = "UIPickerTuileForme"
VERSION = "uipicker-tuile-forme-v6"     # changer le numéro refait la tuile (v2 : pop-out au lieu des tuiles de grille ;
                                         # v3 : titre « État du joueur » ; v4 : logos sortis, contenu centré ;
                                         # v5 : centré en hauteur, écarts 10 ; v6 : calé en bas)
# infobulle du joueur (la « pop-out ») : logos Hiérarchie / Groupe à droite de Taille, ajoutés par-dessus le bloc
INFOBULLE = "PlayerAttributesTooltipBlock"
NOM_LOGOS_INFOS = "UIPickerLogosTaille"
VERSION_LOGOS_INFOS = "uipicker-logos-taille-v2"   # v2 : l'un sur l'autre, bas du rond = bas de la valeur
TITRE = ("État du joueur", "Player status")   # titre fixe (FR, autres langues) à la place de « État d'esprit »
JOUEUR = "player"                        # paramètre de la tuile (une personne)
# (cellule, liens) des icônes d'Infos, chemins de la fiche (person) -> ceux de la tuile (player)
PHYSIQUE = ["PlayerConditionIconCell", "PlayerSharpnessCell", "PlayerFatigueIconCell"]
MENTAL = ["PlayerHappinessCellOnlyIcon", "PlayerMoraleCellNoText"]
HUMEUR = "HierarchyOverallHappinessLevel"   # grande icône + mot de FM (« Parfait ») : le mot est gardé


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def titre(t):
    return first(t, lambda r: t.name(r) == "title-text" and typ(t, r).endswith("SIText"))


def poser_titre(t):
    """titre de FM (traduction « État d'esprit ») -> texte fixe dans la langue du skin"""
    r = titre(t)
    if r is None:
        return
    xd = t.sd(r)
    tb = xd["TextBinding"]
    tb["m_kind"] = 0
    tb["m_direct"] = {"Path": {"m_path": ""}, "Nullable": 0}
    tb["m_visualFunction"] = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                              "m_outputs": {"m_variable": {"m_argumentBytes": []}}}
    xd.update(text=L(*TITRE), text_UxmlAttributeFlags=1, DebugDisplay=L(*TITRE))


def a_jour(t):
    """version actuelle posée, titre dans la langue actuelle (sinon refait : changement de langue)"""
    r = titre(t)
    return any(VERSION in (t.elem(m).get("m_Classes") or []) for m in marques(t)) \
        and (r is None or t.sd(r).get("text") == L(*TITRE))


def liens_tuile(liens, base=JOUEUR):
    return {p: (base + chemin[len("person"):], ty) for p, (chemin, ty) in liens.items()}


def icones(t, parent, noms, ns, rm_note, taille=None, case=None, base=JOUEUR):
    """cellules FM des tableaux (icône seule), chacune dans un BindingRemapper vidé (paramètres -> joueur de la tuile),
    case fixe centrée de la largeur mesurée pour Infos (écarts visibles égaux) ; taille : case et image carrées de
    taille px (icônes agrandies des tuiles de grille) ; base : chemin de la personne (infos_cartes_terrain)"""
    table = {m: (i, liens) for i, (m, liens) in enumerate(fjp.ICONES)}
    for nom in noms:
        if nom not in table:
            return f"{nom} absent des icônes d'Infos"
        i, liens = table[nom]
        bundle, _, stt = nb.find_vta(nom)
        if stt is None:
            return f"{nom} introuvable (le jeu a changé ?)"
        s = Tree(stt)
        racine = s.children(s.tt["m_VisualTree"]["rid"])[0]
        rm = t.clone(rm_note, parent, src=ns)
        for k in list(t.children(rm)):
            t.remove(k)
        t.elem(rm)["m_Classes"] = ["column-direction-normal"]
        t.elem(rm)["m_RuleIndex"] = -1
        t.sd(rm)["name"] = ""
        t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": p, "to": {"m_path": chemin}, "type": {"id": ty}}
                                for p, (chemin, ty) in liens_tuile(liens, base).items()]
        w = fjp.ICONE_LARGEURS[i] if i < len(fjp.ICONE_LARGEURS) else fjp.ICONE_CASE
        h = fjp.ICONE_CASE
        if taille:   # case : largeur commune (textes alignés quelle que soit la taille de l'icône)
            w = h = case or taille + 4
        t.styles.style(t, rm, {"width": w, "height": h, "min-width": w, **FIXE,
                               "align-items": "center", "justify-content": "center"})
        c = t.clone(racine, rm, src=s)
        copy_usings(t, s, racine)
        t.styles.copy_from(Styles(bundle, stt), t, c)
        for r in t.walk(c):
            cls = t.elem(r).get("m_Classes") or []
            t.elem(r)["m_Classes"] = [k for k in cls if not k.startswith(fjp.ICONE_CLASSES_RETIREES)]
            if taille and (typ(t, r).endswith(("SIImage", "SIStyleSetter"))):   # l'image elle-même, agrandie
                t.styles.style(t, r, {"width": taille, "height": taille, "min-width": taille, **FIXE})
    return None


def logos(t, rm, bulle=True, taille=None, en_ligne=False, case=None):
    """logos Hiérarchie / Groupe social (BindingSetter de l'onglet Personnel recopié : sans info, rien) dans le
    conteneur rm (où « person » existe) ; textes retirés, libellé au survol si bulle ; taille = px de l'image ;
    case = hauteur px de chaque ligne (alignée sur les cases des icônes)"""
    fs = src_tree(fjp.GROS_BLOC)
    tip = first(fs, lambda r: typ(fs, r) == "SI.Bindable.Tooltip" and len(fs.children(r)) == 1
                and typ(fs, fs.children(r)[0]) == "SI.Bindable.SIText") if fs else None
    if bulle and tip is None:
        return "modèle d'infobulle introuvable"
    for i, (model, label) in enumerate(fjp.LOGOS_SOURCES):
        bundle, _, stt = nb.find_vta(model)
        s = Tree(stt) if stt is not None else None
        setter = first(s, lambda r: s.name(r) == "BindingDataSetter") if s else None
        if setter is None:
            return f"{model} introuvable (le jeu a changé ?)"
        new = t.clone(setter, rm, src=s)
        t.sd(new)["name"] = ""
        t.styles.copy_from(Styles(bundle, stt), t, new)   # taille de l'image (24 px)
        for r in [r for r in t.walk(new) if typ(t, r) == "SI.Bindable.SIText"]:
            t.remove(r)
        img = next(r for r in t.walk(new) if typ(t, r) == "SI.Bindable.SIImage")
        frame = t.parent[img]
        t.elem(img)["m_Classes"] = []
        if taille:
            t.styles.style(t, img, {"width": taille, "height": taille, "min-width": taille, **FIXE})
        ecart = "margin-right-global-gap-small" if en_ligne else "margin-bottom-global-gap-small"
        t.elem(frame)["m_Classes"] = ["row-direction-normal", "align-items-center"] \
            + ([ecart] if i < len(fjp.LOGOS_SOURCES) - 1 else [])
        if case:
            t.styles.style(t, frame, {"height": case, "min-height": case, "justify-content": "center"})
        if bulle:
            fb, _, ftt = nb.find_vta(fjp.GROS_BLOC)
            tt = t.clone(tip, frame, src=fs)
            t.styles.copy_from(Styles(fb, ftt), t, tt)
            text = t.children(tt)[0]
            t.sd(text)["name"] = ""
            set_text_binding(t, text, {"m_kind": 1, "m_direct": {"Path": {"m_path": label}, "Nullable": 0},
                                       "m_visualFunction": {"m_target": {"m_guid": ""},
                                                            "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                            "m_outputs": {"m_variable": {"m_argumentBytes": []}}}})
    return None


def construire(t):
    """tuile d'origine -> [physique] / trait / [mental | logos] ; renvoie les messages"""
    # grande icône de FM : image (tuiles de grille) ou icône du moral (pop-out, modèle inclus)
    humeur = first(t, lambda r: (typ(t, r) == "SI.Bindable.SIImage" and t.name(r) == "ui concepts-placeholder")
                   or t.elem(r).get("m_TemplateAlias") == "scaling-icons-form-small")
    trait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal")
    if humeur is None or trait is None:
        return ["icône d'état d'esprit ou trait de FM introuvable, ignoré"]
    cadre = t.parent[humeur]              # ComponentElement #Frame : icône + mot (« Parfait »)
    contenu = t.parent[cadre]             # [titre (pop-out)], cadre, trait, Points + / −
    kids = t.children(contenu)
    points = kids[kids.index(trait) + 1:]
    ns = src_tree(fjp.NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == fjp.NOTE_ENTRAINEMENT) if ns else None
    if note is None:
        return ["modèle de liaison introuvable, ignoré"]
    rm_note = ns.parent[note]

    # physique, en haut, centré
    phys = plain(t, contenu, kids.index(cadre), ["row-direction-normal", "align-items-center", VERSION],
                 PREFIXE + "Physique")
    t.elem(phys)["m_RuleIndex"] = -1
    t.styles.style(t, phys, {**FIXE, "margin-bottom": ECART_GROUPES, "align-self": "stretch",
                             "justify-content": "center"})
    err = icones(t, phys, PHYSIQUE, ns, rm_note)
    if err:
        return [err + ", ignoré"]
    t.styles.style(t, trait, {"margin-bottom": ECART_GROUPES})

    # mental, sous le trait, centré : [smiley, boussole] puis le mot de FM ; Points + / − retirés
    # (v5 : logos Hiérarchie / Groupe sortis de la tuile, dans les Infos de l'infobulle : infos_logos)
    for k in points:
        t.remove(k)
    ment = plain(t, contenu, None, ["column-direction-normal", "align-items-center"], PREFIXE + "Mental")
    t.elem(ment)["m_RuleIndex"] = -1
    t.styles.style(t, ment, {**FIXE, "align-self": "stretch"})
    move(t, cadre, ment)
    t.elem(cadre)["m_Classes"] = ["column-direction-normal", "align-items-center"]
    for r in t.children(cadre):   # le mot : entier et centré (le joueur : jamais coupé, « Exceptionnel » compris)
        if typ(t, r).endswith("SIText"):
            t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or [] if c != "content-ellipsis"]
    rang = plain(t, cadre, t.children(cadre).index(humeur), ["row-direction-normal", "align-items-center",
                                                             "margin-bottom-global-gap-small"], PREFIXE + "Icones")
    t.elem(rang)["m_RuleIndex"] = -1
    t.remove(humeur)   # grande icône de FM : la boussole du moral la remplace (même icône, en petit)
    err = icones(t, rang, MENTAL, ns, rm_note)
    if err:
        return [err + ", ignoré"]
    # v6 : vide libre entre le titre et le physique seulement (v5 : centré en hauteur, le joueur : « le bas a encore
    # trop d'espace » : la marge de la tuile + le bas de ligne du mot s'ajoutaient en bas)
    vide = plain(t, contenu, t.children(contenu).index(phys), [])
    t.elem(vide)["m_RuleIndex"] = -1
    t.styles.style(t, vide, {"flex-grow": 1})
    poser_titre(t)
    return ["physique (condition, forme, fatigue) / mental (état d'esprit, moral + mot de FM), centrés"]


def sources_liaison():
    ns = src_tree(fjp.NOTE_SOURCE)
    note = first(ns, lambda r: ns.elem(r).get("m_TemplateAlias") == fjp.NOTE_ENTRAINEMENT) if ns else None
    return (ns, ns.parent[note]) if note is not None else (None, None)


def rangee_icones(t, parent, index, noms, ns, rm_note, classes):
    rang = plain(t, parent, index, ["row-direction-normal", "align-items-center", VERSION_GRILLE] + classes,
                 PREFIXE + "Icones")
    t.elem(rang)["m_RuleIndex"] = -1
    t.styles.style(t, rang, FIXE)
    return icones(t, rang, noms, ns, rm_note)


def ligne_icone(t, parent, index, nom, ns, rm_note, taille, classes=()):
    """[icône agrandie] + place pour un texte, en ligne ; renvoie (ligne, erreur)"""
    ligne = plain(t, parent, index, ["row-direction-normal", "align-items-center", VERSION_GRILLE] + list(classes),
                  PREFIXE + "Ligne")
    t.elem(ligne)["m_RuleIndex"] = -1
    t.styles.style(t, ligne, FIXE)
    err = icones(t, ligne, [nom], ns, rm_note, taille, CASE_ICONE)
    if not err:
        t.elem(t.children(ligne)[-1])["m_Classes"] = ["column-direction-normal", "margin-right-global-gap-small"]
    return ligne, err


def textes_4x4():
    """textes de statut de la forme et de la fatigue de la grande tuile Condition de FM (4x4), ou None"""
    bundle, _, stt = nb.find_vta(SOURCE_STATUTS)
    if stt is None:
        return None
    s = Tree(stt)
    out = {}
    for r in s.walk():
        if typ(s, r).endswith("SIText"):
            octets = bytes((((s.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_inputs") or {})
                           .get("m_variable", {}).get("m_argumentBytes") or [])
            if b"SharpnessStatusDescription" in octets:
                out["forme"] = r
            elif b"Player.Fatigue" in octets:
                out["fatigue"] = r
    return (s, Styles(bundle, stt), out) if len(out) == 2 else None


def texte_copie(t, parent, src, r):
    s, st, _ = src
    c = t.clone(r, parent, src=s)
    copy_usings(t, s, r)
    t.styles.copy_from(st, t, c)
    t.sd(c)["name"] = ""
    return c


def tuile_2x2(t):
    return first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "tile-square-2x2"
                 or t.name(r) == "tile-square-2x2") is not None


def colonne_logos(t, parent, index, ns, rm_note):
    """logos Hiérarchie / Groupe social l'un sur l'autre (cases de la hauteur des icônes) dans un BindingRemapper
    person -> joueur de la tuile ; renvoie (colonne, erreur)"""
    rm = t.clone(rm_note, parent, index, src=ns)
    for k in list(t.children(rm)):
        t.remove(k)
    t.sd(rm)["name"] = PREFIXE + "Logos"
    t.sd(rm)["Mappings"] = [{"m_serialisedType": 0, "from": "person", "to": {"m_path": JOUEUR},
                             "type": {"id": fjp.JOUEUR}}]
    t.elem(rm)["m_Classes"] = ["column-direction-normal", "align-items-center", VERSION_GRILLE]
    t.elem(rm)["m_RuleIndex"] = -1
    t.styles.style(t, rm, FIXE)
    return rm, logos(t, rm, taille=TAILLE_GRANDE, case=CASE_ICONE)


def mental_logos(t, cadre, l1, l2, ns, rm_note):
    """v9 (2026-11-06, le joueur : logos sortis d'Infos, toujours dans cette tuile) : [smiley + mot, boussole +
    moral] | logos, vers la droite sans toucher le bord ; 2x2 en Large (étroite) : textes retirés, [smiley,
    boussole] | [logos] centrés avec de l'air ; renvoie une erreur ou None"""
    i = t.children(cadre).index(l1)
    rang = plain(t, cadre, i, ["row-direction-normal", "align-items-center", VERSION_GRILLE], PREFIXE + "Rangee")
    t.elem(rang)["m_RuleIndex"] = -1
    t.styles.style(t, rang, {"align-self": "stretch"})
    col = plain(t, rang, None, ["column-direction-normal"])
    t.elem(col)["m_RuleIndex"] = -1
    t.styles.style(t, col, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0})
    move(t, l1, col)
    move(t, l2, col)
    lg, err = colonne_logos(t, rang, None, ns, rm_note)
    if err:
        return err
    t.styles.style(t, lg, {"margin-left": LOGOS_ECART_TEXTE, "margin-right": LOGOS_MARGE_DROITE})
    if not tuile_2x2(t):
        return None
    # 2x2 = Medium et Large : la rangée ci-dessus hors Large ; en Large, 4 icônes sans texte
    remplir = ["align-self-stretch-class", VERSION_GRILLE]
    hors = si_large(t, cadre, i, False, remplir)
    t.sd(hors)["name"] = PREFIXE + "HorsLarge"
    move(t, rang, hors)
    large = si_large(t, cadre, i, True, remplir)
    t.sd(large)["name"] = PREFIXE + "Large"
    grille = plain(t, large, None, ["row-direction-normal", "align-items-center", VERSION_GRILLE], PREFIXE + "Grille")
    t.elem(grille)["m_RuleIndex"] = -1
    t.styles.style(t, grille, {"align-self": "stretch", "justify-content": "center"})
    ic = plain(t, grille, None, ["column-direction-normal", "align-items-center"])
    t.elem(ic)["m_RuleIndex"] = -1
    t.styles.style(t, ic, FIXE)
    err = icones(t, ic, MENTAL, ns, rm_note, TAILLE_GRANDE, CASE_ICONE)
    if err:
        return err
    t.elem(t.children(ic)[0])["m_Classes"] += ["margin-bottom-global-gap-small"]
    lg, err = colonne_logos(t, grille, None, ns, rm_note)
    if err:
        return err
    t.styles.style(t, lg, {"margin-left": LOGOS_ECART_LARGE})
    return None


def grille_mental(t):
    """tuile État d'esprit de la fiche (v2, le joueur : icônes plus grosses, des détails) : [smiley] mot de FM
    (« Heureux »), puis [boussole] moral en texte (player.MoraleString) ; Points + / − de FM gardés"""
    humeur = first(t, lambda r: typ(t, r) == "SI.Bindable.SIImage" and t.name(r) == "ui concepts-placeholder")
    ns, rm_note = sources_liaison()
    if humeur is None or ns is None:
        return ["icône d'état d'esprit ou modèle de liaison introuvable, ignoré"]
    cadre = t.parent[humeur]
    mot = next((r for r in t.children(cadre) if typ(t, r).endswith("SIText")), None)
    if mot is None:
        return ["mot de l'état d'esprit introuvable, ignoré"]
    i = t.children(cadre).index(humeur)
    t.remove(humeur)
    l1, err = ligne_icone(t, cadre, i, MENTAL[0], ns, rm_note, TAILLE_GRANDE, ["margin-bottom-global-gap-small"])
    if err:
        return [err + ", ignoré"]
    move(t, mot, l1)
    l2, err = ligne_icone(t, cadre, t.children(cadre).index(l1) + 1, MENTAL[1], ns, rm_note, TAILLE_GRANDE)
    if err:
        return [err + ", ignoré"]
    moral = t.clone_shallow(mot, l2)
    t.sd(moral)["name"] = ""
    t.sd(moral)["text"], t.sd(moral)["text_UxmlAttributeFlags"] = "", 0
    set_text_binding(t, moral, {"m_kind": 1, "m_direct": {"Path": {"m_path": JOUEUR + ".MoraleString"}, "Nullable": 0},
                                "m_visualFunction": {"m_target": {"m_guid": ""},
                                                     "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                                                     "m_outputs": {"m_variable": {"m_argumentBytes": []}}}})
    t.elem(moral)["m_Classes"] = ["body-md", "global-text-secondary", "content-ellipsis"]
    t.elem(moral)["m_RuleIndex"] = -1
    t.elem(cadre)["m_Classes"] = [c for c in t.elem(cadre).get("m_Classes") or [] if c != "flex-grow-class"]
    msgs = ["état d'esprit et moral en grand, chacun avec son texte"]
    err = mental_logos(t, cadre, l1, l2, ns, rm_note)
    if err:
        return [err + ", ignoré"]
    msgs.append("logos Hiérarchie / Groupe social à droite (2x2 en Large : 4 icônes sans texte, centrées)"
                if tuile_2x2(t) else "logos Hiérarchie / Groupe social à droite")
    # v7, Small (le joueur) : le trait au milieu de la tuile = une cale qui grandit avant lui et une après les Points
    boite = t.parent[cadre]
    trait = next((k for k in t.children(boite)[t.children(boite).index(cadre) + 1:]
                  if (t.elem(k).get("m_TemplateAlias") or "").startswith("layout-divider")), None)
    if trait is not None:
        for index in (t.children(boite).index(trait), None):
            cale = fjp.si_small(t, boite, index, True, [VERSION_GRILLE])
            t.styles.style(t, cale, {"flex-grow": 1, "flex-shrink": 1})
        msgs.append("Small : trait au milieu de la tuile")
    return msgs


def si_large(t, parent, index, large, classes):
    """conteneur affiché seulement en Large (large) ou seulement en Medium / Small (settings.AdaptiveScalingLevelIndex :
    Large = mode < 1, sinon mode > 0 ; même liaison que fjp.si_small)"""
    s, vis = fjp.ni.visible_model()
    b = fjp.ni.make_binding(s.sd(vis)["Binding"], 0 if large else 4, [fjp.MODE_AFFICHAGE], 1 if large else 0)
    v = fjp.ni.new_visible(t, s, vis, parent, index, "", b, list(classes))
    t.elem(v)["m_RuleIndex"] = -1
    return v


def compacte(t, cont, ns, rm_note):
    """2x2 en Large (copie de FM cont) : cœur -> rangée condition / forme / fatigue, textes de FM en body-sm, à la
    ligne plutôt que coupés ; renvoie une erreur ou None"""
    ic = next((r for r in t.walk(cont)
               if (t.elem(r).get("m_TemplateAlias") or "").startswith("scaling-icons-condition-medium")), None)
    if ic is None:
        return "icône de condition introuvable"
    cadre = t.parent[ic]
    i = t.children(cadre).index(ic)
    t.remove(ic)
    rang = plain(t, cadre, i, ["row-direction-normal", "align-items-center", "margin-bottom-global-gap-small"],
                 PREFIXE + "Icones")
    t.elem(rang)["m_RuleIndex"] = -1
    t.styles.style(t, rang, FIXE)
    err = icones(t, rang, PHYSIQUE, ns, rm_note, TAILLE_GRANDE, CASE_ICONE)
    if err:
        return err
    t.elem(cadre)["m_Classes"] = ["align-self-stretch"]
    t.styles.style(t, cadre, {"min-width": 0})
    for r in t.walk(cadre):
        if typ(t, r).endswith("SIText"):
            cls = [TEXTE_LARGE.get(c, c) for c in t.elem(r).get("m_Classes") or []
                   if c not in ("content-ellipsis", "content-no-wrap")]
            t.elem(r)["m_Classes"] = list(dict.fromkeys(cls))
    return None


def grille_physique(t):
    """tuile Condition de la fiche (v2, le joueur) : icône de condition à gauche du texte de FM (« À son meilleur
    niveau », blessure) ; 2x2 / 4x2 : dessous, forme et fatigue l'une sous l'autre avec leur statut (textes de la
    grande tuile de FM ; 4x2 : leurs icônes du bas de FM retirées) ; 2x1 : icône de condition seulement"""
    ic = first(t, lambda r: (t.elem(r).get("m_TemplateAlias") or "").startswith("scaling-icons-condition-medium"))
    ns, rm_note = sources_liaison()
    src = textes_4x4()
    if ic is None or ns is None or src is None:
        return ["icône de condition, textes de statut ou modèle de liaison introuvable, ignoré"]
    cadre = t.parent[ic]
    contenu = t.parent[cadre]
    dans = contenu
    msgs = []
    if "row-direction-normal" not in (t.elem(cadre).get("m_Classes") or []):
        # v8, 2x2 (Medium et Large) : la nôtre hors Large ; en Large (étroite, le joueur : « que les icônes limite,
        # et le texte le plus petit ») : copie de FM avec les trois icônes à la place du cœur, textes en petit
        tuile = t.parent[contenu]
        j = t.children(tuile).index(contenu)
        remplir = ["flex-grow-class", "align-self-stretch-class", VERSION_GRILLE]
        large = si_large(t, tuile, j, True, remplir)
        t.sd(large)["name"] = PREFIXE + "Large"
        petit = t.clone(contenu, large)
        hors = si_large(t, tuile, j + 1, False, remplir)
        t.sd(hors)["name"] = PREFIXE + "HorsLarge"
        move(t, contenu, hors)
        err = compacte(t, petit, ns, rm_note)
        if err:
            return [err + ", ignoré"]
        msgs.append("Large : condition / forme / fatigue en icônes, texte en petit")
    i = t.children(cadre).index(ic)
    t.remove(ic)
    textes = list(t.children(cadre))[i:]          # SIVisible pas blessé / blessé (textes de FM)
    rangee = "row-direction-normal" in (t.elem(cadre).get("m_Classes") or [])
    if rangee:   # 2x1 / 4x2 : l'icône est déjà à gauche des textes chez FM, on remplace juste l'icône
        tete, err = ligne_icone(t, cadre, i, PHYSIQUE[0], ns, rm_note, TAILLE_GRANDE)
        t.elem(cadre)["m_Classes"] = [c for c in t.elem(cadre).get("m_Classes") or [] if c != "align-items-center"] \
            + ["align-items-start"]   # v4 : icône calée sur la 1re ligne du texte
    else:        # 2x2 : [icône | textes] au lieu de l'icône au-dessus des textes
        tete, err = ligne_icone(t, cadre, i, PHYSIQUE[0], ns, rm_note, TAILLE_GRANDE, ["align-self-stretch"])
        # v8 : toute la largeur de la tuile (FM : align-self-start = largeur du texte, jamais à la ligne)
        t.elem(cadre)["m_Classes"] = ["align-self-stretch"]
        t.styles.style(t, cadre, {"min-width": 0})
        if not err:
            t.elem(tete)["m_Classes"] = [c if c != "align-items-center" else "align-items-start"
                                         for c in t.elem(tete)["m_Classes"]]
            col = plain(t, tete, None, ["column-direction-normal"])
            t.elem(col)["m_RuleIndex"] = -1
            t.styles.style(t, col, {"flex-shrink": 1, "min-width": 0})
            for k in textes:
                move(t, k, col)
    if err:
        return [err + ", ignoré"]
    for k in textes:   # v8 (Medium plus étroit que Small) : le texte passe à la ligne au lieu d'être coupé
        t.styles.style(t, k, {"flex-shrink": 1, "min-width": 0})
        for r in t.walk(k):
            if typ(t, r).endswith("SIText"):
                t.elem(r)["m_Classes"] = [c for c in t.elem(r).get("m_Classes") or []
                                          if c not in ("content-ellipsis", "content-no-wrap")]
    msgs.append("icône de condition à gauche du texte")
    _, _, statuts = src
    # dans notre version seulement (pas dans la copie du Large)
    forme = next((r for r in t.walk(dans) if (t.elem(r).get("m_TemplateAlias") or "") == "scaling-icons-sharpness-medium"),
                 None)
    fatigue = next((r for r in t.walk(dans) if "game-concepts-fatigue-fresh_medium" in (t.elem(r).get("m_Classes") or [])),
                   None)
    if forme is not None and fatigue is not None:   # 4x2 : icônes du bas de FM retirées (elles passent sous le texte)
        bas = t.parent[t.parent[forme]]
        for k in list(t.children(bas)):
            if k in (t.parent[forme], t.parent[fatigue]) \
                    or t.elem(k).get("m_TemplateAlias") == "layout-divider-solid-vertical":
                t.remove(k)
        for k in [r for r in t.walk(bas) if t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-vertical"]:
            t.remove(k)   # le trait après l'icône de blessure récurrente (plus rien derrière)
        # sous la rangée [icône | textes], avant le trait de FM ; v4 : rangée + lignes dans un bloc qui prend la place
        # (le trait et le badge restent en bas, les lignes juste sous le texte)
        haut = t.parent[cadre]
        p = plain(t, haut, t.children(haut).index(cadre), ["column-direction-normal", "align-self-stretch"])
        t.elem(p)["m_RuleIndex"] = -1
        t.styles.style(t, p, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        move(t, cadre, p)
        # v7 (le joueur : « ça fait 2 groupes ») : marge du bas de FM (12) retirée, lignes collées au texte
        t.styles.style(t, cadre, {"flex-grow": 0, "margin-bottom": 0})
        index = None
    elif not rangee:      # 2x2 : dans la colonne, sous [icône | textes]
        p, index = cadre, None
    else:                 # 2x1 : pas la place
        return msgs
    for nom, cle in ((PHYSIQUE[1], "forme"), (PHYSIQUE[2], "fatigue")):
        ligne, err = ligne_icone(t, p, index, nom, ns, rm_note, TAILLE_PETITE, ["margin-top-global-gap-small"])
        if err:
            return [err + ", ignoré"]
        texte_copie(t, ligne, src, statuts[cle])
        if index is not None:
            index += 1
    msgs.append("forme et fatigue dessous, l'une sous l'autre, avec leur statut")
    return msgs


def infos_logos(t):
    """infobulle du joueur, Infos : logos Hiérarchie / Groupe social côte à côte, à droite de Taille (sous le bouton
    du polygone), plus petits ; ajout par-dessus le bloc actuel (infobulle_pieds le retouche aussi)"""
    for r in named(t, NOM_LOGOS_INFOS):
        if VERSION_LOGOS_INFOS in (t.elem(r).get("m_Classes") or []):
            return []
        t.remove(r)
    taille = first(t, lambda r: typ(t, r).endswith("SIText") and any(
        "[%height#" in s for s in nb.strings_in(bytes(
            ((t.sd(r).get("TextBinding") or {}).get("m_visualFunction") or {}).get("m_inputs", {})
            .get("m_variable", {}).get("m_argumentBytes") or []))))
    if taille is None:
        return ["ligne Taille introuvable, logos ignorés"]
    case = t.parent[taille]   # #Frame : « Taille » + valeur
    t.styles.style(t, case, {"align-self": "stretch"})
    rang = plain(t, case, 0, ["column-direction-normal", "align-items-center", VERSION_LOGOS_INFOS], NOM_LOGOS_INFOS)
    t.elem(rang)["m_RuleIndex"] = -1
    # v2 : l'un sur l'autre (comme dans la fiche), position absolue (ne pousse rien), à droite, le bas du rond au
    # niveau du bas de la valeur (« 190 cm ») : même réglage que la fiche (fjp.LOGOS_BAS, validé en jeu)
    t.styles.style(t, rang, {**FIXE, "position": "absolute", "right": 0, "bottom": fjp.LOGOS_BAS})
    err = logos(t, rang, bulle=False, taille=LOGOS_TAILLE_INFOS)
    if err:
        return [err + ", logos ignorés"]
    return ["logos Hiérarchie / Groupe social à droite de Taille"]


def retirer_infos_logos(t):
    old = named(t, NOM_LOGOS_INFOS)
    for r in old:
        t.remove(r)
    return ["logos de Taille retirés"] if old else []


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre(modeles):
    """modèles marqués remis d'origine (rien enregistré ici) ; True si un a changé"""
    change = False
    for modele in modeles:
        o = ouvrir(modele)
        if o is None or not marques(o[3]):
            continue
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):
            print(f"{modele} : pas de sauvegarde d'origine, rien retiré")
            continue
        enregistrer(bundle, obj, tt, t)
        change = True
        print(f"{modele} : remis d'origine")
    return change


def par_dessus(fn):
    """fn sur l'infobulle telle qu'elle est (pas d'original : infobulle_pieds y a ses ajouts) ; True si changé"""
    o = ouvrir(INFOBULLE)
    if o is None:
        print(f"{INFOBULLE} : introuvable (renommé par une mise à jour ?), ignoré")
        return False
    bundle, obj, tt, t = o
    msgs = fn(t)
    for m in msgs:
        print(f"{INFOBULLE} : {m}")
    if not msgs or any("ignoré" in m for m in msgs):
        return False
    enregistrer(bundle, obj, tt, t)
    return True


def grille_a_jour(t):
    return any(VERSION_GRILLE in (t.elem(m).get("m_Classes") or []) for m in marques(t))


def cmd_appliquer():
    change = remettre(REMISES_FM)
    travaux = [(m, a_jour, construire) for m in MODELES] + [(m, grille_a_jour, grille_mental) for m in GRILLE_MENTAL] \
        + [(m, grille_a_jour, grille_physique) for m in GRILLE_PHYSIQUE]
    for modele, fait, fn in travaux:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if fait(o[3]):
            print(f"{modele} : déjà appliqué")
            continue
        old = bool(marques(o[3]))
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):   # pas de sauvegarde d'origine : on ne refait pas par-dessus
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        msgs = fn(t)
        for m in msgs + (["ancienne version remplacée"] if old else []):
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
            change = True
    change = par_dessus(infos_logos) or change
    if change:
        nb.save_all()   # un seul passage : tuile et infobulle sont dans le même bundle
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    change = remettre(MODELES + ANCIENS)
    if par_dessus(retirer_infos_logos) or change:
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele in MODELES + ANCIENS:
        o = ouvrir(modele)
        print(f"{modele} : " + ("introuvable" if o is None else "appliqué" if marques(o[3]) else "d'origine"))
    o = ouvrir(INFOBULLE)
    print(f"{INFOBULLE} : " + ("introuvable" if o is None else
                               "logos à droite de Taille" if named(o[3], NOM_LOGOS_INFOS) else "sans nos logos"))
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
            print("tuile forme du joueur : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
