"""Largeur des colonnes réglable à la main (2026-11-26, demande du joueur : « toutes les vues qu'on a ajoutées /
modifiées », directement dans chaque fonction, pas une option à part).

StreamedTable de FM : AllowColumnResizing 1 = on tire le bord d'un en-tête pour changer la largeur (comme la Base de
données des joueurs). Seul ce champ change : ResizeColumnWidthsToFit, l'ordre des colonnes et le menu du clic droit
restent ceux du tableau (mises en page déjà validées). Précédents FM à vue unique avec seulement ce champ :
PhysioTeamReportInjuriesBlock #CurrentInjuriesTable, MedicalCentreCurrentInjuriesBlock #NearingReturnTable.
Tous les tableaux visés ont AllowColumnResizing 0 dans FM (relevé le 2026-11-26) : reverrouiller remet 0.
Utilisé par : etat_esprit_fm24, staff_fm24, kinito_enregistrement, kinito_largeur_liste (+ recruteurs_colonnes, qui
fait en plus le déplacement et le clic droit).
"""
CHAMP = "AllowColumnResizing"
# 2026-11-26 (le joueur : « une taille minimum vraiment petite, juste pour que les trucs disparaissent pas ») : minimum
# de chaque colonne de ces vues (m_minWidthOverride ; FM : 44 dans nos vues, 35 à 200 dans les fabriques). 16 = le
# minimum des colonnes Séparateur de FM. Posé par le script qui écrit la vue (minimums_petits).
MINIMUM = 16.0


def minimums_petits(cfg):
    """m_tableConfig d'une vue : chaque colonne au minimum MINIMUM (sans dépasser sa largeur voulue) ; rend cfg"""
    for c in cfg:
        m = c["m_columnMetadata"]
        w = m.get("m_widthOverride") or 0
        m["m_minWidthOverride"] = float(min(MINIMUM, w)) if w > 0 else MINIMUM
    return cfg


def reglable(t, r):
    return bool(t.sd(r).get(CHAMP))


def deverrouiller(t, rs):
    """largeur réglable sur ces tableaux ; True si quelque chose a changé"""
    fait = False
    for r in rs:
        d = t.sd(r)
        if d.get(CHAMP) != 1 or d.get(CHAMP + "_UxmlAttributeFlags") != 1:
            d[CHAMP], d[CHAMP + "_UxmlAttributeFlags"] = 1, 1
            fait = True
    return fait


def reverrouiller(t, rs):
    """largeur fixe (valeur de FM pour ces tableaux) ; True si quelque chose a changé"""
    fait = False
    for r in rs:
        if t.sd(r).get(CHAMP):
            t.sd(r)[CHAMP] = 0
            fait = True
    return fait


def tous_reglables(t, rs):
    return bool(rs) and all(reglable(t, r) for r in rs)
