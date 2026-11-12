"""Tuile « Stats carrière » de la fiche joueur en tableau (demande du joueur, 2026-11-01, modèle : tuile Career Stats
d'une autre interface) : en-tête, une ligne par saison (liste de la page Carrière > Stats carrière, mêmes champs que
son tableau CareerStatsTableFactory), trait, ligne Total.

Colonnes : Saison | [logo] Club | M | B | PD ; gardien : M | Enc | Cln (à la place de B | PD) ; 8x4 (FM y pose
showTransferInfo) : + Infos (prêt, libre...) après le club, Note et HdM au bout. 2x2 : logo seul (pas la place pour le
nom). La liste défile dans la tuile (rien ne dépasse).

Modèles (tous repartent de l'original) : CareerStatsRow (ligne de saison, commune), CareerStatsLargeTileTemplate
(4x4 / 8x4), CareerStatsTile_4x2, CareerStatsTile_2x2 (FM n'y met pas de liste : celle de la 4x2 recopiée).
Usage (jeu fermé) : tuile_carriere.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401  (dossiers des catégories : les scripts s'importent entre eux)
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
from arbre import FIXE, PROPRIETES  # noqa: E402
from elements import first, typ, move, plain, copy_usings, set_text_binding, visible_model  # noqa: E402
from attributs_tout_cocher import ouvrir  # noqa: E402  (modèle d'origine + sa feuille de style)
from notes_installations import make_binding  # noqa: E402
from langue import texte as L  # noqa: E402
from tuile_forme import si_large  # noqa: E402  (SIVisible selon le mode Large / Medium-Small)

for _k, _v in {"width": (131105, 3), "height": (131087, 3), "-unity-text-align": (65546, 7),
               "text-overflow": (196609, 7), "white-space": (65552, 7), "margin-top": (131093, 3)}.items():
    PROPRIETES.setdefault(_k, _v)

# =====================================================================================================
#  RÉGLAGES MODIFIABLES
# =====================================================================================================
L_SAISON = 46     # px : colonne Saison (« 26-27 »)
L_NOMBRE = 30     # px : M, B, PD, Enc, Cln, HdM
L_INFOS = 48      # px : Infos (8x4)
L_NOTE = 38       # px : Note (8x4)
H_ENTETE = 20     # px : ligne d'en-tête
H_LIGNE = 26      # px : ligne de saison (FM : 36)
H_TOTAL = 26      # px : ligne Total
LOGO = 20         # px : logo du club dans la ligne (FM : 24)
MAX_SAISONS = 99  # saisons dans la liste (FM : 1)
ECART_CLUB = 6    # px : espace minimum entre le nom du club et la 1re colonne de stats
L_BARRE = 8       # px : largeur de la barre de défilement de FM, laissée à droite de l'en-tête et du total (alignés
                  # sur les lignes, qui la perdent) ; v7 : 10 -> 8 (mesuré sur capture : lignes 2 px plus à droite)
# =====================================================================================================

LIGNE = "CareerStatsRow"
GRAND = "CareerStatsLargeTileTemplate"   # 4x4 et 8x4
T4X2 = "CareerStatsTile_4x2"
T2X2 = "CareerStatsTile_2x2"
T8X4 = "CareerStatsTile_8x4"             # pas modifiée : source de la BindingVariables de la 2x2
MODELES = [LIGNE, GRAND, T4X2, T2X2]
LISTE = "Player.CareerStatsPerSeason"    # liste de la page Stats carrière (FM, tuile : …LeagueOnly)
EXTRAS = "showTransferInfo"              # variable posée par FM dans la 8x4
COMPACT = "uipickercompact"              # notre variable, posée dans la 2x2 : club sans son nom
GARDIEN = "Player.IsGoalkeeper"
MARKER = os.path.join(backup.BACKUP_DIR, "tuile_carriere.actif")
PREFIXE = "UIPickerCarriere"
VERSION = "uipicker-carriere-v7"         # changer le numéro refait la tuile (v2 : inversions des SIVisible,
                                         # ligne pleine largeur, toutes les saisons ; v3 : texte plus petit en
                                         # Large, barre de défilement ; v4 : nom du club coupé en « … », écart ;
                                         # v5 : ligne de saison rétrécissable, sinon le « … » ne venait jamais ;
                                         # v6 : barre toujours là, en-tête et total décalés de sa largeur ;
                                         # v7 : L_BARRE 8)

ENTETE, LIGNE_SAISON, TOTAL = "entete", "ligne", "total"
CLASSES = {ENTETE: ["body-sm", "global-text-secondary"], LIGNE_SAISON: ["body-md"], TOTAL: ["body-md-strong"]}
# v3 (le joueur : « ça pousse légèrement en très grand ») : en Large, un cran plus petit
CLASSES_LARGE = {ENTETE: ["body-sm", "global-text-secondary"], LIGNE_SAISON: ["body-sm"], TOTAL: ["body-sm-strong"]}
# colonnes après le club : (clé, largeur, en-tête (fr, en), chemin de la saison, chemin du total)
NOMBRES = [("m", L_NOMBRE, ("M", "Apps"), "stat.Appearances", "Player.TotalCareerLeagueAppearances")]
JOUEUR = [("b", L_NOMBRE, ("B", "Gls"), "stat.Goals", "Player.TotalCareerLeagueGoals"),
          ("pd", L_NOMBRE, ("PD", "Ast"), "stat.SeasonStatLeagueOnly.Assists", "Player.TotalCareerLeagueAssists")]
GARDIEN_COLS = [("enc", L_NOMBRE, ("Enc", "Conc"), "stat.Conceded", "Player.Conceded.PropertyValue"),
                ("cln", L_NOMBRE, ("Cln", "Cln"), "stat.CleanSheets", "Player.TotalCareerLeagueCleanSheets")]
INFOS = [("infos", L_INFOS, ("Infos", "Info"), "stat.SeasonTransferInfo", "Player.CareerTransferFeesTotal")]
FIN = [("note", L_NOTE, ("Note", "Rat"), "stat.SeasonStatLeagueOnly.AverageRating",
        "Player.TotalCareerLeagueAverageRating"),
       ("hdm", L_NOMBRE, ("HdM", "PoM"), "stat.SeasonStatLeagueOnly.PlayerOfTheMatchAwards",
        "Player.TotalCareerLeaguePlayerOfTheMatchAwards")]
SANS_FONCTION = {"m_target": {"m_guid": ""}, "m_inputs": {"m_variable": {"m_argumentBytes": []}},
                 "m_outputs": {"m_variable": {"m_argumentBytes": []}}}


def marques(t):
    return [r for r in t.walk() if t.name(r).startswith(PREFIXE)]


def a_jour(t):
    return any(VERSION in (t.elem(m).get("m_Classes") or []) for m in marques(t))


def lien(chemin):
    return {"m_kind": 1, "m_direct": {"Path": {"m_path": chemin}, "Nullable": 0}, "m_visualFunction": SANS_FONCTION}


class Fab:
    """fabrique des éléments d'un modèle : textes copiés d'un SIText du modèle, conteneurs SIVisible d'après le
    sien (pris avant qu'on retire le contenu de FM)"""

    def __init__(self, t):
        self.t = t
        self.classes = CLASSES   # CLASSES_LARGE pendant la version Large d'une ligne
        self.texte_src = first(t, lambda r: typ(t, r).endswith("SIText"))
        self.vis_src = visible_model(t)

    def boite(self, parent, classes, css=None, nom=""):
        t = self.t
        v = plain(t, parent, None, classes, nom)
        t.elem(v)["m_RuleIndex"] = -1
        t.styles.style(t, v, {**FIXE, **(css or {})})
        return v

    def cellule(self, parent, largeur, centre=True):
        css = {"width": largeur, "min-width": largeur} if largeur else {"flex-grow": 1, "flex-shrink": 1, "min-width": 0}
        return self.boite(parent, ["row-direction-normal", "align-items-center"]
                          + (["justify-content-center"] if centre else []), css)

    def texte(self, parent, sorte, chemin=None, fixe=None, coupe=False, secondaire=False):
        t = self.t
        r = t.clone_shallow(self.texte_src, parent)
        sd = t.sd(r)
        sd["name"] = ""
        if "DebugDisplay" in sd:
            sd["DebugDisplay"] = fixe or ""
        if chemin:
            set_text_binding(t, r, lien(chemin))
            sd["text"], sd["text_UxmlAttributeFlags"] = "", 0
        else:
            set_text_binding(t, r, {"m_kind": 0, "m_direct": {"Path": {"m_path": ""}, "Nullable": 0},
                                    "m_visualFunction": SANS_FONCTION})
            sd["text"], sd["text_UxmlAttributeFlags"] = fixe, 1
        cls = list(self.classes[sorte])
        if secondaire and "global-text-secondary" not in cls:
            cls.append("global-text-secondary")
        t.elem(r)["m_Classes"] = cls
        t.elem(r)["m_RuleIndex"] = -1
        css = {"white-space": "nowrap"}
        if coupe:
            css.update({"flex-shrink": 1, "min-width": 0, "overflow": "hidden", "text-overflow": "ellipsis"})
        t.styles.style(t, r, css)
        return r

    def si(self, parent, chemin, inverse, classes=("row-direction-normal",)):
        """conteneur affiché si <chemin> (ou s'il est faux : inverse)"""
        t = self.t
        v = self.boite(parent, list(classes))
        t.to_visible(v, self.vis_src, chemin, inverse, "")
        # v2 : sans ces drapeaux (modèle showTransferInfo de la ligne : 0), FM ignore l'inversion (vu en jeu)
        t.sd(v)["InvertDirectBinding_UxmlAttributeFlags"] = 1
        t.sd(v)["Binding_UxmlAttributeFlags"] = 1
        return v


def rangee(f, parent, index, sorte, compact, extras):
    """une ligne du tableau ; compact / extras : True, False ou None (= décidé en jeu par la variable de FM / la
    nôtre : ligne de saison et 4x4 / 8x4)"""
    t = f.t
    h = {ENTETE: H_ENTETE, LIGNE_SAISON: H_LIGNE, TOTAL: H_TOTAL}[sorte]
    rang = f.boite(parent, ["row-direction-normal", "align-items-center"],
                   {"height": h, "min-height": h, "align-self": "stretch", "flex-shrink": 1, "min-width": 0},
                   PREFIXE + sorte.capitalize())
    if index is not None:
        move(t, rang, parent, index)

    def colonnes(dans, cols):
        for _, largeur, entete, chemin, total in cols:
            c = f.cellule(dans, largeur)
            if sorte == ENTETE:
                f.texte(c, sorte, fixe=L(*entete))
            else:
                f.texte(c, sorte, chemin=chemin if sorte == LIGNE_SAISON else total)

    def selon(valeur, chemin, cols):
        if valeur is False:
            return
        dans = f.si(rang, chemin, False) if valeur is None else rang
        colonnes(dans, cols)

    # saison
    c = f.cellule(rang, L_SAISON, centre=False)
    if sorte == ENTETE:
        f.texte(c, sorte, fixe=L("Saison", "Season"))
    elif sorte == LIGNE_SAISON:
        f.texte(c, sorte, chemin="stat.SeasonYear", secondaire=True)
    else:
        f.texte(c, sorte, fixe="Total")
    # club (la ligne de saison : logo de FM déplacé ici, voir construire_ligne)
    club = f.cellule(rang, None, centre=False)
    t.sd(club)["name"] = PREFIXE + "Club"
    t.styles.style(t, club, {"margin-right": ECART_CLUB, "overflow": "hidden"})   # v4 : jamais collé aux stats
    if sorte == ENTETE and compact is not True:
        dans = f.si(club, COMPACT, True) if compact is None else club
        f.texte(dans, sorte, fixe=L("Club", "Club"), coupe=True)
    elif sorte == TOTAL:
        f.texte(club, sorte, chemin="Player.PlayerCareerClubCount")
        if compact is not True:
            espace = f.texte(club, sorte, fixe=" " + L("clubs", "clubs"), coupe=True, secondaire=True)
            t.elem(espace)["m_Classes"] = [f.classes[LIGNE_SAISON][0], "global-text-secondary"]
    selon(extras, EXTRAS, INFOS)
    colonnes(rang, NOMBRES)
    colonnes(f.si(rang, GARDIEN, True), JOUEUR)
    colonnes(f.si(rang, GARDIEN, False), GARDIEN_COLS)
    selon(extras, EXTRAS, FIN)
    return rang, club


def deux_tailles(f, parent, sorte, compact, extras, apres=None):
    """la ligne en deux versions : Large (texte un cran plus petit) / Medium-Small, chacune dans son SIVisible ;
    apres(rang, club, large) complète chaque version ; renvoie les deux rangées"""
    t = f.t
    rangs = []
    for large in (True, False):
        v = si_large(t, parent, None, large, ["row-direction-normal" if sorte == LIGNE_SAISON
                                              else "column-direction-normal"])
        # v5 (vu en jeu : nom jamais coupé, ligne plus large que la liste) : la ligne de saison peut rétrécir
        t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "min-width": 0} if sorte == LIGNE_SAISON
                       else FIXE)
        f.classes = CLASSES_LARGE if large else CLASSES
        rang, club = rangee(f, v, None, sorte, compact, extras)
        t.elem(rang)["m_Classes"] += [VERSION]
        if sorte != LIGNE_SAISON:   # v6 : la place de la barre de défilement des lignes
            t.styles.style(t, rang, {"margin-right": L_BARRE})
        if apres:
            apres(rang, club, large)
        rangs.append(rang)
    f.classes = CLASSES
    return rangs


def construire_ligne(t):
    """CareerStatsRow : cellules refaites ; logo + nom du club de FM gardés (nom caché en 2x2)"""
    racine = first(t, lambda r: typ(t, r) == "UnityEngine.UIElements.VisualElement" and t.parent.get(r) is not None
                   and typ(t, t.parent[r]).endswith("BindingExpect"))
    logo = first(t, lambda r: typ(t, r).endswith("BindingRemapper"))
    nom = first(t, lambda r: t.binding(r, "TextBinding") == "stat.Team.Club.Name")
    if racine is None or logo is None or nom is None:
        return ["ligne de FM introuvable (le jeu a changé ?), ignoré"]
    t.sd(t.parent[racine])["Parameters"].append(
        {**next(p for p in t.sd(t.parent[racine])["Parameters"] if p["name"] == EXTRAS), "name": COMPACT})
    f = Fab(t)
    anciens = t.children(racine)
    t.styles.style(t, racine, {"height": H_LIGNE, "flex-shrink": 1, "min-width": 0})
    t.styles.style(t, t.parent[racine], {"flex-shrink": 1, "min-width": 0})   # BindingExpect (FM : shrink 0)

    def club_de_fm(rang, club, large):
        # v2 : parent en ligne -> toute la largeur (sinon serrée à gauche)
        t.styles.style(t, rang, {"flex-grow": 1})
        lg = t.clone(logo, club)
        t.elem(lg)["m_Classes"] = ["margin-right-global-gap-small"]
        for r in t.walk(lg):
            if t.elem(r).get("m_TemplateAlias") == "ClubIcon":
                t.elem(r)["m_Classes"] = []
                t.styles.style(t, r, {"width": LOGO, "height": LOGO, **FIXE})
        sans_compact = f.si(club, COMPACT, True)
        t.styles.style(t, sans_compact, {"flex-shrink": 1, "min-width": 0})
        n = t.clone(nom, sans_compact)
        t.elem(n)["m_Classes"] = [CLASSES_LARGE[LIGNE_SAISON][0] if large else CLASSES[LIGNE_SAISON][0]]
        # v4 (le joueur : « s'il passe par-dessus les stats, ça fait ... ») : le nom rétrécit et se coupe en « … »
        t.styles.style(t, n, {"flex-shrink": 1, "min-width": 0, "overflow": "hidden", "text-overflow": "ellipsis",
                              "white-space": "nowrap"})

    deux_tailles(f, racine, LIGNE_SAISON, None, None, club_de_fm)
    for k in anciens:
        t.remove(k)
    return ["ligne de saison : Saison | Club | M | B | PD (gardien : Enc | Cln), Infos / Note / HdM en 8x4"]


def regler_liste(t, liste):
    sd = t.sd(liste)
    # v2 : l'entier de la fonction de FM = nombre de saisons montrées (1 chez FM, vu en jeu)
    sd["Binding"] = make_binding(sd["Binding"], 0, [LISTE], MAX_SAISONS)
    sd["FixedElementSize"] = float(H_LIGNE)
    # v3 (le joueur : « une petite scrollbar à droite pour voir où on en est ») : celle de FM, affichée s'il y a plus
    # de saisons que de place (v1-v2 : cachée)
    # v6 : toujours affichée (même largeur perdue par les lignes, avec ou sans défilement : voir L_BARRE)
    sd["VerticalScrollerVisibility"], sd["VerticalScrollerVisibility_UxmlAttributeFlags"] = 1, 1
    e = t.elem(liste)
    if e.get("m_RuleIndex", -1) >= 0:   # hauteur fixe de FM (176) retirée : la liste prend la place qui reste
        garde = [p for p in t.styles.values(e["m_RuleIndex"]) if p[0] != PROPRIETES["height"][0]]
        e["m_RuleIndex"] = t.styles.add_rule(garde)
    t.styles.style(t, liste, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})


def construire_tuile(t, compact, extras, liste_src=None):
    """tuile (ou modèle 4x4 / 8x4) : [en-tête, liste, trait, total] dans le cadre de FM"""
    trait = first(t, lambda r: t.elem(r).get("m_TemplateAlias") == "layout-divider-solid-horizontal")
    if trait is None:
        return ["trait de FM introuvable (le jeu a changé ?), ignoré"]
    cadre = t.parent[trait]
    liste = first(t, lambda r: typ(t, r).endswith("StreamedObjectList"))
    f = Fab(t)
    anciens = [k for k in t.children(cadre) if k not in (trait, liste)]
    if liste is None:   # 2x2 : liste de la 4x2 recopiée, dans la variable « compact »
        s, liste_fm, var_src, s8 = liste_src
        var = t.clone(var_src, cadre, src=s8)
        for k in list(t.children(var)):
            t.remove(k)
        t.sd(var)["ValueVariables"] = [{"m_name": COMPACT, "m_scopeValue": {"m_serializedData": "Bool|1|"}}]
        t.elem(var)["m_Classes"] = ["column-direction-normal"]
        t.elem(var)["m_RuleIndex"] = -1
        t.styles.style(t, var, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
        liste = t.clone(liste_fm, var, src=s)
        copy_usings(t, s, liste_fm)
        t.styles.copy_from(s.styles, t, liste)
    regler_liste(t, liste)
    deux_tailles(f, cadre, ENTETE, compact, extras)
    bloc = liste if t.parent[liste] == cadre else t.parent[liste]
    move(t, bloc, cadre)
    move(t, trait, cadre)
    t.elem(trait)["m_Classes"] = []
    t.styles.style(t, trait, {"margin-top": 2, "margin-bottom": 0, **FIXE})
    deux_tailles(f, cadre, TOTAL, compact, extras)
    for k in anciens:
        t.remove(k)
    t.styles.style(t, cadre, {"flex-grow": 1, "flex-shrink": 1, "min-height": 0})
    return (["tableau des saisons (en-tête, saisons, total)"] + (["logo du club seul (pas la place du nom)"] if compact
                                                               else [])
            + (["Infos / Note / HdM en 8x4"] if extras is None else []))


def sources_2x2():
    o4, o8 = ouvrir(T4X2, depart_original=True), ouvrir(T8X4, depart_original=True)
    if o4 is None or o8 is None:
        return None
    s, s8 = o4[3], o8[3]
    liste = first(s, lambda r: typ(s, r).endswith("StreamedObjectList"))
    var = first(s8, lambda r: typ(s8, r).endswith("BindingVariables"))
    return (s, liste, var, s8) if liste is not None and var is not None else None


def enregistrer(bundle, obj, tt, t):
    t.finish()
    t.styles.save()
    obj.save_typetree(tt)
    nb._dirty.add(bundle)


def remettre(modeles):
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


def cmd_appliquer():
    travaux = [(LIGNE, construire_ligne), (GRAND, lambda t: construire_tuile(t, False, None)),
               (T4X2, lambda t: construire_tuile(t, False, False)),
               (T2X2, lambda t: construire_tuile(t, True, False, sources_2x2()))]
    change = False
    for modele, fn in travaux:
        o = ouvrir(modele)
        if o is None:
            print(f"{modele} : introuvable (renommé par une mise à jour ?), ignoré")
            continue
        if a_jour(o[3]):
            print(f"{modele} : déjà appliqué")
            continue
        old = bool(marques(o[3]))
        bundle, obj, tt, t = ouvrir(modele, depart_original=True)
        if marques(t):
            print(f"{modele} : ancienne version présente et pas d'original, retirer d'abord")
            continue
        if modele == T2X2 and sources_2x2() is None:
            print(f"{modele} : liste de la 4x2 introuvable (le jeu a changé ?), ignoré")
            continue
        msgs = fn(t)
        for m in msgs + (["ancienne version remplacée"] if old else []):
            print(f"{modele} : {m}")
        if not any("ignoré" in m for m in msgs):
            enregistrer(bundle, obj, tt, t)
            change = True
    if change:
        nb.save_all()
    if not nb.DRY_RUN:
        with open(MARKER, "w", encoding="utf-8") as f:
            json.dump({"actif": True}, f)


def cmd_retirer():
    if os.path.exists(MARKER) and not nb.DRY_RUN:
        os.remove(MARKER)
    if remettre(MODELES):
        nb.save_all()
    else:
        print("rien à retirer")


def cmd_etat():
    for modele in MODELES:
        o = ouvrir(modele)
        print(f"{modele} : " + ("introuvable" if o is None else "appliqué" if marques(o[3]) else "d'origine"))
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
            print("tuile stats carrière : non activée, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
