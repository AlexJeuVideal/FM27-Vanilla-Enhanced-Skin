"""Calendrier > Rencontres, carte du match à droite (2026-11-05, le joueur) : la place en championnat de chaque équipe
sous son nom (« 1er », texte de FM : Team.LeaguePositionString ; vide si l'équipe n'a pas de championnat).

Modèles : CalendarFixtureCard_MaxRes (grand écran) et CalendarFixtureCard_MinRes (petit). Seul écrivain (les autres
scripts ne font qu'y lire). Repérage par #HomeTeamName / #AwayTeamName.
Usage (jeu fermé) : rencontres_place_championnat.py appliquer [--dry-run] | retirer | etat | si-actif
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "commun"))
import chemins  # noqa: E402,F401
import notes_au_lieu_des_libelles as nb  # noqa: E402
import sauvegarde_originaux as backup  # noqa: E402
import arbre as sm  # noqa: E402
from arbre import Tree, named  # noqa: E402
from elements import first, move, plain, appliquer_jobs, src_tree, copy_usings, typ  # noqa: E402
import lancer  # noqa: E402

MARKER = os.path.join(backup.BACKUP_DIR, "rencontres_place_championnat.actif")
MODELES = {"CalendarFixtureCard_MaxRes": "body-md", "CalendarFixtureCard_MinRes": "body-sm"}   # modèle : taille texte
NOM = "UIPickerPlaceChampionnat-v15"   # v8 : score et buteurs centrés (côtés à parts égales)
# v12 (le joueur, captures Large / Medium / Small, match pas joué : météo « 23 °C » sous « Match Amical ») : la ligne
# stade | météo se tassait sur la ligne date | compétition -> les 2 lignes du haut ne rétrécissent plus (flex-shrink 0)
# et 4 px de plus entre elles ; le bloc équipes / heure / forme descend d'autant (le joueur : « descends un peu le bloc »)
# v9 (le joueur : « le stade etc. au-dessus, le jour… bougent ») : lignes date | compétition et stade | spectateurs
# coupées au milieu de la carte (gauche calée à droite, droite calée à gauche), comme le score
PREFIXE_HAUT = "UIPickerHautCarte"
# v10 (le joueur : « très serré, un poil d'espace vers le haut ») : px au-dessus de la ligne du stade, de la rangée du
# score (MaxRes) ; v11 (le joueur : « toujours pas assez haut ») : 4 -> 6, 14 -> 28
# v13 (le joueur, v12 vue : « trop bougé », date collée au bord du haut) : les lignes qui ne se tassent plus prennent
# déjà leur vraie place -> 10 -> 6 (comme avant) et 28 -> 14 au-dessus du bloc des équipes
ECART_HAUT = (6, 14)
# v6 (le joueur : « elle est sur ma page club ») : toujours vide en v5 -> la cellule FM incluse telle quelle, comme
# dans l'en-tête de la page club (ClubSiteHeaderTemplate : ComponentElement + BindingRemapper binding / competition
# -> TeamLastFiveMatchesFormCell), remappée sur Fixture.<équipe> et Fixture.Competition
SOURCE_FORME = "ClubSiteHeaderTemplate"
# v5 : console = liste 0×16 dans le cadre 40 px (largeur jamais donnée hors des tableaux) -> largeur imposée à la liste
# v3 : forme récente (5 barres de la cellule FM TeamLastFiveMatchesFormCell, liste sur <équipe>.RecentFormValues)
# v4 (le joueur : « je vois pas la forme ») : la liste seule ne s'affichait pas -> cadre de la cellule FM recopié en
# entier (classes team-form-cell, liste étirée dedans, comme dans les tableaux), sans l'infobulle ; listes nommées
NOMS_FORME = {"HomeTeamName": "UIPickerFormeDomicile", "AwayTeamName": "UIPickerFormeExterieur"}
FORME = True
FORME_MODELE = "TeamLastFiveMatchesFormCell"
FORME_LARGEUR, FORME_HAUTEUR, FORME_ECART = 56, 16, 8   # px (v7 : largeur du cadre, 5 barres + fond de FM)
NOMS = {"HomeTeamName": "Fixture.HomeTeam.LeaguePositionString",
        "AwayTeamName": "Fixture.AwayTeam.LeaguePositionString"}
COTE = {"HomeTeamName": "flex-end", "AwayTeamName": "flex-start"}   # côté du logo (nom de FM calé dessus)
for _k, _v in {"margin-top": (131093, 3), "align-self": (131074, 7), "flex-direction": (131083, 7), "justify-content": (131088, 7), "align-items": (131073, 7), "margin-left": (131091, 3), "margin-right": (131092, 3),
               "height": (131087, 3), "width": (131105, 3), "flex-shrink": (131085, 2)}.items():
    sm.PROPRIETES.setdefault(_k, _v)
CLASSES_RETIREES = ("thematic-lg", "heading-xsmall-14px", "global-text-primary", "flex-grow-class")


def _a_nous(t, boite, n, chemin):
    """boîte posée par une ancienne version : le nom en 1er, le reste = notre place (et la forme), ou rien"""
    kids = t.children(boite)
    if not kids or kids[0] != n or "column-direction-normal" not in (t.elem(boite).get("m_Classes") or []):
        return False
    return len(kids) == 1 or chemin in str([t.sd(r) for k in kids[1:] for r in t.walk(k)])


def defaire_v1(t):
    """anciennes versions (v1 colonne [nom, place] ; v2 colonne > boîte [nom, place]) : le nom remis à sa place, nos
    boîtes et la place retirées"""
    for nom, chemin in NOMS.items():
        n = first(t, lambda r: t.name(r) == nom)
        while n is not None and _a_nous(t, t.parent[n], n, chemin):
            b = t.parent[n]
            gp = t.parent[b]
            move(t, n, gp, t.children(gp).index(b))
            t.remove(b)


# v14 (le joueur : « même centré c'est un peu chelou ») : coins fixes, moitié gauche collée au bord gauche, moitié
# droite au bord droit (date | compétition, stade | spectateurs / météo) : rien ne bouge, symétrique
CALAGE = ("flex-start", "flex-end")
# v15 (le joueur, v14 vue : « beaucoup trop loin ») : vide de part et d'autre (part 1) et moitiés (part MOITIE
# chacune) -> les coins à ~60 % de la largeur de la carte, à peu près au niveau des noms des équipes, tous modes
MOITIE = 1.5


def _vides(t, ligne, cote):
    """vides de part et d'autre de la ligne coupée (v15), posés une fois"""
    kids = list(t.children(ligne))
    for i, pos in enumerate((0, None)):
        nom = f"{PREFIXE_HAUT}-{cote}-vide{i}"
        if any(t.name(k) == nom for k in kids):
            continue
        v = plain(t, ligne, 0 if pos == 0 else len(t.children(ligne)), [], nom)
        t.elem(v)["m_RuleIndex"] = -1
        t.sd(v)["name_UxmlAttributeFlags"] = 1
        t.styles.style(t, v, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})


def couper_au_milieu(t, ligne, n_gauche, cote):
    """ligne [a, b, c…] -> [vide | gauche (n_gauche premiers) | droite (le reste) | vide], moitiés calées selon
    CALAGE ; la ligne s'étire sur toute la largeur de la carte"""
    kids = list(t.children(ligne))
    if any(t.name(k).startswith(PREFIXE_HAUT) for k in kids):   # déjà coupée (versions d'avant) : calage remis
        moities = [k for k in kids if "-vide" not in t.name(k)]
        for i, k in enumerate(moities):
            t.styles.style(t, k, {"justify-content": CALAGE[min(i, 1)], "flex-grow": MOITIE})
        _vides(t, ligne, cote)
        return False
    if len(kids) <= n_gauche:
        return False
    t.styles.style(t, ligne, {"align-self": "stretch"})
    for i, (part, just) in enumerate(((kids[:n_gauche], CALAGE[0]), (kids[n_gauche:], CALAGE[1]))):
        b = plain(t, ligne, i, ["row-direction-normal", "align-items-center"], f"{PREFIXE_HAUT}-{cote}{i}")
        t.elem(b)["m_RuleIndex"] = -1
        t.sd(b)["name_UxmlAttributeFlags"] = 1
        t.styles.style(t, b, {"flex-grow": MOITIE, "flex-shrink": 1, "flex-basis": 0, "min-width": 0,
                              "justify-content": just})
        for k in part:
            move(t, k, b)
    _vides(t, ligne, cote)
    return True


def lignes_du_haut(t):
    contenu = first(t, lambda r: t.name(r) == "Content")
    if contenu is None:
        return
    for ligne in t.children(contenu):
        noms = [t.name(k) for k in t.children(ligne)]
        # v12 : lignes déjà coupées (versions d'avant) reconnues par leurs moitiés
        if any(n.startswith(PREFIXE_HAUT) for n in noms):
            noms = [t.name(k) for m in t.children(ligne) for k in t.children(m)]
        if noms and noms[0] in ("Date", "FixtureDate"):
            couper_au_milieu(t, ligne, 1, "date")
            t.styles.style(t, ligne, {"flex-shrink": 0})
        elif noms and noms[0] == "Logo" and "AttendanceVisible" in noms:   # MaxRes (MinRes : rien à droite)
            couper_au_milieu(t, ligne, 2, "stade")
            t.styles.style(t, ligne, {"margin-top": ECART_HAUT[0], "flex-shrink": 0})
        elif t.name(ligne) == "Horizontal" and not any(c.startswith("margin-top")
                                                       for c in t.elem(ligne).get("m_Classes") or []):
            t.styles.style(t, ligne, {"margin-top": ECART_HAUT[1]})   # MaxRes (MinRes a déjà sa marge)


def place(texte):
    def job(t):
        if named(t, NOM):
            return []
        msgs = []
        defaire_v1(t)
        forme_arbre = src_tree(SOURCE_FORME) if FORME else None
        inc = forme_arbre and first(forme_arbre, lambda r: forme_arbre.elem(r).get("m_TemplateAlias") == FORME_MODELE)
        forme_src = inc and forme_arbre.parent[inc]   # ComponentElement (remapper) qui inclut la cellule
        for nom, chemin in NOMS.items():
            n = first(t, lambda r: t.name(r) == nom)
            if n is None:
                return [f"#{nom} introuvable (le jeu a changé ?), ignoré"]
            p = t.parent[n]
            cls_nom = t.elem(n).get("m_Classes") or []
            # colonne [nom, place] à la place du nom (elle prend son flex-grow ; le nom garde sa règle : alignement)
            col = plain(t, p, t.children(p).index(n), ["column-direction-normal", "justify-content-center"]
                        + (["flex-grow-class"] if "flex-grow-class" in cls_nom else []))
            t.elem(col)["m_RuleIndex"] = -1
            # v8 (le joueur : « le score bouge tout le temps ») : les 2 côtés à parts égales (base 0), score centré
            # (seulement si la rangée prend toute la largeur : MaxRes ; en MinRes elle suit son contenu -> noms écrasés)
            t.styles.style(t, col, {"min-width": 0, **({"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0}
                                    if "width-100-percent" in (t.elem(p).get("m_Classes") or []) else {})})
            if not msgs:
                t.sd(col)["name"], t.sd(col)["name_UxmlAttributeFlags"] = NOM, 1   # marque (une seule)
            # v2 (le joueur : « centre-le sous le milieu du nom ») : boîte [nom, place] à la largeur du nom (centrée
            # dedans), calée du côté du logo (domicile à droite, extérieur à gauche) comme le nom de FM
            t.styles.style(t, col, {"align-items": COTE[nom]})
            boite = plain(t, col, 0, ["column-direction-normal"])
            t.elem(boite)["m_RuleIndex"] = -1
            t.styles.style(t, boite, {"align-items": "center", "min-width": 0, "flex-shrink": 1, "overflow": "hidden"})
            move(t, n, boite)
            c = t.clone(n, boite)
            sd = t.sd(c)
            sd["name"] = ""
            sd["TextBinding"]["m_direct"]["Path"]["m_path"] = chemin
            sd["DebugDisplay"] = "1st"
            t.elem(c)["m_Classes"] = [k for k in cls_nom if k not in CLASSES_RETIREES] \
                + ["global-text-secondary", texte]
            msgs.append(nom)
            # v3 (le joueur) : forme récente sur la ligne du classement, à gauche à domicile, à droite à l'extérieur
            if FORME and forme_src is not None:
                ligne = plain(t, boite, t.children(boite).index(c), ["row-direction-normal", "align-items-center"])
                t.elem(ligne)["m_RuleIndex"] = -1
                move(t, c, ligne)
                f = t.clone(forme_src, ligne, 0 if nom == "HomeTeamName" else None, src=forme_arbre)
                copy_usings(t, forme_arbre, forme_src)
                for r in t.walk(f):   # règles de la feuille de l'en-tête club : sans objet ici
                    t.elem(r)["m_RuleIndex"] = -1
                t.sd(f)["name"], t.sd(f)["name_UxmlAttributeFlags"] = NOMS_FORME[nom], 1
                refs = {x["rid"]: x for x in t.tt["references"]["RefIds"]}
                for c in t.sd(f)["m_components"]:
                    for mp in refs[c["rid"]]["data"].get("Mappings") or []:
                        mp["to"]["m_path"] = {"binding": f"Fixture.{nom[:4]}Team",
                                              "competition": "Fixture.Competition"}.get(mp["from"], mp["to"]["m_path"])
                # v7 (le joueur : « alignement chelou parfois ») : moins de 5 matchs = cellule plus étroite -> largeur
                # fixe, barres collées au classement (domicile à droite du cadre, extérieur à gauche)
                t.styles.style(t, f, {"flex-shrink": 0, "width": FORME_LARGEUR, "min-width": FORME_LARGEUR,
                                      "flex-direction": "row", "align-items": "center",
                                      "justify-content": "flex-end" if nom == "HomeTeamName" else "flex-start",
                                      ("margin-right" if nom == "HomeTeamName" else "margin-left"): FORME_ECART})
        lignes_du_haut(t)
        # v8 : buteurs / cartons (#KeyEvents) : les 2 colonnes à parts égales, trait au milieu de la carte
        ke = first(t, lambda r: t.name(r) == "KeyEvents"   # MinRes : 2 « KeyEvents », celui des buteurs = la rangée
                   and "row-direction-always-normal" in (t.elem(r).get("m_Classes") or []))
        if ke is not None:
            for k in t.children(ke):
                if not t.elem(k).get("m_TemplateAlias"):   # pas le trait
                    t.styles.style(t, k, {"flex-grow": 1, "flex-shrink": 1, "flex-basis": 0, "min-width": 0})
        if FORME and forme_src is None:
            return ["place en championnat sous le nom des 2 équipes (forme : cellule FM introuvable)"]
        return ["place en championnat " + ("et forme récente " if FORME else "") + "sous le nom des 2 équipes"]
    return job


def jobs():
    return [(m, place(txt)) for m, txt in MODELES.items()]


def cmd_etat():
    for m in MODELES:
        _, _, tt = nb.find_vta(m)
        print(f"{m} : " + ("introuvable" if tt is None else "posé" if named(Tree(tt), NOM) else "rien"))
    print("réapplication automatique après mise à jour (menu, choix 1) :", "oui" if os.path.exists(MARKER) else "non")


def main(argv):
    argv = [a for a in argv if a != "--dry-run"]
    op = argv[0] if argv else ""
    if op == "appliquer":
        appliquer_jobs(jobs(), MARKER)
    elif op == "retirer":
        lancer.retirer_par_restauration(MARKER)
    elif op == "etat":
        cmd_etat()
    elif op == "si-actif":
        if os.path.exists(MARKER):
            appliquer_jobs(jobs(), MARKER)
        else:
            print("place en championnat (rencontres) : non activé, rien à faire")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
